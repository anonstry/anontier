from loguru import logger

from typing import Iterator

from src.session import mongo_database, create_token


class DatabaseMessage:
    mongo_collection = mongo_database["messages"]

    def __init__(
        self,
        from_telegram_chat_id,
        from_room_token,
        telegram_message_id,
        token=None,
        from_primary_room_token=None,
        from_primary_message_token=None,
    ):
        self.token = token or create_token(48)
        self.from_telegram_chat_id = from_telegram_chat_id
        self.from_room_token = from_room_token
        self.telegram_message_id = telegram_message_id
        self.from_primary_room_token = from_primary_room_token
        self.from_primary_message_token = from_primary_message_token
        self.expiration_timestamp = "Nothing here yet" # @experimental @sanitization

    def exists(self):
        query = {
            "from_telegram_chat_id": self.from_telegram_chat_id,
            "from_room_token": self.from_room_token,
            "telegram_message_id": self.telegram_message_id,
        }
        message_document = self.mongo_collection.find_one(query)
        return bool(message_document)

    def create(self, duplicate=False):
        if not duplicate and self.exists():
            return
        else:
            self.mongo_collection.insert_one(
                {
                    "from_telegram_chat_id": self.from_telegram_chat_id,
                    "from_room_token": self.from_room_token,
                    "telegram_message_id": self.telegram_message_id,
                    "token": self.token,
                    "from_primary_room_token": self.from_primary_room_token,
                    "from_primary_message_token": self.from_primary_message_token,
                }
            )

    def refresh(self):
        query = {
            "from_telegram_chat_id": self.from_telegram_chat_id,
            "from_room_token": self.from_room_token,
            "telegram_message_id": self.telegram_message_id,
        }
        message_document = self.mongo_collection.find_one(query)
        assert message_document
        self.from_telegram_chat_id = message_document["from_telegram_chat_id"]
        self.from_room_token = message_document["from_room_token"]
        self.telegram_message_id = message_document["telegram_message_id"]
        self.token = message_document["token"]
        self.from_primary_room_token = message_document["from_primary_room_token"]
        self.from_primary_message_token = message_document["from_primary_message_token"]

    def delete(self):
        query = {"token": self.token}
        self.mongo_collection.delete_one(query)


def search_linked_messages(primary_message_token):  # maybe include_itself=True
    mongo_collection = DatabaseMessage.mongo_collection
    database_linked_messages = mongo_collection.find(
        {"from_primary_message_token": primary_message_token}
    )
    for database_linked_message in database_linked_messages:
        database_linked_message = DatabaseMessage(
            database_linked_message["from_telegram_chat_id"],
            database_linked_message["from_room_token"],
            database_linked_message["telegram_message_id"],
        )
        database_linked_message.refresh()
        yield database_linked_message
    else:
        logger.error("No linked messages!")
        yield from list()  # Empty list



def return_all_messages() -> Iterator[DatabaseMessage]:
    mongo_collection = DatabaseMessage.mongo_collection
    messages_documents = mongo_collection.find()
    for message_document in messages_documents:
        database_message = DatabaseMessage(
            message_document["from_telegram_chat_id"],
            message_document["from_room_token"],
            message_document["telegram_message_id"],
        )
        database_message.refresh()
        yield database_message
    else:
        yield from list() # Empty list



def search_correspondent_replied_message(
    where_telegram_chat_id,
    where_room_token,
    with_primary_message_token,
):
    mongo_collection = DatabaseMessage.mongo_collection
    database_message_document = mongo_collection.find_one(
        {
            "from_telegram_chat_id": where_telegram_chat_id,
            "from_room_token": where_room_token,
            "$or": [
                {"from_primary_message_token": with_primary_message_token},
                {
                    "$and": [
                        {"from_primary_message_token": None},
                        {"token": with_primary_message_token},
                    ]
                },
            ],
        }
    )
    assert database_message_document
    database_message = DatabaseMessage(
        from_telegram_chat_id=database_message_document["from_telegram_chat_id"],
        from_room_token=database_message_document["from_room_token"],
        telegram_message_id=database_message_document["telegram_message_id"],
    )
    database_message.refresh()
    return database_message


def search_for_original_messages_with_id(telegram_message_id):
    mongo_collection = DatabaseMessage.mongo_collection
    database_messages_documents = mongo_collection.find(
        {
            "telegram_message_id": telegram_message_id,
            "from_primary_room_token": None,
            "$expr": {"$ne": ["$from_room_token", None]},  # is not Null
            "from_primary_message_token": None,
        }
    )
    for database_message_document in database_messages_documents:
        database_message = DatabaseMessage(
            from_telegram_chat_id=database_message_document["from_telegram_chat_id"],
            from_room_token=database_message_document["from_room_token"],
            telegram_message_id=database_message_document["telegram_message_id"],
        )
        database_message.refresh()
        yield database_message
    else:
        logger.error("No original messages with the provided ID was found!")
        yield from list()

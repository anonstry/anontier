from pymongo import MongoClient
from dynaconf import settings

import secrets

mongo_client = MongoClient(settings.MONGO_CONNECTION_STRING)
mongo_database = mongo_client[settings.MONGO_DATABASE_NAME]


class Message:  # RoomMessage
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
        self.token = token or secrets.token_hex(32)
        self.from_telegram_chat_id = from_telegram_chat_id
        self.from_room_token = from_room_token
        self.telegram_message_id = telegram_message_id
        self.from_primary_room_token = from_primary_room_token
        self.from_primary_message_token = from_primary_message_token

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
    mongo_collection = Message.mongo_collection

    linked_messages = mongo_collection.find(
        {"from_primary_message_token": primary_message_token}
    )
    linked_messages = list(linked_messages)
    if not linked_messages:
        print("No linked messages", linked_messages)
        return list()  # Empty list
    else:
        for linked_message in linked_messages:
            _linked_message = Message(
                linked_message["from_telegram_chat_id"],
                linked_message["from_room_token"],
                linked_message["telegram_message_id"],
            )
            _linked_message.refresh()
            yield _linked_message


def search_correspondent_replied_message(
    where_telegram_chat_id,
    where_room_token,
    with_primary_message_token,
):  # maybe include_itself=True
    mongo_collection = Message.mongo_collection

    linked_message = mongo_collection.find_one(
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
    assert linked_message
    message = Message(
        from_telegram_chat_id=linked_message["from_telegram_chat_id"],
        from_room_token=linked_message["from_room_token"],
        telegram_message_id=linked_message["telegram_message_id"],
    )
    message.refresh()
    return message


def search_for_deleted_message_with_id(telegram_message_id):  # session.telegram
    mongo_collection = Message.mongo_collection

    message_document = mongo_collection.find_one(
        {
            "telegram_message_id": telegram_message_id,
            "from_primary_room_token": None,
            "$expr": {"$ne": ["$from_room_token", None]},
            "from_primary_message_token": None,
        }
    )
    assert message_document
    _message = Message(
        from_telegram_chat_id=message_document["from_telegram_chat_id"],
        from_room_token=message_document["from_room_token"],
        telegram_message_id=message_document["telegram_message_id"],
    )
    _message.refresh()
    return _message

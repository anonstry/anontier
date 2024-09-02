# Precisamos melhorar isto
# Talvez com o map
# Talvez com um sistema em grafo
# ou talvez com um nome melhor para as variáveis

from typing import Iterator

from loguru import logger
import pendulum

from src.database import create_token, mongo_database


class DatabaseMessage:
    mongo_collection = mongo_database["messages"]

    def __init__(
        self,
        where_telegram_chat_id,
        where_room_token,
        telegram_message_id,
        identifier=None,
        from_root_room_token=None,
        from_root_message_token=None,
        expiration_timestamp=None,
        label=None,
    ):
        self.identifier = identifier or create_token(48)
        self.where_telegram_chat_id = where_telegram_chat_id
        self.where_room_token = where_room_token
        self.telegram_message_id = telegram_message_id
        self.from_root_room_token = from_root_room_token
        self.from_root_message_token = from_root_message_token
        if not expiration_timestamp:
            self.expiration_timestamp = int(pendulum.now().add(year=1).timestamp())
        else:
            self.expiration_timestamp = expiration_timestamp
        self.label = label

    def exists(self):
        query = {
            "where_telegram_chat_id": self.where_telegram_chat_id,
            "where_room_token": self.where_room_token,
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
                    "where_telegram_chat_id": self.where_telegram_chat_id,
                    "where_room_token": self.where_room_token,
                    "telegram_message_id": self.telegram_message_id,
                    "identifier": self.identifier,
                    "label": self.label,
                    "expiration_timestamp": self.expiration_timestamp,
                    "from_root_room_token": self.from_root_room_token,
                    "from_root_message_token": self.from_root_message_token,
                }
            )

    def refresh(self):
        query = {
            "where_telegram_chat_id": self.where_telegram_chat_id,
            "where_room_token": self.where_room_token,
            "telegram_message_id": self.telegram_message_id,
        }
        document = self.mongo_collection.find_one(query)
        self.where_telegram_chat_id = document["where_telegram_chat_id"]
        self.where_room_token = document["where_room_token"]
        self.telegram_message_id = document["telegram_message_id"]
        self.identifier = document["identifier"]
        self.label = document["label"]
        self.expiration_timestamp = document["expiration_timestamp"]
        self.from_root_room_token = document["from_root_room_token"]
        self.from_root_message_token = document["from_root_message_token"]

    def delete(self):
        query = {"identifier": self.identifier}
        self.mongo_collection.delete_one(query)


def search_linked_messages(primary_message_token):  # maybe include_itself=True
    mongo_collection = DatabaseMessage.mongo_collection
    return mongo_collection.find({"from_root_message_token": primary_message_token})


def return_all_messages() -> Iterator[DatabaseMessage]:
    mongo_collection = DatabaseMessage.mongo_collection
    messages_documents = mongo_collection.find()
    for message_document in messages_documents:
        database_message = DatabaseMessage(
            message_document["where_telegram_chat_id"],
            message_document["where_room_token"],
            message_document["telegram_message_id"],
        )
        database_message.refresh()
        yield database_message
    else:
        yield from list()  # Empty list


def return_all_expired_messages() -> Iterator[DatabaseMessage]:
    for database_message in return_all_messages():
        if pendulum.now().timestamp() > database_message.expiration_timestamp:
            yield database_message
    else:
        yield from list()  # Empty list


def return_correspondent_message(
    where_telegram_chat_id,
    where_room_token,
    linked_root_message_identifier,
):
    mongo_collection = DatabaseMessage.mongo_collection
    database_message_document = mongo_collection.find_one(
        {
            "where_telegram_chat_id": where_telegram_chat_id,
            "where_room_token": where_room_token,
            "$or": [
                {"from_root_message_token": linked_root_message_identifier},
                {
                    "$and": [
                        {"from_root_message_token": None},
                        {"identifier": linked_root_message_identifier},
                    ]
                },
            ],
        }
    )
    return database_message_document


def return_root_message(
    where_room_token,
    linked_root_message_identifier,
):
    mongo_collection = DatabaseMessage.mongo_collection
    database_message_document = mongo_collection.find_one(
        {
            "where_room_token": where_room_token,
            "$or": [
                {"from_root_message_token": linked_root_message_identifier},
                {
                    "$and": [
                        {"from_root_message_token": None},
                        {"identifier": linked_root_message_identifier},
                    ]
                },
            ],
        }
    )
    return database_message_document


def search_for_original_messages_with_id(telegram_message_id):
    mongo_collection = DatabaseMessage.mongo_collection
    database_messages_documents = mongo_collection.find(
        {
            "telegram_message_id": telegram_message_id,
            "from_root_room_token": None,
            "$expr": {"$ne": ["$where_room_token", None]},  # is not Null
            "from_root_message_token": None,
        }
    )
    for database_message_document in database_messages_documents:
        database_message = DatabaseMessage(
            where_telegram_chat_id=database_message_document["where_telegram_chat_id"],
            where_room_token=database_message_document["where_room_token"],
            telegram_message_id=database_message_document["telegram_message_id"],
        )
        database_message.refresh()
        yield database_message
    else:
        logger.error("No original messages with the provided ID was found!")
        yield from list()


# def find_root_message

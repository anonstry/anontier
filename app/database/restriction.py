from app.database import mongo_database

import pendulum
from loguru import logger


class DatabaseRestriction:
    mongo_collection = mongo_database["restrictions"]

    def __init__(
        self,
        label,
        until_timestamp,
        where_room_token,
        telegram_account_id,
        applied_by_telegram_account_id,
    ):
        self.label = label  # mute, expulsion, block
        self.until_timestamp = until_timestamp
        self.where_room_token = where_room_token
        self.telegram_account_id = telegram_account_id
        self.applied_by_telegram_account_id = applied_by_telegram_account_id
        self.database_query = {
            "label": self.label,
            "until_timestamp": self.until_timestamp,
            "where_room_token": self.where_room_token,
            "applied_by_telegram_account_id": self.applied_by_telegram_account_id,
        }

    # def reload(self):
    #     document = self.mongo_collection.find_one(self.database_query)
    #     self. = document[""]
    #     # self.room_token = database_user_document["room_token"]
    #     # self.hidden = database_user_document["hidden"]
    #     # self.premium = database_user_document["premium"]
    #     # self.username = database_user_document["username"]
    #     # self.identifier = database_user_document["identifier"]

    # def exists(self):
    #     return bool(self.mongo_collection.find_one(self.database_query))

    # def create(self, duplicate=False):
    #     if not duplicate and self.exists():
    #         return
    #     else:
    #         self.mongo_collection.insert_one(self.database_query)

    # def delete(self):
    #     self.mongo_collection.delete_one(self.database_query)


def new_user_block(
    where_room_token,
    telegram_account_id,
    applied_by_telegram_account_id,
    until_timestamp=None,
):
    if not until_timestamp:
        until_timestamp = pendulum.now().add(days=1).timestamp()
    # DatabaseRestriction.mongo_collection.insert_one(
    #     {
    #         "label": "block",
    #         "where_room_token": where_room_token,
    #         "telegram_account_id": telegram_account_id,
    #         "applied_by_telegram_account_id": applied_by_telegram_account_id,
    #         "until_timestamp": until_timestamp,
    #     }
    # )
    query = {
        "label": "block",
        "where_room_token": where_room_token,
        "telegram_account_id": telegram_account_id,
        "applied_by_telegram_account_id": applied_by_telegram_account_id,
    }
    query2 = {
        "label": "block",
        "where_room_token": where_room_token,
        "telegram_account_id": telegram_account_id,
        "applied_by_telegram_account_id": applied_by_telegram_account_id,
        "until_timestamp": until_timestamp
    }
    DatabaseRestriction.mongo_collection.update_one(
        filter=query,
        update={"$set": query2},
        upsert=True,
    )


def delete_user_block(
    where_room_token,
    telegram_account_id,
    applied_by_telegram_account_id,
):
    DatabaseRestriction.mongo_collection.delete_many(
        {
            "label": "block",
            "where_room_token": where_room_token,
            "telegram_account_id": telegram_account_id,
            "applied_by_telegram_account_id": applied_by_telegram_account_id,
        }
    )


def check_user_block(
    where_room_token,
    telegram_account_id,
    applied_by_telegram_account_id,
):
    query = {
        "label": "block",
        "where_room_token": where_room_token,
        "telegram_account_id": telegram_account_id,
        "applied_by_telegram_account_id": applied_by_telegram_account_id,
    }
    if DatabaseRestriction.mongo_collection.find_one(query):
        return True
    else:
        return False


def search_expired_user_blocks():
    logger.debug("Searching for expired user blocks...")
    documents = DatabaseRestriction.mongo_collection.find({"label": "block"})
    now_timestamp = pendulum.now().timestamp()
    for document in documents:
        if document["until_timestamp"] < now_timestamp:
            yield document
    else:
        yield from list()  # Return empty list


def delete_expired_user_blocks():
    for document in search_expired_user_blocks():
        query = {
            "label": "block",
            "where_room_token": document["where_room_token"],
            "telegram_account_id": document["telegram_account_id"],
            "applied_by_telegram_account_id": document[
                "applied_by_telegram_account_id"
            ],
        }
        DatabaseRestriction.mongo_collection.delete_one(query)
        # DatabaseRestriction.mongo_collection.delete_many(query)

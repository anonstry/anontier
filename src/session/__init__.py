# Session manager

import secrets

from pymongo import MongoClient
from dynaconf import settings

mongo_client = MongoClient(settings.MONGO_CONNECTION_STRING)
mongo_database = mongo_client[settings.MONGO_DATABASE_NAME]


class User:
    mongo_collection = mongo_database["users"]

    def __init__(self, telegram_account_id, room_token=None):
        self.telegram_account_id = telegram_account_id
        self.room_token = room_token
        self.premium = False
        # self.token = secrets.token_hex(16)
        # active_premium

    def refresh(self):
        query = {"telegram_account_id": self.telegram_account_id}
        user_document = self.mongo_collection.find_one(query)
        assert user_document
        self.telegram_account_id = user_document["telegram_account_id"]
        self.room_token = user_document["room_token"]
        self.premium = user_document["premium"]

    def exists(self):
        query = {"telegram_account_id": self.telegram_account_id}
        user_document = self.mongo_collection.find_one(query)
        return bool(user_document)

    def create(self, duplicate=False):
        if not duplicate and self.exists():
            # print("User exists")
            return
        else:
            # print("User not exist")
            self.mongo_collection.insert_one(
                {
                    "telegram_account_id": self.telegram_account_id,
                    "room_token": self.room_token,
                    "premium": self.premium,
                }
            )

    def delete(self):
        query = {"telegram_account_id": self.telegram_account_id}
        self.mongo_collection.delete_one(query)

    def modify_linked_room_token(self, new_room_token):
        self.mongo_collection.update_one(
            filter={"telegram_account_id": self.telegram_account_id},
            update={"$set": {"room_token": new_room_token}},
        )
        self.room_token = new_room_token

    def link_room(self, room_token):
        if self.room_token:
            raise ValueError("Unlink the current room first")
        room = Room(token=room_token)
        self.modify_linked_room_token(room.token)
        room.increment_participants_count()

    def link_new_room(self):
        if self.room_token:
            raise ValueError("Unlink the current room first")
        room = Room()
        room.create()
        self.modify_linked_room_token(room.token)
        room.increment_participants_count()

    def unlink_room(self, room_token):
        room = Room(token=room_token)
        room.refresh()
        self.modify_linked_room_token(new_room_token=None)
        room.increment_participants_count(-1)


class Room:
    mongo_collection = mongo_database["rooms"]

    def __init__(self, token=None, size_limit=2, hidden=False):
        if not token:
            token = secrets.token_hex(48)
        self.token = token
        self.size_limit = max(2, size_limit)  # No lower than 2
        self.size_limit = min(10, self.size_limit)  # No higher than 10 (if not premium)
        self.token = token
        self.hidden = hidden
        self.participants_count = 0

    def refresh(self):
        query = {"token": self.token}
        room_document = self.mongo_collection.find_one(query)
        assert room_document
        self.token = room_document["token"]
        self.hidden = room_document["hidden"]
        self.size_limit = room_document["size_limit"]
        self.participants_count = room_document["participants_count"]

    def exists(self):
        query = {"token": self.token}
        message_document = self.mongo_collection.find_one(query)
        return bool(message_document)

    def create(self, duplicate=False):
        if not duplicate and self.exists():
            return
        else:
            self.mongo_collection.insert_one(
                {
                    "token": self.token,
                    "hidden": self.hidden,
                    "size_limit": self.size_limit,
                    "participants_count": self.participants_count,
                }
            )

    def delete(self):
        query = {"token": self.token}
        self.mongo_collection.delete_one(query)

    def increment_participants_count(self, increment=1):
        updated_collecion = self.mongo_collection.find_one_and_update(
            filter={"token": self.token},
            update={"$inc": {"participants_count": increment}},
            return_document=True,
        )
        self.participants_count = updated_collecion["participants_count"]


def search_public_room(sorting_number):
    mongo_collection = mongo_database["rooms"]

    sorting_number = -1 if sorting_number < 0 else 1
    room_document = mongo_collection.find_one(
        filter={
            "hidden": False,
            "$and": [
                {"$expr": {"$lt": ["$participants_count", "$size_limit"]}},
                {"$expr": {"$gte": ["$participants_count", 1]}},
            ],
        },
        sort=[("participants_count", sorting_number)],
    )
    if not room_document:
        return
    else:
        return Room(
            token=room_document["token"],
            hidden=room_document["hidden"],
            size_limit=room_document["size_limit"],
        )


def search_empty_rooms():
    mongo_collection = mongo_database["rooms"]

    empty_rooms = mongo_collection.find({"participants_count": 0})
    empty_rooms = list(empty_rooms)
    if not empty_rooms:
        return list()  # or None
    for empty_room in empty_rooms:
        room_document = empty_room
        yield Room(
            token=room_document["token"],
            hidden=room_document["hidden"],
            size_limit=room_document["size_limit"],
        )


def sanitize_rooms():
    "Delete empty rooms"
    for room in search_empty_rooms():
        room.delete()


def search_room_members(room_token):
    mongo_collection = mongo_database["users"]

    room_members = mongo_collection.find({"room_token": room_token})
    room_members = list(room_members)
    if not room_members:
        return
    else:
        for room_member in room_members:
            yield User(room_member["telegram_account_id"], room_member["room_token"])


def return_all_users():
    mongo_collection = mongo_database["users"]

    room_members = mongo_collection.find()
    room_members = list(room_members)
    if not room_members:
        return
    else:
        for room_member in room_members:
            user = User(
                room_member["telegram_account_id"],
                room_member["room_token"]
            )
            user.refresh()
            yield user

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
    mongo_collection = mongo_database["messages"]

    linked_messages = mongo_collection.find({"from_primary_message_token": primary_message_token})
    linked_messages = list(linked_messages)
    if not linked_messages:
        print("No linked messages", linked_messages)
        return list() # Empty list
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
    mongo_collection = mongo_database["messages"]

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
    mongo_collection = mongo_database["messages"]

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
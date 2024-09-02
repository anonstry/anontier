from typing import Iterator

from src.database import create_token, create_username, mongo_database
from src.database.room import Room


class DatabaseUser:
    mongo_collection = mongo_database["users"]

    def __init__(self, telegram_account_id, room_token=None):
        self.telegram_account_id = telegram_account_id
        self.room_token = room_token
        self.hidden = False
        self.premium = False
        self.username = create_username(2)
        self.identifier = create_token(16)
        self.deactivated = False

    def reload(self):
        query = {"telegram_account_id": self.telegram_account_id}
        database_user_document = self.mongo_collection.find_one(query)
        self.telegram_account_id = database_user_document["telegram_account_id"]
        self.room_token = database_user_document["room_token"]
        self.hidden = database_user_document["hidden"]
        self.premium = database_user_document["premium"]
        self.username = database_user_document["username"]
        self.identifier = database_user_document["identifier"]
        self.deactivated = database_user_document["deactivated"]

    def exists(self):
        query = {"telegram_account_id": self.telegram_account_id}
        user_document = self.mongo_collection.find_one(query)
        return bool(user_document)

    def create(self, duplicate=False):
        if not duplicate and self.exists():
            return
        else:
            self.mongo_collection.insert_one(
                {
                    "telegram_account_id": self.telegram_account_id,
                    "room_token": self.room_token,
                    "hidden": self.hidden,
                    "premium": self.premium,
                    "username": self.username,
                    "identifier": self.identifier,
                    "deactivated": self.deactivated,
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
        if not room_token:
            return
        room = Room(token=room_token)
        room.refresh()
        self.modify_linked_room_token(new_room_token=None)
        room.increment_participants_count(-1)

    def set_new_username(self):
        query = {"telegram_account_id": self.telegram_account_id}
        self.mongo_collection.update_one(
            query,
            {"$set": {"username": create_username()}},
        )

    def set_hidden_true(self):
        query = {"telegram_account_id": self.telegram_account_id}
        self.mongo_collection.update_one(
            query,
            {"$set": {"hidden": True}},
        )

    def set_hidden_false(self):
        query = {"telegram_account_id": self.telegram_account_id}
        self.mongo_collection.update_one(
            query,
            {"$set": {"hidden": False}},
        )

    def set_premium_true(self):
        query = {"telegram_account_id": self.telegram_account_id}
        self.mongo_collection.update_one(
            query,
            {"$set": {"premium": True}},
        )

    def set_premium_false(self):
        query = {"telegram_account_id": self.telegram_account_id}
        self.mongo_collection.update_one(
            query,
            {"$set": {"premium": False}},
        )


def search_room_members(room_token):
    mongo_collection = DatabaseUser.mongo_collection
    room_members = mongo_collection.find({"room_token": room_token})
    room_members = list(room_members)
    if not room_members:
        return
    else:
        for room_member in room_members:
            yield DatabaseUser(
                room_member["telegram_account_id"],
                room_member["room_token"],
            )


def return_all_users() -> Iterator[DatabaseUser]:
    mongo_collection = DatabaseUser.mongo_collection
    room_members = mongo_collection.find()
    room_members = list(room_members)
    if not room_members:
        return
    else:
        for room_member in room_members:
            user = DatabaseUser(
                room_member["telegram_account_id"],
                room_member["room_token"],
            )
            user.reload()
            yield user


# def deactivate_user(telegram_account_id):
#     DatabaseUser.mongo_collection.update_one(
#         {"telegram_account_id": telegram_account_id},
#         {
#             "$set": {"deactivated": True},
#         },
#     )


# def reactivate_user(telegram_account_id):
#     DatabaseUser.mongo_collection.update_one(
#         {"telegram_account_id": telegram_account_id},
#         {
#             "$set": {"deactivated": False},
#         },
#     )

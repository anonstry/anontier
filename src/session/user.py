from collections.abc import Generator

from src.session import create_token, mongo_database
from src.session.room import Room


class User:
    mongo_collection = mongo_database["users"]

    def __init__(self, telegram_account_id, room_token=None):
        self.telegram_account_id = telegram_account_id
        self.room_token = room_token
        self.premium = False
        self.token = create_token(16)
        self.protected_transmition = True
        self.title = "Nothing here yet"

    def refresh(self):
        query = {"telegram_account_id": self.telegram_account_id}
        database_user_document = self.mongo_collection.find_one(query)
        assert database_user_document
        self.telegram_account_id = database_user_document["telegram_account_id"]
        self.room_token = database_user_document["room_token"]
        self.premium = database_user_document["premium"]
        self.protected_transmition = database_user_document.get(
            "protected_transmition", True
        )

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
                    "protected_transmition": self.protected_transmition,
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


def search_room_members(room_token):
    mongo_collection = User.mongo_collection

    room_members = mongo_collection.find({"room_token": room_token})
    room_members = list(room_members)
    if not room_members:
        return
    else:
        for room_member in room_members:
            yield User(room_member["telegram_account_id"], room_member["room_token"])


def return_all_users() -> Generator[User]:
    mongo_collection = User.mongo_collection

    room_members = mongo_collection.find()
    room_members = list(room_members)
    if not room_members:
        return
    else:
        for room_member in room_members:
            user = User(room_member["telegram_account_id"], room_member["room_token"])
            user.refresh()
            yield user


DatabaseUser = User

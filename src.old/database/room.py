from typing import Iterator

from loguru import logger

from src.database import mongo_database, create_token


class Room:
    mongo_collection = mongo_database["rooms"]

    def __init__(self, token=None, size_limit=2, hidden=False):
        self.token = token or create_token(24)
        self.size_limit = min(max(2, size_limit), 100)
        self.hidden = hidden
        self.participants_count = 0
        self.title = None  # @experimental

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
    sorting_number = -1 if sorting_number < 0 else 1
    telegram_room_document = Room.mongo_collection.find_one(
        filter={
            "hidden": False,
            "$and": [
                {"$expr": {"$lt": ["$participants_count", "$size_limit"]}},
                {"$expr": {"$gte": ["$participants_count", 1]}},
            ],
        },
        sort=[("participants_count", sorting_number)],
    )
    if not telegram_room_document:
        return
    else:
        return await TelegramRoom(
            token=telegram_room_document.token,
            hidden=telegram_room_document.hidden,
            size_limit=room_document["size_limit"],
        ).


def search_empty_rooms():
    empty_rooms = Room.mongo_collection.find({"participants_count": 0})
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


def return_all_rooms() -> Iterator[Room]:
    yield from Room.mongo_collection.find()


def delete_empty_rooms():
    logger.debug("Searching for all empty rooms...")
    "Delete rooms with no linked users"
    for room in search_empty_rooms():
        room.delete()
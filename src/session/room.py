from src.session import mongo_database, create_token


class Room:
    mongo_collection = mongo_database["rooms"]

    def __init__(self, token=None, size_limit=2, hidden=False):
        self.token = token or create_token(32)
        self.size_limit = max(2, size_limit)  # No lower than 2
        self.size_limit = min(10, self.size_limit)  # No higher than 10 (if not premium)
        self.token = token
        self.hidden = hidden
        self.participants_count = 0
        self.title = None # @experimental
        self.obrigatory_rules = None # @experimental
        self.restricted_users = None # @experimental
        self.restricted_rights = None # @experimental
        self.not_permited_users = None # @experimental
        self.muted_users = None # @experimental
        self.flood_wait = None # @experimental @maybe-redis

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
    mongo_collection = Room.mongo_collection

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
    mongo_collection = Room.mongo_collection

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
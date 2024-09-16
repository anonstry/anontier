from hydrogram import filters
from hydrogram.filters import Filter
from hydrogram.client import Client
from hydrogram.types import Message

from app.database.user import DatabaseUser


async def check_room_linked(_: Filter, __: Client, message: Message):
    database_user = DatabaseUser(message.from_user.id)
    database_user.create()
    database_user.reload()
    if not database_user.room_token:
        return False  # User is not linked to a room
    else:
        return True


filter_room_linked = filters.create(check_room_linked)
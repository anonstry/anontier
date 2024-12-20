from hydrogram import filters
from hydrogram.filters import Filter
from hydrogram.client import Client
from hydrogram.types import Message

from src.database import get_document_user_linked_room_token


async def check_room_linked(_: Filter, __: Client, message: Message):
    linked_room_token = await get_document_user_linked_room_token(message.from_user.id)
    if not linked_room_token:
        return False  # User is not linked to a room
    else:
        return True


linked_room__filter = filters.create(check_room_linked)

from hydrogram import filters

from src.session.user import DatabaseUser


async def _filter_room_linked(_, __, message):
    database_user = DatabaseUser(message.from_user.id)
    database_user.create()
    database_user.refresh()
    if not database_user.room_token:
        return False  # User is not linked to a room


filter_room_linked = filters.create(_filter_room_linked)
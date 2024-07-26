from hydrogram import filters

from src.session.user import DatabaseUser

async def filter_media_copiable(_, __, message):
    database_user = DatabaseUser(message.from_user.id)
    database_user.refresh()
    if not database_user.room_token:
        return False  # User is not linked to a room


media_copiable = filters.create(filter_media_copiable)
from hydrogram import filters
from hydrogram.client import Client
from hydrogram.errors.exceptions.forbidden_403 import UserIsBlocked
from hydrogram.types import Message
from loguru import logger

from src import client
from src.telegram.filters.room import filter_room_linked
from src.session.message import DatabaseMessage, search_correspondent_replied_message
from src.session.user import User as DatabaseUser
from src.session.user import search_room_members


async def send_single_message(
    client: Client,
    message: Message,
    database_message: DatabaseMessage,
    reply_to_message_id,
    room_member: DatabaseUser,
    from_database_user: DatabaseUser,
):
    try:
        new_message = await message.copy(
            room_member.telegram_account_id,
            reply_to_message_id=reply_to_message_id,
            protect_content=from_database_user.protected_transmition,
        )
        database_new_message = DatabaseMessage(
            from_telegram_chat_id=room_member.telegram_account_id,
            from_room_token=room_member.room_token,
            telegram_message_id=new_message.id,
            from_primary_room_token=from_database_user.room_token,
            from_primary_message_token=database_message.token,
        )
        database_new_message.create()
    except UserIsBlocked:
        room_token = room_member.room_token
        room_member.unlink_room(room_token)
        room_member.delete()


@client.on_message(
    filters.private
    & filter_room_linked
    & ~filters.media_group
    & ~filters.command(str())
)
async def broadcast(client: Client, message: Message):
    database_user = DatabaseUser(message.from_user.id)
    database_user.create()
    database_user.refresh()
    database_message = DatabaseMessage(
        from_telegram_chat_id=message.chat.id,
        from_room_token=database_user.room_token,
        telegram_message_id=message.id,
    )
    database_message.create()
    database_message.refresh()
    room_members = list(
        filter(
            lambda room_member: room_member
            and room_member.telegram_account_id != database_user.telegram_account_id,
            search_room_members(database_user.room_token),
        )
    )
    for room_member in room_members:
        reply_to_message_id = None
        if message.reply_to_message_id:
            try:
                database_reply_to_message = DatabaseMessage(
                    from_telegram_chat_id=message.chat.id,
                    from_room_token=database_user.room_token,
                    telegram_message_id=message.reply_to_message_id,
                )
                database_reply_to_message.refresh()
                database_linked_reply_to_message = search_correspondent_replied_message(
                    where_telegram_chat_id=room_member.telegram_account_id,
                    where_room_token=room_member.room_token,
                    with_primary_message_token=database_reply_to_message.from_primary_message_token
                    or database_reply_to_message.token,
                )
            except AssertionError:
                logger.error(
                    "Could not find which message(s) is being replied in the current room!"
                )
            else:
                reply_to_message_id = (
                    database_linked_reply_to_message.telegram_message_id
                )
        await send_single_message(
            client,
            message,
            database_message,
            reply_to_message_id,
            room_member,
            database_user,
        )
    message.stop_propagation()

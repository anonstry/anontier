from hydrogram import filters
from hydrogram.client import Client
from hydrogram.errors import InputUserDeactivated, UserIsBlocked
from hydrogram.types import Message
from loguru import logger

from app.database.message import DatabaseMessage, return_correspondent_message
from app.database.user import DatabaseUser, search_room_members
from app.modules.connection import add_message_header
from app.telegram.filters.room import filter_room_linked
from app.database.restriction import check_user_block


async def send_single_message(
    client: Client,
    message: Message,
    database_message: DatabaseMessage,
    reply_to_message_id,
    room_member: DatabaseUser,
    from_database_user: DatabaseUser,
):
    try:
        if not message.text:
            new_message = await message.copy(
                room_member.telegram_account_id,
                caption=add_message_header(message, from_database_user),
                reply_to_message_id=reply_to_message_id,
            )
        else:
            new_message = await client.send_message(
                room_member.telegram_account_id,
                add_message_header(message, from_database_user),
                protect_content=True,
                reply_to_message_id=reply_to_message_id,
            )
        database_new_message = DatabaseMessage(
            label="bridge",
            where_telegram_chat_id=room_member.telegram_account_id,
            where_room_token=room_member.room_token,
            telegram_message_id=new_message.id,
            from_root_room_token=from_database_user.room_token,
            from_root_message_token=database_message.identifier,
            expiration_timestamp=database_message.expiration_timestamp,
        )
        database_new_message.create()
    except (UserIsBlocked, InputUserDeactivated):
        room_token = room_member.room_token
        room_member.unlink_room(room_token)
        room_member.delete()


@Client.on_message(
    filters.private
    & filter_room_linked
    & ~filters.regex("^/")
    # & ~filters.command
    & ~filters.media_group
)
async def broadcast(client: Client, message: Message):
    database_user = DatabaseUser(message.from_user.id)
    database_user.create()
    database_user.reload()
    database_message = DatabaseMessage(
        label="bridge",
        where_telegram_chat_id=message.chat.id,
        where_room_token=database_user.room_token,
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
        if check_user_block(
            where_room_token=database_user.room_token,
            telegram_account_id=message.from_user.id,
            applied_by_telegram_account_id=room_member.telegram_account_id,
        ):
            return
        reply_to_message_id = None
        if message.reply_to_message_id:
            try:
                database_reply_to_message = DatabaseMessage(
                    where_telegram_chat_id=message.chat.id,
                    where_room_token=database_user.room_token,
                    telegram_message_id=message.reply_to_message_id,
                )
                database_reply_to_message.refresh()
                document_message = return_correspondent_message(
                    where_telegram_chat_id=room_member.telegram_account_id,
                    where_room_token=room_member.room_token,
                    linked_root_message_identifier=database_reply_to_message.from_root_message_token
                    or database_reply_to_message.identifier,
                )
                reply_to_message_id = document_message["telegram_message_id"]
            except (AssertionError, TypeError, KeyError):
                logger.error("A replied message was not found!")
        await send_single_message(
            client,
            message,
            database_message,
            reply_to_message_id,
            room_member,
            database_user,
        )

    message.stop_propagation()

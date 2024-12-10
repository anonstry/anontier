from contextlib import suppress

from hydrogram import filters
from hydrogram.client import Client
from hydrogram.errors import MessageIdInvalid, MessageNotModified
from hydrogram.types import Message

from src.database.message import (
    DatabaseMessage,
    search_for_original_messages_with_id,
    search_linked_messages,
)
from src.database.user import DocumentU
from src.modules.connection import add_message_header
from src.telegram.tools.media import mount_input_media

from loguru import logger


@Client.on_edited_message(filters.private & filters.text)
async def edit_linked_message_text(client: Client, message: Message):
    
    
    document_user = DocumentUser()
    database_user = DatabaseUser(message.from_user.id)
    database_user.create()
    database_user.reload()
    
    document_user = 
    
    database_message = DatabaseMessage(
        where_telegram_chat_id=message.chat.id,
        where_room_token=database_user.room_token,
        telegram_message_id=message.id,
    )
    database_message.create()
    database_message.refresh()
    database_linked_messages = search_linked_messages(database_message.identifier)
    for database_linked_message in database_linked_messages:
        linked_message = await client.get_messages(
            database_linked_message["where_telegram_chat_id"],
            database_linked_message["telegram_message_id"],
        )
        await linked_message.edit(
            add_message_header(message, database_user),
            reply_markup=linked_message.reply_markup,
        )
    else:
        logger.error("Found no linked messages to edit")


@Client.on_edited_message(filters.private & filters.media)
async def edit_linked_message_media(client: Client, message: Message):
    database_user = DatabaseUser(message.from_user.id)
    database_user.create()
    database_user.reload()
    database_message = DatabaseMessage(
        where_telegram_chat_id=message.chat.id,
        where_room_token=database_user.room_token,
        telegram_message_id=message.id,
    )
    database_message.create()
    database_message.refresh()
    database_linked_messages = search_linked_messages(database_message.identifier)
    message_media = getattr(message, message.media.value)
    input_media = await mount_input_media(client, message, message_media)
    assert input_media
    for database_linked_message in database_linked_messages:
        linked_message = await client.get_messages(
            database_linked_message["where_telegram_chat_id"],
            database_linked_message["telegram_message_id"],
        )
        with suppress(MessageNotModified):
            await linked_message.edit_media(
                input_media,
                reply_markup=linked_message.reply_markup,
            )
        with suppress(MessageNotModified):
            await linked_message.edit_caption(
                add_message_header(message, database_user),
                reply_markup=linked_message.reply_markup,
            )
    else:
        logger.error("Found no linked messages to edit")


@Client.on_deleted_messages()
async def delete_linked_messages(client: Client, messages: list[Message]):
    for deleted_message in messages:
        for database_message in search_for_original_messages_with_id(
            deleted_message.id
        ):
            database_linked_messages = search_linked_messages(
                database_message.identifier
            )
            for database_linked_message in database_linked_messages:
                with suppress(MessageIdInvalid):  # Instead of "Except"
                    linked_message = await client.get_messages(
                        database_linked_message["where_telegram_chat_id"],
                        database_linked_message["telegram_message_id"],
                    )
                    if (
                        linked_message
                        and linked_message.from_user
                        and linked_message.from_user.username == client.me.username
                    ):
                        await linked_message.delete()
                        database_linked_message = DatabaseMessage(
                            database_linked_message["where_telegram_chat_id"],
                            database_linked_message["where_room_token"],
                            database_linked_message["telegram_message_id"],
                        )
                        database_linked_message.delete()
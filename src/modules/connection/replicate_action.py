from contextlib import suppress

from hydrogram import filters
from hydrogram.client import Client
from hydrogram.errors.exceptions.bad_request_400 import (
    MessageIdInvalid,
    MessageNotModified,
)
from hydrogram.types import Message

from src import client
from src.session.message import DatabaseMessage
from src.session.message import (
    search_for_original_messages_with_id,
    search_linked_messages,
)
from src.session.user import DatabaseUser
from src.telegram.methods import mount_input_media


@client.on_edited_message(filters.private & filters.text)
async def edit_linked_message_text(client: Client, message: Message):
    user = DatabaseUser(message.from_user.id)
    user.create()
    user.refresh()
    database_message = DatabaseMessage(
        from_telegram_chat_id=message.chat.id,
        from_room_token=user.room_token,
        telegram_message_id=message.id,
    )
    database_message.create()
    database_message.refresh()
    database_linked_messages = search_linked_messages(database_message.token)
    for database_linked_message in database_linked_messages:
        await client.edit_message_text(
            database_linked_message.from_telegram_chat_id,
            database_linked_message.telegram_message_id,
            message.text,
        )


@client.on_edited_message(filters.private & filters.media)
async def edit_linked_message_media(client: Client, message: Message):
    print("Message media")
    user = DatabaseUser(message.from_user.id)
    user.create()
    user.refresh()
    database_message = DatabaseMessage(
        from_telegram_chat_id=message.chat.id,
        from_room_token=user.room_token,
        telegram_message_id=message.id,
    )
    database_message.create()
    database_message.refresh()
    database_linked_messages = search_linked_messages(database_message.token)
    message_media = getattr(message, message.media.value)
    input_media = await mount_input_media(client, message, message_media)
    assert input_media
    for database_linked_message in database_linked_messages:
        try:
            await client.edit_message_media(
                database_linked_message.from_telegram_chat_id,
                database_linked_message.telegram_message_id,
                input_media,
            )
        except MessageNotModified:  # The media still the same
            await client.edit_message_caption(
                database_linked_message.from_telegram_chat_id,
                database_linked_message.telegram_message_id,
                message.caption or str(),
            )  # Try to edit or delete the caption


@client.on_deleted_messages()
async def delete_linked_messages(client: Client, messages: list[Message]):
    for deleted_message in messages:
        for database_message in search_for_original_messages_with_id(
            deleted_message.id
        ):
            database_linked_messages = search_linked_messages(database_message.token)
            for database_linked_message in database_linked_messages:
                with suppress(MessageIdInvalid):  # Instead of "Except"
                    await client.delete_messages(
                        database_linked_message.from_telegram_chat_id,
                        database_linked_message.telegram_message_id,
                    )

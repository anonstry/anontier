from contextlib import suppress

from hydrogram import filters
from hydrogram.client import Client
from hydrogram.errors.exceptions.bad_request_400 import (
    MessageIdInvalid,
    MessageNotModified,
)
from hydrogram.types import Message

from src.session.message import DatabaseMessage
from src.session.message import (
    search_for_original_messages_with_id,
    search_linked_messages,
)
from src.session.user import DatabaseUser
from src.telegram.tools.media import mount_input_media


@Client.on_edited_message(filters.private & filters.text)
async def edit_linked_message_text(client: Client, message: Message):
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
    database_linked_messages = search_linked_messages(database_message.token)
    for database_linked_message in database_linked_messages:
        await client.edit_message_text(
            database_linked_message.from_telegram_chat_id,
            database_linked_message.telegram_message_id,
            message.text.html,
        )


@Client.on_edited_message(filters.private & filters.media)
async def edit_linked_message_media(client: Client, message: Message):
    print("Message media")
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
                message.caption.html or str(),
            )  # Try to edit or delete the caption


@Client.on_deleted_messages()
async def delete_linked_messages(client: Client, messages: list[Message]):
    for deleted_message in messages:
        for database_message in search_for_original_messages_with_id(
            deleted_message.id
        ):
            database_linked_messages = search_linked_messages(database_message.token)
            for database_linked_message in database_linked_messages:
                with suppress(MessageIdInvalid):  # Instead of "Except"
                    linked_message = await client.get_messages(
                        database_linked_message.from_telegram_chat_id,
                        database_linked_message.telegram_message_id,
                    )
                    if linked_message.from_user.username == client.me.username:
                        await linked_message.delete()

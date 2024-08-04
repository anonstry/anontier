from contextlib import suppress

from hydrogram import filters
from hydrogram.client import Client
from hydrogram.errors import MessageIdInvalid, MessageNotModified
from hydrogram.types import Message

from src.session.message import (
    DatabaseMessage,
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
        linked_message = await client.get_messages(
            database_linked_message["from_telegram_chat_id"],
            database_linked_message["telegram_message_id"],
        )
        await linked_message.edit(
            message.text.html,
            reply_markup=linked_message.reply_markup,
        )


@Client.on_edited_message(filters.private & filters.media)
async def edit_linked_message_media(client: Client, message: Message):
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
        linked_message = await client.get_messages(
            database_linked_message["from_telegram_chat_id"],
            database_linked_message["telegram_message_id"],
        )
        with suppress(MessageNotModified):
            await linked_message.edit_media(
                input_media,
                reply_markup=linked_message.reply_markup,
            )
        with suppress(MessageNotModified):
            if message.caption and message.caption.html:
                new_html_caption = message.caption.html
            else:
                new_html_caption = str()
            await linked_message.edit_caption(
                new_html_caption,
                reply_markup=linked_message.reply_markup,
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
                        database_linked_message["from_telegram_chat_id"],
                        database_linked_message["telegram_message_id"],
                    )
                    if (
                        linked_message
                        and linked_message.from_user
                        and linked_message.from_user.username == client.me.username
                    ):
                        await linked_message.delete()

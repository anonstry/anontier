from contextlib import suppress

from hydrogram import filters
from hydrogram.client import Client
from hydrogram.errors.exceptions.bad_request_400 import (
    MessageIdInvalid,
    MessageNotModified,
)
from hydrogram.types import Message
from loguru import logger

from src import client, methods, session


def implement():
    "Lazy function"
    logger.info("Module to mimic messages alterations was implemented")


@client.on_edited_message(filters.private & filters.text)
async def edit_linked_message_text(client: Client, message: Message):
    user = session.User(message.from_user.id)
    user.create()
    user.refresh()
    _message = session.Message(
        from_telegram_chat_id=message.chat.id,
        from_room_token=user.room_token,
        telegram_message_id=message.id,
    )
    _message.create()
    _message.refresh()
    _linked_messages = session.search_linked_messages(_message.token)
    for _linked_message in _linked_messages:
        await client.edit_message_text(
            _linked_message.from_telegram_chat_id,
            _linked_message.telegram_message_id,
            message.text,
        )


@client.on_edited_message(filters.private & filters.media)
async def edit_linked_message_media(client: Client, message: Message):
    print("Message media")
    user = session.User(message.from_user.id)
    user.create()
    user.refresh()
    _message = session.Message(
        from_telegram_chat_id=message.chat.id,
        from_room_token=user.room_token,
        telegram_message_id=message.id,
    )
    _message.create()
    _message.refresh()
    _linked_messages = session.search_linked_messages(_message.token)
    message_media = getattr(message, message.media.value)
    input_media = await methods.mount_input_media(client, message, message_media)
    if not input_media:
        return
    for _linked_message in _linked_messages:
        try:
            await client.edit_message_media(
                _linked_message.from_telegram_chat_id,
                _linked_message.telegram_message_id,
                input_media,
            )
        except MessageNotModified:  # The media did not change
            await client.edit_message_caption(
                _linked_message.from_telegram_chat_id,
                _linked_message.telegram_message_id,
                message.caption or str(),
            )


@client.on_deleted_messages()
async def delete_linked_messages(client: Client, messages: list[Message]):
    for deleted_message in messages:
        message_id = deleted_message.id
        try:
            _deleted_message = session.search_for_deleted_message_with_id(message_id)
        except AssertionError:  # No linked message found to delete
            return
        _deleted_message.create()
        _deleted_message.refresh()
        _linked_messages = session.search_linked_messages(_deleted_message.token)
        for _linked_message in _linked_messages:
            with suppress(MessageIdInvalid):  # Instead of "Except"
                await client.delete_messages(
                    _linked_message.from_telegram_chat_id,
                    _linked_message.telegram_message_id,
                )

from contextlib import suppress

from hydrogram import filters
from hydrogram.client import Client
from hydrogram.errors import MessageNotModified

# from hydrogram.errors import MessageIdInvalid, MessageNotModified
from hydrogram.types import InlineKeyboardMarkup, Message


from src.database import (
    get_document_message_from_generic_specifications,
    search_all_linked_messages,
)
from src._parser import add_message_header
from src.telegram.tools.media import mount_input_media
from src.telegram.filters.room import linked_room__filter


# from loguru import logger


@Client.on_edited_message(filters.private & filters.text & linked_room__filter)
async def edit_linked_message_text(client: Client, message: Message):
    if client.me is None:
        print("edit_linked_message_text: client.me is None")
        return

    source_document = await get_document_message_from_generic_specifications(
        where_telegram_client_id=client.me.id,
        where_telegram_chat_id=message.chat.id,
        telegram_message_id=message.id,
    )

    if source_document is None:
        print("edit_linked_message_text: source_document is None")
        return

    all_linked_messages = await search_all_linked_messages(source_document.family_id)
    if all_linked_messages:
        linked_documents = list(
            filter(
                lambda shadow_document: shadow_document.id != source_document.id,
                all_linked_messages,
            )
        )
    else:
        print("edit_linked_message_text: all_linked_messages is None")
        return

    for document in linked_documents:
        linked_message = await client.get_messages(
            document.where_telegram_chat_id,
            document.telegram_message_id,
        )

        if isinstance(linked_message, Message):
            if isinstance(linked_message.reply_markup, InlineKeyboardMarkup):
                await linked_message.edit(
                    await add_message_header(message),
                    reply_markup=linked_message.reply_markup,
                )
            else:
                await linked_message.edit(await add_message_header(message))
        else:
            print("edit_linked_message_text: linked_message are multiple messages")


@Client.on_edited_message(filters.private & filters.media)
async def edit_linked_message_media(client: Client, message: Message):
    source_document = await get_document_message_from_generic_specifications(
        where_telegram_client_id=client.me.id,
        where_telegram_chat_id=message.chat.id,
        telegram_message_id=message.id,
    )
    linked_documents = list(
        filter(
            lambda shadow_document: shadow_document.id != source_document.id,
            await search_all_linked_messages(source_document.family_id),
        )
    )
    message_media = getattr(message, message.media.value)
    input_media = await mount_input_media(client, message, message_media)
    assert input_media
    for document in linked_documents:
        linked_message = await client.get_messages(
            document.where_telegram_chat_id,
            document.telegram_message_id,
        )
        with suppress(MessageNotModified):
            await linked_message.edit_media(
                input_media,
                reply_markup=linked_message.reply_markup,
            )
        with suppress(MessageNotModified):
            await linked_message.edit_caption(
                await add_message_header(message),
                reply_markup=linked_message.reply_markup,
            )
    # else:
    #     logger.error("Found no linked messages to edit")


# @Client.on_deleted_messages()
# async def delete_linked_messages(client: Client, messages: list[Message]):
#     for deleted_message in messages:
#         for database_message in search_for_original_messages_with_id(
#             deleted_message.id
#         ):
#             database_linked_messages = search_linked_messages(
#                 database_message.identifier
#             )
#             for database_linked_message in database_linked_messages:
#                 with suppress(MessageIdInvalid):  # Instead of "Except"
#                     linked_message = await client.get_messages(
#                         database_linked_message["where_telegram_chat_id"],
#                         database_linked_message["telegram_message_id"],
#                     )
#                     if (
#                         linked_message
#                         and linked_message.from_user
#                         and linked_message.from_user.username == client.me.username
#                     ):
#                         await linked_message.delete()
#                         database_linked_message = DatabaseMessage(
#                             database_linked_message["where_telegram_chat_id"],
#                             database_linked_message["where_room_token"],
#                             database_linked_message["telegram_message_id"],
#                         )
#                         database_linked_message.delete()

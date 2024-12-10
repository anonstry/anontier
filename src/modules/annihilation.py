from hydrogram.client import Client
from hydrogram.types import Message
from hydrogram import filters
# from loguru import logger

from src.database import (
    get_document_message_from_generic_specifications,
    search_all_linked_messages,
    get_document_user_linked_room_token,
)


@Client.on_message(filters.private & filters.command("annihilate"))
async def annihilate(client: Client, message: Message):
    room_token = await get_document_user_linked_room_token(message.from_user.id)
    replied_message_document = await get_document_message_from_generic_specifications(
        where_telegram_client_id=client.me.id,
        where_telegram_chat_id=message.chat.id,
        where_room_token=room_token,
        telegram_message_id=message.reply_to_message_id,
    )
    documents = await search_all_linked_messages(
        family_id=replied_message_document.family_id
    )
    for document in documents:
        await client.delete_messages(
            document.where_telegram_chat_id,
            document.telegram_message_id,
        )
        await document.delete()
    await message.delete()
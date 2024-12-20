# Move to src.modules

from hydrogram import filters
from hydrogram.client import Client

# from hydrogram.raw.types import UpdateBotStopped
from hydrogram.types import CallbackQuery
# from loguru import logger

from src.modules import show_main_menu
from src.database import (
    create_document_room,
    get_document_user_linked_room_token,
    modify_document_room_participants_count,
    search_public_room_token,
    unlink_document_user_room_token,
    update_document_user_room_token,
)
from src.telegram.filters.room import linked_room__filter


@Client.on_message(
    filters.private & filters.command("unmatch-room") & linked_room__filter
)
async def suggest_match(client: Client, callback_query: CallbackQuery):
    caption = "You are not into a room yet. Try /match"
    await callback_query.message.reply(text=caption, quote=True)
    callback_query.message.stop_propagation()


@Client.on_callback_query(
    filters.private
    & (
        filters.regex("^match-room")
        | filters.regex("^create-public-room")
        | filters.regex("^create-private-room")
        | filters.regex("^create-room-invite-link")
    )
    & linked_room__filter,
)
async def suggest_unmatch(client: Client, callback_query: CallbackQuery):
    caption = "You already in a conversation/room."
    await callback_query.message.reply(text=caption, quote=True)
    callback_query.message.stop_propagation()


@Client.on_callback_query(
    filters.private & filters.regex("^match-room") & ~linked_room__filter
)
async def match_room(client: Client, callback_query: CallbackQuery):
    public_telegram_room_token = await search_public_room_token(sorting_number=1)
    if public_telegram_room_token:
        await update_document_user_room_token(
            callback_query.from_user.id,
            public_telegram_room_token,
        )
        await modify_document_room_participants_count(public_telegram_room_token, +1)
        caption = "You joined in a public room..."
        await callback_query.message.reply(caption)
    else:
        await callback_query.message.reply("No available public rooms.")
        document_room = await create_document_room()
        await update_document_user_room_token(
            callback_query.message.from_user.id, document_room.token
        )
        await modify_document_room_participants_count(document_room.token, +1)
        caption = "New public room created and started."
        await callback_query.message.reply(text=caption, quote=True)
    await show_main_menu(client, where_telegram_chat_id=callback_query.from_user.id)
    await callback_query.message.delete()


@Client.on_callback_query(
    filters.private & filters.regex("^create-public-room") & ~linked_room__filter
)
async def create_new_private_room(client: Client, callback_query: CallbackQuery):
    room_document = await create_document_room(size_limit=10)
    await update_document_user_room_token(
        callback_query.from_user.id, room_document.token
    )
    await show_main_menu(client, where_telegram_chat_id=callback_query.from_user.id)
    await callback_query.message.delete()


@Client.on_callback_query(
    filters.private & filters.regex("^create-private-room") & ~linked_room__filter
)
async def create_new_public_room(client: Client, callback_query: CallbackQuery):
    room_document = await create_document_room(size_limit=10, hidden=True)
    await update_document_user_room_token(
        callback_query.from_user.id, room_document.token
    )
    await show_main_menu(client, where_telegram_chat_id=callback_query.from_user.id)
    await callback_query.message.delete()


@Client.on_callback_query(
    filters.private & filters.regex("^unmatch-room") & linked_room__filter
)
async def unmatch_room(client: Client, callback_query: CallbackQuery):
    room_token = await get_document_user_linked_room_token(callback_query.from_user.id)
    await unlink_document_user_room_token(callback_query.from_user.id)
    await modify_document_room_participants_count(room_token, -1)
    caption = "You left the room."
    await callback_query.message.reply(text=caption)
    await show_main_menu(client, where_telegram_chat_id=callback_query.from_user.id)

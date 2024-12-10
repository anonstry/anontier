# Move to src.modules

from hydrogram import filters
from hydrogram.client import Client

# from hydrogram.raw.types import UpdateBotStopped
from hydrogram.types import Message
from loguru import logger

from src.database import (
    create_document_room,
    create_document_user,
    get_document_room,
    get_document_user_linked_room_token,
    modify_document_room_participants_count,
    search_public_room_token,
    unlink_document_user_room_token,
    update_document_user_room_token,
)
from src.telegram.filters.room import linked_room__filter
from src import client as hydrogramClient


@Client.on_message(self=hydrogramClient, filters=filters.private & filters.command("unmatch") & ~linked_room__filter)
async def suggest_match(client: Client, message: Message):
    caption = "You are not into a room yet. Try /match"
    await message.reply(text=caption, quote=True)
    message.stop_propagation()


@Client.on_message(
    self=hydrogramClient,
    filters=filters.private
    & (filters.command("join") | filters.command("party") | filters.command("match"))
    & linked_room__filter
)
async def suggest_unmatch(client: Client, message: Message):
    caption = "You already in a conversation/room. Try /unmatch"
    await message.reply(text=caption, quote=True)
    message.stop_propagation()


@Client.on_message(self=hydrogramClient, filters=filters.private & filters.command("unmatch") & linked_room__filter)
async def quit_room(client: Client, message: Message):
    room_token = await get_document_user_linked_room_token(message.from_user.id)
    await unlink_document_user_room_token(message.from_user.id)
    await modify_document_room_participants_count(room_token, -1)
    caption = "You left the room."
    new_message = await message.reply(text=caption)
    caption = "Start a new one: /match."
    await new_message.reply(text=caption, quote=True)
    # caption = "Someone left the room. Send /status to check."
    # await notify_room_members(client, caption, room.token)
    message.stop_propagation()


@Client.on_message(self=hydrogramClient, filters=filters.private & filters.command("match") & ~linked_room__filter)
async def match_room(client: Client, message: Message):
    await create_document_user(telegram_account_id=message.from_user.id)
    try:
        command = message.command
        if command:
            sorting_number = int(command[1])
        else:
            raise Exception("Command not found")
    except (IndexError, ValueError, Exception):  # Not exists or not integer
        sorting_number = 1
    public_telegram_room_token = await search_public_room_token(sorting_number)
    if public_telegram_room_token:
        await update_document_user_room_token(
            message.from_user.id, public_telegram_room_token
        )
        await modify_document_room_participants_count(public_telegram_room_token, +1)
        caption = "You joined in a public room.."
        _message = await message.reply(caption)
        caption = f"**Token to invite:** <code>{public_telegram_room_token}</code>"
        await _message.reply(caption)
        # caption = "**A partner connected.**\n __Someone joined in your room...__"
        # await notify_room_members(
        #     client,
        #     caption,
        #     room.token,
        #     exclude_telegram_accounts_ids=[user.telegram_account_id],
        # )
    else:
        await message.reply("No available public rooms.")
        document_room = await create_document_room()
        await update_document_user_room_token(message.from_user.id, document_room.token)
        await modify_document_room_participants_count(document_room.token, +1)
        caption = "New public room created and started."
        new_message = await message.reply(text=caption, quote=True)
        caption = f"**Token to invite:** <code>{document_room.token}</code>\n__Waiting for a partner to connect with...__"
        await new_message.reply(text=caption, quote=True)
    message.stop_propagation()


@Client.on_message(self=hydrogramClient, filters=filters.private & filters.command("nroom") & ~linked_room__filter)
async def create_new_room(client: Client, message: Message):
    try:
        command = message.command
        if command:
            room_size_limit = command[1]
        else:
            raise Exception("Command not found")
    except IndexError:
        caption = "You must write the room size limit!"
        await message.reply(text=caption, quote=True, protect_content=True)
        return
    try:
        room_size_limit = int(room_size_limit)
    except ValueError:
        caption = "You must provide a valid room size number!"
        await message.reply(text=caption, quote=True, protect_content=True)
        return
    if room_size_limit < 0:  # -1 or less
        hidden = True
    else:
        hidden = False
    room_size_limit = min(abs(room_size_limit), 10)
    #     if room_size_limit > 3 and not database_user.premium:
    #         caption = "You are not a /premium user to create a room bigger than 3."
    #         await message.reply(caption, quote=True)
    #         return
    room_document = await create_document_room(room_size_limit)
    await update_document_user_room_token(message.from_user.id, room_document.token)
    if not hidden:
        caption = "You created a new public room!"
    else:
        caption = "You created a new private room!"
    new_message = await message.reply(text=caption, quote=True, protect_content=True)
    await new_message.reply(f"**Token to invite:** <code>{room_document.token}</code>")
    # await notify_room_members(
    #     client,
    #     caption,
    #     room.token,

    #     exclude_telegram_accounts_ids=[user.telegram_account_id],
    # )
    message.stop_propagation()


@Client.on_message(self=hydrogramClient, filters=filters.private & filters.command("join") & ~linked_room__filter)
async def join_room(client: Client, message: Message):
    room_token = None
    try:
        command = message.command
        if command:
            room_token = command[1]
        else:
            raise Exception("Command not found")
    except IndexError:
        logger.error("A user provided an empty token!")
        caption = "You must provide a room token! Try /manual"
        await message.reply(text=caption, quote=True, protect_content=True)
        return
    try:
        assert room_token
        assert isinstance(room_token, str)
        assert await get_document_room(room_token)
    except AssertionError:
        caption = "You must provide a valid room token!"
        await message.reply(text=caption, quote=True, protect_content=True)
        return
    else:
        await update_document_user_room_token(message.from_user.id, room_token)
        caption = "Room linked successfully! Try /status"
        await message.reply(text=caption, quote=True)
        # new_message = await message.reply(text=caption, quote=True)
        # caption = f"Room invite link: t.me/{client.me.username}?room_token={room_token}"
        # await new_message.reply(text=caption, quote=True)  # def invite
        # caption = "**A partner connected.**\n __Someone joined in your room...__"
        # await notify_room_members(
        #     client,
        #     caption,
        #     room.token,
        #     exclude_telegram_accounts_ids=[user.telegram_account_id],
        # )
    message.stop_propagation()



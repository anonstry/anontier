from hydrogram import filters
from hydrogram.client import Client
from hydrogram.raw.types import UpdateBotStopped
from hydrogram.types import Message, Update
from loguru import logger

from src.sanitization import delete_empty_rooms
from src.session.room import Room, search_public_room
from src.session.user import DatabaseUser
from src.telegram.filters.room import filter_room_linked


@Client.on_raw_update()
async def bot_stopped(client: Client, update: Update, _, __):
    if isinstance(update, UpdateBotStopped) and update.stopped:
        database_user = DatabaseUser(update.user_id)
        database_user.refresh()
        room_token = database_user.room_token
        assert room_token
        database_user.unlink_room(room_token)
        database_user.delete()
        # caption = "__A member of your current room blocked the bot. See about the current /status!__"
        # await notify_room_members(client, caption, room_token)

@Client.on_message(filters.private & filters.command("unmatch") & ~filter_room_linked)
async def suggest_match(client: Client, message: Message):
    caption = "You are not into a room yet. Try /match"
    await message.reply(text=caption, quote=True)
    message.stop_propagation()


@Client.on_message(
    filters.private
    & (filters.command("join") | filters.command("party") | filters.command("match"))
    & filter_room_linked
)
async def suggest_unmatch(client: Client, message: Message):
    caption = "You already in a conversation/room. Try /unmatch"
    await message.reply(text=caption, quote=True)
    message.stop_propagation()


@Client.on_message(filters.private & filters.command("unmatch") & filter_room_linked)
async def quit_room(client: Client, message: Message):
    database_user = DatabaseUser(message.from_user.id)
    database_user.refresh()
    room = Room(database_user.room_token)
    database_user.unlink_room(room.token)
    caption = "You left the room."
    new_message = await message.reply(text=caption)
    caption = "Start a new one: /match."
    await new_message.reply(text=caption, quote=True)
    # caption = "Someone left the room. Send /status to check."
    # await notify_room_members(client, caption, room.token)
    delete_empty_rooms()
    message.stop_propagation()


@Client.on_message(filters.private & filters.command("match") & ~filter_room_linked)
async def match_room(client: Client, message: Message):
    database_user = DatabaseUser(message.from_user.id)
    database_user.refresh()
    try:
        sorting_number = int(message.command[1])
    except (IndexError, ValueError, Exception):  # Not exists or not integer
        sorting_number = 1
    room = search_public_room(sorting_number)
    available_public_room = bool(room)
    if not available_public_room:
        await message.reply("No available public rooms.")
        database_user.link_new_room()
        room = Room(database_user.room_token)
        room.create()
        room.refresh()
        caption = "New public room started."
        new_message = await message.reply(text=caption, quote=True)
        caption = f"**Token to invite:** <code>{room.token}</code>\n__Waiting for a partner to connect with...__"
        await new_message.reply(text=caption, quote=True)
    else:
        database_user.link_room(room.token)
        caption = "You joined in a public room.."
        _message = await message.reply(caption)
        caption = f"**Token to invite:** <code>{room.token}</code>"
        await _message.reply(caption)
        # caption = "**A partner connected.**\n __Someone joined in your room...__"
        # await notify_room_members(
        #     client,
        #     caption,
        #     room.token,
        #     exclude_telegram_accounts_ids=[user.telegram_account_id],
        # )
    message.stop_propagation()


@Client.on_message(filters.private & filters.command("party") & ~filter_room_linked)
async def create_party(client: Client, message: Message):
    database_user = DatabaseUser(message.from_user.id)
    database_user.refresh()
    try:
        room_size_limit = message.command[1]
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
    if room_size_limit < 0:
        hidden = True
    else:
        hidden = False
    room_size_limit = abs(room_size_limit)
    room = Room(size_limit=room_size_limit, hidden=hidden)
    room.create()
    room.refresh()
    database_user.link_room(room.token)
    if hidden:
        caption = "You created a new private room/party!"
    else:
        caption = "You created a new public room/party!"
    new_message = await message.reply(text=caption, quote=True, protect_content=True)
    await new_message.reply(f"**Token to invite:** <code>{room.token}</code>")
    # await notify_room_members(
    #     client,
    #     caption,
    #     room.token,
    #     exclude_telegram_accounts_ids=[user.telegram_account_id],
    # )
    message.stop_propagation()


@Client.on_message(filters.private & filters.command("join") & ~filter_room_linked)
async def join_room(client: Client, message: Message):
    database_user = DatabaseUser(message.from_user.id)
    database_user.refresh()
    room_token = None
    try:
        room_token = message.command[1]
    except IndexError:
        logger.error("A user provided an empty token!")
        caption = "You must provide a room token! Try /manual"
        await message.reply(text=caption, quote=True, protect_content=True)
        return
    try:
        room = Room(room_token)
        room.refresh()
    except AssertionError:
        logger.error("A user provided an invalid token!")
        caption = "You must provide a valid room token!"
        await message.reply(text=caption, quote=True, protect_content=True)
        return
    database_user.link_room(room_token)
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

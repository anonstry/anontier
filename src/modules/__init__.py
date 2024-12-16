from pathlib import Path

from hydrogram import filters
from hydrogram.client import Client
from hydrogram.raw.types import UpdateBotStopped
from hydrogram.types import Message, Update

from re import compile

from src.database import (
    deactivate_document_user,
    unlink_document_user_room_token,
    create_document_user,
)
from src.telegram.filters.room import linked_room__filter
from src.database import (
    update_document_user_room_token,
    get_document_user_linked_room_token,
)


@Client.on_message(filters.private, group=-1)
async def register(client, message: Message):
    await create_document_user(message.from_user.id)


# def advice to use a command
# def dynamic rotative username


@Client.on_message(filters.private & filters.command("link"))
async def create_room_link(client: Client, message: Message):
    room_token = await get_document_user_linked_room_token(message.from_user.id)
    await message.reply(
        f"https://t.me/{client.me.username}?start=join-room-token={room_token}"
    )


@Client.on_message(filters.private & filters.command("start"))
async def join_using_room_link(client: Client, message: Message):
    pattern = compile(r"^join-room-token=")
    if not len(message.command) > 1:
        return
    if not pattern.match(message.command[1]):
        return

    room_token = pattern.split(message.command[1])[1]

    await update_document_user_room_token(message.from_user.id, room_token)

    await message.reply(f"You entered in a room (token: {room_token})")

    message.stop_propagation()


@Client.on_message(filters.private & filters.command("start") & ~linked_room__filter)
async def initialize(client, message: Message):
    caption_text = Path("assets/texts/initialization.txt").read_text()
    photo_filepath = Path("assets/images/initialization.jpg")
    if photo_filepath.exists():
        await message.reply_photo(str(photo_filepath), caption=caption_text, quote=True)
    message.stop_propagation()


@Client.on_raw_update()
async def bot_stopped(client: Client, update: Update, __, ___):
    if isinstance(update, UpdateBotStopped) and update.stopped:
        await unlink_document_user_room_token(update.user_id)
        await deactivate_document_user(update.user_id)

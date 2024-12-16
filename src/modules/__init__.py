from pathlib import Path

from hydrogram import filters
from hydrogram.client import Client
from hydrogram.raw.types import UpdateBotStopped
from hydrogram.types import Message, Update

from src.database import (
    deactivate_document_user,
    unlink_document_user_room_token,
    create_document_user,
)
from src.telegram.filters.room import linked_room__filter


@Client.on_message(filters=filters.private, group=-1)
async def register(_, message: Message):
    await create_document_user(message.from_user.id)


# def advice to use a command
# def dynamic rotative username

@Client.on_message(filters=filters.private & filters.command("start") & ~linked_room__filter)
async def initialize(_, message: Message):
    caption_text = Path("assets/texts/initialization.txt").read_text()
    photo_filepath = Path("assets/images/initialization.jpg")
    if photo_filepath.exists():
        await message.reply_photo(str(photo_filepath), caption=caption_text, quote=True)
    message.stop_propagation()


@Client.on_raw_update()
async def bot_stopped(_: Client, update: Update, __, ___):
    if isinstance(update, UpdateBotStopped) and update.stopped:
        await unlink_document_user_room_token(update.user_id)
        await deactivate_document_user(update.user_id)

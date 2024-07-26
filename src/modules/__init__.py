from pathlib import Path

from hydrogram import filters
from hydrogram.client import Client
from hydrogram.enums import ChatAction
from hydrogram.types import Message

from src.session.user import DatabaseUser
from src.telegram.filters.room import filter_room_linked


@Client.on_message(filters.private & filters.command("start") & ~filter_room_linked)
async def initialize(client: Client, message: Message):
    database_user = DatabaseUser(message.from_user.id)
    database_user.create()
    database_user.refresh()
    file = Path("messages/initialization.txt")
    caption = file.read_text()
    await message.reply(text=caption, quote=True)
    message.stop_propagation()


@Client.on_message(filters.group)
async def send_typing_signal(client: Client, message: Message):
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)

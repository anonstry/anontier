from pathlib import Path

from hydrogram import filters
from hydrogram.client import Client
from hydrogram.types import Message
from loguru import logger

from .. import client, session


def implement():
    "Lazy function"
    logger.info("Module to catch guidelines commands was implemented")


@client.on_message(filters.private & filters.command("start"))
async def initialize(client: Client, message: Message):  # initialization
    user = session.User(message.from_user.id)
    user.create()
    user.refresh()
    if user.room_token:
        caption = "You already in a conversation"
        await message.reply(text=caption, quote=True)
        return
    file = Path("messages/initialization.txt")
    caption = file.read_text()
    await message.reply(text=caption, quote=True)
    message.stop_propagation()
    # The max size for a url parameter is 64


@client.on_message(filters.private & filters.command("status"))
async def show_bot_status(client: Client, message: Message):
    user = session.User(message.from_user.id)
    user.create()
    user.refresh()
    room = session.Room(user.room_token)
    file = Path("messages/dynamic/status.txt")
    try:
        room.refresh()
        caption = file.read_text().format(
            INSTANCE_USERNAME=client.me.username,
            ROOM_TOKEN=room.token,
            ROOM_PARTICIPANTS_COUNT=room.participants_count,
            ROOM_SIZE_LIMIT=room.size_limit,
        )
    except AssertionError:
        caption = file.read_text().format(
            INSTANCE_USERNAME=client.me.username,
            ROOM_TOKEN="Null",
            ROOM_PARTICIPANTS_COUNT="Null",
            ROOM_SIZE_LIMIT="Null",
        )
    await message.reply(text=caption, quote=True)
    message.stop_propagation()


@client.on_message(filters.private & filters.command("manual"))
async def show_bot_manual(client: Client, message: Message):
    file = Path("messages/manual.txt")
    caption = file.read_text()
    await message.reply(text=caption, quote=True)
    message.stop_propagation()


@client.on_message(filters.private & filters.command("terms"))
async def show_bot_terms(client: Client, message: Message):
    file = Path("messages/terms.txt")
    caption = file.read_text()
    await message.reply(
        text=caption,
        quote=True,
        protect_content=True,
        disable_web_page_preview=True,
    )
    message.stop_propagation()

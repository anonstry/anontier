from pathlib import Path

from hydrogram import filters
from hydrogram.client import Client
from hydrogram.types import Message

from src.session.user import DatabaseUser
from src.session.room import Room
from src import latest_git_repository_commit_shorted

@Client.on_message(filters.private & filters.command("status"))
async def show_bot_status(client: Client, message: Message):
    database_user = DatabaseUser(message.from_user.id)
    database_user.create()
    database_user.refresh()
    room = Room(database_user.room_token)
    file = Path("messages/dynamic/status.txt")
    try:
        room.refresh()
        caption = file.read_text().format(
            INSTANCE_USERNAME=client.me.username,
            LAST_COMMIT=latest_git_repository_commit_shorted,
            ROOM_TOKEN=room.token,
            ROOM_PARTICIPANTS_COUNT=room.participants_count,
            ROOM_SIZE_LIMIT=room.size_limit,
        )
    except AssertionError:
        caption = file.read_text().format(
            INSTANCE_USERNAME=client.me.username,
            LAST_COMMIT=latest_git_repository_commit_shorted,
            ROOM_TOKEN="Null",
            ROOM_PARTICIPANTS_COUNT="Null",
            ROOM_SIZE_LIMIT="Null",
        )
    await message.reply(text=caption, quote=True)
    message.stop_propagation()


@Client.on_message(filters.private & filters.command("manual"))
async def show_bot_manual(client: Client, message: Message):
    file = Path("messages/manual.txt")
    caption = file.read_text()
    await message.reply(text=caption, quote=True)
    message.stop_propagation()


@Client.on_message(filters.private & filters.command("terms"))
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

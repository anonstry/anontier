from pathlib import Path

from hydrogram import filters
from hydrogram.client import Client
from hydrogram.types import Message

from src.database.user import DatabaseUser
from src.database.room import Room
from src import latest_git_repository_commit_shorted, git_repository_remote_link


@Client.on_message(filters.private & filters.command("status"))
async def show_bot_status(client: Client, message: Message):
    database_user = DatabaseUser(message.from_user.id)
    database_user.create()
    database_user.reload()
    room = Room(database_user.room_token)
    file = Path("assets/texts/dynamic/status.txt")
    try:
        room.refresh()
        caption = file.read_text().format(
            INSTANCE_USERNAME=client.me.username,
            REPOSITORY_REMOTE_LINK=git_repository_remote_link,
            LAST_COMMIT=latest_git_repository_commit_shorted,
            ROOM_TOKEN=room.token,
            ROOM_PARTICIPANTS_COUNT=room.participants_count,
            ROOM_SIZE_LIMIT=room.size_limit,
        )
    except AssertionError:
        caption = file.read_text().format(
            INSTANCE_USERNAME=client.me.username,
            REPOSITORY_REMOTE_LINK=git_repository_remote_link,
            LAST_COMMIT=latest_git_repository_commit_shorted,
            ROOM_TOKEN="Null",
            ROOM_PARTICIPANTS_COUNT="Null",
            ROOM_SIZE_LIMIT="Null",
        )
    await message.reply(text=caption, quote=True, disable_web_page_preview=True)
    message.stop_propagation()


@Client.on_message(filters.private & filters.command("manual"))
async def show_bot_manual(client: Client, message: Message):
    file = Path("assets/texts/manual.txt")
    caption = file.read_text()
    await message.reply(text=caption, quote=True)
    message.stop_propagation()


@Client.on_message(filters.private & filters.command("terms"))
async def show_bot_terms(client: Client, message: Message):
    file = Path("assets/texts/terms.txt")
    caption = file.read_text()
    await message.reply(
        text=caption,
        quote=True,
        protect_content=True,
        disable_web_page_preview=True,
    )
    message.stop_propagation()


@Client.on_message(filters.private & filters.command("donation"))
async def show_bot_donation_guide(client: Client, message: Message):
    file = Path("assets/texts/donation.txt")
    caption = file.read_text()
    await message.reply(
        text=caption,
        quote=True,
        protect_content=True,
        disable_web_page_preview=True,
    )
    message.stop_propagation()


@Client.on_message(filters.private & filters.command("premium"))
async def show_bot_premium_guide(client: Client, message: Message):
    database_user = DatabaseUser(message.from_user.id)
    database_user.create()
    database_user.reload()
    if database_user.premium:
        caption = "❖ **Premium activated.**\nThank you for supporting the project!\nAnd if you want the help us more, try a /donation"
        await message.reply(caption, quote=True)
    else:
        caption = Path("assets/texts/premium.txt").read_text()
        filepath = Path("assets/images/premium.jpg")
        await client.send_photo(
            message.chat.id,
            photo=str(filepath),
            caption=caption,
            protect_content=True,
            reply_to_message_id=message.id,
            # disable_web_page_preview=True,
        )
    message.stop_propagation()

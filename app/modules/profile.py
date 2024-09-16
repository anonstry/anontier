from pathlib import Path

from hydrogram import filters
from hydrogram.client import Client
from hydrogram.types import Message

from app.database.user import DatabaseUser


@Client.on_message(filters.command("tagme"))
async def new_username(client: Client, message: Message):
    database_user = DatabaseUser(message.from_user.id)
    database_user.create()
    database_user.reload()

    if database_user.username:
        await message.reply("↻ Recreating your username")
    else:
        await message.reply("🛈 Creating a new username")

    database_user.set_new_username()
    database_user.reload()
    caption = f"ꜝYour new username is: **{database_user.username}**"
    filepath = Path("assets/images/new_username.jpg")
    await message.reply_photo(str(filepath), quote=True, caption=caption)


@Client.on_message(filters.command("hideme"))
async def enable_user_hidden_mode(client: Client, message: Message):
    database_user = DatabaseUser(message.from_user.id)
    database_user.create()
    database_user.reload()

    if not database_user.premium:
        caption = "ꜝYou are not a /premium user to do that."
        await message.reply(caption, quote=True)
        message.stop_propagation()
        return
    elif database_user.hidden:
        caption = "ꜝYou are already in the hidden mode."
        await message.reply(caption, quote=True)
        return
    else:
        database_user.set_hidden_true()
        database_user.reload()
        caption = "ꜝUsername disabled. Now you are hidden."
        filepath = Path("assets/images/enable_user_hidden_mode.jpg")
        await message.reply_photo(str(filepath), quote=True, caption=caption)


@Client.on_message(filters.command("unhideme"))
async def disable_user_hidden_mode(client: Client, message: Message):
    database_user = DatabaseUser(message.from_user.id)
    database_user.create()
    database_user.reload()

    if not database_user.hidden:
        await message.reply("ꜝYou are not in the hidden mode.")
    else:
        database_user.set_hidden_false()
        database_user.reload()
        caption = "ꜝUsername enabled. Now you are no longer hidden."
        filepath = Path("assets/images/disable_user_hidden_mode.jpg")
        await message.reply_photo(str(filepath), quote=True, caption=caption)

from hydrogram import filters
from hydrogram.client import Client
from hydrogram.raw.types import UpdateBotStopped
from hydrogram.types import Message, Update

from src import client
from src.session.user import User as DatabaseUser
from src.telegram.filters.room import filter_room_linked


@client.on_message(filters.private & filters.command("unmatch") & ~filter_room_linked)
async def suggest_match(client: Client, message: Message):
    caption = "You are not into a room yet. Try /match"
    await message.reply(text=caption, quote=True)
    message.stop_propagation()


@client.on_message(
    filters.private
    & (filters.command("join") | filters.command("party") | filters.command("match"))
    & filter_room_linked
)
async def suggest_unmatch(client: Client, message: Message):
    caption = "You already in a conversation/room. Try /unmatch"
    await message.reply(text=caption, quote=True)


@client.on_raw_update()
async def bot_stopped(client: Client, update: Update, _, __):
    if isinstance(update, UpdateBotStopped) and update.stopped:
        user = DatabaseUser(update.user_id)
        user.refresh()
        room_token = user.room_token
        assert room_token
        user.unlink_room(room_token)
        user.delete()
        # caption = "__A member of your current room blocked the bot. See about the current /status!__"
        # await notify_room_members(client, caption, room_token)

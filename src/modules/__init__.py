from re import compile

from hydrogram import filters
from hydrogram.client import Client
from hydrogram.raw.types import UpdateBotStopped
from hydrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    Update,
)

from src.database import (
    create_document_user,
    deactivate_document_user,
    get_document_user_linked_room_token,
    get_document_user_protection_status,
    unlink_document_user_room_token,
    update_document_user_room_token,
)

# from src.telegram.filters.room import linked_room__filter


@Client.on_message(filters.private, group=-1)
async def register(client, message: Message):
    await create_document_user(message.from_user.id)


@Client.on_message(filters.private & filters.command("start"))
async def join_using_room_link(client: Client, message: Message):
    pattern = compile(r"^join-room-token=")
    if not len(message.command) > 1:
        return
    if not pattern.match(message.command[1]):
        return

    room_token = pattern.split(message.command[1])[1]

    if room_token == "None":
        await message.reply("Send /config or /c again and match a room")
        await message.stop_propagation()
        return

    await update_document_user_room_token(message.from_user.id, room_token)

    await message.reply(f"You entered in a room (token: {room_token})")


async def show_main_menu(client, where_telegram_chat_id):
    # Depois pode ser possível um "mount_main_menu" e um "mount_main_menu_without_about_room"
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("• ROOM •", "about-rooms")],
            [
                InlineKeyboardButton("match a room", "match-room"),
                InlineKeyboardButton("unmatch a room", "unmatch-room"),
            ],
            [
                InlineKeyboardButton("create a public room", "create-public-room"),
                InlineKeyboardButton("create a private room", "create-private-room"),
            ],
        ]
    )

    room_token = await get_document_user_linked_room_token(where_telegram_chat_id)
    room_invite_link = f"t.me/{client.me.username}?start=join-room-token={room_token}"

    await client.send_message(
        where_telegram_chat_id,
        f"Hi [#u{where_telegram_chat_id}]\n"
        f"Your linked room invite link: {room_invite_link}\n\n"
        f"  **• Allow forwarding:** {await get_document_user_protection_status(where_telegram_chat_id)}`\n",
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


@Client.on_message(
    filters.private
    & (filters.command("start") | filters.command("config") | filters.command("c"))
)
async def initialize(client, message: Message):
    await show_main_menu(client, where_telegram_chat_id=message.from_user.id)


@Client.on_raw_update()
async def bot_stopped(client: Client, update: Update, __, ___):
    if isinstance(update, UpdateBotStopped) and update.stopped:
        await unlink_document_user_room_token(update.user_id)
        await deactivate_document_user(update.user_id)

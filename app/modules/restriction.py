# Local preferences for a user
# Seria bom uma função pra adicionar lifetime às mensagens

from hydrogram import filters
from hydrogram.client import Client
from hydrogram.types import Message

from app.database.user import DatabaseUser
from app.database.message import DatabaseMessage, return_root_message
from app.database.restriction import new_user_block, delete_user_block


@Client.on_message(
    filters.private
    & ~filters.reply
    & (filters.command("ignore") | filters.command("signore"))
)
async def show_usage_suggestion(client: Client, message: Message):
    caption = "ꜝYou need to reply a user message first."
    await message.reply(caption, quote=True)
    message.stop_propagation()
    return


# Lembrar de depois adicionar um tempo personalizável
@Client.on_message(filters.private & filters.command("ignore"))
async def ignore_user(client: Client, message: Message):
    database_user = DatabaseUser(message.from_user.id)
    database_user.create()
    database_user.reload()
    target_message = await client.get_messages(
        message.chat.id,
        message.reply_to_message_id,
    )
    if target_message.from_user.id == message.from_user.id:
        caption = "ꜝYou can not ignore yourself..."
        await message.reply(caption, quote=True)
        return

    target_database_message = DatabaseMessage(
        where_room_token=database_user.room_token,
        where_telegram_chat_id=message.chat.id,
        telegram_message_id=message.reply_to_message_id,
    )
    try:
        target_database_message.refresh()
    except TypeError:
        target_database_message.label = "unknown"
        target_database_message.create()
        target_database_message.refresh()
    if (
        not target_database_message
        or not target_database_message.from_root_message_token
        and not target_database_message.label == "bridge"
    ):
        caption = "ꜝThe marked message label is unknown."
        await message.reply(caption, quote=True)
        return  # Improve this block later

    target_database_root_message = return_root_message(
        where_room_token=database_user.room_token,
        linked_root_message_identifier=target_database_message.from_root_message_token,
    )

    new_user_block(
        where_room_token=database_user.room_token,
        telegram_account_id=target_database_root_message["where_telegram_chat_id"],
        applied_by_telegram_account_id=message.from_user.id,
    )
    caption = "ꜝBlocking this user for next 24h."
    await target_message.reply(caption, quote=True)


# Lembrar de depois adicionar um tempo personalizável
@Client.on_message(filters.private & filters.command("signore"))
async def stop_ignore(client: Client, message: Message):
    database_user = DatabaseUser(message.from_user.id)
    database_user.create()
    database_user.reload()
    target_message = await client.get_messages(
        message.chat.id,
        message.reply_to_message_id,
    )
    if target_message.from_user.id == message.from_user.id:
        caption = "ꜝYou can not mark yourself..."
        await message.reply(caption, quote=True)
        message.stop_propagation()
        return

    target_database_message = DatabaseMessage(
        where_room_token=database_user.room_token,
        where_telegram_chat_id=message.chat.id,
        telegram_message_id=message.reply_to_message_id,
    )
    try:
        target_database_message.refresh()
    except TypeError:
        target_database_message.label = "unknown"
        target_database_message.create()
        target_database_message.refresh()
    if (
        not target_database_message
        or not target_database_message.from_root_message_token
        and not target_database_message.label == "bridge"
    ):
        caption = "ꜝThe marked message label is unknown."
        await message.reply(caption, quote=True)
        return  # Improve this block later

    target_database_root_message = return_root_message(
        where_room_token=database_user.room_token,
        linked_root_message_identifier=target_database_message.from_root_message_token,
    )

    delete_user_block(
        where_room_token=database_user.room_token,
        telegram_account_id=target_database_root_message["where_telegram_chat_id"],
        applied_by_telegram_account_id=message.from_user.id,
    )
    caption = "ꜝThis user is no longer blocked."
    await target_message.reply(caption, quote=True)

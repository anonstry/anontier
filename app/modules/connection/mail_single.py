"""
Mailing system
Ainda falta um sistema de correios em grupo (mail_group)

Uma coisa legal para se adicionar seria exclusão.
Exemplo: /mail -<mention> para todos da sala menos o usuário

To do:
    Messages with more than 800 characters: split in two or more parts
"""

from contextlib import suppress

# from loguru import logger
from hydrogram import filters
from hydrogram.client import Client
from hydrogram.errors import (
    PeerIdInvalid,
    UsernameInvalid,
    UsernameNotOccupied,
    # MessageNotModified,
    # MessageEmpty,
)
from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.database.message import DatabaseMessage
from app.database.user import DatabaseUser
from app.modules.connection import add_message_header


def remove_text_command(message):
    caption = message.text or message.caption
    try:
        new_html_caption = caption.html.split(maxsplit=2)[2:][0]
    except IndexError:
        new_html_caption = str()
    finally:
        return new_html_caption


@Client.on_message(filters.private & filters.command("mail") & ~filters.media_group)
async def send_mail(client: Client, message: Message):
    database_user = DatabaseUser(message.from_user.id)
    database_user.create()
    database_user.reload()
    database_message = DatabaseMessage(
        where_telegram_chat_id=message.chat.id,
        where_room_token=database_user.room_token,
        telegram_message_id=message.id,
    )
    database_message.create()
    database_message.refresh()
    try:
        target_mention = message.command[1]
    except IndexError:
        await message.reply("Mail could not be sent. Missing mention.")
        return
    try:
        target_peer = await client.resolve_peer(target_mention)
    except (UsernameInvalid, UsernameNotOccupied):
        await message.reply("Mail could not be sent. Invalid username.")
        return
    try:
        assert target_peer.user_id
    except (AssertionError, AttributeError):
        await message.reply("Mail could not be sent. Target is not a user.")
        return
    database_target_user = DatabaseUser(message.from_user.id)
    database_target_user.create()
    database_target_user.reload()
    loading_message = await message.reply("🕊")
    button = InlineKeyboardButton("✉️ Mail • Não-respondível", "mail_guide")
    with suppress(PeerIdInvalid):
        if message.text:
            new_message = await client.send_message(
                target_peer.user_id,
                add_message_header(message, database_user),
                protect_content=True,
                reply_markup=InlineKeyboardMarkup([[button]]),
            )
        else:
            new_message = await message.copy(
                target_peer.user_id,
                add_message_header(message, database_user),
                protect_content=True,
                reply_markup=InlineKeyboardMarkup([[button]]),
            )
        database_new_message = DatabaseMessage(
            label="bridge",
            where_telegram_chat_id=database_target_user.telegram_account_id,
            where_room_token=database_target_user.room_token,
            telegram_message_id=new_message.id,
            from_root_room_token=database_target_user.room_token,
            from_root_message_token=database_message.identifier,
            expiration_timestamp=database_message.expiration_timestamp,
        )
        database_new_message.create()
    await loading_message.edit("Mail successfully sent!")
    # logger.debug("Stopping mailing command propagation...")
    message.stop_propagation()


# @client.on_message(filters.private & filters.command("explode"))
# async def pega_mensagem_bomba(client: Client, message: Message):
#     # pessoa clicar num botão que dê acesso ao bot, talvez como um link de afiliado
#     # apenas uma midia por pessoa e por vez
#     receive_message_address = criar_sessao.mensagens_bombas[message.from_user.id]
#     criar_sessao.mensagens_bombas[message.from_user.id] = None
#     try:
#         chat_id, message_id = resolve_message_address(receive_message_address)
#         receive_message = await client.copy_message(message.from_user.id, chat_id, message_id, protect_content=True)
#         a = await receive_message.reply("Here is a dropped media for you")
#         await sleep(60*1.5)
#         await receive_message.delete()
#         await a.delete()
#     except:
#         ...

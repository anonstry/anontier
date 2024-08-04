"""
Mailing system
Ainda falta um sistema de correios em grupo (mail_group)

Uma coisa legal para se adicionar seria exclusão.
Exemplo: /mail -<mention> para todos da sala menos o usuário
"""

from hydrogram.client import Client
from hydrogram.types import Message
from hydrogram import filters
from hydrogram.errors import UsernameInvalid


from src.session.user import DatabaseUser
from src.session.message import DatabaseMessage


def remove_text_command(message):
    caption_html = (message.text or message.caption).html
    return caption_html.split(maxsplit=2)[-1]


@Client.on_message(filters.private & filters.command("mail") & ~filters.media_group)
async def send_mail(client: Client, message: Message):
    database_user = DatabaseUser(message.from_user.id)
    database_user.create()
    database_user.refresh()
    database_message = DatabaseMessage(
        from_telegram_chat_id=message.chat.id,
        from_room_token=database_user.room_token,
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
    except UsernameInvalid:
        await message.reply("Mail could not be sent. Invalid username.")
        return
    try:
        assert target_peer.user_id
    except AssertionError:
        await message.reply("Mail could not be sent. Target is not a user.")
        return
    database_target_user = DatabaseUser(message.from_user.id)
    database_target_user.create()
    database_target_user.refresh()
    loading_message = await message.reply("🕊")
    new_message = await message.copy(
        target_peer.user_id,
        remove_text_command(message),
        protect_content=database_user.protected_transmition,
    )
    database_new_message = DatabaseMessage(
        from_telegram_chat_id=database_target_user.telegram_account_id,
        from_room_token=database_target_user.room_token,
        telegram_message_id=new_message.id,
        from_primary_room_token=database_user.room_token,
        from_primary_message_token=database_message.token,
        # expiration = "1 day" # @experimental
    )
    database_new_message.create()
    await loading_message.edit("Mail successfully sent!")
    message.stop_propagation()

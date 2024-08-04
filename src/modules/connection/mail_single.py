"""
Mailing system
Ainda falta um sistema de correios em grupo (mail_group)
"""

from hydrogram.client import Client
from hydrogram.types import Message
from hydrogram import filters
from hydrogram.errors import UsernameInvalid


from src.session.user import DatabaseUser


@Client.on_message(filters.private & filters.command("mail") & ~filters.media_group)
async def send_mail(client: Client, message: Message):
    database_user = DatabaseUser(message.from_user.id)
    database_user.create()
    database_user.refresh()
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
    loading_message = await message.reply("🕊")
    await message.copy(
        target_peer.user_id,
        protect_content=database_user.protected_transmition,
    )
    await loading_message.edit("Mail successfully sent!")
    message.stop_propagation()

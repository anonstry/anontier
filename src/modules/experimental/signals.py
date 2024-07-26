from hydrogram.enums import ChatAction
from hydrogram.client import Client
from hydrogram.types import Message
from hydrogram import filters
from loguru import logger

from .. import client


def implement():
    "Lazy function"
    logger.info("Module to send group typing signals was implemented")


@client.on_message(filters.group)
async def send_typing_signal(client: Client, message: Message):
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)

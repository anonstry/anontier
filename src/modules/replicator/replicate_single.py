from random import choice
from typing import Optional

from hydrogram import filters
from hydrogram.client import Client
from hydrogram.errors import InputUserDeactivated, UserIsBlocked
from hydrogram.types import Message
from loguru import logger

from src.database import (
    create_document_message,
    deactivate_document_user,
    get_document_message_from_generic_specifications,
    get_document_user_linked_room_token,
    search_linked_message,
    search_room_members,
    unlink_document_user_room_token,
    get_document_user_protection_status,
    modify_document_room_participants_count
)

# from src.database.restriction import check_user_block
# from src.modules.connection import add_message_header
from src.modules.protector.mitigate_flood import SpamChecker
from src.telegram.filters.room import linked_room__filter


async def send_single_message(
    client: Client,
    message: Message,
    where_room_token,
    where_telegram_chat_id: int,
    family_id: int,
    protect_content: bool = False,
    reply_to_message_id: Optional[int] = None,
):
    try:
        if not message.text:
            shadow_message = await message.copy(
                where_telegram_chat_id,
                caption=message.caption,
                caption_entities=message.caption_entities,
                reply_to_message_id=reply_to_message_id,
            )
        else:
            shadow_message = await client.send_message(
                where_telegram_chat_id,
                text=message.text,
                entities=message.entities,
                protect_content=protect_content,
                reply_to_message_id=reply_to_message_id,
            )
        if shadow_message is not None and isinstance(shadow_message, Message):
            await create_document_message(
                where_telegram_client_id=client.me.id,
                where_telegram_chat_id=where_telegram_chat_id,
                where_room_token=where_room_token,
                telegram_message_id=shadow_message.id,
                label="replicator-shadow-message",
                family_id=family_id,
            )

    except (UserIsBlocked, InputUserDeactivated):
        await modify_document_room_participants_count(where_room_token, -1)
        await unlink_document_user_room_token(where_telegram_chat_id)
        await deactivate_document_user(where_telegram_chat_id)


@Client.on_message(
    filters.private & linked_room__filter & ~filters.regex("^/") & ~filters.media_group
)
async def single_message_receptor(client: Client, message: Message):
    spam_checker = SpamChecker()
    if spam_checker.add_message(message.from_user.id):
        await client.send_message(
            message.from_user.id,
            text="Your message wasn't sent, it was flagged as spam",
            reply_to_message_id=message.id,
        )
        return

    family_id = int(
        str(message.from_user.id + message.id + choice(range(1000)))
    )  # Calculating the family ID
    room_token = await get_document_user_linked_room_token(message.from_user.id)
    await create_document_message(
        where_telegram_client_id=client.me.id,
        where_telegram_chat_id=message.chat.id,
        where_room_token=room_token,
        telegram_message_id=message.id,
        label="replicator-source-message",
        family_id=family_id,
    )
    room_members = list(
        filter(
            lambda room_member: room_member
            and room_member.telegram_account_id != message.from_user.id,
            await search_room_members(room_token),
        )
    )
    protect_content = await get_document_user_protection_status(message.from_user.id)
    for room_member in room_members:
        reply_to_message_id = None
        if message.reply_to_message_id:
            try:
                replied_message_document = (
                    await get_document_message_from_generic_specifications(
                        where_telegram_client_id=client.me.id,
                        where_telegram_chat_id=message.chat.id,
                        where_room_token=room_token,
                        telegram_message_id=message.reply_to_message_id,
                    )
                )
                if replied_message_document:
                    derivated_message_document = await search_linked_message(
                        where_telegram_chat_id=room_member.telegram_account_id,
                        where_room_token=room_token,
                        family_id=replied_message_document.family_id,
                        document_message_id=replied_message_document.id,
                    )
                    if derivated_message_document is not None:
                        reply_to_message_id = (
                            derivated_message_document.telegram_message_id
                        )
            except AssertionError:
                # logger.error(exception)
                logger.error("A replied message was not found!")
        await send_single_message(
            client=client,
            message=message,
            where_telegram_chat_id=room_member.telegram_account_id,
            reply_to_message_id=reply_to_message_id,
            where_room_token=room_token,
            family_id=family_id,
            protect_content=protect_content,
        )

    message.stop_propagation()

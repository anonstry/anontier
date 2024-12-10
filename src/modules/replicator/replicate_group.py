import asyncio
import traceback
from collections import defaultdict
from dataclasses import dataclass
from random import choice
from typing import Coroutine, Optional, TypeVar

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
)

# from src.modules.connection import add_message_header
from src.telegram.filters.room import linked_room__filter
from src.telegram.modded.copy_media_group import copy_media_group


_tasks = set()
T = TypeVar("T")


def background(coro: Coroutine[None, None, T]) -> asyncio.Task[T]:
    loop = asyncio.get_event_loop()
    task = loop.create_task(coro)
    _tasks.add(task)
    task.add_done_callback(_tasks.remove)
    return task


@dataclass
class Album:
    media_group_id: str
    messages: list[Message]


# chat_id: group_id: album
_albums: defaultdict[int, dict[str, Album]] = defaultdict(dict)


@Client.on_message(
    filters.private
    & linked_room__filter
    & ~filters.regex("^/")
    # & ~filters.command
    & filters.media_group
)
async def on_media_group(client: Client, message: Message):
    try:
        chat_id = message.chat.id
        media_group_id = message.media_group_id
        if media_group_id is None:
            return

        if media_group_id not in _albums[chat_id]:
            album = Album(messages=[message], media_group_id=media_group_id)
            _albums[chat_id][media_group_id] = album

            async def task():
                await asyncio.sleep(1)
                _albums[chat_id].pop(media_group_id, None)
                try:
                    album.messages.sort(key=lambda m: m.id)
                    await on_album(client, album)
                except Exception:
                    traceback.print_exc()

            background(task())
        else:
            album = _albums[chat_id][media_group_id]
            album.messages.append(message)
    finally:
        message.continue_propagation()


async def on_album(client: Client, album: Album):
    first_album_message = album.messages[0]
    # last_album_message = album.messages[-1]
    family_ids = list()
    room_token = await get_document_user_linked_room_token(
        first_album_message.from_user.id
    )
    for message in album.messages:
        family_id = int(
            str(message.from_user.id + first_album_message.id + choice(range(1000)))
        )  # Calculating the family ID
        family_ids.append(family_id)
        await create_document_message(
            where_telegram_client_id=client.me.id,
            where_telegram_chat_id=message.chat.id,
            where_room_token=room_token,
            telegram_message_id=message.id,
            label="connection-source-message",
            family_id=family_id,
            media_group_id=message.media_group_id,
        )
    room_members = list(
        filter(
            lambda room_member: room_member
            and room_member.telegram_account_id != first_album_message.from_user.id,
            await search_room_members(room_token),
        )
    )
    for room_member in room_members:
        # if check_user_block(
        #     where_room_token=room_token,
        #     telegram_account_id=first_album_message.from_user.id,
        #     applied_by_telegram_account_id=room_member.telegram_account_id,
        # ):
        #     return
        reply_to_message_id = None
        if first_album_message.reply_to_message_id:
            try:
                replied_message_document = (
                    await get_document_message_from_generic_specifications(
                        where_telegram_client_id=client.me.id,
                        where_telegram_chat_id=first_album_message.chat.id,
                        where_room_token=room_token,
                        telegram_message_id=first_album_message.reply_to_message_id,
                    )
                )
                derivated_message_document = await search_linked_message(
                    where_telegram_chat_id=room_member.telegram_account_id,
                    where_room_token=room_token,
                    family_id=replied_message_document.family_id,
                    document_message_id=replied_message_document.id,
                )
                assert derivated_message_document
                reply_to_message_id = derivated_message_document.telegram_message_id
            except AssertionError:
                # logger.error(exception)
                logger.error("A replied message was not found!")
        await send_grouped_messages(
            client=client,
            messages=album.messages,
            where_telegram_chat_id=room_member.telegram_account_id,
            reply_to_message_id=reply_to_message_id,
            where_room_token=room_token,
            family_ids=family_ids,
        )
        # last_album_message.stop_propagation()


async def send_grouped_messages(
    client: Client,
    messages: list[Message],
    where_room_token,
    where_telegram_chat_id: int,
    family_ids: list[int],
    reply_to_message_id: Optional[int] = None,
):
    # Aqui precisamos melhorar
    # Provavelmente será necessário uma
    # forma de registrar todos os albums
    # e tambem todos as mensagens single como um album,
    # para quando for editar uma mensagem: sempre edite a primeira.
    first_album_message = messages[0]
    try:
        shadow_messages = await copy_media_group(
            client,
            where_telegram_chat_id,
            first_album_message.chat.id,
            first_album_message.id,
            reply_to_message_id=reply_to_message_id,
            # protect_content=True,
            captions=[
                #     # add_message_header(message, from_database_user) for message in messages
                message.caption
                for message in messages
            ],
            # ][0],  # Apenas a legenda da primeira mensagem é preservada,
        )
        for shadow_message, family_id in zip(shadow_messages, family_ids):
            await create_document_message(
                where_telegram_client_id=client.me.id,
                where_telegram_chat_id=where_telegram_chat_id,
                where_room_token=where_room_token,
                telegram_message_id=shadow_message.id,
                label="connection-shadow-message",
                family_id=family_id,
                media_group_id=shadow_message.media_group_id,
            )
            logger.debug(shadow_message.media_group_id)
        for shadow_message, source_message in zip(shadow_messages, messages):
            if not source_message.caption:
                continue
            if (
                shadow_message.caption == source_message.caption
                and shadow_message.caption_entities == source_message.caption_entities
            ):
                continue
            await shadow_message.edit_caption(
                caption=source_message.caption,
                caption_entities=source_message.caption_entities,
            )
    except (UserIsBlocked, InputUserDeactivated):
        await unlink_document_user_room_token(where_telegram_chat_id)
        await deactivate_document_user(where_telegram_chat_id)

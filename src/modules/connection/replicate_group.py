import asyncio
import traceback
from collections import defaultdict
from dataclasses import dataclass
from typing import Coroutine, TypeVar

from hydrogram import filters
from hydrogram.client import Client
from hydrogram.errors.exceptions.forbidden_403 import UserIsBlocked
from hydrogram.types import Message
from loguru import logger

from src.session.message import DatabaseMessage, search_correspondent_replied_message
from src.session.user import User as DatabaseUser
from src.session.user import search_room_members
from src.telegram.filters.room import filter_room_linked
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
    & filter_room_linked
    & filters.media_group
    & ~filters.command(str())
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
    last_album_message = album.messages[-1]
    first_album_message = album.messages[0]
    database_user = DatabaseUser(first_album_message.from_user.id)
    database_user.create()
    database_user.refresh()
    database_messages = [
        DatabaseMessage(
            from_telegram_chat_id=message.chat.id,
            from_room_token=database_user.room_token,
            telegram_message_id=message.id,
        )
        for message in album.messages
    ]
    for database_message in database_messages:
        database_message.create()
        database_message.refresh()
    room_members = list(
        filter(
            lambda room_member: room_member
            and room_member.telegram_account_id != database_user.telegram_account_id,
            search_room_members(database_user.room_token),
        )
    )
    for room_member in room_members:
        reply_to_message_id = None
        if first_album_message.reply_to_message_id:
            try:
                database_reply_to_message = DatabaseMessage(
                    from_telegram_chat_id=first_album_message.chat.id,
                    from_room_token=room_member.room_token,
                    telegram_message_id=first_album_message.reply_to_message_id,
                )
                database_reply_to_message.refresh()
                database_linked_reply_to_message = search_correspondent_replied_message(
                    where_telegram_chat_id=room_member.telegram_account_id,
                    where_room_token=room_member.room_token,
                    with_primary_message_token=database_reply_to_message.from_primary_message_token
                    or database_reply_to_message.token,
                )
            except AssertionError:
                logger.error(
                    "Could not find which message(s) is being replied in the current room!"
                )
            else:
                reply_to_message_id = (
                    database_linked_reply_to_message.telegram_message_id
                )
        await send_grouped_messages(
            client,
            album.messages,
            database_messages,
            reply_to_message_id,
            room_member,
            database_user,
        )
        last_album_message.stop_propagation()


async def send_grouped_messages(
    client: Client,
    messages: list[Message],
    database_messages: list[DatabaseMessage],
    reply_to_message_id,
    room_member: DatabaseUser,
    from_database_user: DatabaseUser,
):
    first_album_message = messages[0]
    try:
        new_messages = await copy_media_group(
            client,
            room_member.telegram_account_id,
            first_album_message.chat.id,
            first_album_message.id,
            reply_to_message_id=reply_to_message_id,
            protect_content=from_database_user.protected_transmition,
        )
        for new_message, database_message in zip(new_messages, database_messages):
            database_new_message = DatabaseMessage(
                from_telegram_chat_id=room_member.telegram_account_id,
                from_room_token=room_member.room_token,
                telegram_message_id=new_message.id,
                from_primary_room_token=room_member.room_token,
                from_primary_message_token=database_message.token,
            )
            database_new_message.create()
    except UserIsBlocked:
        room_token = room_member.room_token
        room_member.unlink_room(room_token)
        room_member.delete()

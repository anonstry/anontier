import asyncio
import traceback
from collections import defaultdict
from dataclasses import dataclass
from typing import Coroutine, TypeVar

from hydrogram import filters
from hydrogram.client import Client
from hydrogram.errors.exceptions.forbidden_403 import UserIsBlocked
from hydrogram.types import Message, Update
from hydrogram.raw.types import UpdateBotStopped
from loguru import logger

from .. import client, session
from ..broadcast import notify_room_members
from ..modded.copy_media_group import copy_media_group


def implement():
    "Lazy function"
    logger.info("Module to catch connection commands and messages was implemented")


@client.on_message(
    filters.private
    & (filters.command("join") | filters.command("party") | filters.command("match")),
)
async def unmatch_suggestion(client: Client, message: Message):
    user = session.User(message.from_user.id)
    user.create(duplicate=False)
    user.refresh()
    if user.room_token:
        caption = "You already in a conversation/room. Try /unmatch"
        await message.reply(text=caption, quote=True)
    else:
        message.continue_propagation()
    message.stop_propagation()

@client.on_message(filters.private & filters.command("join"))
async def join_room(client: Client, message: Message):
    user = session.User(message.from_user.id)
    user.refresh()
    room_token = None
    try:
        room_token = message.command[1]
    except IndexError:
        caption = "You must provide a room token! Try /manual"
        await message.reply(text=caption, quote=True, protect_content=True)
        return
    try:
        room = session.Room(room_token)
        room.refresh()
    except AssertionError:
        caption = "You must provide a valid room token!"
        await message.reply(text=caption, quote=True, protect_content=True)
        return
    user.link_room(room_token)
    caption = "Room linked successfully! Try /status"
    new_message = await message.reply(text=caption, quote=True)
    caption = f"Room invite link: t.me/{client.me.username}?room_token={room_token}"
    await new_message.reply(text=caption, quote=True)  # def invite
    caption = "**A partner connected.**\n __Someone joined in your room...__"
    await notify_room_members(
        client,
        caption,
        room.token,
        exclude_telegram_accounts_ids=[user.telegram_account_id],
    )
    message.stop_propagation()


@client.on_message(filters.private & filters.command("party"))
async def create_party(client: Client, message: Message):
    user = session.User(message.from_user.id)
    user.refresh()
    try:
        room_size_limit = message.command[1]
    except IndexError:
        caption = "You must write the room size limit!"
        await message.reply(text=caption, quote=True, protect_content=True)
        return
    try:
        room_size_limit = int(room_size_limit)
    except ValueError:
        caption = "You must provide a valid room size number!"
        await message.reply(text=caption, quote=True, protect_content=True)
        return
    if room_size_limit < 0:
        hidden = True
    else:
        hidden = False
    room_size_limit = abs(room_size_limit)
    room = session.Room(size_limit=room_size_limit, hidden=hidden)
    room.create()
    room.refresh()
    user.link_room(room.token)
    if hidden:
        caption = "You created a new private room/party!"
    else:
        caption = "You created a new public room/party!"
    new_message = await message.reply(text=caption, quote=True, protect_content=True)
    await new_message.reply(f"**Token to invite:** <code>{room.token}</code>")
    await notify_room_members(
        client,
        caption,
        room.token,
        exclude_telegram_accounts_ids=[user.telegram_account_id],
    )
    message.stop_propagation()


@client.on_message(filters.private & filters.command("match"))
async def match_room(client: Client, message: Message):
    user = session.User(message.from_user.id)
    user.refresh()
    try:
        sorting_number = int(message.command[1])
    except (IndexError, ValueError, Exception):  # Not exists or not integer
        sorting_number = 1
    room = session.search_public_room(sorting_number)
    if not room:
        await message.reply("No available public rooms.")
        user.link_new_room()
        room = session.Room(user.room_token)
        room.create()
        room.refresh()
        caption = "New public room started."
        _message = await message.reply(text=caption, quote=True)
        caption = f"**Token to invite:** <code>{room.token}</code>\n__Waiting for a partner to connect with...__"
        await _message.reply(text=caption, quote=True)
    else:
        user.link_room(room.token)
        caption = "You joined in a public room.."
        _message = await message.reply(caption)
        caption = f"**Token to invite:** <code>{room.token}</code>"
        await _message.reply(caption)
        caption = "**A partner connected.**\n __Someone joined in your room...__"
        await notify_room_members(
            client,
            caption,
            room.token,
            exclude_telegram_accounts_ids=[user.telegram_account_id],
        )
    message.stop_propagation()


@client.on_message(filters.private & filters.command("unmatch"))
async def quit_room(client: Client, message: Message):
    user = session.User(message.from_user.id)
    user.refresh()
    room = session.Room(user.room_token)
    try:
        room.refresh()
    except AssertionError:
        caption = "You are not in a conversation yet"
        await message.reply(text=caption, quote=True)
    else:
        user.unlink_room(room.token)
        caption = "You left the room."
        new_message = await message.reply(text=caption)
        caption = "Start a new one: /match."
        await new_message.reply(text=caption, quote=True)
        caption = "Someone left the room. Send /status to check."
        await notify_room_members(client, caption, room.token)
    finally:
        session.sanitize_rooms()
    message.stop_propagation()


@client.on_message(filters.private & ~filters.media_group)
async def broadcast(client: Client, message: Message):
    user = session.User(message.from_user.id)
    user.refresh()
    if not user.room_token:
        caption = "You are not into a room. Try /match"
        await message.reply(text=caption, quote=True)
        message.continue_propagation()
        return
    _message = session.Message(
        from_telegram_chat_id=message.chat.id,
        from_room_token=user.room_token,
        telegram_message_id=message.id,
    )
    _message.create()
    _message.refresh()
    if message.reply_to_message_id:
        _reply_to_message = session.Message(
            from_telegram_chat_id=message.chat.id,
            from_room_token=user.room_token,
            telegram_message_id=message.reply_to_message_id,
        )
        _reply_to_message.refresh()
    else:
        _reply_to_message = None
    room_members = list(
        filter(
            lambda room_member: room_member
            and room_member.telegram_account_id != user.telegram_account_id,
            session.search_room_members(user.room_token),
        )
    )
    if not room_members:
        caption = "This room is empty."
        await message.reply(text=caption, quote=True)
        return
    for room_member in room_members:
        _linked_reply_to_message_id = None
        if _reply_to_message:  # primary token
            _linked_reply_to_message = session.search_correspondent_replied_message(
                where_telegram_chat_id=room_member.telegram_account_id,
                where_room_token=room_member.room_token,
                with_primary_message_token=_reply_to_message.from_primary_message_token
                or _reply_to_message.token,
            )
            _linked_reply_to_message_id = _linked_reply_to_message.telegram_message_id
        try:
            new_message = await message.copy(
                room_member.telegram_account_id,
                reply_to_message_id=_linked_reply_to_message_id,
                protect_content=True,
                # invert_media=message.invert_media,
            )
            _new_message = session.Message(
                from_telegram_chat_id=room_member.telegram_account_id,
                from_room_token=room_member.room_token,
                telegram_message_id=new_message.id,
                from_primary_room_token=user.room_token,
                from_primary_message_token=_message.token,
            )
            _new_message.create()
        except UserIsBlocked:
            room_token = room_member.room_token
            room_member.unlink_room(room_token)
            room_member.delete()
            caption = "__A member of your current room blocked the bot and could not receive the message.\n See about the current /status!__"
            await notify_room_members(client, caption, room_token)
    message.stop_propagation()


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


@client.on_message(filters.private & filters.media_group)
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
    user = session.User(first_album_message.from_user.id)
    user.refresh()
    if not user.room_token:
        caption = "You are not into a room. Try /match"
        await first_album_message.reply(text=caption, quote=True)
        return
    _messages: list[session.Message] = [
        session.Message(
            from_telegram_chat_id=message.chat.id,
            from_room_token=user.room_token,
            telegram_message_id=message.id,
        ) for message in album.messages
    ]
    for _message in _messages:
        _message.create()
        _message.refresh()
    if album.messages[0].reply_to_message_id:
        _reply_to_message = session.Message(
            from_telegram_chat_id=first_album_message.chat.id,
            from_room_token=user.room_token,
            telegram_message_id=first_album_message.reply_to_message_id,
        )
        _reply_to_message.create() # maybe remove later
        _reply_to_message.refresh()
    else:
        _reply_to_message = None
    room_members = list(
        filter(
            lambda room_member: room_member
            and room_member.telegram_account_id != user.telegram_account_id,
            session.search_room_members(user.room_token),
        )
    )
    if not room_members:
        caption = "This room is empty."
        await first_album_message.reply(text=caption, quote=True)
        return  # Move to another function later
    for room_member in room_members:
        _linked_reply_to_message_id = None
        if _reply_to_message:  # primary token
            _linked_reply_to_message = session.search_correspondent_replied_message(
                where_telegram_chat_id=room_member.telegram_account_id,
                where_room_token=room_member.room_token,
                with_primary_message_token=_reply_to_message.from_primary_message_token
                or _reply_to_message.token,
            )
            _linked_reply_to_message_id = _linked_reply_to_message.telegram_message_id
        try:
            new_messages = await copy_media_group(
                client,
                room_member.telegram_account_id,
                first_album_message.chat.id,
                first_album_message.id,
                reply_to_message_id=_linked_reply_to_message_id,
                protect_content=True,
                # invert_media=first_album_message.invert_media # wait for the release asdsdds dsdd
            )
            for new_message, _original_message in zip(new_messages, _messages):
                _new_message = session.Message(
                    from_telegram_chat_id=room_member.telegram_account_id,
                    from_room_token=room_member.room_token,
                    telegram_message_id=new_message.id,
                    from_primary_room_token=user.room_token,
                    from_primary_message_token=_original_message.token,
                )
                _new_message.create()
        except UserIsBlocked:
            room_token = room_member.room_token
            room_member.unlink_room(room_token)
            room_member.delete()
            caption = "__A member of your current room blocked the bot and could not receive the message.\n See about the current /status!__"
            await notify_room_members(client, caption, room_token)
    # first_album_message.stop_propagation()


@client.on_raw_update()
async def bot_stopped(client: Client, update: Update, _, __):
    if isinstance(update, UpdateBotStopped) and update.stopped:
        user = session.User(update.user_id)
        user.refresh()
        room_token = user.room_token
        assert room_token
        user.unlink_room(room_token)
        user.delete()
        caption = "__A member of your current room blocked the bot. See about the current /status!__"
        await notify_room_members(client, caption, room_token)

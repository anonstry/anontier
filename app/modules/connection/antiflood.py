# Sistema de antiflood primitivo
# E ainda falta o painel de gerenciamento
# e ainda o sistema de prevenção contra spam

import pendulum
from loguru import logger
from hydrogram import filters
from hydrogram.client import Client
from hydrogram.types import Message

from app.database.user import DatabaseUser, search_room_members
from app.database.restriction import new_user_block

import hashlib

# hash: [ocorrency, lifetime_timestamp]

_cache = dict()

logger.info("Here")


@Client.on_message(
    filters.private, group=-1
)  # security.filters.antiflood_enabled (take a breath)
async def verify_media_flood(client: Client, message: Message):
    global _cache
    cache = dict()
    for hash_ in _cache:
        if _cache[hash_]["lifetime_timestamp"] > pendulum.now().timestamp():
            cache[hash_] = _cache[hash_]
    del _cache
    _cache = cache

    if not message.text:
        media = getattr(message, message.media.value)
        hash_ = media.file_unique_id
    else:
        hash_ = hashlib.sha256(message.text.encode()).hexdigest()

    if not cache.get(hash_):
        cache[hash_] = {
            "count": 1,
            "lifetime_timestamp": int(pendulum.now().add(seconds=10).timestamp()),
        }
    else:
        cache[hash_]["count"] = cache[hash_]["count"] + 1

    if cache[hash_]["count"] > 10:
        database_user = DatabaseUser(message.from_user.id)
        database_user.reload()
        for room_member in search_room_members(database_user.room_token):
            if room_member.telegram_account_id == message.from_user.id:
                continue
            mute_duration = int(pendulum.now().add(minutes=10).timestamp())
            new_user_block(
                where_room_token=room_member.room_token,
                telegram_account_id=database_user.telegram_account_id,
                applied_by_telegram_account_id=room_member.telegram_account_id,
                until_timestamp=mute_duration,
            )
        caption = "[spam protection]\nꜝNow you are muted for all room users.\n Take a breath for 10 minutes."
        await message.reply(caption, quote=True)
        message.stop_propagation
        return
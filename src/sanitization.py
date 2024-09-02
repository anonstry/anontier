# Adicionar algo para verificar se houve
# alguma mensagem não registradas (ex.: as últimas 10)

from functools import partial
from contextlib import suppress

from hydrogram.client import Client
from hydrogram.enums import ChatAction
from hydrogram.errors import InputUserDeactivated, UserIsBlocked
from loguru import logger

from src import scheduler
from src.database.room import delete_empty_rooms, return_all_rooms, Room
from src.database.user import return_all_users, search_room_members
from src.database.message import return_all_expired_messages
from src.database.subscription import deactivate_expired_premium_subscriptions
from src.database.restriction import delete_expired_user_blocks


async def remove_blocked_users(client: Client):
    logger.debug("Searching for all blocked users...")
    for database_user in return_all_users():
        try:
            await client.send_chat_action(
                database_user.telegram_account_id,
                ChatAction.PLAYING,
            )
        except (UserIsBlocked, InputUserDeactivated):
            room_token = database_user.room_token
            database_user.unlink_room(room_token)
            database_user.delete()


async def check_room_participant_count(client: Client):
    logger.debug("Recounting all room participants...")
    for document in return_all_rooms():
        room = Room(document["token"])
        room.refresh()
        participants_count = 0
        for room_member in search_room_members(room.token):
            with suppress(UserIsBlocked, InputUserDeactivated):
                await client.send_chat_action(
                    room_member.telegram_account_id,
                    ChatAction.PLAYING,
                )
                participants_count += 1
            room.increment_participants_count(-room.participants_count)  # Zero
            room.increment_participants_count(participants_count)


# async def check_messages_health(client: Client):
#     logger.debug("Searching for all messages health...")
#     for database_message in return_all_messages():
#         await client.get_messages(
#             database_message.where_telegram_chat_id,
#             database_message.telegram_message_id,
#         )


async def delete_messages_with_expired_lifetime(client: Client):
    logger.debug("Searching for all expired messages lifetime...")
    for database_message in return_all_expired_messages():
        try:
            await client.delete_messages(
                database_message.where_telegram_chat_id,
                database_message.telegram_message_id,
            )
            database_message.delete()
        except Exception as exception:
            logger.error(exception)


def schedule_sanization(client):
    scheduled_tasks = [
        {
            "func": partial(remove_blocked_users, client),
            "trigger": "cron",
            "minute": 1,
        },
        {
            "func": partial(check_room_participant_count, client),
            "trigger": "cron",
            "minute": 1,
        },
        {
            "func": partial(delete_messages_with_expired_lifetime, client),
            "trigger": "cron",
            "minute": 1,
        },
        {
            "func": delete_empty_rooms,
            "trigger": "cron",
            "minute": 1,
        },
        {
            "func": deactivate_expired_premium_subscriptions,
            "trigger": "cron",
            "hour": 1,
        },
        {
            "func": delete_expired_user_blocks, # restrictions
            "trigger": "cron",
            "minute": 1,
        },
    ]
    for scheduled_task in scheduled_tasks:
        scheduler.add_job(**scheduled_task)

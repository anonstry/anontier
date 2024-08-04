from functools import partial

from hydrogram.client import Client
from hydrogram.enums import ChatAction
from hydrogram.errors import InputUserDeactivated, UserIsBlocked
from loguru import logger

from src import scheduler
from src.session.room import search_empty_rooms
from src.session.user import return_all_users
from src.session.message import return_all_messages


def delete_empty_rooms():
    logger.debug("Searching for all empty rooms...")
    "Delete rooms with no linked users"
    for room in search_empty_rooms():
        room.delete()


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


# async def search_not_registered_messages(client: Client):
#     for database_user in return_all_users():
#         dialog = await client.get_his
#     async for dialog in client.get_dialogs():
#         print(dialog.chat.username)


async def check_room_participant_count():
    "Recount"
    print("Nothing here yet")


async def check_messages_health(client: Client):
    logger.debug("Searching for all messages health...")
    for database_message in return_all_messages():
        await client.get_messages(
            database_message.from_telegram_chat_id,
            database_message.telegram_message_id,
        )


def schedule_sanization(client):
    scheduled_tasks = [
        {
            "func": partial(remove_blocked_users, client),
            "trigger": "cron",
            "minute": 10,
        },
        {
            "func": delete_empty_rooms,
            "trigger": "cron",
            "second": 1,
        },
    ]
    for scheduled_task in scheduled_tasks:
        scheduler.add_job(**scheduled_task)

from functools import partial

from hydrogram.client import Client
from hydrogram.enums import ChatAction
from hydrogram.errors import InputUserDeactivated, UserIsBlocked
from loguru import logger

from src import scheduler
from src.session.room import search_empty_rooms
from src.session.user import return_all_users


def delete_empty_rooms():
    logger.debug("Searching for all empty rooms...")
    "Delete rooms with no linked users"
    for room in search_empty_rooms():
        room.delete()


async def remove_blocked_users(client: Client):
    logger.debug("Searching for all blocked users...")
    for user in return_all_users():
        try:
            await client.send_chat_action(user.telegram_account_id, ChatAction.PLAYING)
        except (UserIsBlocked, InputUserDeactivated):
            room_token = user.room_token
            user.unlink_room(room_token)
            user.delete()

async def check_participant_count():
    "Recount"
    print("Nothing here yet")


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

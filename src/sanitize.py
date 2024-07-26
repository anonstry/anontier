from functools import partial
from hydrogram.client import Client
from hydrogram.enums import ChatAction

from src import broadcast, scheduler
from src.session.room import search_empty_rooms
from src.session.user import return_all_users

from hydrogram.errors import UserIsBlocked


def delete_empty_rooms():
    "Delete rooms with no linked users"
    for room in search_empty_rooms():
        room.delete()


async def find_blocked_users(client: Client):
    for user in return_all_users():
        try:
            await client.send_chat_action(user.telegram_account_id, ChatAction.PLAYING)
        except UserIsBlocked:
            room_token = user.room_token
            user.unlink_room(room_token)
            user.delete()
            if room_token:
                caption = "__A member of your current room blocked the bot. See about the current /status!__"
                await broadcast.notify_room_members(client, caption, room_token)


def schedule_sanization(client):
    scheduled_tasks = [
        {
            "func": partial(find_blocked_users, client),
            "trigger": "cron",
            "minute": 10,
        },
        {
            "func": delete_empty_rooms,
            "trigger": "cron",
            "second": 60,
        },
    ]
    for scheduled_task in scheduled_tasks:
        scheduler.add_job(**scheduled_task)
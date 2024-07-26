# Arquivo é bem básico ainda.
# Move to session/sanization.py @future


from hydrogram.client import Client
from hydrogram.enums import ChatAction

from src import session, broadcast


from hydrogram.errors import UserIsBlocked


async def check_blocked_users(client: Client):
    print("Here")
    for user in session.return_all_users():
        try:
            await client.send_chat_action(user.telegram_account_id, ChatAction.PLAYING)
        except UserIsBlocked:
            room_token = user.room_token
            user.unlink_room(room_token)
            user.delete()
            if room_token:
                caption = "__A member of your current room blocked the bot. See about the current /status!__"
                await broadcast.notify_room_members(client, caption, room_token)




# scheduled_tasks = [
#     {
#         "func": partial(sanitize.check_blocked_users, client),
#         "trigger": "cron",
#         # "minute": 1,
#         "minute": 0,
#         "second": 1,
#     },
#     {
#         "func": session.sanitize_rooms,
#         "trigger": "cron",
#         "minute": 1,
#     },
# ]
# for scheduled_task in scheduled_tasks:
#     scheduler.add_job(**scheduled_task)
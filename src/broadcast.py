from hydrogram.client import Client

from . import session


async def notify_all_users(client: Client, caption: str):
    "Broadcast for all users"
    for user in session.return_all_users():
        await client.send_message(user.telegram_account_id, text=caption)


async def notify_room_members(
    client: Client,
    caption: str,
    room_token: str,
    # *,
    exclude_telegram_accounts_ids=list(),
):
    "Broadcast for all room members"
    "Not registered messages"
    room_members = filter(
        lambda room_member: room_member
        and room_member.telegram_account_id not in exclude_telegram_accounts_ids,
        session.search_room_members(room_token),
    )
    for room_member in room_members:
        await client.send_message(room_member.telegram_account_id, text=caption)
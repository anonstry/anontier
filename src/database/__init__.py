import secrets

from typing import Optional

from beanie import Document, init_beanie
from dynaconf import settings
from motor.motor_asyncio import AsyncIOMotorClient

from loguru import logger

# from typing import Annotated, Optional
# from beanie import Document, Indexed, init_beanie


mongo_client = AsyncIOMotorClient(settings.MONGO_CONNECTION_STRING)


def create_random_string(size=16):
    return secrets.token_hex(size)[:size]


# def create_username(words=2):
#     fake = Faker()
#     # title = " ".join([fake.word().capitalize() for _ in range(words)])
#     # title = f"[{title}] #{fake.pystr(4, 6)}"
#     title = f"{fake.name().title()} #{fake.pystr(4, 6)}"
#     return title


class DocumentMessage(Document):
    where_telegram_client_id: int
    where_telegram_chat_id: int
    where_room_token: str
    telegram_message_id: int
    family_id: Optional[int] = None
    label: Optional[str] = None  # message-father or message-child
    media_group_id: Optional[int] = None
    reported: bool = False
    has_protected_content: bool = False
    has_media_spoiler: bool = False
    # signature: Optional[str] = create_random_string(64)
    # expiration_timestamp = int(pendulum.now().add(years=1).timestamp())

    class Settings:
        name = "messages"


class DocumentUser(Document):
    telegram_account_id: int
    room_token: Optional[str] = None
    # hidden: bool = False
    # premium: bool = False
    # username: Optional[str] = None
    deactivated: bool = False
    allow_protection: bool = False

    # signature = create_token(16)

    class Settings:
        name = "users"


class DocumentNotification:
    where_room_token: Optional[str]
    where_telegram_chat_id: int
    until_timestamp: int
    label: str

    class Settings:
        name = "notifications"


class DocumentRestriction:
    where_room_token: Optional[str]
    where_telegram_chat_id: int
    applied_by_telegram_account_id: int  # can be the bot
    until_timestamp: int
    label: str  # mute or block

    class Settings:
        name = "restrictions"


class DocumentMembership:
    where_room_token: str
    where_telegram_chat_id: int
    roles: Optional[list[str]] = list()  # e.g.: owner or moderator
    permissions: Optional[list[str]] = list()  # e.g.: can_mute or can_delete_room

    class Settings:
        name = "memberships"


# class Settings
#   dynamic username
#   dynamic username symbol


class DocumentRoom(Document):
    token: str
    size_limit: int
    hidden: bool = False
    title: Optional[str] = None
    participants_count: int = 0

    class Settings:
        name = "rooms"


async def init_database():
    await init_beanie(
        database=getattr(mongo_client, settings.MONGO_DATABASE_NAME),
        document_models=[DocumentMessage, DocumentUser, DocumentRoom],
    )
    logger.info("Database was initiated")


async def get_document_user_visibility(telegram_account_id):
    document_user = await DocumentUser.find_one(
        {DocumentUser.telegram_account_id: telegram_account_id}
    )
    if document_user:
        return document_user.hidden


async def get_document_user_username(telegram_account_id):
    document_user = await DocumentUser.find_one(
        {DocumentUser.telegram_account_id: telegram_account_id}
    )
    if document_user:
        return document_user.username


async def get_document_user_premium_status(telegram_account_id):
    document_user = await DocumentUser.find_one(
        {DocumentUser.telegram_account_id: telegram_account_id}
    )
    if document_user:
        return document_user.premium


async def create_document_user(telegram_account_id):
    document_user = await DocumentUser.find_one(
        {DocumentUser.telegram_account_id: telegram_account_id}
    )
    if not document_user:
        document_user = DocumentUser(telegram_account_id=telegram_account_id)
        await document_user.insert()
    return document_user


async def get_document_user_linked_room_token(telegram_account_id):
    document_user = await DocumentUser.find_one(
        {DocumentUser.telegram_account_id: telegram_account_id}
    )
    return document_user.room_token


async def unlink_document_user_room_token(telegram_account_id):
    document_user = DocumentUser.find_one(
        {DocumentUser.telegram_account_id: telegram_account_id}
    )
    await document_user.set({DocumentUser.room_token: None})


async def update_document_user_room_token(telegram_account_id, new_room_token):
    document_user = DocumentUser.find_one(
        {DocumentUser.telegram_account_id: telegram_account_id}
    )
    await document_user.set({DocumentUser.room_token: new_room_token})


async def deactivate_document_user(telegram_account_id):
    document_user = DocumentUser.find_one(
        {DocumentUser.telegram_account_id: telegram_account_id}
    )
    await document_user.set({DocumentUser.deactivated: True})


async def search_public_room_token(sorting_number):
    if sorting_number >= 0:
        sorting_order = -DocumentRoom.participants_count  # Desceding
    else:
        sorting_order = +DocumentRoom.participants_count  # Ascending
    telegram_room_documents = (
        await DocumentRoom.find(
            {
                "hidden": False,
                "$and": [
                    {"$expr": {"$lt": ["$participants_count", "$size_limit"]}},
                    {"$expr": {"$gte": ["$participants_count", 1]}},
                ],
            }
        )
        .limit(1)
        .sort(sorting_order)
        .to_list()
    )
    if not telegram_room_documents:
        return
    telegram_room_document = telegram_room_documents[0]
    return telegram_room_document.token


async def get_document_room(token):
    return await DocumentRoom.find_one({DocumentRoom.token: token})


async def create_document_room(size_limit=10, hidden=False):
    room_token = create_random_string(32)
    document_room = await get_document_room(room_token)
    if not document_room:
        document_room = DocumentRoom(
            token=room_token, size_limit=size_limit, hidden=hidden,
        )
        await document_room.insert()
    return document_room


async def modify_document_room_participants_count(room_token, with_value):
    document_room = await DocumentRoom.find_one({DocumentRoom.token: room_token})
    await document_room.inc({DocumentRoom.participants_count: with_value})


async def get_document_message_from_generic_specifications(
    where_telegram_client_id,
    where_telegram_chat_id,
    telegram_message_id,
    where_room_token=None,
):
    if not where_room_token:
        document_message = await DocumentMessage.find_one(
            {
                DocumentMessage.where_telegram_client_id: where_telegram_client_id,
                DocumentMessage.where_telegram_chat_id: where_telegram_chat_id,
                DocumentMessage.telegram_message_id: telegram_message_id,
            }
        )
    else:
        document_message = await DocumentMessage.find_one(
            {
                DocumentMessage.where_telegram_client_id: where_telegram_client_id,
                DocumentMessage.where_telegram_chat_id: where_telegram_chat_id,
                DocumentMessage.where_room_token: where_room_token,
                DocumentMessage.telegram_message_id: telegram_message_id,
            }
        )
    return document_message


async def get_document_message(
    where_telegram_client_id,
    where_telegram_chat_id,
    where_room_token,
    telegram_message_id,
    label,
    family_id,
):
    document_message = await DocumentMessage.find_one(
        {
            DocumentMessage.where_telegram_client_id: where_telegram_client_id,
            DocumentMessage.where_telegram_chat_id: where_telegram_chat_id,
            DocumentMessage.where_room_token: where_room_token,
            DocumentMessage.telegram_message_id: telegram_message_id,
            DocumentMessage.label: label,
            DocumentMessage.family_id: family_id,
        }
    )
    return document_message


async def create_document_message(
    where_telegram_client_id,
    where_telegram_chat_id,
    where_room_token,
    telegram_message_id,
    label,
    family_id,
    media_group_id=None,
):
    document_message = await get_document_message(
        where_telegram_client_id=where_telegram_client_id,
        where_telegram_chat_id=where_telegram_chat_id,
        where_room_token=where_room_token,
        telegram_message_id=telegram_message_id,
        label=label,
        family_id=family_id,
        # media_group_id=media_group_id,
    )
    if not document_message:
        document_user = DocumentMessage(
            where_telegram_client_id=where_telegram_client_id,
            where_telegram_chat_id=where_telegram_chat_id,
            where_room_token=where_room_token,
            telegram_message_id=telegram_message_id,
            label=label,
            family_id=family_id,
            media_group_id=media_group_id,
        )
        await document_user.insert()
    return document_user


async def search_room_members(where_room_token):
    room_members_documents = await DocumentUser.find(
        {
            "$and": [
                {DocumentUser.room_token: where_room_token},
                {DocumentUser.room_token: {"$exists": True, "$ne": ""}},
            ]
        }
    ).to_list()
    return room_members_documents


async def search_linked_message(
    where_telegram_chat_id,
    where_room_token,
    document_message_id,
    family_id,
):
    documents = await DocumentMessage.find(
        {
            "$and": [
                {"_id": {"$ne": document_message_id}},
                {DocumentMessage.family_id: family_id},
                {DocumentMessage.where_room_token: where_room_token},
                {DocumentMessage.where_telegram_chat_id: where_telegram_chat_id},
            ]
        }
    ).to_list()
    try:
        return documents[0]
    except IndexError:
        return None


async def search_all_linked_messages(family_id):
    documents = await DocumentMessage.find(
        DocumentMessage.family_id == family_id
    ).to_list()
    try:
        return documents
    except IndexError:
        return None


async def get_document_user_protection_status(telegram_account_id):
    document_user = await DocumentUser.find_one(
        {DocumentUser.telegram_account_id: telegram_account_id}
    )
    if document_user:
        return document_user.allow_protection

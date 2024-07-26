from hydrogram import Client
from dynaconf import settings
# from apscheduler.schedulers.asyncio import AsyncIOScheduler

client: Client = Client(
    name=settings.TELEGRAM_APP_NAME,
    api_id=settings.TELEGRAM_API_ID,
    api_hash=settings.TELEGRAM_API_HASH,
    bot_token=settings.TELEGRAM_BOT_TOKEN,
)

# scheduler = AsyncIOScheduler()
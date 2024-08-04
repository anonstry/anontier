from hydrogram import idle
from loguru import logger

from src import client, scheduler
from src.sanitization import schedule_sanization, check_messages_health, search_not_registered_messages


async def routine(app):
    await app.start()
    logger.info("Bot Telegram client started")

    schedule_sanization(client)
    logger.info("Scheduled sanitization tasks")

    scheduler.start()
    logger.info("Scheduler worker started")

    # await check_messages_health(app)
    # await search_not_registered_messages(app)

    await idle()

    await app.stop()
    logger.info("Bot Telegram client stopped")


client.run(routine(app=client))

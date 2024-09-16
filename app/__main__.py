from hydrogram import idle
from loguru import logger

from app import client, scheduler
from app.sanitization import schedule_sanization


async def routine(app):
    await app.start()
    logger.info("Bot Telegram client started")

    schedule_sanization(client)
    logger.info("Scheduled sanitization tasks")

    scheduler.start()
    logger.info("Scheduler worker started")

    await idle()

    await app.stop()
    logger.info("Bot Telegram client stopped")


client.run(routine(app=client))

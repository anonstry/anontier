from hydrogram import idle
from loguru import logger

from src import client

# from src import client, scheduler, instancies
# from src.sanitization import schedule_sanization
from src.database import init_database


async def routine():
    global client

    logger.debug("Starting main routine...")

    await client.start()
    logger.info(f"Bot Telegram client @{client.me.username} started")

    # instancies[app.me.id] = app

    # schedule_sanization(client)
    # logger.info("Scheduled sanitization tasks")

    await init_database()

    # scheduler.start()
    # logger.info("Scheduler worker started")

    await idle()

    logger.info("Bot Telegram client stopped")


client.run(routine())

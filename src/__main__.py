from hydrogram import idle

# from loguru import logger
from src import client
from src.modules import guidelines  # lazy-import


async def routine(app):
    await app.start()
    await idle()
    await app.stop()


client.run(routine(app=client))

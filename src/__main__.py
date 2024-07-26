from hydrogram import idle

from src import client


async def routine(app):
    await app.start()
    await idle()
    await app.stop()


client.run(routine(app=client))

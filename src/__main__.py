from hydrogram import idle

from . import client, modules


async def routine(app):
    modules.implement()
    await app.start()
    await idle()
    await app.stop()


client.run(routine(app=client))

# import pendulum
# from loguru import logger
# from hydrogram import filters
# from hydrogram.client import Client
# from hydrogram.types import Message

# # from src.session.message import (
# #     DatabaseMessage,
# #     search_for_original_messages_with_id,
# #     search_linked_messages,
# # )
# # from src.session.user import DatabaseUser
# # from src.telegram.tools.media import mount_input_media


# cache = dict()


# logger.info("Here")


# @Client.on_message(
#     filters.private & filters.media, group=-1
# )  # security.filters.antiflood_enabled (take a breath)
# async def verify_media_flood(client: Client, message: Message):
#     media = getattr(message, message.media.value)
#     timestamp = pendulum.now().timestamp()
#     logger.info("Here")
#     print(cache)

#     identifier = media.file_unique_id
#     if (
#         identifier not in cache
#         or cache[identifier]["timestamp"] < pendulum.now().timestamp()
#     ):
#         cache[identifier] = {
#             "flagged": False,
#             "timestamp": pendulum.now().add(seconds=10).timestamp(),
#             "media_group_id": message.media_group_id,
#         }
#         return
#     elif (
#         cache[identifier]["timestamp"] > timestamp
#         and not cache[identifier]["media_group_id"]
#     ):
#         if not cache[identifier]["flagged"]:
#             await message.reply("Take a breath! **10s**")
#             cache[identifier]["flagged"] = True
#         message.stop_propagation()
#     elif (
#         cache[identifier]["timestamp"] > timestamp
#         and cache[identifier]["media_group_id"] != message.media_group_id
#     ):
#         if not cache[identifier]["flagged"]:
#             await message.reply("Take a breath! **10s**")
#             cache[identifier]["flagged"] = True
#         message.stop_propagation()
    
#     if cache[identifier]["timestamp"] > pendulum.now().timestamp():
#         logger.info("Popped")
#         cache.pop(identifier)

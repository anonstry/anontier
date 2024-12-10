# def search_room_members(room_token):
#     mongo_collection = DatabaseUser.mongo_collection
#     room_members = mongo_collection.find({"room_token": room_token})
#     room_members = list(room_members)
#     if not room_members:
#         return
#     else:
#         for room_member in room_members:
#             yield DatabaseUser(
#                 room_member["telegram_account_id"],
#                 room_member["room_token"],
#             )


# def return_all_users() -> Iterator[DatabaseUser]:
#     mongo_collection = DatabaseUser.mongo_collection
#     room_members = mongo_collection.find()
#     room_members = list(room_members)
#     if not room_members:
#         return
#     else:
#         for room_member in room_members:
#             user = DatabaseUser(
#                 room_member["telegram_account_id"],
#                 room_member["room_token"],
#             )
#             user.reload()
#             yield user
            
            
# # def deactivate_user(telegram_account_id):
# #     DatabaseUser.mongo_collection.update_one(
# #         {"telegram_account_id": telegram_account_id},
# #         {
# #             "$set": {"deactivated": True},
# #         },
# #     )


# def search_public_room(sorting_number):
#     sorting_number = -1 if sorting_number < 0 else 1
#     room_document = Room.mongo_collection.find_one(
#         filter={
#             "hidden": False,
#             "$and": [
#                 {"$expr": {"$lt": ["$participants_count", "$size_limit"]}},
#                 {"$expr": {"$gte": ["$participants_count", 1]}},
#             ],
#         },
#         sort=[("participants_count", sorting_number)],
#     )
#     if not room_document:
#         return
#     else:
#         return Room(
#             token=room_document["token"],
#             hidden=room_document["hidden"],
#             size_limit=room_document["size_limit"],
#         )


# def search_empty_rooms():
#     empty_rooms = Room.mongo_collection.find({"participants_count": 0})
#     empty_rooms = list(empty_rooms)
#     if not empty_rooms:
#         return list()  # or None
#     for empty_room in empty_rooms:
#         room_document = empty_room
#         yield Room(
#             token=room_document["token"],
#             hidden=room_document["hidden"],
#             size_limit=room_document["size_limit"],
#         )


# def return_all_rooms() -> Iterator[Room]:
#     yield from Room.mongo_collection.find()


# def delete_empty_rooms():
#     logger.debug("Searching for all empty rooms...")
#     "Delete rooms with no linked users"
#     for room in search_empty_rooms():
#         room.delete()



# def search_linked_messages(primary_message_token):  # maybe include_itself=True
#     mongo_collection = DatabaseMessage.mongo_collection
#     return mongo_collection.find({"from_root_message_token": primary_message_token})


# def return_all_messages() -> Iterator[DatabaseMessage]:
#     mongo_collection = DatabaseMessage.mongo_collection
#     messages_documents = mongo_collection.find()
#     for message_document in messages_documents:
#         database_message = DatabaseMessage(
#             message_document["where_telegram_chat_id"],
#             message_document["where_room_token"],
#             message_document["telegram_message_id"],
#         )
#         database_message.refresh()
#         yield database_message
#     else:
#         yield from list()  # Empty list


# def return_all_expired_messages() -> Iterator[DatabaseMessage]:
#     for database_message in return_all_messages():
#         if pendulum.now().timestamp() > database_message.expiration_timestamp:
#             yield database_message
#     else:
#         yield from list()  # Empty list


# def return_correspondent_message(
#     where_telegram_chat_id,
#     where_room_token,
#     linked_root_message_identifier,
# ):
#     mongo_collection = DatabaseMessage.mongo_collection
#     database_message_document = mongo_collection.find_one(
#         {
#             "where_telegram_chat_id": where_telegram_chat_id,
#             "where_room_token": where_room_token,
#             "$or": [
#                 {"from_root_message_token": linked_root_message_identifier},
#                 {
#                     "$and": [
#                         {"from_root_message_token": None},
#                         {"identifier": linked_root_message_identifier},
#                     ]
#                 },
#             ],
#         }
#     )
#     return database_message_document


# def return_root_message(
#     where_room_token,
#     linked_root_message_identifier,
# ):
#     mongo_collection = DatabaseMessage.mongo_collection
#     database_message_document = mongo_collection.find_one(
#         {
#             "where_room_token": where_room_token,
#             "$or": [
#                 {"from_root_message_token": linked_root_message_identifier},
#                 {
#                     "$and": [
#                         {"from_root_message_token": None},
#                         {"identifier": linked_root_message_identifier},
#                     ]
#                 },
#             ],
#         }
#     )
#     return database_message_document


# def search_for_original_messages_with_id(telegram_message_id):
#     mongo_collection = DatabaseMessage.mongo_collection
#     database_messages_documents = mongo_collection.find(
#         {
#             "telegram_message_id": telegram_message_id,
#             "from_root_room_token": None,
#             "$expr": {"$ne": ["$where_room_token", None]},  # is not Null
#             "from_root_message_token": None,
#         }
#     )
#     for database_message_document in database_messages_documents:
#         database_message = DatabaseMessage(
#             where_telegram_chat_id=database_message_document["where_telegram_chat_id"],
#             where_room_token=database_message_document["where_room_token"],
#             telegram_message_id=database_message_document["telegram_message_id"],
#         )
#         database_message.refresh()
#         yield database_message
#     else:
#         logger.error("No original messages with the provided ID was found!")
#         yield from list()


# # def find_root_message

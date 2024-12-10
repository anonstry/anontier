# from src.database import mongo_database
# from src.database.user import DatabaseUser

# import pendulum
# from loguru import logger


# class DatabaseSubscription:
#     mongo_collection = mongo_database["subscriptions"]

#     def __init__(self, telegram_account_id, label, until_timestamp):
#         self.telegram_account_id = telegram_account_id
#         self.label = label
#         self.until_timestamp = until_timestamp

#     def reload(self):
#         query = {"telegram_account_id": self.telegram_account_id}
#         database_user_document = self.mongo_collection.find_one(query)
#         self.telegram_account_id = database_user_document["telegram_account_id"]
#         self.label = database_user_document["label"]
#         self.until_timestamp = database_user_document["until_timestamp"]

#     def exists(self):
#         query = {"telegram_account_id": self.telegram_account_id}
#         database_user_document = self.mongo_collection.find_one(query)
#         return bool(database_user_document)

#     def create(self, duplicate=False):
#         if not duplicate and self.exists():
#             return
#         else:
#             self.mongo_collection.insert_one(
#                 {
#                     "telegram_account_id": self.telegram_account_id,
#                     "label": self.label,
#                     "until_timestamp": self.until_timestamp,
#                 }
#             )

#     def delete(self):
#         query = {"telegram_account_id": self.telegram_account_id}
#         self.mongo_collection.delete_one(query)


# def new_anual_premium_subscription(telegram_account_id):
#     expiration_timestamp = pendulum.now().add(years=1).timestamp()
#     DatabaseSubscription.mongo_collection.update_one(
#         filter={"telegram_account_id": telegram_account_id},
#         update={
#             "$set": {
#                 "label": "premium",
#                 "until_timestamp": expiration_timestamp,
#             }
#         },
#         upsert=True,
#     )
#     database_user = DatabaseUser(telegram_account_id)
#     database_user.reload()
#     database_user.set_premium_true()


# def search_expired_premium_subscriptions():
#     logger.info("Searching for expired premium subscriptions...")
#     documents = DatabaseSubscription.mongo_collection.find({"label": "premium"})
#     now_timestamp = pendulum.now().timestamp()
#     for document in documents:
#         if document["until_timestamp"] < now_timestamp:
#             yield document
#     else:
#         yield from list()  # Return empty list


# def deactivate_expired_premium_subscriptions():
#     for subscription in search_expired_premium_subscriptions():
#         database_user = DatabaseUser(subscription["telegram_account_id"])
#         database_user.reload()
#         database_user.set_premium_false()

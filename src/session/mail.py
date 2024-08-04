from src.session import mongo_database


class DatabaseMail:
    mongo_collection = mongo_database["mails"]
    ...
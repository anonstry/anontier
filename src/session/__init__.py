# Session manager

from pymongo import MongoClient
from dynaconf import settings

mongo_client = MongoClient(settings.MONGO_CONNECTION_STRING)
mongo_database = mongo_client[settings.MONGO_DATABASE_NAME]
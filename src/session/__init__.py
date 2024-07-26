# Session manager
# Maybe in future:
#   DatabaseUser (Mongo) for persistent
#   and MemoryUser (Redis) for cache
# or something like this...

from pymongo import MongoClient
from dynaconf import settings

import secrets

mongo_client = MongoClient(settings.MONGO_CONNECTION_STRING)
mongo_database = mongo_client[settings.MONGO_DATABASE_NAME]


def create_token(size=16):
    return secrets.token_hex(size)
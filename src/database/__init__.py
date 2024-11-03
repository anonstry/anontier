import secrets

from dynaconf import settings
from faker import Faker
from pymongo import MongoClient

mongo_client = MongoClient(settings.MONGO_CONNECTION_STRING)
mongo_database = mongo_client[settings.MONGO_DATABASE_NAME]


def create_token(size=16):
    return secrets.token_hex(size)


def create_username(words=2):
    fake = Faker()
    # title = " ".join([fake.word().capitalize() for _ in range(words)])
    # title = f"[{title}] #{fake.pystr(4, 6)}"
    title = f"{fake.name().title()} #{fake.pystr(4, 6)}"
    return title

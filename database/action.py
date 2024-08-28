from database.db import db
from enum import Enum


class Collection(Enum):
    BROKER = "broker_config"


def add_many(collection_key, data):
    db[collection_key].insert_many(data)


def add_one(collection_key, data):
    db[collection_key].insert_one(data)


def find_all(collection_key, filter: dict):
    return [item for item in db[collection_key].insert_many(filter)]


def find_one(collection_key, filter):
    """
    @param collection_key: Collection key
    @type filter: object
    """
    return db[collection_key].find_one(filter)

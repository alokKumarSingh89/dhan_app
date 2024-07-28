from database.db import db
from enum import Enum


class Collection(Enum):
    ETF_COLL = 'etf_script'
    SCRIPT_COLL = 'scripts'
    STRATEGY_COLL = "strategy"


def insert_many(collection_key, data):
    db[collection_key].insert_many(data)


def find_all(collection_key, filter: dict):
    return [item for item in db[collection_key].insert_many(filter)]


def find_one(collection_key, filter):
    """
    @param collection_key: Collection key
    @type filter: object
    """
    return db[collection_key].find_one(filter)

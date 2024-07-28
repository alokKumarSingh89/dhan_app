from pymongo import MongoClient

client = MongoClient("mongodb://admin:password@localhost:27017")

db = client.trade

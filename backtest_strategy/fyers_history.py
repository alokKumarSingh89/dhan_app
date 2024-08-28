
from brokers.fyers.login import Login
from datetime import timedelta
import time as dttime
from database.db import db
import pandas as pd
login = Login()
fyers = login.get()

max_day = 100

def fetch_from_broker(data):
    collection_name = f"{data['symbol']}-{data['resolution']}"
    response = fyers.history(data=data)
    # response = None
    if response['code'] != 200:
        raise Exception(f"{response['message']}")
    if len(response["candles"]) == 0:
        raise Exception(f"Holiday on {data['range_from']}")
    df = pd.DataFrame(columns=["date", "open", "high", "low", "close", "volumn"], data=response["candles"])
    df['date'] = pd.to_datetime(df['date'], unit='s')
    df['date'] = df['date'].dt.tz_localize('utc').dt.tz_convert('Asia/kolkata')
    df['date'] = df['date'].dt.tz_localize(None)
    df['date_only'] = df['date'].dt.strftime('%Y-%m-%d')
    records = df.to_dict('records')
    db[collection_name].insert_many(records)
    return df



def fetch_stock_data_from_db(data, date_range):
    collection_name = f"{data['symbol']}-{data['resolution']}"
    collection = [item for item in db[collection_name].find( { "date_only": { "$in": date_range } } )]
    if len(collection) > 0:
        df = pd.DataFrame(collection)
        df = df.drop(columns=["_id"], axis=1)
        return df
    else:
        return None


def fetch_etf(data, time):
    collection_name = f"eft-{data['range_from'].split('-')[0]}"
    collection = db[collection_name].find_one({"symbol": data['symbol'], "date": time})
    if collection is not None:
        print("Data from databse")
        del collection["_id"]
        df = pd.DataFrame([collection])
        return df
    else:
        response = fyers.history(data=data)
        if response['code'] != 200:
            raise Exception(f"{response['message']}")
        if len(response["candles"]) == 0:
            raise Exception(f"Holiday on {data['range_from']}")
        df = pd.DataFrame(columns=["date", "open", "high", "low", "close", "volumn"], data=response["candles"])
        df['date'] = pd.to_datetime(df['date'], unit='s')
        df['date'] = df['date'].dt.tz_localize('utc').dt.tz_convert('Asia/kolkata')
        df['date'] = df['date'].dt.tz_localize(None)
        df['symbol'] = data["symbol"]
        records = df.to_dict('records')
        db[collection_name].insert_many(records)
        return df
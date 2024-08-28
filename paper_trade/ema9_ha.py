import time
from datetime import datetime, timedelta

import requests
from bson import ObjectId

from backtest_strategy.fyers_history import fetch_from_broker
from backtest_strategy.strategy_list.ha import calculate_heikin_ashi
import ta
import calendar
import pandas as pd
import logging
from database.db import db


def get_history_data(script):
    now = datetime.today()
    start_date = now - timedelta(days=10)
    end_date = now
    data = {
        "symbol": f"NSE:{script}-EQ",
        "resolution": "5",
        "date_format": "0",
        "range_from": calendar.timegm(start_date.timetuple()),
        "range_to": calendar.timegm(end_date.timetuple()),
        "cont_flag": "1"
    }
    return fetch_from_broker(data)


def format_data(data):
    new_data = data.copy()
    new_data = new_data.sort_values(by='date')
    new_data = calculate_heikin_ashi(new_data)
    close = new_data["HA_Close"].to_numpy()
    ema_9 = ta.trend.EMAIndicator(pd.Series(close), 9, False).ema_indicator()
    new_data["ema_9"] = round(ema_9, 2)
    new_data["ema_9"] = new_data["ema_9"].fillna(0.0)
    return new_data


last_insert_id = None


def place_order(price, date, symbol, transaction_type):
    current = datetime.now()
    global last_insert_id
    result = db[f"paper-trading-{current.year}"].insert_one({
        "entry_price": price,
        "entry_date": date,
        "symbol": symbol,
        "transaction_type": transaction_type
    })
    last_insert_id = result.inserted_id
    print(last_insert_id, result)


def exit_postion(price, date):
    global last_insert_id
    current = datetime.now()
    result = db[f"paper-trading-{current.year}"].update_one({'_id': ObjectId(last_insert_id)}, {'$set': {
        "exit_price": price,
        "exit_date": date
    }}, upsert=False)
    print(result)
    last_insert_id = None


timeframe = 5  # 5 min

def get_live_feed(symbol: str):
    data = requests.get(f"http://localhost:8000/script/{symbol}")
    print(symbol, data)
def ema9_ha(symbol: str):
    previous_data = get_history_data(symbol)
    previous_data = format_data(previous_data)
    print(f"Script:{symbol}")
    current = datetime.now()
    is_in_trade = False
    trade_type = 0
    start_time = datetime(year=current.year, month=current.month, day=current.day, hour=9, minute=25, second=0)
    end_time = datetime(year=current.year, month=current.month, day=current.day, hour=15, minute=20, second=0)
    while current.time() < end_time.time():
        if current.time() >= start_time.time():
            print("time reached", current)
            print(current.minute % timeframe, timeframe, current.minute, current.second)
            if current.minute % timeframe == 0 and current.second == 0:
                current_feed = get_live_feed(symbol=symbol)
                time.sleep(1)
                return
                data = pd.concat(previous_data, current_feed)

                index = len(data) - 2
                date = data.loc[index, "date"]
                HA_Close = data.loc[index, "HA_Close"]
                ema = data.loc[index, "ema_9"]
                candle_type = data.loc[index, "Candle_Type"]
                logging.warning(f"HA_Close:{HA_Close},EMA:{ema},Date:{date},candle_type:{candle_type}, and trade_type:{trade_type}")
                if ema < HA_Close and candle_type == 1 and is_in_trade == False:
                    logging.warning(f"Buy Entry {date}")
                    place_order(price=HA_Close, transaction_type="Buy", date=date, symbol=symbol)
                    is_in_trade = True
                    trade_type = 1
                elif ema > HA_Close and candle_type == -1 and is_in_trade == False:
                    place_order(price=HA_Close, transaction_type="Sell", date=date, symbol=symbol)
                    is_in_trade = True
                    trade_type = -1
                elif is_in_trade == True and trade_type == 1 and candle_type == -1:
                    exit_postion(price=HA_Close, date=date)
                    is_in_trade = False
                    trade_type = 0
                    logging.warning(f"Buy Close {date}")
                    if ema > HA_Close:
                        logging.warning(f"Sell Entry {date}")
                        place_order(price=HA_Close, transaction_type="Sell", date=date, symbol=symbol)
                        is_in_trade = True
                        trade_type = -1

                elif is_in_trade == True and trade_type == -1 and candle_type == 1:
                    logging.warning(f"Sell Close {date}")
                    exit_postion(price=HA_Close, date=date)
                    is_in_trade = False
                    trade_type = 0
                    if ema < HA_Close:
                        logging.warning(f"Buy Entry {date}")
                        place_order(price=HA_Close, transaction_type="Buy", date=date, symbol=symbol)
                        is_in_trade = True
                        trade_type = 1
            time.sleep(1)
        else:
            time.sleep(1)
            print(current, " Waiting for Time to check new ATM ")
        current = datetime.now()
    if current.time() > end_time.time() and is_in_trade == True:
        exit_postion(price=HA_Close, date=date)
        is_in_trade = False
        trade_type = 0
    print("Time up")


# data = {
#     "symbol":"NSE:SBIN-EQ",
#     "ohlcv_flag":"1"
# }
#
# from brokers.fyers.login import Login
# login = Login()
# fyers = login.get()
# response = fyers.depth(data=data)
# print(response)
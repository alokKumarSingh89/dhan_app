from brokers.fyers.login import Login
import pandas as pd
import pandas_ta as pta
import numpy as np
from datetime import datetime, timedelta
import ta
import time
import asyncio
import logging
from strategy.fyers_history import fetch_stock_data


login = Login()
fyers = login.get()


# close = df["close"].to_numpy()
# ema = ta.trend.EMAIndicator(pd.Series(close), 20, False).ema_indicator()
def calculate_levels(data, lookback_period=60):
    data['High_15m'] = max([data["high"].iloc[0]], [data["high"].iloc[1]], [data["high"].iloc[3]])[0]
    data['Low_15m'] = min([data["low"].iloc[0]], [data["low"].iloc[1]], [data["low"].iloc[2]])[0]
    # Rolling for candle
    #  = data['high'].rolling(window=lookback_period, min_periods=1).max()
    #  = data['low'].rolling(window=lookback_period, min_periods=1).min()
    return data


sl_pr = .5/100

def take_entry(data, pnl, loc, type):
    pnl["date"].append(data['date'].iloc[loc])
    pnl["entry"].append(data['close'].iloc[loc])
    if type == -1:
        pnl["transaction"].append('Sell')
        sl = round(data['close'].iloc[loc] + (data['close'].iloc[loc] * sl_pr), 3)
        return sl
    elif type == 1:
        pnl["transaction"].append('Buy')
        sl = round(data['close'].iloc[loc] - (data['close'].iloc[loc] * sl_pr), 3)
        return sl

def place_order(data, pnl):
    sl = 0
    is_any_trade = False
    is_in_trade = False
    is_trade_open = False
    number_of_trade = 1
    trade_type = 0
    for i in range(len(data)):
        if number_of_trade <= 0 and is_in_trade == False:
            break
        close = data.loc[i, 'close']
        registance = data.loc[i, 'High_15m']
        support = data.loc[i, 'Low_15m']
        logging.warning(f"Date-{data['date'].iloc[i]}, sl:{sl}, close({data['close'].iloc[i]})")
        if close <= support and is_in_trade == False:
            logging.warning("Sell Entry")
            sl = take_entry(data=data,pnl=pnl,loc=i,type=-1)
            is_in_trade = True
            is_trade_open = True
            is_any_trade= True
            trade_type = -1
            number_of_trade -= 1
        elif close >= registance and is_in_trade == False:
            logging.warning("Buy  Entry")
            is_any_trade = True
            sl = take_entry(data=data, pnl=pnl, loc=i, type=1)
            is_in_trade = True
            is_trade_open = True
            trade_type = 1
            number_of_trade -= 1
        elif data['close'].iloc[i] >= sl and is_in_trade == True and trade_type == -1:
            logging.warning("Sell Exit")
            pnl["exit"].append(data['close'].iloc[i])
            pnl["exit_time"].append(data['date'].iloc[i])
            is_in_trade = False
            is_trade_open = False
        elif  data['close'].iloc[i] <= sl and is_in_trade == True and trade_type == 1:
            logging.warning("Buy Exit")
            pnl["exit"].append(data['close'].iloc[i])
            pnl["exit_time"].append(data['date'].iloc[i])
            is_in_trade = False
            is_trade_open = False
        elif trade_type == -1:
            logging.warning("Sell SL checking")
            new_sl = round(data['close'].iloc[i] + (data['close'].iloc[i] * sl_pr), 3)
            if ((-sl + new_sl) / sl) > sl_pr:
                sl = round(data['close'].iloc[i] + (data['close'].iloc[i] * (sl_pr / 2)), 3)
        elif trade_type == 1:
            logging.warning("Buy SL checking")
            new_sl = round(data['close'].iloc[i] - (data['close'].iloc[i] * sl_pr), 3)
            if ((-sl + new_sl) / sl) > sl_pr:
                sl = round(data['close'].iloc[i] - (data['close'].iloc[i] * (sl_pr / 2)), 3)


    if is_trade_open == True:
        pnl["exit"].append(data['close'].iloc[-2])
        pnl['exit_time'].append(data['date'].iloc[-2])


    if is_any_trade == False:
        pnl["date"].append(data['date'].iloc[-1])
        pnl["entry"].append(None)
        pnl["transaction"].append(None)
        pnl["exit"].append(None)
        pnl['exit_time'].append(None)


def start(start_date, end_date,name, script):
    pnl = {
        "date":[],
        "entry":[],
        "exit":[],
        "exit_time": [],
        # "pnl":[],
        "transaction":[]
    }
    while start_date <= end_date:
        try:
            date = start_date.strftime('%Y-%m-%d')
            data = fetch_stock_data(data={
                "symbol": f"NSE:{script}-EQ",
                "resolution": "5",
                "date_format": "1",
                "range_from": date,
                "range_to": date,
                "cont_flag": "1"

            })
            data = calculate_levels(data, lookback_period=74)
            place_order(data=data, pnl=pnl)
        except Exception as e:
            logging.warning(e)
        time.sleep(1)
        start_date += timedelta(days=1)

    df = pd.DataFrame(pnl)
    df.to_csv(f"{name}-{script}.csv", index=False)

def year_wise():
    for i in range(2023,2024):
        for symbol in ["LTIM"]:
            start(start_date=datetime(i, 1, 1), end_date=datetime(i, 12, 31), name=i, script=symbol)



year_wise()


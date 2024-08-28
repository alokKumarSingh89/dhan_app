import time
from datetime import datetime, timedelta
import pandas as pd
from pprint import pprint
import ta
from ha import calculate_heikin_ashi
import logging

from backtest_strategy.fyers_history import fetch_stock_data_from_db, fetch_from_broker, max_day

config = {
    "entry_hour": 9,
    "entry_minutes": 25,
    "exit_hour": 15,
    "exit_minutes": 15,

}


def get_today_data(symbol, resolution, date):
    data = {
        "symbol": f"NSE:{symbol}-EQ",
        "resolution": resolution,
    }
    db_data = fetch_stock_data_from_db(data=data, date_range=[date.strftime('%Y-%m-%d')])
    return db_data


def get_pnl(data):
    return  round(((data["exit"] - data["entry"])/data["entry"])*100 if data["tranaction_type"] == "Buy" else ((-data["exit"] + data["entry"])/data["exit"])*100, 2)

def process(data, symbol, resolution, start_date):
    global config
    is_in_trade = False
    trade_type = 0
    pnl = {
        "entry": [],
        "exit": [],
        "entry_time": [],
        "exit_time": [],
        "tranaction_type": [],
    }
    current_data = get_today_data(symbol, resolution, start_date)
    if current_data is None:
        return None
    for index, row in current_data.iterrows():
        previous_len = len(data)
        data.loc[previous_len] = row
        data = format_data(data)
        candle_type = data.loc[previous_len, "Candle_Type"]
        date = data.loc[previous_len, "date"]
        HA_Close = data.loc[previous_len, "HA_Close"]
        ema = data.loc[previous_len, "ema_9"]
        start_time = config["entry_hour"]*60+config["entry_minutes"]
        exit_time = config["exit_hour"]*60+config["exit_minutes"]
        current_time = date.hour*60+date.minute
        if start_time <= current_time <= exit_time:
            logging.warning(f"Date:{date},candle_type:{candle_type}, and trade_type:{trade_type}")
            if ema < HA_Close and candle_type == 1 and is_in_trade == False:
                logging.warning(f"Buy Entry {date}")
                pnl["entry"].append(HA_Close)
                pnl["tranaction_type"].append("Buy")
                pnl["entry_time"].append(date)
                is_in_trade = True
                trade_type = 1
            elif ema > HA_Close and candle_type == -1 and is_in_trade == False:
                logging.warning(f"Sell Entry {date}")
                pnl["entry"].append(HA_Close)
                pnl["tranaction_type"].append("Sell")
                pnl["entry_time"].append(date)
                is_in_trade = True
                trade_type = -1
            elif is_in_trade == True and trade_type == 1 and candle_type == -1:
                pnl["exit"].append(HA_Close)
                pnl["exit_time"].append(date)
                is_in_trade = False
                trade_type = 0
                logging.warning(f"Buy Close {date}")
                if ema > HA_Close:
                    logging.warning(f"Sell Entry {date}")
                    pnl["entry"].append(HA_Close)
                    pnl["tranaction_type"].append("Sell")
                    pnl["entry_time"].append(date)
                    is_in_trade = True
                    trade_type = -1

            elif is_in_trade == True and trade_type == -1 and candle_type == 1:
                logging.warning(f"Sell Close {date}")
                pnl["exit"].append(HA_Close)
                pnl["exit_time"].append(date)
                is_in_trade = False
                trade_type = 0
                if ema < HA_Close:
                    logging.warning(f"Buy Entry {date}")
                    pnl["entry"].append(HA_Close)
                    pnl["tranaction_type"].append("Buy")
                    pnl["entry_time"].append(date)
                    is_in_trade = True
                    trade_type = 1

        elif current_time > exit_time and is_in_trade == True:
            pnl["exit"].append(HA_Close)
            pnl["exit_time"].append(date)
            is_in_trade = False
            trade_type = 0
            logging.warning(f"End of day Close {date}-> {trade_type}")
        else:
            logging.warning("Not doing anything")
    df = pd.DataFrame(pnl)
    df["pnl"] = df.apply(get_pnl, axis=1)
    return df



def get_historycal_data(date, symbol, resolution):
    data = {
        "symbol": f"NSE:{symbol}-EQ",
        "resolution": resolution,
    }
    end = date - timedelta(days=3)
    start = date - timedelta(days=1)
    date_range = [item.strftime('%Y-%m-%d') for item in pd.date_range(start=end, end=start)]
    db_data = fetch_stock_data_from_db(data=data, date_range=date_range)
    return db_data


def format_data(data):
    new_data = data.copy()
    new_data = new_data.sort_values(by='date')
    new_data = calculate_heikin_ashi(new_data)
    close = new_data["HA_Close"].to_numpy()
    ema_9 = ta.trend.EMAIndicator(pd.Series(close), 9, False).ema_indicator()
    new_data["ema_9"] = round(ema_9, 2)
    new_data["ema_9"] = new_data["ema_9"].fillna(0.0)
    return new_data


def start(start_date, symbol, resolution):
    try:
        db_data = get_historycal_data(date=start_date, symbol=symbol, resolution=resolution)
        if db_data is None:
            print("problem in db")
            return None
        data = db_data.copy()
        data.drop_duplicates(subset=['date'], inplace=True)
        data = data.reset_index()
        data = data.drop(columns=["index", "date_only"], axis=1)
        data = format_data(data=data)
        return process(data, symbol, resolution, start_date)

    except Exception as e:
        print(e)
        return None


def main():
    # month = 7
    # year = 2020
    symbol="INDUSINDBK"
    resolution = "5"
    for year in range(2024,2025):
        for month in range(1, 13):
            df = pd.DataFrame()
            for day in range(1,32):
                try:
                    data = start(start_date=datetime(year, month, day), symbol=symbol, resolution=resolution)
                    if data is not None:
                        df = pd.concat([df,data])
                except Exception as e:
                    print(e)
            df.reset_index(inplace=True)
            df.drop(columns=["index"], inplace=True)
            df.to_csv(f"{symbol}-{resolution}-{month}-{year}.csv")

main()
def pull_data():
    now = datetime.today()
    for i in range(1,4):
        start_date = now - timedelta(days=100)
        end_date = now
        now = start_date - timedelta(days=1)
        data = {
            "symbol": "NSE:BAJFINANCE-EQ",
            "resolution": "5",
            "date_format": "1",
            "range_from": start_date.strftime('%Y-%m-%d'),
            "range_to": end_date.strftime('%Y-%m-%d'),
            "cont_flag": "1"
        }
        tmp = fetch_from_broker(data)
        print(tmp)
        time.sleep(1)
    print("Done")

# pull_data()

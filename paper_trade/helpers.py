import calendar
from datetime import datetime, timedelta
import pandas as pd
import ta
import requests
from backtest_strategy.fyers_history import fetch_from_broker
from backtest_strategy.strategy_list.ha import calculate_heikin_ashi


def format_data(data, config):
    h_data = data.copy()
    if config["chart_type"] == "HA":
        h_data = add_ha(h_data)
    if "ema" in config["indicator"]:
        h_data = add_ema(h_data)
    return h_data


def get_live_feed(symbol, timeframe):
    data = requests.get(f"http://localhost:8888/script/{symbol}")
    data = data.json()
    if len(data['open']) == 0:
        return None
    df = pd.DataFrame(data)
    df["date1"] = pd.to_datetime(df['date'])
    df = df.set_index("date1")
    dataframe_M5 = df.resample(timeframe).agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volumn': 'sum', 'date':'first'})
    dataframe_M5["date"] = pd.to_datetime(dataframe_M5["date"])
    return dataframe_M5

def add_ema(data):
    new_data = data.copy()
    new_data = new_data.sort_values(by='date')
    close = new_data["HA_Close"].to_numpy()
    ema_9 = ta.trend.EMAIndicator(pd.Series(close), 9, False).ema_indicator()
    new_data["ema_9"] = round(ema_9, 2)
    new_data["ema_9"] = new_data["ema_9"].fillna(0.0)
    return new_data
def add_ha(data):
    new_data = data.copy()
    new_data = new_data.sort_values(by='date')
    return calculate_heikin_ashi(new_data)

def get_history_data(data, days):
    now = datetime.today()
    start_date = now - timedelta(days=days)
    end_date = now
    data = {
        **data,
        "date_format": "0",
        "range_from": calendar.timegm(start_date.timetuple()),
        "range_to": calendar.timegm(end_date.timetuple()),
        "cont_flag": "1"
    }
    return fetch_from_broker(data)
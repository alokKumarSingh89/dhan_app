import pandas as pd
from datetime import datetime, timedelta
import ta
import time
import pandas_ta as pta
import logging

from strategy.fyers_history import fetch_stock_data
from ha import calculate_heikin_ashi

holiday_list = pd.read_json("./holiday_list.json")
holiday_list = list(holiday_list["data"])

def create_dataframe(start_date, end_date, script, resolution):
    df_list = []
    while start_date <= end_date:
        try:
            date = start_date.strftime('%Y-%m-%d')
            if date in holiday_list:
                print("Holiday From DB", date)
                start_date = start_date + timedelta(days=1)
                continue
            data = {
                "symbol": f"NSE:{script}-INDEX",
                "resolution": resolution,
                "date_format": "1",
                "range_from": date,
                "range_to": date,
                "cont_flag": "1"

            }
            res = fetch_stock_data(data)
            df_list.append(res)
        except Exception as e:
            print(e)
        start_date = start_date + timedelta(days=1)
    data = pd.concat(df_list)
    data = data.reset_index()
    data.drop(columns=["index"],inplace=True)
    data = calculate_heikin_ashi(data)
    close = data["HA_Close"].to_numpy()
    macd_ind = ta.trend.MACD(pd.Series(close))
    data["macd"] = round(macd_ind.macd(),2)
    data["signal"] = round(macd_ind.macd_signal(), 2)
    data["bb_hband"] = round(ta.volatility.bollinger_hband(pd.Series(close)), 2)
    data["bb_lband"] = round(ta.volatility.bollinger_lband(pd.Series(close)), 2)
    data["bb_mavg"] = round(ta.volatility.bollinger_mavg(pd.Series(close)), 2)
    data["bb_mavg"] = data["bb_mavg"].fillna(0.0)
    data["macd"] = data["macd"].fillna(0.0)
    data["signal"] = data["signal"].fillna(0.0)
    data["bb_hband"] = data["bb_hband"].fillna(0.0)
    data["bb_lband"] = data["bb_lband"].fillna(0.0)

    return data

def check_ind(first, sec):
    if first < sec:
        return -1
    elif first > sec:
        return +1
    else:
        return 0

def check_tide(data, date):
    date = date.strftime('%Y-%m-%d')
    df = data.copy()
    df = df[df["date"] < date]

    macd_diff = check_ind(df["macd"].iloc[-2], df["macd"].iloc[-1])
    pre_macd_diff = check_ind(df["macd"].iloc[-3], df["macd"].iloc[-2])
    print(macd_diff, pre_macd_diff)
    print(df.iloc[-3],df.iloc[-2],df.iloc[-1])
    # return macd_diff

def process(daily_df, houly_df, start_date):
    # date = start_date.strftime('%Y-%m-%d')
    check_tide(daily_df, pd.Timestamp("2024-07-03"))
    # for index in range(len(houly_df)):
    #     if houly_df.loc[index,"signal"] == 0.0 or houly_df.loc[index,"macd"] == 0.0:
    #         continue
    #     elif pd.Timestamp(start_date) <= pd.Timestamp(houly_df.loc[index,"date_only"]):
    #         check_tide(daily_df, pd.Timestamp(houly_df.loc[index,"date_only"])-timedelta(days=1))
    #
    # print(daily_df)


def start(start_date, script):
    end_date = datetime.now()
    # Need atleast 190 candle
    start = start_date - timedelta(days=180)
    daily_df = create_dataframe(start_date=start, end_date=end_date,script=script, resolution="D")
    logging.info("TEst")
    # Hourly_df
    start = start_date - timedelta(days=100)
    houly_df = create_dataframe(start_date=start, end_date=end_date,script=script, resolution="60")
    process(daily_df,houly_df, start_date)
# For Daily need 6 months data

start(start_date=datetime(2024, 7, 1),script="NIFTYBANK")
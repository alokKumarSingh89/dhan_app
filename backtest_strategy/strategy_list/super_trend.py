from datetime import datetime, timedelta
import pandas_ta as pta
import pandas as pd
from strategy.fyers_history import fetch_stock_daily_data
from strategy.strategy_list.ha import calculate_heikin_ashi

holiday_list = pd.read_json("./holiday_list.json")
holiday_list = list(holiday_list["data"])


def determine_ha_candle_type(data):
    price_diff = (abs(data['HA_Close'] - data['HA_Open']) / data['HA_Close']) * 100
    if data['HA_Close'] > data['HA_Open'] and price_diff > .2:
        return 1
    elif data['HA_Close'] < data['HA_Open'] and price_diff > .2:
        return -1
    else:
        return 0


def place_order(data):
    is_in_trade = False
    trade_type = 0
    entry_hour = 9
    entry_minuts = 20
    pnl = {
        "entry_date": [],
        "exit_date": [],
        "entry_price": [],
        "exit_price": [],
        "tranaction_type": [],

    }
    sl = 0
    number_of_trade = 2
    for row_index in range(len(data)):
        if data["sup"].iloc[row_index] > 0.0:
            row = data.iloc[row_index]
            date = row["date"]
            close = row["close"]
            HA_Open = row["HA_Open"]
            HA_High = row["HA_High"]
            HA_Low = row["HA_Low"]
            HA_Close = row["HA_Close"]
            super = row["sup"]
            Candle_Type = row["Candle_Type"]
            # Check super trande direction, True == Bullish, False == Bearish
            super_trande = super < HA_Close
            # print(date, HA_Open, HA_Close, HA_Low, HA_High, super, Candle_Type, super_trande)

            # is_entry_time = (date.hour*60 +date.minute) >= (entry_hour*60 + entry_minuts)
            # if is_entry_time == False:
            #     number_of_trade = 2
            #     continue
            # if number_of_trade == 0:
            #     continue
            # # Buy Trade
            print(f"super_trande: {super_trande}:{HA_Close}-{super} at {date} ")
            if is_in_trade == False and super_trande == True and Candle_Type == 1:
                is_in_trade = True
                pnl["entry_date"].append(date)
                pnl["entry_price"].append(close)
                pnl["tranaction_type"].append("Buy")
                sl = data.iloc[row_index-2]["HA_Low"]
                trade_type = 1
                print(f"Buy at {date}")
            # Sell Trade
            elif is_in_trade == False and super_trande == False  and Candle_Type == -1:
                is_in_trade = True
                pnl["entry_date"].append(date)
                pnl["entry_price"].append(close)
                pnl["tranaction_type"].append("Sell")
                trade_type = -1
                sl = data.iloc[row_index - 2]["HA_High"]
                print(f"Sell at {date}")
            elif is_in_trade == True and super_trande == True and Candle_Type == -1:
                is_in_trade = False
                pnl["exit_date"].append(date)
                pnl["exit_price"].append(close)
                trade_type = 0
                number_of_trade -= 1
                print(f"Exit from buy at {date}")
            elif is_in_trade == True and super_trande == False and Candle_Type == 1:
                is_in_trade = False
                pnl["exit_date"].append(date)
                pnl["exit_price"].append(close)
                trade_type = 0
                number_of_trade -= 1
                print(f"Exit from Sell at {date}")
            # elif date.hour == 15 and date.minute == 25 and is_in_trade == True:
            #     is_in_trade = False
            #     pnl["exit_date"].append(date)
            #     pnl["exit_price"].append(close)
            #     trade_type = 0
            #     number_of_trade -= 1
            #     print(f"Exit {date}")

    if is_in_trade == True:
        row = data.iloc[-1]
        pnl["exit_date"].append(row["date"])
        pnl["exit_price"].append(row["close"])
        print(f"Exit {date}")
    df = pd.DataFrame(pnl)
    df.to_csv("test.csv", mode="w")

def super_trend(start_date, end_date, name, symbol):
    # Super trande
    df_list = []
    while start_date <= end_date:
        start = start_date.strftime('%Y-%m-%d')
        start_date = start_date + timedelta(days=1)
        if start in holiday_list:
            print("Holiday From DB", start)
            continue
        try:
            data = fetch_stock_daily_data(data={
                "symbol": f"NSE:{symbol}-EQ",
                "resolution": "15",
                "date_format": "1",
                "range_from": start,
                "range_to": start,
                "cont_flag": "1"

            })
            df_list.append(data)
        except Exception as e:
            print(e)
    data = pd.concat(df_list)
    data = data.reset_index()
    data = calculate_heikin_ashi(data)
    high = data["HA_High"].to_numpy()
    low = data["HA_Low"].to_numpy()
    close = data["HA_Close"].to_numpy()
    supertrend = pd.DataFrame(pta.supertrend(pd.Series(high), pd.Series(low), pd.Series(close), 10, 3))
    data["sup"] = supertrend.iloc[:, 0]
    data["sup"] = data["sup"].fillna(0.0)
    data['Candle_Type'] = data.apply(determine_ha_candle_type, axis=1)
    place_order(data)
    # print(data)


super_trend(start_date=datetime(2024, 7, 1), end_date=datetime(2024, 8, 2), name=2024, symbol="LTIM")

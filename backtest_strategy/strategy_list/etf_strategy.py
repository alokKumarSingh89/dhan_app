from datetime import timedelta, datetime
import pandas as pd

from strategy.fyers_history import fetch_etf

holiday_list = pd.read_json("./holiday_list.json")
holiday_list = list(holiday_list["data"])

entry = {

}

def process(data, symbol):
    global entry
    for i in range(len(data)):
        open = data.loc[i,"open"]
        close = data.loc[i,"close"]
        per_change = data.loc[i, "per_change"]
        entry_value = 0 if len(entry[symbol]['entry']) == 0 else entry[symbol]['entry'][-1]
        if per_change < -2:
            entry[symbol]['entry'].append(close)



def start(start_date, end_date, symbol, name):
    global entry
    df_list = []
    while start_date <= end_date:
        start = start_date.strftime('%Y-%m-%d')
        time  = start_date + timedelta(hours=5, minutes=30)
        start_date = start_date + timedelta(days=1)
        if symbol not in entry:
            entry[symbol] = {
                "entry": [],
                "en_date": [],
                "ex_date": [],
                "exit": []
            }
        if start in holiday_list:
            print("Holiday From DB", start)
            continue
        try:
            data = fetch_etf(data={
                "symbol": f"NSE:{symbol}-EQ",
                "resolution": "D",
                "date_format": "1",
                "range_from": start,
                "range_to": start,
                "cont_flag": "1"

            }, time=time)
            df_list.append(data)
        except Exception as e:
            print("Exception: ",e, start_date)
    data = pd.concat(df_list)
    data = data.reset_index()
    data["per_change"] = ((data["close"]-data["open"])/data["open"])*100
    process(data, symbol)


start(start_date=datetime(2023, 10, 27), end_date=datetime(2024, 8, 2), name=2024, symbol="ITETF")

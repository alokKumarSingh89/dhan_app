from datetime import datetime
import time

import pandas as pd

from .helpers import get_history_data, format_data, get_live_feed

last_insert_id = None #For paper trade

def check_entry_condition(data, config):
    last_row = data.iloc[-1]
    entry_condition = config["entry_condition"]

    print(config)


def process(config):
    h_data = get_history_data(data={
        "symbol": config["script"],
        "resolution":config["time_frame"],
    }, days=config["old_data"])
    current = datetime.now()
    is_in_trade = False
    trade_type = 0
    start_time = datetime(year=current.year, month=current.month, day=current.day, hour=config["entry"]["hour"], minute=config["entry"]["minutes"], second=0)
    end_time = datetime(year=current.year, month=current.month, day=current.day, hour=config["exit"]["hour"], minute=config["exit"]["minutes"], second=0)
    print(config)
    while current.time() < end_time.time():
        if current.time() > start_time.time():
            print("Witing for timeframe", current)
            if current.minute % config["time_frame"] == 0 and current.second == 0:
                current_feed = get_live_feed(symbol=config["script"], timeframe=config["resmaple"])
                data = pd.concat([h_data, current_feed])
                data = data.reset_index()
                data.drop(columns=["index"], inplace=True)
                data.sort_values("date")
                data = format_data(data, config)
                check_entry_condition(data, config)
            time.sleep(1)
        else:
            print(f"Waiting to start , current time is {current}")
            time.sleep(1)
        current = datetime.now()
    print("Done For day")
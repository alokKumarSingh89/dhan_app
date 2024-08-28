
import asyncio
import time

import pandas as pd
from brokers.fyers.login import Login
from brokers.fyers.sticke import getLTP
from database.action import Collection, find_one

index_list = {
    "NIFTY": "NSE:NIFTY50-INDEX",
    "BankNifty": "NSE:NIFTYBANK-INDEX"
}
login = Login()




async def cnc_strategy(strategy):
    global index_list
    script = strategy.get("script")
    legs = strategy.get("legs")
    script_name = ""
    if index_list.get(script) is None:
        script_name = f"NSE:{script}-EQ"
    else:
        script_name = index_list[script]
    script_ltp = find_one(Collection.ScriptList, {"symbol": script_name})
    script_ltp = getLTP(script_name)
    print(script_name, script_ltp, script_ltp)


async def mis_strategy(strategy):
    global index_list
    script = strategy.get("script")
    legs = strategy.get("legs")
    script_name = ""
    if index_list.get(script) is None:
        script_name = f"NSE:{script}-EQ"
    else:
        script_name = index_list[script]
    script_config = find_one(Collection.ScriptList, {"symbol": script_name})
    script_ltp = getLTP(script_name)
    print(script_name,script_config, script_ltp)


async def main(strategies):

    for strategy in strategies:
        if strategy.get("order_type") == "MIS":
            asyncio.create_task(mis_strategy(strategy))
        else:
            asyncio.create_task(cnc_strategy(strategy))


market_config = {
    "open_hour": 9,
    "open_min": 20,
    "close_hour": 21,
    "close_min": 40
}


def run_engine(strategies):
    current = pd.Timestamp.now()
    print(current.hour, current.minute, current.min)
    while True:
        if current.hour < market_config["open_hour"] or (current.hour == market_config["open_hour"] and current.minute < market_config["open_min"]):
            time.sleep(1)
            continue
        elif (current.hour > market_config["close_hour"]) or (current.minute > market_config["close_min"]):
            print("Market Closed")
            break
        elif current.hour >= market_config["open_hour"] and current.minute >= market_config["open_min"]:
            asyncio.run(main(strategies))
            break
        else:
            print("Please check")
            break
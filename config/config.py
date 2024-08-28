import pandas as pd
import os
import json
from brokers.fyers.login import Login
fyers = Login().get()

#

def get_script_list():
    f = open(f"{os.getcwd()}/config/config.json")
    instument_list = []
    data = json.load(f)
    equity = [f"NSE:{item}-EQ" for item in data["equity"]]
    fno = data["FNO"]
    instument_list = instument_list + fno
    index = [f"NSE:{item}-INDEX" for item in data["index"]]

    for item in index+equity:
        data = {
            "symbol": item,
            "strikecount": 10,
            "timestamp": ""
        }
        response = fyers.optionchain(data=data)
        instument_list = instument_list + [script["symbol"] for script in response["data"]["optionsChain"]]
    return instument_list


def get_strategy_list():
    f = open(f"{os.getcwd()}/config/strategy.json")
    data = json.load(f)
    return data

get_script_list()
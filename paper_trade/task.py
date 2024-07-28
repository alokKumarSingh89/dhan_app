from fyers_apiv3 import fyersModel
import pandas as pd
import time
from login.fyers_login.login import Login

from database.action import Collection, find_one, find_all, insert_many

login = Login()


def update_stick(strategy):
    running_template = []
    scripts = find_one(Collection.SCRIPT_COLL, {"name": strategy["script"]})
    fyers = login.get()
    data = {
        "symbol": scripts["symbol"],
        "strikecount": 20,
        "timestamp": ""
    }
    response = fyers.optionchain(data=data)
    options_chain = response["data"]["optionsChain"]
    atm_stick_info = list(filter(lambda x: x["strike_price"] == -1, options_chain))[0]
    ltp = int(atm_stick_info["ltp"])
    rem = int(ltp % scripts["stick_diff"])
    atm = 0
    if rem > int(scripts["stick_diff"] / 2):
        atm = ltp + (scripts["stick_diff"] - rem)
    else:
        atm = ltp - rem
    for leg in strategy["legs"]:
        tmp = None
        if leg["option_type"] == "CE":
            ce = atm + leg["sticke"] * scripts["stick_diff"]
            tmp = list(filter(lambda x: x["strike_price"] == ce and x["option_type"] == "CE", options_chain))[0]
        else:
            pe = atm - leg["sticke"] * scripts["stick_diff"]
            tmp = list(filter(lambda x: x["strike_price"] == pe and x["option_type"] == "PE", options_chain))[0]
        running_template.append(
            {"strategy_id": strategy["_id"], "start_date": pd.Timestamp.now(), "o_symbol": tmp["symbol"],
             "start_ltp": tmp["ltp"], "current_ltp": 0})
    return running_template


def check_and_update_ltp(queue):
    script = [x["o_symbol"] for x in queue]
    symbols = ",".join(script)
    now = pd.Timestamp.now()
    while True:
        print("----Proceesing-----")
        if now.hour == 21 and now.minute > 20:
            break
        fyers = login.get()

        data = {
            "symbols": symbols
        }
        response = fyers.quotes(data=data)
        for s in response["d"]:
            pass
        time.sleep(60)


def run_all_availble():
    running_queue = [];
    for strategy in find_all(collection_key=Collection.STRATEGY_COLL, filter={}):
        running_strategy = find_one("running_queue", {"strategy_id": strategy["_id"]})
        if running_strategy is None:
            running_template = update_stick(strategy)
            running_queue = running_queue + running_template
            insert_many("running_queue", running_queue)
        else:
            tmp = [item for item in find_all("running_queue", {"strategy_id": strategy["_id"]})]
            running_queue = running_queue + tmp
    check_and_update_ltp(running_queue);
    # connect_with_broker(script=running_queue, token=token.get_token())

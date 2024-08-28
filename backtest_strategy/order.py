from brokers.fyers.login import Login
from database.action import Collection, find_one, add_many
import pandas as pd
login = Login()

order_config = {
    "close_h":15,
    "close_m":30,
    "open_h":9,
    "open_m":15
}

def place_order(strategy):
    current_time = pd.Timestamp.now()
    order = []
    scipy_config = find_one(Collection.ScriptList,{"symbol":strategy["symbol"]})
    fyer = login.get()
    option_chain = fyer.optionchain({"symbol":strategy["symbol"], "strikecount": 15})["data"]["optionsChain"]
    symbol_config = list(filter(lambda x: x["strike_price"] == -1,option_chain))

    symbol_ltp = symbol_config[0]["ltp"]
    atm = (symbol_ltp//scipy_config["stick_diff"])*scipy_config["stick_diff"]
    for leg in strategy["legs"]:
        strick = atm + (leg["sticke"]*scipy_config["stick_diff"])
        p = list(filter(lambda x: x["strike_price"] == strick and x['option_type'] == leg["option_type"], option_chain))[0]
        # print(strick, p)
        order.append({
            "start_date": pd.Timestamp.now(),
            "end_date": "",
            "sticke": p["symbol"],
            "entry_price": p["ltp"],
            "exit_price": 0,
            "name": strategy["name"],
            "symbol": strategy["symbol"],
            "expiry": strategy["expiry"],
            "strategy_id":strategy["_id"],
            "lot": strategy["lot"],
        })
    # print(order)
    add_many(Collection.RunningQueue, order)
    return "Done"

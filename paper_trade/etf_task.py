from login.fyers_login.login import Login
from database.action import find_all, Collection

login = Login()


# Buy on every 2% fall and book profit on 3%
def check_etf_status():
    # fyers etf
    etf_list = []
    for item in find_all(Collection.ETF_COLL, {"broker": "fyers"}):
        etf_list.append(item["name"])
    etf = ",".join(etf_list)
    fyers = login.get()
    data = {
        "symbols": etf
    }
    response = fyers.quotes(data=data)
    print(response)

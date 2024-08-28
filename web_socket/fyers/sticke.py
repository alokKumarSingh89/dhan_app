from brokers.fyers.login import Login

index_list = {
    "NIFTY50": "NSE:NIFTY50-INDEX",
    "BankNifty": "NSE:NIFTYBANK-INDEX"
}

login = Login()


def getLTP(script):
    data = {
        "symbols": script
    }

    response = login.get().quotes(data=data)
    return response["d"][0]["v"]["lp"]


def stick(strategy):
    script = strategy.get("script")
    legs = strategy.get("legs")
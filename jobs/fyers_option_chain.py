import time
from database.db import db
import pandas as pd  
from fyers_apiv3 import fyersModel
import cred as cred
from fyers_api.token import Token
from datetime import datetime

token = Token();
fyers = fyersModel.FyersModel(client_id=cred.fyers["client_id"], token=token.get_token(),is_async=False, log_path="")
def fetch_option(symbol):
    data = {
        "symbol":symbol,
        "strikecount":10,
        "timestamp": ""
    }
    current_date = pd.Timestamp.now()
    response = fyers.optionchain(data=data);
    db["pull_data"].insert_one({"time": current_date.strftime("%d-%m-%Y %H:%M"), "data":response["data"]})
    print(f"Done for {symbol}")

def pull_option_chain(curr_time):
    symbolList = [script["symbol"] for script in db.scripts.find({})];
    for symbol in symbolList:
        fetch_option(symbol);
    

def processdata(data):
    if "expiryData" in data:
        del data["expiryData"]
    if "indiavixData" in data:
        del data["indiavixData"]
    return data;

def process_option_data():
    data = [item for item in db.pull_data.find({})]
    if len(data) <= 0:
        raise Exception("Don't have data to procces")
    df = pd.DataFrame(data)
    df["data"] = df["data"].apply(processdata);
    parse_dict = {
        "symbol":[],
        "volume":[],
        "strike_price":[],
        "date":[],
        "totalcallOi":[],
        "totalputOi":[],
        "ltp":[],
        "io":[],
        "oich":[],
        "option_type":[],
        "scripts":[]
    }

    def spread(row):
        data = [s for s in row["data"]["optionsChain"] if s["strike_price"] != -1]
        symbol = [s for s in row["data"]["optionsChain"] if s["strike_price"] == -1]
        ex_symbol = symbol[0]["ex_symbol"]
        for item in data:
            parse_dict["totalcallOi"].append(row["data"]["callOi"]);
            parse_dict["totalputOi"].append(row["data"]["putOi"])
            parse_dict["date"].append(row["time"])
            parse_dict["ltp"].append(item["ltp"])
            parse_dict["io"].append(item["oi"])
            parse_dict["oich"].append(item["oich"])
            parse_dict["option_type"].append(item["option_type"])
            parse_dict["strike_price"].append(item["strike_price"])
            parse_dict["symbol"].append(item["symbol"])
            parse_dict["volume"].append(item["volume"])
            parse_dict["scripts"].append(ex_symbol)

    df.apply(spread, axis=1)
    parse_df = pd.DataFrame(parse_dict)
    records = parse_df.to_dict('records')
    month = datetime.now().month
    year = datetime.now().year
    db[f'{month}-{year}'].insert_many(records);
    db["pull_data"].drop()

from fastapi import APIRouter

from brokers.fyers.model import OptionModal, Strategy_type
from database.db import db
import requests
from model import Broker


fyers = APIRouter(
    prefix='/fyers',
    tags=['Fyers Trading API']
)


@fyers.get("")
def fyers_health_check():
    return {"status": "running"}

@fyers.get("/place_order")
def get_script_list():
    return "Hello"

def get_ltp(script):
    res = requests.get("http://localhost:8888/script/" + script)
    print(res.json())

@fyers.post("/option_details")
def get_option_details(data: OptionModal):
    response = {}
    script_config = db["script_config"].find_one({"symbol":data.script})
    get_ltp(data.script)

    response["lots"] = script_config["lots"]
    # atm = fyers_data["d"][0]["v"]["lp"]
    # atm = int(round((atm / script_config["stick_diff"]),0) * script_config["stick_diff"])
    # if Strategy_type.Bearish == data.strategy_name:
    #     response["hedge"] = f"NSE:{script_config['script']}{data.expiry}{atm+(script_config['stick_diff']*data.hedge_strick)}CE"
    #     response["sell"] = f"NSE:{script_config['script']}{data.expiry}{atm+(script_config['stick_diff']*data.sell_strick)}CE"
    # else:
    #     response["hedge"] = f"NSE:{script_config['script']}{data.expiry}{atm-(script_config['stick_diff']*data.hedge_strick)}PE"
    #     response["sell"] = f"NSE:{script_config['script']}{data.expiry}{atm-(script_config['stick_diff']*data.sell_strick)}PE"

    return response


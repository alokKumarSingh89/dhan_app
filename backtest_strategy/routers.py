from fastapi import APIRouter, HTTPException, BackgroundTasks
import json
from fastapi.encoders import jsonable_encoder
from starlette import status
from bson import json_util, ObjectId
import pandas as pd
from model import Broker

from database.action import find_one, add_one, Collection, find_all, add_many
from backtest_strategy.model import StrategyModel
from brokers.fyers.tasks import run_engine
from backtest_strategy.order import place_order as place_order_s

strategy: APIRouter = APIRouter(
    prefix='/stratergy',
    tags=['Strategy']
)


@strategy.get("/")
def all_strategy():
    script = find_all(Collection.Strategy)
    script = json.loads(json_util.dumps(script))
    return script


@strategy.get("/deploy")
def all_strategy():
    script = find_all(Collection.DeployedStrategy)
    script = json.loads(json_util.dumps(script))
    return script


@strategy.post("/")
def create_new_strategy(items: StrategyModel):
    body = jsonable_encoder(items)
    script_data = find_one(Collection.Strategy,{"name": body.get("name")})
    if script_data is None:
        add_one(Collection.Strategy, body)
        return "Success"
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{body.get('name')} already exits in db")


@strategy.post("/deploy/{strategy_id}")
def create_new_strategy(strategy_id: str, body:dict):
    strategy = find_one(Collection.Strategy,{"_id": ObjectId(strategy_id)})
    dep_stra = find_one(Collection.DeployedStrategy,{"name": strategy["name"],"symbol": body["symbol"],"expiry":body["expiry"]})
    if dep_stra is None:
        del strategy["_id"]
        add_one(Collection.DeployedStrategy, {**strategy, **body})
        return "backtest_strategy"
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{strategy.get('name')} already deployed in db")


@strategy.get("/place_order/{deployed_id}")
def place_order(deployed_id: str, background_task: BackgroundTasks):
    strategy = find_one(Collection.DeployedStrategy, {"_id": ObjectId(deployed_id)})
    running_stra = find_one(Collection.RunningQueue, {"name":strategy["name"],"symbol":strategy["symbol"], "expiry":strategy["expiry"]})
    if running_stra is None:
        place_order_s(strategy)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Already running")


@strategy.get("/running-backtest_strategy")
def running_stragegy():
    running_stra = find_all(Collection.RunningQueue)
    running_stra = json.loads(json_util.dumps(running_stra))
    return running_stra



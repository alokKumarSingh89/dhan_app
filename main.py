import json

from bson import json_util
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from starlette import status

# Router import , broker wise
from brokers.fyers.routers import fyers
from backtest_strategy.routers import strategy
from paper_trade.mis import process
from scripts.routers import script
from paper_trade.router import paper_trade

from database.action import add_one, Collection, find_one, find_all
from model import BrokerRequest

from config.config import get_strategy_list, get_script_list
from worker.celery_app import celery_app

origins = [
    "http://localhost:3000",
]

app = FastAPI(title="Trading App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fyers)
app.include_router(strategy)
app.include_router(script)
app.include_router(paper_trade)


@app.get("/")
def alph_test():
    return {"Name": "Alok"}


@app.post("/add_broker")
def add_broker(body: BrokerRequest):
    body = jsonable_encoder(body)
    broker = find_one(Collection.Broker, {"name": body["name"]})
    if broker is None:
        return add_one(Collection.Broker, body)
    else:
        raise HTTPException(detail="Broker Already added, Please esit the detail",
                            status_code=status.HTTP_403_FORBIDDEN)


@app.put("/add_broker/{broker_id}")
def add_broker(broker_id: str):
    return broker_id


@app.get("/broker-list")
def broker_list():
    script = find_all(Collection.Broker)
    script = json.loads(json_util.dumps(script))
    return script


@app.get("/start_all_intraday_strategy")
def start_all_intraday_strategy():
    task_name = "worker.celery_worker.mis_paper"
    for config in get_strategy_list():
        if config["disable"] == False:
            process(config)
            # task = celery_app.send_task(task_name, args=[config, ])
            # print(task)
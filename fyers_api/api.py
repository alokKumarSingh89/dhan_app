from fastapi import APIRouter, Path, HTTPException, BackgroundTasks
from datetime import date
import cred
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from starlette import status
import json
from bson import json_util

from database.db import db
from .validation_model import request_model
from .run_for_strategy import run
from jobs.fyers_option_chain import pull_option_chain, process_option_data
from .schedule import startOptionJob

router = APIRouter(
    prefix='/fyers-trade',
    tags=['Fyers Trading API']
)

collection = {
    "scripts": "scripts",
    "backtest_strategy": "backtest_strategy"
}


@router.post("/script", status_code=200)
def config_script(script: request_model.ScriptModel):
    script_data = db[collection["scripts"]].find_one({"name": script.name})
    if script_data is None:
        db[collection["scripts"]].insert_one(jsonable_encoder(script))
        return "Success"
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{script.name} already exits in db")


@router.get("/script")
def all_scripts():
    script = [report for report in db[collection["scripts"]].find({})]
    script = json.loads(json_util.dumps(script))
    return script


@router.get("/get_option_chain")
def fetch_and_save_option_chain(backhround_task: BackgroundTasks):
    backhround_task.add_task(startOptionJob)
    return "Running"


@router.get("/create_option_data")
def create_option_data(backhround_task: BackgroundTasks):
    backhround_task.add_task(process_option_data)
    return "Running"

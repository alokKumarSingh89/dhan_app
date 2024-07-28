from fastapi import APIRouter, Path, HTTPException
import json
from fastapi.encoders import jsonable_encoder
from starlette import status
from bson import json_util

from database.db import db

from strategy.model import StrategyModel

strategy: APIRouter = APIRouter(
    prefix='/stratergy',
    tags=['Strategy']
)


@strategy.get("/")
def all_strategy():
    script = [report for report in db["strategy"].find({})]
    script = json.loads(json_util.dumps(script))
    return script


@strategy.post("/")
def create_new_strategy(items: StrategyModel):
    script_data = db["strategy"].find_one({"name": items.name})
    if script_data is None:
        db["strategy"].insert_one(jsonable_encoder(items))
        return "Success"
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{items.name} already exits in db")

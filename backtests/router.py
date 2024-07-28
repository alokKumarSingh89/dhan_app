from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder

from backtests.model import BackTestRequest
from backtests.task import execute_strategy

backtest = APIRouter(
    prefix='/backtest',
    tags=['Backtest']
)


@backtest.post("/")
def backtest_strategy(item: BackTestRequest):
    execute_strategy(jsonable_encoder(item))

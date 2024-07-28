from fastapi import APIRouter, BackgroundTasks

from .task import run_all_availble
from .etf_task import check_etf_status

paper_trade = APIRouter(
    prefix='/paper',
    tags=['Paper Trade']
)


@paper_trade.get("/")
def start_engine(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_all_availble)
    return "success"


@paper_trade.get("/etf")
def check_etf(background_tasks: BackgroundTasks):
    background_tasks.add_task(check_etf_status)

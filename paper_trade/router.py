from fastapi import APIRouter, BackgroundTasks
import pandas as pd
from starlette.concurrency import run_in_threadpool
import threading
from .task import run_all_availble
from .etf_task import check_etf_status
from .ema9_ha import ema9_ha
running_script_task = []
from worker.celery_app import celery_app

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


# def start_9_ema():
#     task_name = "worker.celery_worker.ema_9"
#     print(task_name)
#     for script in ema_9_script:
#         if script not in running_script_task:
#             task = celery_app.send_task(task_name, args=[script,])
#             print(task)
#             running_script_task.append(script)
#         else:
#             print(f"{script} already running")

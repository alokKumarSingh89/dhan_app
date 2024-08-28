from fastapi import FastAPI, HTTPException, BackgroundTasks
import pandas as pd

from config.config import get_script_list
from web_socket.script_worker import subscribe, disconnect, time_frame_data

app = FastAPI(title="Trading App")


@app.get("/")
def socket_health():
    return {"Name": "Socket Running"}


@app.get("/start-broker")
def start_broker_to_subcribe_script(background_task: BackgroundTasks):
    disconnect()
    scripts = get_script_list()
    background_task.add_task(subscribe, scripts)
    return "success"


@app.get("/script/{script_name}")
def get_lpt_detail(script_name: str):
    print(time_frame_data.get(script_name), time_frame_data)
    return time_frame_data.get(script_name) or -1

from fastapi import APIRouter
import requests
from model import Broker

fyers = APIRouter(
    prefix='/fyers',
    tags=['Fyers Trading API']
)


@fyers.get("")
def fyers_health_check():
    return {"status": "running"}


@fyers.get("/start")
def start_broker():
    requests.get("http://localhost:8888/start-broker/"+Broker.FYERS.value)
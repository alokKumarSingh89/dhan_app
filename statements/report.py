from fastapi import APIRouter, Path, HTTPException
from typing import Annotated, Any
import datetime as dt
from starlette import status
from pydantic import BaseModel
from bson import json_util
import json

from lib.dhan import DhanClass
from database.db import db

statements_collection = db.statements
process_date = db.processed_date


class StatementReport(BaseModel):  # use to omit id
    dhanClientId: str
    orderId: str
    exchangeOrderId: str
    exchangeTradeId: str
    transactionType: str
    exchangeSegment: str
    productType: str
    orderType: str
    customSymbol: str
    securityId: str
    tradedQuantity: int
    tradedPrice: float
    sebiTax: float
    stt: float
    brokerageCharges: float
    serviceTax: float
    exchangeTransactionCharges: float
    stampDuty: float
    exchangeTime: str
    drvOptionType: str
    status: int
    process_date: str


router = APIRouter(
    prefix='/reports',
    tags=['Reports']
)


@router.get('/statement/{date}')
def get_statement_by_date(date: Annotated[dt.date, Path(default_factory=dt.date)]) -> Any:
    report = [report for report in statements_collection.find({"process_date": str(date)})]
    report = json.loads(json_util.dumps(report))
    return report


@router.post('/statement/{date}')
def get_statement_by_date(date: Annotated[dt.date, Path(default_factory=dt.date)]) -> Any:
    is_processed = process_date.find_one({"date": str(date)})
    if is_processed is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Date Already proccess")
    dhan = DhanClass()
    report = dhan.getStatements(date, date)
    if len(report) == 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Don't have report for this date")
    report = [{**item, "status": 0, "process_date": str(date)} for item in report]
    process_date.insert_one({"date": str(date)})
    statements_collection.insert_many(report)
    return {"status": "Successfull"}

from pydantic import BaseModel, Field
from typing import List
from enum import Enum


class TransactionType(Enum):
    BUY = "Buy"
    SELL = "Sell"


class OptionType(Enum):
    CE = "CE"
    PE = "PE"


class OrderType(Enum):
    MIS = "MIS"
    CNC = "CNC"


class ProfitType(Enum):
    POINT = "POINT"
    PERCENTAGE = "PERCENTAGE"


class Legs(BaseModel):
    sticke: int = Field(description="Option Stick", default=0)
    transaction_type: TransactionType = Field(description="Buy/Cell", default=TransactionType.SELL)
    option_type: OptionType = Field(description="Ce/Pe", default=OptionType.CE)
    sl_type: ProfitType = Field(description="Provide sl type", default=ProfitType.POINT)
    sl: int = Field(description="Provide SL", default=0)
    target_type: ProfitType = Field(description="Provide Target type", default=ProfitType.POINT)
    target: int = Field(description="Provide Target", default=0)


class StrategyModel(BaseModel):
    name: str = Field(default="Bull", description="Strategy Name")
    legs: List[Legs]
    script: str = Field(default="NSE:SBIN-EQ")
    order_type: OrderType = Field(default=OrderType.MIS, description="Select Intraday/Potional")
    sl_type: ProfitType = Field(description="Provide sl type", default=ProfitType.POINT)
    sl: int = Field(description="Provide SL", default=0)
    target_type: ProfitType = Field(description="Provide Target type", default=ProfitType.POINT)
    target: int = Field(description="Provide Target", default=0)

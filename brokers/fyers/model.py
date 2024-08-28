from pydantic import BaseModel, Field
from enum import Enum

class Strategy_type(Enum):
    Bullish = "Bull Put"
    Bearish = "Bear Call"

class OptionModal(BaseModel):
    hedge_strick: int = Field(default=1)
    script: str = Field()
    sell_strick: int = Field(lt=0, default=-3)
    strategy_name:Strategy_type = Field(default=Strategy_type.Bullish)
    expiry: str = Field()
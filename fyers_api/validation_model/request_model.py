from pydantic import BaseModel, Field

class ScriptModel(BaseModel):
    name: str = Field(default="Nifty", description="Script Name")
    symbol:str = Field(default="Nifty50", description="Script Symbol")
    lot_size: int = Field(default=25,gt=0, description="Lot size of script")
    expiry_day: str = Field(default="Thr", description="Day of expiry")
    stick_diff:int = Field(default=50,gt=0, description="Strick Difference")

class StrategyModel(BaseModel):
    name:str = Field(default="Bull", description="Strategy Name")
    sell_leg_strick: int = Field(description="Sell Strategy Leg from atm", default=-3, lt=1) 
    hedge_leg_strick: int = Field(description="Margin Benefit ", default=4, gt=2) 
    buy_leg:int = Field(description="Buy Leg ", default=4, gt=2) 
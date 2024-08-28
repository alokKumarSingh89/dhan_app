from pydantic import BaseModel, Field
from enum import Enum


class Broker(Enum):
    FYERS = "fyers"
    DHAN = "dhan"


class BrokerRequest(BaseModel):
    name: Broker = Field(description="Broker Name", default=Broker.FYERS)
    credential: dict = Field(description="Provide", default={})
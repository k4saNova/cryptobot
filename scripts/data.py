from dataclasses import dataclass
from enum import Enum, auto

class Side(Enum):
    BUY = 1
    SELL = -1

     
class ExecutionType(Enum):
    MARKET = auto()
    LIMIT = auto()
    STOP = auto()
    TRIAL = auto()
     

class Exchange(Enum):
    GMO = auto()
    bitFlyer = auto()
    Simu = auto()

    
@dataclass
class Order:
    symbol: str
    side: Side
    size: float
    execution_type: ExecutionType
    price: float = 0. # price of symbol's coin
    time_in_force: str = ""
    losscut_price: str = ""
    cancel_before: bool = ""


@dataclass
class Ticker:
    ask: float
    bid: float
    last: float
    volume: float
    timestamp: str

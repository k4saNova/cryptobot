from dataclasses import dataclass

@dataclass
class Order:
     symbol: str # e.g. "BTC"
     side: int # -1: sell, 1: buy
     size: float
     execution_type: str # "MARKET", "LIMIT"
     price: float = 0. # price of symbol's coin
     time_in_force: str = ""
     losscut_price: str = ""
     cancel_before: bool = ""


@dataclass
class Ticker:
    last: float
    volume: float


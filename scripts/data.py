from dataclasses import dataclass
from enum import Enum, auto
from numbers import Real


class Side(Enum):
    BUY  = 1
    SELL = -1


class ExecutionType(Enum):
    MARKET = auto()
    LIMIT  = auto()
    STOP   = auto()
    TRIAL  = auto()


class Exchange(Enum):
    GMO      = auto()
    bitFlyer = auto()
    Simu     = auto()


class Price(object):
    step_values = {}
    def __init__(self, symbol=None, x=None):
        if symbol is None and x is None:
            self.value = None
            return None

        if symbol not in Price.step_values:
            raise KeyError(f"specify step value of {symbol}")

        actual_value = float(x)
        step = Price.step_values[symbol]
        is_int_step = "." not in step
        if is_int_step:
            precision = 0
            step = int(step)
        else:
            precision = len(step.split(".")[1])
            step = float(step)

        if is_int_step:
            v = int((actual_value // step) * step)
            self.value = str(v)
        else:
            v = str((actual_value // step) * step)
            a, b = v.split(".")
            self.value = f"{a}.{b[:self.precision]}"

    def __repr__(self):
        return f"<Price: {self.value}>"


class Size(object):
    min_lot = {}
    max_lot = {}
    round_level = 8
    def __init__(self):
        pass


@dataclass
class Order:
    symbol: str
    side: Side
    size: float
    execution_type: ExecutionType
    price: Price = Price()
    time_in_force: str = ""
    losscut_price: str = ""
    cancel_before: bool = ""

    def __post_init__(self):
        # Type Check
        if type(self.side) is not Side:
            raise TypeError(f"{type(order.side)}: use Side")

        if type(self.execution_type) is not ExecutionType:
            raise TypeError(f"{type(order.execution_type)}: use ExecutionType")

        if type(self.price) is not Price:
            raise TypeError(f"{type(order.price)}: use Price")


@dataclass
class Ticker:
    ask: float
    bid: float
    last: float
    volume: float
    timestamp: str

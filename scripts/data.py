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


class Exchange(Enum):
    """supported exchanges
    """
    GMO      = auto()
    bitFlyer = auto()


class OrderStatus(Enum):
    UNORDERED = auto()
    ## 未注文時の状態

    ACTIVE    = auto()
    ## 注文が有効な状態（一部約定）
    ## GMOのORDERED, WAITINGに対応
    ## bitFlyerのACTIVEに対応

    COMPLETED = auto()
    ## 約定済み
    ## GMOのEXECUTEDに対応
    ## bitFlyerのCOMPLETEDに対応

    CANCELED  = auto()
    ## キャンセル済み
    ## GMOのCANCELEDに対応
    ## bitFlyerのCANCELEDに対応

    MODIFYING = auto()
    ## 注文の変更中
    ## GMOのCANCELING, MODIFYINGに対応
    ## bitFlyerには対応する状態なし

    EXPIRED   = auto()
    ## 失効済み
    ## GMOのEXPIREDに対応
    ## bitFlyerのEXPIRED, REJECTEDに対応


class Price(object):
    step_values = {}
    def __init__(self, symbol, x):
        if symbol not in Price.step_values:
            raise KeyError(f"specify step value of {symbol}")

        actual_value = float(x)
        step = Price.step_values[symbol]
        if "." not in step:
            step = int(step)
            v = int((actual_value // step) * step)
            self.actual_value = actual_value
            self.value = str(v)
        else:
            precision = len(step.split(".")[1])
            step = float(step)
            v = str((actual_value // step) * step)
            a, b = v.split(".")
            self.actual_value = actual_value
            self.value = f"{a}.{b[:self.precision]}"


    def __repr__(self):
        return f"Price(value={self.value})"


class Size(object):
    min_sizes = {}
    max_sizes = {}
    round_level = 8
    def __init__(self, symbol, val=None, lot=None):
        if (val is None and lot is None) or\
           (val is not None and lot is not None):
            raise ValueError("specify either of x or lot")

        if symbol not in Size.min_sizes:
            raise KeyError(f"specify the minimum size of {symbol}")

        if symbol not in Size.max_sizes:
            raise KeyError(f"specify the maximum size of {symbol}")

        mins = Size.min_sizes[symbol]
        maxs = Size.max_sizes[symbol]
        if lot is None:
            # val is given
            self.lot = int(val // mins)
        if val is None:
            # lot is given
            self.lot = lot
        self.actual_value = round(min(self.lot * mins, maxs),
                                  Size.round_level)
        self.value = str(self.actual_value)


    def __repr__(self):
        return f"Size(lot={self.lot}, value={self.value})"



@dataclass
class Asset:
    amount: float
    available: float

    def __post_init__(self):
        self.amount = float(self.amount)
        self.available = float(self.available)


@dataclass
class Order:
    symbol: str
    side: Side
    size: Size
    execution_type: ExecutionType
    price: Price
    time_in_force: str = ""
    losscut_price: str = ""
    cancel_before: bool = ""
    status: OrderStatus = OrderStatus.UNORDERED
    ID: str = -1
    timestamp: str = ""

    def __post_init__(self):
        # Type Check
        if type(self.side) is not Side:
            raise TypeError(f"{type(self.side)}: use Side")

        if type(self.size) is not Size:
            raise TypeError(f"{type(self.size)}: use Size")

        if type(self.execution_type) is not ExecutionType:
            raise TypeError(f"{type(self.execution_type)}: use ExecutionType")

        if type(self.price) is not Price:
            raise TypeError(f"{type(self.price)}: use Price")


@dataclass
class Ticker:
    ask: float
    bid: float
    last: float
    volume: float
    timestamp: str

    def __post_init__(self):
        self.ask = float(self.ask)
        self.bid = float(self.bid)
        self.last = float(self.last)
        self.volume = float(self.volume)

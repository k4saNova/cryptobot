import json
import hmac
import hashlib
import time
from datetime import datetime

from abc import ABCMeta, abstractmethod
from .utils import *
from .data import *


class Api(metaclass=ABCMeta):
    # exchange name
    exchange = None

    @abstractmethod
    def __init__(self, api_key, secret_key):
        raise NotImplementedError()


    @abstractmethod
    def is_available(self):
        """returns True if the market is available
        """
        raise NotImplementedError()


    @abstractmethod
    def get_ticker(self):
        """returns ticker
        """
        raise NotImplementedError()


    @abstractmethod
    def get_orderbooks(self):
        """ returns orderbooks
        """
        raise NotImplementedError()


    @abstractmethod
    def get_assets(self):
        """returns assets
        """
        raise NotImplementedError()


    @abstractmethod
    def post_order(self):
        """posts the order and returns a responce
        Args:
            order: Order object (see data.py)
        """
        raise NotImplementedError()



class SimulationApi(Api):
    exchange = Exchange.Simu.name

    def __init__(self):
        pass

    def is_available(self):
        return True

    def get_ticker(self, t):
        pass

    def get_orderbooks(self):
        pass

    def post_order(self, order):
        pass



class GmoApi(Api):
    exchange = Exchange.GMO.name

    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.public_endpoint = "https://api.coin.z.com/public"
        self.ws_public_endpoint = "wss://api.coin.z.com/ws/public"
        self.private_endpoint = "https://api.coin.z.com/private"
        self.ws_private_endpoint = "wss://api.coin.z.com/ws/private"


    def get_api_header(self, method, path, payload={}):
        """return the api header for GMO private api
        Args:
            method: http method 'GET', 'POST'
            path: path to endpoint
            payload: responce body, dict
        """
        timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        text = timestamp + method + path
        if payload:
            text += json.dumps(payload)

        sign = hmac.new(bytes(self.secret_key.encode('ascii')),
                        bytes(text.encode('ascii')),
                        hashlib.sha256)\
                   .hexdigest()
        return {
            "API-KEY": self.api_key,
            "API-TIMESTAMP": timestamp,
            "API-SIGN": sign
        }


    def is_available(self):
        path = "/v1/status"
        resp = http_get(self.public_endpoint + path)
        if resp["data"]["status"] == "OPEN":
            return True
        else:
            return False


    def get_ticker(self, symbols):
        path = "/v1/ticker"
        resp = http_get(self.public_endpoint + path)

        ticker = {}
        for data in resp["data"]:
            s = data["symbol"]
            if s not in symbols:
                continue

            ticker[s] = Ticker(
                ask = float(data["ask"]),
                bid = float(data["bid"]),
                last = float(data["last"]),
                volume = float(data["volume"]),
                timestamp = data["timestamp"]
            )
        return ticker


    def get_orderbooks(self, symbol):
        path = "/v1/orderbooks"
        resp = http_get(self.public_endpoint + path,
                        params={"symbol": symbol})
        data = resp["data"]
        sort_with_price = lambda x: float(x["price"])
        data["asks"].sort(key=sort_with_price)
        data["bids"].sort(key=sort_with_price, reverse=True)
        return data


    def get_assets(self, symbols):
        path = "/v1/account/assets"
        resp = http_get(self.private_endpoint + path,
                        headers=self.get_api_header("GET", path))

        assets = {}
        for data in resp["data"]:
            if data["symbol"] in symbols:
                assets[data["symbol"]] = {
                    key: float(data[key])
                    for key in ["amount", "available", "conversionRate"]
                }
        return assets


    def post_order(self, order):
        payload = {}

        # required fields
        payload["symbol"] = order.symbol

        if type(order.side) is Side:
            payload["side"] = order.side.name
        else:
            raise TypeError(f"{type(order.side)}: use Side")

        payload["size"] = str(order.size)

        if type(order.execution_type) is ExecutionType:
            payload["executionType"] = order.execution_type.name
        else:
            raise TypeError(f"{type(order.execution_type)}: use ExecutionType")

        if order.execution_type is not ExecutionType.MARKET:
            if order.price:
                payload["price"] = str(order.price)
            else:
                raise ValueError("Specify price")

        # optional fields
        if order.time_in_force:
            payload["timeInForce"] = order.time_in_force
        if order.losscut_price:
            payload["losscutPrice"] = order.losscut_price
        if order.cancel_before:
            payload["cancelBefore"] = order.cancel_before


        # post order
        path = "/v1/order"
        resp = http_post(self.private_endpoint + path,
                         headers=self.get_api_header("POST", path, payload),
                         payload=payload)
        return resp



class BitFlyerApi(Api):
    exchange = Exchange.bitFlyer.name

    def __init__(self, api_key, secret_key):
        raise NotImplementedError()

    def is_available(self):
        raise NotImplementedError()

    def get_assets(self):
        raise NotImplementedError()

    def get_ticker(self):
        raise NotImplementedError()

    def post_order(self):
        raise NotImplementedError()


def get_crypto_api_client(name, api_key, secret_key):
    if name == Exchange.GMO.name:
        return GmoApi(api_key, secret_key)
    elif name == Exchange.bitFlyer.name:
        return BitFlyerApi(api_key, secret_key)
    elif name == Exchange.Simu.name:
        return SimulationApi()
    else:
        raise ValueError(f"invalid name: {name}")

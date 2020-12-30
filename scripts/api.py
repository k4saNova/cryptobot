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
        """returns True if the exchange opens
        """
        raise NotImplementedError()


    @abstractmethod
    def get_ticker(self):
        """returns ticker
        """
        raise NotImplementedError()


    @abstractmethod
    def get_execution_history(self):
        """returns trade history
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
    def get_orders(self, order_ids):
        """gets order information of order_ids
        """
        raise NotImplementedError()


    @abstractmethod
    def post_order(self, order):
        """posts an order and returns the order id
        Args:
            order: Order object (see data.py)
        """
        raise NotImplementedError()


    @abstractmethod
    def post_cancel_orders(self, order_ids):
        """cancel specified orders
        """
        raise NotImplementedError()


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


    def validate_response(self, resp):
        """returns resp['data'] if resp['status'] == 0
        """
        if resp["status"] == 0:
            # success
            return resp["data"]
        else:
            raise RuntimeError(resp["messages"])


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


    def get_execution_history(self, symbol, page=1, count=100):
        path = "/v1/trades"
        params = {
            "symbol": symbol,
            "page": page,
            "count": count = min(count, 100)
        }
        resp = http_get(self.public_endpoint + path,
                        params = params)
        data = self.validate_response(resp)
        return data["list"]

        

    def get_orderbooks(self, symbol):
        path = "/v1/orderbooks"
        resp = http_get(self.public_endpoint + path,
                        params={"symbol": symbol})
        data = self.validate_response(resp)
        sort_with_price = lambda x: float(x["price"])
        data["asks"].sort(key=sort_with_price)
        data["bids"].sort(key=sort_with_price, reverse=True)
        return data


    def get_assets(self, symbols):
        path = "/v1/account/assets"
        resp = http_get(self.private_endpoint + path,
                        headers=self.get_api_header("GET", path))
        data = self.validate_response(resp)

        assets = {}
        for d in data:
            if d["symbol"] not in symbols:
                continue

            assets[d["symbol"]] = Asset(
                amount = d["amount"],
                available = d["available"]
            )
        return assets


    def get_orders(self, orders):
        order_ids = []
        if type(orders) is list:
            for order in orders:
                order_ids.append(order.ID)

        elif type(orders) is Order:
            # single order
            order_ids.append(orders.ID)
            orders = [orders]

        else:
            raise TypeError(f"{type(orders)}: use Order or list of Order")
        order_ids.sort(key=lambda x: int(x))

        path = "/v1/orders"
        params = {"orderId": ",".join(order_ids)}
        resp = http_get(self.private_endpoint + path,
                        params=params,
                        headers=self.get_api_header("GET", path))
        data = self.validate_response(resp)
        data["list"].sort(key=lambda x: x["orderId"])

        for order, d in zip(orders, data["list"]):
            order.timestamp = d["timestamp"]
            if d["status"] in ["WAITING", "ORDERED"]:
                order.status = OrderStatus.ACTIVE
            elif d["status"] == "EXECUTED":
                order.status = OrderStatus.COMPLETED
            elif d["status"] == "CANCELED":
                order.status = OrderStatus.CANCELED
            elif d["status"] in ["CANCELING", "MODIFYING"]:
                order.status = OrderStatus.MODIFYING
            elif d["status"] == "EXPIRED":
                order.status = OrderStatus.EXPIRED
            else:
                raise RuntimeError(f"undefined status {d['status']}")
        return orders



    def post_order(self, order):
        if type(order) is not Order:
            raise TypeError(f"{type(order)}: use Order")

        payload = {}

        # required fields
        payload["symbol"] = order.symbol
        payload["side"] = order.side.name
        payload["size"] = order.size.value
        payload["executionType"] = order.execution_type.name
        if order.execution_type is not ExecutionType.MARKET:
            payload["price"] = order.price.value

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
        order_id = self.validate_response(resp)
        return order_id


    def post_cancel_orders(self, orders):
        order_ids = []
        if type(orders) is list:
            for order in orders:
                order_ids.append(order.ID)

        elif type(orders) is Order:
            # single order
            order_ids.append(orders.ID)
            orders = [orders]

        else:
            raise TypeError(f"{type(orders)}: use Order or list of Order")
        order_ids.sort(key=lambda x: int(x))

        path = "/v1/cancelOrders"
        payload = {
            "orderIds": order_ids
        }
        resp = http_post(self.private_endpoint + path,
                         headers=self.get_api_header("POST", path, payload),
                         payload=payload)
        data = self.validate_response(resp)
        return data


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

    def post_cancel_orders(self):
        raise NotImplementedError()



def get_crypto_api_client(name, api_key, secret_key):
    if name == Exchange.GMO.name:
        return GmoApi(api_key, secret_key)
    elif name == Exchange.bitFlyer.name:
        return BitFlyerApi(api_key, secret_key)
    else:
        raise ValueError(f"invalid name: {name}")

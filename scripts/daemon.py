from math import log2, ceil, floor
from time import sleep
from pprint import pprint

from .data import *

class ShannonsDaemon(object):
    """auto-trading bot based on Shannon's Demon.
    """
    def __init__(self, api, symbols,
                 min_lot, max_lot,
                 delay=15, jpy_symbol="JPY"):
        self.api = api
        self.min_lot = min_lot
        self.max_lot = max_lot
        self.delay = delay
        self.JPY = jpy_symbol
        self.round_level = 8

        self.symbols = symbols
        if self.JPY not in symbols:
            self.symbols.append(self.JPY)
        if self.JPY not in min_lot:
            self.min_lot[self.JPY] = 1.


    def estimate_assets(self, assets, ticker):
        """returns total assets and each value with given ticker
        """
        real_time_assets = {
            symbol: assets[symbol]["amount"] * ticker[symbol]["last"]
            for symbol in self.symbols
        }
        total_assets = sum(real_time_assets.values())
        return real_time_assets, total_assets


    def rebalance(self, assets, ticker):
        values, total = self.estimate_assets(assets, ticker)
        balance_val = total / len(values)
        new_assets = {}
        for symbol in sorted(self.symbols,
                             key=lambda s: values[s]/balance_val,
                             reverse=True):
            r = values[symbol] / balance_val
            amount = assets[symbol]["amount"]
            rate = ticker[symbol]["last"]
            n = abs(amount - balance_val/rate)
            if r >= 1:
                side = -1
                size = ceil(n / self.min_lot[symbol]) * self.min_lot[symbol]
            else:
                side = 1
                size = floor(n / self.min_lot[symbol]) * self.min_lot[symbol]
            size = round(min(size, self.max_lot[symbol]), self.round_level)

            new_assets[symbol] = {
                "side": side,
                "amount": round(amount + side * size, self.round_level),
                "size": size,
                "est_price": size * ticker[symbol]["last"]
            }

        return new_assets


    def entropy(self, assets, ticker):
        """return entropy with value
        Arg:
            asset: dict, market values
        """
        values, total = self.estimate_assets(assets, ticker)
        ratios = [v/total for v in values.values()]
        return sum(-r*log2(r) for r in ratios)



    def order(self, new_assets):
        success = True
        # make the order
        resp = {}
        for symbol, v in new_assets.items():
            if symbol == self.JPY:
                continue

            if v["size"] < self.min_lot[symbol]:
                continue
            
            # fetch limit price
            side = v["side"]
            orderbooks = self.api.get_orderbooks(symbol)
            if side == 1:
                price = orderbooks["bids"][0]["price"]
            elif side == -1:
                price = orderbooks["asks"][0]["price"]
            else:
                print(f"invalid side: {side}")
                continue
            #
            order = Order(
                symbol = symbol,
                side = side,
                size = v["size"],
                execution_type = "LIMIT",
                price = price,
                time_in_force = "SOK"
            )
            resp[symbol] = self.api.post_order(order)
            sleep(0.4)
        return resp


    def run(self):
        if not self.api.is_available():
            raise ValueError("Exchange is not available now")

        ticker = self.api.get_ticker(self.symbols)
        assets = self.api.get_assets(self.symbols)

        if self.JPY not in ticker:
            ticker[self.JPY] = {}
            ticker[self.JPY]["last"] = 1.

        new_assets = self.rebalance(assets, ticker)
        pprint(new_assets)

        if self.entropy(new_assets, ticker) >\
           self.entropy(assets, ticker):
            print("POST ORDER")
            resp = self.order(new_assets)
            pprint(resp)
            

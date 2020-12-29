from math import log2, ceil, floor
from time import sleep
from pprint import pprint

from .data import *

class ShannonsDaemon(object):
    """auto-trading bot based on Shannon's Demon.
    """
    def __init__(self, api, symbols,
                 min_lot, max_lot, step_values,
                 delay=15, jpy_symbol="JPY"):
        """
        Args:
            api: api client (see api.py)
            symbols: list of coins' symbol
            min_lot: dict of minimum lot
            max_lot: dict of maximum lot
            step_value: step values of each coin
        """
        self.api = api
        self.min_lot = min_lot
        self.max_lot = max_lot
        self.delay = delay
        self.JPY = jpy_symbol
        self.round_level = 8

        Price.step_values = step_values
        self.symbols = symbols
        if self.JPY not in symbols:
            self.symbols.append(self.JPY)


    def rebalance(self, assets, ticker):
        """returns list of orders
        """
        # solve balanced price
        total = 0
        for symbol in self.symbols:
            if symbol == self.JPY:
                total += assets[symbol]["amount"]
            else: # crypto
                total += assets[symbol]["amount"] * ticker[symbol].last
        balanced_val = total / len(self.symbols)

        # make orders
        orders = []
        size = lambda s, n: round(min(n * self.min_lot[s], self.max_lot[s]), self.round_level)
        for symbol in self.symbols:
            if symbol == self.JPY:
                continue

            amount = assets[symbol]["amount"]
            rate = ticker[symbol].last
            if amount*rate / balanced_val < 1:
                side = Side.BUY
            else:
                side = Side.SELL
            nlot = ceil(abs(amount - balanced_val/rate) / self.min_lot[symbol])

            # decide number of lot using entropy
            ratio = lambda n: (amount + side.value*size(symbol, n)) / balanced_val
            r0, r1 = ratio(nlot), ratio(nlot-1)
            if -r0*log2(r0) < -r1*log2(r1):
                nlot = nlot - 1

            if nlot > 0:
                # decide price
                if side is Side.BUY:
                    p = ticker[symbol].bid
                else:
                    p = ticker[symbol].ask

                orders.append(
                    Order(
                        symbol = symbol,
                        side = side,
                        size = size(symbol, nlot),
                        execution_type = ExecutionType.LIMIT,
                        price = Price(symbol, p),
                        time_in_force = "SOK"
                    )
                )
        return orders


    def run(self):
        if not self.api.is_available():
            raise ValueError("Exchange is not available now")

        assets = self.api.get_assets(self.symbols)
        ticker = self.api.get_ticker(self.symbols)
        orders = self.rebalance(assets, ticker)

        # post orders
        for order in orders:
            # pprint(order)
            success, resp = self.api.post_order(order)
            pprint(resp)
            sleep(0.4)


    def run_forever(self):
        while True:
            try:
                self.run()
            except Exception as e:
                print(f"Error: {e}")
            finally:
                sleep(self.delay)

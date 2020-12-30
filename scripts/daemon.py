from math import log2, ceil, floor
from time import sleep
from pprint import pprint

from .data import *

class ShannonsDaemon(object):
    """auto-trading bot based on Shannon's Demon.
    """
    def __init__(self, api, symbols,
                 min_sizes, max_sizes, step_values,
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
        self.delay = delay
        self.symbols = symbols
        self.JPY = jpy_symbol
        if self.JPY not in symbols:
            self.symbols.append(self.JPY)
        self.posting_orders = []
        Size.min_sizes = min_sizes
        Size.max_sizes = max_sizes
        Price.step_values = step_values



    def rebalance(self, assets, ticker):
        """returns list of orders
        """
        # solve balanced price
        total = 0
        for symbol in self.symbols:
            if symbol == self.JPY:
                total += assets[symbol].amount
            else: # crypto
                total += assets[symbol].amount * ticker[symbol].last
        balanced_val = total / len(self.symbols)

        # make orders
        orders = []
        for symbol in self.symbols:
            if symbol == self.JPY:
                continue

            amount = assets[symbol].amount
            rate = ticker[symbol].last
            if amount*rate / balanced_val < 1:
                side = Side.BUY
            else:
                side = Side.SELL
            nlot = Size(symbol, val=abs(amount - balanced_val/rate)).lot

            # decide number of lot using entropy
            ratio = lambda n: (amount + side.value*Size(symbol, lot=n).actual_value) / balanced_val
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
                        size = Size(symbol, lot=nlot),
                        execution_type = ExecutionType.LIMIT,
                        price = Price(symbol, p),
                        time_in_force = "SOK"
                    )
                )
        return orders


    def run(self):
        if not self.api.is_available():
            raise RuntimeError("Exchange is not available now")

        assets = self.api.get_assets(self.symbols)
        ticker = self.api.get_ticker(self.symbols)
        orders = self.rebalance(assets, ticker)

        # post orders
        for order in orders:
            pprint(order)
            order.ID = self.api.post_order(order)
            self.posting_orders.append(order)
            # print(order_id)
            # sleep(0.4)

        # check orders



    def run_forever(self):
        while True:
            try:
                self.run()
            except Exception as e:
                print(f"Error: {e}")
            finally:
                sleep(self.delay)

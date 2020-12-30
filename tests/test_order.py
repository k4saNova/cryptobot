import sys
sys.path.append(".")

from pprint import pprint
from scripts import *
from scripts.data import *

def test_gmo_order():
    config = load_yaml("data/config/gmo.yaml")
    api = get_crypto_api_client(config["exchange"],
                                config["api-key"],
                                config["secret-key"])

    if api.is_available():
        Price.step_values = config["step-values"]
        Size.min_sizes = config["min-sizes"]
        Size.max_sizes = config["max-sizes"]
        orders = [
            Order(symbol = "BTC",
                  side = Side.BUY,
                  size = Size("BTC", val=0.0001),
                  execution_type = ExecutionType.LIMIT,
                  price = Price("BTC", 2500000),
                  time_in_force = "SOK"),
            Order(symbol = "LTC",
                  side = Side.BUY,
                  size = Size("LTC", lot=1),
                  execution_type = ExecutionType.LIMIT,
                  price = Price("LTC", 10000),
                  time_in_force = "SOK")
        ]
        
        print("===== ORDERS =====")
        pprint(orders)
        for order in orders:
            order.ID = api.post_order(order)


        # check order
        print("===== POSTING ORDER =====")
        posting_orders = api.get_orders(orders)
        pprint(posting_orders)

        # cancel order
        data = api.post_cancel_orders(posting_orders)
        pprint(data)


if __name__ == '__main__':
    test_gmo_order()

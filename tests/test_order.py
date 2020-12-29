import sys
sys.path.append(".")

from pprint import pprint
from scripts import *

def test_gmo_order():
    config = load_yaml("data/config/gmo.yaml")
    api = get_crypto_api_client(config["exchange"],
                                config["api-key"],
                                config["secret-key"])

    if api.is_available():
        Price.step_values = config["step-values"]
        order = Order(
            symbol = "BTC",
            side = Side.BUY,
            size = 0.0001,
            execution_type = ExecutionType.LIMIT,
            price = Price("BTC", 2500000),
            time_in_force = "SOK"
        )
        print("===== ORDER =====")
        pprint(order)

        resp = api.post_order(order)
        order_id = resp
        print("===== ORDER ID =====")
        pprint(resp)
            
        # check order
        data = api.get_orders([order_id])
        pprint(data)
        
        # cancel order
        data = api.post_cancel_orders([order_id])
        pprint(data)

        
if __name__ == '__main__':
    test_gmo_order()

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
        order = Order(
            symbol = "BTC",
            side = 1,
            size = 0.0001,
            execution_type = "LIMIT",
            price = 2600000,
            time_in_force = "SOK"
        )
        print("===== ORDER =====")
        pprint(order)

        resp = api.post_order(order)
        print("===== RESP =====")
        pprint(resp)

        
if __name__ == '__main__':
    test_gmo_order()

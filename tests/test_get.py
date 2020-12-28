import sys
sys.path.append(".")

from pprint import pprint
from scripts import *

def test_gmo_get_api():
    config = load_yaml("data/config/gmo.yaml")
    name = config["exchange"]
    api_key = config["api-key"]
    secret_key = config["secret-key"]    
    api = get_crypto_api_client(name, api_key, secret_key)

    symbols = ["BTC", "JPY", "LTC"]
    if api.is_available():
        assets = api.get_assets(symbols)
        print("----- assets -----")
        pprint(assets)

        ticker = api.get_ticker(symbols)
        print("----- ticker -----")
        pprint(ticker)

        orderbooks = api.get_orderbooks("BTC")
        print("----- orderbooks -----")
        pprint(orderbooks["asks"][:3])
        pprint(orderbooks["bids"][:3])
        

        
if __name__ == '__main__':
    test_gmo_get_api()

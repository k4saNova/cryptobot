import sys
sys.path.append(".")
from scripts import *
from datetime import datetime

def test_download():
    api = get_crypto_api_client("GMO", "NONE", "NONE")
    print("https://api.coin.z.com/data/trades/BTC/2020/03/20200314_BTC.csv.gz")
    api.download_execution_history("BTC",
                                   datetime(2020, 3, 14),
                                   "data/history/BTC")
    api.download_execution_history("BTC",
                                   datetime(2100, 3, 14),
                                   "data/history/BTC")    
    
    
if __name__ == '__main__':
    test_download()

    

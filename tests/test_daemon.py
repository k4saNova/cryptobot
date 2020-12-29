import sys
sys.path.append(".")
from scripts import *

def test_daemon():
    config = load_yaml("data/config/gmo.yaml")
    api = get_crypto_api_client(config["exchange"],
                                config["api-key"],
                                config["secret-key"])
    daemon = ShannonsDaemon(api,
                            config["symbols"],
                            config["min-lot"],
                            config["max-lot"],
                            config["step-values"],
                            3)
    daemon.run()


if __name__ == '__main__':
    test_daemon()

from scripts import *

import sys

def main():
    config = load_yaml("data/config/gmo.yaml")
    print(config)

if __name__ == '__main__':
    main()

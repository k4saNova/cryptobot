import sys
sys.path.append(".")

from pprint import pprint
from scripts import *

def test_price():
    Price.step_value = {
        "A": "1",
        "B": "0.001",
        "C": "5"
    }
    pprint(Price.step_value)
    print(Price("A", 100.00000003).submit())
    print(Price("B", 25.25252525).submit())
    print(Price("C", 333.33).submit())
    
    
if __name__ == '__main__':
    test_price()

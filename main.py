import argparse
import os
from src.anarede import Anarede
from src.utils.functions import *

def main():
    args = argparse.ArgumentParser()
    args.add_argument('--file', type=str, default='data/file.pwf')
    args = args.parse_args()
    anarede = Anarede(args=args)
    mkdir_if_not_exists('results/')
    print("*************** Y_BUS ******************")
    write_csv(anarede.y_bus, 'results/y_bus.csv')
    print("[!] - Y_Bus saved on the 'results/y_bus.csv'")
        
        
if __name__ == "__main__":
    main()
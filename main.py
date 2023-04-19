import argparse
import os
from src.anarede import Anarede
from src.utils.functions import *

def main():
    args = argparse.ArgumentParser()
    args.add_argument('--file', type=str, default='data/file.pwf')
    args = args.parse_args()
    anarede = Anarede(args=args)

        
if __name__ == "__main__":
    main()
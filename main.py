import argparse
from src.anarede import Anarede
def main():
    args = argparse.ArgumentParser()
    args.add_argument('--file', type=str, default='data/file.pwf')
    args = args.parse_args()
    anarede = Anarede(args=args)

if __name__ == "__main__":
    main()
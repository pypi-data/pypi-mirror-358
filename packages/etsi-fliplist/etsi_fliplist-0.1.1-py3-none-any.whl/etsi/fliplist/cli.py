# etsi/fliplist/cli.py

import argparse
from .core import reverse_list
from .utils import print_banner


def main():
    # print_banner()
    parser = argparse.ArgumentParser(description="Flip a list of items")
    parser.add_argument("items", nargs='+', help="Items to reverse")
    args = parser.parse_args()

    result = reverse_list(args.items)
    print("Original:", args.items)
    print("Reversed:", result)

if __name__ == "__main__":
    main()

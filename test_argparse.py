import sys
import argparse

def test():
    parser = argparse.ArgumentParser(description="Bedrock Copilot")
    subparsers = parser.add_subparsers(dest="command")

    map_parser = subparsers.add_parser("map")
    map_parser.add_argument("path")

    analyze_parser = subparsers.add_parser("analyze")
    analyze_parser.add_argument("path")

    costs_parser = subparsers.add_parser("costs")
    costs_parser.add_argument("--timerange")
    costs_parser.add_argument("--format")

    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("--type")

    args = parser.parse_args()
    print(args)

if __name__ == "__main__":
    test()

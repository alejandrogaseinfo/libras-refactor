"""Offline diagnostics only; model execution is intentionally absent from the CLI."""

import argparse
import json

from .runtime import doctor


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["doctor"])
    parser.parse_args()
    print(json.dumps(doctor(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

import argparse
import logging
import os

from . import config
from .pair import pair
from .poller import run


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        prog="ecobee_exporter",
        description="Export ecobee sensor data via HomeKit as Prometheus metrics",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    pair_parser = subparsers.add_parser("pair", help="Pair with an ecobee thermostat")
    pair_parser.add_argument(
        "--data-dir",
        default=config.DATA_DIR,
        help=f"Directory for pairing and data files (default: $ECOBEE_DATA_DIR or '.')",
    )

    subparsers.add_parser("run", help="Start the polling daemon")

    args = parser.parse_args()

    if args.command == "pair":
        pair(os.path.join(args.data_dir, "pairing.json"))
    elif args.command == "run":
        run()


main()

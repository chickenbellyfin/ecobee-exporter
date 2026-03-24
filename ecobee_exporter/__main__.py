import argparse
import logging

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
        "--pairing-file",
        default=config.PAIRING_FILE,
        help=f"Path to save pairing data (default: {config.PAIRING_FILE})",
    )

    subparsers.add_parser("run", help="Start the polling daemon")

    args = parser.parse_args()

    if args.command == "pair":
        pair(args.pairing_file)
    elif args.command == "run":
        run()


main()

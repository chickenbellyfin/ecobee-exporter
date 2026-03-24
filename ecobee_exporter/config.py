import os


PAIRING_FILE = os.environ.get("ECOBEE_PAIRING_FILE", "./pairing.json")
POLL_INTERVAL = int(os.environ.get("ECOBEE_POLL_INTERVAL", "300"))
METRICS_PORT = int(os.environ.get("ECOBEE_METRICS_PORT", "9101"))

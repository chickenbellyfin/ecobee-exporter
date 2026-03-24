import os


DATA_DIR = os.environ.get("ECOBEE_DATA_DIR", ".")
PAIRING_FILE = os.path.join(DATA_DIR, "pairing.json")
POLL_INTERVAL = int(os.environ.get("ECOBEE_POLL_INTERVAL", "300"))
METRICS_PORT = int(os.environ.get("ECOBEE_METRICS_PORT", "9101"))

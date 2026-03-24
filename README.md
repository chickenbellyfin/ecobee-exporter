# Ecobee Exporter

Reads sensor data from an ecobee thermostat over the local network via HomeKit Accessory Protocol and exports Prometheus metrics. No ecobee API key or cloud access needed.

## Metrics Exported

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `ecobee_temperature_celsius` | Gauge | `sensor` | Current temperature (Celsius) |
| `ecobee_humidity_percent` | Gauge | `sensor` | Current relative humidity (%) |
| `ecobee_occupancy` | Gauge | `sensor` | Occupancy detected (1/0) |
| `ecobee_heating_cooling_current` | Gauge | — | Current HVAC state (0=Off, 1=Heat, 2=Cool) |
| `ecobee_heating_cooling_target` | Gauge | — | Target HVAC mode (0=Off, 1=Heat, 2=Cool, 3=Auto) |
| `ecobee_target_temperature_celsius` | Gauge | — | Temperature setpoint (Celsius) |
| `ecobee_last_poll_timestamp_seconds` | Gauge | — | Unix timestamp of last successful poll |
| `ecobee_poll_errors_total` | Counter | — | Total failed poll attempts |

## Prerequisites

- ecobee thermostat with HomeKit enabled
- HomeKit setup code (8-digit code from the ecobee or its packaging)
- Python 3.10+

## Setup

```bash
pip install -r requirements.txt
```

## Pairing (one-time)

Run interactively on the same network as the ecobee:

```bash
python -m ecobee_exporter pair --pairing-file ./pairing.json
```

This discovers the ecobee via mDNS, prompts for the HomeKit setup code, and saves pairing credentials. The ecobee supports up to 16 controller pairings, so this won't interfere with Apple Home.

## Running

```bash
# Using environment variables
export ECOBEE_PAIRING_FILE=./pairing.json
export ECOBEE_POLL_INTERVAL=300
export ECOBEE_METRICS_PORT=9101
python -m ecobee_exporter run
```

Metrics are served at `http://localhost:9101/metrics`.

## Docker

```bash
# Start the container (it will wait for pairing)
docker compose up -d

# Pair interactively from inside the running container
docker exec -it ecobee-exporter python -m ecobee_exporter pair

# The poller automatically detects the new pairing file and starts polling
```

Host networking is required for mDNS discovery and direct TCP to the ecobee. Pairing data is persisted in the `./data/` directory.

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `ECOBEE_PAIRING_FILE` | `./pairing.json` | Path to pairing data file |
| `ECOBEE_POLL_INTERVAL` | `300` | Seconds between polls |
| `ECOBEE_METRICS_PORT` | `9101` | Prometheus metrics HTTP port |

## Prometheus Scrape Config

```yaml
scrape_configs:
  - job_name: ecobee
    static_configs:
      - targets: ['localhost:9101']
```

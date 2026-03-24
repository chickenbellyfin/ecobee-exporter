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

## Docker

### docker-compose.yml

```yaml
services: # :9101
  ecobee-exporter:
    image: ghcr.io/chickenbellyfin/ecobee-exporter:latest
    network_mode: host
    volumes:
      - ./ecobee-exporter:/data
    environment:
      - ECOBEE_POLL_INTERVAL=300 # Optional, default 300
      - ECOBEE_METRICS_PORT=9101 # Optional, default 9101
      - ECOBEE_DATA_DIR=/data # Optional, default /data
    restart: unless-stopped
```

### Pairing (one-time)

```bash
# Start the container (it will wait for pairing)
docker compose up -d

# Pair interactively from inside the running container
docker exec -it ecobee-exporter pair

# The poller automatically detects the new pairing file and starts polling
```

This discovers the ecobee via mDNS, prompts for the HomeKit setup code, and saves pairing credentials.

Host networking is required for mDNS discovery and direct TCP to the ecobee. Pairing data is persisted in the `./data/` directory.

Metrics are served at `http://localhost:9101/metrics`.

## Prometheus Scrape Config

```yaml
scrape_configs:
  - job_name: ecobee
    static_configs:
      - targets: ['localhost:9101']
```

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `ECOBEE_DATA_DIR` | `/data` | Directory for pairing and data files |
| `ECOBEE_POLL_INTERVAL` | `300` | Seconds between polls |
| `ECOBEE_METRICS_PORT` | `9101` | Prometheus metrics HTTP port |

## Running with Python

### Prerequisites

- ecobee thermostat with HomeKit enabled
- HomeKit setup code (8-digit code from the ecobee or its packaging)
- Python 3.10+

### Setup

```bash
pip install -r requirements.txt
```

### Pairing (one-time)

```bash
python -m ecobee_exporter pair --data-dir ./data
```

### Running

```bash
export ECOBEE_DATA_DIR=.
export ECOBEE_POLL_INTERVAL=300
export ECOBEE_METRICS_PORT=9101
python -m ecobee_exporter run
```

## (publish image)
```
docker buildx build . -t ghcr.io/chickenbellyfin/ecobee-exporter:$(git rev-parse --short HEAD) --platform linux/amd64,linux/arm64 --push
docker buildx build . -t ghcr.io/chickenbellyfin/ecobee-exporter:latest --platform linux/amd64,linux/arm64 --push
```

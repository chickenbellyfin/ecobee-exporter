from prometheus_client import Counter, Gauge

temperature = Gauge(
    "ecobee_temperature_celsius",
    "Current temperature in Celsius",
    ["sensor"],
)

humidity = Gauge(
    "ecobee_humidity_percent",
    "Current relative humidity percentage",
    ["sensor"],
)

occupancy = Gauge(
    "ecobee_occupancy",
    "Occupancy detected (1=occupied, 0=not occupied)",
    ["sensor"],
)

heating_cooling_current = Gauge(
    "ecobee_heating_cooling_current",
    "Current heating/cooling state (0=Off, 1=Heat, 2=Cool)",
)

heating_cooling_target = Gauge(
    "ecobee_heating_cooling_target",
    "Target heating/cooling state (0=Off, 1=Heat, 2=Cool, 3=Auto)",
)

fan_running = Gauge(
    "ecobee_fan_running",
    "Fan currently running (0=Off, 1=On)",
)

target_temperature = Gauge(
    "ecobee_target_temperature_celsius",
    "Target temperature setpoint in Celsius",
)

last_poll_timestamp = Gauge(
    "ecobee_last_poll_timestamp_seconds",
    "Unix timestamp of last successful poll",
)

poll_errors = Counter(
    "ecobee_poll_errors_total",
    "Total number of failed poll attempts",
)

import asyncio
import logging
import time

from aiohomekit import Controller
from aiohomekit.model.characteristics import CharacteristicsTypes
from prometheus_client import start_http_server
from zeroconf.asyncio import AsyncServiceBrowser, AsyncZeroconf

from . import metrics
from .config import METRICS_PORT, PAIRING_FILE, POLL_INTERVAL

logger = logging.getLogger(__name__)

WAIT_FOR_PAIRING_INTERVAL = 10


def _try_load_pairing(controller) -> bool:
    """Attempt to load the pairing file. Returns True if 'ecobee' pairing is available."""
    try:
        controller.load_data(PAIRING_FILE)
        return "ecobee" in controller.aliases
    except Exception:
        return False


async def poll_once(pairing) -> None:
    accessories = await pairing.list_accessories_and_characteristics()

    for accessory in accessories:
        sensor_name = None
        temp_value = None
        humidity_value = None
        occupancy_value = None
        hc_current = None
        hc_target = None
        fan_current = None
        target_temp = None

        for service in accessory.get("services", []):
            for char in service.get("characteristics", []):
                char_type = char.get("type", "")
                value = char.get("value")

                if char_type == CharacteristicsTypes.NAME:
                    sensor_name = value
                elif char_type == CharacteristicsTypes.TEMPERATURE_CURRENT:
                    temp_value = value
                elif char_type == CharacteristicsTypes.RELATIVE_HUMIDITY_CURRENT:
                    humidity_value = value
                elif char_type == CharacteristicsTypes.OCCUPANCY_DETECTED:
                    occupancy_value = value
                elif char_type == CharacteristicsTypes.HEATING_COOLING_CURRENT:
                    hc_current = value
                elif char_type == CharacteristicsTypes.HEATING_COOLING_TARGET:
                    hc_target = value
                elif char_type == CharacteristicsTypes.FAN_STATE_CURRENT:
                    fan_current = value
                elif char_type == CharacteristicsTypes.TEMPERATURE_TARGET:
                    target_temp = value

        if sensor_name is None:
            continue

        if temp_value is not None:
            metrics.temperature.labels(sensor=sensor_name).set(temp_value)
        if humidity_value is not None:
            metrics.humidity.labels(sensor=sensor_name).set(humidity_value)
        if occupancy_value is not None:
            metrics.occupancy.labels(sensor=sensor_name).set(
                1 if occupancy_value else 0
            )

        # Thermostat-level characteristics (typically only on the main accessory)
        if hc_current is not None:
            metrics.heating_cooling_current.set(hc_current)
        if hc_target is not None:
            metrics.heating_cooling_target.set(hc_target)
        if fan_current is not None:
            metrics.fan_running.set(fan_current)
        if target_temp is not None:
            metrics.target_temperature.set(target_temp)

    metrics.last_poll_timestamp.set(time.time())
    logger.info("Poll complete")


async def _wait_for_pairing(controller) -> None:
    """Block until the pairing file exists and contains a valid 'ecobee' pairing."""
    if _try_load_pairing(controller):
        return

    logger.info(
        "Waiting for pairing file %s. "
        "Run 'docker exec -it ecobee-exporter pair' to pair.",
        PAIRING_FILE,
    )
    while True:
        await asyncio.sleep(WAIT_FOR_PAIRING_INTERVAL)
        if _try_load_pairing(controller):
            return


async def _run() -> None:
    async with AsyncZeroconf() as azc:
        browser = AsyncServiceBrowser(
            azc.zeroconf,
            ["_hap._tcp.local.", "_hap._udp.local."],
            handlers=[lambda **kwargs: None],
        )
        async with Controller(async_zeroconf_instance=azc) as controller:
            logger.info("Starting metrics server on port %d", METRICS_PORT)
            start_http_server(METRICS_PORT)

            await _wait_for_pairing(controller)
            logger.info("Pairing loaded successfully")

            pairing = controller.aliases["ecobee"]

            logger.info("Polling every %d seconds", POLL_INTERVAL)
            try:
                while True:
                    try:
                        await poll_once(pairing)
                    except Exception:
                        logger.warning("Poll failed", exc_info=True)
                        metrics.poll_errors.inc()

                    await asyncio.sleep(POLL_INTERVAL)
            finally:
                await browser.async_cancel()


def run() -> None:
    asyncio.run(_run())

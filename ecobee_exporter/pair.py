import asyncio
import sys

from aiohomekit import Controller
from zeroconf.asyncio import AsyncServiceBrowser, AsyncZeroconf


async def _pair(pairing_file: str) -> None:
    async with AsyncZeroconf() as azc:
        browser = AsyncServiceBrowser(
            azc.zeroconf,
            ["_hap._tcp.local.", "_hap._udp.local."],
            handlers=[lambda **kwargs: None],
        )
        # Give the browser time to register with zeroconf
        await asyncio.sleep(2)
        async with Controller(async_zeroconf_instance=azc) as controller:
            try:
                print("Discovering HomeKit devices on the local network...")
                devices = []
                async for discovery in controller.async_discover(timeout=10):
                    devices.append(discovery)

                if not devices:
                    print("No HomeKit devices found. Make sure the ecobee is on the same network.")
                    sys.exit(1)

                # Filter for ecobee devices, fall back to showing all
                ecobee_devices = [
                    d for d in devices if "ecobee" in d.description.name.lower()
                ]
                candidates = ecobee_devices if ecobee_devices else devices

                print(f"\nFound {len(candidates)} device(s):\n")
                for i, discovery in enumerate(candidates):
                    desc = discovery.description
                    print(f"  [{i}] {desc.name} (model: {desc.model}, id: {desc.id})")

                if len(candidates) == 1:
                    selected = candidates[0]
                    print(f"\nAuto-selecting: {selected.description.name}")
                else:
                    try:
                        choice = int(input("\nSelect Ecobee device number: "))
                        selected = candidates[choice]
                    except (ValueError, IndexError):
                        print("Invalid selection.")
                        sys.exit(1)

                raw_pin = input("\nEnter the HomeKit setup code (XXX-XX-XXX): ").strip()
                pin = raw_pin.replace("-", "").replace(" ", "")
                if len(pin) != 8 or not pin.isdigit():
                    print("Invalid setup code. Expected 8 digits (e.g. 123-45-678).")
                    sys.exit(1)
                pin = f"{pin[:3]}-{pin[3:5]}-{pin[5:]}"

                print(f"\nPairing with {selected.description.name}...")
                try:
                    finish_pairing = await selected.async_start_pairing("ecobee")
                    pairing = await finish_pairing(pin)
                except Exception as e:
                    print(f"Pairing failed: {e}")
                    sys.exit(1)

                # Register in the top-level controller so save_data can find it
                controller.aliases["ecobee"] = pairing
                controller.save_data(pairing_file)
                print(f"Pairing successful! Data saved to {pairing_file}")
            finally:
                await browser.async_cancel()


def pair(pairing_file: str) -> None:
    asyncio.run(_pair(pairing_file))

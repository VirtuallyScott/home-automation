# ---------------------------------------------------------------------------
# main.py — Local Temp Monitor entry point (MicroPython)
#
# Boot sequence:
#   1. Bring up Ethernet (PoE — Olimex ESP32-POE-ISO-IND)
#   2. Scan 1-Wire bus, print discovered ROM addresses
#   3. Loop: read sensors → write to InfluxDB → sleep POLL_INTERVAL_S
# ---------------------------------------------------------------------------

import time
import network
from machine import Pin

import config
import sensors as sensor_bus
import influx


# ---------------------------------------------------------------------------
# Ethernet init
# ---------------------------------------------------------------------------

def init_ethernet():
    lan = network.LAN(
        mdc         = Pin(config.ETH_MDC_PIN),
        mdio        = Pin(config.ETH_MDIO_PIN),
        power       = Pin(config.ETH_POWER_PIN),
        phy_type    = network.PHY_LAN8720,
        phy_addr    = config.ETH_PHY_ADDR,
        clock_mode  = network.ETH_CLOCK_GPIO17_OUT,
    )
    lan.active(True)

    if config.STATIC_IP:
        lan.ifconfig((
            config.STATIC_IP,
            config.STATIC_MASK,
            config.STATIC_GW,
            config.STATIC_DNS,
        ))
        print(f"[net] Static IP: {config.STATIC_IP}")
    else:
        # DHCP — wait for address
        print("[net] Waiting for DHCP...")
        timeout = 20
        while not lan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1

        if not lan.isconnected():
            raise RuntimeError("Ethernet: DHCP timeout after 20 s")

    ip, mask, gw, dns = lan.ifconfig()
    print(f"[net] Connected — IP={ip}  GW={gw}")
    return lan


# ---------------------------------------------------------------------------
# Sensor discovery helper
# ---------------------------------------------------------------------------

def discover_sensors(bus):
    """Scan bus, print ROM addresses.  Required on first flash to populate config."""
    found = bus.scan()
    print(f"[sensors] Found {len(found)} sensor(s):")
    for rom, label in found:
        hex_addr = "".join("{:02x}".format(b) for b in rom)
        print(f"  ROM={hex_addr}  label={label}")
    return found


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def run():
    # 1. Network
    init_ethernet()

    # 2. Sensor init
    bus = sensor_bus.TempSensorBus()
    discover_sensors(bus)

    # 3. Poll loop
    print(f"[main] Starting poll loop — interval={config.POLL_INTERVAL_S}s")
    consecutive_errors = 0
    MAX_CONSECUTIVE_ERRORS = 10

    while True:
        loop_start = time.time()
        try:
            readings = bus.read_all()

            # Log to serial
            for r in readings:
                f_temp = r["celsius"] * 9 / 5 + 32
                print(f"  {r['label']}: {r['celsius']:.2f} °C / {f_temp:.1f} °F")

            # Write to InfluxDB
            influx.write(readings, timestamp_s=loop_start)
            consecutive_errors = 0

        except Exception as exc:
            consecutive_errors += 1
            print(f"[main] ERROR ({consecutive_errors}/{MAX_CONSECUTIVE_ERRORS}): {exc}")
            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                print("[main] Too many consecutive errors — rebooting")
                import machine
                machine.reset()

        # Sleep remainder of interval
        elapsed = time.time() - loop_start
        sleep_s = max(0, config.POLL_INTERVAL_S - elapsed)
        time.sleep(sleep_s)


# ---------------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------------

try:
    run()
except Exception as exc:
    print(f"[main] Fatal: {exc}")
    import machine
    time.sleep(5)
    machine.reset()

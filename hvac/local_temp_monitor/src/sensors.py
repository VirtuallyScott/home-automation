# ---------------------------------------------------------------------------
# sensors.py — DS18B20 1-Wire temperature sensor driver
# MicroPython: uses built-in onewire + ds18x20 modules.
# ---------------------------------------------------------------------------

import time
import onewire
import ds18x20
from machine import Pin

import config


class TempSensorBus:
    """Manages one 1-Wire bus with one or more DS18B20 sensors."""

    def __init__(self):
        pin = Pin(config.ONE_WIRE_PIN)
        self._ow  = onewire.OneWire(pin)
        self._ds  = ds18x20.DS18X20(self._ow)
        self._roms = []

    def scan(self):
        """Scan bus, store ROM addresses, return list of (rom_bytes, label)."""
        self._roms = self._ds.scan()
        if not self._roms:
            raise RuntimeError("No DS18B20 sensors found on 1-Wire bus")

        result = []
        for rom in self._roms:
            label = config.SENSOR_LABELS.get(bytes(rom), _rom_hex(rom))
            result.append((bytes(rom), label))
        return result

    def read_all(self):
        """
        Trigger conversion on all sensors, wait, then return readings.

        Returns list of dicts:
            {"rom": bytes, "label": str, "celsius": float}

        Raises RuntimeError if no sensor returns a valid reading.
        """
        if not self._roms:
            self.scan()

        self._ds.convert_temp()
        time.sleep_ms(750)  # DS18B20 max conversion time at 12-bit resolution

        readings = []
        for rom in self._roms:
            try:
                c = self._ds.read_temp(rom)
                label = config.SENSOR_LABELS.get(bytes(rom), _rom_hex(rom))
                readings.append({
                    "rom":     bytes(rom),
                    "label":   label,
                    "celsius": c,
                })
            except Exception as exc:
                print(f"[sensors] read_temp failed for {_rom_hex(rom)}: {exc}")

        if not readings:
            raise RuntimeError("All DS18B20 reads failed")

        return readings


def _rom_hex(rom) -> str:
    """Return ROM address as hex string, e.g. '28ff1234567890ab'."""
    return "".join("{:02x}".format(b) for b in rom)

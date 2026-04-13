# ---------------------------------------------------------------------------
# config.py — Local Temp Monitor
# Edit these values before flashing.
# ---------------------------------------------------------------------------

# --- Ethernet / network -----------------------------------------------------
# DHCP is used by default.  Set STATIC_IP = None for DHCP.
STATIC_IP      = None   # e.g. "192.168.1.50"
STATIC_MASK    = None   # e.g. "255.255.255.0"
STATIC_GW      = None   # e.g. "192.168.1.1"
STATIC_DNS     = None   # e.g. "192.168.1.1"

# --- 1-Wire sensor GPIO -----------------------------------------------------
ONE_WIRE_PIN   = 4      # GPIO4 — shared DS18B20 data bus

# --- Sensor labels (keyed by DS18B20 ROM address bytes) ---------------------
# ROM addresses are discovered at first boot and printed to serial.
# Paste the discovered addresses here then re-flash.
# Format: bytes object, e.g. b'\x28\xff\x...'
# Leave empty dict to auto-detect and log all found sensors.
SENSOR_LABELS  = {
    # b'\x28\xXX\xXX\xXX\xXX\xXX\xXX\xXX': "return_plenum",
    # b'\x28\xXX\xXX\xXX\xXX\xXX\xXX\xXX': "supply_plenum",
    # b'\x28\xXX\xXX\xXX\xXX\xXX\xXX\xXX': "attic",
}

# --- Poll interval ----------------------------------------------------------
POLL_INTERVAL_S = 30    # seconds between readings  (TBD — candidates: 10, 30, 60)

# --- InfluxDB v2 ------------------------------------------------------------
INFLUX_HOST    = "192.168.1.XX"     # on-prem host IP or hostname
INFLUX_PORT    = 8086
INFLUX_ORG     = "home"
INFLUX_BUCKET  = "hvac"
INFLUX_TOKEN   = "REPLACE_WITH_YOUR_INFLUXDB_TOKEN"  # do not commit real token

# Measurement name written to InfluxDB
INFLUX_MEASUREMENT = "temperature"

# --- Hardware (Olimex ESP32-POE-ISO-IND) ------------------------------------
# These match the Olimex board — do not change unless using different hardware.
ETH_MDC_PIN    = 23
ETH_MDIO_PIN   = 18
ETH_POWER_PIN  = 12     # Active-high enable for LAN8710A
ETH_PHY_ADDR   = 0

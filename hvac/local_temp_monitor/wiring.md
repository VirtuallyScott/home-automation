# Local Temp Monitor — Wiring Diagram

## Architecture

```text
  [RJ45 PoE In] ──► [ESP32-POE-ISO-IND] ──► GPIO4 (1-Wire DATA bus)
  (UniFi Switch)        │                         │
                      3.3V + GND                4.7KΩ pull-up
                        │                    to 3.3V (on breadboard)
                        └──► [Solder Breadboard]
                                    │
                     ┌──────────────┼──────────────┐────── (spare)
                     │              │              │
                  [TB1]          [TB2]          [TB3]        [TB4]
               Return Plenum   Supply Plenum    Attic         Spare
               DS18B20 #1      DS18B20 #2      DS18B20 #3
```

---

## Terminal Block Pinout (all 4 identical)

Each `691210910003` 3-pos 2.54mm terminal block:

```text
  ┌─────┬─────--┬─────┐
  │  1  │  2    │  3  │
  │ VCC │ DATA  │ GND │
  │3.3V │1-Wire │  0V │
  └─────┴─────--┴─────┘
```

---

## Breadboard Wiring

```text
  ESP32-POE-ISO-IND
  ┌────────────────────────────────┐
  │  3.3V ──────────────────────── │──► PWR rail (+)
  │  GND  ──────────────────────── │──► GND rail (-)
  │  GPIO4 ─────────────────────── │──► 1-Wire DATA bus
  └────────────────────────────────┘

  Breadboard
  ┌─────────────────────────────────────────────────────┐
  │                                                     │
  │  PWR (+3.3V) ──┬──────────────────────────────────  │
  │                │                                    │
  │               [R1 4.7KΩ]  ← pull-up (CF14JT4K70)    │
  │                │                                    │
  │  DATA bus  ────┴── TB1.2 ── TB2.2 ── TB3.2 ──TB4.2  │
  │                                                     │
  │  GND  (-)  ──────  TB1.3 ── TB2.3 ── TB3.3 ──TB4.3  │
  │                                                     │
  │  PWR (+3.3V) ──────TB1.1 ── TB2.1 ── TB3.1 ──TB4.1  │
  │                                                     │
  └─────────────────────────────────────────────────────┘
```

---

## DS18B20 Sensor Wire Colors (DFR0198)

| Wire | Color | Connect to |
| --- | --- | --- |
| VCC | Red | TB pin 1 (3.3V) |
| DATA | Yellow | TB pin 2 (1-Wire bus) |
| GND | Black | TB pin 3 (GND) |

---

## ESP32-POE-ISO-IND Pin Assignments

| ESP32 Pin | Function | Notes |
| --- | --- | --- |
| 3.3V | Power out | To breadboard PWR rail |
| GND | Ground | To breadboard GND rail |
| GPIO4 | 1-Wire DATA | To breadboard DATA bus |
| ETH (RJ45) | PoE input | From UniFi switch |

> **Note:** GPIO4 is free on ESP32-POE-ISO-IND. Avoid GPIO0, GPIO2, GPIO12–GPIO15 (used by Ethernet PHY / boot strapping).

---

## Pull-up Resistor

- **Value:** 4.7KΩ (CF14JT4K70)
- **Location:** On breadboard between 3.3V rail and DATA bus
- **Qty:** 1 shared across all sensors (1-Wire bus)
- Install remaining 4 resistors as spares

---

## Cable Entry

Each sensor cable enters enclosure through a `IPG-2227` PG7 cable gland (3.05–6.1mm). Four glands fitted — one per sensor position including spare.

---

## Sensor Assignment

| Terminal Block | Sensor | Location |
| -------------- | ------ | -------- |
| TB1 | DS18B20 #1 | Return air plenum |
| TB2 | DS18B20 #2 | Supply air plenum |
| TB3 | DS18B20 #3 | Attic |
| TB4 | — (spare) | Future expansion |

---

## 1-Wire Bus Notes

- All 3 (or 4) sensors share single GPIO pin — 1-Wire is multi-drop
- Each DS18B20 has unique 64-bit ROM address; addressed individually in firmware
- Max recommended devices on bus: ~10 with 4.7KΩ pull-up
- Max cable run: ~100m with proper pull-up; attic run should be fine

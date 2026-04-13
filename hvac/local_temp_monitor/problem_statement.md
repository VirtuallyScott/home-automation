# Local Temperature Monitor — Problem Statement

## Overview

Monitor HVAC performance and attic thermal conditions via three DS18B20 waterproof temperature sensors connected to a PoE-powered ESP32 board. Data streams to on-premise InfluxDB and visualized in Grafana.

## Problem

No visibility into HVAC delta-T (supply vs return) or attic temperature in real time. Without this data:

- Can't detect low refrigerant or airflow restriction (low delta-T)
- Can't detect frozen coil or blocked filter (abnormal delta-T)
- Can't correlate attic temp with HVAC load or insulation performance
- No historical trend data for seasonal analysis

## Solution

Deploy a single ESP32-POE-ISO-IND board powered via PoE from a UniFi switch. Three DS18B20 sensors routed to probe points. Board polls sensors every N seconds (TBD) and pushes readings to InfluxDB over the local network.

## Sensor Placement

| Sensor | Location | Purpose |
| --- | --- | --- |
| Sensor 1 | Return air plenum | Measure return air temp entering air handler |
| Sensor 2 | Supply air plenum | Measure conditioned air leaving air handler |
| Sensor 3 | Attic | Monitor attic ambient temp |

**Delta-T** (supply − return) = primary HVAC health indicator. Expected: 16–22°F for healthy cooling system.

## Data Pipeline

```text
ESP32 sensors
    → poll every N seconds (TBD)
    → HTTP/TCP → InfluxDB (on-prem)
    → Grafana dashboard
```

## Power

PoE from UniFi switch. No separate power supply needed. Board: ESP32-POE-ISO-IND (isolated PoE, 802.3af).

## Open Questions

- [ ] Poll interval N (candidates: 10s, 30s, 60s)
- [ ] InfluxDB host/bucket/org config
- [ ] Grafana dashboard panels — raw temps + delta-T + attic overlay
- [ ] Alert thresholds (e.g. delta-T < 10°F, attic > 130°F)
- [ ] Sensor wire routing and gland placement on enclosure

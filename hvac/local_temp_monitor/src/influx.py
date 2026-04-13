# ---------------------------------------------------------------------------
# influx.py — InfluxDB v2 line-protocol writer
# Uses MicroPython urequests (no TLS required for on-prem).
# ---------------------------------------------------------------------------

import urequests

import config


def write(readings: list, timestamp_s: int | None = None):
    """
    Write a list of sensor readings to InfluxDB using line protocol.

    readings: list of dicts with keys "label" and "celsius"
              (as returned by TempSensorBus.read_all)
    timestamp_s: Unix epoch seconds.  If None, InfluxDB uses server time.

    Raises OSError / ValueError on network or HTTP error.
    """
    lines = []
    for r in readings:
        tag   = _escape_tag(r["label"])
        value = "{:.4f}".format(r["celsius"])
        line  = f'{config.INFLUX_MEASUREMENT},sensor={tag} celsius={value}'
        if timestamp_s is not None:
            line += f" {timestamp_s}"
        lines.append(line)

    body = "\n".join(lines)
    url  = (
        f"http://{config.INFLUX_HOST}:{config.INFLUX_PORT}"
        f"/api/v2/write"
        f"?org={config.INFLUX_ORG}"
        f"&bucket={config.INFLUX_BUCKET}"
        f"&precision=s"
    )
    headers = {
        "Authorization": f"Token {config.INFLUX_TOKEN}",
        "Content-Type": "text/plain; charset=utf-8",
    }

    resp = urequests.post(url, data=body, headers=headers)
    status = resp.status_code
    resp.close()

    # InfluxDB v2 returns 204 on success
    if status != 204:
        raise OSError(f"InfluxDB write rejected: HTTP {status}")


def _escape_tag(value: str) -> str:
    """Escape spaces and commas in InfluxDB tag values."""
    return value.replace(" ", "\\ ").replace(",", "\\,")

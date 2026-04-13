#!/usr/bin/env python3
"""
Generate KiCad 10 schematic for ESP32 local temp monitor.

Run:  python3 generate_schematic.py
Out:  esp32_temp_monitor.kicad_sch

Components
----------
J1  ESP32-POE-ISO-IND (Conn_01x03, mirror_y) — GPIO4/+3V3/GND
R1  4.7 kΩ pull-up (Device:R)
J2  TB1 Return Plenum  (Conn_01x03)
J3  TB2 Supply Plenum  (Conn_01x03)
J4  TB3 Attic          (Conn_01x03)
J5  TB4 Spare          (Conn_01x03)
"""

import uuid, os, sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_FILE   = os.path.join(SCRIPT_DIR, "esp32_temp_monitor.kicad_sch")
LIB_BASE   = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"


# ── helpers ──────────────────────────────────────────────────────────────────

def uid():
    return str(uuid.uuid4())


def extract_symbol(lib: str, name: str) -> str:
    path = f"{LIB_BASE}/{lib}.kicad_sym"
    with open(path) as f:
        text = f.read()
    pattern = f'(symbol "{name}"'
    idx = text.find(pattern)
    if idx < 0:
        raise ValueError(f"Symbol '{name}' not found in {lib}.kicad_sym")
    depth = 0
    for i, ch in enumerate(text[idx:], idx):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return text[idx : i + 1]
    raise ValueError("Unbalanced parentheses in symbol")


def embed_lib_sym(lib: str, name: str) -> str:
    """Return the symbol block with the lib:name prefix for lib_symbols."""
    raw = extract_symbol(lib, name)
    # Replace top-level symbol name with lib:name (first occurrence only)
    return raw.replace(f'(symbol "{name}"', f'(symbol "{lib}:{name}"', 1)


# ── schematic element builders ────────────────────────────────────────────────

def sym_props(reference, value, ref_x, ref_y, ref_angle=0, val_x=0, val_y=0, val_angle=0):
    return f"""\
        (property "Reference" "{reference}"
            (at {ref_x} {ref_y} {ref_angle})
            (do_not_autoplace no)
            (effects (font (size 1.27 1.27)))
        )
        (property "Value" "{value}"
            (at {val_x} {val_y} {val_angle})
            (do_not_autoplace no)
            (effects (font (size 1.27 1.27)))
        )
        (property "Footprint" ""
            (at 0 0 0)
            (do_not_autoplace no)
            (hide yes)
            (effects (font (size 1.27 1.27)))
        )
        (property "Datasheet" ""
            (at 0 0 0)
            (do_not_autoplace no)
            (hide yes)
            (effects (font (size 1.27 1.27)))
        )\
"""


def power_sym(lib_id: str, value: str, x: float, y: float, ref_num: int, angle: int = 0) -> str:
    return f"""    (symbol
        (lib_id "{lib_id}")
        (at {x:.4f} {y:.4f} {angle})
        (unit 1)
        (exclude_from_sim no)
        (in_bom yes)
        (on_board yes)
        (dnp no)
        (fields_autoplaced yes)
        (property "Reference" "#PWR{ref_num:02d}"
            (at 0 0 0)
            (do_not_autoplace no)
            (hide yes)
            (effects (font (size 1.27 1.27)))
        )
        (property "Value" "{value}"
            (at 0 0 0)
            (do_not_autoplace no)
            (effects (font (size 1.27 1.27)))
        )
        (property "Footprint" ""
            (at 0 0 0)
            (do_not_autoplace no)
            (hide yes)
            (effects (font (size 1.27 1.27)))
        )
        (property "Datasheet" ""
            (at 0 0 0)
            (do_not_autoplace no)
            (hide yes)
            (effects (font (size 1.27 1.27)))
        )
        (pin "1" (uuid "{uid()}"))
        (uuid "{uid()}")
    )"""


def connector(ref: str, value: str, x: float, y: float,
              mirror: str | None = None, angle: int = 0,
              pin_count: int = 3) -> str:
    mirror_line = f"\n        (mirror {mirror})" if mirror else ""
    pins = "\n".join(
        f'        (pin "{i}" (uuid "{uid()}"))' for i in range(1, pin_count + 1)
    )
    return f"""    (symbol
        (lib_id "Connector_Generic:Conn_01x03")
        (at {x:.4f} {y:.4f} {angle}){mirror_line}
        (unit 1)
        (exclude_from_sim no)
        (in_bom yes)
        (on_board yes)
        (dnp no)
        (property "Reference" "{ref}"
            (at 0 5.08 0)
            (do_not_autoplace no)
            (effects (font (size 1.27 1.27)))
        )
        (property "Value" "{value}"
            (at 0 -5.08 0)
            (do_not_autoplace no)
            (effects (font (size 1.27 1.27)))
        )
        (property "Footprint" ""
            (at 0 0 0)
            (do_not_autoplace no)
            (hide yes)
            (effects (font (size 1.27 1.27)))
        )
        (property "Datasheet" ""
            (at 0 0 0)
            (do_not_autoplace no)
            (hide yes)
            (effects (font (size 1.27 1.27)))
        )
{pins}
        (uuid "{uid()}")
    )"""


def resistor(ref: str, value: str, x: float, y: float, angle: int = 0) -> str:
    return f"""    (symbol
        (lib_id "Device:R")
        (at {x:.4f} {y:.4f} {angle})
        (unit 1)
        (exclude_from_sim no)
        (in_bom yes)
        (on_board yes)
        (dnp no)
        (property "Reference" "{ref}"
            (at 2.032 0 90)
            (do_not_autoplace no)
            (effects (font (size 1.27 1.27)))
        )
        (property "Value" "{value}"
            (at 0 0 90)
            (do_not_autoplace no)
            (effects (font (size 1.27 1.27)))
        )
        (property "Footprint" ""
            (at 0 0 0)
            (do_not_autoplace no)
            (hide yes)
            (effects (font (size 1.27 1.27)))
        )
        (property "Datasheet" ""
            (at 0 0 0)
            (do_not_autoplace no)
            (hide yes)
            (effects (font (size 1.27 1.27)))
        )
        (pin "1" (uuid "{uid()}"))
        (pin "2" (uuid "{uid()}"))
        (uuid "{uid()}")
    )"""


def label(name: str, x: float, y: float, angle: int = 0) -> str:
    return f"""    (label "{name}"
        (at {x:.4f} {y:.4f} {angle})
        (fields_autoplaced yes)
        (effects
            (font (size 1.27 1.27))
            (justify left bottom)
        )
        (uuid "{uid()}")
    )"""


def wire(x1: float, y1: float, x2: float, y2: float) -> str:
    return f"""    (wire
        (pts (xy {x1:.4f} {y1:.4f}) (xy {x2:.4f} {y2:.4f}))
        (stroke (width 0) (type default))
        (uuid "{uid()}")
    )"""


def no_connect(x: float, y: float) -> str:
    return f"""    (no_connect (at {x:.4f} {y:.4f}) (uuid "{uid()}"))"""


def text(content: str, x: float, y: float, size: float = 1.27) -> str:
    return f"""    (text "{content}"
        (at {x:.4f} {y:.4f} 0)
        (effects (font (size {size} {size})))
        (uuid "{uid()}")
    )"""


# ── pin coordinate helpers ────────────────────────────────────────────────────
# Conn_01x03 library pins at (-5.08, +2.54), (-5.08, 0), (-5.08, -2.54) angle 0
# With mirror_y: pin x negated → (+5.08, +2.54), (+5.08, 0), (+5.08, -2.54)
# Device:R pins at (0, +3.81) angle 270 and (0, -3.81) angle 90
# power:GND pin at (0,0); power:+3V3 pin at (0,0)

def conn_pins(ox, oy, mirror_y=False):
    """Return dict of pin number → (px, py) for Conn_01x03."""
    sign = 1 if mirror_y else -1
    return {
        1: (ox + sign * 5.08, oy + 2.54),
        2: (ox + sign * 5.08, oy + 0.00),
        3: (ox + sign * 5.08, oy - 2.54),
    }

def resistor_pins(ox, oy, angle=0):
    """Return (pin1_xy, pin2_xy) for Device:R at (ox,oy) with rotation."""
    import math
    a = math.radians(angle)
    cos_a, sin_a = math.cos(a), math.sin(a)
    def rot(x, y):
        return (ox + x * cos_a - y * sin_a, oy + x * sin_a + y * cos_a)
    return rot(0, 3.81), rot(0, -3.81)   # pin1, pin2


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    # --- embedded lib symbols -------------------------------------------------
    lib_gnd  = embed_lib_sym("power", "GND")
    lib_3v3  = embed_lib_sym("power", "+3V3")
    lib_r    = embed_lib_sym("Device", "R")
    lib_conn = embed_lib_sym("Connector_Generic", "Conn_01x03")

    # --- component positions --------------------------------------------------
    # J1  ESP32 connector — mirror_y so pins face RIGHT
    J1_X, J1_Y = 50.0, 95.0
    j1_pins = conn_pins(J1_X, J1_Y, mirror_y=True)
    # j1_pins[1] = GPIO4/DATA, [2] = +3V3, [3] = GND

    # R1  pull-up resistor — vertical (angle 0), placed between J1 and TBs
    R1_X, R1_Y = 90.0, 91.0
    r1_p1, r1_p2 = resistor_pins(R1_X, R1_Y, angle=0)
    # r1_p1 = bottom (DATA bus), r1_p2 = top (+3V3)

    # J2-J5 terminal blocks — default (pins face LEFT)
    TB_X = 155.0
    tb_positions = {
        "J2": (TB_X, 75.0,  "TB1: Return Plenum"),
        "J3": (TB_X, 105.0, "TB2: Supply Plenum"),
        "J4": (TB_X, 135.0, "TB3: Attic"),
        "J5": (TB_X, 165.0, "TB4: Spare"),
    }

    # --- build elements -------------------------------------------------------
    elements = []

    # J1 with wires to R1 and then label
    # Pin 3 → GND, Pin 2 → +3V3, Pin 1 → DATA wire to R1 pin 1 (bottom)
    elements.append(connector("J1", "ESP32-POE-ISO-IND", J1_X, J1_Y, mirror="y"))

    p1x, p1y = j1_pins[1]   # DATA  at bottom
    p2x, p2y = j1_pins[2]   # +3V3  at middle
    p3x, p3y = j1_pins[3]   # GND   at top

    # J1 pin 1 (DATA) → wire right → join R1 data wire → continue right labelled 1WIRE_DATA
    # Use a horizontal wire from J1 to R1 pin1, then a vertical wire up to R1
    # R1 pin1 (bottom) is below R1 body; make a neat wire path.
    # Simpler: just use net labels everywhere for the DATA bus.

    # Power/gnd for J1
    elements.append(power_sym("power:+3V3", "+3V3", p2x, p2y, ref_num=1))
    elements.append(power_sym("power:GND",  "GND",  p3x, p3y, ref_num=2))

    # DATA wire: J1 pin1 → horizontal → junction → R1 pin1 (bottom)
    r1p1x, r1p1y = r1_p1   # R1 bottom (DATA end)
    # Wire: horizontal from J1 DATA pin to R1 DATA pin x, then vertical up to R1
    elements.append(wire(p1x, p1y, r1p1x, p1y))     # horizontal
    elements.append(wire(r1p1x, p1y, r1p1x, r1p1y)) # vertical up to R1 pin1

    # Horizontal data bus going right from R1 pin1 level
    DATA_BUS_Y = r1p1y  # horizontal bus at this Y

    # R1 component
    elements.append(resistor("R1", "4.7kΩ", R1_X, R1_Y, angle=0))
    r1p2x, r1p2y = r1_p2  # R1 top (+3V3 end)
    elements.append(power_sym("power:+3V3", "+3V3", r1p2x, r1p2y, ref_num=3))

    # Data bus: extend from R1 pin1 rightward; TB connectors tap off it
    # We'll use net labels for TB connections instead of a long bus wire
    # (cleaner for widely spaced components)

    # TB connectors
    ref_offset = 4
    for idx, (ref, (tx, ty, tval)) in enumerate(tb_positions.items()):
        elements.append(connector(ref, tval, tx, ty))
        tb_p = conn_pins(tx, ty, mirror_y=False)
        tbp1x, tbp1y = tb_p[1]  # +3V3
        tbp2x, tbp2y = tb_p[2]  # DATA
        tbp3x, tbp3y = tb_p[3]  # GND

        elements.append(power_sym("power:+3V3", "+3V3", tbp1x, tbp1y, ref_num=ref_offset + idx * 3))
        elements.append(label("1WIRE_DATA", tbp2x, tbp2y, angle=180))
        elements.append(power_sym("power:GND",  "GND",  tbp3x, tbp3y, ref_num=ref_offset + idx * 3 + 1))

    # Net label on J1 DATA → same net "1WIRE_DATA"
    # Connect via a label at the junction point between the wire and R1
    elements.append(label("1WIRE_DATA", r1p1x, DATA_BUS_Y, angle=270))

    # Title annotation text
    elements.append(text("1-Wire Bus (shared GPIO4)", 95.0, 108.0, size=1.0))
    elements.append(text("Pull-up to +3V3", r1p2x + 3, r1p2y, size=1.0))

    # --- assemble schematic ---------------------------------------------------
    lib_block = "\n".join([
        "    " + lib_gnd,
        "    " + lib_3v3,
        "    " + lib_r,
        "    " + lib_conn,
    ])

    body = "\n".join(elements)

    schematic = f"""(kicad_sch
    (version 20250114)
    (generator "eeschema")
    (generator_version "9.0")
    (uuid "{uid()}")
    (paper "A4")
    (title_block
        (title "Local Temp Monitor — ESP32 Wiring")
        (date "2026-04-12")
        (rev "1.0")
        (comment 1 "ESP32-POE-ISO-IND + DS18B20 1-Wire sensors")
        (comment 2 "PoE from UniFi switch → InfluxDB → Grafana")
    )
    (lib_symbols
{lib_block}
    )
{body}
)
"""

    with open(OUT_FILE, "w") as f:
        f.write(schematic)

    print(f"Written: {OUT_FILE}")
    print(f"  Open with: open '{OUT_FILE}'")


if __name__ == "__main__":
    main()

"""
Marine piping system reference data.
Pipe schedules per ASME B36.10, materials per class society guidelines.
"""

# ── Standard pipe sizes (NPS → OD mm, then schedules → wall thickness mm) ──
# OD values per ASME B36.10M
PIPE_SIZES = {
    "DN15 (1/2\")":   {"OD": 21.3,  "schedules": {"SCH 40": 2.77, "SCH 80": 3.73, "SCH 160": 4.78}},
    "DN20 (3/4\")":   {"OD": 26.7,  "schedules": {"SCH 40": 2.87, "SCH 80": 3.91, "SCH 160": 5.56}},
    "DN25 (1\")":     {"OD": 33.4,  "schedules": {"SCH 40": 3.38, "SCH 80": 4.55, "SCH 160": 6.35}},
    "DN32 (1-1/4\")": {"OD": 42.2,  "schedules": {"SCH 40": 3.56, "SCH 80": 4.85, "SCH 160": 6.35}},
    "DN40 (1-1/2\")": {"OD": 48.3,  "schedules": {"SCH 40": 3.68, "SCH 80": 5.08, "SCH 160": 7.14}},
    "DN50 (2\")":     {"OD": 60.3,  "schedules": {"SCH 40": 3.91, "SCH 80": 5.54, "SCH 160": 8.74}},
    "DN65 (2-1/2\")": {"OD": 73.0,  "schedules": {"SCH 40": 5.16, "SCH 80": 7.01, "SCH 160": 9.53}},
    "DN80 (3\")":     {"OD": 88.9,  "schedules": {"SCH 40": 5.49, "SCH 80": 7.62, "SCH 160": 11.13}},
    "DN100 (4\")":    {"OD": 114.3, "schedules": {"SCH 40": 6.02, "SCH 80": 8.56, "SCH 160": 13.49}},
    "DN125 (5\")":    {"OD": 141.3, "schedules": {"SCH 40": 6.55, "SCH 80": 9.53, "SCH 160": 15.88}},
    "DN150 (6\")":    {"OD": 168.3, "schedules": {"SCH 40": 7.11, "SCH 80": 10.97, "SCH 160": 18.26}},
    "DN200 (8\")":    {"OD": 219.1, "schedules": {"SCH 40": 8.18, "SCH 80": 12.70, "SCH 160": 23.01}},
    "DN250 (10\")":   {"OD": 273.1, "schedules": {"SCH 40": 9.27, "SCH 80": 15.09, "SCH 160": 28.58}},
    "DN300 (12\")":   {"OD": 323.9, "schedules": {"SCH 40": 10.31,"SCH 80": 17.48, "SCH 160": 33.32}},
    "DN350 (14\")":   {"OD": 355.6, "schedules": {"SCH 40": 11.13,"SCH 80": 19.05, "SCH 160": 35.71}},
    "DN400 (16\")":   {"OD": 406.4, "schedules": {"SCH 40": 12.70,"SCH 80": 21.44, "SCH 160": 40.49}},
    "DN450 (18\")":   {"OD": 457.2, "schedules": {"SCH 40": 14.27,"SCH 80": 23.83, "SCH 160": 45.24}},
    "DN500 (20\")":   {"OD": 508.0, "schedules": {"SCH 40": 15.09,"SCH 80": 26.19, "SCH 160": 50.01}},
}

# ── Fluid properties at ~25°C ──────────────────────────────────────────────
FLUID_PROPERTIES = {
    "Sea Water":    {"density": 1025, "viscosity": 1.07e-3, "roughness": 0.046},
    "Fresh Water":  {"density": 998,  "viscosity": 1.00e-3, "roughness": 0.046},
    "HFO":         {"density": 991,  "viscosity": 380e-3,  "roughness": 0.046},
    "MDO/DO":      {"density": 870,  "viscosity": 4.5e-3,  "roughness": 0.046},
    "Lube Oil":    {"density": 890,  "viscosity": 68e-3,   "roughness": 0.046},
}

# ── Recommended flow velocities (m/s) ─────────────────────────────────────
VELOCITY_RANGES = {
    "Ballast":      {"fluid": "Sea Water",   "min": 1.5, "max": 3.0, "recommended": 2.0},
    "Bilge":        {"fluid": "Sea Water",   "min": 1.0, "max": 2.5, "recommended": 1.8},
    "Fuel Oil HFO": {"fluid": "HFO",         "min": 0.5, "max": 1.0, "recommended": 0.8},
    "Fuel Oil MDO": {"fluid": "MDO/DO",      "min": 0.8, "max": 1.5, "recommended": 1.2},
    "Fire & GS":    {"fluid": "Sea Water",   "min": 3.0, "max": 5.0, "recommended": 4.0},
    "Fresh Water":  {"fluid": "Fresh Water", "min": 1.0, "max": 2.5, "recommended": 1.8},
    "Cooling SW":   {"fluid": "Sea Water",   "min": 1.5, "max": 3.0, "recommended": 2.0},
    "Cooling FW":   {"fluid": "Fresh Water", "min": 1.0, "max": 2.5, "recommended": 1.8},
}

# ── Materials by system ─────────────────────────────────────────────────────
MATERIALS = {
    "Ballast":      {"material": "Carbon Steel (CS) + Epoxy Coating", "standard": "ASTM A53 / IS 1239", "note": "Hot-dip galvanized acceptable for smaller sizes"},
    "Bilge":        {"material": "Carbon Steel Galvanized (GI)", "standard": "IS 1239 / BS 1387", "note": "GRP acceptable for non-machinery spaces"},
    "Fuel Oil HFO": {"material": "Seamless Carbon Steel", "standard": "ASTM A106 Gr.B", "note": "Flanged joints only in machinery spaces - no screwed joints"},
    "Fuel Oil MDO": {"material": "Seamless Carbon Steel", "standard": "ASTM A106 Gr.B", "note": "Flanged joints only in machinery spaces"},
    "Fire & GS":    {"material": "Galvanized Iron (GI) / CS with coating", "standard": "IS 1239 / SOLAS Reg.", "note": "Fire main must be tested to 1.5× working pressure"},
    "Fresh Water":  {"material": "Copper-Nickel 90/10 or SS 316", "standard": "ASTM B466 / ASTM A312", "note": "Avoid galvanized for potable water"},
    "Cooling SW":   {"material": "Copper-Nickel 90/10 (Cu-Ni)", "standard": "ASTM B466", "note": "Cu-Ni preferred for sea water corrosion resistance"},
    "Cooling FW":   {"material": "Carbon Steel (CS)", "standard": "ASTM A53", "note": "Closed circuit - CS acceptable with inhibitor treatment"},
}

# ── Schedule recommendation by system working pressure ─────────────────────
def recommended_schedule(system: str, pressure_bar: float) -> str:
    if pressure_bar <= 10:
        return "SCH 40"
    elif pressure_bar <= 20:
        return "SCH 80"
    else:
        return "SCH 160"

# ── BOM component lists by system ──────────────────────────────────────────
SYSTEM_COMPONENTS = {
    "Ballast": [
        ("Sea Chest (Low)", 1, "set", "Cast iron / bronze body, grating"),
        ("Sea Chest (High)", 1, "set", "Emergency suction"),
        ("Kingston Valve (Sea Inlet)", 2, "no.", "Bronze, flanged, PN16"),
        ("Sea Chest Strainer", 2, "no.", "Bronze, Y-type or basket"),
        ("Ballast Pump", 2, "no.", "Centrifugal, self-priming"),
        ("Pump Inlet Strainer", 2, "no.", "Duplex basket strainer"),
        ("Gate Valve (Isolation)", 8, "no.", "CS/CI, flanged, PN16"),
        ("Butterfly Valve (Tank Suction)", 6, "no.", "CS, lug type, PN16"),
        ("Non-Return Valve (NRV)", 4, "no.", "Swing check, flanged"),
        ("Gate Valve (Tank Vent)", 4, "no.", "CS, flanged"),
        ("Air Pipe Head", 6, "no.", "Weathertight, self-closing"),
        ("Sounding Pipe with Cock", 6, "no.", "With self-closing device"),
        ("Pressure Gauge", 4, "no.", "0-10 bar, glycerin filled"),
        ("Flow Meter", 1, "no.", "Electromagnetic, flanged"),
        ("Manifold / Distribution Box", 1, "set", "CS fabricated"),
        ("Pipe Supports / Hangers", 1, "lot", "As per routing"),
        ("Expansion Bellows", 2, "no.", "Rubber, flanged"),
    ],
    "Bilge": [
        ("Bilge Pump (Main)", 2, "no.", "Self-priming centrifugal"),
        ("Emergency Bilge Pump", 1, "no.", "Portable / fixed submersible"),
        ("Strum Box (Bilge Suction)", 6, "no.", "Per bilge well"),
        ("Bilge Main Cock", 1, "no.", "Bronze, 3-way"),
        ("Gate Valve (Suction)", 6, "no.", "CS/bronze, flanged"),
        ("Non-Return Valve", 4, "no.", "Swing check, flanged"),
        ("Bilge Ejector", 1, "no.", "For emergency bilge suction"),
        ("Bilge Level Sensor / Float Switch", 6, "no.", "Per bilge well"),
        ("High Bilge Level Alarm", 1, "set", "Panel mounted"),
        ("Bilge Separator / OWS", 1, "no.", "15 ppm, MARPOL compliant"),
        ("Sludge Tank Valve", 2, "no.", "Gate valve, CS"),
        ("Overboard Discharge Valve", 2, "no.", "With MARPOL locking"),
        ("Pressure Gauge", 2, "no.", "0-6 bar"),
        ("Pipe Supports / Hangers", 1, "lot", "As per routing"),
    ],
    "Fuel Oil HFO": [
        ("HFO Storage Tank Valve", 4, "no.", "Quick-closing, remote operated"),
        ("HFO Transfer Pump", 2, "no.", "Gear pump, heated"),
        ("HFO Service Pump", 2, "no.", "Gear pump, heated"),
        ("HFO Duplex Filter / Strainer", 2, "set", "Self-cleaning, 50 micron"),
        ("HFO Flow Meter", 2, "no.", "Mass flow, Coriolis type"),
        ("HFO Heater (Steam/Electric)", 2, "no.", "Shell & tube / electric"),
        ("HFO Viscosity Controller", 1, "no.", "Automatic, inline"),
        ("HFO Pressure Control Valve", 2, "no.", "Self-actuating"),
        ("HFO Overflow / Return Valve", 2, "no.", "Float controlled"),
        ("Quick-Closing Valve (Actuated)", 6, "no.", "Remote operation from bridge"),
        ("Drip Tray with Drain Valve", 1, "lot", "Under all HFO equipment"),
        ("Fuel Oil Purifier", 2, "no.", "Centrifugal disc type"),
        ("Sludge Pump", 1, "no.", "For purifier sludge"),
        ("Pressure Gauge", 6, "no.", "0-16 bar, glycerin"),
        ("Temperature Gauge", 4, "no.", "0-200°C"),
        ("Pipe Supports / Hangers", 1, "lot", "Insulated as required"),
        ("Flanged Joints (all)", 1, "lot", "No screwed joints in machinery spaces"),
    ],
    "Fuel Oil MDO": [
        ("MDO Storage Tank Valve", 2, "no.", "Quick-closing, remote operated"),
        ("MDO Service Pump", 2, "no.", "Gear pump"),
        ("MDO Duplex Filter", 2, "set", "10 micron, duplex"),
        ("MDO Flow Meter", 1, "no.", "Volumetric or Coriolis"),
        ("MDO Pressure Control Valve", 2, "no.", "Self-actuating"),
        ("MDO Return Valve", 1, "no.", ""),
        ("Quick-Closing Valve (Actuated)", 4, "no.", "Remote from bridge"),
        ("Pressure Gauge", 4, "no.", "0-10 bar"),
        ("Drip Tray", 1, "lot", "Under all MDO equipment"),
        ("Pipe Supports / Hangers", 1, "lot", ""),
    ],
    "Fire & GS": [
        ("Fire Main Pump (Main)", 2, "no.", "Centrifugal, SOLAS compliant"),
        ("Emergency Fire Pump", 1, "no.", "Independent, diesel driven"),
        ("Fire Hydrant with Valve & Hose", 1, "lot", "Per SOLAS - 1 per 30m"),
        ("Hose Box with 15m Hose & Nozzle", 1, "lot", "Port & Starboard per deck"),
        ("International Shore Connection", 2, "no.", "Per SOLAS II-2 Reg.19"),
        ("Sea Chest (Fire Main)", 1, "set", "Dedicated or shared"),
        ("Kingston Valve", 2, "no.", "Bronze, flanged"),
        ("Isolating Valve (Section)", 6, "no.", "Gate valve, CS, PN16"),
        ("Non-Return Valve", 4, "no.", "Swing check"),
        ("GS Pump", 2, "no.", "Centrifugal, multi-purpose"),
        ("Pressure Gauge (Fire Main)", 4, "no.", "0-16 bar"),
        ("Fire Detection Panel Connection", 1, "set", "Pressure switch to alarm"),
        ("Foam System (if applicable)", 1, "lot", "Proportioner + monitors"),
        ("CO2 Fixed System (if applicable)", 1, "lot", "For machinery spaces"),
        ("Pipe Supports / Hangers", 1, "lot", ""),
    ],
    "Fresh Water": [
        ("FW Generator (Evaporator)", 1, "no.", "Plate type, IMO certified"),
        ("FW Storage Tank Valve", 4, "no.", "Gate valve, SS/GI"),
        ("FW Transfer Pump", 2, "no.", "Centrifugal"),
        ("FW Hydrophore Unit (Pressure Pump)", 1, "set", "With pressure vessel & controls"),
        ("FW Chlorinator / UV Sterilizer", 1, "no.", "SOLAS compliant"),
        ("FW Filter (Activated Carbon)", 1, "no.", "For potable water"),
        ("FW Flow Meter", 1, "no.", "Volumetric"),
        ("FW Pressure Reducing Valve", 2, "no.", "For distribution network"),
        ("FW Non-Return Valve", 4, "no.", "Swing check, SS"),
        ("Air Pipe Head (FW Tank)", 2, "no.", "Weathertight"),
        ("Sounding Pipe with Cock", 2, "no.", "With self-closing device"),
        ("FW Analysis Kit Connection", 1, "set", "Sampling point"),
        ("Pressure Gauge", 4, "no.", "0-10 bar"),
        ("Pipe Supports / Hangers", 1, "lot", ""),
    ],
    "Cooling SW": [
        ("Sea Chest (Cooling)", 1, "set", "Low / high sea chest"),
        ("SW Cooling Pump", 2, "no.", "Centrifugal, main & standby"),
        ("Central Cooler (SW Side)", 1, "no.", "Plate heat exchanger"),
        ("Auto Back-flush SW Strainer", 2, "no.", "Automatic self-cleaning"),
        ("Kingston Valve", 2, "no.", "Bronze, flanged"),
        ("Overboard Discharge Valve", 2, "no.", "CS, flanged"),
        ("Sea Water Temperature Sensor", 2, "no.", "Inlet & outlet"),
        ("Pressure Gauge", 4, "no.", "0-10 bar"),
        ("Non-Return Valve", 2, "no.", "Swing check"),
        ("Isolating Valve", 6, "no.", "Gate valve, CS"),
        ("Pipe Supports / Hangers", 1, "lot", ""),
    ],
    "Cooling FW": [
        ("FW Cooling Pump", 2, "no.", "Centrifugal, main & standby"),
        ("Central Cooler (FW Side)", 1, "no.", "Plate heat exchanger"),
        ("FW Expansion Tank", 1, "no.", "With level gauge & alarm"),
        ("3-Way Temperature Control Valve", 2, "no.", "Automatic, thermostat controlled"),
        ("FW Cooling Heater (Preheater)", 1, "no.", "Steam or electric"),
        ("Pressure Cap / Deaerator", 1, "no.", "For closed circuit"),
        ("Inhibitor Dosing Pump", 1, "no.", "Corrosion inhibitor injection"),
        ("FW Temperature Sensor", 4, "no.", "Inlet/outlet per cooler"),
        ("Pressure Gauge", 4, "no.", "0-6 bar"),
        ("Non-Return Valve", 2, "no.", "Swing check"),
        ("Isolating Valve", 6, "no.", "Gate valve, CS"),
        ("Pipe Supports / Hangers", 1, "lot", ""),
    ],
}

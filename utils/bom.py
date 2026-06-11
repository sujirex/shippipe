"""
Bill of Materials (BOM) generation for marine piping systems.
"""
import pandas as pd
from utils.systems_data import SYSTEM_COMPONENTS, MATERIALS


def generate_bom(system: str, flow_m3h: float, vessel_length_m: float) -> pd.DataFrame:
    """
    Generate component BOM for a given system.
    Adjusts quantities for vessel size where applicable.
    """
    components = SYSTEM_COMPONENTS.get(system, [])
    rows = []
    scale = max(1, round(vessel_length_m / 100))  # scale factor for larger vessels

    for item in components:
        desc, qty, unit, spec = item
        # Scale hydrant count for fire system based on vessel length
        if system == "Fire & GS" and "Hydrant" in desc:
            qty = max(2, round(vessel_length_m / 30))
        # Scale bilge wells for vessel length
        if system == "Bilge" and "Strum" in desc:
            qty = max(4, round(vessel_length_m / 25))
        # Scale tank valves / sounding pipes for larger vessels
        if unit == "lot":
            qty = 1
        rows.append({
            "Item": desc,
            "Qty": qty,
            "Unit": unit,
            "Specification / Notes": spec,
        })

    df = pd.DataFrame(rows)
    df.index = range(1, len(df) + 1)
    df.index.name = "No."
    return df


def material_spec(system: str) -> dict:
    return MATERIALS.get(system, {"material": "Carbon Steel", "standard": "ASTM A53", "note": ""})

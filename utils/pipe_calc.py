"""
Pipe sizing calculations for marine piping systems.
Methods: ASME B36.10 pipe selection, Darcy-Weisbach pressure drop.
"""
import math
import numpy as np
from utils.systems_data import PIPE_SIZES, FLUID_PROPERTIES


def flow_m3s(flow_m3h: float) -> float:
    return flow_m3h / 3600.0


def required_id(flow_m3h: float, velocity_ms: float) -> float:
    """Return required internal diameter (mm) for given flow and velocity."""
    Q = flow_m3s(flow_m3h)
    area = Q / velocity_ms          # m²
    id_m = math.sqrt(4 * area / math.pi)
    return id_m * 1000              # mm


def select_pipe(required_id_mm: float, schedule: str = "SCH 40"):
    """
    Select smallest standard pipe whose ID >= required ID.
    Returns dict with NPS, OD, wall, ID, flow_area.
    """
    results = []
    for nps, data in PIPE_SIZES.items():
        OD = data["OD"]
        wall = data["schedules"].get(schedule, data["schedules"].get("SCH 40"))
        ID = OD - 2 * wall
        if ID >= required_id_mm:
            results.append((nps, OD, wall, ID))
    if not results:
        # return largest available
        nps = list(PIPE_SIZES.keys())[-1]
        OD = PIPE_SIZES[nps]["OD"]
        wall = PIPE_SIZES[nps]["schedules"].get(schedule, list(PIPE_SIZES[nps]["schedules"].values())[0])
        ID = OD - 2 * wall
        return {"nps": nps, "OD": OD, "wall": wall, "ID": ID,
                "flow_area_m2": math.pi * (ID / 1000) ** 2 / 4}
    nps, OD, wall, ID = results[0]
    return {"nps": nps, "OD": OD, "wall": wall, "ID": ID,
            "flow_area_m2": math.pi * (ID / 1000) ** 2 / 4}


def actual_velocity(flow_m3h: float, pipe_id_mm: float) -> float:
    """Actual flow velocity in m/s."""
    Q = flow_m3s(flow_m3h)
    area = math.pi * (pipe_id_mm / 1000) ** 2 / 4
    return Q / area if area > 0 else 0


def reynolds_number(velocity: float, pipe_id_mm: float, fluid: str) -> float:
    props = FLUID_PROPERTIES[fluid]
    return (props["density"] * velocity * (pipe_id_mm / 1000)) / props["viscosity"]


def friction_factor(Re: float, roughness_mm: float, pipe_id_mm: float) -> float:
    """Colebrook-White equation (iterative)."""
    if Re < 2300:
        return 64 / Re if Re > 0 else 0.02
    e_D = roughness_mm / pipe_id_mm
    # Initial guess (Swamee-Jain)
    f = 0.25 / (math.log10(e_D / 3.7 + 5.74 / Re ** 0.9)) ** 2
    for _ in range(50):
        f_new = (-2 * math.log10(e_D / 3.7 + 2.51 / (Re * math.sqrt(f)))) ** (-2)
        if abs(f_new - f) < 1e-8:
            break
        f = f_new
    return f


def pressure_drop(flow_m3h: float, pipe_id_mm: float, length_m: float,
                  fluid: str, fittings_equiv_length: float = 0.0) -> dict:
    """
    Darcy-Weisbach pressure drop.
    Returns pressure drop in Pa and bar, velocity, Re, friction factor.
    """
    props = FLUID_PROPERTIES[fluid]
    v = actual_velocity(flow_m3h, pipe_id_mm)
    Re = reynolds_number(v, pipe_id_mm, fluid)
    roughness = props["roughness"]
    f = friction_factor(Re, roughness, pipe_id_mm)
    L_total = length_m + fittings_equiv_length
    dP_Pa = f * (L_total / (pipe_id_mm / 1000)) * (props["density"] * v ** 2 / 2)
    return {
        "velocity_ms": round(v, 3),
        "Re": round(Re, 0),
        "friction_factor": round(f, 5),
        "pressure_drop_Pa": round(dP_Pa, 1),
        "pressure_drop_bar": round(dP_Pa / 1e5, 4),
        "pressure_drop_mH2O": round(dP_Pa / (props["density"] * 9.81), 3),
    }


def pipe_weight_per_m(OD_mm: float, wall_mm: float, density_kg_m3: float = 7850) -> float:
    """Pipe weight per metre (kg/m) - steel default density 7850 kg/m³."""
    OD = OD_mm / 1000
    ID = (OD_mm - 2 * wall_mm) / 1000
    area = math.pi / 4 * (OD ** 2 - ID ** 2)
    return round(area * density_kg_m3, 2)


def pipe_summary(flow_m3h: float, velocity_ms: float, pipe_length_m: float,
                 schedule: str, fluid: str, pressure_bar: float) -> dict:
    """Full pipe sizing summary for one line."""
    req_id = required_id(flow_m3h, velocity_ms)
    pipe = select_pipe(req_id, schedule)
    v_actual = actual_velocity(flow_m3h, pipe["ID"])
    fittings_eq = pipe_length_m * 0.30  # 30% addition for fittings
    dp = pressure_drop(flow_m3h, pipe["ID"], pipe_length_m, fluid, fittings_eq)
    weight = pipe_weight_per_m(pipe["OD"], pipe["wall"])
    return {
        "required_id_mm": round(req_id, 1),
        "selected_nps": pipe["nps"],
        "OD_mm": pipe["OD"],
        "wall_mm": pipe["wall"],
        "ID_mm": round(pipe["ID"], 2),
        "schedule": schedule,
        "actual_velocity_ms": round(v_actual, 2),
        "Re": dp["Re"],
        "pressure_drop_bar": dp["pressure_drop_bar"],
        "pressure_drop_mH2O": dp["pressure_drop_mH2O"],
        "pipe_weight_kg_m": weight,
        "total_weight_kg": round(weight * pipe_length_m, 1),
    }

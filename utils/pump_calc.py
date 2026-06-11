"""
Pump sizing calculations for marine piping systems.
"""
import math
from utils.systems_data import FLUID_PROPERTIES


def total_head(static_head_m: float, friction_loss_mH2O: float,
               velocity_head_m: float = 0.0, safety_factor: float = 1.1) -> float:
    """Total pump head in metres."""
    H = (static_head_m + friction_loss_mH2O + velocity_head_m) * safety_factor
    return round(H, 2)


def motor_power_kw(flow_m3h: float, head_m: float, fluid: str,
                   pump_eff: float = 0.72, motor_eff: float = 0.92) -> float:
    """Shaft power and motor power in kW."""
    rho = FLUID_PROPERTIES[fluid]["density"]
    g = 9.81
    Q = flow_m3h / 3600
    hydraulic_power = rho * g * Q * head_m          # W
    shaft_power = hydraulic_power / pump_eff         # W
    motor_power = shaft_power / motor_eff            # W
    return round(motor_power / 1000, 2)              # kW


def select_pump_type(system: str) -> dict:
    mapping = {
        "Ballast":      {"type": "Centrifugal (self-priming)", "drive": "Electric motor", "note": "Main & standby - identical units"},
        "Bilge":        {"type": "Centrifugal (self-priming)", "drive": "Electric motor", "note": "Must handle solids up to 10mm - consider submersible for emergency"},
        "Fuel Oil HFO": {"type": "Gear pump (positive displacement)", "drive": "Electric motor with VFD", "note": "Heated pump body for HFO viscosity - trace heating on suction"},
        "Fuel Oil MDO": {"type": "Gear pump (positive displacement)", "drive": "Electric motor", "note": ""},
        "Fire & GS":    {"type": "Centrifugal (single stage)", "drive": "Electric motor (emergency: diesel)", "note": "SOLAS: capacity ≥ 2 hydrants simultaneously at 0.25 N/mm²"},
        "Fresh Water":  {"type": "Centrifugal (hydrophore set)", "drive": "Electric motor", "note": "Pressure vessel with bladder - maintains 2.5-4 bar at outlets"},
        "Cooling SW":   {"type": "Centrifugal (single stage)", "drive": "Electric motor", "note": "Main & standby - consider titanium impeller for sea water"},
        "Cooling FW":   {"type": "Centrifugal (single stage)", "drive": "Electric motor", "note": "Closed-circuit - standard CS casing acceptable"},
    }
    return mapping.get(system, {"type": "Centrifugal", "drive": "Electric motor", "note": ""})


def npshr_check(suction_head_m: float, friction_suction_mH2O: float,
                fluid: str, vapour_pressure_kPa: float = 3.2) -> dict:
    """
    Available NPSH check.
    vapour_pressure_kPa: ~3.2 kPa for sea water @ 25°C
    """
    rho = FLUID_PROPERTIES[fluid]["density"]
    g = 9.81
    atm_pressure_m = 101325 / (rho * g)    # ~10.1 m for sea water
    NPSHA = atm_pressure_m + suction_head_m - friction_suction_mH2O - (vapour_pressure_kPa * 1000) / (rho * g)
    status = "OK - Adequate" if NPSHA > 2.0 else "Check pump NPSHR - low margin"
    return {"NPSHA_m": round(NPSHA, 2), "status": status}


def pump_summary(flow_m3h: float, static_head_m: float,
                 friction_loss_mH2O: float, system: str, fluid: str,
                 pump_eff: float = 0.72) -> dict:
    """Complete pump specification summary."""
    H = total_head(static_head_m, friction_loss_mH2O)
    P = motor_power_kw(flow_m3h, H, fluid, pump_eff)
    pump_type = select_pump_type(system)
    npsh = npshr_check(static_head_m * 0.3, friction_loss_mH2O * 0.2, fluid)
    return {
        "flow_rate_m3h": flow_m3h,
        "total_head_m": H,
        "motor_power_kw": P,
        "recommended_motor_kw": next(
            kw for kw in [0.37,0.55,0.75,1.1,1.5,2.2,3.0,4.0,5.5,7.5,
                          11,15,18.5,22,30,37,45,55,75,90,110,132,160,200]
            if kw >= P
        ),
        "pump_type": pump_type["type"],
        "drive": pump_type["drive"],
        "note": pump_type["note"],
        "NPSHA_m": npsh["NPSHA_m"],
        "npsh_status": npsh["status"],
        "pump_efficiency_pct": int(pump_eff * 100),
    }

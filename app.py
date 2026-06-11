"""
ShipPipe — Marine Piping System Designer
Suji Kumar C | pipe.sujikumar.com
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from utils.pipe_calc import pipe_summary, required_id
from utils.pump_calc import pump_summary
from utils.bom import generate_bom, material_spec
from utils.export import to_excel, to_pdf
from utils.systems_data import VELOCITY_RANGES, MATERIALS, PIPE_SIZES, recommended_schedule

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ShipPipe — Marine Piping System Designer",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .block-container { padding-top: 1.5rem; }
  .stTabs [data-baseweb="tab-list"] { gap: 4px; }
  .stTabs [data-baseweb="tab"] {
    padding: 8px 18px;
    border-radius: 6px 6px 0 0;
    font-weight: 600;
    font-size: 0.85rem;
  }
  .result-card {
    background: rgba(0,180,220,0.07);
    border: 1px solid rgba(0,180,220,0.25);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
  }
  .metric-label { font-size: 0.75rem; color: #94a3b8; margin-bottom: 2px; }
  .metric-value { font-size: 1.3rem; font-weight: 700; color: #e2e8f0; }
  .metric-unit  { font-size: 0.75rem; color: #64748b; margin-left: 4px; }
  .section-title {
    font-size: 1.1rem; font-weight: 700;
    color: #00b4dc; border-left: 3px solid #00b4dc;
    padding-left: 10px; margin: 1rem 0 0.6rem 0;
  }
  footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚢 ShipPipe")
    st.markdown("**Marine Piping System Designer**")
    st.markdown("---")

    st.markdown("### Vessel / Project Info")
    vessel_name  = st.text_input("Vessel / Project Name", value="MV Example")
    vessel_loa   = st.number_input("Length Overall (m)", 50.0, 400.0, 120.0, 5.0)
    vessel_dwt   = st.number_input("Deadweight (DWT)", 500, 200000, 5000, 500)
    vessel_draft = st.number_input("Design Draft (m)", 2.0, 25.0, 6.5, 0.5)

    st.markdown("---")
    st.markdown("### Global Settings")
    default_schedule = st.selectbox("Pipe Schedule", ["SCH 40", "SCH 80", "SCH 160"], index=0)
    pump_efficiency  = st.slider("Pump Efficiency (%)", 60, 85, 72) / 100

    st.markdown("---")
    st.markdown("**Built by [Suji Kumar C](https://sujikumar.com)**")
    st.markdown("Marine Software Engineer")
    st.caption("pipe.sujikumar.com")


# ── Helper: velocity gauge ──────────────────────────────────────────────────
def velocity_gauge(v_actual, v_min, v_max, v_rec, title="Flow Velocity"):
    fig, ax = plt.subplots(figsize=(4, 0.6))
    fig.patch.set_facecolor("#0f2040")
    ax.set_facecolor("#0f2040")
    # background bar
    ax.barh(0, v_max * 1.2, height=0.5, color="#1e3a5f", left=0)
    # green zone
    ax.barh(0, v_max - v_min, height=0.5, color="#10b981", left=v_min, alpha=0.4)
    # actual value
    color = "#00b4dc" if v_min <= v_actual <= v_max else "#ef4444"
    ax.barh(0, v_actual, height=0.5, color=color, left=0)
    ax.axvline(v_rec, color="#f59e0b", linewidth=1.5, linestyle="--")
    ax.set_xlim(0, v_max * 1.2)
    ax.set_yticks([])
    ax.tick_params(axis="x", colors="#94a3b8", labelsize=7)
    ax.spines[:].set_visible(False)
    ax.set_title(f"{title}: {v_actual:.2f} m/s", color="#e2e8f0", fontsize=8, pad=2)
    plt.tight_layout(pad=0.2)
    return fig


# ── Helper: render results ──────────────────────────────────────────────────
def render_system(system_key: str, system_label: str):
    vrange = VELOCITY_RANGES[system_key]
    fluid  = vrange["fluid"]

    st.markdown(f"### {system_label} System Designer")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.markdown('<div class="section-title">Flow Requirements</div>', unsafe_allow_html=True)
        flow_rate   = st.number_input("Flow Rate (m³/h)", 1.0, 5000.0,
                                       float(vessel_dwt / 800 * 10), 5.0,
                                       key=f"{system_key}_flow")
        pipe_length = st.number_input("Pipe Length (m)", 5.0, 500.0, 50.0, 5.0,
                                       key=f"{system_key}_len")
        static_head = st.number_input("Static Head (m)", 0.0, 50.0, 8.0, 0.5,
                                       key=f"{system_key}_head")
        velocity    = st.slider(
            f"Design Velocity (m/s)  [rec: {vrange['recommended']} m/s]",
            vrange["min"], vrange["max"], vrange["recommended"], 0.1,
            key=f"{system_key}_vel"
        )
        design_pressure = st.number_input("Design Pressure (bar)", 1.0, 40.0, 7.0, 0.5,
                                           key=f"{system_key}_pres")
        schedule = recommended_schedule(system_key, design_pressure)

    # Run calculations
    pipe = pipe_summary(flow_rate, velocity, pipe_length, schedule, fluid, design_pressure)
    pump = pump_summary(flow_rate, static_head, pipe["pressure_drop_mH2O"],
                        system_key, fluid, pump_efficiency)
    bom  = generate_bom(system_key, flow_rate, vessel_loa)
    mat  = material_spec(system_key)

    with col2:
        st.markdown('<div class="section-title">Pipe Sizing Results</div>', unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        m1.metric("Selected Pipe", pipe["selected_nps"])
        m2.metric("Pipe Schedule", pipe["schedule"])
        m1.metric("OD", f"{pipe['OD_mm']} mm")
        m2.metric("ID", f"{pipe['ID_mm']} mm")
        m1.metric("Wall Thickness", f"{pipe['wall_mm']} mm")
        m2.metric("Weight/m", f"{pipe['pipe_weight_kg_m']} kg/m")

        st.pyplot(velocity_gauge(
            pipe["actual_velocity_ms"],
            vrange["min"], vrange["max"], vrange["recommended"]
        ), use_container_width=False)

        st.markdown(f"""
        | Parameter | Value |
        |-----------|-------|
        | Required ID | {pipe['required_id_mm']} mm |
        | Actual Velocity | **{pipe['actual_velocity_ms']} m/s** |
        | Reynolds Number | {int(pipe['Re']):,} |
        | Pressure Drop | {pipe['pressure_drop_bar']} bar ({pipe['pressure_drop_mH2O']} mH₂O) |
        | Total Pipe Weight | {pipe['total_weight_kg']} kg |
        """)

        st.info(f"**Material:** {mat['material']}  \n**Standard:** {mat['standard']}  \n{mat['note']}")

    with col3:
        st.markdown('<div class="section-title">Pump Specification</div>', unsafe_allow_html=True)
        p1, p2 = st.columns(2)
        p1.metric("Total Head", f"{pump['total_head_m']} m")
        p2.metric("Motor Power", f"{pump['motor_power_kw']} kW")
        p1.metric("Std Motor", f"{pump['recommended_motor_kw']} kW")
        p2.metric("NPSHA", f"{pump['NPSHA_m']} m")

        st.markdown(f"""
        | Parameter | Value |
        |-----------|-------|
        | Flow Rate | {pump['flow_rate_m3h']} m³/h |
        | Total Head | {pump['total_head_m']} m |
        | Motor Power (calc) | {pump['motor_power_kw']} kW |
        | Recommended Motor | **{pump['recommended_motor_kw']} kW** |
        | Pump Type | {pump['pump_type']} |
        | Drive | {pump['drive']} |
        | NPSH Available | {pump['NPSHA_m']} m — {pump['npsh_status']} |
        | Efficiency | {pump['pump_efficiency_pct']}% |
        """)

        if pump["note"]:
            st.warning(pump["note"])

    # BOM table
    st.markdown('<div class="section-title">Bill of Materials</div>', unsafe_allow_html=True)
    st.dataframe(bom, use_container_width=True, height=320)

    # Export buttons
    st.markdown('<div class="section-title">Export</div>', unsafe_allow_html=True)
    ecol1, ecol2 = st.columns(2)

    with ecol1:
        excel_data = to_excel(pipe, pump, bom, system_label, vessel_name)
        st.download_button(
            label="📥 Download Excel Spec Sheet",
            data=excel_data,
            file_name=f"ShipPipe_{system_key.replace(' ', '_')}_{vessel_name.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    with ecol2:
        pdf_data = to_pdf(pipe, pump, bom, system_label, vessel_name)
        st.download_button(
            label="📄 Download PDF Spec Sheet",
            data=pdf_data,
            file_name=f"ShipPipe_{system_key.replace(' ', '_')}_{vessel_name.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


# ── Main header ────────────────────────────────────────────────────────────────
st.markdown("# 🚢 ShipPipe")
st.markdown("**Marine Piping System Designer** — Pipe sizing, pump specification, BOM & export for all major ship systems")
st.markdown("---")

# ── Tabs ───────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "⚓ Ballast",
    "💧 Bilge",
    "🛢 Fuel Oil HFO",
    "⛽ Fuel Oil MDO",
    "🔥 Fire & GS",
    "🚰 Fresh Water",
    "❄️ Cooling SW",
    "🌊 Cooling FW",
    "📋 About",
])

with tabs[0]:
    render_system("Ballast", "Ballast")

with tabs[1]:
    render_system("Bilge", "Bilge")

with tabs[2]:
    render_system("Fuel Oil HFO", "Fuel Oil HFO")

with tabs[3]:
    render_system("Fuel Oil MDO", "Fuel Oil MDO")

with tabs[4]:
    render_system("Fire & GS", "Fire & GS")

with tabs[5]:
    render_system("Fresh Water", "Fresh Water")

with tabs[6]:
    render_system("Cooling SW", "Cooling SW")

with tabs[7]:
    render_system("Cooling FW", "Cooling FW")

with tabs[8]:
    st.markdown("## About ShipPipe")
    st.markdown("""
**ShipPipe** is a marine piping system design tool built by **Suji Kumar C**, Marine Software Engineer at Shoft Shipyard, Gujarat.

### What it does
- Sizes pipes for all major shipboard systems using ASME B36.10 standard pipe schedules
- Calculates flow velocity, Reynolds number, and pressure drop using the Darcy-Weisbach equation
- Specifies pumps with total head, motor power, and NPSH check
- Generates a complete Bill of Materials for each system
- Exports results as Excel or PDF spec sheets

### Systems Covered
| System | Fluid | Typical Velocity |
|--------|-------|-----------------|
| Ballast | Sea Water | 1.5 – 3.0 m/s |
| Bilge | Sea Water | 1.0 – 2.5 m/s |
| Fuel Oil HFO | Heavy Fuel Oil | 0.5 – 1.0 m/s |
| Fuel Oil MDO | Marine Diesel Oil | 0.8 – 1.5 m/s |
| Fire & GS | Sea Water | 3.0 – 5.0 m/s |
| Fresh Water | Fresh Water | 1.0 – 2.5 m/s |
| Cooling SW | Sea Water | 1.5 – 3.0 m/s |
| Cooling FW | Fresh Water | 1.0 – 2.5 m/s |

### Engineering References
- Pipe schedules: **ASME B36.10M**
- Pressure drop: **Darcy-Weisbach** + Colebrook-White friction factor
- Pump sizing: Class society guidelines + 10% safety factor on total head
- Fire system capacity: **SOLAS II-2** requirements
- Fuel oil piping: **SOLAS II-2 Reg. 4** (flanged joints only in machinery spaces)

### About the Developer
**Suji Kumar C** — Marine Software Engineer with 13+ years across every layer of a shipyard:
electrical systems, hull production, nesting technology, IT infrastructure, and software development.

🌐 [sujikumar.com](https://sujikumar.com) · 💼 [LinkedIn](https://linkedin.com/in/sujikumar)
    """)

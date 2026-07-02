"""
ShipPipe v2 - Marine Piping System Designer
Suji Kumar C | pipe.sujikumar.com
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import numpy as np
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

from utils.pipe_calc import pipe_summary, required_id
from utils.pump_calc import pump_summary
from utils.bom import generate_bom, material_spec
from utils.export import to_excel, to_pdf
from utils.systems_data import VELOCITY_RANGES, MATERIALS, recommended_schedule

st.set_page_config(
    page_title="ShipPipe -- Marine Piping Designer",
    page_icon="favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -- Session State
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "system_results" not in st.session_state:
    st.session_state.system_results = {}

# -- Gate Valve SVG (P&ID symbol)
def valve_svg(color: str, size: int = 52) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 52 52" xmlns="http://www.w3.org/2000/svg">
  <line x1="0" y1="26" x2="8" y2="26" stroke="{color}" stroke-width="4" stroke-linecap="round"/>
  <line x1="44" y1="26" x2="52" y2="26" stroke="{color}" stroke-width="4" stroke-linecap="round"/>
  <polygon points="8,14 8,38 24,26" fill="{color}"/>
  <polygon points="44,14 44,38 28,26" fill="{color}"/>
  <line x1="24" y1="26" x2="28" y2="26" stroke="{color}" stroke-width="2.5"/>
  <line x1="26" y1="14" x2="26" y2="5" stroke="{color}" stroke-width="2.5" stroke-linecap="round"/>
  <circle cx="26" cy="5" r="7" stroke="{color}" stroke-width="2.2" fill="none"/>
  <line x1="19" y1="5" x2="33" y2="5" stroke="{color}" stroke-width="1.8"/>
  <line x1="26" y1="0" x2="26" y2="10" stroke="{color}" stroke-width="1.8"/>
</svg>"""

# -- Theme
def get_theme():
    if st.session_state.dark_mode:
        return dict(
            bg        = "#060d1a",
            bg2       = "#0a1628",
            card      = "#0d1f3c",
            card2     = "#0f2545",
            border    = "rgba(0,212,255,0.18)",
            glow      = "rgba(0,212,255,0.08)",
            primary   = "#00d4ff",
            primary2  = "#0099cc",
            text      = "#ffffff",
            text2     = "#94b8d0",
            muted     = "#4a7fa0",
            success   = "#00e5a0",
            danger    = "#ff4d6d",
            sel_text  = "#060d1a",
            chart_bg  = "#0a1628",
            c1        = "#00d4ff",
            c2        = "#00e5a0",
            c3        = "#ff9f43",
            mode_btn  = "Light Mode",
        )
    return dict(
        bg        = "#f4f8fc",
        bg2       = "#e8f0f8",
        card      = "#ffffff",
        card2     = "#f0f6ff",
        border    = "rgba(0,100,180,0.18)",
        glow      = "rgba(0,100,180,0.04)",
        primary   = "#0066cc",
        primary2  = "#004fa3",
        text      = "#0a0e1a",
        text2     = "#3a5a7a",
        muted     = "#6b8fa8",
        success   = "#00875a",
        danger    = "#cc1f3a",
        sel_text  = "#ffffff",
        chart_bg  = "#f0f6ff",
        c1        = "#0066cc",
        c2        = "#00875a",
        c3        = "#d4600a",
        mode_btn  = "Dark Mode",
    )

T = get_theme()

# -- Global CSS
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"], .stApp, .stApp * {{
  font-family: 'Inter', sans-serif !important;
  box-sizing: border-box;
}}
h1,h2,h3,h4,h5,h6,
.stMarkdown h1,.stMarkdown h2,.stMarkdown h3 {{
  font-family: 'Space Grotesk', sans-serif !important;
}}

.stApp {{ background: {T["bg"]} !important; }}
.block-container {{ padding-top: 1rem !important; max-width: 1400px; }}

/* Sidebar */
section[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, {T["bg2"]} 0%, {T["bg"]} 100%) !important;
  border-right: 1px solid {T["border"]};
}}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {{
  color: {T["text"]} !important;
  font-family: 'Inter', sans-serif !important;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
  gap: 2px;
  background: {T["card"]} !important;
  border: 1px solid {T["border"]};
  padding: 5px 6px;
  border-radius: 12px;
  box-shadow: 0 2px 12px {T["glow"]};
}}
.stTabs [data-baseweb="tab"] {{
  padding: 7px 15px !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  font-size: 0.76rem !important;
  color: {T["text2"]} !important;
  letter-spacing: 0.01em;
  transition: all 0.15s ease;
  font-family: 'Space Grotesk', sans-serif !important;
}}
.stTabs [aria-selected="true"] {{
  background: linear-gradient(135deg, {T["primary"]}, {T["primary2"]}) !important;
  color: {T["sel_text"]} !important;
  box-shadow: 0 2px 10px rgba(0,180,220,0.3);
}}
.stTabs [data-baseweb="tab-panel"] {{ background: transparent !important; }}

/* Inputs */
input, select, textarea, .stSelectbox,
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {{
  background: {T["card"]} !important;
  border: 1px solid {T["border"]} !important;
  color: {T["text"]} !important;
  border-radius: 8px !important;
  font-family: 'Inter', sans-serif !important;
}}
.stSlider [data-baseweb="slider"] {{ margin-top: 4px; }}

/* Metrics */
[data-testid="stMetricLabel"] {{
  color: {T["muted"]} !important;
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}}
[data-testid="stMetricValue"] {{
  color: {T["primary"]} !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-weight: 800 !important;
  font-size: 1.5rem !important;
}}

/* Text */
p, li, td, th, .stMarkdown, .stMarkdown p {{
  color: {T["text"]} !important;
  font-family: 'Inter', sans-serif !important;
}}
h1,h2,h3,h4 {{ color: {T["text"]} !important; }}
caption, .stCaption {{ color: {T["text2"]} !important; }}

/* Tables */
.stDataFrame {{ border-radius: 12px !important; overflow: hidden; border: 1px solid {T["border"]}; }}
.stDataFrame th {{
  background: {T["card2"]} !important;
  color: {T["primary"]} !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-weight: 700 !important;
}}
.stDataFrame td {{ color: {T["text"]} !important; }}

/* Buttons */
.stDownloadButton > button {{
  background: linear-gradient(135deg, {T["primary"]}, {T["primary2"]}) !important;
  color: {T["sel_text"]} !important;
  border: none !important;
  border-radius: 9px !important;
  font-weight: 700 !important;
  font-size: 0.82rem !important;
  padding: 8px 16px !important;
  font-family: 'Space Grotesk', sans-serif !important;
  box-shadow: 0 3px 12px rgba(0,180,220,0.25);
  transition: all 0.15s ease;
}}
.stDownloadButton > button:hover {{
  box-shadow: 0 5px 18px rgba(0,180,220,0.4) !important;
  transform: translateY(-1px);
}}
.stButton > button {{
  background: {T["card"]} !important;
  color: {T["text"]} !important;
  border: 1.5px solid {T["primary"]} !important;
  border-radius: 9px !important;
  font-weight: 700 !important;
  font-family: 'Space Grotesk', sans-serif !important;
  transition: all 0.15s ease;
}}
.stButton > button:hover {{
  background: linear-gradient(135deg, {T["primary"]}, {T["primary2"]}) !important;
  color: {T["sel_text"]} !important;
}}

/* Alerts */
.stInfo, .stWarning, .stSuccess, .stError {{
  border-radius: 10px !important;
  border-left-width: 4px !important;
}}

/* Custom classes */
.sp-card {{
  background: {T["card"]};
  border: 1px solid {T["border"]};
  border-radius: 14px;
  padding: 16px 20px;
  box-shadow: 0 4px 20px {T["glow"]};
  margin-bottom: 10px;
}}
.sp-section-title {{
  font-family: 'Space Grotesk', sans-serif !important;
  font-size: 0.82rem;
  font-weight: 700;
  color: {T["primary"]};
  text-transform: uppercase;
  letter-spacing: 0.08em;
  border-left: 3px solid {T["primary"]};
  padding-left: 10px;
  margin: 16px 0 10px 0;
}}
.sp-kpi {{
  background: {T["card"]};
  border: 1px solid {T["border"]};
  border-top: 3px solid {T["primary"]};
  border-radius: 14px;
  padding: 16px;
  text-align: center;
  box-shadow: 0 4px 20px {T["glow"]};
  transition: box-shadow 0.2s;
}}
.sp-kpi:hover {{ box-shadow: 0 6px 28px rgba(0,180,220,0.2); }}
.sp-kpi-num {{
  font-family: 'Space Grotesk', sans-serif;
  font-size: 2.2rem;
  font-weight: 900;
  color: {T["primary"]};
  line-height: 1.1;
}}
.sp-kpi-lbl {{
  font-size: 0.68rem;
  color: {T["muted"]};
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-top: 4px;
}}
.sp-mat-badge {{
  display: inline-block;
  background: linear-gradient(135deg, {T["primary"]}22, {T["primary"]}11);
  border: 1px solid {T["primary"]}44;
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 0.8rem;
  color: {T["text"]};
  margin-top: 6px;
  line-height: 1.6;
}}

footer {{ visibility: hidden; }}
#MainMenu {{ visibility: hidden; }}
/* Remove Streamlit native header */
header[data-testid="stHeader"] {{ display: none !important; }}
[data-testid="stDecoration"]   {{ display: none !important; }}
[data-testid="stToolbar"]      {{ display: none !important; }}
.main .block-container {{ padding-top: 0.8rem !important; }}

/* File uploader - hide duplicate text, show single clean button */
[data-testid="stFileUploaderDropzone"] {{
    border: 1.5px dashed {T["primary"]}55 !important;
    border-radius: 10px !important;
    background: {T["card"]} !important;
    padding: 8px 10px !important;
}}
[data-testid="stFileUploaderDropzoneInstructions"] {{
    display: none !important;
}}
[data-testid="stFileUploaderDropzone"] button span,
[data-testid="stFileUploaderDropzone"] button p,
[data-testid="stFileUploaderDropzone"] button div {{
    display: none !important;
}}
[data-testid="stFileUploaderDropzone"] button {{
    background: linear-gradient(135deg, {T["primary"]}, {T["primary2"]}) !important;
    color: {T["sel_text"]} !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 5px 14px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    min-width: 90px !important;
}}
[data-testid="stFileUploaderDropzone"] button::after {{
    content: "Browse File";
    font-size: 0.76rem;
    font-weight: 700;
    font-family: 'Space Grotesk', sans-serif;
    color: {T["sel_text"]};
    display: block !important;
}}
/* Hide ALL Streamlit chrome */
[data-testid="stToolbar"] {{ display: none !important; }}
[data-testid="stToolbarActions"] {{ display: none !important; }}
[data-testid="stStatusWidget"] {{ display: none !important; }}
button[data-testid="baseButton-header"] {{ display: none !important; }}
/* Hide sidebar COLLAPSE button only - keep expand visible */
[data-testid="stSidebarCollapseButton"] {{ display: none !important; }}
button[aria-label="Collapse sidebar"] {{ display: none !important; }}
button[title="Collapse sidebar"] {{ display: none !important; }}
</style>
""", unsafe_allow_html=True)


# -- Sidebar
with st.sidebar:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:12px;padding:8px 0 4px;">'
        f'  {valve_svg(T["primary"], 44)}'
        f'  <div>'
        f'    <div style="font-family:Space Grotesk,sans-serif;font-size:1.35rem;font-weight:800;'
        f'         color:{T["primary"]};line-height:1.1;">ShipPipe</div>'
        f'    <div style="font-size:0.68rem;color:{T["muted"]};letter-spacing:0.06em;'
        f'         text-transform:uppercase;font-weight:600;">Marine Piping Designer</div>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True
    )
    st.markdown(f'<div style="height:1px;background:{T["border"]};margin:10px 0 14px;"></div>',
                unsafe_allow_html=True)

    if st.button(T["mode_btn"], use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    st.markdown(f'<div style="font-family:Space Grotesk,sans-serif;font-size:0.75rem;font-weight:700;'
                f'color:{T["muted"]};text-transform:uppercase;letter-spacing:0.07em;'
                f'margin:16px 0 6px;">Vessel / Project</div>', unsafe_allow_html=True)
    vessel_name  = st.text_input("Vessel Name",   value="MV Example",  label_visibility="collapsed")
    vessel_loa   = st.number_input("LOA (m)",      50.0, 400.0, 120.0, 5.0)
    vessel_dwt   = st.number_input("DWT",           500, 200000, 5000,  500)
    vessel_draft = st.number_input("Draft (m)",     2.0,  25.0,  6.5,   0.5)

    st.markdown(f'<div style="font-family:Space Grotesk,sans-serif;font-size:0.75rem;font-weight:700;'
                f'color:{T["muted"]};text-transform:uppercase;letter-spacing:0.07em;'
                f'margin:16px 0 6px;">Settings</div>', unsafe_allow_html=True)
    default_schedule = st.selectbox("Schedule", ["SCH 40","SCH 80","SCH 160"])
    pump_efficiency  = st.slider("Pump n (%)", 60, 85, 72) / 100

    st.markdown(f'<div style="font-family:Space Grotesk,sans-serif;font-size:0.75rem;font-weight:700;'
                f'color:{T["muted"]};text-transform:uppercase;letter-spacing:0.07em;'
                f'margin:16px 0 6px;">Import Template</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Vessel template (.xlsx)", type=["xlsx"])
    if uploaded:
        try:
            df_in = pd.read_excel(uploaded, sheet_name="Vessel Data")
            vessel_name  = str(df_in.iloc[0,1])
            vessel_loa   = float(df_in.iloc[1,1])
            vessel_dwt   = float(df_in.iloc[2,1])
            vessel_draft = float(df_in.iloc[3,1])
            st.success("Vessel data imported!")
        except Exception:
            st.error("Invalid template.")

    st.markdown(f'<div style="height:1px;background:{T["border"]};margin:14px 0 10px;"></div>',
                unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-size:0.72rem;color:{T["muted"]};text-align:center;">'
        f'Built by <a href="https://sujikumar.com" style="color:{T["primary"]};'
        f'text-decoration:none;font-weight:600;">Suji Kumar C</a></div>',
        unsafe_allow_html=True
    )


# -- Velocity Gauge
def velocity_gauge(v_actual, v_min, v_max, v_rec):
    bg = T["chart_bg"]
    tc = T["text"]
    fig, ax = plt.subplots(figsize=(4.5, 0.6))
    fig.patch.set_facecolor(bg); ax.set_facecolor(bg)
    ax.barh(0, v_max*1.25, height=0.45,
            color="#0d1f3c" if st.session_state.dark_mode else "#dce8f5", left=0)
    ax.barh(0, v_max-v_min, height=0.45, color=T["success"], left=v_min, alpha=0.28)
    color = T["primary"] if v_min<=v_actual<=v_max else T["danger"]
    ax.barh(0, v_actual, height=0.45, color=color, alpha=0.9)
    ax.axvline(v_rec, color="#ffffff" if st.session_state.dark_mode else "#333",
               linewidth=1.6, linestyle="--", alpha=0.7)
    ax.set_xlim(0, v_max*1.25); ax.set_yticks([])
    ax.tick_params(axis="x", colors=T["text2"], labelsize=7)
    ax.spines[:].set_visible(False)
    ax.set_title(f"Velocity: {v_actual:.2f} m/s", color=tc,
                 fontsize=8.5, pad=3, fontweight="bold")
    plt.tight_layout(pad=0.1)
    return fig


# -- System Renderer
def render_system(system_key: str, system_label: str):
    vrange = VELOCITY_RANGES[system_key]
    fluid  = vrange["fluid"]
    default_flow = max(5.0, float(vessel_dwt/800*10))
    if system_key == "Compressed Air":            default_flow = 30.0
    if system_key in ("Lube Oil","Hydraulic"):    default_flow = 20.0
    if system_key == "Sewage":                    default_flow = 5.0

    st.markdown(
        f'<div style="font-family:Space Grotesk,sans-serif;font-size:1.45rem;font-weight:800;'
        f'color:{T["primary"]};margin:4px 0 16px;letter-spacing:-0.01em;">'
        f'{system_label} System</div>',
        unsafe_allow_html=True
    )
    col1, col2, col3 = st.columns([1,1,1], gap="medium")

    with col1:
        st.markdown('<div class="sp-section-title">Flow Requirements</div>', unsafe_allow_html=True)
        flow_rate   = st.number_input("Flow Rate (m3/h)", 0.5, 5000.0, default_flow, 5.0, key=f"{system_key}_flow")
        pipe_length = st.number_input("Pipe Length (m)",  5.0, 500.0, 50.0, 5.0,  key=f"{system_key}_len")
        static_head = st.number_input("Static Head (m)",  0.0, 50.0,  8.0,  0.5,  key=f"{system_key}_head")
        velocity    = st.slider(
            f"Velocity (m/s) rec: {vrange['recommended']}",
            vrange["min"], vrange["max"], vrange["recommended"], 0.1,
            key=f"{system_key}_vel"
        )
        design_pres = st.number_input("Design Pressure (bar)", 1.0, 400.0, 7.0, 0.5, key=f"{system_key}_pres")
        schedule    = recommended_schedule(system_key, design_pres)
        st.markdown(
            f'<div style="font-size:0.78rem;color:{T["muted"]};margin-top:2px;">'
            f'Auto schedule: <span style="color:{T["primary"]};font-weight:700;">{schedule}</span></div>',
            unsafe_allow_html=True
        )

    pipe = pipe_summary(flow_rate, velocity, pipe_length, schedule, fluid, design_pres)
    pump = pump_summary(flow_rate, static_head, pipe["pressure_drop_mH2O"], system_key, fluid, pump_efficiency)
    bom  = generate_bom(system_key, flow_rate, vessel_loa)
    mat  = material_spec(system_key)

    st.session_state.system_results[system_key] = {
        "label": system_label, "pipe": pipe, "pump": pump, "bom": bom,
        "flow": flow_rate, "length": pipe_length, "fluid": fluid,
    }

    with col2:
        st.markdown('<div class="sp-section-title">Pipe Sizing</div>', unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        m1.metric("Pipe Size", pipe["selected_nps"].split(" ")[0])
        m2.metric("Schedule",  pipe["schedule"])
        m1.metric("OD",   f'{pipe["OD_mm"]} mm')
        m2.metric("ID",   f'{pipe["ID_mm"]} mm')
        m1.metric("Wall", f'{pipe["wall_mm"]} mm')
        m2.metric("kg/m", str(pipe["pipe_weight_kg_m"]))
        st.pyplot(velocity_gauge(
            pipe["actual_velocity_ms"], vrange["min"], vrange["max"], vrange["recommended"]
        ), use_container_width=False)
        st.markdown(f"""
| Parameter | Value |
|:---|---:|
| Required ID | {pipe['required_id_mm']} mm |
| Actual Velocity | **{pipe['actual_velocity_ms']} m/s** |
| Reynolds No. | {int(pipe['Re']):,} |
| Pressure Drop | {pipe['pressure_drop_bar']} bar |
| Pipe Weight | {pipe['total_weight_kg']} kg |
        """)
        st.markdown(
            f'<div class="sp-mat-badge">'
            f'<span style="color:{T["primary"]};font-weight:700;">Material</span> {mat["material"]}<br>'
            f'<span style="color:{T["primary"]};font-weight:700;">Standard</span> {mat["standard"]}<br>'
            f'<span style="color:{T["text2"]};font-size:0.76rem;">{mat["note"]}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

    with col3:
        st.markdown('<div class="sp-section-title">Pump Specification</div>', unsafe_allow_html=True)
        p1, p2 = st.columns(2)
        p1.metric("Total Head", f'{pump["total_head_m"]} m')
        p2.metric("Std Motor",  f'{pump["recommended_motor_kw"]} kW')
        p1.metric("NPSHA",      f'{pump["NPSHA_m"]} m')
        p2.metric("Efficiency", f'{pump["pump_efficiency_pct"]}%')
        st.markdown(f"""
| Parameter | Value |
|:---|---:|
| Flow Rate | {pump['flow_rate_m3h']} m3/h |
| Total Head | {pump['total_head_m']} m |
| Calc Power | {pump['motor_power_kw']} kW |
| **Std Motor** | **{pump['recommended_motor_kw']} kW** |
| Pump Type | {pump['pump_type']} |
| Drive | {pump['drive']} |
| NPSH Status | {pump['npsh_status']} |
        """)
        if pump["note"]:
            st.warning(pump["note"])

    st.markdown('<div class="sp-section-title">Bill of Materials</div>', unsafe_allow_html=True)
    st.dataframe(bom, use_container_width=True, height=280)

    st.markdown('<div class="sp-section-title">Export</div>', unsafe_allow_html=True)
    ec1, ec2 = st.columns(2)
    with ec1:
        st.download_button(
            "Excel Spec Sheet",
            to_excel(pipe, pump, bom, system_label, vessel_name),
            f"ShipPipe_{system_key.replace(' ','_')}_{vessel_name.replace(' ','_')}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    with ec2:
        st.download_button(
            "PDF Spec Sheet",
            to_pdf(pipe, pump, bom, system_label, vessel_name),
            f"ShipPipe_{system_key.replace(' ','_')}_{vessel_name.replace(' ','_')}.pdf",
            "application/pdf",
            use_container_width=True
        )


# -- Dashboard
def render_dashboard():
    bg = T["chart_bg"]
    tc = T["text"]

    st.markdown(
        f'<div style="font-family:Space Grotesk,sans-serif;font-size:1.45rem;font-weight:800;'
        f'color:{T["primary"]};margin:4px 0 4px;letter-spacing:-0.01em;">Project Dashboard</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div style="font-size:0.82rem;color:{T["text2"]};margin-bottom:16px;">'
        f'<strong style="color:{T["text"]};">{vessel_name}</strong> &nbsp;|&nbsp; '
        f'LOA {vessel_loa} m &nbsp;|&nbsp; DWT {vessel_dwt:,} &nbsp;|&nbsp; Draft {vessel_draft} m</div>',
        unsafe_allow_html=True
    )

    results   = st.session_state.system_results
    n_sys     = len(results)
    total_bom = sum(len(v["bom"]) for v in results.values()) if results else 0
    total_kw  = sum(v["pump"]["recommended_motor_kw"] for v in results.values()) if results else 0
    max_pipe  = max((v["pipe"]["OD_mm"] for v in results.values()), default=0)

    k1, k2, k3, k4 = st.columns(4)
    for col, num, lbl in [
        (k1, str(n_sys),          "Systems Sized"),
        (k2, str(total_bom),      "Total BOM Items"),
        (k3, f"{total_kw:.0f} kW","Total Pump Power"),
        (k4, f"{max_pipe:.0f} mm","Largest Pipe OD"),
    ]:
        col.markdown(
            f'<div class="sp-kpi"><div class="sp-kpi-num">{num}</div>'
            f'<div class="sp-kpi-lbl">{lbl}</div></div>',
            unsafe_allow_html=True
        )

    if not results:
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("Open any system tab -> set parameters -> results appear here automatically.")
        st.markdown("---")
        tpl = io.BytesIO()
        tdf = pd.DataFrame({"Field":["Vessel Name","LOA (m)","DWT","Draft (m)"],
                             "Value":[vessel_name,vessel_loa,vessel_dwt,vessel_draft]})
        with pd.ExcelWriter(tpl, engine="openpyxl") as w:
            tdf.to_excel(w, sheet_name="Vessel Data", index=False)
        st.download_button("Download Vessel Template", tpl.getvalue(),
            "ShipPipe_VesselTemplate.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        return

    st.markdown("<br>", unsafe_allow_html=True)
    systems = list(results.keys())
    labels  = [s[:13] for s in systems]

    def make_fig(w=5.2, h=3.2):
        fig, ax = plt.subplots(figsize=(w, h))
        fig.patch.set_facecolor(bg); ax.set_facecolor(bg)
        ax.spines[:].set_visible(False)
        ax.tick_params(colors=tc, labelsize=8)
        return fig, ax

    ch1, ch2 = st.columns(2, gap="medium")
    with ch1:
        st.markdown('<div class="sp-section-title">Pipe OD by System (mm)</div>', unsafe_allow_html=True)
        ods = [results[s]["pipe"]["OD_mm"] for s in systems]
        fig, ax = make_fig()
        bars = ax.barh(labels, ods, color=T["c1"], edgecolor="none", height=0.55)
        ax.bar_label(bars, fmt="%.1f", color=tc, fontsize=8, padding=4)
        ax.set_xlabel("OD (mm)", color=T["text2"], fontsize=8)
        plt.tight_layout(); st.pyplot(fig, use_container_width=True)

    with ch2:
        st.markdown('<div class="sp-section-title">Motor Power by System (kW)</div>', unsafe_allow_html=True)
        kws = [results[s]["pump"]["recommended_motor_kw"] for s in systems]
        fig2, ax2 = make_fig()
        bars2 = ax2.barh(labels, kws, color=T["c2"], edgecolor="none", height=0.55)
        ax2.bar_label(bars2, fmt="%.1f kW", color=tc, fontsize=8, padding=4)
        ax2.set_xlabel("kW", color=T["text2"], fontsize=8)
        plt.tight_layout(); st.pyplot(fig2, use_container_width=True)

    ch3, ch4 = st.columns(2, gap="medium")
    with ch3:
        st.markdown('<div class="sp-section-title">BOM Items by System</div>', unsafe_allow_html=True)
        bom_counts = [len(results[s]["bom"]) for s in systems]
        fig3, ax3 = make_fig(4.2, 3.2)
        palette = [T["c1"],T["c2"],T["c3"],"#a78bfa","#fb923c",
                   "#34d399","#60a5fa","#f472b6","#facc15","#4ade80","#38bdf8","#c084fc"]
        wedges, texts, autotexts = ax3.pie(
            bom_counts, labels=labels, autopct="%1.0f%%",
            colors=palette[:len(systems)],
            textprops={"color": tc, "fontsize": 7},
            wedgeprops={"edgecolor": bg, "linewidth": 1.8}
        )
        for at in autotexts:
            at.set_fontsize(7); at.set_color("#060d1a")
        plt.tight_layout(); st.pyplot(fig3, use_container_width=True)

    with ch4:
        st.markdown('<div class="sp-section-title">Pressure Drop by System (bar)</div>', unsafe_allow_html=True)
        dps = [results[s]["pipe"]["pressure_drop_bar"] for s in systems]
        fig4, ax4 = make_fig()
        ax4.bar(labels, dps, color=T["c3"], edgecolor="none", width=0.55)
        ax4.tick_params(axis="x", colors=tc, labelsize=7, rotation=32)
        ax4.tick_params(axis="y", colors=tc, labelsize=8)
        ax4.set_ylabel("bar", color=T["text2"], fontsize=8)
        plt.tight_layout(); st.pyplot(fig4, use_container_width=True)

    st.markdown('<div class="sp-section-title">System Summary</div>', unsafe_allow_html=True)
    rows = []
    for s in systems:
        r = results[s]
        rows.append({
            "System": s,
            "Flow (m3/h)": r["flow"],
            "Pipe Size": r["pipe"]["selected_nps"].split(" ")[0],
            "OD (mm)": r["pipe"]["OD_mm"],
            "ID (mm)": r["pipe"]["ID_mm"],
            "Sched.": r["pipe"]["schedule"],
            "Vel. (m/s)": r["pipe"]["actual_velocity_ms"],
            "dP (bar)": r["pipe"]["pressure_drop_bar"],
            "Head (m)": r["pump"]["total_head_m"],
            "Motor (kW)": r["pump"]["recommended_motor_kw"],
            "BOM": len(r["bom"]),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown('<div class="sp-section-title">Bulk Export</div>', unsafe_allow_html=True)
    ex1, ex2, ex3 = st.columns(3)

    with ex1:
        all_xl = io.BytesIO()
        with pd.ExcelWriter(all_xl, engine="openpyxl") as writer:
            pd.DataFrame(rows).to_excel(writer, sheet_name="Summary", index=False)
            for s in systems:
                r = results[s]
                pipe_df = pd.DataFrame([r["pipe"]]).T.reset_index(); pipe_df.columns=["Parameter","Value"]
                pump_df = pd.DataFrame([r["pump"]]).T.reset_index(); pump_df.columns=["Parameter","Value"]
                sheet   = s[:28].replace("/","-").replace(" ","_")
                pd.concat([pipe_df, pd.DataFrame([["",""]] * 2, columns=["Parameter","Value"]), pump_df])\
                  .to_excel(writer, sheet_name=f"{sheet}_Pipe_Pump", index=False)
                r["bom"].to_excel(writer, sheet_name=f"{sheet}_BOM")
        st.download_button("All Systems Excel", all_xl.getvalue(),
            f"ShipPipe_ALL_{vessel_name.replace(' ','_')}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)

    with ex2:
        tpl2 = io.BytesIO()
        tdf2 = pd.DataFrame({"Field":["Vessel Name","LOA (m)","DWT","Draft (m)"],
                              "Value":[vessel_name,vessel_loa,vessel_dwt,vessel_draft]})
        with pd.ExcelWriter(tpl2, engine="openpyxl") as w:
            tdf2.to_excel(w, sheet_name="Vessel Data", index=False)
        st.download_button("Vessel Template", tpl2.getvalue(),
            "ShipPipe_VesselTemplate.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)

    with ex3:
        bom_all = pd.concat([v["bom"].assign(System=k) for k,v in results.items()], ignore_index=True)
        bom_xl  = io.BytesIO()
        with pd.ExcelWriter(bom_xl, engine="openpyxl") as w:
            bom_all.to_excel(w, sheet_name="Master BOM", index=False)
        st.download_button("Master BOM", bom_xl.getvalue(),
            f"ShipPipe_MasterBOM_{vessel_name.replace(' ','_')}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)


# -- Page Header
st.markdown(
    f'<div style="display:flex;align-items:center;gap:14px;padding:4px 0 10px;">'
    f'  {valve_svg(T["primary"], 46)}'
    f'  <div>'
    f'    <div style="font-family:Space Grotesk,sans-serif;font-size:1.75rem;font-weight:900;'
    f'         color:{T["primary"]};line-height:1.1;letter-spacing:-0.02em;">ShipPipe</div>'
    f'    <div style="font-size:0.8rem;color:{T["text2"]};margin-top:2px;letter-spacing:0.01em;">'
    f'      Marine Piping System Designer &nbsp;·&nbsp; 12 Systems &nbsp;·&nbsp; '
    f'      Pipe Sizing · Pump Spec · BOM · Excel &amp; PDF Export'
    f'    </div>'
    f'  </div>'
    f'</div>'
    f'<div style="height:1px;background:linear-gradient(90deg,{T["primary"]}88,transparent);'
    f'margin-bottom:16px;"></div>',
    unsafe_allow_html=True
)


# -- Tabs
tabs = st.tabs([
    "Dashboard", "Ballast", "Bilge", "FO HFO", "FO MDO",
    "Fire & GS", "Fresh Water", "Cooling SW", "Cooling FW",
    "Lube Oil", "Hydraulic", "Comp. Air", "Sewage", "About",
])

with tabs[0]:  render_dashboard()
with tabs[1]:  render_system("Ballast",        "Ballast")
with tabs[2]:  render_system("Bilge",          "Bilge")
with tabs[3]:  render_system("Fuel Oil HFO",   "Fuel Oil HFO")
with tabs[4]:  render_system("Fuel Oil MDO",   "Fuel Oil MDO")
with tabs[5]:  render_system("Fire & GS",      "Fire & GS")
with tabs[6]:  render_system("Fresh Water",    "Fresh Water")
with tabs[7]:  render_system("Cooling SW",     "Cooling SW")
with tabs[8]:  render_system("Cooling FW",     "Cooling FW")
with tabs[9]:  render_system("Lube Oil",       "Lube Oil")
with tabs[10]: render_system("Hydraulic",      "Hydraulic")
with tabs[11]: render_system("Compressed Air", "Compressed Air")
with tabs[12]: render_system("Sewage",         "Sewage")

with tabs[13]:
    st.markdown(
        f'<div style="font-family:Space Grotesk,sans-serif;font-size:1.45rem;font-weight:800;'
        f'color:{T["primary"]};margin-bottom:12px;">About ShipPipe</div>',
        unsafe_allow_html=True
    )
    st.markdown("""
**ShipPipe** is a marine piping system design tool built by **Suji Kumar C**, Marine Software Engineer at Shoft Shipyard, Gujarat.

### Systems (12 total)
| # | System | Design Fluid | Velocity Range |
|---|--------|-------------|----------------|
| 1 | Ballast | Sea Water | 1.5 - 3.0 m/s |
| 2 | Bilge | Sea Water | 1.0 - 2.5 m/s |
| 3 | Fuel Oil HFO | Heavy Fuel Oil | 0.5 - 1.0 m/s |
| 4 | Fuel Oil MDO | Marine Diesel Oil | 0.8 - 1.5 m/s |
| 5 | Fire & GS | Sea Water | 3.0 - 5.0 m/s |
| 6 | Fresh Water | Fresh Water | 1.0 - 2.5 m/s |
| 7 | Cooling SW | Sea Water | 1.5 - 3.0 m/s |
| 8 | Cooling FW | Fresh Water | 1.0 - 2.5 m/s |
| 9 | Lube Oil | Lube Oil | 0.5 - 1.5 m/s |
| 10 | Hydraulic | Hydraulic Oil | 2.0 - 4.0 m/s |
| 11 | Compressed Air | Gas (7-30 bar) | 8.0 - 20.0 m/s |
| 12 | Sewage | Fresh Water | 0.6 - 2.0 m/s |

### Engineering References
- Pipe schedules: **ASME B36.10M**
- Pressure drop: **Darcy-Weisbach + Colebrook-White**
- Fire & GS: **SOLAS II-2**
- Sewage: **MARPOL Annex IV / ISO 8099**
- Fuel oil systems: **SOLAS II-2 Reg. 4**

[sujikumar.com](https://sujikumar.com) | [LinkedIn](https://linkedin.com/in/sujikumar)
    """)

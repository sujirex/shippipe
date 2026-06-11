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

from utils.pipe_calc import pipe_summary, required_id
from utils.pump_calc import pump_summary
from utils.bom import generate_bom, material_spec
from utils.export import to_excel, to_pdf
from utils.systems_data import VELOCITY_RANGES, MATERIALS, recommended_schedule

st.set_page_config(
    page_title="ShipPipe - Marine Piping Designer",
    page_icon="🎛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session State ──────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "system_results" not in st.session_state:
    st.session_state.system_results = {}

# ── Theme Palette ──────────────────────────────────────────────────────────────
def get_theme():
    if st.session_state.dark_mode:
        return {
            "bg":      "#0a1a1a",
            "bg2":     "#0d2424",
            "card":    "#112e2e",
            "border":  "#00bcd440",
            "primary": "#00bcd4",
            "text":    "#ffffff",
            "text2":   "#80deea",
            "muted":   "#4db6ac",
            "success": "#26a69a",
            "danger":  "#ef5350",
            "tab_sel_text": "#0a1a1a",
            "chart_bar1": "#00bcd4",
            "chart_bar2": "#26a69a",
            "chart_bar3": "#fb923c",
        }
    return {
        "bg":      "#e0f7fa",
        "bg2":     "#b2ebf2",
        "card":    "#ffffff",
        "border":  "#00838f60",
        "primary": "#00695c",
        "text":    "#000000",
        "text2":   "#004d40",
        "muted":   "#00695c",
        "success": "#2e7d32",
        "danger":  "#c62828",
        "tab_sel_text": "#ffffff",
        "chart_bar1": "#00838f",
        "chart_bar2": "#2e7d32",
        "chart_bar3": "#e65100",
    }

T = get_theme()

# ── Gate Valve SVG ─────────────────────────────────────────────────────────────
# P&ID gate valve symbol: two triangles + handwheel + pipe ends
def valve_svg(color: str, size: int = 48) -> str:
    c = color
    s = size
    sc = s / 48  # scale factor
    return f"""<svg width="{s}" height="{s}" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
  <!-- Pipe ends -->
  <line x1="0" y1="24" x2="6" y2="24" stroke="{c}" stroke-width="3.5" stroke-linecap="round"/>
  <line x1="42" y1="24" x2="48" y2="24" stroke="{c}" stroke-width="3.5" stroke-linecap="round"/>
  <!-- Left triangle (body half) -->
  <polygon points="6,14 6,34 22,24" fill="{c}"/>
  <!-- Right triangle (body half) -->
  <polygon points="42,14 42,34 26,24" fill="{c}"/>
  <!-- Center gap line -->
  <line x1="22" y1="24" x2="26" y2="24" stroke="{c}" stroke-width="2.5"/>
  <!-- Stem -->
  <line x1="24" y1="14" x2="24" y2="4" stroke="{c}" stroke-width="2.5" stroke-linecap="round"/>
  <!-- Handwheel -->
  <circle cx="24" cy="4" r="6" stroke="{c}" stroke-width="2" fill="none"/>
  <line x1="18" y1="4" x2="30" y2="4" stroke="{c}" stroke-width="1.5"/>
  <line x1="24" y1="0" x2="24" y2="8" stroke="{c}" stroke-width="1.5"/>
</svg>"""

# ── CSS Injection ──────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  .stApp {{ background-color: {T["bg"]} !important; color: {T["text"]} !important; }}
  .block-container {{ padding-top: 1.2rem; }}

  section[data-testid="stSidebar"] {{ background-color: {T["bg2"]} !important; }}
  section[data-testid="stSidebar"] * {{ color: {T["text"]} !important; }}
  section[data-testid="stSidebar"] label {{ color: {T["text2"]} !important; }}

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {{
    gap: 3px; background: {T["bg2"]}; padding: 4px; border-radius: 8px;
  }}
  .stTabs [data-baseweb="tab"] {{
    padding: 6px 14px; border-radius: 6px;
    font-weight: 600; font-size: 0.78rem; color: {T["text2"]} !important;
  }}
  .stTabs [aria-selected="true"] {{
    background: {T["primary"]} !important;
    color: {T["tab_sel_text"]} !important;
  }}
  .stTabs [data-baseweb="tab-panel"] {{ background: transparent; }}

  /* General text overrides for light mode */
  .stMarkdown, .stMarkdown p, .stMarkdown li,
  h1, h2, h3, h4, h5, h6 {{ color: {T["text"]} !important; }}
  .stDataFrame {{ color: {T["text"]} !important; border-radius: 8px; overflow: hidden; }}

  /* Metrics */
  [data-testid="stMetricLabel"] {{ color: {T["muted"]} !important; }}
  [data-testid="stMetricValue"] {{ color: {T["primary"]} !important; }}

  /* Custom components */
  .sec-title {{
    font-size: 0.9rem; font-weight: 700; color: {T["primary"]};
    border-left: 3px solid {T["primary"]}; padding-left: 8px;
    margin: 14px 0 8px 0;
  }}
  .info-card {{
    background: {T["card"]}; border: 1px solid {T["border"]};
    border-radius: 8px; padding: 10px 14px; margin: 6px 0;
    font-size: 0.82rem; color: {T["text"]};
  }}
  .dash-card {{
    background: {T["card"]}; border: 1px solid {T["border"]};
    border-top: 3px solid {T["primary"]};
    border-radius: 10px; padding: 14px; text-align: center;
  }}
  .dash-num {{ font-size: 2rem; font-weight: 900; color: {T["primary"]}; }}
  .dash-lbl {{
    font-size: 0.72rem; color: {T["muted"]}; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.05em;
  }}

  /* Buttons */
  .stDownloadButton > button {{
    background: {T["primary"]} !important;
    color: {T["tab_sel_text"]} !important;
    border: none !important; border-radius: 6px !important;
    font-weight: 600 !important;
  }}
  .stButton > button {{
    background: {T["bg2"]} !important;
    color: {T["text"]} !important;
    border: 1px solid {T["primary"]} !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
  }}
  .stButton > button:hover {{
    background: {T["primary"]} !important;
    color: {T["tab_sel_text"]} !important;
  }}

  footer {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Valve icon + title
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">'
        f'{valve_svg(T["primary"], 40)}'
        f'<div><span style="font-size:1.3rem;font-weight:800;color:{T["primary"]};">ShipPipe</span>'
        f'<br><span style="font-size:0.72rem;color:{T["text2"]};">Marine Piping Designer</span></div>'
        f'</div>',
        unsafe_allow_html=True
    )

    mode_label = "☀️ Light Mode" if st.session_state.dark_mode else "🌙 Dark Mode"
    if st.button(mode_label, use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    st.markdown("---")
    st.markdown(f"**Vessel / Project Info**")
    vessel_name  = st.text_input("Vessel / Project", value="MV Example", label_visibility="collapsed")
    vessel_loa   = st.number_input("Length Overall (m)", 50.0, 400.0, 120.0, 5.0)
    vessel_dwt   = st.number_input("Deadweight (DWT)", 500, 200000, 5000, 500)
    vessel_draft = st.number_input("Design Draft (m)", 2.0, 25.0, 6.5, 0.5)

    st.markdown("---")
    st.markdown("**Global Settings**")
    default_schedule = st.selectbox("Pipe Schedule", ["SCH 40", "SCH 80", "SCH 160"])
    pump_efficiency  = st.slider("Pump Efficiency (%)", 60, 85, 72) / 100

    st.markdown("---")
    st.markdown("**Import Vessel Template**")
    uploaded = st.file_uploader("Upload Excel template", type=["xlsx"], label_visibility="collapsed")
    if uploaded:
        try:
            df_in = pd.read_excel(uploaded, sheet_name="Vessel Data")
            vessel_name  = str(df_in.iloc[0, 1])
            vessel_loa   = float(df_in.iloc[1, 1])
            vessel_dwt   = float(df_in.iloc[2, 1])
            vessel_draft = float(df_in.iloc[3, 1])
            st.success("Vessel data imported!")
        except Exception:
            st.error("Invalid template. Download from the Dashboard tab.")

    st.markdown("---")
    st.caption(f"Built by [Suji Kumar C](https://sujikumar.com)")


# ── Velocity Gauge ─────────────────────────────────────────────────────────────
def velocity_gauge(v_actual, v_min, v_max, v_rec, title="Flow Velocity"):
    dark = st.session_state.dark_mode
    bg = T["bg2"]
    tc = T["text"]
    fig, ax = plt.subplots(figsize=(4, 0.55))
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)
    ax.barh(0, v_max * 1.2, height=0.4, color="#112e2e" if dark else "#b2ebf2", left=0)
    ax.barh(0, v_max - v_min, height=0.4, color="#26a69a", left=v_min, alpha=0.5)
    color = "#00bcd4" if v_min <= v_actual <= v_max else "#ef5350"
    ax.barh(0, v_actual, height=0.4, color=color)
    ax.axvline(v_rec, color="#80deea" if dark else "#004d40", linewidth=1.5, linestyle="--")
    ax.set_xlim(0, v_max * 1.2)
    ax.set_yticks([])
    ax.tick_params(axis="x", colors=T["text2"], labelsize=7)
    ax.spines[:].set_visible(False)
    ax.set_title(f"{title}: {v_actual:.2f} m/s", color=tc, fontsize=8, pad=2)
    plt.tight_layout(pad=0.1)
    return fig


# ── System Renderer ────────────────────────────────────────────────────────────
def render_system(system_key: str, system_label: str):
    vrange = VELOCITY_RANGES[system_key]
    fluid  = vrange["fluid"]
    default_flow = max(5.0, float(vessel_dwt / 800 * 10))
    if system_key == "Compressed Air":  default_flow = 30.0
    if system_key in ("Lube Oil", "Hydraulic"): default_flow = 20.0
    if system_key == "Sewage":          default_flow = 5.0

    st.markdown(f'<h3 style="color:{T["primary"]}">{system_label} System</h3>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.markdown('<div class="sec-title">Flow Requirements</div>', unsafe_allow_html=True)
        flow_rate   = st.number_input("Flow Rate (m³/h)", 0.5, 5000.0, default_flow, 5.0, key=f"{system_key}_flow")
        pipe_length = st.number_input("Pipe Length (m)",  5.0, 500.0, 50.0, 5.0,  key=f"{system_key}_len")
        static_head = st.number_input("Static Head (m)",  0.0, 50.0,  8.0,  0.5,  key=f"{system_key}_head")
        velocity    = st.slider(
            f"Design Velocity (m/s)  [rec: {vrange['recommended']}]",
            vrange["min"], vrange["max"], vrange["recommended"], 0.1,
            key=f"{system_key}_vel"
        )
        design_pres = st.number_input("Design Pressure (bar)", 1.0, 400.0, 7.0, 0.5, key=f"{system_key}_pres")
        schedule    = recommended_schedule(system_key, design_pres)
        st.caption(f"Auto schedule: **{schedule}**")

    pipe = pipe_summary(flow_rate, velocity, pipe_length, schedule, fluid, design_pres)
    pump = pump_summary(flow_rate, static_head, pipe["pressure_drop_mH2O"], system_key, fluid, pump_efficiency)
    bom  = generate_bom(system_key, flow_rate, vessel_loa)
    mat  = material_spec(system_key)

    st.session_state.system_results[system_key] = {
        "label": system_label, "pipe": pipe, "pump": pump, "bom": bom,
        "flow": flow_rate, "length": pipe_length, "fluid": fluid,
    }

    with col2:
        st.markdown('<div class="sec-title">Pipe Sizing</div>', unsafe_allow_html=True)
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
|---|---|
| Required ID | {pipe['required_id_mm']} mm |
| Actual Velocity | **{pipe['actual_velocity_ms']} m/s** |
| Reynolds No. | {int(pipe['Re']):,} |
| Pressure Drop | {pipe['pressure_drop_bar']} bar |
| Pipe Weight Total | {pipe['total_weight_kg']} kg |
        """)
        st.markdown(
            f'<div class="info-card"><b>Material:</b> {mat["material"]}<br>'
            f'<b>Standard:</b> {mat["standard"]}<br>{mat["note"]}</div>',
            unsafe_allow_html=True
        )

    with col3:
        st.markdown('<div class="sec-title">Pump Specification</div>', unsafe_allow_html=True)
        p1, p2 = st.columns(2)
        p1.metric("Total Head", f'{pump["total_head_m"]} m')
        p2.metric("Std Motor",  f'{pump["recommended_motor_kw"]} kW')
        p1.metric("NPSHA",      f'{pump["NPSHA_m"]} m')
        p2.metric("Efficiency", f'{pump["pump_efficiency_pct"]}%')

        st.markdown(f"""
| Parameter | Value |
|---|---|
| Flow Rate | {pump['flow_rate_m3h']} m³/h |
| Total Head | {pump['total_head_m']} m |
| Calc Power | {pump['motor_power_kw']} kW |
| **Std Motor** | **{pump['recommended_motor_kw']} kW** |
| Pump Type | {pump['pump_type']} |
| Drive | {pump['drive']} |
| NPSH Status | {pump['npsh_status']} |
        """)
        if pump["note"]:
            st.warning(pump["note"])

    st.markdown('<div class="sec-title">Bill of Materials</div>', unsafe_allow_html=True)
    st.dataframe(bom, use_container_width=True, height=300)

    st.markdown('<div class="sec-title">Export</div>', unsafe_allow_html=True)
    ec1, ec2 = st.columns(2)
    with ec1:
        st.download_button(
            "📥 Excel Spec Sheet",
            to_excel(pipe, pump, bom, system_label, vessel_name),
            f"ShipPipe_{system_key.replace(' ','_')}_{vessel_name.replace(' ','_')}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    with ec2:
        st.download_button(
            "📄 PDF Spec Sheet",
            to_pdf(pipe, pump, bom, system_label, vessel_name),
            f"ShipPipe_{system_key.replace(' ','_')}_{vessel_name.replace(' ','_')}.pdf",
            "application/pdf",
            use_container_width=True
        )


# ── Dashboard ──────────────────────────────────────────────────────────────────
def render_dashboard():
    bg = T["bg2"]
    tc = T["text"]
    c1 = T["chart_bar1"]
    c2 = T["chart_bar2"]
    c3 = T["chart_bar3"]

    st.markdown(f'<h3 style="color:{T["primary"]}">Project Dashboard</h3>', unsafe_allow_html=True)
    st.caption(f"Vessel: **{vessel_name}** | LOA: {vessel_loa} m | DWT: {vessel_dwt} | Draft: {vessel_draft} m")

    results   = st.session_state.system_results
    n_sys     = len(results)
    total_bom = sum(len(v["bom"]) for v in results.values()) if results else 0
    total_kw  = sum(v["pump"]["recommended_motor_kw"] for v in results.values()) if results else 0
    max_pipe  = max((v["pipe"]["OD_mm"] for v in results.values()), default=0)

    # KPI cards
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="dash-card"><div class="dash-num">{n_sys}</div>'
                f'<div class="dash-lbl">Systems Sized</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="dash-card"><div class="dash-num">{total_bom}</div>'
                f'<div class="dash-lbl">Total BOM Items</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="dash-card"><div class="dash-num">{total_kw:.0f} kW</div>'
                f'<div class="dash-lbl">Total Pump Power</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="dash-card"><div class="dash-num">{max_pipe:.0f} mm</div>'
                f'<div class="dash-lbl">Largest Pipe OD</div></div>', unsafe_allow_html=True)

    if not results:
        st.info("Go to any system tab, set your parameters, and results will appear here automatically.")
        st.markdown("---")
        st.markdown("**Download Vessel Template** — fill in and upload in the sidebar to pre-populate inputs")
        tpl = io.BytesIO()
        tdf = pd.DataFrame({"Field": ["Vessel Name","LOA (m)","DWT","Draft (m)"],
                             "Value": [vessel_name, vessel_loa, vessel_dwt, vessel_draft]})
        with pd.ExcelWriter(tpl, engine="openpyxl") as w:
            tdf.to_excel(w, sheet_name="Vessel Data", index=False)
        st.download_button("📥 Download Vessel Template", tpl.getvalue(),
            "ShipPipe_VesselTemplate.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        return

    st.markdown("---")
    systems = list(results.keys())
    labels  = [s[:12] for s in systems]

    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown('<div class="sec-title">Pipe OD by System (mm)</div>', unsafe_allow_html=True)
        ods = [results[s]["pipe"]["OD_mm"] for s in systems]
        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor(bg); ax.set_facecolor(bg)
        bars = ax.barh(labels, ods, color=c1, edgecolor=T["muted"], height=0.6)
        ax.bar_label(bars, fmt="%.1f", color=tc, fontsize=8, padding=3)
        ax.tick_params(colors=tc, labelsize=8)
        ax.spines[:].set_visible(False)
        ax.set_xlabel("OD (mm)", color=tc, fontsize=8)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)

    with ch2:
        st.markdown('<div class="sec-title">Motor Power by System (kW)</div>', unsafe_allow_html=True)
        kws = [results[s]["pump"]["recommended_motor_kw"] for s in systems]
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        fig2.patch.set_facecolor(bg); ax2.set_facecolor(bg)
        bars2 = ax2.barh(labels, kws, color=c2, edgecolor=T["muted"], height=0.6)
        ax2.bar_label(bars2, fmt="%.1f kW", color=tc, fontsize=8, padding=3)
        ax2.tick_params(colors=tc, labelsize=8)
        ax2.spines[:].set_visible(False)
        ax2.set_xlabel("Motor Power (kW)", color=tc, fontsize=8)
        plt.tight_layout()
        st.pyplot(fig2, use_container_width=True)

    ch3, ch4 = st.columns(2)
    with ch3:
        st.markdown('<div class="sec-title">BOM Items by System</div>', unsafe_allow_html=True)
        bom_counts = [len(results[s]["bom"]) for s in systems]
        fig3, ax3 = plt.subplots(figsize=(4, 3))
        fig3.patch.set_facecolor(bg); ax3.set_facecolor(bg)
        palette = ["#00bcd4","#26a69a","#00838f","#4db6ac","#80deea",
                   "#006064","#00acc1","#0097a7","#00bfa5","#1de9b6","#64ffda","#84ffff"]
        wedges, texts, autotexts = ax3.pie(
            bom_counts, labels=labels, autopct="%1.0f%%",
            colors=palette[:len(systems)],
            textprops={"color": tc, "fontsize": 7},
            wedgeprops={"edgecolor": bg, "linewidth": 1.5}
        )
        for at in autotexts:
            at.set_color("#0a1a1a")
            at.set_fontsize(7)
        plt.tight_layout()
        st.pyplot(fig3, use_container_width=True)

    with ch4:
        st.markdown('<div class="sec-title">Pressure Drop by System (bar)</div>', unsafe_allow_html=True)
        dps = [results[s]["pipe"]["pressure_drop_bar"] for s in systems]
        fig4, ax4 = plt.subplots(figsize=(5, 3))
        fig4.patch.set_facecolor(bg); ax4.set_facecolor(bg)
        ax4.bar(labels, dps, color=c3, edgecolor=T["muted"], width=0.6)
        ax4.tick_params(axis="x", colors=tc, labelsize=7, rotation=30)
        ax4.tick_params(axis="y", colors=tc, labelsize=8)
        ax4.spines[:].set_visible(False)
        ax4.set_ylabel("bar", color=tc, fontsize=8)
        plt.tight_layout()
        st.pyplot(fig4, use_container_width=True)

    # Summary table
    st.markdown('<div class="sec-title">System Summary Table</div>', unsafe_allow_html=True)
    rows = []
    for s in systems:
        r = results[s]
        rows.append({
            "System": s,
            "Flow (m3/h)": r["flow"],
            "Pipe Size": r["pipe"]["selected_nps"].split(" ")[0],
            "OD (mm)": r["pipe"]["OD_mm"],
            "ID (mm)": r["pipe"]["ID_mm"],
            "Schedule": r["pipe"]["schedule"],
            "Velocity (m/s)": r["pipe"]["actual_velocity_ms"],
            "dP (bar)": r["pipe"]["pressure_drop_bar"],
            "Pump Head (m)": r["pump"]["total_head_m"],
            "Motor (kW)": r["pump"]["recommended_motor_kw"],
            "BOM Items": len(r["bom"]),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Multi-system exports
    st.markdown("---")
    st.markdown('<div class="sec-title">Export All Systems</div>', unsafe_allow_html=True)
    ex1, ex2, ex3 = st.columns(3)

    with ex1:
        all_xl = io.BytesIO()
        with pd.ExcelWriter(all_xl, engine="openpyxl") as writer:
            pd.DataFrame(rows).to_excel(writer, sheet_name="Summary", index=False)
            for s in systems:
                r = results[s]
                pipe_df = pd.DataFrame([r["pipe"]]).T.reset_index(); pipe_df.columns = ["Parameter","Value"]
                pump_df = pd.DataFrame([r["pump"]]).T.reset_index(); pump_df.columns = ["Parameter","Value"]
                sheet = s[:28].replace("/","-").replace(" ","_")
                pd.concat([pipe_df, pd.DataFrame([["",""]] * 2, columns=["Parameter","Value"]), pump_df])\
                  .to_excel(writer, sheet_name=f"{sheet}_Pipe_Pump", index=False)
                r["bom"].to_excel(writer, sheet_name=f"{sheet}_BOM")
        st.download_button("📥 All Systems Excel", all_xl.getvalue(),
            f"ShipPipe_ALL_{vessel_name.replace(' ','_')}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)

    with ex2:
        tpl2 = io.BytesIO()
        tdf2 = pd.DataFrame({"Field": ["Vessel Name","LOA (m)","DWT","Draft (m)"],
                              "Value": [vessel_name, vessel_loa, vessel_dwt, vessel_draft]})
        with pd.ExcelWriter(tpl2, engine="openpyxl") as w:
            tdf2.to_excel(w, sheet_name="Vessel Data", index=False)
        st.download_button("📋 Vessel Template", tpl2.getvalue(),
            "ShipPipe_VesselTemplate.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)

    with ex3:
        bom_all = pd.concat([v["bom"].assign(System=k) for k,v in results.items()], ignore_index=True)
        bom_xl = io.BytesIO()
        with pd.ExcelWriter(bom_xl, engine="openpyxl") as w:
            bom_all.to_excel(w, sheet_name="Master BOM", index=False)
        st.download_button("📦 Master BOM", bom_xl.getvalue(),
            f"ShipPipe_MasterBOM_{vessel_name.replace(' ','_')}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)


# ── Page Header ────────────────────────────────────────────────────────────────
hcol1, hcol2 = st.columns([1, 12])
with hcol1:
    st.markdown(valve_svg(T["primary"], 52), unsafe_allow_html=True)
with hcol2:
    st.markdown(
        f'<h2 style="color:{T["primary"]};margin:0;line-height:1.2;">ShipPipe</h2>'
        f'<p style="color:{T["text2"]};margin:0;font-size:0.88rem;">'
        f'Marine Piping System Designer — 12 systems | Pipe sizing | Pump spec | BOM | Excel & PDF</p>',
        unsafe_allow_html=True
    )
st.markdown("---")


# ── Tabs ───────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📊 Dashboard",
    "⚓ Ballast",
    "💧 Bilge",
    "🛢 FO HFO",
    "⛽ FO MDO",
    "🔥 Fire & GS",
    "🚰 Fresh Water",
    "❄️ Cooling SW",
    "🌊 Cooling FW",
    "⚙️ Lube Oil",
    "💠 Hydraulic",
    "💨 Comp. Air",
    "🚽 Sewage",
    "📋 About",
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
    st.markdown(f'<h2 style="color:{T["primary"]}">About ShipPipe</h2>', unsafe_allow_html=True)
    st.markdown(f"""
**ShipPipe** is a marine piping system design tool built by **Suji Kumar C**.

### Systems (12 total)
| # | System | Fluid | Velocity |
|---|--------|-------|---------|
| 1 | Ballast | Sea Water | 1.5-3.0 m/s |
| 2 | Bilge | Sea Water | 1.0-2.5 m/s |
| 3 | Fuel Oil HFO | Heavy Fuel Oil | 0.5-1.0 m/s |
| 4 | Fuel Oil MDO | Marine Diesel Oil | 0.8-1.5 m/s |
| 5 | Fire & GS | Sea Water | 3.0-5.0 m/s |
| 6 | Fresh Water | Fresh Water | 1.0-2.5 m/s |
| 7 | Cooling SW | Sea Water | 1.5-3.0 m/s |
| 8 | Cooling FW | Fresh Water | 1.0-2.5 m/s |
| 9 | Lube Oil | Lube Oil | 0.5-1.5 m/s |
| 10 | Hydraulic | Hydraulic Oil | 2.0-4.0 m/s |
| 11 | Compressed Air | Gas (7-30 bar) | 8.0-20.0 m/s |
| 12 | Sewage | Fresh Water | 0.6-2.0 m/s |

### Engineering References
- Pipe schedules: **ASME B36.10M**
- Pressure drop: **Darcy-Weisbach + Colebrook-White**
- Fire system: **SOLAS II-2**
- Sewage: **MARPOL Annex IV / ISO 8099**
- Fuel oil: **SOLAS II-2 Reg. 4**

### Developer
**Suji Kumar C** — Marine Software Engineer, Shoft Shipyard, Gujarat

[sujikumar.com](https://sujikumar.com) | [LinkedIn](https://linkedin.com/in/sujikumar)
    """)

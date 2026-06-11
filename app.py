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
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme ──────────────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "system_results" not in st.session_state:
    st.session_state.system_results = {}

def get_theme():
    if st.session_state.dark_mode:
        return {
            "bg":        "#1a1208",
            "bg2":       "#2d1f0a",
            "card":      "#3a2810",
            "border":    "#f59e0b40",
            "primary":   "#f59e0b",
            "text":      "#fef3c7",
            "text2":     "#d97706",
            "muted":     "#92400e",
            "success":   "#10b981",
            "danger":    "#ef4444",
        }
    return {
        "bg":        "#fffbeb",
        "bg2":       "#fef3c7",
        "card":      "#ffffff",
        "border":    "#f59e0b60",
        "primary":   "#b45309",
        "text":      "#1c1410",
        "text2":     "#92400e",
        "muted":     "#78350f",
        "success":   "#059669",
        "danger":    "#dc2626",
    }

T = get_theme()

st.markdown(f"""
<style>
  .stApp {{ background-color: {T["bg"]}; }}
  .block-container {{ padding-top: 1.2rem; }}
  section[data-testid="stSidebar"] {{ background-color: {T["bg2"]} !important; }}
  .stTabs [data-baseweb="tab-list"] {{ gap: 3px; background: {T["bg2"]}; padding: 4px; border-radius: 8px; }}
  .stTabs [data-baseweb="tab"] {{
    padding: 6px 14px; border-radius: 6px;
    font-weight: 600; font-size: 0.78rem; color: {T["text2"]};
  }}
  .stTabs [aria-selected="true"] {{
    background: {T["primary"]} !important; color: #1a1208 !important;
  }}
  .metric-row {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 10px; }}
  .metric-box {{
    background: {T["card"]}; border: 1px solid {T["border"]};
    border-radius: 10px; padding: 12px 16px; flex: 1; min-width: 120px;
  }}
  .metric-label {{ font-size: 0.68rem; color: {T["muted"]}; font-weight: 600;
                   text-transform: uppercase; letter-spacing: 0.05em; }}
  .metric-value {{ font-size: 1.4rem; font-weight: 800; color: {T["primary"]}; }}
  .metric-unit  {{ font-size: 0.72rem; color: {T["text2"]}; margin-left: 3px; }}
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
  .dash-lbl {{ font-size: 0.72rem; color: {T["muted"]}; font-weight: 600;
               text-transform: uppercase; letter-spacing: 0.05em; }}
  footer {{ visibility: hidden; }}
  .stDataFrame {{ border-radius: 8px; overflow: hidden; }}
</style>
""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("## 🔧")
    with c2:
        st.markdown(f"### ShipPipe")
        st.caption("Marine Piping Designer")

    mode_label = "☀️ Light Mode" if st.session_state.dark_mode else "🌙 Dark Mode"
    if st.button(mode_label, use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    st.markdown("---")
    st.markdown("**Vessel / Project Info**")
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
            st.error("Invalid template. Download the template from the Dashboard tab.")

    st.markdown("---")
    st.caption("Built by [Suji Kumar C](https://sujikumar.com)")


# ── Velocity gauge ─────────────────────────────────────────────────────────────
def velocity_gauge(v_actual, v_min, v_max, v_rec, title="Flow Velocity"):
    dark = st.session_state.dark_mode
    bg = "#2d1f0a" if dark else "#fef3c7"
    fig, ax = plt.subplots(figsize=(4, 0.55))
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)
    ax.barh(0, v_max * 1.2, height=0.4, color="#3a2810" if dark else "#fed7aa", left=0)
    ax.barh(0, v_max - v_min, height=0.4, color="#10b981", left=v_min, alpha=0.4)
    color = "#f59e0b" if v_min <= v_actual <= v_max else "#ef4444"
    ax.barh(0, v_actual, height=0.4, color=color)
    ax.axvline(v_rec, color="#fbbf24", linewidth=1.5, linestyle="--")
    ax.set_xlim(0, v_max * 1.2)
    ax.set_yticks([])
    ax.tick_params(axis="x", colors="#d97706" if dark else "#92400e", labelsize=7)
    ax.spines[:].set_visible(False)
    tc = "#fef3c7" if dark else "#1c1410"
    ax.set_title(f"{title}: {v_actual:.2f} m/s", color=tc, fontsize=8, pad=2)
    plt.tight_layout(pad=0.1)
    return fig


# ── System renderer ────────────────────────────────────────────────────────────
def render_system(system_key: str, system_label: str):
    vrange = VELOCITY_RANGES[system_key]
    fluid  = vrange["fluid"]
    default_flow = max(5.0, float(vessel_dwt / 800 * 10))
    if system_key == "Compressed Air":
        default_flow = 30.0
    if system_key in ("Lube Oil", "Hydraulic"):
        default_flow = 20.0
    if system_key == "Sewage":
        default_flow = 5.0

    st.markdown(f"### {system_label} System")
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.markdown('<div class="sec-title">Flow Requirements</div>', unsafe_allow_html=True)
        flow_rate   = st.number_input("Flow Rate (m³/h)", 0.5, 5000.0, default_flow, 5.0, key=f"{system_key}_flow")
        pipe_length = st.number_input("Pipe Length (m)",         5.0,  500.0,  50.0, 5.0,       key=f"{system_key}_len")
        static_head = st.number_input("Static Head (m)",         0.0,  50.0,   8.0,  0.5,       key=f"{system_key}_head")
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

    # Save to session state for dashboard
    st.session_state.system_results[system_key] = {
        "label": system_label, "pipe": pipe, "pump": pump, "bom": bom,
        "flow": flow_rate, "length": pipe_length, "fluid": fluid,
    }

    with col2:
        st.markdown('<div class="sec-title">Pipe Sizing</div>', unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        m1.metric("Pipe Size", pipe["selected_nps"].split(" ")[0])
        m2.metric("Schedule", pipe["schedule"])
        m1.metric("OD", f'{pipe["OD_mm"]} mm')
        m2.metric("ID", f'{pipe["ID_mm"]} mm')
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
        st.markdown(f'<div class="info-card"><b>Material:</b> {mat["material"]}<br>'
                    f'<b>Standard:</b> {mat["standard"]}<br>{mat["note"]}</div>',
                    unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="sec-title">Pump Specification</div>', unsafe_allow_html=True)
        p1, p2 = st.columns(2)
        p1.metric("Total Head", f'{pump["total_head_m"]} m')
        p2.metric("Std Motor", f'{pump["recommended_motor_kw"]} kW')
        p1.metric("NPSHA", f'{pump["NPSHA_m"]} m')
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
        st.download_button("📥 Excel Spec Sheet", to_excel(pipe, pump, bom, system_label, vessel_name),
            f"ShipPipe_{system_key.replace(' ','_')}_{vessel_name.replace(' ','_')}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)
    with ec2:
        st.download_button("📄 PDF Spec Sheet", to_pdf(pipe, pump, bom, system_label, vessel_name),
            f"ShipPipe_{system_key.replace(' ','_')}_{vessel_name.replace(' ','_')}.pdf",
            "application/pdf", use_container_width=True)


# ── Dashboard ──────────────────────────────────────────────────────────────────
def render_dashboard():
    dark = st.session_state.dark_mode
    bg   = "#2d1f0a" if dark else "#fef3c7"
    tc   = "#fef3c7" if dark else "#1c1410"

    st.markdown("### Project Dashboard")
    st.caption(f"Vessel: **{vessel_name}** | LOA: {vessel_loa} m | DWT: {vessel_dwt} | Draft: {vessel_draft} m")

    results = st.session_state.system_results
    n_sys   = len(results)
    total_bom = sum(len(v["bom"]) for v in results.values()) if results else 0
    total_kw  = sum(v["pump"]["recommended_motor_kw"] for v in results.values()) if results else 0
    max_pipe  = max((v["pipe"]["OD_mm"] for v in results.values()), default=0)

    # KPI cards
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="dash-card"><div class="dash-num">{n_sys}</div>'
                f'<div class="dash-lbl">Systems Sized</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="dash-card"><div class="dash-num">{total_bom}</div>'
                f'<div class="dash-lbl">Total BOM Items</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="dash-card"><div class="dash-num">{total_kw:.0f} kW</div>'
                f'<div class="dash-lbl">Total Pump Power</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="dash-card"><div class="dash-num">{max_pipe:.0f} mm</div>'
                f'<div class="dash-lbl">Largest Pipe OD</div></div>', unsafe_allow_html=True)

    if not results:
        st.info("Go to any system tab, set your parameters, and results will appear here automatically.")
        # Template download
        st.markdown("---")
        st.markdown("**Download Vessel Template** — fill in and upload in the sidebar to pre-populate inputs")
        tpl = io.BytesIO()
        tdf = pd.DataFrame({
            "Field": ["Vessel Name", "LOA (m)", "DWT", "Draft (m)"],
            "Value": [vessel_name, vessel_loa, vessel_dwt, vessel_draft],
        })
        with pd.ExcelWriter(tpl, engine="openpyxl") as w:
            tdf.to_excel(w, sheet_name="Vessel Data", index=False)
        st.download_button("📥 Download Vessel Template", tpl.getvalue(),
            "ShipPipe_VesselTemplate.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        return

    st.markdown("---")
    # Comparison charts
    ch1, ch2 = st.columns(2)
    systems = list(results.keys())
    labels  = [s[:12] for s in systems]

    with ch1:
        st.markdown('<div class="sec-title">Pipe OD by System (mm)</div>', unsafe_allow_html=True)
        ods = [results[s]["pipe"]["OD_mm"] for s in systems]
        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor(bg); ax.set_facecolor(bg)
        bars = ax.barh(labels, ods, color="#f59e0b", edgecolor="#d97706", height=0.6)
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
        bars2 = ax2.barh(labels, kws, color="#10b981", edgecolor="#059669", height=0.6)
        ax2.bar_label(bars2, fmt="%.1f kW", color=tc, fontsize=8, padding=3)
        ax2.tick_params(colors=tc, labelsize=8)
        ax2.spines[:].set_visible(False)
        ax2.set_xlabel("Motor Power (kW)", color=tc, fontsize=8)
        plt.tight_layout()
        st.pyplot(fig2, use_container_width=True)

    # BOM breakdown pie
    ch3, ch4 = st.columns(2)
    with ch3:
        st.markdown('<div class="sec-title">BOM Items by System</div>', unsafe_allow_html=True)
        bom_counts = [len(results[s]["bom"]) for s in systems]
        fig3, ax3 = plt.subplots(figsize=(4, 3))
        fig3.patch.set_facecolor(bg); ax3.set_facecolor(bg)
        palette = ["#f59e0b","#fb923c","#fbbf24","#10b981","#14b8a6",
                   "#06b6d4","#3b82f6","#8b5cf6","#ec4899","#ef4444","#84cc16","#f97316"]
        wedges, texts, autotexts = ax3.pie(
            bom_counts, labels=labels, autopct="%1.0f%%",
            colors=palette[:len(systems)], textprops={"color": tc, "fontsize": 7},
            wedgeprops={"edgecolor": bg, "linewidth": 1.5}
        )
        for at in autotexts:
            at.set_color("#1a1208")
            at.set_fontsize(7)
        plt.tight_layout()
        st.pyplot(fig3, use_container_width=True)

    with ch4:
        st.markdown('<div class="sec-title">Pressure Drop by System (bar)</div>', unsafe_allow_html=True)
        dps = [results[s]["pipe"]["pressure_drop_bar"] for s in systems]
        fig4, ax4 = plt.subplots(figsize=(5, 3))
        fig4.patch.set_facecolor(bg); ax4.set_facecolor(bg)
        ax4.bar(labels, dps, color="#fb923c", edgecolor="#d97706", width=0.6)
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

    # Multi-system export
    st.markdown("---")
    st.markdown('<div class="sec-title">Export All Systems</div>', unsafe_allow_html=True)
    ec1, ec2, ec3 = st.columns(3)

    with ec1:
        all_xl = io.BytesIO()
        with pd.ExcelWriter(all_xl, engine="openpyxl") as writer:
            pd.DataFrame(rows).to_excel(writer, sheet_name="Summary", index=False)
            for s in systems:
                r = results[s]
                pipe_df = pd.DataFrame([r["pipe"]]).T.reset_index()
                pipe_df.columns = ["Parameter", "Value"]
                pump_df = pd.DataFrame([r["pump"]]).T.reset_index()
                pump_df.columns = ["Parameter", "Value"]
                sheet = s[:28].replace("/", "-").replace(" ", "_")
                pd.concat([pipe_df, pd.DataFrame([["", ""]]*2, columns=["Parameter","Value"]), pump_df]).to_excel(
                    writer, sheet_name=f"{sheet}_Pipe_Pump", index=False)
                r["bom"].to_excel(writer, sheet_name=f"{sheet}_BOM")
        st.download_button("📥 All Systems Excel",
            all_xl.getvalue(),
            f"ShipPipe_ALL_{vessel_name.replace(' ','_')}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)

    with ec2:
        tpl2 = io.BytesIO()
        tdf2 = pd.DataFrame({
            "Field": ["Vessel Name", "LOA (m)", "DWT", "Draft (m)"],
            "Value": [vessel_name, vessel_loa, vessel_dwt, vessel_draft],
        })
        with pd.ExcelWriter(tpl2, engine="openpyxl") as w:
            tdf2.to_excel(w, sheet_name="Vessel Data", index=False)
        st.download_button("📋 Vessel Template",
            tpl2.getvalue(),
            "ShipPipe_VesselTemplate.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)

    with ec3:
        bom_all = pd.concat(
            [v["bom"].assign(System=k) for k, v in results.items()],
            ignore_index=True
        )
        bom_xl = io.BytesIO()
        with pd.ExcelWriter(bom_xl, engine="openpyxl") as w:
            bom_all.to_excel(w, sheet_name="Master BOM", index=False)
        st.download_button("📦 Master BOM Excel",
            bom_xl.getvalue(),
            f"ShipPipe_MasterBOM_{vessel_name.replace(' ','_')}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f'<h2 style="color:{T["primary"]}; margin-bottom:2px;">🔧 ShipPipe</h2>', unsafe_allow_html=True)
st.markdown(f'<p style="color:{T["text2"]}; margin-top:0; font-size:0.9rem;">Marine Piping System Designer — 12 systems | Pipe sizing | Pump spec | BOM | Excel & PDF export</p>', unsafe_allow_html=True)
st.markdown("---")

# ── Tabs ────────────────────────────────────────────────────────────────────────
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
    "🔩 Lube Oil",
    "🔧 Hydraulic",
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
    st.markdown("## About ShipPipe")
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
**Suji Kumar C** - Marine Software Engineer, Shoft Shipyard, Gujarat

[sujikumar.com](https://sujikumar.com) | [LinkedIn](https://linkedin.com/in/sujikumar)
    """)

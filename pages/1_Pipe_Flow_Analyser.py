"""
pages/1_Pipe_Flow_Analyser.py

Module A of the capstone: Pipe Flow Analyser. Lets the user pick a fluid
(preset or user-defined), set pipe geometry and flow rate, and view
velocity, Reynolds number, friction factor, and pressure drop, plus an
interactive pressure-drop-vs-flow-rate plot and a CSV export.
"""

import io

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from engineering import Fluid, Pipe, PipeFlowAnalyzer

st.set_page_config(page_title="Pipe Flow Analyser", page_icon="🌊", layout="wide")

st.title("🌊 Pipe Flow Analyser")
st.subheader("Velocity, Reynolds number, friction factor, and pressure drop for pipe flow")

with st.expander("📖 How to use this module", expanded=False):
    st.markdown(
        """
        1. Pick a **fluid** — a built-in preset (water, air, crude oil)
           or **User-defined**, where you type in the density and
           viscosity yourself.
        2. Set the **pipe diameter**, **length**, and **roughness**
           (a measure of internal surface texture — smoother pipes like
           PVC have lower roughness than rough ones like concrete).
        3. Set the **flow rate** — how much fluid passes per second.
        4. Read the calculated **velocity, Reynolds number, friction
           factor**, and **pressure drop** below.
        5. The chart shows pressure drop across a range of flow rates,
           with your current setting highlighted.
        6. Use the **download button** to export the swept results as a CSV.

        All inputs must be positive numbers. Invalid inputs show a
        warning instead of crashing the app.
        """
    )


def build_fluid(fluid_choice: str, custom_density: float, custom_viscosity: float) -> Fluid:
    """
    Build a Fluid object from the sidebar selection.

    Args:
        fluid_choice: The selected option from the fluid selectbox —
            either a key in Fluid.PRESET_FLUIDS or "User-defined".
        custom_density: Density to use in kg/m^3 if fluid_choice is
            "User-defined".
        custom_viscosity: Viscosity to use in Pa.s if fluid_choice is
            "User-defined".

    Returns:
        A Fluid instance.

    Raises:
        ValueError: If a user-defined density or viscosity is not positive.
    """
    if fluid_choice == "User-defined":
        return Fluid("User-defined fluid", custom_density, custom_viscosity)
    return Fluid.from_preset(fluid_choice)


# ----------------------------------------------------------------------------
# Sidebar inputs
# ----------------------------------------------------------------------------
st.sidebar.header("⚙️ Fluid & Pipe Inputs")

fluid_options = list(Fluid.PRESET_FLUIDS.keys()) + ["User-defined"]
fluid_choice = st.sidebar.selectbox("Fluid", fluid_options, index=0)

if fluid_choice == "User-defined":
    custom_density = st.sidebar.number_input(
        "Density (kg/m³)", min_value=0.0, value=1000.0, step=10.0,
        help="Mass per unit volume of the fluid.",
    )
    custom_viscosity = st.sidebar.number_input(
        "Dynamic viscosity (Pa·s)", min_value=0.0, value=0.001, step=0.0001,
        format="%.5f",
        help="A measure of the fluid's resistance to flow/shear.",
    )
else:
    custom_density, custom_viscosity = 1000.0, 0.001  # unused placeholders

diameter_mm = st.sidebar.slider(
    "Pipe internal diameter, D (mm)", min_value=1.0, max_value=500.0, value=50.0, step=1.0,
    help="Internal diameter of the pipe bore.",
)

length_m = st.sidebar.number_input(
    "Pipe length, L (m)", min_value=0.0, max_value=10000.0, value=100.0, step=1.0,
    help="Total length of pipe the fluid travels through.",
)

roughness_mm = st.sidebar.selectbox(
    "Pipe roughness, ε",
    options=[
        ("Drawn tubing / copper (0.0015 mm)", 0.0015),
        ("PVC / plastic (0.0015 mm)", 0.0015),
        ("Commercial steel (0.045 mm)", 0.045),
        ("Galvanized iron (0.15 mm)", 0.15),
        ("Cast iron (0.26 mm)", 0.26),
        ("Concrete (1.0 mm)", 1.0),
    ],
    format_func=lambda x: x[0],
    index=2,
)[1]

flow_rate_lps = st.sidebar.slider(
    "Flow rate, Q (L/s)", min_value=0.0, max_value=50.0, value=5.0, step=0.1,
    help="Volume of fluid passing through the pipe per second.",
)

# ----------------------------------------------------------------------------
# Validation + calculation (error handling requirement)
# ----------------------------------------------------------------------------
try:
    fluid = build_fluid(fluid_choice, custom_density, custom_viscosity)
    pipe = Pipe(diameter_m=diameter_mm / 1000.0, length_m=length_m, roughness_m=roughness_mm / 1000.0)
    analyzer = PipeFlowAnalyzer(fluid, pipe)
    result = analyzer.analyze(flow_rate_lps / 1000.0)
except ValueError as exc:
    st.warning(f"⚠️ {exc}")
    st.info("Please correct the highlighted inputs in the sidebar to see results.")
    st.stop()

if flow_rate_lps == 0:
    st.warning("⚠️ Flow rate is 0 — velocity and pressure drop are both 0.")

# ----------------------------------------------------------------------------
# Results summary
# ----------------------------------------------------------------------------
st.markdown("### 📊 Results for current inputs")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Velocity", f"{result['velocity_ms']:.3f} m/s")
col2.metric("Reynolds number", f"{result['reynolds_number']:.0f}")
col3.metric("Flow regime", result["regime"])
col4.metric("Pressure drop", f"{result['pressure_drop_kpa']:.2f} kPa")

st.metric("Friction factor (Darcy)", f"{result['friction_factor']:.4f}")

# ----------------------------------------------------------------------------
# Chart: pressure drop vs flow rate sweep
# ----------------------------------------------------------------------------
st.markdown("### 📈 Pressure Drop vs Flow Rate")

max_sweep = max(flow_rate_lps * 2.0, 10.0)
sweep_lps = np.linspace(0.01, max_sweep, 60)
sweep_rows = []
for q in sweep_lps:
    r = analyzer.analyze(q / 1000.0)
    sweep_rows.append(r)

sweep_df = pd.DataFrame(sweep_rows)
sweep_df["flow_rate_lps"] = sweep_lps

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=sweep_df["flow_rate_lps"], y=sweep_df["pressure_drop_kpa"],
        mode="lines", name="Pressure drop",
        line=dict(color="#1f77b4", width=3),
    )
)
fig.add_trace(
    go.Scatter(
        x=[flow_rate_lps], y=[result["pressure_drop_kpa"]],
        mode="markers", name="Current operating point",
        marker=dict(color="red", size=12, symbol="circle"),
    )
)
fig.update_layout(
    xaxis_title="Flow rate (L/s)", yaxis_title="Pressure drop (kPa)",
    hovermode="x unified", height=450, margin=dict(l=10, r=10, t=30, b=10),
)
st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------------
# Results table + CSV export
# ----------------------------------------------------------------------------
st.markdown("### 📋 Swept Results Table")

display_df = pd.DataFrame(
    {
        "Flow rate (L/s)": sweep_df["flow_rate_lps"].round(2),
        "Velocity (m/s)": sweep_df["velocity_ms"].round(3),
        "Reynolds number": sweep_df["reynolds_number"].round(0).astype(int),
        "Friction factor": sweep_df["friction_factor"].round(4),
        "Pressure drop (kPa)": sweep_df["pressure_drop_kpa"].round(2),
        "Regime": sweep_df["regime"],
    }
)
st.dataframe(display_df.iloc[::5].reset_index(drop=True), use_container_width=True, hide_index=True)

csv_buffer = io.StringIO()
display_df.to_csv(csv_buffer, index=False)
st.download_button(
    label="⬇️ Download full swept results as CSV",
    data=csv_buffer.getvalue(),
    file_name="pipe_flow_results.csv",
    mime="text/csv",
)

st.markdown("---")
st.caption(
    "Darcy-Weisbach pressure drop · Friction factor via Swamee-Jain (turbulent) / 64/Re (laminar) · "
    "Verified against hand-calculated worked examples."
)

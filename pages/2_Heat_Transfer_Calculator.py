"""
pages/2_Heat_Transfer_Calculator.py

Module B of the capstone: Heat Transfer Calculator. Two calculations:
  1. Steady-state conduction through a flat wall (Fourier's Law).
  2. Newton's Law of Cooling: time to cool an object from T0 to a target
     temperature in a constant-temperature ambient, plus a
     temperature-vs-time plot of the cooling process.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from engineering import FlatWallConduction, NewtonianCooling

st.set_page_config(page_title="Heat Transfer Calculator", page_icon="🔥", layout="wide")

st.title("🔥 Heat Transfer Calculator")
st.subheader("Steady-state conduction (Fourier's Law) and Newton's Law of Cooling")

with st.expander("📖 How to use this module", expanded=False):
    st.markdown(
        """
        This page has two independent calculators:

        **1. Steady-state conduction** — heat flowing through a single
        flat layer of material (e.g. a wall) between a hot face and a
        cold face, using Fourier's Law: Q = k·A·(T_hot − T_cold) / L.

        **2. Newton's Law of Cooling** — how long it takes an object at
        an initial temperature to cool (or heat) to a target temperature
        while sitting in a constant-temperature ambient fluid, plus a
        plot of temperature against time.

        Every input below has a short physical description and its
        units. Invalid inputs (e.g. a target temperature the object can
        never physically reach) show a warning instead of crashing the app.
        """
    )

MATERIALS_K = {
    "Brick": 0.72, "Concrete": 1.4, "Glass": 0.96, "Wood (pine)": 0.13,
    "Fiberglass insulation": 0.04, "Steel": 45.0, "Aluminium": 205.0, "Copper": 385.0,
}

MATERIALS_C = {
    "Water": 4186.0, "Aluminium": 900.0, "Steel": 490.0, "Copper": 385.0,
    "Glass": 840.0, "Ice": 2100.0,
}

st.markdown("---")
st.markdown("## 1️⃣ Steady-State Conduction Through a Flat Wall")

col_a, col_b = st.columns([1, 1.4])

with col_a:
    material_name = st.selectbox(
        "Wall material", list(MATERIALS_K.keys()), index=0,
        help="Sets the thermal conductivity, k — how easily heat flows through the material. Higher k = better conductor.",
    )
    thickness_mm = st.slider(
        "Wall thickness, L (mm)", min_value=1.0, max_value=500.0, value=200.0, step=1.0,
        help="The distance heat has to travel through the wall.",
    )
    area_m2 = st.number_input(
        "Wall area, A (m²)", min_value=0.01, max_value=1000.0, value=10.0, step=0.5,
        help="The surface area of the wall normal to the direction of heat flow.",
    )
    t_hot = st.number_input(
        "Hot face temperature, T_hot (°C)", value=25.0, step=1.0,
        help="Temperature of the warmer side of the wall.",
    )
    t_cold = st.number_input(
        "Cold face temperature, T_cold (°C)", value=5.0, step=1.0,
        help="Temperature of the cooler side of the wall.",
    )

try:
    wall = FlatWallConduction(
        thermal_conductivity=MATERIALS_K[material_name],
        area_m2=area_m2,
        thickness_m=thickness_mm / 1000.0,
    )
    q_conduction = wall.heat_transfer_rate(t_hot, t_cold)
except ValueError as exc:
    st.warning(f"⚠️ {exc}")
    q_conduction = None

with col_b:
    if q_conduction is not None:
        st.metric("Heat transfer rate, Q", f"{q_conduction:.1f} W")
        if q_conduction < 0:
            st.info("Q is negative, meaning heat is actually flowing from the 'cold' face to the 'hot' face — check your temperatures.")
        st.caption(
            f"Fourier's Law: Q = k·A·(T_hot − T_cold)/L = "
            f"{MATERIALS_K[material_name]} × {area_m2} × ({t_hot} − {t_cold}) / {thickness_mm/1000:.3f}"
        )

st.markdown("---")
st.markdown("## 2️⃣ Newton's Law of Cooling")

col_c, col_d = st.columns([1, 1.4])

with col_c:
    c_material = st.selectbox(
        "Object material", list(MATERIALS_C.keys()), index=1,
        help="Sets the specific heat capacity, c — the energy needed to change the object's temperature by 1°C per kg.",
    )
    mass_kg = st.number_input(
        "Object mass, m (kg)", min_value=0.01, max_value=1000.0, value=1.0, step=0.1,
        help="The mass of the object that is cooling or heating.",
    )
    h_coeff = st.slider(
        "Convection coefficient, h (W/m²·K)", min_value=1.0, max_value=200.0, value=15.0, step=1.0,
        help="How effectively heat transfers between the object's surface and the surrounding fluid (higher = faster cooling, e.g. moving air or water vs still air).",
    )
    surface_area_m2 = st.number_input(
        "Object surface area, A (m²)", min_value=0.001, max_value=100.0, value=0.1, step=0.01,
        help="The surface area of the object exposed to the ambient fluid.",
    )
    t_initial = st.number_input(
        "Initial object temperature, T₀ (°C)", value=90.0, step=1.0,
        help="The object's starting temperature.",
    )
    t_ambient = st.number_input(
        "Ambient temperature, T∞ (°C)", value=20.0, step=1.0,
        help="The constant temperature of the surrounding air or fluid the object is cooling into.",
    )
    t_target = st.number_input(
        "Target temperature, T_target (°C)", value=30.0, step=1.0,
        help="The temperature you want to know the time to reach. Must be strictly between T∞ and T₀.",
    )

try:
    cooling = NewtonianCooling(
        mass_kg=mass_kg,
        specific_heat=MATERIALS_C[c_material],
        h=h_coeff,
        area_m2=surface_area_m2,
        t_ambient=t_ambient,
    )
    time_to_target_s = cooling.time_to_reach(t_initial, t_target)
    cooling_error = None
except ValueError as exc:
    cooling_error = str(exc)
    time_to_target_s = None

with col_d:
    if cooling_error:
        st.warning(f"⚠️ {cooling_error}")
    else:
        minutes = time_to_target_s / 60.0
        st.metric("Time to reach target", f"{time_to_target_s:.0f} s ({minutes:.1f} min)")
        st.caption(f"Thermal time constant, τ = (m·c)/(h·A) = {cooling.time_constant_s:.1f} s")

# ----------------------------------------------------------------------------
# Temperature vs time plot
# ----------------------------------------------------------------------------
if not cooling_error:
    st.markdown("### 📈 Temperature vs Time")

    plot_duration_s = time_to_target_s * 1.3
    time_points = np.linspace(0, plot_duration_s, 100)
    temps = [cooling.temperature_at(t_initial, t) for t in time_points]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=time_points, y=temps, mode="lines", name="Object temperature",
            line=dict(color="#d62728", width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[time_to_target_s], y=[t_target], mode="markers", name="Target reached",
            marker=dict(color="red", size=12, symbol="circle"),
        )
    )
    fig.add_hline(y=t_ambient, line_dash="dash", line_color="gray",
                   annotation_text="Ambient temperature", annotation_position="bottom right")
    fig.update_layout(
        xaxis_title="Time (s)", yaxis_title="Temperature (°C)",
        hovermode="x unified", height=450, margin=dict(l=10, r=10, t=30, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📋 Cooling Curve Table")
    curve_df = pd.DataFrame({"Time (s)": time_points.round(1), "Temperature (°C)": np.round(temps, 2)})
    st.dataframe(curve_df.iloc[::5].reset_index(drop=True), use_container_width=True, hide_index=True)

st.markdown("---")
st.caption(
    "Fourier's Law: Q = k·A·ΔT/L · Newton's Law of Cooling: T(t) = T∞ + (T₀−T∞)e^(−t/τ), τ=(m·c)/(h·A) · "
    "Verified against analytical worked examples."
)

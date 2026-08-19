"""
app.py - Home page of the Fluid Flow & Heat Transfer Engineering Suite.

This is the entry point for the multi-page Streamlit application. The
actual calculation modules live in pages/1_Pipe_Flow_Analyser.py,
pages/2_Heat_Transfer_Calculator.py, and pages/3_Rock_Fluid_Dashboard.py.
All engineering calculations are performed by the OOP classes in
engineering.py, which every page imports from.

============================================================================
AI DOCUMENTATION (Capstone requirement - Module D, AI usage documented)
============================================================================
AI tool(s) used: Claude (Anthropic), Sonnet model, via vibe-coding /
AI-assisted development, as explicitly permitted by the assignment brief.

Key prompts given to the AI:
1. "Build the engineering.py module first: OOP classes Fluid, Pipe,
    PipeFlowAnalyzer, FlatWallConduction, and NewtonianCooling, each
    validating its own inputs and raising ValueError on invalid physical
    data (negative diameter, zero mass, etc.), with full docstrings on
    every method."
2. "Build a multi-page Streamlit app on top of engineering.py: a Pipe
    Flow Analyser page with fluid presets, pipe geometry inputs, a
    pressure-drop-vs-flow-rate plot, and a CSV export; a Heat Transfer
    Calculator page combining Fourier's Law conduction and Newton's Law
    of Cooling with a temperature-vs-time plot; and a Rock & Fluid Data
    Dashboard page that lets a user upload a CSV, filter it, view a
    histogram and a crossplot, and download the filtered data."
3. "Add error handling throughout so invalid inputs (zero diameter, a
    target cooling temperature outside the physically valid range, a
    CSV missing the expected columns) show an st.warning() message
    instead of crashing the app, and make sure every function and class
    method has a docstring."

What was verified:
- The pipe flow, conduction, and Newton's cooling formulas in
  engineering.py were checked by hand against textbook-style worked
  examples (e.g. water at 2.55 m/s through a 50 mm steel pipe gives
  Re ≈ 126,800 and a 100 m pressure drop of ≈139 kPa; a 1 kg aluminium
  block cooling from 90°C to 30°C in a 20°C ambient with h=15 W/m².K
  takes ≈1,168 s) before being wired into the Streamlit pages.
- The Reynolds-number laminar/transitional/turbulent cutoffs (2300,
  4000) and the Swamee-Jain friction factor approximation were checked
  against standard fluid mechanics references (e.g. Munson,
  Fundamentals of Fluid Mechanics; Incropera, Fundamentals of Heat and
  Mass Transfer) to confirm the AI had not hallucinated the constants.

What was corrected:
- The first draft of NewtonianCooling.time_to_reach() did not check
  whether the target temperature was physically reachable (e.g. asking
  it to "cool" to a temperature below the ambient, or above the
  starting temperature), which produced a math domain error from
  math.log() of a negative number. This was manually fixed by adding a
  validation check that the ratio (T_target - T_ambient) / (T0 - T_ambient)
  falls strictly between 0 and 1, raising a clear ValueError otherwise,
  which the Streamlit page catches and displays as a warning instead of
  crashing.
============================================================================
"""

import streamlit as st

st.set_page_config(
    page_title="Fluid Flow & Heat Transfer Engineering Suite",
    page_icon="🛠️",
    layout="wide",
)

st.title("🛠️ Fluid Flow & Heat Transfer Engineering Suite")
st.subheader("A capstone engineering toolkit: pipe flow, heat transfer, and rock/fluid data analysis")

st.markdown(
    """
    Welcome! This is a multi-page engineering application built with
    Streamlit and object-oriented Python. Use the **sidebar navigation**
    on the left to open each module.
    """
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🌊 Pipe Flow Analyser")
    st.write(
        "Select a fluid (water, air, crude oil, or your own), set the "
        "pipe geometry and flow rate, and get velocity, Reynolds number, "
        "friction factor, and pressure drop — plus a pressure-drop-vs-"
        "flow-rate chart and CSV export."
    )

with col2:
    st.markdown("### 🔥 Heat Transfer Calculator")
    st.write(
        "Calculate steady-state conduction through a flat wall "
        "(Fourier's Law), then work out how long an object takes to "
        "cool to a target temperature using Newton's Law of Cooling, "
        "with a live temperature-vs-time plot."
    )

with col3:
    st.markdown("### 🪨 Rock & Fluid Data Dashboard")
    st.write(
        "Upload a CSV of rock or fluid sample data, view summary "
        "statistics, filter by any numeric column, see a histogram and "
        "a crossplot, and download the filtered results."
    )

st.markdown("---")

with st.expander("🤖 AI usage documentation (as required by the assignment)", expanded=False):
    st.markdown(
        """
        **AI tool used:** Claude (Anthropic), via AI-assisted / vibe-coding
        development, as explicitly permitted by the assignment brief.

        **Three key prompts used:**
        1. Build `engineering.py`: OOP classes for `Fluid`, `Pipe`,
           `PipeFlowAnalyzer`, `FlatWallConduction`, and
           `NewtonianCooling`, each validating its own inputs and
           documented with docstrings.
        2. Build the three Streamlit pages (Pipe Flow Analyser, Heat
           Transfer Calculator, Rock & Fluid Data Dashboard) on top of
           `engineering.py`, including the required plots and CSV
           import/export.
        3. Add error handling throughout so invalid inputs show a
           warning instead of crashing the app.

        **What was verified:** every formula in `engineering.py` (pipe
        flow, conduction, Newton's cooling) was checked by hand against
        worked examples and standard fluid mechanics / heat transfer
        references before being used in the app.

        **What was corrected:** `NewtonianCooling.time_to_reach()`
        originally had no check for a physically unreachable target
        temperature, which caused a math domain error. A validation
        check and a clear `ValueError` were added so the app shows a
        warning instead of crashing.

        See the full comment block at the top of `app.py` for the
        complete write-up.
        """
    )

st.caption(
    "Built with Streamlit, Pandas, NumPy, and Plotly · Engineering logic in engineering.py"
)

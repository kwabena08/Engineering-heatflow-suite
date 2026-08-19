"""
pages/3_Rock_Fluid_Dashboard.py

Module C of the capstone: Rock & Fluid Data Dashboard. Lets the user
upload a CSV of rock or fluid sample data (or load the bundled sample
dataset), view summary statistics, filter by any numeric column, see a
histogram and a crossplot, and download the filtered results as a CSV.
"""

import io
import os

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Rock & Fluid Data Dashboard", page_icon="🪨", layout="wide")

st.title("🪨 Rock & Fluid Data Dashboard")
st.subheader("Upload, summarise, filter, and visualise rock or fluid sample data")

with st.expander("📖 How to use this module", expanded=False):
    st.markdown(
        """
        1. **Upload a CSV** of rock or fluid sample data using the
           uploader below, or click **Load sample data** to try the
           dashboard with a bundled example dataset (60 synthetic rock
           samples with porosity and permeability).
        2. Review the **summary statistics** table.
        3. Use the **filter** controls to narrow the data — e.g. show
           only samples where porosity is greater than a chosen value.
        4. View the **histogram** and **crossplot** below, which update
           with your filter.
        5. **Download** the filtered data as a CSV.

        The dashboard works with any CSV that has at least one numeric
        column. If it doesn't find columns named "Porosity" and
        "Permeability", you can pick which columns to plot yourself.
        """
    )


def load_sample_data() -> pd.DataFrame:
    """
    Load the bundled example rock/fluid dataset.

    Returns:
        A DataFrame of synthetic rock sample data (Sample_ID, Rock_Type,
        Depth_m, Porosity_pct, Permeability_mD, Grain_Density_kg_m3).
    """
    sample_path = os.path.join(os.path.dirname(__file__), "..", "sample_data", "rock_fluid_sample.csv")
    return pd.read_csv(sample_path)


# ----------------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------------
st.markdown("### 📁 Load data")
col_up, col_sample = st.columns([2, 1])

with col_up:
    uploaded_file = st.file_uploader("Upload a CSV of rock or fluid data", type=["csv"])

with col_sample:
    st.write("")
    st.write("")
    use_sample = st.button("📎 Load sample data instead")

if "dashboard_df" not in st.session_state:
    st.session_state["dashboard_df"] = None

if uploaded_file is not None:
    try:
        st.session_state["dashboard_df"] = pd.read_csv(uploaded_file)
    except Exception as exc:  # noqa: BLE001 - want to catch any parse failure and show it
        st.warning(f"⚠️ Could not read that file as a CSV ({exc}). Please check the file and try again.")
        st.session_state["dashboard_df"] = None
elif use_sample:
    st.session_state["dashboard_df"] = load_sample_data()

df = st.session_state["dashboard_df"]

if df is None:
    st.info("⬆️ Upload a CSV or click 'Load sample data' to get started.")
    st.stop()

if df.empty:
    st.warning("⚠️ The loaded file has no rows. Please upload a CSV with data.")
    st.stop()

numeric_cols = df.select_dtypes(include="number").columns.tolist()
if not numeric_cols:
    st.warning("⚠️ This CSV has no numeric columns to filter or plot. Please upload a different file.")
    st.dataframe(df, use_container_width=True)
    st.stop()

# ----------------------------------------------------------------------------
# Summary statistics
# ----------------------------------------------------------------------------
st.markdown("### 📊 Summary Statistics")
st.dataframe(df.describe().round(3), use_container_width=True)

# ----------------------------------------------------------------------------
# Filtering
# ----------------------------------------------------------------------------
st.markdown("### 🔎 Filter Data")

default_col_idx = 0
for i, c in enumerate(numeric_cols):
    if "poros" in c.lower():
        default_col_idx = i
        break

filter_col = st.selectbox("Filter by column", numeric_cols, index=default_col_idx)
col_min, col_max = float(df[filter_col].min()), float(df[filter_col].max())

if col_min == col_max:
    st.info(f"All values in '{filter_col}' are the same ({col_min}), so no filtering range is available.")
    filtered_df = df.copy()
else:
    threshold = st.slider(
        f"Show only samples where {filter_col} >",
        min_value=col_min, max_value=col_max,
        value=col_min, step=(col_max - col_min) / 100,
    )
    filtered_df = df[df[filter_col] > threshold]

st.write(f"Showing **{len(filtered_df)}** of **{len(df)}** samples.")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)

if filtered_df.empty:
    st.warning("⚠️ No samples match this filter. Try lowering the threshold.")
    st.stop()

# ----------------------------------------------------------------------------
# Charts
# ----------------------------------------------------------------------------
st.markdown("### 📈 Charts")

chart_col1, chart_col2 = st.columns(2)


def guess_column(columns: list, keyword: str, fallback_index: int) -> str:
    """
    Guess which column name best matches a keyword (e.g. 'poros').

    Args:
        columns: List of candidate column names.
        keyword: Lowercase substring to search for, e.g. 'poros'.
        fallback_index: Index to fall back to if no match is found.

    Returns:
        The best-matching column name.
    """
    for c in columns:
        if keyword in c.lower():
            return c
    return columns[min(fallback_index, len(columns) - 1)]


with chart_col1:
    st.markdown("**Histogram**")
    hist_col = st.selectbox(
        "Column to histogram",
        numeric_cols,
        index=numeric_cols.index(guess_column(numeric_cols, "poros", 0)),
        key="hist_col",
    )
    fig_hist = px.histogram(filtered_df, x=hist_col, nbins=20)
    fig_hist.update_layout(height=400, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_hist, use_container_width=True)

with chart_col2:
    st.markdown("**Crossplot**")
    x_default = guess_column(numeric_cols, "poros", 0)
    y_default = guess_column(numeric_cols, "perm", min(1, len(numeric_cols) - 1))
    x_col = st.selectbox("X-axis column", numeric_cols, index=numeric_cols.index(x_default), key="x_col")
    y_col = st.selectbox("Y-axis column", numeric_cols, index=numeric_cols.index(y_default), key="y_col")

    color_col = None
    non_numeric_cols = df.select_dtypes(exclude="number").columns.tolist()
    if non_numeric_cols:
        color_col = st.selectbox("Colour by (optional)", ["None"] + non_numeric_cols, index=0, key="color_col")
        color_col = None if color_col == "None" else color_col

    fig_cross = px.scatter(filtered_df, x=x_col, y=y_col, color=color_col)
    fig_cross.update_layout(height=400, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_cross, use_container_width=True)

# ----------------------------------------------------------------------------
# Download filtered data
# ----------------------------------------------------------------------------
st.markdown("### ⬇️ Download Filtered Data")
csv_buffer = io.StringIO()
filtered_df.to_csv(csv_buffer, index=False)
st.download_button(
    label="Download filtered data as CSV",
    data=csv_buffer.getvalue(),
    file_name="filtered_rock_fluid_data.csv",
    mime="text/csv",
)

st.markdown("---")
st.caption("Tip: click 'Load sample data' above to try this dashboard instantly without your own CSV.")

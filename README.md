# 🛠️ Fluid Flow & Heat Transfer Engineering Suite

This is a multi-page Streamlit capstone application that brings together three engineering tools built on a shared object-oriented calculation engine (`engineering.py`). The **Pipe Flow Analyser** lets a user pick a fluid (water, air, crude oil, or their own custom properties), set pipe geometry and flow rate, and instantly see velocity, Reynolds number, friction factor, and pressure drop, complete with a pressure-drop-vs-flow-rate chart and CSV export. The **Heat Transfer Calculator** combines steady-state conduction through a flat wall (Fourier's Law) with Newton's Law of Cooling, calculating how long an object takes to cool to a target temperature and plotting the full temperature-vs-time curve. The **Rock & Fluid Data Dashboard** lets a user upload any CSV of sample data (or load a bundled example dataset), view summary statistics, filter by any numeric column, generate a histogram and a crossplot, and download the filtered results. Every calculation class validates its own inputs and raises clear errors that the UI catches and displays as warnings instead of crashes.

**Live app URL:** _[Add your Streamlit Community Cloud URL here after deploying, e.g. https://your-app-name.streamlit.app]_

## Project structure

```
fluid-heat-suite/
├── app.py                              # Home page (multi-page app entry point)
├── engineering.py                      # OOP classes: Fluid, Pipe, PipeFlowAnalyzer,
│                                        #   FlatWallConduction, NewtonianCooling
├── pages/
│   ├── 1_Pipe_Flow_Analyser.py         # Module A
│   ├── 2_Heat_Transfer_Calculator.py   # Module B
│   └── 3_Rock_Fluid_Dashboard.py       # Module C
├── sample_data/
│   └── rock_fluid_sample.csv           # Example dataset for Module C
├── requirements.txt
└── README.md
```

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## AI usage

This project was built using AI-assisted ("vibe coding") development with Claude (Anthropic), as permitted by the assignment brief. Full documentation of the AI tools used, the key prompts given, what was verified against hand calculations and standard references, and what was manually corrected is included as a comment block at the top of `app.py`, and is also viewable inside the running app under the "AI usage documentation" section on the Home page.

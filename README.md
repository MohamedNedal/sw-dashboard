# ☀️ Space Weather Dashboard

A local, real-time space-weather dashboard you run on your Mac (or any
machine with Python + internet). It pulls live data from public space-weather
services and presents the current state of the Sun–Earth system in one place:

- **🛰️ Overview** — current NOAA R/S/G scales, latest GOES X-ray flare class,
  solar-wind speed/density, IMF Bz, a planetary **Kp** gauge, and a 24-hour
  flare-probability snapshot.
- **🌞 Imagery** — latest solar images from selected spacecraft/instruments
  (SDO **AIA** & **HMI**, SOHO **LASCO**, **STEREO**) via the Helioviewer API.
- **📈 Time Series** — GOES **X-ray** flux (with flare-class bands), integral
  **proton** and **electron** fluxes, **solar wind** speed & **IMF Bz**, and
  the **Kp** index.
- **🔥 Flares** — NOAA SWPC C/M/X flare and proton-event probabilities for the
  next 3 days, plus the full 3-day forecast discussion.
- **🌪️ HUXt / CME** — configure and run a cone-CME simulation of the inner
  heliosphere with the **HUXt** model (with a kinematic fallback if HUXt isn't
  installed), including Earth-arrival diagnostics.
- **🪐 Spacecraft** — a top-down view of the inner heliosphere showing the
  current positions of the planets and key spacecraft (STEREO-A, Parker Solar
  Probe, Solar Orbiter, BepiColombo) from JPL Horizons via SunPy.

The UI auto-refreshes so it always shows near-real-time conditions.

## Data sources

| Panel | Source |
|-------|--------|
| Scales, X-ray, particles, solar wind, Kp, forecasts | [NOAA SWPC](https://services.swpc.noaa.gov) |
| Solar imagery | [Helioviewer API](https://api.helioviewer.org) |
| Spacecraft/planet positions | JPL Horizons (via [SunPy](https://sunpy.org)) |
| CME modelling | [HUXt](https://github.com/University-of-Reading-Space-Science/HUXt) |

All sources are public; no API keys are required.

## Quick start (macOS)

### Option A — conda (recommended, includes the real HUXt model)

HUXt requires Python ≥ 3.12, so use a dedicated conda environment:

```bash
git clone https://github.com/mohamednedal/sw-dashboard.git
cd sw-dashboard
conda env create -f environment.yml   # Python 3.12 + deps + HUXt
conda activate swdash
./run.sh                              # installs into the active env and launches
```

### Option B — plain virtualenv (no real HUXt; kinematic CME fallback)

Works on Python 3.10/3.11. `run.sh` creates a local `.venv`, installs
dependencies, and launches the dashboard at <http://localhost:8501>:

```bash
git clone https://github.com/mohamednedal/sw-dashboard.git
cd sw-dashboard
./run.sh
```

`run.sh` detects an already-active conda/virtualenv and installs into it;
otherwise it creates `.venv`. It launches via `python -m streamlit` to avoid
stale `streamlit` console-script shims.

### Manual setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run swdash/app.py
```

### About the HUXt CME model

The HUXt panel works in a kinematic-approximation mode out of the box. The
**conda environment (Option A)** installs the full physical model for you. To
add it manually to an existing Python ≥ 3.12 environment:

```bash
pip install "git+https://github.com/University-of-Reading-Space-Science/HUXt.git"
```

> ⚠️ HUXt pins `sunpy >= 7.1`, which needs **Python ≥ 3.12**. On Python 3.11 or
> earlier the install fails with an unsatisfiable `sunpy` requirement — use the
> conda environment (or any 3.12+ interpreter) for the real model.

To drive HUXt with real MAS coronal boundary conditions (instead of the
built-in synthetic stream), tick **"Use MAS coronal boundary"** in the panel —
the first run downloads the required map for the current Carrington rotation.

### Optional science extras

The libraries below are listed (commented) in `requirements.txt` for deeper
analysis and additional missions:

- **aiapy** — calibrated SDO/AIA imagery
- **pyspedas** — heliophysics mission data (THEMIS, MMS, …)
- **sunkit-image** — extra solar image processing

## Project layout

```
swdash/
├── app.py              # Streamlit entry point (tabs + sidebar + auto-refresh)
├── config.py           # endpoints, imagery sources, spacecraft list
├── cache.py            # Streamlit-cached wrappers (per-feed TTLs)
├── data/               # framework-agnostic data layer
│   ├── http.py         # requests helper + DataUnavailable error
│   ├── swpc.py         # NOAA SWPC: X-rays, particles, solar wind, Kp, scales
│   ├── flares.py       # flare/proton probabilities
│   ├── imagery.py      # Helioviewer imagery
│   ├── spacecraft.py   # JPL Horizons positions via SunPy
│   └── huxt_model.py   # HUXt runner (+ synthetic boundary)
└── panels/             # one module per dashboard tab
tests/                  # offline parser tests (no network needed)
```

The `data/` layer is deliberately independent of Streamlit: each network
`fetch_*` is paired with a pure `parse_*` so the parsing logic is unit-tested
offline.

## Running the tests

```bash
pip install pytest pandas numpy requests
python -m pytest tests/ -q
```

The tests use captured-format fixtures and need no internet connection.

## Notes

- Designed for research and educational use; not an operational forecast
  product. Always defer to official sources (e.g. NOAA SWPC) for decisions.
- Panels fail gracefully: if a single feed is unreachable, that section shows a
  warning while the rest of the dashboard keeps working.
- Live auto-refresh uses `streamlit-autorefresh` (included in
  `requirements.txt`). Without it, use the **🔄 Refresh now** button.

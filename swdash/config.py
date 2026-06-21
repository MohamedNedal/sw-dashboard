"""Central configuration for the space-weather dashboard.

All network endpoints, imagery source definitions and spacecraft lists live
here so the rest of the code stays declarative and easy to tweak.
"""
from __future__ import annotations

APP_TITLE = "Space Weather Dashboard"
APP_ICON = "☀️"  # sun
DEFAULT_REFRESH_SECONDS = 120  # auto-refresh cadence for real-time panels

# Network timeout (seconds) for every outbound HTTP request.
HTTP_TIMEOUT = 30

# ---------------------------------------------------------------------------
# NOAA SWPC real-time products (public, no auth required)
# ---------------------------------------------------------------------------
SWPC = {
    # GOES X-ray flux (the standard flare proxy)
    "xray_1d": "https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json",
    "xray_7d": "https://services.swpc.noaa.gov/json/goes/primary/xrays-7-day.json",
    "xray_flares": "https://services.swpc.noaa.gov/json/goes/primary/xray-flares-7-day.json",
    # GOES energetic particles
    "protons_1d": "https://services.swpc.noaa.gov/json/goes/primary/integral-protons-1-day.json",
    "electrons_1d": "https://services.swpc.noaa.gov/json/goes/primary/integral-electrons-1-day.json",
    # Real-time solar wind (DSCOVR, ACE backup) as array-of-arrays products
    "sw_plasma_1d": "https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json",
    "sw_mag_1d": "https://services.swpc.noaa.gov/products/solar-wind/mag-1-day.json",
    # Geomagnetic activity
    "kp_1m": "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json",
    # Current NOAA R/S/G scales
    "scales": "https://services.swpc.noaa.gov/products/noaa-scales.json",
    # Forecasts
    "solar_prob": "https://services.swpc.noaa.gov/json/solar_probabilities.json",
    "forecast_3day": "https://services.swpc.noaa.gov/text/3-day-forecast.txt",
}

# ---------------------------------------------------------------------------
# Helioviewer imagery (https://api.helioviewer.org)
# ---------------------------------------------------------------------------
HELIOVIEWER_BASE = "https://api.helioviewer.org/v2"

# Curated full-disk / coronagraph layers keyed by a friendly label.
# `image_scale` is arcsec/pixel chosen so a ~1024 px frame nicely fits the FOV.
# Source IDs follow Helioviewer's getDataSources tree; the imagery module can
# also discover sources live, so this is a sensible default menu only.
IMAGERY_SOURCES: dict[str, dict] = {
    "SDO/AIA 171 (corona, quiet)": {"source_id": 10, "image_scale": 2.5},
    "SDO/AIA 193 (corona, hot)": {"source_id": 11, "image_scale": 2.5},
    "SDO/AIA 211 (active regions)": {"source_id": 12, "image_scale": 2.5},
    "SDO/AIA 304 (chromosphere)": {"source_id": 13, "image_scale": 2.5},
    "SDO/AIA 131 (flares)": {"source_id": 9, "image_scale": 2.5},
    "SDO/AIA 335 (active regions)": {"source_id": 14, "image_scale": 2.5},
    "SDO/AIA 094 (flares)": {"source_id": 8, "image_scale": 2.5},
    "SDO/AIA 1600 (photosphere/TR)": {"source_id": 15, "image_scale": 2.5},
    "SDO/HMI Continuum (sunspots)": {"source_id": 18, "image_scale": 2.5},
    "SDO/HMI Magnetogram": {"source_id": 19, "image_scale": 2.5},
    "SOHO/LASCO C2 (coronagraph)": {"source_id": 4, "image_scale": 14.7},
    "SOHO/LASCO C3 (coronagraph)": {"source_id": 5, "image_scale": 56.0},
    "STEREO-A/EUVI 195": {"source_id": 21, "image_scale": 3.6},
    "STEREO-A/COR2": {"source_id": 25, "image_scale": 30.0},
}

DEFAULT_IMAGERY = [
    "SDO/AIA 171 (corona, quiet)",
    "SDO/AIA 193 (corona, hot)",
    "SDO/AIA 304 (chromosphere)",
    "SOHO/LASCO C2 (coronagraph)",
]

# ---------------------------------------------------------------------------
# Heliospheric bodies / spacecraft for the top-view plot.
# Names are JPL Horizons identifiers understood by sunpy.get_horizons_coord.
# ---------------------------------------------------------------------------
HELIO_BODIES: dict[str, dict] = {
    "Sun": {"id": "Sun", "color": "#FDB813", "kind": "star"},
    "Mercury": {"id": "Mercury", "color": "#9c9c9c", "kind": "planet"},
    "Venus": {"id": "Venus", "color": "#d8a25e", "kind": "planet"},
    "Earth": {"id": "Earth", "color": "#2a7de1", "kind": "planet"},
    "Mars": {"id": "Mars", "color": "#c1440e", "kind": "planet"},
    "STEREO-A": {"id": "STEREO-A", "color": "#e23bb0", "kind": "spacecraft"},
    "Parker Solar Probe": {"id": "Parker Solar Probe", "color": "#ffd24d", "kind": "spacecraft"},
    "Solar Orbiter": {"id": "Solar Orbiter", "color": "#52e3a4", "kind": "spacecraft"},
    "BepiColombo": {"id": "BepiColombo", "color": "#b07bff", "kind": "spacecraft"},
}

DEFAULT_BODIES = ["Sun", "Mercury", "Venus", "Earth", "Mars",
                  "STEREO-A", "Parker Solar Probe", "Solar Orbiter"]

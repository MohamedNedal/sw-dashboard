"""NOAA SWPC real-time data: X-rays, particles, solar wind, Kp, scales, flares.

Network functions are named ``fetch_*``; the pure transformation helpers are
named ``parse_*`` and operate on already-decoded JSON so they can be tested
offline against captured fixtures.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from swdash.config import SWPC
from swdash.data.http import get_json, get_text

# GOES X-ray classification uses the long (0.1-0.8 nm) channel.
XRAY_LONG_BAND = "0.1-0.8nm"
XRAY_SHORT_BAND = "0.05-0.4nm"


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------
def parse_product_table(rows: list[list]) -> pd.DataFrame:
    """Convert an SWPC 'products' array-of-arrays (header row first) to a frame."""
    if not rows or len(rows) < 2:
        return pd.DataFrame()
    header, *data = rows
    df = pd.DataFrame(data, columns=header)
    if "time_tag" in df.columns:
        df["time_tag"] = pd.to_datetime(df["time_tag"], utc=True, errors="coerce")
    for col in df.columns:
        if col != "time_tag":
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def flux_to_class(flux_wm2: float) -> str:
    """Map a long-channel X-ray flux (W/m^2) to a GOES flare class string."""
    if flux_wm2 is None or not np.isfinite(flux_wm2) or flux_wm2 <= 0:
        return "—"
    bands = [
        (1e-4, "X"),
        (1e-5, "M"),
        (1e-6, "C"),
        (1e-7, "B"),
        (0.0, "A"),
    ]
    for threshold, letter in bands:
        if flux_wm2 >= threshold:
            return f"{letter}{flux_wm2 / threshold:.1f}" if threshold else f"A{flux_wm2 / 1e-8:.1f}"
    return "A0.0"


# ---------------------------------------------------------------------------
# X-ray flux
# ---------------------------------------------------------------------------
def parse_xrays(raw: list[dict]) -> pd.DataFrame:
    """Return a frame indexed by time with 'short' and 'long' flux columns."""
    if not raw:
        return pd.DataFrame()
    df = pd.DataFrame(raw)
    df["time_tag"] = pd.to_datetime(df["time_tag"], utc=True, errors="coerce")
    df["flux"] = pd.to_numeric(df["flux"], errors="coerce")
    wide = df.pivot_table(index="time_tag", columns="energy", values="flux", aggfunc="last")
    out = pd.DataFrame(index=wide.index)
    out["long"] = wide.get(XRAY_LONG_BAND)
    out["short"] = wide.get(XRAY_SHORT_BAND)
    return out.sort_index()


def fetch_xrays(window: str = "1d") -> pd.DataFrame:
    url = SWPC["xray_7d" if window == "7d" else "xray_1d"]
    return parse_xrays(get_json(url))


def parse_xray_flares(raw: list[dict]) -> pd.DataFrame:
    if not raw:
        return pd.DataFrame()
    df = pd.DataFrame(raw)
    for col in ("begin_time", "max_time", "end_time"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")
    return df


def fetch_xray_flares() -> pd.DataFrame:
    return parse_xray_flares(get_json(SWPC["xray_flares"]))


# ---------------------------------------------------------------------------
# Energetic particles
# ---------------------------------------------------------------------------
def _parse_particles(raw: list[dict]) -> pd.DataFrame:
    if not raw:
        return pd.DataFrame()
    df = pd.DataFrame(raw)
    df["time_tag"] = pd.to_datetime(df["time_tag"], utc=True, errors="coerce")
    df["flux"] = pd.to_numeric(df["flux"], errors="coerce")
    wide = df.pivot_table(index="time_tag", columns="energy", values="flux", aggfunc="last")
    return wide.sort_index()


def fetch_protons() -> pd.DataFrame:
    return _parse_particles(get_json(SWPC["protons_1d"]))


def fetch_electrons() -> pd.DataFrame:
    return _parse_particles(get_json(SWPC["electrons_1d"]))


# ---------------------------------------------------------------------------
# Solar wind (real-time DSCOVR/ACE)
# ---------------------------------------------------------------------------
def fetch_solar_wind_plasma() -> pd.DataFrame:
    """Columns: density (p/cc), speed (km/s), temperature (K)."""
    df = parse_product_table(get_json(SWPC["sw_plasma_1d"]))
    return df.set_index("time_tag") if "time_tag" in df.columns else df


def fetch_solar_wind_mag() -> pd.DataFrame:
    """Columns: bx_gsm, by_gsm, bz_gsm, lon_gsm, lat_gsm, bt (nT)."""
    df = parse_product_table(get_json(SWPC["sw_mag_1d"]))
    return df.set_index("time_tag") if "time_tag" in df.columns else df


# ---------------------------------------------------------------------------
# Planetary K index
# ---------------------------------------------------------------------------
def fetch_kp() -> pd.DataFrame:
    df = parse_product_table(get_json(SWPC["kp_1m"]))
    return df.set_index("time_tag") if "time_tag" in df.columns else df


# ---------------------------------------------------------------------------
# NOAA R/S/G scales (current conditions)
# ---------------------------------------------------------------------------
def fetch_scales() -> dict:
    """Return the most recent R/S/G scale block as a flat dict."""
    raw = get_json(SWPC["scales"])
    if not isinstance(raw, dict) or not raw:
        return {}
    # Keys are stringified day offsets; "0" is the current day.
    block = raw.get("0") or raw[sorted(raw)[0]]
    out = {}
    for scale in ("R", "S", "G"):
        node = block.get(scale, {}) if isinstance(block, dict) else {}
        out[scale] = {"scale": node.get("Scale"), "text": node.get("Text")}
    return out


# ---------------------------------------------------------------------------
# 3-day forecast text
# ---------------------------------------------------------------------------
def fetch_forecast_text() -> str:
    return get_text(SWPC["forecast_3day"])

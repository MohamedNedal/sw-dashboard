"""Streamlit entry point for the Space Weather Dashboard.

Run with:  streamlit run swdash/app.py
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone

# Streamlit runs this file as a top-level script, putting swdash/ (not the repo
# root) on sys.path. Add the repo root so the `swdash` package is importable.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import streamlit as st

from swdash.config import APP_ICON, APP_TITLE, DEFAULT_REFRESH_SECONDS
from swdash.panels import flares, huxt, imagery, overview, spacecraft, timeseries

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")


def _autorefresh(seconds: int):
    """Auto-refresh if streamlit-autorefresh is available, else no-op."""
    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=seconds * 1000, key="swdash_autorefresh")
        return True
    except Exception:  # noqa: BLE001
        return False


def main():
    st.title(f"{APP_ICON} {APP_TITLE}")

    with st.sidebar:
        st.header("Controls")
        auto = st.toggle("Auto-refresh", value=True)
        interval = st.number_input("Refresh interval (s)", 30, 1800,
                                   DEFAULT_REFRESH_SECONDS, 30)
        if st.button("🔄 Refresh now", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        st.caption("Data: NOAA SWPC, Helioviewer, JPL Horizons. "
                   "For research/educational use.")

    has_autorefresh = False
    if auto:
        has_autorefresh = _autorefresh(int(interval))

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    note = "" if has_autorefresh else " · (install streamlit-autorefresh for live updates)"
    st.caption(f"Last loaded: {now}{note}")

    tabs = st.tabs([
        "🛰️ Overview", "🌞 Imagery", "📈 Time Series",
        "🔥 Flares", "🌪️ HUXt / CME", "🪐 Spacecraft",
    ])
    with tabs[0]:
        overview.render()
    with tabs[1]:
        imagery.render()
    with tabs[2]:
        timeseries.render()
    with tabs[3]:
        flares.render()
    with tabs[4]:
        huxt.render()
    with tabs[5]:
        spacecraft.render()


if __name__ == "__main__":
    main()

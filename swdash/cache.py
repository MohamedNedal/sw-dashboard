"""Streamlit-cached wrappers around the network data layer.

Centralising the cache here keeps the panels clean and lets us tune TTLs per
data product (real-time feeds refresh often, forecasts and ephemerides rarely).
"""
from __future__ import annotations

from datetime import datetime

import streamlit as st

from swdash.data import flares, imagery, spacecraft, swpc


@st.cache_data(ttl=60, show_spinner=False)
def xrays(window: str = "1d"):
    return swpc.fetch_xrays(window)


@st.cache_data(ttl=300, show_spinner=False)
def xray_flares():
    return swpc.fetch_xray_flares()


@st.cache_data(ttl=300, show_spinner=False)
def protons():
    return swpc.fetch_protons()


@st.cache_data(ttl=300, show_spinner=False)
def electrons():
    return swpc.fetch_electrons()


@st.cache_data(ttl=60, show_spinner=False)
def solar_wind_plasma():
    return swpc.fetch_solar_wind_plasma()


@st.cache_data(ttl=60, show_spinner=False)
def solar_wind_mag():
    return swpc.fetch_solar_wind_mag()


@st.cache_data(ttl=300, show_spinner=False)
def kp():
    return swpc.fetch_kp()


@st.cache_data(ttl=300, show_spinner=False)
def scales():
    return swpc.fetch_scales()


@st.cache_data(ttl=3600, show_spinner=False)
def solar_probabilities():
    return flares.fetch_solar_probabilities()


@st.cache_data(ttl=1800, show_spinner=False)
def forecast_text():
    return swpc.fetch_forecast_text()


@st.cache_data(ttl=300, show_spinner=True)
def latest_image(label: str, size: int = 1024) -> bytes:
    return imagery.latest_image(label, size=size)


@st.cache_data(ttl=3600, show_spinner=True)
def positions(bodies: tuple[str, ...], day_key: str):
    # day_key (e.g. an ISO date) busts the cache once per day.
    return spacecraft.get_positions(list(bodies))

"""Top-level 'current conditions' panel: NOAA scales, Kp, X-ray, solar wind."""
from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from swdash import cache
from swdash.data.swpc import flux_to_class
from swdash.panels.common import guard, style_fig


def _kp_gauge(kp_value: float):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=kp_value,
        title={"text": "Planetary Kp"},
        gauge={
            "axis": {"range": [0, 9]},
            "bar": {"color": "#ffffff"},
            "steps": [
                {"range": [0, 4], "color": "#2e7d32"},
                {"range": [4, 5], "color": "#f9a825"},
                {"range": [5, 7], "color": "#ef6c00"},
                {"range": [7, 9], "color": "#c62828"},
            ],
        },
    ))
    return style_fig(fig, height=260)


def render():
    st.subheader("Current Space Weather Conditions")

    # --- NOAA R/S/G scales ---------------------------------------------------
    with guard("NOAA scales"):
        sc = cache.scales()
        c1, c2, c3 = st.columns(3)
        labels = {
            "R": ("Radio Blackouts", c1),
            "S": ("Solar Radiation", c2),
            "G": ("Geomagnetic Storm", c3),
        }
        for key, (name, col) in labels.items():
            node = sc.get(key, {})
            level = node.get("scale")
            text = node.get("text") or "none"
            col.metric(f"{key} · {name}", f"{key}{level}" if level not in (None, "0") else "none", text)

    st.divider()
    left, right = st.columns([1, 1])

    # --- Latest X-ray flux / flare class ------------------------------------
    with left:
        with guard("GOES X-ray flux"):
            xr = cache.xrays("1d")
            if not xr.empty and "long" in xr:
                latest = xr["long"].dropna()
                if len(latest):
                    val = float(latest.iloc[-1])
                    st.metric("Latest GOES X-ray (0.1–0.8 nm)",
                              flux_to_class(val), f"{val:.2e} W/m²")

        with guard("Solar wind"):
            plasma = cache.solar_wind_plasma()
            mag = cache.solar_wind_mag()
            cc = st.columns(3)
            if not plasma.empty:
                spd = plasma["speed"].dropna()
                den = plasma["density"].dropna()
                if len(spd):
                    cc[0].metric("Wind speed", f"{spd.iloc[-1]:.0f} km/s")
                if len(den):
                    cc[1].metric("Density", f"{den.iloc[-1]:.1f} p/cc")
            if not mag.empty and "bz_gsm" in mag:
                bz = mag["bz_gsm"].dropna()
                if len(bz):
                    cc[2].metric("IMF Bz", f"{bz.iloc[-1]:+.1f} nT")

    # --- Kp gauge ------------------------------------------------------------
    with right:
        with guard("Planetary K-index"):
            kp = cache.kp()
            if not kp.empty and "Kp" in kp.columns:
                kp_series = kp["Kp"].dropna()
                if len(kp_series):
                    st.plotly_chart(_kp_gauge(float(kp_series.iloc[-1])),
                                    use_container_width=True)

    # --- Flare probability snapshot -----------------------------------------
    st.divider()
    with guard("Flare probabilities"):
        prob = cache.solar_probabilities()
        if not prob.empty:
            day1 = prob[prob["day"] == "Day 1"].set_index("event")["probability"]
            cols = st.columns(len(day1))
            for col, (event, p) in zip(cols, day1.items()):
                col.metric(f"{event} (24 h)", f"{p:.0f}%" if np.isfinite(p) else "—")

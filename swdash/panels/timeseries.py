"""Time-series panel: X-rays, particle fluxes, solar wind and geomagnetic Kp."""
from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from swdash import cache
from swdash.panels.common import guard, style_fig

# GOES flare-class reference levels (long channel, W/m^2).
FLARE_LEVELS = {"A": 1e-8, "B": 1e-7, "C": 1e-6, "M": 1e-5, "X": 1e-4}


def _xray_fig(df):
    fig = go.Figure()
    if "long" in df:
        fig.add_scatter(x=df.index, y=df["long"], name="0.1–0.8 nm (long)",
                        line=dict(color="#ff5252"))
    if "short" in df:
        fig.add_scatter(x=df.index, y=df["short"], name="0.05–0.4 nm (short)",
                        line=dict(color="#40c4ff"))
    for cls, lvl in FLARE_LEVELS.items():
        fig.add_hline(y=lvl, line_dash="dot", line_color="rgba(255,255,255,0.25)",
                      annotation_text=cls, annotation_position="right")
    fig.update_yaxes(type="log", title="Flux (W/m²)", range=[-9, -3])
    return style_fig(fig, title="GOES X-ray flux")


def _flux_fig(df, title, ytitle):
    fig = go.Figure()
    for col in df.columns:
        fig.add_scatter(x=df.index, y=df[col], name=str(col))
    fig.update_yaxes(type="log", title=ytitle)
    return style_fig(fig, title=title)


def _solar_wind_fig(plasma, mag):
    fig = go.Figure()
    if not plasma.empty and "speed" in plasma:
        fig.add_scatter(x=plasma.index, y=plasma["speed"], name="Speed (km/s)",
                        yaxis="y1", line=dict(color="#ffd54f"))
    if not mag.empty and "bz_gsm" in mag:
        fig.add_scatter(x=mag.index, y=mag["bz_gsm"], name="Bz GSM (nT)",
                        yaxis="y2", line=dict(color="#80cbc4"))
    fig.update_layout(
        yaxis=dict(title="Speed (km/s)"),
        yaxis2=dict(title="Bz (nT)", overlaying="y", side="right", showgrid=False),
    )
    return style_fig(fig, title="Solar wind speed & IMF Bz")


def _kp_fig(df):
    colors = ["#2e7d32" if v < 5 else "#ef6c00" if v < 7 else "#c62828"
              for v in df["Kp"]]
    fig = go.Figure(go.Bar(x=df.index, y=df["Kp"], marker_color=colors))
    fig.update_yaxes(title="Kp", range=[0, 9])
    return style_fig(fig, title="Planetary K-index")


def render():
    st.subheader("Time Series")
    window = st.radio("X-ray window", ["1d", "7d"], horizontal=True, index=0)

    with guard("GOES X-ray flux"):
        xr = cache.xrays(window)
        if not xr.empty:
            st.plotly_chart(_xray_fig(xr), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        with guard("Proton flux"):
            p = cache.protons()
            if not p.empty:
                st.plotly_chart(_flux_fig(p, "GOES integral protons",
                                          "p/cm²·s·sr"), use_container_width=True)
    with c2:
        with guard("Electron flux"):
            e = cache.electrons()
            if not e.empty:
                st.plotly_chart(_flux_fig(e, "GOES integral electrons",
                                          "e/cm²·s·sr"), use_container_width=True)

    with guard("Solar wind"):
        plasma = cache.solar_wind_plasma()
        mag = cache.solar_wind_mag()
        if not plasma.empty or not mag.empty:
            st.plotly_chart(_solar_wind_fig(plasma, mag), use_container_width=True)

    with guard("Planetary K-index"):
        kp = cache.kp()
        if not kp.empty and "Kp" in kp.columns:
            st.plotly_chart(_kp_fig(kp.dropna(subset=["Kp"])),
                            use_container_width=True)

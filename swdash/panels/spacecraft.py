"""Heliosphere top-view panel: current positions of planets and spacecraft."""
from __future__ import annotations

from datetime import datetime, timezone

import plotly.graph_objects as go
import streamlit as st

from swdash import cache
from swdash.config import DEFAULT_BODIES, HELIO_BODIES
from swdash.panels.common import guard, style_fig


def _polar_fig(positions: list[dict]):
    fig = go.Figure()
    # Reference orbit circles at 0.5 / 1.0 / 1.5 AU.
    for r in (0.5, 1.0, 1.5):
        fig.add_trace(go.Scatterpolar(
            r=[r] * 361, theta=list(range(361)), mode="lines",
            line=dict(color="rgba(255,255,255,0.12)", width=1),
            hoverinfo="skip", showlegend=False,
        ))
    for body in positions:
        marker_size = 16 if body["kind"] == "star" else (
            11 if body["kind"] == "planet" else 9)
        fig.add_trace(go.Scatterpolar(
            r=[body["r_au"]],
            theta=[body["lon_deg"]],
            mode="markers+text",
            text=[body["name"]],
            textposition="top center",
            marker=dict(size=marker_size, color=body["color"],
                        symbol="star" if body["kind"] == "star" else "circle"),
            name=body["name"],
        ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(range=[0, 1.8], title="AU", tickvals=[0.5, 1.0, 1.5]),
            angularaxis=dict(rotation=0, direction="counterclockwise"),
        ),
        showlegend=True,
    )
    return style_fig(fig, height=620,
                     title="Top view (Heliographic Stonyhurst — Earth at 0°)")


def render():
    st.subheader("Spacecraft & Planet Positions")
    st.caption("Top-down view of the inner heliosphere from JPL Horizons "
               "(via SunPy). Earth is fixed at longitude 0°.")

    bodies = st.multiselect(
        "Bodies to plot",
        options=list(HELIO_BODIES.keys()),
        default=DEFAULT_BODIES,
    )
    if not bodies:
        st.info("Select at least one body.")
        return

    day_key = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with guard("Spacecraft positions"):
        try:
            positions = cache.positions(tuple(bodies), day_key)
        except ImportError:
            st.warning("This panel needs SunPy & astropy. Install them with:\n\n"
                       "`pip install sunpy astropy astroquery`")
            return
        if not positions:
            st.warning("No positions resolved. SunPy/astropy and internet access "
                       "to JPL Horizons are required for this panel.")
            return
        st.plotly_chart(_polar_fig(positions), use_container_width=True)
        with st.expander("Position table"):
            st.dataframe(
                [{"Body": b["name"], "r (AU)": round(b["r_au"], 3),
                  "Longitude (°)": round(b["lon_deg"], 1)} for b in positions],
                use_container_width=True,
            )

"""Flare-forecast panel: NOAA probabilities and the 3-day forecast discussion."""
from __future__ import annotations

import plotly.express as px
import streamlit as st

from swdash import cache
from swdash.panels.common import guard, style_fig


def _prob_fig(df):
    fig = px.bar(df, x="event", y="probability", color="day", barmode="group",
                 color_discrete_sequence=["#ff5252", "#ffb300", "#42a5f5"])
    fig.update_yaxes(title="Probability (%)", range=[0, 100])
    fig.update_xaxes(title="")
    return style_fig(fig, title="NOAA SWPC event probabilities")


def render():
    st.subheader("Flare & Event Forecast")

    with guard("Flare probabilities"):
        prob = cache.solar_probabilities()
        if not prob.empty:
            issued = prob.attrs.get("issued")
            if issued is not None:
                st.caption(f"Issued: {issued}")
            st.plotly_chart(_prob_fig(prob), use_container_width=True)
            pivot = prob.pivot_table(index="event", columns="day",
                                     values="probability")
            st.dataframe(pivot, use_container_width=True)

    with guard("3-day forecast"):
        text = cache.forecast_text()
        with st.expander("NOAA SWPC 3-day forecast (full text)"):
            st.text(text)

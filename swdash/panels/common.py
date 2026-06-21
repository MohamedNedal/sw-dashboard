"""Shared helpers for panels: plotly theming and graceful error handling."""
from __future__ import annotations

from contextlib import contextmanager

import streamlit as st

from swdash.data.http import DataUnavailable

PLOTLY_TEMPLATE = "plotly_dark"


def style_fig(fig, height: int = 360, title: str | None = None):
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        height=height,
        margin=dict(l=50, r=20, t=40 if title else 20, b=40),
        title=title,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


@contextmanager
def guard(what: str):
    """Wrap a panel section so a single dead feed doesn't crash the page."""
    try:
        yield
    except DataUnavailable as exc:
        st.warning(f"⚠️ {what} is currently unavailable.\n\n{exc}")
    except Exception as exc:  # noqa: BLE001
        st.error(f"Unexpected error loading {what}: {exc}")

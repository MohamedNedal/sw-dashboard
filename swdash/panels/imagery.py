"""Solar imagery panel — latest frames from selected spacecraft/instruments."""
from __future__ import annotations

import streamlit as st

from swdash import cache
from swdash.config import DEFAULT_IMAGERY, IMAGERY_SOURCES
from swdash.panels.common import guard


def render():
    st.subheader("Solar Imagery")
    st.caption("Latest available frames via the Helioviewer API "
               "(SDO/AIA & HMI, SOHO/LASCO, STEREO).")

    selected = st.multiselect(
        "Spacecraft / instrument layers",
        options=list(IMAGERY_SOURCES.keys()),
        default=DEFAULT_IMAGERY,
    )
    size = st.select_slider("Image size (px)", options=[512, 768, 1024], value=768)

    if not selected:
        st.info("Select one or more imagery layers above.")
        return

    cols = st.columns(2)
    for i, label in enumerate(selected):
        with cols[i % 2]:
            with guard(label):
                png = cache.latest_image(label, size=size)
                st.image(png, caption=label, use_container_width=True)

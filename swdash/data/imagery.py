"""Latest solar imagery via the Helioviewer API.

We use the ``takeScreenshot`` endpoint which renders the closest available
image to a requested time for one or more layers and streams a PNG back.  No
heavy dependencies are required for the default view; SunPy/aiapy remain useful
for deeper science work and are listed as optional extras.
"""
from __future__ import annotations

from datetime import datetime, timezone

from swdash.config import HELIOVIEWER_BASE, IMAGERY_SOURCES
from swdash.data.http import get_bytes, get_json


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def take_screenshot(
    source_id: int,
    image_scale: float,
    when: str | None = None,
    width: int = 1024,
    height: int = 1024,
) -> bytes:
    """Return PNG bytes for the latest image of a single Helioviewer layer."""
    params = {
        "date": when or _now_iso(),
        "imageScale": image_scale,
        "layers": f"[{source_id},1,100]",
        "x0": 0,
        "y0": 0,
        "width": width,
        "height": height,
        "display": "true",
        "watermark": "false",
    }
    return get_bytes(f"{HELIOVIEWER_BASE}/takeScreenshot/", params=params)


def latest_image(label: str, when: str | None = None, size: int = 1024) -> bytes:
    """Fetch the latest image for a curated source label from config."""
    if label not in IMAGERY_SOURCES:
        raise KeyError(f"Unknown imagery source: {label}")
    src = IMAGERY_SOURCES[label]
    return take_screenshot(
        src["source_id"], src["image_scale"], when=when, width=size, height=size
    )


def get_data_sources() -> dict:
    """Live discovery of every observatory/instrument/measurement available.

    Useful for building a dynamic source picker if the curated list in config
    goes stale.  Returns Helioviewer's nested tree as-is.
    """
    return get_json(f"{HELIOVIEWER_BASE}/getDataSources/")

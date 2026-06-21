"""Current heliospheric positions of planets and spacecraft.

Positions come from JPL Horizons via SunPy's ``get_horizons_coord`` and are
expressed in Heliographic Stonyhurst coordinates so that Earth sits at
longitude 0.  The returned radius/longitude pairs feed the top-view polar plot.
"""
from __future__ import annotations

from datetime import datetime, timezone

from swdash.config import HELIO_BODIES


def get_positions(bodies: list[str], when: datetime | None = None) -> list[dict]:
    """Return a list of dicts with name, color, kind, r_au and lon_deg.

    Requires ``sunpy`` and ``astropy`` (and network access to JPL Horizons).
    Bodies that fail to resolve are skipped rather than aborting the whole set.
    """
    import astropy.units as u  # imported lazily so the rest of the app loads without it
    from sunpy.coordinates import HeliographicStonyhurst, get_horizons_coord

    when = when or datetime.now(timezone.utc)
    results: list[dict] = []
    for name in bodies:
        cfg = HELIO_BODIES.get(name)
        if not cfg:
            continue
        if cfg["kind"] == "star":  # the Sun is the origin
            results.append({"name": name, "color": cfg["color"], "kind": "star",
                            "r_au": 0.0, "lon_deg": 0.0})
            continue
        try:
            coord = get_horizons_coord(cfg["id"], when)
            hgs = coord.transform_to(HeliographicStonyhurst(obstime=when))
            results.append({
                "name": name,
                "color": cfg["color"],
                "kind": cfg["kind"],
                "r_au": float(hgs.radius.to(u.AU).value),
                "lon_deg": float(hgs.lon.to(u.deg).value),
            })
        except Exception:  # noqa: BLE001 - any body may be unavailable for a date
            continue
    return results

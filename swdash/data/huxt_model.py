"""HUXt heliospheric solar-wind / CME model integration.

HUXt (Heliospheric Upwind eXtrapolation, time-dependent) is an optional heavy
dependency.  When it is installed we run a real ambient + cone-CME simulation
and return the velocity grid for plotting.  When it is not, the caller can fall
back to the lightweight kinematic approximation in :mod:`swdash.panels.huxt`.

See https://github.com/University-of-Reading-Space-Science/HUXt
"""
from __future__ import annotations

import numpy as np


def _import_huxt():
    """Return the HUXt core and inputs modules across packaging layouts.

    Recent releases ship a ``huxt`` package whose ``__init__`` is empty, so the
    classes live in the ``huxt.huxt`` submodule.  Older copies expose flat
    top-level modules (``huxt`` / ``huxt_inputs``).  Try both.
    """
    try:  # current packaged layout: huxt/huxt.py, huxt/huxt_inputs.py
        from huxt import huxt as H
        from huxt import huxt_inputs as Hin
    except Exception:  # noqa: BLE001 - fall back to legacy flat modules
        import huxt as H  # type: ignore
        import huxt_inputs as Hin  # type: ignore
    if not hasattr(H, "HUXt"):
        raise ImportError("HUXt class not found in installed 'huxt' package")
    return H, Hin


def huxt_available() -> bool:
    try:
        _import_huxt()
        return True
    except Exception:  # noqa: BLE001
        return False


def _synthetic_boundary(n: int = 128, slow: float = 350.0, fast: float = 650.0):
    """A simple fast/slow stream inner-boundary speed profile (km/s).

    Used when MAS coronal maps are not downloaded; gives a realistic-looking
    ambient solar wind with two fast streams so co-rotating structure forms.
    """
    lon = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    profile = slow + (fast - slow) * 0.5 * (
        1.0 + np.sin(2 * lon) * (np.sin(2 * lon) > 0)
    )
    return profile


def run_huxt(
    cme_speed: float = 1000.0,
    cme_longitude: float = 0.0,
    cme_width: float = 40.0,
    cme_thickness: float = 5.0,
    simtime_days: float = 5.0,
    cr_num: int | None = None,
    use_mas: bool = False,
) -> dict:
    """Run a HUXt simulation and return arrays suitable for a polar plot.

    Parameters are in physical units: speed km/s, angles degrees, thickness in
    solar radii, time in days.  Returns a dict with ``times_hr`` (n_t),
    ``r_rs`` (n_r, solar radii), ``lon_rad`` (n_lon), ``v_grid``
    (n_t, n_lon, n_r, km/s) and optional ``arrival`` info at Earth.
    """
    import astropy.units as u

    H, Hin = _import_huxt()

    if use_mas and cr_num is not None:
        v_boundary = Hin.get_MAS_long_profile(cr_num)
    else:
        v_boundary = _synthetic_boundary() * (u.km / u.s)

    cr_num = cr_num or 2254  # any reference rotation works for synthetic runs
    model = H.HUXt(
        v_boundary=v_boundary,
        cr_num=cr_num,
        simtime=simtime_days * u.day,
        dt_scale=4,
    )

    cme = H.ConeCME(
        t_launch=0 * u.day,
        longitude=cme_longitude * u.deg,
        width=cme_width * u.deg,
        v=cme_speed * (u.km / u.s),
        thickness=cme_thickness * u.solRad,
    )
    model.solve([cme])

    result = {
        "times_hr": np.asarray(model.time_out.to(u.hr).value),
        "r_rs": np.asarray(model.r.to(u.solRad).value),
        "lon_rad": np.asarray(model.lon.to(u.rad).value),
        "v_grid": np.asarray(model.v_grid.to(u.km / u.s).value),
        "arrival": None,
    }

    try:  # arrival diagnostics require the bundled ephemeris
        stats = model.cmes[0].compute_arrival_at_body("EARTH")
        result["arrival"] = {
            "hit": bool(stats.get("hit", False)),
            "arrival_time": str(stats.get("t_arrive")),
            "transit_time_days": float(stats.get("t_transit").to(u.day).value)
            if stats.get("t_transit") is not None else None,
            "arrival_speed": float(stats.get("v").to(u.km / u.s).value)
            if stats.get("v") is not None else None,
        }
    except Exception:  # noqa: BLE001
        pass

    return result

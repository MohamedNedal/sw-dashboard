"""Flare and proton event probabilities from NOAA SWPC."""
from __future__ import annotations

import pandas as pd

from swdash.config import SWPC
from swdash.data.http import get_json


def parse_solar_probabilities(raw: list[dict]) -> pd.DataFrame:
    """Tidy the solar_probabilities feed into rows of (date, class, day, prob).

    The raw feed carries one record per issue date with columns such as
    ``c_class_1_day`` / ``m_class_2_day`` / ``x_class_3_day`` (percent) plus
    ``10mev_protons_1_day``.  We keep the most recent issue and reshape it into
    a small long-format frame that is trivial to chart or tabulate.
    """
    if not raw:
        return pd.DataFrame()
    df = pd.DataFrame(raw)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.sort_values("date")
    latest = df.iloc[-1]

    records = []
    label_map = {
        "c_class": "C flare",
        "m_class": "M flare",
        "x_class": "X flare",
        "10mev_protons": "S1+ protons",
    }
    for key, label in label_map.items():
        for day in (1, 2, 3):
            col = f"{key}_{day}_day"
            if col in latest.index:
                val = pd.to_numeric(latest[col], errors="coerce")
                records.append({"event": label, "day": f"Day {day}", "probability": val})
    out = pd.DataFrame(records)
    out.attrs["issued"] = latest.get("date")
    return out


def fetch_solar_probabilities() -> pd.DataFrame:
    return parse_solar_probabilities(get_json(SWPC["solar_prob"]))

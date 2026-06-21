"""Offline tests for the SWPC/flare parsers using captured-format fixtures.

These exercise the pure ``parse_*`` helpers with no network access so the data
pipeline can be validated in CI or on a plane.
"""
import numpy as np
import pandas as pd

from swdash.data import swpc
from swdash.data.flares import parse_solar_probabilities


def test_flux_to_class():
    assert swpc.flux_to_class(5e-5).startswith("M")
    assert swpc.flux_to_class(2e-4).startswith("X")
    assert swpc.flux_to_class(3e-6).startswith("C")
    assert swpc.flux_to_class(0) == "—"
    assert swpc.flux_to_class(float("nan")) == "—"


def test_parse_product_table():
    rows = [
        ["time_tag", "density", "speed", "temperature"],
        ["2024-01-01T00:00:00.000Z", "5.0", "420.0", "100000"],
        ["2024-01-01T00:01:00.000Z", "5.5", "430.0", "110000"],
    ]
    df = swpc.parse_product_table(rows)
    assert list(df.columns) == ["time_tag", "density", "speed", "temperature"]
    assert len(df) == 2
    assert pd.api.types.is_datetime64_any_dtype(df["time_tag"])
    assert df["speed"].iloc[-1] == 430.0


def test_parse_product_table_empty():
    assert swpc.parse_product_table([]).empty
    assert swpc.parse_product_table([["only", "header"]]).empty


def test_parse_xrays_pivots_bands():
    raw = [
        {"time_tag": "2024-01-01T00:00:00Z", "flux": 1e-6, "energy": "0.1-0.8nm"},
        {"time_tag": "2024-01-01T00:00:00Z", "flux": 2e-7, "energy": "0.05-0.4nm"},
        {"time_tag": "2024-01-01T00:01:00Z", "flux": 1.5e-6, "energy": "0.1-0.8nm"},
    ]
    df = swpc.parse_xrays(raw)
    assert "long" in df.columns and "short" in df.columns
    assert df["long"].iloc[-1] == 1.5e-6
    assert df["short"].iloc[0] == 2e-7


def test_parse_xrays_empty():
    assert swpc.parse_xrays([]).empty


def test_parse_solar_probabilities():
    raw = [
        {"date": "2024-01-01", "c_class_1_day": 30, "m_class_1_day": 10,
         "x_class_1_day": 1, "10mev_protons_1_day": 5,
         "c_class_2_day": 25, "m_class_2_day": 8, "x_class_2_day": 1,
         "10mev_protons_2_day": 4, "c_class_3_day": 20, "m_class_3_day": 7,
         "x_class_3_day": 1, "10mev_protons_3_day": 3},
        {"date": "2024-01-02", "c_class_1_day": 60, "m_class_1_day": 20,
         "x_class_1_day": 5, "10mev_protons_1_day": 10,
         "c_class_2_day": 55, "m_class_2_day": 18, "x_class_2_day": 4,
         "10mev_protons_2_day": 9, "c_class_3_day": 50, "m_class_3_day": 15,
         "x_class_3_day": 3, "10mev_protons_3_day": 8},
    ]
    df = parse_solar_probabilities(raw)
    # Latest issue (2024-01-02) should be used.
    day1 = df[df["day"] == "Day 1"].set_index("event")["probability"]
    assert day1["C flare"] == 60
    assert day1["M flare"] == 20
    assert day1["X flare"] == 5
    assert set(df["day"]) == {"Day 1", "Day 2", "Day 3"}
    assert set(df["event"]) == {"C flare", "M flare", "X flare", "S1+ protons"}


def test_huxt_synthetic_boundary_shape():
    from swdash.data.huxt_model import _synthetic_boundary
    prof = _synthetic_boundary(128)
    assert prof.shape == (128,)
    assert np.all(prof >= 350) and np.all(prof <= 650)

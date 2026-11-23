import math
import pytest

from osdagbridge.core.bridge_components.sub_structure.pier.geometry import (
    pier_geometry,
    pier_reinforcement_geometry,
)
from osdagbridge.core.bridge_components.sub_structure.pier_cap.geometry import (
    pier_cap_geometry,
    pier_cap_length_from_deck,
    pier_cap_reinforcement_geometry,
)
from osdagbridge.core.bridge_components.foundation.pile_cap.geometry import (
    pile_cap_geometry,
    pile_cap_reinforcement_geometry,
)
from osdagbridge.core.bridge_components.foundation.pile.geometry import (
    pile_geometry,
)

def test_default_pier_geometry():
    res = pier_geometry()
    assert res["diameter"] == 800.0
    assert res["radius"] == 400.0
    assert res["height"] == 3000.0
    expected_vol = math.pi * (400.0 ** 2) * 3000.0
    assert pytest.approx(res["volume"], rel=1e-5) == expected_vol
    assert pytest.approx(res["volume_m3"], rel=1e-5) == expected_vol / 1e9

def test_default_pier_reinforcement_geometry():
    res = pier_reinforcement_geometry()
    # Task requirement: 15 main bars on radius 344 mm, 15 ties
    assert pytest.approx(res["rebar_radius"], abs=1e-3) == 344.0
    assert res["main_bar_count"] == 15
    assert res["tie_count"] == 15
    assert len(res["main_bars"]) == 15
    assert len(res["ties"]) == 15

    # Check that main bars lie on radius 344 mm
    for bar in res["main_bars"]:
        r = math.hypot(bar["x"], bar["y"])
        assert pytest.approx(r, abs=1e-3) == 344.0
        assert bar["diameter"] == 16.0
        assert bar["length"] == 2920.0

    # Check ties diameter and clear height distribution
    for tie in res["ties"]:
        assert tie["diameter"] == 8.0
        assert 40.0 <= tie["z"] <= 2960.0

    assert res["total_weight_kg"] > 0
    assert res["total_rebar_volume"] > 0

def test_default_pier_cap_geometry():
    res = pier_cap_geometry(length=12000.0)
    assert res["top_width"] == 3000.0
    assert res["bottom_width"] == 1200.0
    assert res["depth"] == 600.0
    expected_area = ((3000.0 + 1200.0) / 2.0) * 600.0
    assert pytest.approx(res["area_xz"]) == expected_area
    assert pytest.approx(res["volume"]) == expected_area * 12000.0
    assert pytest.approx(res["volume_m3"]) == 15.12

def test_pier_cap_deck_width_reuse():
    # Reuses calculate_deck_width from deck/builder.py
    w = pier_cap_length_from_deck(
        footpath_config="NONE",
        carriageway_width=12000.0,
        crash_barrier_base_width=450.0,
    )
    assert w == 12000.0 + 2 * 450.0

def test_pier_cap_reinforcement():
    res = pier_cap_reinforcement_geometry(length=12000.0)
    assert res["total_main_bars"] > 0
    assert res["tie_count"] > 0
    assert res["total_weight_kg"] > 0
    assert len(res["main_bars"]) == res["total_main_bars"]

def test_default_pile_cap_geometry():
    res = pile_cap_geometry()
    assert res["length_x"] == 2200.0
    assert res["width_y"] == 1200.0
    assert res["depth_z"] == 600.0
    expected_vol = 2200.0 * 1200.0 * 600.0
    assert pytest.approx(res["volume"]) == expected_vol
    assert pytest.approx(res["volume_m3"]) == 1.584

def test_pile_cap_reinforcement():
    res = pile_cap_reinforcement_geometry()
    assert res["total_main_bars"] > 0
    assert res["tie_count"] > 0
    assert res["total_weight_kg"] > 0

def test_default_piles_geometry():
    res = pile_geometry()
    assert res["diameter"] == 400.0
    assert res["radius"] == 200.0
    assert res["length"] == 5000.0
    assert res["spacing"] == 600.0
    assert res["pile_count"] == 4
    assert len(res["piles"]) == 4

    single_vol = math.pi * (200.0 ** 2) * 5000.0
    assert pytest.approx(res["single_volume"]) == single_vol
    assert pytest.approx(res["total_volume"]) == 4 * single_vol

    # Verify 2x2 grid spacing around center
    coords = {(round(p["x_offset"], 1), round(p["y_offset"], 1)) for p in res["piles"]}
    expected_coords = {(-300.0, -300.0), (300.0, -300.0), (-300.0, 300.0), (300.0, 300.0)}
    assert coords == expected_coords

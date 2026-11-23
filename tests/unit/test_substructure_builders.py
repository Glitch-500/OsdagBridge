import pytest

from osdagbridge.core.bridge_components.sub_structure.placement import (
    calculate_substructure_placement,
)
from osdagbridge.core.bridge_components.sub_structure.pier.builder import (
    build_pier_geometry,
)
from osdagbridge.core.bridge_components.sub_structure.pier_cap.builder import (
    build_pier_cap_geometry,
)
from osdagbridge.core.bridge_components.foundation.pile_cap.builder import (
    build_pile_cap_geometry,
)
from osdagbridge.core.bridge_components.foundation.pile.builder import (
    build_piles_geometry,
)

def test_substructure_placement():
    pos = calculate_substructure_placement(
        span_length_L=25000.0,
        girder_section_d=900.0,
        girder_section_tf_b=260.0,
        bearing_height=0.0,
        cap_depth=600.0,
        pier_height=3000.0,
        pile_cap_depth=600.0,
        pile_length=5000.0,
        pile_spacing=600.0,
    )

    assert pos["x_center"] == 12500.0
    assert pos["y_center"] == 0.0

    # Contact below bottom flange at -(900/2 + 260) = -710.0
    assert pos["z_cap_top"] == -710.0
    assert pos["z_cap_bot"] == -1310.0
    assert pos["z_pier_top"] == -1310.0
    assert pos["z_pier_bot"] == -4310.0
    assert pos["z_pile_cap_top"] == -4310.0
    assert pos["z_pile_cap_bot"] == -4910.0
    assert pos["z_pile_top"] == -4910.0
    assert pos["z_pile_bot"] == -9910.0

    # Piles 2x2 grid around (12500, 0)
    assert len(pos["piles"]) == 4
    pile_coords = {(p["x"], p["y"]) for p in pos["piles"]}
    expected_pile_coords = {
        (12200.0, -300.0),
        (12800.0, -300.0),
        (12200.0, 300.0),
        (12800.0, 300.0),
    }
    assert pile_coords == expected_pile_coords

def test_pier_builder_call():
    pier = build_pier_geometry(
        diameter=800.0,
        height=3000.0,
        center_x=12500.0,
        center_y=0.0,
        bottom_z=-4310.0,
    )
    assert pier is not None

def test_pier_cap_builder_call():
    cap = build_pier_cap_geometry(
        top_width=3000.0,
        bottom_width=1200.0,
        depth=600.0,
        length=12000.0,
        center_x=12500.0,
        center_y=0.0,
        bottom_z=-1310.0,
    )
    assert cap is not None

def test_pile_cap_builder_call():
    pile_cap = build_pile_cap_geometry(
        length_x=2200.0,
        width_y=1200.0,
        depth_z=600.0,
        center_x=12500.0,
        center_y=0.0,
        bottom_z=-4910.0,
    )
    assert pile_cap is not None

def test_piles_builder_call():
    piles = build_piles_geometry(
        diameter=400.0,
        length=5000.0,
        spacing=600.0,
        center_x=12500.0,
        center_y=0.0,
        bottom_z=-9910.0,
    )
    assert piles is not None
    assert len(piles) == 4

import pytest

try:
    import OCC
    _HAS_OCC = True
except (ImportError, ModuleNotFoundError):
    _HAS_OCC = False

from osdagbridge.core.bridge_components.sub_structure.placement import (
    calculate_substructure_placement,
)
from osdagbridge.core.bridge_components.sub_structure.pier.builder import (
    build_pier_rebar,
)
from osdagbridge.core.bridge_components.sub_structure.pier_cap.builder import (
    build_pier_cap_rebar,
)
from osdagbridge.core.bridge_components.foundation.pile_cap.builder import (
    build_pile_cap_rebar,
)


def test_pier_rebar():
    pos = calculate_substructure_placement()
    res = build_pier_rebar(
        diameter=800.0,
        height=3000.0,
        center_x=pos["pier"]["x"],
        center_y=pos["pier"]["y"],
        bottom_z=pos["pier"]["z_bot"],
        cover=40.0,
        main_dia=16.0,
        tie_dia=8.0,
    )

    assert len(res["main_bars"]) == 15
    for bar in res["main_bars"]:
        assert bar["role"] == "MAIN"
        assert bar["diameter"] == 16.0
        assert pytest.approx(bar["length"], abs=1e-2) == 2920.0
        dx = bar["p1"][0] - pos["pier"]["x"]
        dy = bar["p1"][1] - pos["pier"]["y"]
        r = (dx ** 2 + dy ** 2) ** 0.5
        assert r < 400.0 - 40.0

    assert len(res["ties"]) == 15
    for tie in res["ties"]:
        assert tie["role"] == "LIGATURE"
        assert tie["diameter"] == 8.0
        assert pytest.approx(tie["radius"], abs=1e-2) == 356.0
        assert tie["center"][2] >= pos["pier"]["z_bot"]
        assert tie["center"][2] <= pos["pier"]["z_top"]


def test_pier_cap_rebar():
    pos = calculate_substructure_placement()
    res = build_pier_cap_rebar(
        top_width=3000.0,
        bottom_width=1200.0,
        depth=600.0,
        length=12000.0,
        center_x=pos["pier_cap"]["x"],
        center_y=pos["pier_cap"]["y"],
        bottom_z=pos["pier_cap"]["z_bot"],
        cover=40.0,
        main_dia=16.0,
        tie_dia=8.0,
    )

    assert len(res["main_bars"]) == 28
    assert len(res["main_bars"]) == res["geometry"]["total_main_bars"]
    for bar in res["main_bars"]:
        assert bar["role"] == "MAIN"
        assert bar["diameter"] == 16.0
        assert pytest.approx(bar["length"], abs=1e-2) == 11920.0

    assert len(res["ties"]) == 60
    assert len(res["ties"]) == res["geometry"]["tie_count"]
    for st in res["ties"]:
        assert st["role"] == "LIGATURE"
        assert st["diameter"] == 8.0
        assert len(st["points"]) == 4


def test_pile_cap_rebar():
    pos = calculate_substructure_placement()
    res = build_pile_cap_rebar(
        length_x=2200.0,
        width_y=1200.0,
        depth_z=600.0,
        center_x=pos["pile_cap"]["x"],
        center_y=pos["pile_cap"]["y"],
        bottom_z=pos["pile_cap"]["z_bot"],
        cover=40.0,
        main_dia=16.0,
        tie_dia=8.0,
    )

    assert len(res["main_bars"]) == 46
    for bar in res["main_bars"]:
        assert bar["role"] == "MAIN"
        assert bar["diameter"] == 16.0

    assert len(res["ties"]) == 6
    assert len(res["ties"]) == res["geometry"]["tie_count"]
    for st in res["ties"]:
        assert st["role"] == "LIGATURE"
        assert st["diameter"] == 8.0
        assert len(st["points"]) == 4


@pytest.mark.skipif(not _HAS_OCC, reason="Requires pythonOCC")
def test_generator_substructure_rebar():
    from osdagbridge.core.bridge_types.plate_girder.cad_generator import (
        PlateGirderCADGenerator,
    )
    gen = PlateGirderCADGenerator(
        span_length_L=25000.0,
        carriageway_width=12000.0,
        girder_section_d=900.0,
        girder_section_tf_b=260.0,
    )
    data = gen.generate()
    assert "pier_cap_rebar" in data
    assert "pier_rebar" in data
    assert "pile_cap_rebar" in data
    assert "substructure_rebar" in data
    assert len(data["pier_rebar"]["main_bars"]) == 15
    assert len(data["pier_rebar"]["ties"]) == 15
    assert len(data["pier_cap_rebar"]["main_bars"]) > 0
    assert len(data["pile_cap_rebar"]["main_bars"]) > 0

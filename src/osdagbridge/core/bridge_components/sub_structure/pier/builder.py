try:
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
    from OCC.Core.gp import gp_Vec, gp_Trsf, gp_Ax2, gp_Pnt, gp_Dir
    _HAS_OCC = True
except (ImportError, ModuleNotFoundError):
    _HAS_OCC = False

from osdagbridge.core.bridge_components.sub_structure.pier.geometry import (
    pier_reinforcement_geometry
)
from osdagbridge.core.bridge_components.sub_structure.rebar_builder import (
    make_straight_bar,
    make_circular_hoop,
    combine_rebar_shapes
)


def _translate(shape, dx=0.0, dy=0.0, dz=0.0):
    if not _HAS_OCC:
        return shape
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(float(dx), float(dy), float(dz)))
    return BRepBuilderAPI_Transform(shape, trsf, True).Shape()


def build_pier_geometry(
    diameter=800.0,
    height=3000.0,
    center_x=0.0,
    center_y=0.0,
    bottom_z=0.0,
):
    radius = diameter / 2.0
    if not _HAS_OCC:
        return {
            "type": "pier",
            "diameter": diameter,
            "height": height,
            "center": (center_x, center_y, bottom_z + height / 2.0),
            "bottom_z": bottom_z,
            "shape": None,
        }

    axis = gp_Ax2(gp_Pnt(center_x, center_y, bottom_z), gp_Dir(0, 0, 1))
    cylinder = BRepPrimAPI_MakeCylinder(axis, radius, height).Shape()
    return cylinder


def build_pier_rebar(
    diameter=800.0,
    height=3000.0,
    center_x=0.0,
    center_y=0.0,
    bottom_z=0.0,
    cover=40.0,
    main_dia=16.0,
    main_spacing=150.0,
    tie_dia=8.0,
    tie_spacing=200.0,
):
    geo = pier_reinforcement_geometry(
        diameter=diameter,
        height=height,
        cover=cover,
        main_dia=main_dia,
        main_spacing=main_spacing,
        tie_dia=tie_dia,
        tie_spacing=tie_spacing,
    )

    z_start = bottom_z + cover
    z_end = bottom_z + height - cover

    main_bars = []
    for b in geo["main_bars"]:
        p1 = (center_x + b["x"], center_y + b["y"], z_start)
        p2 = (center_x + b["x"], center_y + b["y"], z_end)
        bar_item = make_straight_bar(p1, p2, diameter=main_dia, role="MAIN")
        if bar_item:
            main_bars.append(bar_item)

    ties = []
    for t in geo["ties"]:
        z_tie = bottom_z + t["z"]
        tie_item = make_circular_hoop(
            (center_x, center_y, z_tie),
            radius=t["radius"],
            diameter=tie_dia,
            role="LIGATURE",
        )
        if tie_item:
            ties.append(tie_item)

    all_items = main_bars + ties
    return {
        "main_bars": main_bars,
        "ties": ties,
        "items": all_items,
        "shape": combine_rebar_shapes(all_items),
        "geometry": geo,
    }

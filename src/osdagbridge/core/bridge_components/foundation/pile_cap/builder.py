try:
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
    from OCC.Core.gp import gp_Vec, gp_Trsf
    _HAS_OCC = True
except (ImportError, ModuleNotFoundError):
    _HAS_OCC = False

from osdagbridge.core.bridge_components.foundation.pile_cap.geometry import (
    pile_cap_reinforcement_geometry
)
from osdagbridge.core.bridge_components.sub_structure.rebar_builder import (
    make_straight_bar,
    make_polygon_stirrup,
    combine_rebar_shapes
)


def _translate(shape, dx=0.0, dy=0.0, dz=0.0):
    if not _HAS_OCC:
        return shape
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(float(dx), float(dy), float(dz)))
    return BRepBuilderAPI_Transform(shape, trsf, True).Shape()


def build_pile_cap_geometry(
    length_x=2200.0,
    width_y=1200.0,
    depth_z=600.0,
    center_x=0.0,
    center_y=0.0,
    bottom_z=0.0,
):
    if not _HAS_OCC:
        return {
            "type": "pile_cap",
            "length_x": length_x,
            "width_y": width_y,
            "depth_z": depth_z,
            "center": (center_x, center_y, bottom_z + depth_z / 2.0),
            "bottom_z": bottom_z,
            "shape": None,
        }

    box = BRepPrimAPI_MakeBox(
        float(length_x), float(width_y), float(depth_z)
    ).Shape()
    box = _translate(
        box,
        -length_x / 2.0,
        -width_y / 2.0,
        0.0,
    )
    return _translate(box, center_x, center_y, bottom_z)


def build_pile_cap_rebar(
    length_x=2200.0,
    width_y=1200.0,
    depth_z=600.0,
    center_x=0.0,
    center_y=0.0,
    bottom_z=0.0,
    cover=40.0,
    main_dia=16.0,
    main_spacing=150.0,
    tie_dia=8.0,
    tie_spacing=200.0,
):
    geo = pile_cap_reinforcement_geometry(
        length_x=length_x,
        width_y=width_y,
        depth_z=depth_z,
        cover=cover,
        main_dia=main_dia,
        main_spacing=main_spacing,
        tie_dia=tie_dia,
        tie_spacing=tie_spacing,
    )

    mid_z = bottom_z + depth_z / 2.0

    main_bars = []
    for b in geo["main_bars"]:
        bar_z = mid_z + b["z"]
        if b["direction"] == "X":
            x_start = center_x - b["length"] / 2.0
            x_end = center_x + b["length"] / 2.0
            bar_y = center_y + b["y"]
            p1 = (x_start, bar_y, bar_z)
            p2 = (x_end, bar_y, bar_z)
        else:
            y_start = center_y - b["length"] / 2.0
            y_end = center_y + b["length"] / 2.0
            bar_x = center_x + b["x"]
            p1 = (bar_x, y_start, bar_z)
            p2 = (bar_x, y_end, bar_z)

        bar_item = make_straight_bar(p1, p2, diameter=b["diameter"], role="MAIN")
        if bar_item:
            main_bars.append(bar_item)

    x_half = (length_x - 2.0 * cover - tie_dia) / 2.0
    z_bot = bottom_z + cover + tie_dia / 2.0
    z_top = bottom_z + depth_z - cover - tie_dia / 2.0

    ties = []
    for t in geo["ties"]:
        y_pos = center_y + t["y"]
        p1 = (center_x - x_half, y_pos, z_bot)
        p2 = (center_x + x_half, y_pos, z_bot)
        p3 = (center_x + x_half, y_pos, z_top)
        p4 = (center_x - x_half, y_pos, z_top)
        st_item = make_polygon_stirrup([p1, p2, p3, p4], diameter=t["diameter"], role="LIGATURE")
        if st_item:
            ties.append(st_item)

    all_items = main_bars + ties
    return {
        "main_bars": main_bars,
        "ties": ties,
        "items": all_items,
        "shape": combine_rebar_shapes(all_items),
        "geometry": geo,
    }

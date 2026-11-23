try:
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism
    from OCC.Core.BRepBuilderAPI import (
        BRepBuilderAPI_Transform,
        BRepBuilderAPI_MakePolygon,
        BRepBuilderAPI_MakeFace,
    )
    from OCC.Core.gp import gp_Vec, gp_Trsf, gp_Pnt
    _HAS_OCC = True
except (ImportError, ModuleNotFoundError):
    _HAS_OCC = False

from osdagbridge.core.bridge_components.sub_structure.pier_cap.geometry import (
    pier_cap_reinforcement_geometry
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


def build_pier_cap_geometry(
    top_width=3000.0,
    bottom_width=1200.0,
    depth=600.0,
    length=12000.0,
    center_x=0.0,
    center_y=0.0,
    bottom_z=0.0,
):
    if not _HAS_OCC:
        return {
            "type": "pier_cap",
            "top_width": top_width,
            "bottom_width": bottom_width,
            "depth": depth,
            "length": length,
            "center": (center_x, center_y, bottom_z + depth / 2.0),
            "bottom_z": bottom_z,
            "shape": None,
        }

    x_top_half = top_width / 2.0
    x_bot_half = bottom_width / 2.0
    y_start = center_y - length / 2.0
    z_bot = bottom_z
    z_top = bottom_z + depth

    p1 = gp_Pnt(center_x - x_bot_half, y_start, z_bot)
    p2 = gp_Pnt(center_x + x_bot_half, y_start, z_bot)
    p3 = gp_Pnt(center_x + x_top_half, y_start, z_top)
    p4 = gp_Pnt(center_x - x_top_half, y_start, z_top)

    poly = BRepBuilderAPI_MakePolygon()
    poly.Add(p1)
    poly.Add(p2)
    poly.Add(p3)
    poly.Add(p4)
    poly.Close()

    face = BRepBuilderAPI_MakeFace(poly.Wire()).Face()
    prism = BRepPrimAPI_MakePrism(face, gp_Vec(0.0, float(length), 0.0)).Shape()
    return prism


def build_pier_cap_rebar(
    top_width=3000.0,
    bottom_width=1200.0,
    depth=600.0,
    length=12000.0,
    center_x=0.0,
    center_y=0.0,
    bottom_z=0.0,
    cover=40.0,
    main_dia=16.0,
    main_spacing=150.0,
    tie_dia=8.0,
    tie_spacing=200.0,
):
    geo = pier_cap_reinforcement_geometry(
        top_width=top_width,
        bottom_width=bottom_width,
        depth=depth,
        length=length,
        cover=cover,
        main_dia=main_dia,
        main_spacing=main_spacing,
        tie_dia=tie_dia,
        tie_spacing=tie_spacing,
    )

    y_start = center_y - geo["eff_length"] / 2.0
    y_end = center_y + geo["eff_length"] / 2.0
    mid_z = bottom_z + depth / 2.0

    main_bars = []
    for b in geo["main_bars"]:
        p1 = (center_x + b["x"], y_start, mid_z + b["z"])
        p2 = (center_x + b["x"], y_end, mid_z + b["z"])
        bar_item = make_straight_bar(p1, p2, diameter=main_dia, role="MAIN")
        if bar_item:
            main_bars.append(bar_item)

    z_bot = bottom_z + cover + tie_dia / 2.0
    z_top = bottom_z + depth - cover - tie_dia / 2.0

    stirrups = []
    for t in geo["ties"]:
        y_pos = center_x_y = center_y + t["y"]
        x_bot_half = t["bottom_width"] / 2.0
        x_top_half = t["top_width"] / 2.0
        p1 = (center_x - x_bot_half, y_pos, z_bot)
        p2 = (center_x + x_bot_half, y_pos, z_bot)
        p3 = (center_x + x_top_half, y_pos, z_top)
        p4 = (center_x - x_top_half, y_pos, z_top)
        st_item = make_polygon_stirrup([p1, p2, p3, p4], diameter=tie_dia, role="LIGATURE")
        if st_item:
            stirrups.append(st_item)

    all_items = main_bars + stirrups
    return {
        "main_bars": main_bars,
        "ties": stirrups,
        "items": all_items,
        "shape": combine_rebar_shapes(all_items),
        "geometry": geo,
    }

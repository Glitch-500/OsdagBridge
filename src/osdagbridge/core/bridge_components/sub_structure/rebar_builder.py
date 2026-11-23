import math

try:
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeTorus
    from OCC.Core.BRep import BRep_Builder
    from OCC.Core.TopoDS import TopoDS_Compound
    from OCC.Core.gp import gp_Ax2, gp_Pnt, gp_Dir
    _HAS_OCC = True
except (ImportError, ModuleNotFoundError):
    _HAS_OCC = False


def make_straight_bar(p1, p2, diameter=16.0, role="MAIN"):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dz = p2[2] - p1[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length <= 0.0:
        return None

    shape = None
    if _HAS_OCC:
        axis = gp_Ax2(gp_Pnt(p1[0], p1[1], p1[2]), gp_Dir(dx, dy, dz))
        shape = BRepPrimAPI_MakeCylinder(axis, diameter / 2.0, length).Shape()

    return {
        "type": "straight",
        "role": role,
        "diameter": diameter,
        "length": length,
        "p1": p1,
        "p2": p2,
        "shape": shape,
    }


def make_circular_hoop(center, radius, diameter=8.0, role="LIGATURE"):
    shape = None
    if _HAS_OCC:
        axis = gp_Ax2(gp_Pnt(center[0], center[1], center[2]), gp_Dir(0, 0, 1))
        shape = BRepPrimAPI_MakeTorus(axis, float(radius), diameter / 2.0).Shape()

    return {
        "type": "hoop",
        "role": role,
        "diameter": diameter,
        "radius": radius,
        "length": 2.0 * math.pi * radius,
        "center": center,
        "shape": shape,
    }


def make_polygon_stirrup(points, diameter=8.0, role="LIGATURE"):
    segments = []
    total_len = 0.0
    n = len(points)
    for i in range(n):
        p_start = points[i]
        p_end = points[(i + 1) % n]
        seg = make_straight_bar(p_start, p_end, diameter, role=role)
        if seg:
            segments.append(seg)
            total_len += seg["length"]

    shape = None
    if _HAS_OCC:
        builder = BRep_Builder()
        compound = TopoDS_Compound()
        builder.MakeCompound(compound)
        for s in segments:
            if s["shape"] is not None:
                builder.Add(compound, s["shape"])
        shape = compound

    return {
        "type": "stirrup",
        "role": role,
        "diameter": diameter,
        "length": total_len,
        "points": points,
        "segments": segments,
        "shape": shape,
    }


def combine_rebar_shapes(rebar_items):
    shapes = []
    for item in rebar_items:
        s = item.get("shape")
        if s is not None:
            shapes.append(s)
        # Also check child segments if stirrup
        for seg in item.get("segments", []):
            cs = seg.get("shape")
            if cs is not None and s is None:
                shapes.append(cs)

    if not _HAS_OCC or not shapes:
        return None

    builder = BRep_Builder()
    compound = TopoDS_Compound()
    builder.MakeCompound(compound)
    for shp in shapes:
        builder.Add(compound, shp)
    return compound

try:
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from OCC.Core.gp import gp_Ax2, gp_Pnt, gp_Dir
    _HAS_OCC = True
except (ImportError, ModuleNotFoundError):
    _HAS_OCC = False

def build_piles_geometry(
    diameter=400.0,
    length=5000.0,
    spacing=600.0,
    center_x=0.0,
    center_y=0.0,
    bottom_z=0.0,
    grid_n_x=2,
    grid_n_y=2,
):
    radius = diameter / 2.0
    offsets_x = [
        -spacing * (grid_n_x - 1) / 2.0 + i * spacing for i in range(grid_n_x)
    ]
    offsets_y = [
        -spacing * (grid_n_y - 1) / 2.0 + j * spacing for j in range(grid_n_y)
    ]

    if not _HAS_OCC:
        piles_info = []
        for ox in offsets_x:
            for oy in offsets_y:
                piles_info.append({
                    "center": (center_x + ox, center_y + oy, bottom_z + length / 2.0),
                    "bottom_z": bottom_z,
                    "radius": radius,
                    "length": length,
                })
        return piles_info

    pile_shapes = []
    for ox in offsets_x:
        for oy in offsets_y:
            px = center_x + ox
            py = center_y + oy
            axis = gp_Ax2(gp_Pnt(px, py, bottom_z), gp_Dir(0, 0, 1))
            cyl = BRepPrimAPI_MakeCylinder(axis, radius, length).Shape()
            pile_shapes.append(cyl)

    return pile_shapes

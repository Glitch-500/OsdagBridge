import math

def pile_geometry(
    diameter=400.0,
    length=5000.0,
    spacing=600.0,
    grid_n_x=2,
    grid_n_y=2,
):
    radius = diameter / 2.0
    single_area = math.pi * radius ** 2
    single_volume = single_area * length
    single_surface_area = 2.0 * math.pi * radius * length

    pile_count = grid_n_x * grid_n_y
    total_volume = single_volume * pile_count

    # 2x2 grid centered at (0, 0)
    offsets_x = [
        -spacing * (grid_n_x - 1) / 2.0 + i * spacing for i in range(grid_n_x)
    ]
    offsets_y = [
        -spacing * (grid_n_y - 1) / 2.0 + j * spacing for j in range(grid_n_y)
    ]

    piles = []
    idx = 0
    for ox in offsets_x:
        for oy in offsets_y:
            piles.append({
                "index": idx,
                "x_offset": ox,
                "y_offset": oy,
                "diameter": diameter,
                "radius": radius,
                "length": length,
                "volume": single_volume,
            })
            idx += 1

    return {
        "diameter": diameter,
        "radius": radius,
        "length": length,
        "spacing": spacing,
        "pile_count": pile_count,
        "piles": piles,
        "single_area": single_area,
        "single_volume": single_volume,
        "total_volume": total_volume,
        "total_volume_m3": total_volume / 1e9,
        "single_surface_area": single_surface_area,
    }

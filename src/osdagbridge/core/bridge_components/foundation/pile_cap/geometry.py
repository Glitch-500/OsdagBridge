import math

STEEL_DENSITY_KG_MM3 = 7850.0 / 1e9

def pile_cap_geometry(
    length_x=2200.0,
    width_y=1200.0,
    depth_z=600.0,
):
    area_xy = length_x * width_y
    volume = area_xy * depth_z
    surface_area = 2.0 * (
        length_x * width_y + length_x * depth_z + width_y * depth_z
    )
    return {
        "length_x": length_x,
        "width_y": width_y,
        "depth_z": depth_z,
        "area_xy": area_xy,
        "volume": volume,
        "volume_m3": volume / 1e9,
        "surface_area": surface_area,
    }

def pile_cap_reinforcement_geometry(
    length_x=2200.0,
    width_y=1200.0,
    depth_z=600.0,
    cover=40.0,
    main_dia=16.0,
    main_spacing=150.0,
    tie_dia=8.0,
    tie_spacing=200.0,
):
    eff_x = max(0.0, length_x - 2.0 * cover)
    eff_y = max(0.0, width_y - 2.0 * cover)

    # Number of bars running in X direction (spaced along Y)
    span_y = max(0.0, width_y - 2.0 * (cover + tie_dia) - main_dia)
    n_x_bars = max(2, int(round(span_y / main_spacing)) + 1)

    # Number of bars running in Y direction (spaced along X)
    span_x = max(0.0, length_x - 2.0 * (cover + tie_dia) - main_dia)
    n_y_bars = max(2, int(round(span_x / main_spacing)) + 1)

    # Two mats: bottom mat and top mat
    total_x_bars = n_x_bars * 2
    total_y_bars = n_y_bars * 2
    total_main_bars = total_x_bars + total_y_bars

    main_bars = []
    # Bottom mat: X bars at z_bot_x, Y bars above them
    z_bot = -depth_z / 2.0 + cover + tie_dia + main_dia / 2.0
    z_top = depth_z / 2.0 - cover - tie_dia - main_dia / 2.0

    dy = span_y / float(n_x_bars - 1) if n_x_bars > 1 else 0.0
    dx = span_x / float(n_y_bars - 1) if n_y_bars > 1 else 0.0

    for layer, z in [("bottom", z_bot), ("top", z_top)]:
        # Longitudinal bars (along X)
        for i in range(n_x_bars):
            y = -span_y / 2.0 + i * dy
            main_bars.append({
                "layer": layer,
                "direction": "X",
                "y": y,
                "z": z,
                "length": eff_x,
                "diameter": main_dia,
            })
        # Transverse bars (along Y)
        for j in range(n_y_bars):
            x = -span_x / 2.0 + j * dx
            main_bars.append({
                "layer": layer,
                "direction": "Y",
                "x": x,
                "z": z,
                "length": eff_y,
                "diameter": main_dia,
            })

    single_main_bar_area = math.pi * (main_dia / 2.0) ** 2
    total_main_length = total_x_bars * eff_x + total_y_bars * eff_y
    total_main_weight = total_main_length * single_main_bar_area * STEEL_DENSITY_KG_MM3

    # Vertical perimeter tie stirrups
    tie_perimeter = 2.0 * (
        (length_x - 2.0 * cover - tie_dia) + (depth_z - 2.0 * cover - tie_dia)
    )
    tie_count = max(2, int(round(eff_y / tie_spacing)))
    dy_tie = eff_y / float(tie_count)

    ties = []
    for k in range(tie_count):
        y = -width_y / 2.0 + cover + (k + 0.5) * dy_tie
        ties.append({
            "index": k,
            "y": y,
            "length": tie_perimeter,
            "diameter": tie_dia,
        })

    single_tie_area = math.pi * (tie_dia / 2.0) ** 2
    total_tie_length = tie_count * tie_perimeter
    total_tie_weight = total_tie_length * single_tie_area * STEEL_DENSITY_KG_MM3

    total_weight = total_main_weight + total_tie_weight
    total_rebar_volume = (
        total_main_length * single_main_bar_area + total_tie_length * single_tie_area
    )

    return {
        "eff_x": eff_x,
        "eff_y": eff_y,
        "n_x_bars": n_x_bars,
        "n_y_bars": n_y_bars,
        "total_main_bars": total_main_bars,
        "main_bars": main_bars,
        "tie_count": tie_count,
        "ties": ties,
        "total_main_length": total_main_length,
        "total_tie_length": total_tie_length,
        "total_weight_kg": total_weight,
        "total_rebar_volume": total_rebar_volume,
        "cover": cover,
    }

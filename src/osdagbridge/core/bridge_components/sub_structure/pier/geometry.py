import math

STEEL_DENSITY_KG_MM3 = 7850.0 / 1e9

def pier_geometry(diameter=800.0, height=3000.0):
    radius = diameter / 2.0
    area = math.pi * radius ** 2
    volume = area * height
    surface_area = 2.0 * math.pi * radius * height
    return {
        "diameter": diameter,
        "radius": radius,
        "height": height,
        "area": area,
        "volume": volume,
        "volume_m3": volume / 1e9,
        "surface_area": surface_area,
    }

def pier_reinforcement_geometry(
    diameter=800.0,
    height=3000.0,
    cover=40.0,
    main_dia=16.0,
    main_spacing=150.0,
    tie_dia=8.0,
    tie_spacing=200.0,
):
    # Main bar pitch circle radius sits inside the outer ties
    rebar_radius = diameter / 2.0 - cover - tie_dia - main_dia / 2.0
    perimeter = 2.0 * math.pi * rebar_radius
    # Max spacing rule: spacing must not exceed main_spacing
    main_bar_count = max(6, math.ceil(perimeter / main_spacing))

    main_bar_length = max(0.0, height - 2.0 * cover)
    single_main_bar_area = math.pi * (main_dia / 2.0) ** 2
    total_main_length = main_bar_count * main_bar_length
    total_main_weight = total_main_length * single_main_bar_area * STEEL_DENSITY_KG_MM3

    main_bars = []
    angle_step = 2.0 * math.pi / main_bar_count
    for i in range(main_bar_count):
        theta = i * angle_step
        bx = rebar_radius * math.cos(theta)
        by = rebar_radius * math.sin(theta)
        main_bars.append({
            "index": i,
            "x": bx,
            "y": by,
            "angle_rad": theta,
            "diameter": main_dia,
            "length": main_bar_length,
        })

    tie_radius = diameter / 2.0 - cover - tie_dia / 2.0
    single_tie_length = 2.0 * math.pi * tie_radius
    clear_tie_height = max(0.0, height - 2.0 * cover)
    tie_count = max(2, int(round(clear_tie_height / tie_spacing)))

    single_tie_area = math.pi * (tie_dia / 2.0) ** 2
    total_tie_length = tie_count * single_tie_length
    total_tie_weight = total_tie_length * single_tie_area * STEEL_DENSITY_KG_MM3

    ties = []
    dz = clear_tie_height / float(tie_count)
    for j in range(tie_count):
        z = cover + (j + 0.5) * dz
        ties.append({
            "index": j,
            "z": z,
            "radius": tie_radius,
            "diameter": tie_dia,
            "length": single_tie_length,
        })

    total_weight = total_main_weight + total_tie_weight
    total_rebar_volume = (
        total_main_length * single_main_bar_area + total_tie_length * single_tie_area
    )

    return {
        "rebar_radius": rebar_radius,
        "main_bar_count": main_bar_count,
        "main_bar_length": main_bar_length,
        "main_bars": main_bars,
        "tie_radius": tie_radius,
        "tie_count": tie_count,
        "ties": ties,
        "total_main_length": total_main_length,
        "total_tie_length": total_tie_length,
        "total_weight_kg": total_weight,
        "total_rebar_volume": total_rebar_volume,
        "cover": cover,
    }

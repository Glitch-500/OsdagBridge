import math

STEEL_DENSITY_KG_MM3 = 7850.0 / 1e9

def pier_cap_geometry(
    top_width=3000.0,
    bottom_width=1200.0,
    depth=600.0,
    length=12000.0,
):
    area_xz = ((top_width + bottom_width) / 2.0) * depth
    volume = area_xz * length
    slant = math.hypot((top_width - bottom_width) / 2.0, depth)
    surface_area = (
        2.0 * area_xz
        + (top_width + bottom_width + 2.0 * slant) * length
    )
    return {
        "top_width": top_width,
        "bottom_width": bottom_width,
        "depth": depth,
        "length": length,
        "area_xz": area_xz,
        "volume": volume,
        "volume_m3": volume / 1e9,
        "surface_area": surface_area,
    }

def pier_cap_length_from_deck(
    footpath_config="NONE",
    carriageway_width=12000.0,
    crash_barrier_base_width=450.0,
    footpath_width=1500.0,
    railing_width=275.0,
):
    try:
        from osdagbridge.core.bridge_components.super_structure.deck.builder import calculate_deck_width
        return calculate_deck_width(
            footpath_config=footpath_config,
            carriageway_width=carriageway_width,
            crash_barrier_base_width=crash_barrier_base_width,
            footpath_width=footpath_width,
            railing_width=railing_width,
        )
    except (ImportError, ModuleNotFoundError):
        if footpath_config == "NONE":
            return carriageway_width + 2.0 * crash_barrier_base_width
        elif footpath_config in ("LEFT", "RIGHT"):
            return (
                carriageway_width
                + 2.0 * crash_barrier_base_width
                + footpath_width
                + railing_width
            )
        elif footpath_config == "BOTH":
            return (
                carriageway_width
                + 2.0 * crash_barrier_base_width
                + 2.0 * footpath_width
                + 2.0 * railing_width
            )
        raise ValueError(f"Invalid footpath_config: {footpath_config}")

def pier_cap_reinforcement_geometry(
    top_width=3000.0,
    bottom_width=1200.0,
    depth=600.0,
    length=12000.0,
    cover=40.0,
    main_dia=16.0,
    main_spacing=150.0,
    tie_dia=8.0,
    tie_spacing=200.0,
):
    eff_length = max(0.0, length - 2.0 * cover)

    # Top and bottom longitudinal bar rows along cap length (Y)
    top_span_x = max(0.0, top_width - 2.0 * (cover + tie_dia) - main_dia)
    bot_span_x = max(0.0, bottom_width - 2.0 * (cover + tie_dia) - main_dia)

    n_top = max(2, int(round(top_span_x / main_spacing)) + 1)
    n_bot = max(2, int(round(bot_span_x / main_spacing)) + 1)
    total_main_bars = n_top + n_bot

    main_bars = []
    z_top_bar = depth / 2.0 - cover - tie_dia - main_dia / 2.0
    z_bot_bar = -depth / 2.0 + cover + tie_dia + main_dia / 2.0

    dx_top = top_span_x / float(n_top - 1) if n_top > 1 else 0.0
    for i in range(n_top):
        x = -top_span_x / 2.0 + i * dx_top
        main_bars.append({
            "layer": "top",
            "x": x,
            "z": z_top_bar,
            "diameter": main_dia,
            "length": eff_length,
        })

    dx_bot = bot_span_x / float(n_bot - 1) if n_bot > 1 else 0.0
    for i in range(n_bot):
        x = -bot_span_x / 2.0 + i * dx_bot
        main_bars.append({
            "layer": "bottom",
            "x": x,
            "z": z_bot_bar,
            "diameter": main_dia,
            "length": eff_length,
        })

    single_main_bar_area = math.pi * (main_dia / 2.0) ** 2
    total_main_length = total_main_bars * eff_length
    total_main_weight = total_main_length * single_main_bar_area * STEEL_DENSITY_KG_MM3

    # Trapezoidal stirrup ties spaced along Y
    tie_top_w = max(0.0, top_width - 2.0 * cover - tie_dia)
    tie_bot_w = max(0.0, bottom_width - 2.0 * cover - tie_dia)
    tie_h = max(0.0, depth - 2.0 * cover - tie_dia)
    slant_tie = math.hypot((tie_top_w - tie_bot_w) / 2.0, tie_h)
    single_tie_perimeter = tie_top_w + tie_bot_w + 2.0 * slant_tie

    tie_count = max(2, int(round(eff_length / tie_spacing)))
    dy_tie = eff_length / float(tie_count)

    ties = []
    for j in range(tie_count):
        y = -length / 2.0 + cover + (j + 0.5) * dy_tie
        ties.append({
            "index": j,
            "y": y,
            "top_width": tie_top_w,
            "bottom_width": tie_bot_w,
            "height": tie_h,
            "diameter": tie_dia,
            "length": single_tie_perimeter,
        })

    single_tie_area = math.pi * (tie_dia / 2.0) ** 2
    total_tie_length = tie_count * single_tie_perimeter
    total_tie_weight = total_tie_length * single_tie_area * STEEL_DENSITY_KG_MM3

    total_weight = total_main_weight + total_tie_weight
    total_rebar_volume = (
        total_main_length * single_main_bar_area + total_tie_length * single_tie_area
    )

    return {
        "eff_length": eff_length,
        "n_top": n_top,
        "n_bot": n_bot,
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

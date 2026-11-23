def calculate_substructure_placement(
    span_length_L=25000.0,
    girder_section_d=900.0,
    girder_section_tf_b=260.0,
    bearing_height=0.0,
    cap_depth=600.0,
    pier_height=3000.0,
    pile_cap_depth=600.0,
    pile_length=5000.0,
    pile_spacing=600.0,
    pile_grid_nx=2,
    pile_grid_ny=2,
):
    x_center = span_length_L / 2.0
    y_center = 0.0

    # Contact level below bottom of girder bottom flange
    girder_bottom_z = -(girder_section_d / 2.0 + girder_section_tf_b)
    z_cap_top = girder_bottom_z - bearing_height
    z_cap_bot = z_cap_top - cap_depth

    z_pier_top = z_cap_bot
    z_pier_bot = z_pier_top - pier_height

    z_pile_cap_top = z_pier_bot
    z_pile_cap_bot = z_pile_cap_top - pile_cap_depth

    z_pile_top = z_pile_cap_bot
    z_pile_bot = z_pile_top - pile_length

    # 2x2 grid offsets for piles
    pile_offsets_x = [
        -pile_spacing * (pile_grid_nx - 1) / 2.0 + i * pile_spacing
        for i in range(pile_grid_nx)
    ]
    pile_offsets_y = [
        -pile_spacing * (pile_grid_ny - 1) / 2.0 + j * pile_spacing
        for j in range(pile_grid_ny)
    ]

    piles = []
    idx = 0
    for ox in pile_offsets_x:
        for oy in pile_offsets_y:
            piles.append({
                "index": idx,
                "x": x_center + ox,
                "y": y_center + oy,
                "z_top": z_pile_top,
                "z_bot": z_pile_bot,
                "length": pile_length,
            })
            idx += 1

    return {
        "x_center": x_center,
        "y_center": y_center,
        "z_cap_top": z_cap_top,
        "z_cap_bot": z_cap_bot,
        "z_pier_top": z_pier_top,
        "z_pier_bot": z_pier_bot,
        "z_pile_cap_top": z_pile_cap_top,
        "z_pile_cap_bot": z_pile_cap_bot,
        "z_pile_top": z_pile_top,
        "z_pile_bot": z_pile_bot,
        "pier_cap": {
            "x": x_center,
            "y": y_center,
            "z_top": z_cap_top,
            "z_bot": z_cap_bot,
            "depth": cap_depth,
        },
        "pier": {
            "x": x_center,
            "y": y_center,
            "z_top": z_pier_top,
            "z_bot": z_pier_bot,
            "height": pier_height,
        },
        "pile_cap": {
            "x": x_center,
            "y": y_center,
            "z_top": z_pile_cap_top,
            "z_bot": z_pile_cap_bot,
            "depth": pile_cap_depth,
        },
        "piles": piles,
    }

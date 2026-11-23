import os
import sys
import math
from pathlib import Path
import ifcopenshell

# Ensure src is on sys.path
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / "src"))

from osdagbridge.core.bridge_types.plate_girder.dto import (
    BridgeParametersDTO,
    SectionDimsDTO,
    ISectionDimsDTO,
)
from osdagbridge.core.ifc_export_bridge.export_ifc_handler import (
    PlateGirderIfcExportHandler,
)


def create_sample_dto():
    return BridgeParametersDTO(
        span_length_L=25000.0,
        girder_section_d=900.0,
        girder_section_bf=500.0,
        girder_section_bf_b=500.0,
        girder_section_tf=260.0,
        girder_section_tf_b=260.0,
        girder_section_tw=100.0,
        num_girders=5,
        girder_spacing=2750.0,
        skew_angle=0.0,
        carriageway_width=12000.0,
        deck_thickness=400.0,
        footpath_config="BOTH",
        footpath_width=1500.0,
        railing_width=300.0,
        barrier_type="Rigid",
        crash_barrier_subtype="IRC-5R",
        enable_median=False,
        median_type="Raised Kerb",
        rail_count=3,
        railing_type="rcc",
        include_intermediate_stiffeners=True,
        intermediate_stiffener_spacing=2000.0,
        intermediate_stiffener_thickness=20.0,
        intermediate_stiffener_outstand=None,
        num_end_stiffener_pairs=4,
        end_stiffener_thickness=30.0,
        end_stiffener_outstand=None,
        include_longitudinal_stiffeners=False,
        num_longitudinal_stiffeners=0,
        longitudinal_stiffener_thickness=20.0,
        longitudinal_stiffener_outstand=None,
        cross_bracing_spacing=4000.0,
        bracing_type="X",
        x_bracket_option="BOTH",
        k_top_bracket=True,
        diagonal_section_type="ANGLE",
        diagonal_section_dims=SectionDimsDTO(leg_h=100, leg_w=50, connection_type="LONGER_LEG"),
        diagonal_thickness=5.0,
        top_chord_section_type="DOUBLE_CHANNEL",
        top_chord_section_dims=SectionDimsDTO(leg_h=80, leg_w=40, connection_type="LONGER_LEG"),
        top_chord_thickness=5.0,
        bottom_chord_section_type="ANGLE",
        bottom_chord_section_dims=SectionDimsDTO(leg_h=80, leg_w=40, connection_type="LONGER_LEG"),
        bottom_chord_thickness=5.0,
        end_diaphragm_type="Cross Bracing",
        end_diaphragm_spacing=100.0,
        end_diaphragm_bracing_type="K",
        end_diaphragm_diagonal_section_type="ANGLE",
        end_diaphragm_diagonal_section_dims=SectionDimsDTO(leg_h=100, leg_w=50, connection_type="LONGER_LEG"),
        end_diaphragm_diagonal_thickness=5.0,
        end_diaphragm_top_chord_section_type="CHANNEL",
        end_diaphragm_top_chord_section_dims=SectionDimsDTO(leg_h=80, leg_w=40, connection_type="LONGER_LEG"),
        end_diaphragm_top_chord_thickness=5.0,
        end_diaphragm_bottom_chord_section_type="ANGLE",
        end_diaphragm_bottom_chord_section_dims=SectionDimsDTO(leg_h=80, leg_w=40, connection_type="LONGER_LEG"),
        end_diaphragm_bottom_chord_thickness=5.0,
        end_diaphragm_section="I_SECTION",
        end_diaphragm_dims=ISectionDimsDTO(depth=800, flange_width=250, web_thickness=12, flange_thickness=100),
        steel_grade="E 250A",
        concrete_grade="M30",
    )


def verify_ifc_export(output_path="verified_bridge.ifc"):
    print("=" * 60)
    print("RUNNING IFC SUBSTRUCTURE VERIFICATION SCRIPT")
    print("=" * 60)

    dto = create_sample_dto()

    # Step 1: Export through PlateGirderIfcExportHandler
    export_ok = False
    def cb(success, msg):
        nonlocal export_ok
        export_ok = success
        print(f"Export Handler Callback: success={success}, msg={msg}")

    handler = PlateGirderIfcExportHandler(dto, output_path, completion_callback=cb)
    handler.export()

    if not export_ok or not os.path.exists(output_path):
        raise RuntimeError(f"Export failed for {output_path}")

    # Step 2: Reopen with ifcopenshell
    f = ifcopenshell.open(output_path)
    print(f"\n[OK] Reopened IFC file: {output_path}")
    print(f"  Schema: {f.schema}")
    assert f.schema == "IFC4", f"Expected IFC4 schema, got {f.schema}"

    # Step 3: Check storeys
    storeys = {s.Name: s for s in f.by_type("IfcBuildingStorey")}
    print(f"  Storeys: {list(storeys.keys())}")
    assert "Superstructure" in storeys, "Missing 'Superstructure' storey"
    assert "Substructure" in storeys, "Missing 'Substructure' storey"

    # Step 4: Count elements per storey
    sub_elements = []
    for rel in f.by_type("IfcRelContainedInSpatialStructure"):
        if rel.RelatingStructure == storeys["Substructure"]:
            sub_elements.extend(rel.RelatedElements)

    sub_counts = {}
    for e in sub_elements:
        sub_counts[e.is_a()] = sub_counts.get(e.is_a(), 0) + 1

    print("\n[OK] Substructure Storey Element Counts:")
    for k, v in sorted(sub_counts.items()):
        print(f"  {k}: {v}")

    assert sub_counts.get("IfcBeam") == 1, "Expected 1 Pier Cap (IfcBeam)"
    assert sub_counts.get("IfcColumn") == 1, "Expected 1 Pier (IfcColumn)"
    assert sub_counts.get("IfcFooting") == 1, "Expected 1 Pile Cap (IfcFooting)"
    assert sub_counts.get("IfcPile") == 4, "Expected 4 Piles (IfcPile)"
    assert sub_counts.get("IfcReinforcingBar", 0) > 0, "Expected IfcReinforcingBar elements"

    # Verify pile cap PredefinedType
    footings = [e for e in sub_elements if e.is_a("IfcFooting")]
    assert footings[0].PredefinedType == "PILE_CAP", f"Expected PILE_CAP, got {footings[0].PredefinedType}"

    # Step 5: Element Placements and Alignment Check (Rule 9)
    print("\n[OK] Substructure Element Placements & Member Axis Alignment:")
    def get_placement(elem):
        rel = elem.ObjectPlacement.RelativePlacement
        loc = rel.Location.Coordinates
        axis = rel.Axis.DirectionRatios if rel.Axis else (0.0, 0.0, 1.0)
        x_dir = rel.RefDirection.DirectionRatios if rel.RefDirection else (1.0, 0.0, 0.0)
        return loc, axis, x_dir

    cap = [e for e in sub_elements if e.is_a("IfcBeam")][0]
    pier = [e for e in sub_elements if e.is_a("IfcColumn")][0]
    pcap = [e for e in sub_elements if e.is_a("IfcFooting")][0]
    piles = [e for e in sub_elements if e.is_a("IfcPile")]

    loc_cap, axis_cap, x_cap = get_placement(cap)
    loc_pier, axis_pier, x_pier = get_placement(pier)
    loc_pcap, axis_pcap, x_pcap = get_placement(pcap)

    print(f"  Pier Cap:  origin=({loc_cap[0]:.3f}, {loc_cap[1]:.3f}, {loc_cap[2]:.3f}) | Local Z={axis_cap}")
    print(f"  Pier:      origin=({loc_pier[0]:.3f}, {loc_pier[1]:.3f}, {loc_pier[2]:.3f}) | Local Z={axis_pier}")
    print(f"  Pile Cap:  origin=({loc_pcap[0]:.3f}, {loc_pcap[1]:.3f}, {loc_pcap[2]:.3f}) | Local Z={axis_pcap}")
    for idx, p in enumerate(piles):
        loc_p, axis_p, _ = get_placement(p)
        print(f"  Pile {idx+1}:    origin=({loc_p[0]:.3f}, {loc_p[1]:.3f}, {loc_p[2]:.3f}) | Local Z={axis_p}")

    # Vertical contact check:
    # Pier Cap depth = 0.600 m -> Top = loc_cap[2] + 0.600
    assert math.isclose(loc_cap[2] + 0.600, -0.710, abs_tol=1e-3), "Pier Cap top must touch girder bottom (-0.710m)"
    assert math.isclose(loc_cap[2], loc_pier[2] + 3.000, abs_tol=1e-3), "Pier top must touch Pier Cap bottom (-1.310m)"
    assert math.isclose(loc_pier[2], loc_pcap[2] + 0.600, abs_tol=1e-3), "Pile Cap top must touch Pier base (-4.310m)"
    for p in piles:
        loc_p, _, _ = get_placement(p)
        assert math.isclose(loc_p[2] + 5.000, loc_pcap[2], abs_tol=1e-3), "Pile top must touch Pile Cap bottom (-4.910m)"

    print("  -> Alignment check PASSED: All substructure parts connect seamlessly.")

    # Step 6: Materials & Quantity Sets (Rule 5)
    print("\n[OK] Qto Quantity Sets & Bill of Quantities Check:")
    qto_sets = {}
    for rel in f.by_type("IfcRelDefinesByProperties"):
        pdef = rel.RelatingPropertyDefinition
        if pdef.is_a("IfcElementQuantity"):
            for e in rel.RelatedObjects:
                qto_sets[e.is_a()] = qto_sets.get(e.is_a(), set())
                qto_sets[e.is_a()].add(pdef.Name)

    for cls_name, qtos in sorted(qto_sets.items()):
        print(f"  {cls_name} -> {list(qtos)}")

    assert "Qto_ColumnBaseQuantities" in qto_sets.get("IfcColumn", set())
    assert "Qto_BeamBaseQuantities" in qto_sets.get("IfcBeam", set())
    assert "Qto_FootingBaseQuantities" in qto_sets.get("IfcFooting", set())
    assert "Qto_PileBaseQuantities" in qto_sets.get("IfcPile", set())
    assert "Qto_ReinforcingElementBaseQuantities" in qto_sets.get("IfcReinforcingBar", set())

    # Step 7: Clean up test file
    try:
        os.remove(output_path)
    except OSError:
        pass

    print("\n" + "=" * 60)
    print("ALL IFC SUBSTRUCTURE VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    verify_ifc_export()

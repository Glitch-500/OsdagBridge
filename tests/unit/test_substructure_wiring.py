import ast
import pytest

try:
    import PySide6
    _HAS_GUI = True
except (ImportError, ModuleNotFoundError):
    _HAS_GUI = False

try:
    import OCC
    _HAS_OCC = True
except (ImportError, ModuleNotFoundError):
    _HAS_OCC = False


def _parse_components_from_file():
    with open("src/osdagbridge/desktop/ui/cad_3d.py", "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "BridgeComponentCheckbox":
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and target.id == "COMPONENTS":
                            result = []
                            for elt in item.value.elts:
                                label = elt.elts[0].value
                                key = elt.elts[1].value if isinstance(elt.elts[1], ast.Constant) else None
                                result.append((label, key))
                            return result
    return []


def test_checkbox_components_registered():
    components = _parse_components_from_file()
    comp_map = dict(components)
    assert comp_map.get("Pier Cap") == "Pier Cap"
    assert comp_map.get("Pier") == "Pier"
    assert comp_map.get("Pile Cap") == "Pile Cap"
    assert comp_map.get("Piles") == "Piles"
    assert comp_map.get("Substructure Rebar") == "Substructure Rebar"


@pytest.mark.skipif(not _HAS_OCC, reason="Requires pythonOCC")
def test_cad_keys_defined():
    from osdagbridge.core.bridge_types.plate_girder.cad_generator import (
        KEY_CAD_PIER,
        KEY_CAD_PIER_CAP,
        KEY_CAD_PILE_CAP,
        KEY_CAD_PILES,
        KEY_CAD_SUBSTRUCTURE,
        KEY_CAD_SUBSTRUCTURE_REBAR,
    )
    assert KEY_CAD_PIER == "Pier"
    assert KEY_CAD_PIER_CAP == "Pier Cap"
    assert KEY_CAD_PILE_CAP == "Pile Cap"
    assert KEY_CAD_PILES == "Piles"
    assert KEY_CAD_SUBSTRUCTURE == "Substructure"
    assert KEY_CAD_SUBSTRUCTURE_REBAR == "Substructure Rebar"

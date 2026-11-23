# OsdagBridge

OsdagBridge is a modular, shared-core software plugin for the analysis and design of steel bridges within the Osdag ecosystem.  
It supports desktop (PySide6), web (Django + React), and CLI interfaces through a unified Python core.

The system currently supports:
- Plate Girder Bridges  
 

Additional bridge types can be added through the plugin architecture.

---

## Key Features

### Shared Core Architecture
All numerical logic and I/O are implemented once in `osdagbridge.core`.  
The desktop GUI, web app, and CLI all reuse the same core for consistent behavior.

### Modular Bridge-Type System
Each bridge type includes:
- DTO (input model schema)
- Initial sizing routines
- Structural analysis configuration
- Design and code-check modules
- CAD geometry generation
- Report generation utilities

### Reusable Bridge Components
Common structural elements are defined in `bridge_components/`:
- Girders  
- Decks  
- Crash barriers  
- Pedestals  
- Piers (circular column, reinforcement cage)  
- Pier caps (trapezoidal cap, stirrups)  
- Foundations (pile cap with two-way mats, 2x2 pile grid)  

Components are shared across multiple bridge types.

---

## Substructure & Foundation Module

The substructure system provides parametric 3D models (OpenCASCADE), desktop GUI visualization with independent checkbox toggles and opacity controls, and IFC4 BIM export with Bill of Quantities (Qto) metadata.

### Component Structure

```
src/osdagbridge/core/bridge_components/
├── sub_structure/
│   ├── placement.py           # Shared placement helper (CAD & IFC coordinate alignment)
│   ├── rebar_builder.py       # Rebar OCC solid helper (bars, circular ties, stirrups)
│   ├── pier/
│   │   ├── geometry.py        # Pure math: dimensions, bar counts, cover, volume (no OCC)
│   │   └── builder.py         # 3D OCC solids for pier cylinder and reinforcement cage
│   └── pier_cap/
│       ├── geometry.py        # Pure math: trapezoid profile, rebar math, deck width reuse
│       └── builder.py         # 3D OCC solids for trapezoid prism and stirrup reinforcement
└── foundation/
    ├── pile_cap/
    │   ├── geometry.py        # Pure math: box geometry, two-way mat rebar, ties
    │   └── builder.py         # 3D OCC solids for rectangular box and mat rebar
    └── pile/
        ├── geometry.py        # Pure math: 2x2 pile grid, cylindrical volume
        └── builder.py         # 3D OCC solids for 4 piles (concrete-only, no rebar)
```

### Parametric Defaults & Geometry Assumptions

All dimensions are keyword arguments with defaults in millimeters:
- **Pier**: Circular cylinder, diameter 800 mm, height 3000 mm.
- **Pier Cap**: Inverted trapezoid, top width 3000 mm, bottom width 1200 mm, depth 600 mm, length = total deck width (reusing `calculate_deck_width`).
- **Pile Cap**: Rectangular solid, 2200 x 1200 x 600 mm (X x Y x Z).
- **Piles**: 4 cylindrical piles in a 2x2 grid, diameter 400 mm, length 5000 mm, center-to-center spacing 600 mm. Piles are plain concrete with no rebar.
- **Reinforcement**: Main bars diameter 16 mm @ 150 mm c/c, ties/stirrups diameter 8 mm @ 200 mm c/c, clear cover 40 mm.
  - Pier cage: 15 vertical main bars on pitch circle radius 344 mm, 15 circular ties on radius 356 mm.
  - Pier cap: Top (20 bars) and bottom (8 bars) longitudinal layers with 60 closed trapezoidal stirrups.
  - Pile cap: Top and bottom two-way orthogonal mats (46 bars total) with 6 perimeter rectangular ties.

### Coordinate System & Vertical Stacking

- **Axes**: X along bridge span (0 to span length $L$), Y transverse across deck width, Z vertical upwards.
- **Span Center**: $X = L/2$, $Y = 0$.
- **Stacking Elevations**:
  - Girder bottom flange contact: $Z = -(D/2 + T_{\text{fb}})$.
  - Pier Cap: $Z \in [Z_{\text{cap\_bot}}, Z_{\text{cap\_top}}]$ where $Z_{\text{cap\_top}} = -(D/2 + T_{\text{fb}})$, depth 600 mm.
  - Pier Column: $Z \in [Z_{\text{pier\_bot}}, Z_{\text{pier\_top}}]$ where $Z_{\text{pier\_top}} = Z_{\text{cap\_bot}}$, height 3000 mm.
  - Pile Cap: $Z \in [Z_{\text{pc\_bot}}, Z_{\text{pc\_top}}]$ where $Z_{\text{pc\_top}} = Z_{\text{pier\_bot}}$, depth 600 mm.
  - Piles: $Z \in [Z_{\text{pile\_bot}}, Z_{\text{pile\_top}}]$ where $Z_{\text{pile\_top}} = Z_{\text{pc\_bot}}$, length 5000 mm.

### 3D CAD & GUI Integration

- **Interactive Checkboxes**: The desktop viewer side panel provides individual toggles for `Pier Cap`, `Pier`, `Pile Cap`, `Piles`, and `Substructure Rebar`.
- **Transparency**: Concrete elements are rendered semi-transparent (opacity 0.35, OCCT `transparency=0.65`) so internal opaque steel rebar (`transparency=0.0`) is visible within the concrete bodies.

### IFC4 BIM Export & Bill of Quantities

Substructure is exported through `File > Save 3D CAD Model > Save as type .ifc` via `PlateGirderIfcExportHandler`:
- **Storeys**: Elements are organized under a dedicated `Substructure` `IfcBuildingStorey` alongside the existing `Superstructure` storey. Existing superstructure elements remain completely untouched.
- **IFC Entities**:
  - Pier: `IfcColumn` with circle profile (`IfcCircleProfileDef`).
  - Pier Cap: `IfcBeam` with trapezoid profile, extruded along transverse axis.
  - Pile Cap: `IfcFooting` with `PredefinedType="PILE_CAP"`.
  - Piles: `IfcPile` (4 instances in 2x2 grid).
  - Rebar: `IfcReinforcingBar` (`PredefinedType="MAIN"` and `"LIGATURE"`).
- **Placements**: Each element has defined global placement and member-aligned local $Z$-axis.
- **Materials**: `Concrete_M30` for concrete bodies, `Steel_Fe500` for reinforcement.
- **Quantity Sets (Qto)**: `Qto_ColumnBaseQuantities`, `Qto_BeamBaseQuantities`, `Qto_FootingBaseQuantities`, `Qto_PileBaseQuantities`, `Qto_ReinforcingElementBaseQuantities` containing length, width, height, cross-section area, outer surface area, gross volume, gross weight, and element counts for BOQ calculation.

### Running Tests & Verification

Run the full test suite:
```bash
pytest -v
```

Run substructure unit tests:
```bash
pytest tests/unit/test_substructure_geometry.py tests/unit/test_substructure_builders.py tests/unit/test_substructure_rebar.py tests/unit/test_substructure_wiring.py tests/unit/test_ifc_substructure.py -v
```

Run the standalone IFC export verification script:
```bash
python tests/verify_ifc_substructure.py
```

### Multi-Solver Analysis Support
Multiple analysis backends are supported:
- Native lightweight FEM solver  
- OpenSeesPy  
- OspGrillage  

Solvers are switchable at runtime via adapters.

### Integrated Indian Standards
Included under `core/utils/codes/`:
- IRC:6–2017  
- IRC:22–2015  
- IRC:24–2010  

These modules provide load models, combinations, material factors, and code checks.

---

## Project Structure

```
OsdagBridge/
├── docs/
├── examples/
├── tests/
└── src/
    └── osdagbridge/
        ├── core/              # Analysis, design, IO, solvers, codes
        ├── bridge_types/      # Plate girder, box girder, truss
        ├── bridge_components/ # Reusable components
        ├── cli/               # Command-line interface
        ├── desktop/           # PySide6 GUI
        └── web/               # Django + React web stack
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/osdag-admin/OsdagBridge.git
cd OsdagBridge
```

Install in editable mode:

```bash
pip install -e .
```

---

## Usage

### Command-Line Interface

Run an analysis:

```bash
osdagbridge analyze project.yaml --solver native
```

Generate a report:

```bash
osdagbridge report project.yaml report.pdf
```

### Desktop Application

```bash
python -m osdagbridge.desktop
```

### Web Application

Backend:

```bash
python src/osdagbridge/web/backend/manage.py runserver
```

Frontend:

```bash
cd src/osdagbridge/web/frontend
npm install
npm start
```

---

## Testing

Run the complete test suite:

```bash
pytest -q
```

Continuous integration runs automatically through GitHub Actions (`.github/workflows/ci.yml`).

---

## Development Guidelines

### Key Code Locations
- Core logic: `src/osdagbridge/core/`
- Codes & standards: `src/osdagbridge/core/utils/codes/`
- Bridge types: `src/osdagbridge/bridge_types/`
- Components: `src/osdagbridge/bridge_components/`
- CLI: `src/osdagbridge/cli/`
- Desktop GUI: `src/osdagbridge/desktop/`
- Web backend/frontend: `src/osdagbridge/web/`

### Contribution Workflow
1. Fork the repository  
2. Create a feature branch  
3. Ensure all tests pass (`pytest`)  
4. Submit a pull request

---

## Acknowledgements

OsdagBridge is part of the Osdag project, promoting open-source tools for steel design education, research, and practice.

---

## License

This project is licensed under the MIT License.  
See the `LICENSE` file for full details.

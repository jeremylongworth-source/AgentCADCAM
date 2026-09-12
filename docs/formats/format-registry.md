# Format Registry

| Format | Intended purpose | Commonly preserved | Commonly lost or ambiguous | Required validation |
| --- | --- | --- | --- | --- |
| Native CAD | Authoritative parametric/product definition | Features, parameters, assemblies, PMI depending on product | Vendor-specific semantics and version compatibility | Source authority, version, units, opening/rebuild check |
| STEP AP242 | Structured neutral CAD/product exchange | B-rep geometry, assemblies, selected PMI/product data | Feature history, application-specific semantics | Schema/import check, units, geometry, PMI and revision comparison |
| IGES | Legacy surface/curve exchange | Surfaces, curves, basic geometry | Solid intent, topology, PMI, feature history | Healing/topology check, units, closure, source comparison |
| DXF | 2D geometry exchange | Curves, layers, annotations depending on export | Parametric intent, manufacturing meaning, some entities | Version, units, scale, entity support, closure and duplicates |
| SVG | 2D vector exchange | Paths and basic vector geometry | CAD units, layers, manufacturing semantics | ViewBox/units, scale, path closure, duplicate/open geometry |
| STL | Mesh geometry derivative | Triangle surface approximation | Units, PMI, materials, tolerances, design history | Manifoldness, normals, scale, build volume, source provenance |
| 3MF | Additive package exchange | Mesh plus package metadata and print intent where supported | Vendor-specific profile semantics and complete design intent | Package integrity, mesh, profile/material/printer compatibility |
| NC/G-code | Controller-directed textual artifact | Motions and commands expressible in dialect | Original design intent, safety, machine suitability | Units, dialect, modal state, tool/offset references, static review and simulation |
| STEP-NC | Research track for structured manufacturing data | Manufacturing feature/process semantics where supported | Ecosystem interoperability and machine support | Explicit research status; never assume runtime support |

Parseability is not semantic fidelity, and semantic fidelity is not manufacturing approval.

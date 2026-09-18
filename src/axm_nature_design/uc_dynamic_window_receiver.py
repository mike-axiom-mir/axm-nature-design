"""Nature-local Technical Art adapter for the east/rear Runtime dynamic window.

The exact Runtime/VFX owner proves that moving source vertices are already the single
contiguous source-index window [110,370).  This adapter preserves that source index
identity in one UC surface so a target host can exercise a real vertex-buffer region
update.  It intentionally stays in Nature Design: Universal Creation sees only its
generic axm.surface-3d/v0.1 contract and receives no branch, wind, Runtime or Godot
policy.

The material is proof-only.  Final Nature look, foliage sidedness, Animation timing,
physical wind, device performance, Art/QA acceptance, CANON and production readiness
remain outside this contract.
"""
from __future__ import annotations

import math
from typing import Any

from .uc_surface_bridge import SOURCE_COORDINATES, TARGET_COORDINATES, UC_SURFACE_SCHEMA, _source_to_uc

RECEIVER_SCHEMA = "axm.nature-east-rear-dynamic-window-uc-receiver/v0.1"
EXPECTED_TOTAL_VERTICES = 390
EXPECTED_DYNAMIC_WINDOW = (110, 370)
EXPECTED_DYNAMIC_VERTICES = 260
POSITION_STRIDE_BYTES = 12
PROOF_MATERIAL = {"color": "#6B7556FF", "metallic": 0.0, "roughness": 0.82}


def _sub(a: list[float], b: list[float]) -> list[float]:
    return [float(a[i]) - float(b[i]) for i in range(3)]


def _cross(a: list[float], b: list[float]) -> list[float]:
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def _normalize(v: list[float]) -> list[float]:
    length = math.sqrt(sum(float(x) * float(x) for x in v))
    if not math.isfinite(length) or length <= 1e-12:
        raise ValueError("dynamic-window receiver normal is degenerate")
    return [float(x) / length for x in v]


def _vertex_normals(vertices: list[list[float]], triangles: list[list[int]]) -> list[list[float]]:
    accum = [[0.0, 0.0, 0.0] for _ in vertices]
    for tri in triangles:
        if not isinstance(tri, list) or len(tri) != 3:
            raise ValueError("Nature triangle shape drift")
        a, b, c = [int(value) for value in tri]
        if any(index < 0 or index >= len(vertices) for index in (a, b, c)):
            raise ValueError("Nature triangle index drift")
        ab = _sub(vertices[b], vertices[a])
        ac = _sub(vertices[c], vertices[a])
        raw = _cross(ab, ac)
        area2 = math.sqrt(sum(value * value for value in raw))
        if not math.isfinite(area2) or area2 <= 1e-12:
            raise ValueError("Nature source contains a degenerate triangle")
        # Area-weighted accumulation is deterministic and proof-only.  It does not
        # replace source/Materials normal authority.
        for index in (a, b, c):
            for axis in range(3):
                accum[index][axis] += raw[axis]
    return [_normalize(row) for row in accum]


def build_dynamic_window_surface(
    source: dict[str, Any],
    mesh: dict[str, Any],
    runtime_receipt: dict[str, Any],
) -> dict[str, Any]:
    if source.get("coordinate_system") != SOURCE_COORDINATES:
        raise ValueError("Nature source coordinate-system drift")
    vertices = mesh.get("vertices")
    triangles = mesh.get("triangles")
    if not isinstance(vertices, list) or len(vertices) != EXPECTED_TOTAL_VERTICES:
        raise ValueError("east/rear receiver must retain exactly 390 source vertices")
    if not isinstance(triangles, list) or not triangles:
        raise ValueError("east/rear receiver is missing source triangles")

    representation = runtime_receipt.get("representation") or {}
    measurements = runtime_receipt.get("measurements") or {}
    if representation.get("dynamic_window_original_indices") != list(EXPECTED_DYNAMIC_WINDOW):
        raise ValueError("Runtime dynamic-window identity drift")
    if representation.get("geometry_reindexed") is not False or representation.get("index_buffer_changed") is not False:
        raise ValueError("Technical Art requires Runtime's no-reindex/no-index-rewrite result")
    if int(measurements.get("dynamic_vertices", -1)) != EXPECTED_DYNAMIC_VERTICES:
        raise ValueError("Runtime dynamic-vertex count drift")
    if float(measurements.get("maximum_control_candidate_vertex_component_delta_m", 1.0)) != 0.0:
        raise ValueError("Runtime control/candidate position identity is no longer exact")

    normals_source = _vertex_normals(vertices, triangles)
    positions_uc = [_source_to_uc([float(value) for value in vertex]) for vertex in vertices]
    normals_uc = [_source_to_uc(normal) for normal in normals_source]

    # [x,y,z] -> [x,z,y] has determinant -1, therefore each source triangle is
    # reversed exactly once at the receiving boundary.
    indices_uc: list[int] = []
    for tri in triangles:
        a, b, c = [int(value) for value in tri]
        indices_uc.extend([a, c, b])

    start, end = EXPECTED_DYNAMIC_WINDOW
    surface = {
        "schema": UC_SURFACE_SCHEMA,
        "name": f"{source.get('study_id', 'nature-east-rear')}-dynamic-window-receiver",
        "primitives": [{
            "id": "east-rear-dynamic-window",
            "positions": positions_uc,
            "normals": normals_uc,
            "indices": indices_uc,
            "material": dict(PROOF_MATERIAL),
        }],
    }
    return {
        "schema": RECEIVER_SCHEMA,
        "source_coordinate_system": SOURCE_COORDINATES,
        "target_coordinate_system": TARGET_COORDINATES,
        "surface": surface,
        "source_vertex_count": len(vertices),
        "source_triangle_count": len(triangles),
        "target_index_count": len(indices_uc),
        "source_vertex_to_uc_vertex_identity": True,
        "dynamic_window_original_indices": [start, end],
        "dynamic_window_target_vertex_indices": [start, end],
        "target_vertex_stride_bytes": POSITION_STRIDE_BYTES,
        "target_dynamic_byte_offset": start * POSITION_STRIDE_BYTES,
        "target_dynamic_byte_length": (end - start) * POSITION_STRIDE_BYTES,
        "target_full_position_bytes": len(vertices) * POSITION_STRIDE_BYTES,
        "coordinate_handedness_determinant": -1,
        "triangle_winding_reversed_exactly_once": True,
        "normal_scope": "TECHNICAL_ART_AREA_WEIGHTED_PROOF_NORMALS_NOT_SOURCE_OR_MATERIALS_AUTHORITY",
        "material_scope": "TECHNICAL_ART_RECEIVER_PROOF_ONLY_NOT_NATURE_LOOKDEV",
        "foliage_sidedness_scope": "TARGET_PROOF_MAY_OVERRIDE_CULLING_FOR_OBSERVABILITY_NOT_SOURCE_POLICY",
        "truth_boundary": {
            "source_or_geometry_reauthored": False,
            "runtime_window_reauthored": False,
            "vfx_or_wind_semantics_reauthored": False,
            "animation_timing_reauthored": False,
            "uc_domain_semantics_required": False,
            "target_host_partial_vertex_update_claimed": False,
            "target_device_performance_claimed": False,
            "art_or_visual_qa_acceptance_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }

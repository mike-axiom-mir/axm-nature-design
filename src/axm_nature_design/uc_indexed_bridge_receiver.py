"""Nature-local Technical Art adapter for the north-low indexed bridge diagnostic.

Geometry owns the diagnostic 8+8 bridge topology and exact indexed trunk receiver
points. Rigging owns the moving branch endpoint socket/domain and proves paired-span
non-collapse. This adapter only transports that already-owned evidence into one generic
UC surface whose first eight vertices form the moving endpoint region and whose final
eight vertices remain fixed.

Universal Creation receives only axm.surface-3d/v0.1. It does not learn Nature branch,
Rigging, indexed-trunk, Animation, Runtime, Godot, art-direction or production policy.
"""
from __future__ import annotations

import math
from typing import Any

from .uc_surface_bridge import SOURCE_COORDINATES, TARGET_COORDINATES, UC_SURFACE_SCHEMA, _source_to_uc

RECEIVER_SCHEMA = "axm.nature-north-low-indexed-bridge-uc-receiver/v0.1"
GEOMETRY_RESULT = "PASS_NORTH_LOW_EXACT_INDEXED_TRUNK_SURFACE_REBIND__HOLD_INDEXED_CUT_CONNECTED_JUNCTION"
RIGGING_RESULT = "PASS_NORTH_LOW_INDEXED_SURFACE_RECEIVER_RIGGING_REBIND_AND_CONTINUOUS_PAIRED_SPAN_NONCOLLAPSE_MINUS5_TO_PLUS5__HOLD_INDEXED_CUT_CONNECTED_JUNCTION_TRIANGLE_FOLDOVER_COLLISION"
EXPECTED_VERTICES = 16
EXPECTED_TRIANGLES = 16
EXPECTED_MOVING_VERTICES = 8
POSITION_STRIDE_BYTES = 12
PROOF_MATERIAL = {"color": "#73815FFF", "metallic": 0.0, "roughness": 0.82}


def _sub(a: list[float], b: list[float]) -> list[float]:
    return [float(a[i]) - float(b[i]) for i in range(3)]


def _cross(a: list[float], b: list[float]) -> list[float]:
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def _normalize(v: list[float]) -> list[float]:
    length = math.sqrt(sum(float(value) * float(value) for value in v))
    if not math.isfinite(length) or length <= 1e-12:
        raise ValueError("indexed bridge proof normal is degenerate")
    return [float(value) / length for value in v]


def _vertex_normals(vertices: list[list[float]], triangles: list[list[int]]) -> list[list[float]]:
    """Build neutral proof normals without changing owner geometry.

    The diagnostic bridge contains intentionally uneven triangle areas around the
    indexed projection. Area-weighted accumulation can let one large face overpower
    an adjacent face at a shared vertex and violate UC's fail-closed winding/normal
    contract. Equal-weight unit face normals preserve the exact owner topology while
    keeping every incident face in the same positive normal hemisphere. These remain
    Technical Art proof normals only; they are not Nature's final shading authority.
    """
    accum = [[0.0, 0.0, 0.0] for _ in vertices]
    for face in triangles:
        if len(face) != 3:
            raise ValueError("indexed bridge triangle cardinality drift")
        a, b, c = [int(value) for value in face]
        if min(a, b, c) < 0 or max(a, b, c) >= len(vertices):
            raise ValueError("indexed bridge triangle index drift")
        raw = _cross(_sub(vertices[b], vertices[a]), _sub(vertices[c], vertices[a]))
        face_normal = _normalize(raw)
        for index in (a, b, c):
            for axis in range(3):
                accum[index][axis] += face_normal[axis]
    normals = [_normalize(row) for row in accum]
    for triangle_index, face in enumerate(triangles):
        a, b, c = [int(value) for value in face]
        raw = _cross(_sub(vertices[b], vertices[a]), _sub(vertices[c], vertices[a]))
        if any(sum(raw[axis] * normals[index][axis] for axis in range(3)) <= 0.0 for index in (a, b, c)):
            raise ValueError(f"indexed bridge proof normal disagrees with owner winding at triangle {triangle_index}")
    return normals


def build_indexed_bridge_surface(
    source: dict[str, Any],
    geometry_report: dict[str, Any],
    geometry_candidate: dict[str, Any],
    rigging_receipt: dict[str, Any],
    *,
    moving_vertex_end: int = EXPECTED_MOVING_VERTICES,
) -> dict[str, Any]:
    if source.get("coordinate_system") != SOURCE_COORDINATES:
        raise ValueError("Nature source coordinate-system drift")
    if geometry_report.get("result") != GEOMETRY_RESULT:
        raise ValueError("exact indexed-surface Geometry prerequisite is not green")
    if rigging_receipt.get("result") != RIGGING_RESULT:
        raise ValueError("exact indexed-surface Rigging prerequisite is not green")
    if int(moving_vertex_end) != EXPECTED_MOVING_VERTICES:
        raise ValueError("Technical Art may not widen the exact Rigging moving endpoint region")
    if geometry_report.get("source_digest") != rigging_receipt.get("source_digest"):
        raise ValueError("Geometry/Rigging source identity disagreement")

    geometry_truth = geometry_report.get("truth_boundary") or {}
    rigging_truth = rigging_receipt.get("truth_boundary") or {}
    if geometry_truth.get("connected_branch_trunk_indexed_topology_proven") is not False:
        raise ValueError("Geometry prerequisite unexpectedly claims connected topology")
    if rigging_truth.get("technical_art_target_host_claimed") is not False:
        raise ValueError("Rigging prerequisite must not pre-claim Technical Art target-host authority")
    if rigging_truth.get("animation_timing_interpolation_or_playback_claimed") is not False:
        raise ValueError("Rigging prerequisite must not pre-claim Animation acceptance")

    bridge = geometry_candidate.get("bridge_only") or {}
    vertices = [[float(value) for value in row] for row in bridge.get("vertices", [])]
    triangles = [[int(value) for value in row] for row in bridge.get("triangles", [])]
    if len(vertices) != EXPECTED_VERTICES or len(triangles) != EXPECTED_TRIANGLES:
        raise ValueError("indexed bridge receiver cardinality drift")
    if any(len(row) != 3 or min(row) < 0 or max(row) >= EXPECTED_VERTICES for row in triangles):
        raise ValueError("indexed bridge receiver triangle drift")

    normals_source = _vertex_normals(vertices, triangles)
    positions_uc = [_source_to_uc(row) for row in vertices]
    normals_uc = [_source_to_uc(row) for row in normals_source]
    indices_uc: list[int] = []
    for a, b, c in triangles:
        # [x,y,z] -> [x,z,y] has determinant -1, therefore reverse once.
        indices_uc.extend([a, c, b])

    surface = {
        "schema": UC_SURFACE_SCHEMA,
        "name": "nature-north-low-indexed-bridge-target-receiver",
        "primitives": [{
            "id": "north-low-indexed-bridge",
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
        "source_vertex_count": EXPECTED_VERTICES,
        "source_triangle_count": EXPECTED_TRIANGLES,
        "moving_source_vertex_region": [0, EXPECTED_MOVING_VERTICES],
        "fixed_source_vertex_region": [EXPECTED_MOVING_VERTICES, EXPECTED_VERTICES],
        "moving_target_vertex_region": [0, EXPECTED_MOVING_VERTICES],
        "fixed_target_vertex_region": [EXPECTED_MOVING_VERTICES, EXPECTED_VERTICES],
        "source_vertex_to_uc_vertex_identity": True,
        "target_vertex_stride_bytes": POSITION_STRIDE_BYTES,
        "target_moving_byte_offset": 0,
        "target_moving_byte_length": EXPECTED_MOVING_VERTICES * POSITION_STRIDE_BYTES,
        "target_full_position_bytes": EXPECTED_VERTICES * POSITION_STRIDE_BYTES,
        "coordinate_handedness_determinant": -1,
        "triangle_winding_reversed_exactly_once": True,
        "normal_scope": "TECHNICAL_ART_EQUAL_WEIGHT_FACE_AVERAGE_NEUTRAL_PROOF_NORMALS_ONLY_NOT_FINAL_NATURE_NORMAL_AUTHORITY",
        "material_scope": "TECHNICAL_ART_RECEIVER_PROOF_ONLY_NOT_NATURE_LOOKDEV",
        "truth_boundary": {
            "geometry_or_rigging_reauthored": False,
            "indexed_trunk_cut_or_connected_junction_claimed": False,
            "production_skinning_claimed": False,
            "animation_timing_or_playback_claimed": False,
            "target_host_endpoint_region_transport_claimed": False,
            "runtime_controller_device_or_performance_claimed": False,
            "art_or_visual_qa_acceptance_claimed": False,
            "uc_domain_semantics_required": False,
            "canon_or_production_readiness_claimed": False,
        },
    }

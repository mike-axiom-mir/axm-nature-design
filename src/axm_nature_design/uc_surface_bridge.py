"""Explicit Nature Design -> Universal Creation surface handoff.

This module keeps Nature source semantics local while translating the current
sapling triangle body into Universal Creation's strict axm.surface-3d/v0.1
contract. It also closes one renderer-facing gap for planar leaf cards without
changing UC: leaf faces are emitted with explicit opposite-winding back faces so
the retained GLB does not depend on an unproven two-sided material extension.

The bridge is intentionally static. It does not carry flex zones, wind state,
rigging, animation, environment placement, or final look-development semantics.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Any

from .organic_form import build_mesh, digest as nature_digest, validate_source

BRIDGE_SCHEMA = "axm.nature-uc-surface-bridge-evidence/v0.1"
UC_SURFACE_SCHEMA = "axm.surface-3d/v0.1"
SOURCE_COORDINATES = "+X east/right, +Y north/forward, +Z up; metres"
TARGET_COORDINATES = "+X right, +Y up, +Z forward; metres"

# Proof-only materials make the two structural groups inspectable. They are not
# a Nature look-development contract and are deliberately owned by this bridge,
# not Universal Creation.
PROOF_MATERIALS = {
    "woody": {"color": "#6B5138FF", "metallic": 0.0, "roughness": 0.92},
    "foliage": {"color": "#4E7B45FF", "metallic": 0.0, "roughness": 0.88},
}


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sub(a: list[float], b: list[float]) -> list[float]:
    return [a[i] - b[i] for i in range(3)]


def _cross(a: list[float], b: list[float]) -> list[float]:
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def _normal(a: list[float], b: list[float], c: list[float]) -> list[float]:
    raw = _cross(_sub(b, a), _sub(c, a))
    length = math.sqrt(sum(value * value for value in raw))
    if not math.isfinite(length) or length <= 1e-12:
        raise ValueError("cannot bridge a degenerate source triangle")
    return [value / length for value in raw]


def _source_to_uc(vector: list[float]) -> list[float]:
    """Map Nature right/forward/up to UC right/up/forward.

    Swapping Y and Z changes handedness. Front-face triangle winding is therefore
    reversed when emitted so transformed normals and geometric winding agree.
    """
    if not isinstance(vector, (list, tuple)) or len(vector) != 3:
        raise ValueError("Nature bridge vectors must have exactly three values")
    values = [float(value) for value in vector]
    if not all(math.isfinite(value) for value in values):
        raise ValueError("Nature bridge vectors must be finite")
    x_right, y_forward, z_up = values
    return [round(x_right, 9), round(z_up, 9), round(y_forward, 9)]


def _region_by_triangle(mesh: dict[str, Any]) -> list[dict[str, Any]]:
    triangles = mesh.get("triangles")
    regions = mesh.get("regions")
    if not isinstance(triangles, list) or not isinstance(regions, list):
        raise ValueError("Nature mesh must expose triangles and regions")
    ownership: list[dict[str, Any] | None] = [None] * len(triangles)
    for region in regions:
        if not isinstance(region, dict):
            raise ValueError("Nature mesh region must be an object")
        start = region.get("triangle_start")
        count = region.get("triangle_count")
        if type(start) is not int or type(count) is not int or start < 0 or count <= 0 or start + count > len(triangles):
            raise ValueError("Nature mesh region triangle range is invalid")
        for index in range(start, start + count):
            if ownership[index] is not None:
                raise ValueError("Nature mesh regions overlap")
            ownership[index] = region
    if any(region is None for region in ownership):
        raise ValueError("Nature mesh contains triangles without region provenance")
    return [region for region in ownership if region is not None]


def _empty_group(identifier: str) -> dict[str, Any]:
    return {
        "id": identifier,
        "positions": [],
        "normals": [],
        "indices": [],
        "material": dict(PROOF_MATERIALS[identifier]),
    }


def _emit_face(group: dict[str, Any], points: list[list[float]], normal: list[float], *, reverse: bool) -> None:
    order = [0, 2, 1] if reverse else [0, 1, 2]
    base = len(group["positions"])
    for source_index in order:
        group["positions"].append(_source_to_uc(points[source_index]))
        group["normals"].append(_source_to_uc(normal))
    group["indices"].extend([base, base + 1, base + 2])


def adapt_source_for_uc(source: dict[str, Any]) -> dict[str, Any]:
    """Build a strict UC surface from the exact Nature source without mutation."""
    validate_source(source)
    if source.get("coordinate_system") != SOURCE_COORDINATES:
        raise ValueError("unsupported Nature coordinate system; refusing implicit conversion")

    mesh = build_mesh(source)
    owners = _region_by_triangle(mesh)
    vertices = mesh["vertices"]
    groups = {"woody": _empty_group("woody"), "foliage": _empty_group("foliage")}
    source_leaf_triangles = 0

    for triangle_index, triangle in enumerate(mesh["triangles"]):
        if not isinstance(triangle, list) or len(triangle) != 3 or any(type(index) is not int or not 0 <= index < len(vertices) for index in triangle):
            raise ValueError("Nature mesh triangle indices are invalid")
        points = [vertices[index] for index in triangle]
        face_normal = _normal(points[0], points[1], points[2])
        region = owners[triangle_index]
        is_leaf = region.get("kind") == "leaf-blade"
        target = groups["foliage" if is_leaf else "woody"]

        # The coordinate swap changes handedness, so the transformed front face
        # uses reversed winding while keeping the transformed source normal.
        _emit_face(target, points, face_normal, reverse=True)

        # UC's current bounded surface material contract has no sidedness field.
        # For planar foliage only, emit an explicit back face with opposite normal
        # rather than pretending target renderers will disable culling.
        if is_leaf:
            source_leaf_triangles += 1
            _emit_face(target, points, [-value for value in face_normal], reverse=False)

    surface = {
        "schema": UC_SURFACE_SCHEMA,
        "name": f"{source['study_id']}-nature-bridge",
        "primitives": [groups["woody"], groups["foliage"]],
    }
    return {
        "schema": BRIDGE_SCHEMA,
        "study_id": source["study_id"],
        "source_coordinate_system": SOURCE_COORDINATES,
        "target_coordinate_system": TARGET_COORDINATES,
        "source_digest": nature_digest(source),
        "source_mesh_digest": nature_digest(mesh),
        "source_triangles": len(mesh["triangles"]),
        "source_leaf_triangles": source_leaf_triangles,
        "emitted_triangles": sum(len(group["indices"]) // 3 for group in surface["primitives"]),
        "emitted_vertices": sum(len(group["positions"]) for group in surface["primitives"]),
        "leaf_sidedness_strategy": "EXPLICIT_OPPOSITE_WINDING_BACKFACE_GEOMETRY",
        "material_scope": "PROOF_ONLY_GROUPING_NOT_LOOKDEV",
        "surface_digest": digest(surface),
        "surface": surface,
        "truth_boundary": "Static Nature mesh -> UC surface handoff only. No two-sided material extension, final leaf shader, wind/deformation state, environment placement, target-engine import, visual acceptance, runtime cost, or production readiness is claimed.",
    }

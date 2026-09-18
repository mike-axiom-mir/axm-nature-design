"""Technical-Art Nature receiver adapter for five independently articulated primary branches.

This module stays in Nature Design.  It consumes Rigging-owned branch partitions and
converts the already-proven Nature mesh into a UC surface whose five branch groups can
be moved independently by a target host.  Universal Creation remains generic: it sees
only surface primitives plus a caller-authored rigid scene-graph manifest.

The adapter does not define wind, biological range of motion, animation timing,
simultaneous branch behavior, gameplay, Runtime policy, or visual acceptance.
"""
from __future__ import annotations

import copy
import math
from typing import Any

from .uc_surface_bridge import (
    BRIDGE_SCHEMA,
    PROOF_MATERIALS,
    SOURCE_COORDINATES,
    TARGET_COORDINATES,
    UC_SURFACE_SCHEMA,
    _normal,
    _region_by_triangle,
    _source_to_uc,
)

RECEIVER_SCHEMA = "axm.nature-primary-branch-uc-receiver/v0.1"
RIGID_SCENE_SCHEMA = "axm.rigid-scene-graph/v0.1"
BRANCH_IDS = ("south-low", "north-low", "east-mid", "west-high", "north-top")


def _sub(a: list[float], b: list[float]) -> list[float]:
    return [float(a[i]) - float(b[i]) for i in range(3)]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(float(a[i]) * float(b[i]) for i in range(3))


def _length(v: list[float]) -> float:
    return math.sqrt(_dot(v, v))


def _normalize(v: list[float]) -> list[float]:
    length = _length(v)
    if not math.isfinite(length) or length <= 1e-12:
        raise ValueError("receiver axis must be finite and non-degenerate")
    return [float(value) / length for value in v]


def _empty_group(identifier: str, material_key: str) -> dict[str, Any]:
    return {
        "id": identifier,
        "positions": [],
        "normals": [],
        "indices": [],
        "material": dict(PROOF_MATERIALS[material_key]),
    }


def _emit_face(
    group: dict[str, Any],
    points: list[list[float]],
    normal: list[float],
    *,
    origin: list[float] | None,
    reverse: bool,
) -> None:
    order = [0, 2, 1] if reverse else [0, 1, 2]
    base = len(group["positions"])
    for source_index in order:
        point = points[source_index]
        if origin is not None:
            point = _sub(point, origin)
        group["positions"].append(_source_to_uc(point))
        group["normals"].append(_source_to_uc(normal))
    group["indices"].extend([base, base + 1, base + 2])


def _triangle_records(surface: dict[str, Any], pivots: dict[str, list[float]]) -> list[tuple]:
    """Canonical neutral-world triangle records for partition-equivalence checks."""
    rows: list[tuple] = []
    for primitive in surface["primitives"]:
        primitive_id = primitive["id"]
        material_key = "foliage" if primitive_id.endswith("foliage") else "woody"
        pivot = None
        for branch_id, value in pivots.items():
            if primitive_id.startswith(branch_id + "-"):
                pivot = value
                break
        positions = primitive["positions"]
        normals = primitive["normals"]
        indices = primitive["indices"]
        for offset in range(0, len(indices), 3):
            tri_pos = []
            tri_norm = []
            for index in indices[offset:offset + 3]:
                position = list(positions[index])
                if pivot is not None:
                    position = [position[i] + pivot[i] for i in range(3)]
                tri_pos.append(tuple(round(float(value), 9) for value in position))
                tri_norm.append(tuple(round(float(value), 9) for value in normals[index]))
            rows.append((material_key, tuple(tri_pos), tuple(tri_norm)))
    rows.sort(key=repr)
    return rows


def _distance_from_axis(point: list[float], pivot: list[float], axis: list[float]) -> float:
    relative = _sub(point, pivot)
    projection = _dot(relative, axis)
    perpendicular = [relative[i] - projection * axis[i] for i in range(3)]
    return _length(perpendicular)


def build_primary_branch_receiver(
    source: dict[str, Any],
    mesh: dict[str, Any],
    rigging_family: dict[str, Any],
    *,
    baseline_surface: dict[str, Any],
) -> dict[str, Any]:
    if source.get("coordinate_system") != SOURCE_COORDINATES:
        raise ValueError("Nature source coordinate system drift")
    probes = (rigging_family.get("rigging_family") or {}).get("probes")
    if not isinstance(probes, list) or [row.get("branch_id") for row in probes] != list(BRANCH_IDS):
        raise ValueError("exact Rigging five-branch family is required")
    if not (rigging_family.get("rigging_family") or {}).get("pairwise_child_vertex_disjoint"):
        raise ValueError("Rigging branch partitions must be pairwise disjoint")
    if rigging_family.get("truth_boundary", {}).get("technical_art_target_host_claimed") is not False:
        raise ValueError("Rigging prerequisite must not pre-claim Technical Art target-host authority")

    owners = _region_by_triangle(mesh)
    vertices = mesh.get("vertices")
    triangles = mesh.get("triangles")
    if not isinstance(vertices, list) or not isinstance(triangles, list):
        raise ValueError("Nature mesh is missing vertices/triangles")

    branch_by_region: dict[str, str] = {}
    selected_by_branch: dict[str, set[int]] = {}
    probe_by_branch: dict[str, dict[str, Any]] = {}
    pivot_source: dict[str, list[float]] = {}
    pivot_uc: dict[str, list[float]] = {}
    axis_uc: dict[str, list[float]] = {}
    for probe in probes:
        branch_id = probe["branch_id"]
        probe_by_branch[branch_id] = probe
        selected = {int(value) for value in probe["selected_vertex_indices"]}
        selected_by_branch[branch_id] = selected
        if len(selected) != 52 or int(probe["selected_triangles"]) != 72:
            raise ValueError(f"Rigging partition drift for {branch_id}")
        for region_id in probe["selected_regions"]:
            if region_id in branch_by_region:
                raise ValueError(f"Rigging region is owned by multiple branches: {region_id}")
            branch_by_region[str(region_id)] = branch_id
        pivot = [float(value) for value in probe["joint_pivot_m"]]
        axis = _normalize([float(value) for value in probe["source_derived_axis"]])
        pivot_source[branch_id] = pivot
        pivot_uc[branch_id] = _source_to_uc(pivot)
        axis_uc[branch_id] = _normalize(_source_to_uc(axis))

    groups: dict[str, dict[str, Any]] = {
        "static-woody": _empty_group("static-woody", "woody"),
        "static-foliage": _empty_group("static-foliage", "foliage"),
    }
    for branch_id in BRANCH_IDS:
        groups[f"{branch_id}-woody"] = _empty_group(f"{branch_id}-woody", "woody")
        groups[f"{branch_id}-foliage"] = _empty_group(f"{branch_id}-foliage", "foliage")

    source_front_counts = {branch_id: 0 for branch_id in BRANCH_IDS}
    candidate_witnesses: dict[str, list[dict[str, Any]]] = {branch_id: [] for branch_id in BRANCH_IDS}
    source_leaf_triangles = 0

    for triangle_index, triangle in enumerate(triangles):
        if not isinstance(triangle, list) or len(triangle) != 3:
            raise ValueError("Nature mesh triangle drift")
        region = owners[triangle_index]
        region_id = str(region.get("id"))
        branch_id = branch_by_region.get(region_id)
        is_leaf = region.get("kind") == "leaf-blade"
        material_key = "foliage" if is_leaf else "woody"
        primitive_id = f"{branch_id}-{material_key}" if branch_id else f"static-{material_key}"
        origin = pivot_source[branch_id] if branch_id else None
        points = [[float(value) for value in vertices[index]] for index in triangle]
        face_normal = _normal(points[0], points[1], points[2])
        _emit_face(groups[primitive_id], points, face_normal, origin=origin, reverse=True)
        if branch_id:
            source_front_counts[branch_id] += 1
            selected = selected_by_branch[branch_id]
            if any(int(index) not in selected for index in triangle):
                raise ValueError(f"selected Rigging region escaped its vertex partition: {branch_id}/{region_id}")
            axis = [float(value) for value in probe_by_branch[branch_id]["source_derived_axis"]]
            pivot = pivot_source[branch_id]
            for index in triangle:
                point = [float(value) for value in vertices[index]]
                candidate_witnesses[branch_id].append({
                    "source_vertex_index": int(index),
                    "primitive_id": primitive_id,
                    "radial_distance_m": _distance_from_axis(point, pivot, axis),
                    "source_neutral_world_m": point,
                    "local_position_uc_m": _source_to_uc(_sub(point, pivot)),
                })
        if is_leaf:
            source_leaf_triangles += 1
            _emit_face(groups[primitive_id], points, [-value for value in face_normal], origin=origin, reverse=False)

    for branch_id in BRANCH_IDS:
        if source_front_counts[branch_id] != 72:
            raise ValueError(f"branch front-triangle partition drift: {branch_id}={source_front_counts[branch_id]}")
        for suffix in ("woody", "foliage"):
            primitive = groups[f"{branch_id}-{suffix}"]
            if not primitive["positions"] or not primitive["indices"]:
                raise ValueError(f"branch receiver primitive is unexpectedly empty: {branch_id}-{suffix}")

    surface = {
        "schema": UC_SURFACE_SCHEMA,
        "name": f"{source['study_id']}-primary-branch-target-receiver",
        "primitives": [groups["static-woody"], groups["static-foliage"]] + [
            groups[f"{branch_id}-{suffix}"]
            for branch_id in BRANCH_IDS
            for suffix in ("woody", "foliage")
        ],
    }
    if any(not primitive["positions"] for primitive in surface["primitives"]):
        raise ValueError("receiver surface contains an empty primitive")

    emitted_triangles = sum(len(primitive["indices"]) // 3 for primitive in surface["primitives"])
    baseline_triangles = sum(len(primitive["indices"]) // 3 for primitive in baseline_surface["primitives"])
    neutral_records = _triangle_records(surface, pivot_uc)
    baseline_records = _triangle_records(baseline_surface, {})
    if emitted_triangles != baseline_triangles or neutral_records != baseline_records:
        raise ValueError("partitioned receiver is not exact neutral-world geometry-equivalent to the static TA bridge")

    manifest_nodes: list[dict[str, Any]] = [
        {"name": "static-woody", "parent": None},
        {"name": "static-foliage", "parent": None},
    ]
    witnesses: dict[str, Any] = {}
    for branch_id in BRANCH_IDS:
        manifest_nodes.append({
            "name": f"{branch_id}-woody",
            "parent": None,
            "translation": pivot_uc[branch_id],
        })
        manifest_nodes.append({
            "name": f"{branch_id}-foliage",
            "parent": f"{branch_id}-woody",
        })
        candidates = candidate_witnesses[branch_id]
        witness = max(candidates, key=lambda row: (row["radial_distance_m"], -row["source_vertex_index"]))
        if float(witness["radial_distance_m"]) <= 1e-6:
            raise ValueError(f"branch witness is too close to rotation axis: {branch_id}")
        witnesses[branch_id] = {
            **witness,
            "owner_pivot_source_m": pivot_source[branch_id],
            "owner_axis_source": [float(value) for value in probe_by_branch[branch_id]["source_derived_axis"]],
            "target_pivot_uc_m": pivot_uc[branch_id],
            "target_axis_uc": axis_uc[branch_id],
            "handedness_transport": "SOURCE_AXIS_MAPPED_BY_[x,y,z]->[x,z,y]__TARGET_ANGLE_EQUALS_NEGATED_SOURCE_ANGLE",
        }

    return {
        "schema": RECEIVER_SCHEMA,
        "source_coordinate_system": SOURCE_COORDINATES,
        "target_coordinate_system": TARGET_COORDINATES,
        "surface_bridge_schema": BRIDGE_SCHEMA,
        "surface": surface,
        "manifest": {"schema": RIGID_SCENE_SCHEMA, "nodes": manifest_nodes},
        "branch_ids": list(BRANCH_IDS),
        "branch_front_triangle_counts": source_front_counts,
        "source_leaf_triangles": source_leaf_triangles,
        "emitted_triangles": emitted_triangles,
        "baseline_emitted_triangles": baseline_triangles,
        "neutral_world_geometry_equivalent_to_static_bridge": True,
        "branch_witnesses": witnesses,
        "truth_boundary": {
            "rigging_partition_reauthored": False,
            "animation_timing_reauthored": False,
            "target_coordinate_handedness_adapted_by_technical_art": True,
            "uc_domain_semantics_required": False,
            "simultaneous_multi_branch_motion_claimed": False,
            "wind_or_vfx_behavior_claimed": False,
            "runtime_controller_or_device_claimed": False,
            "gameplay_or_physics_claimed": False,
            "visual_acceptance_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }

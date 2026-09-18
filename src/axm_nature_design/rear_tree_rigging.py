"""Bounded Rigging evidence for the exact east/rear Nature branch-root socket.

This module consumes Organic-owned source metadata without rewriting it.  It proves
only a diagnostic rigid-child articulation around one exact source root.  It does
not author animation, wind, runtime/controller behavior, biology, or a production
range of motion.
"""
from __future__ import annotations

import copy
import math
from typing import Iterable

from .organic_form import build_mesh, digest, validate_source

SCHEMA = "axm.nature-east-rear-root-socket-rigging-evidence/v0.1"
RESULT = "PASS_NORTH_TOP_ROOT_SOCKET_RIGID_CHILD_ARTICULATION_DIAGNOSTIC_MINUS5_TO_PLUS5"
STUDY_ID = "east-rear-tree-neutral-001"
SOURCE_OWNER_HEAD = "fdc9d2b6ee729728551e22fd3eafa23ad60b6c7a"
EXPECTED_SOURCE_DIGEST = "178cd8cfb1a859bff411f60e13154109528062cf0ad2384b343d406cc0cc9d61"
EXPECTED_MESH_DIGEST = "d7fc5deaa1c12d1d8c7d7b6dc95bf1e8544ce26140ee2e4a7d2c67a2c4133e48"
BRANCH_ID = "north-top"
LEAF_CLUSTER_ID = "north-top-leaves"
FLEX_ZONE_ID = "north-top-branch-flex"
EXPECTED_FLEX_RADIUS_M = 0.12
DIAGNOSTIC_MIN_DEG = -5.0
DIAGNOSTIC_MAX_DEG = 5.0
REPRESENTATIVE_ANGLES_DEG = (-5.0, -2.5, 0.0, 2.5, 5.0)
TOL = 1e-12


def _add(a, b):
    return [float(a[i]) + float(b[i]) for i in range(3)]


def _sub(a, b):
    return [float(a[i]) - float(b[i]) for i in range(3)]


def _mul(a, s):
    return [float(a[i]) * float(s) for i in range(3)]


def _dot(a, b):
    return sum(float(a[i]) * float(b[i]) for i in range(3))


def _cross(a, b):
    return [
        float(a[1]) * float(b[2]) - float(a[2]) * float(b[1]),
        float(a[2]) * float(b[0]) - float(a[0]) * float(b[2]),
        float(a[0]) * float(b[1]) - float(a[1]) * float(b[0]),
    ]


def _length(v):
    return math.sqrt(_dot(v, v))


def _norm(v):
    n = _length(v)
    if n <= 1e-15:
        raise ValueError("cannot normalize zero-length vector")
    return [float(x) / n for x in v]


def _distance(a, b):
    return _length(_sub(a, b))


def _close_vec(a, b, tolerance=TOL):
    return len(a) == len(b) and all(abs(float(a[i]) - float(b[i])) <= tolerance for i in range(len(a)))


def _rotate_about_axis(point, pivot, axis, angle_deg):
    """Rodrigues rotation around a unit axis through pivot."""
    v = _sub(point, pivot)
    theta = math.radians(float(angle_deg))
    c = math.cos(theta)
    s = math.sin(theta)
    term0 = _mul(v, c)
    term1 = _mul(_cross(axis, v), s)
    term2 = _mul(axis, _dot(axis, v) * (1.0 - c))
    return _add(pivot, _add(_add(term0, term1), term2))


def _closest_segment_and_tangent(point, trunk):
    best = None
    for index in range(len(trunk) - 1):
        a = [float(x) for x in trunk[index]["position"]]
        b = [float(x) for x in trunk[index + 1]["position"]]
        ab = _sub(b, a)
        denom = _dot(ab, ab)
        if denom <= 1e-18:
            raise ValueError("degenerate trunk segment")
        t = max(0.0, min(1.0, _dot(_sub(point, a), ab) / denom))
        nearest = _add(a, _mul(ab, t))
        d = _distance(point, nearest)
        candidate = (d, index, t, _norm(ab), nearest)
        if best is None or candidate[0] < best[0]:
            best = candidate
    if best is None:
        raise ValueError("source has no trunk segment")
    return best


def _region_vertex_indices(mesh, region_ids: Iterable[str]):
    region_ids = set(region_ids)
    indices = set()
    triangle_count = 0
    found = set()
    for region in mesh["regions"]:
        if region["id"] not in region_ids:
            continue
        found.add(region["id"])
        start = int(region["triangle_start"])
        count = int(region["triangle_count"])
        triangle_count += count
        for triangle in mesh["triangles"][start : start + count]:
            indices.update(int(i) for i in triangle)
    missing = region_ids - found
    if missing:
        raise ValueError(f"missing selected regions: {sorted(missing)}")
    return sorted(indices), triangle_count


def _pairwise_distances(vertices):
    values = []
    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            values.append(_distance(vertices[i], vertices[j]))
    return values


def _max_abs_delta(a, b):
    if len(a) != len(b):
        raise ValueError("mismatched evidence vector lengths")
    return max((abs(float(x) - float(y)) for x, y in zip(a, b)), default=0.0)


def evaluate(
    source: dict,
    *,
    requested_branch_id: str = BRANCH_ID,
    joint_pivot_override=None,
    diagnostic_min_deg: float = DIAGNOSTIC_MIN_DEG,
    diagnostic_max_deg: float = DIAGNOSTIC_MAX_DEG,
    claim_source_rom: bool = False,
    claim_animation_acceptance: bool = False,
    claim_runtime_acceptance: bool = False,
) -> dict:
    """Evaluate one exact source-owned root socket as a diagnostic Rigging probe."""
    validate_source(source)
    if source.get("study_id") != STUDY_ID:
        raise ValueError("unexpected Nature study identity")
    source_digest = digest(source)
    if source_digest != EXPECTED_SOURCE_DIGEST:
        raise ValueError("exact Organic source identity drift")
    if requested_branch_id != BRANCH_ID:
        raise ValueError("this bounded lane owns only north-top")
    if abs(float(diagnostic_min_deg) - DIAGNOSTIC_MIN_DEG) > TOL or abs(float(diagnostic_max_deg) - DIAGNOSTIC_MAX_DEG) > TOL:
        raise ValueError("diagnostic probe interval may not be widened or retimed")
    if claim_source_rom:
        raise ValueError("diagnostic probe must not be promoted to source/biological ROM")
    if claim_animation_acceptance:
        raise ValueError("Rigging evidence cannot claim Animation acceptance")
    if claim_runtime_acceptance:
        raise ValueError("Rigging evidence cannot claim Runtime acceptance")

    branches = {branch["id"]: branch for branch in source["branches"]}
    branch = branches.get(BRANCH_ID)
    if branch is None:
        raise ValueError("north-top source branch missing")
    cluster = next((item for item in source["leaf_clusters"] if item["id"] == LEAF_CLUSTER_ID), None)
    if cluster is None:
        raise ValueError("north-top leaf cluster missing")
    flex = next((item for item in source["flex_zones"] if item["id"] == FLEX_ZONE_ID), None)
    if flex is None:
        raise ValueError("north-top flex metadata missing")
    if flex.get("status") != "DECLARED_NOT_DEFORMATION_TESTED":
        raise ValueError("source flex metadata truth boundary changed")
    if abs(float(flex["radius"]) - EXPECTED_FLEX_RADIUS_M) > TOL:
        raise ValueError("north-top owner flex radius drift")

    pivot = [float(x) for x in branch["points"][0]]
    flex_center = [float(x) for x in flex["center"]]
    if not _close_vec(pivot, flex_center):
        raise ValueError("owner flex center is not the exact branch root")
    if joint_pivot_override is not None and not _close_vec([float(x) for x in joint_pivot_override], pivot):
        raise ValueError("Rigging pivot must remain the exact source-owned flex center")

    nearest_distance, trunk_segment_index, trunk_t, trunk_tangent, trunk_nearest = _closest_segment_and_tangent(
        pivot, source["trunk"]
    )
    branch_tangent = _norm(_sub(branch["points"][1], pivot))
    axis_raw = _cross(trunk_tangent, branch_tangent)
    if _length(axis_raw) <= 1e-9:
        raise ValueError("source-derived bend-plane axis is degenerate")
    axis = _norm(axis_raw)

    mesh = build_mesh(source)
    mesh_digest = digest(mesh)
    if mesh_digest != EXPECTED_MESH_DIGEST:
        raise ValueError("exact generated Organic mesh identity drift")

    selected_region_ids = [
        f"branch:{BRANCH_ID}:0",
        f"branch:{BRANCH_ID}:1",
        *[f"leaf:{LEAF_CLUSTER_ID}:{i}" for i in range(len(cluster["blades"]))],
    ]
    selected_indices, selected_triangle_count = _region_vertex_indices(mesh, selected_region_ids)
    if len(selected_indices) != 52 or selected_triangle_count != 72:
        raise ValueError("north-top generated subtree identity drift")
    selected_set = set(selected_indices)
    fixed_indices = [i for i in range(len(mesh["vertices"])) if i not in selected_set]
    if len(fixed_indices) != 338:
        raise ValueError("fixed receiver partition drift")

    neutral_vertices = [[float(x) for x in v] for v in mesh["vertices"]]
    neutral_selected = [neutral_vertices[i] for i in selected_indices]
    neutral_pairwise = _pairwise_distances(neutral_selected)
    pivot_indices = [i for i in selected_indices if _distance(neutral_vertices[i], pivot) <= TOL]
    if len(pivot_indices) != 1:
        raise ValueError("expected one exact generated pivot-center vertex")

    poses = []
    maximum_fixed_drift = 0.0
    maximum_pivot_drift = 0.0
    maximum_pairwise_drift = 0.0
    maximum_axis_projection_drift = 0.0
    maximum_selected_displacement = 0.0

    for angle in REPRESENTATIVE_ANGLES_DEG:
        deformed = copy.deepcopy(neutral_vertices)
        for index in selected_indices:
            deformed[index] = _rotate_about_axis(neutral_vertices[index], pivot, axis, angle)

        fixed_drift = max((_distance(deformed[i], neutral_vertices[i]) for i in fixed_indices), default=0.0)
        pivot_drift = max((_distance(deformed[i], neutral_vertices[i]) for i in pivot_indices), default=0.0)
        selected = [deformed[i] for i in selected_indices]
        pairwise_drift = _max_abs_delta(_pairwise_distances(selected), neutral_pairwise)
        axis_projection_drift = max(
            (
                abs(_dot(_sub(deformed[i], pivot), axis) - _dot(_sub(neutral_vertices[i], pivot), axis))
                for i in selected_indices
            ),
            default=0.0,
        )
        selected_displacement = max(
            (_distance(deformed[i], neutral_vertices[i]) for i in selected_indices), default=0.0
        )

        maximum_fixed_drift = max(maximum_fixed_drift, fixed_drift)
        maximum_pivot_drift = max(maximum_pivot_drift, pivot_drift)
        maximum_pairwise_drift = max(maximum_pairwise_drift, pairwise_drift)
        maximum_axis_projection_drift = max(maximum_axis_projection_drift, axis_projection_drift)
        maximum_selected_displacement = max(maximum_selected_displacement, selected_displacement)

        poses.append(
            {
                "angle_deg": angle,
                "fixed_vertex_drift_m": fixed_drift,
                "pivot_vertex_drift_m": pivot_drift,
                "selected_pairwise_distance_drift_m": pairwise_drift,
                "selected_axis_projection_drift_m": axis_projection_drift,
                "maximum_selected_vertex_displacement_m": selected_displacement,
            }
        )

    checks = {
        "exact_source_identity": source_digest == EXPECTED_SOURCE_DIGEST,
        "exact_generated_mesh_identity": mesh_digest == EXPECTED_MESH_DIGEST,
        "exact_root_flex_metadata": _close_vec(flex_center, pivot)
        and abs(float(flex["radius"]) - EXPECTED_FLEX_RADIUS_M) <= TOL
        and flex["status"] == "DECLARED_NOT_DEFORMATION_TESTED",
        "source_derived_axis_is_unit": abs(_length(axis) - 1.0) <= TOL,
        "source_derived_axis_perpendicular_to_local_trunk": abs(_dot(axis, trunk_tangent)) <= TOL,
        "source_derived_axis_perpendicular_to_branch_tangent": abs(_dot(axis, branch_tangent)) <= TOL,
        "exact_generated_child_partition": len(selected_indices) == 52
        and selected_triangle_count == 72
        and len(fixed_indices) == 338,
        "fixed_receiver_is_exact": maximum_fixed_drift <= TOL,
        "source_owned_pivot_is_exact": maximum_pivot_drift <= TOL,
        "rigid_child_pairwise_distances_preserved": maximum_pairwise_drift <= TOL,
        "rotation_axis_projection_preserved": maximum_axis_projection_drift <= TOL,
        "diagnostic_interval_not_promoted_to_rom": not claim_source_rom,
        "animation_acceptance_not_claimed": not claim_animation_acceptance,
        "runtime_acceptance_not_claimed": not claim_runtime_acceptance,
    }

    return {
        "schema": SCHEMA,
        "result": RESULT if all(checks.values()) else "FAIL",
        "source_owner": {
            "repository": "mike-axiom-mir/axm-nature-design",
            "pr": 8,
            "head": SOURCE_OWNER_HEAD,
            "source_digest": source_digest,
            "generated_mesh_digest": mesh_digest,
        },
        "rigging_probe": {
            "branch_id": BRANCH_ID,
            "leaf_cluster_id": LEAF_CLUSTER_ID,
            "flex_zone_id": FLEX_ZONE_ID,
            "joint_pivot_m": pivot,
            "source_flex_radius_m": float(flex["radius"]),
            "source_flex_status": flex["status"],
            "local_trunk_segment": f"{source['trunk'][trunk_segment_index]['id']}->{source['trunk'][trunk_segment_index + 1]['id']}",
            "local_trunk_parameter": trunk_t,
            "local_trunk_nearest_point_m": trunk_nearest,
            "branch_root_to_trunk_centerline_m": nearest_distance,
            "source_derived_axis": axis,
            "diagnostic_interval_deg": [DIAGNOSTIC_MIN_DEG, DIAGNOSTIC_MAX_DEG],
            "diagnostic_interval_semantics": "RIGGING_VERIFICATION_PROBE_ONLY_NOT_SOURCE_OR_BIOLOGICAL_ROM",
            "representative_angles_deg": list(REPRESENTATIVE_ANGLES_DEG),
            "selected_regions": selected_region_ids,
            "selected_vertices": len(selected_indices),
            "selected_triangles": selected_triangle_count,
            "fixed_vertices": len(fixed_indices),
            "generated_pivot_vertex_indices": pivot_indices,
        },
        "measurements": {
            "maximum_fixed_vertex_drift_m": maximum_fixed_drift,
            "maximum_pivot_vertex_drift_m": maximum_pivot_drift,
            "maximum_selected_pairwise_distance_drift_m": maximum_pairwise_drift,
            "maximum_selected_axis_projection_drift_m": maximum_axis_projection_drift,
            "maximum_selected_vertex_displacement_m": maximum_selected_displacement,
        },
        "poses": poses,
        "continuous_invariant": {
            "statement": (
                "For every real angle in the declared diagnostic interval, selected child vertices use one "
                "Rodrigues rigid rotation around the exact source-owned pivot/axis while every unselected "
                "vertex is identity-mapped. Therefore pivot position, child pairwise distances, child axis "
                "projections, and fixed-receiver positions are invariant by construction."
            ),
            "collision_or_clearance_proven": False,
            "surface_attachment_or_stress_proven": False,
            "source_range_of_motion_proven": False,
        },
        "checks": checks,
        "truth_boundary": {
            "rigging_socket_probe_tested": True,
            "production_skin_weights_tested": False,
            "biological_range_of_motion_claimed": False,
            "wind_or_vfx_response_claimed": False,
            "animation_timing_or_playback_claimed": False,
            "runtime_controller_or_device_claimed": False,
            "geometry_topology_acceptance_claimed": False,
            "visual_acceptance_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }

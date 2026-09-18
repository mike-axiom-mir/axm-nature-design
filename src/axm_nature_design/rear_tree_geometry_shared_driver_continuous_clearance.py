"""Geometry-owned continuous cross-branch separation certificate.

Rigging owns one exact scalar diagnostic parameter over [-5,+5] degrees for five
pairwise-disjoint rigid branch children. Earlier Geometry evidence covers finite
static witnesses only. This module does not promote those samples. Instead it proves
a stronger, narrowly structural statement for cross-branch triangle pairs:

at neutral, every triangle pair has a fixed separating-axis projection margin larger
than the maximum amount both triangles can move toward that axis anywhere in the
entire Rigging interval.

For a point at perpendicular radius r from a fixed rotation axis, rotating by at
most theta from neutral moves it by at most 2*r*sin(theta/2). The distance-to-axis
norm is convex over a triangle, so the maximum triangle radius occurs at a vertex.
If one neutral separating-axis gap exceeds the sum of the two full-interval motion
bounds, that same fixed world-space axis remains separating for every parameter in
the closed interval.

This is a source-space Geometry certificate for child-child triangle separation only.
It is not physical collision, child-vs-fixed-receiver clearance, target-host playback,
biological ROM, Animation acceptance, Runtime acceptance, gameplay, or CANON.
"""
from __future__ import annotations

import itertools
import math
from typing import Iterable

from . import rear_tree_rigging as rig_math
from . import rear_tree_rigging_primary_branch_family as rig_family
from . import rear_tree_rigging_shared_driver_composition as rig_composition
from .organic_form import build_mesh, digest, validate_source
from .rear_tree_geometry_shared_driver_static_rebind import evaluate as evaluate_static_geometry

SCHEMA = "axm.nature-geometry-shared-driver-continuous-cross-branch-clearance/v0.1"
RESULT = "PASS_CONTINUOUS_SHARED_DRIVER_CROSS_BRANCH_TRIANGLE_SEPARATION_CERTIFIED"
HOLD_BUDGET = "HOLD_CONTINUOUS_CLEARANCE_CERTIFICATE_WORK_BUDGET"
HOLD_MARGIN = "HOLD_CONTINUOUS_CLEARANCE_UNCERTIFIED_TRIANGLE_PAIR"
PRIOR_GEOMETRY_HEAD = "3197eba862a6b7e6e93098a5b98d2c91bf48d32a"
RIGGING_CONTINUOUS_HEAD = "b4b480b415047fea90b4740f7702ced0dba9142d"
BRANCH_IDS = tuple(rig_family.BRANCH_IDS)
SHARED_DRIVER_MIN_DEG = float(rig_composition.SHARED_DRIVER_MIN_DEG)
SHARED_DRIVER_MAX_DEG = float(rig_composition.SHARED_DRIVER_MAX_DEG)
EXPECTED_MIGRATED_MESH_DIGEST = rig_family.EXPECTED_MIGRATED_MESH_DIGEST
TRIANGLES_PER_CHILD = 72
EXPECTED_BRANCH_PAIR_COUNT = 10
EXPECTED_CROSS_TRIANGLE_PAIR_COUNT = EXPECTED_BRANCH_PAIR_COUNT * TRIANGLES_PER_CHILD * TRIANGLES_PER_CHILD
SEPARATION_EPS_M = 1e-10
AXIS_EPS = 1e-14


def _sub(a: Iterable[float], b: Iterable[float]) -> tuple[float, float, float]:
    aa = tuple(float(v) for v in a)
    bb = tuple(float(v) for v in b)
    return (aa[0] - bb[0], aa[1] - bb[1], aa[2] - bb[2])


def _dot(a: Iterable[float], b: Iterable[float]) -> float:
    aa = tuple(float(v) for v in a)
    bb = tuple(float(v) for v in b)
    return aa[0] * bb[0] + aa[1] * bb[1] + aa[2] * bb[2]


def _cross(a: Iterable[float], b: Iterable[float]) -> tuple[float, float, float]:
    aa = tuple(float(v) for v in a)
    bb = tuple(float(v) for v in b)
    return (
        aa[1] * bb[2] - aa[2] * bb[1],
        aa[2] * bb[0] - aa[0] * bb[2],
        aa[0] * bb[1] - aa[1] * bb[0],
    )


def _length(v: Iterable[float]) -> float:
    return math.sqrt(_dot(v, v))


def _triangle_edges(triangle: list[tuple[float, float, float]]) -> list[tuple[float, float, float]]:
    return [
        _sub(triangle[1], triangle[0]),
        _sub(triangle[2], triangle[1]),
        _sub(triangle[0], triangle[2]),
    ]


def _candidate_separating_axes(
    left: list[tuple[float, float, float]],
    right: list[tuple[float, float, float]],
) -> list[tuple[float, float, float]]:
    """Return only proof-safe axes; completeness is not required for a positive proof."""
    left_edges = _triangle_edges(left)
    right_edges = _triangle_edges(right)
    left_normal = _cross(left_edges[0], left_edges[1])
    right_normal = _cross(right_edges[0], right_edges[1])
    axes = [left_normal, right_normal]
    axes.extend(_cross(a, b) for a in left_edges for b in right_edges)
    # Coplanar/disjoint triangles need in-plane edge-normal candidates too.
    axes.extend(_cross(left_normal, edge) for edge in left_edges)
    axes.extend(_cross(right_normal, edge) for edge in right_edges)
    axes.extend(_cross(left_normal, edge) for edge in right_edges)
    axes.extend(_cross(right_normal, edge) for edge in left_edges)
    return axes


def _projection_gap(
    left: list[tuple[float, float, float]],
    right: list[tuple[float, float, float]],
    axis: Iterable[float],
) -> float:
    length = _length(axis)
    if length <= AXIS_EPS:
        return 0.0
    unit = tuple(float(v) / length for v in axis)
    left_projection = [_dot(point, unit) for point in left]
    right_projection = [_dot(point, unit) for point in right]
    return max(
        min(right_projection) - max(left_projection),
        min(left_projection) - max(right_projection),
        0.0,
    )


def _neutral_separation_margin(
    left: list[tuple[float, float, float]],
    right: list[tuple[float, float, float]],
) -> float:
    """Maximum proven projection gap over a bounded deterministic axis family."""
    return max(
        (_projection_gap(left, right, axis) for axis in _candidate_separating_axes(left, right)),
        default=0.0,
    )


def _radius_to_axis(point: Iterable[float], pivot: Iterable[float], axis: Iterable[float]) -> float:
    offset = _sub(point, pivot)
    projection = _dot(offset, axis)
    radial = (
        offset[0] - float(tuple(axis)[0]) * projection,
        offset[1] - float(tuple(axis)[1]) * projection,
        offset[2] - float(tuple(axis)[2]) * projection,
    )
    return _length(radial)


def _full_interval_motion_bound(radius_m: float) -> float:
    max_abs_deg = max(abs(SHARED_DRIVER_MIN_DEG), abs(SHARED_DRIVER_MAX_DEG))
    return 2.0 * float(radius_m) * math.sin(math.radians(max_abs_deg) * 0.5)


def _owned_triangles(mesh: dict, selected_sets: dict[str, set[int]]) -> dict[str, list[int]]:
    owned = {branch_id: [] for branch_id in BRANCH_IDS}
    for triangle_index, triangle in enumerate(mesh["triangles"]):
        face = set(int(index) for index in triangle)
        owners = [branch_id for branch_id in BRANCH_IDS if face.issubset(selected_sets[branch_id])]
        if len(owners) == 1:
            owned[owners[0]].append(triangle_index)
    return owned


def evaluate(
    source: dict,
    *,
    requested_rigging_head: str = RIGGING_CONTINUOUS_HEAD,
    requested_interval_deg: tuple[float, float] = (SHARED_DRIVER_MIN_DEG, SHARED_DRIVER_MAX_DEG),
    max_triangle_pair_certificates: int = EXPECTED_CROSS_TRIANGLE_PAIR_COUNT,
    claim_child_fixed_receiver_clearance: bool = False,
    claim_physical_collision_or_gameplay: bool = False,
    claim_target_host_or_runtime: bool = False,
) -> dict:
    """Certify continuous child-child separation over the exact shared-driver interval."""
    validate_source(source)
    if requested_rigging_head != RIGGING_CONTINUOUS_HEAD:
        raise ValueError("exact continuous Rigging donor head drift")
    interval = tuple(float(v) for v in requested_interval_deg)
    if interval != (SHARED_DRIVER_MIN_DEG, SHARED_DRIVER_MAX_DEG):
        raise ValueError("continuous Geometry certificate requires the exact Rigging interval")
    if claim_child_fixed_receiver_clearance:
        raise ValueError("child-child certificate cannot claim child-vs-fixed-receiver clearance")
    if claim_physical_collision_or_gameplay:
        raise ValueError("Geometry separation evidence cannot claim physical collision/gameplay acceptance")
    if claim_target_host_or_runtime:
        raise ValueError("source-space Geometry evidence cannot claim target-host/Runtime acceptance")

    static = evaluate_static_geometry(source)
    if static.get("result") != "PASS_SHARED_DRIVER_STATIC_WITNESS_STRUCTURE_REBOUND":
        raise ValueError("prior static Geometry rebind is not green")

    rigging = rig_composition.evaluate(source)
    if rigging.get("result") != rig_composition.RESULT:
        raise ValueError("continuous Rigging composition donor is not green")
    certificate = rigging.get("continuous_parameter_certificate", {})
    if certificate.get("continuous_for_every_real_parameter_in_closed_interval") is not True:
        raise ValueError("Rigging donor does not expose continuous parameter identity")
    if certificate.get("continuous_collision_clearance_proven") is not False:
        raise ValueError("Rigging donor unexpectedly claims continuous collision clearance")

    mesh = build_mesh(source)
    mesh_digest = digest(mesh)
    if mesh_digest != EXPECTED_MIGRATED_MESH_DIGEST:
        raise ValueError("exact Geometry-migrated receiver identity drift")

    probes = [rig_family._probe_branch(source, mesh, branch_id) for branch_id in BRANCH_IDS]
    probes_by_branch = {probe["branch_id"]: probe for probe in probes}
    selected_sets = {
        branch_id: set(int(index) for index in probes_by_branch[branch_id]["selected_vertex_indices"])
        for branch_id in BRANCH_IDS
    }
    if any(selected_sets[left] & selected_sets[right] for i, left in enumerate(BRANCH_IDS) for right in BRANCH_IDS[i + 1 :]):
        raise ValueError("continuous certificate requires pairwise-disjoint child vertex ownership")

    owned = _owned_triangles(mesh, selected_sets)
    if any(len(indices) != TRIANGLES_PER_CHILD for indices in owned.values()):
        raise ValueError("exact 72-triangle child ownership drift")

    pair_ids = list(itertools.combinations(BRANCH_IDS, 2))
    expected_pair_certificates = sum(len(owned[left]) * len(owned[right]) for left, right in pair_ids)
    if len(pair_ids) != EXPECTED_BRANCH_PAIR_COUNT or expected_pair_certificates != EXPECTED_CROSS_TRIANGLE_PAIR_COUNT:
        raise ValueError("cross-branch triangle-pair family cardinality drift")

    requested_budget = int(max_triangle_pair_certificates)
    if requested_budget < expected_pair_certificates:
        return {
            "schema": SCHEMA,
            "result": HOLD_BUDGET,
            "lineage": {
                "prior_geometry_head": PRIOR_GEOMETRY_HEAD,
                "rigging_continuous_head": RIGGING_CONTINUOUS_HEAD,
                "migrated_mesh_digest": mesh_digest,
            },
            "work": {
                "triangle_pair_certificates_required": expected_pair_certificates,
                "triangle_pair_certificate_budget": requested_budget,
                "triangle_pair_certificates_performed": 0,
                "partial_clearance_verdict_exposed": False,
            },
            "truth_boundary": {
                "continuous_cross_branch_separation_proven": False,
                "budget_hold_before_scan": True,
                "child_fixed_receiver_clearance_checked": False,
                "physical_collision_or_gameplay_claimed": False,
                "target_host_or_runtime_claimed": False,
                "canon_or_production_readiness_claimed": False,
            },
        }

    vertices = [tuple(float(value) for value in vertex) for vertex in mesh["vertices"]]
    triangle_radius: dict[tuple[str, int], float] = {}
    for branch_id in BRANCH_IDS:
        probe = probes_by_branch[branch_id]
        pivot = probe["joint_pivot_m"]
        axis = probe["source_derived_axis"]
        if abs(rig_math._length(axis) - 1.0) > rig_family.TOL:
            raise ValueError(f"non-unit Rigging axis: {branch_id}")
        for triangle_index in owned[branch_id]:
            triangle_radius[(branch_id, triangle_index)] = max(
                _radius_to_axis(vertices[vertex_index], pivot, axis)
                for vertex_index in mesh["triangles"][triangle_index]
            )

    performed = 0
    uncertified: list[dict] = []
    pair_rows: list[dict] = []
    global_minimum_slack = math.inf
    global_maximum_motion_bound = 0.0
    global_tightest: dict | None = None

    for left, right in pair_ids:
        pair_minimum_slack = math.inf
        pair_maximum_motion_bound = 0.0
        pair_tightest: dict | None = None
        pair_uncertified = 0
        for left_triangle_index in owned[left]:
            left_triangle = [vertices[index] for index in mesh["triangles"][left_triangle_index]]
            left_motion = _full_interval_motion_bound(triangle_radius[(left, left_triangle_index)])
            for right_triangle_index in owned[right]:
                performed += 1
                right_triangle = [vertices[index] for index in mesh["triangles"][right_triangle_index]]
                right_motion = _full_interval_motion_bound(triangle_radius[(right, right_triangle_index)])
                total_motion = left_motion + right_motion
                neutral_margin = _neutral_separation_margin(left_triangle, right_triangle)
                slack = neutral_margin - total_motion
                row = {
                    "left_triangle_index": left_triangle_index,
                    "right_triangle_index": right_triangle_index,
                    "neutral_separating_axis_margin_m": neutral_margin,
                    "full_interval_combined_motion_bound_m": total_motion,
                    "certified_slack_m": slack,
                }
                if slack <= SEPARATION_EPS_M:
                    pair_uncertified += 1
                    if len(uncertified) < 32:
                        uncertified.append({"left": left, "right": right, **row})
                if slack < pair_minimum_slack:
                    pair_minimum_slack = slack
                    pair_tightest = row
                if slack < global_minimum_slack:
                    global_minimum_slack = slack
                    global_tightest = {"left": left, "right": right, **row}
                pair_maximum_motion_bound = max(pair_maximum_motion_bound, total_motion)
                global_maximum_motion_bound = max(global_maximum_motion_bound, total_motion)
        pair_rows.append(
            {
                "left": left,
                "right": right,
                "triangle_pair_certificates": len(owned[left]) * len(owned[right]),
                "uncertified_triangle_pair_count": pair_uncertified,
                "minimum_certified_slack_m": pair_minimum_slack,
                "maximum_full_interval_combined_motion_bound_m": pair_maximum_motion_bound,
                "tightest_pair": pair_tightest,
            }
        )

    all_certified = not uncertified and performed == expected_pair_certificates and global_minimum_slack > SEPARATION_EPS_M
    result = RESULT if all_certified else HOLD_MARGIN

    return {
        "schema": SCHEMA,
        "result": result,
        "lineage": {
            "prior_geometry_head": PRIOR_GEOMETRY_HEAD,
            "rigging_continuous_head": RIGGING_CONTINUOUS_HEAD,
            "organic_source_owner_head": rig_family.SOURCE_OWNER_HEAD,
            "geometry_receiver_head": rig_family.GEOMETRY_RECEIVER_HEAD,
            "source_digest": rig_family.EXPECTED_SOURCE_DIGEST,
            "migrated_mesh_digest": mesh_digest,
        },
        "scope": {
            "shared_driver_interval_deg": [SHARED_DRIVER_MIN_DEG, SHARED_DRIVER_MAX_DEG],
            "branch_ids": list(BRANCH_IDS),
            "branch_pair_count": len(pair_ids),
            "triangles_per_child": TRIANGLES_PER_CHILD,
            "cross_branch_triangle_pair_trajectories": expected_pair_certificates,
            "method": "NEUTRAL_FIXED_SEPARATING_AXIS_MARGIN_GT_SUM_OF_FULL_INTERVAL_RIGID_ROTATION_DISPLACEMENT_BOUNDS",
            "motion_bound_formula": "delta_triangle <= 2 * max_vertex_radius_to_axis * sin(max_abs_angle_rad / 2)",
            "fixed_axis_reasoning": "If a neutral world-space projection gap exceeds both triangles' maximum Euclidean movement, that same axis remains separating for the entire closed parameter interval.",
            "separation_epsilon_m": SEPARATION_EPS_M,
        },
        "measurements": {
            "triangle_pair_certificates_performed": performed,
            "uncertified_triangle_pair_count": sum(row["uncertified_triangle_pair_count"] for row in pair_rows),
            "minimum_certified_slack_m": global_minimum_slack,
            "maximum_full_interval_combined_motion_bound_m": global_maximum_motion_bound,
            "tightest_pair": global_tightest,
            "pair_rows": pair_rows,
            "uncertified_examples": uncertified,
        },
        "prior_evidence": {
            "static_geometry_result": static["result"],
            "continuous_rigging_result": rigging["result"],
            "finite_static_witnesses_promoted_to_continuous": False,
        },
        "truth_boundary": {
            "continuous_cross_branch_separation_proven": all_certified,
            "proof_is_source_space_triangle_separation_not_physical_collision": True,
            "child_internal_self_intersection_checked": False,
            "child_fixed_receiver_clearance_checked": False,
            "adjacent_attachment_contact_or_foldover_checked": False,
            "branch_stress_or_attachment_strength_checked": False,
            "source_or_biological_rom_claimed": False,
            "animation_timing_or_playback_claimed": False,
            "physical_wind_claimed": False,
            "target_host_or_runtime_claimed": False,
            "physics_or_gameplay_claimed": False,
            "automatic_source_or_receiver_adoption": False,
            "canon_or_production_readiness_claimed": False,
            "game_readiness_or_geometry_mastery_claimed": False,
        },
    }

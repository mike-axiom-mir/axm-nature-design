"""Source-owned neutral branch transition evidence for the east/rear Nature tree.

This observer measures only authored centerlines and radii. It estimates how far each
primary branch's first tapered segment remains fully supported by the authored trunk
radial envelope before that full branch radius first reaches the envelope boundary.

It does not inspect indexed connectivity, choose a weld/remesh strategy, simulate
deformation, assign rig weights, or establish botanical/biological attachment.
"""
from __future__ import annotations

import math

SCHEMA = "axm.nature-neutral-branch-transition-envelope/v0.1"
FLEX_STATUS = "DECLARED_NOT_DEFORMATION_TESTED"
TOLERANCE = 1e-9
SEARCH_STEPS = 4096
BISECTION_STEPS = 80


def _sub(a, b):
    return [float(a[i]) - float(b[i]) for i in range(3)]


def _dot(a, b):
    return sum(float(a[i]) * float(b[i]) for i in range(3))


def _length(v):
    return math.sqrt(_dot(v, v))


def _lerp(a, b, t):
    return [float(a[i]) + t * (float(b[i]) - float(a[i])) for i in range(3)]


def _vector_matches(a, b, tolerance=TOLERANCE):
    return (
        isinstance(a, list)
        and isinstance(b, list)
        and len(a) == len(b) == 3
        and all(abs(float(a[i]) - float(b[i])) <= tolerance for i in range(3))
    )


def _closest_on_segment(point, a, b):
    ab = _sub(b, a)
    denom = _dot(ab, ab)
    if denom <= 1e-18:
        raise ValueError("zero-length trunk segment")
    t = _dot(_sub(point, a), ab) / denom
    t = max(0.0, min(1.0, t))
    closest = [float(a[i]) + t * ab[i] for i in range(3)]
    return t, closest, _length(_sub(point, closest))


def _nearest_trunk_support(trunk, point):
    candidates = []
    for index in range(len(trunk) - 1):
        start = trunk[index]
        end = trunk[index + 1]
        t, closest, distance = _closest_on_segment(point, start["position"], end["position"])
        radius = float(start["radius"]) + t * (float(end["radius"]) - float(start["radius"]))
        candidates.append(
            {
                "segment": f"{start['id']}->{end['id']}",
                "segment_index": index,
                "segment_t": t,
                "closest_centerline_point_m": closest,
                "centerline_distance_m": distance,
                "local_trunk_radius_m": radius,
            }
        )
    return min(candidates, key=lambda item: (item["centerline_distance_m"], item["segment_index"]))


def _sample_first_segment(trunk, branch, u):
    points = branch["points"]
    radii = branch["radii"]
    point = _lerp(points[0], points[1], u)
    branch_radius = float(radii[0]) + u * (float(radii[1]) - float(radii[0]))
    support = _nearest_trunk_support(trunk, point)
    margin = support["local_trunk_radius_m"] - support["centerline_distance_m"] - branch_radius
    return {
        "u": u,
        "point_m": point,
        "branch_radius_m": branch_radius,
        "neutral_support_margin_m": margin,
        **support,
    }


def _first_exit_boundary(trunk, branch):
    root = _sample_first_segment(trunk, branch, 0.0)
    if root["neutral_support_margin_m"] < -TOLERANCE:
        raise ValueError(f"branch {branch.get('id')} root is outside the authored trunk support envelope")

    end = _sample_first_segment(trunk, branch, 1.0)
    previous = root
    bracket = None
    for index in range(1, SEARCH_STEPS + 1):
        u = index / SEARCH_STEPS
        current = _sample_first_segment(trunk, branch, u)
        if previous["neutral_support_margin_m"] > 0.0 and current["neutral_support_margin_m"] <= 0.0:
            bracket = (previous["u"], current["u"])
            break
        previous = current

    if bracket is None:
        return root, end, None

    low, high = bracket
    for _ in range(BISECTION_STEPS):
        mid = (low + high) * 0.5
        sample = _sample_first_segment(trunk, branch, mid)
        if sample["neutral_support_margin_m"] > 0.0:
            low = mid
        else:
            high = mid

    boundary = _sample_first_segment(trunk, branch, (low + high) * 0.5)
    return root, end, boundary


def evaluate(source: dict) -> dict:
    trunk = source.get("trunk", [])
    branches = source.get("branches", [])
    flex_zones = source.get("flex_zones", [])
    if len(trunk) < 2:
        raise ValueError("transition evidence requires at least two authored trunk points")
    if not branches:
        raise ValueError("transition evidence requires authored branches")
    if not flex_zones or any(zone.get("status") != FLEX_STATUS for zone in flex_zones):
        raise ValueError("all source flex declarations must remain unproven")

    reports = []
    for branch in branches:
        points = branch.get("points", [])
        radii = branch.get("radii", [])
        if len(points) < 2 or len(radii) < 2:
            raise ValueError(f"branch {branch.get('id')} requires a first tapered segment")
        first_segment_length = _length(_sub(points[1], points[0]))
        if first_segment_length <= 1e-12:
            raise ValueError(f"branch {branch.get('id')} first segment must have nonzero length")
        if float(radii[0]) <= 0.0 or float(radii[1]) <= 0.0:
            raise ValueError(f"branch {branch.get('id')} first-segment radii must be positive")

        root = [float(value) for value in points[0]]
        matching_zones = [zone for zone in flex_zones if _vector_matches(zone.get("center"), root)]
        if len(matching_zones) != 1:
            raise ValueError(f"branch {branch.get('id')} requires exactly one flex declaration at its root")
        zone = matching_zones[0]

        root_sample, end_sample, boundary = _first_exit_boundary(trunk, branch)
        if boundary is None:
            transition_state = "FULL_FIRST_SEGMENT_REMAINS_WITHIN_TRUNK_RADIAL_ENVELOPE"
            embedded_fraction = 1.0
            embedded_length = first_segment_length
            boundary_payload = None
        else:
            transition_state = "FULL_BRANCH_RADIUS_EXITS_TRUNK_RADIAL_ENVELOPE_WITHIN_FIRST_SEGMENT"
            embedded_fraction = float(boundary["u"])
            embedded_length = embedded_fraction * first_segment_length
            boundary_payload = {
                "u": float(boundary["u"]),
                "point_m": boundary["point_m"],
                "branch_radius_m": float(boundary["branch_radius_m"]),
                "nearest_trunk_segment": boundary["segment"],
                "nearest_trunk_segment_t": float(boundary["segment_t"]),
                "nearest_trunk_centerline_point_m": boundary["closest_centerline_point_m"],
                "centerline_distance_m": float(boundary["centerline_distance_m"]),
                "local_trunk_radius_m": float(boundary["local_trunk_radius_m"]),
                "boundary_residual_m": float(boundary["neutral_support_margin_m"]),
            }

        reports.append(
            {
                "branch_id": branch.get("id"),
                "root_point_m": root,
                "root_radius_m": float(radii[0]),
                "first_segment_end_m": [float(value) for value in points[1]],
                "first_segment_end_radius_m": float(radii[1]),
                "first_segment_length_m": first_segment_length,
                "exact_root_flex_zone_id": zone.get("id"),
                "exact_root_flex_zone_status": zone.get("status"),
                "root_nearest_trunk_segment": root_sample["segment"],
                "root_nearest_trunk_segment_t": float(root_sample["segment_t"]),
                "root_centerline_distance_m": float(root_sample["centerline_distance_m"]),
                "root_local_trunk_radius_m": float(root_sample["local_trunk_radius_m"]),
                "root_full_radius_support_margin_m": float(root_sample["neutral_support_margin_m"]),
                "first_segment_end_support_margin_m": float(end_sample["neutral_support_margin_m"]),
                "transition_state": transition_state,
                "embedded_fraction_of_first_segment": embedded_fraction,
                "embedded_length_along_first_segment_m": embedded_length,
                "first_full_radius_exit_boundary": boundary_payload,
            }
        )

    all_roots_supported = all(row["root_full_radius_support_margin_m"] >= -TOLERANCE for row in reports)
    all_exit_within_first = all(
        row["transition_state"] == "FULL_BRANCH_RADIUS_EXITS_TRUNK_RADIAL_ENVELOPE_WITHIN_FIRST_SEGMENT"
        for row in reports
    )
    if not all_roots_supported:
        state = "FAIL_NEUTRAL_BRANCH_ROOT_SUPPORT"
    elif all_exit_within_first:
        state = "PASS_EXACT_NEUTRAL_BRANCH_TRANSITION_ENVELOPES__CONNECTED_TOPOLOGY_HELD"
    else:
        state = "PASS_NEUTRAL_BRANCH_TRANSITION_ENVELOPES__MIXED_FIRST_SEGMENT_EXIT_STATE__CONNECTED_TOPOLOGY_HELD"

    embedded_lengths = [row["embedded_length_along_first_segment_m"] for row in reports]
    return {
        "schema": SCHEMA,
        "study_id": source.get("study_id"),
        "state": state,
        "branch_count": len(reports),
        "branches": reports,
        "minimum_embedded_length_along_first_segment_m": min(embedded_lengths),
        "maximum_embedded_length_along_first_segment_m": max(embedded_lengths),
        "checks": {
            "all_branch_roots_have_full_radius_neutral_support": all_roots_supported,
            "all_primary_branches_have_exact_unproven_root_flex_declaration": all(
                row["exact_root_flex_zone_status"] == FLEX_STATUS for row in reports
            ),
            "all_primary_branches_have_measured_first_segment_transition": all(
                row["first_full_radius_exit_boundary"] is not None for row in reports
            ),
        },
        "handoff": {
            "organic_claim": "AUTHORED_NEUTRAL_RADIAL_TRANSITION_GEOMETRY_ONLY",
            "connected_topology_state": "HELD_FOR_GEOMETRY",
            "junction_strategy_selected": False,
            "source_compensation_authorized": False,
        },
        "truth_boundary": {
            "authored_centerlines_and_radii_measured": True,
            "source_geometry_changed": False,
            "flex_zone_metadata_changed": False,
            "generated_mesh_connectivity_inspected": False,
            "connected_branch_trunk_topology_proven": False,
            "weld_boolean_or_remesh_strategy_selected": False,
            "deformation_simulated": False,
            "rigging_hierarchy_or_weights_inferred": False,
            "biological_attachment_claimed": False,
            "runtime_readiness_claimed": False,
        },
    }

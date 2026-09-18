"""Source-owned neutral attachment evidence for the east/rear Nature tree.

This module measures only authored neutral-form relationships that are useful before
any deformation work starts. It does not rig, bend, simulate wind, certify tissue or
botanical mechanics, or accept deformation quality.
"""
from __future__ import annotations

import math

SCHEMA = "axm.nature-rear-tree-deformation-readiness/v0.1"
FLEX_STATUS = "DECLARED_NOT_DEFORMATION_TESTED"
TOLERANCE = 1e-9


def _sub(a, b):
    return [float(a[i]) - float(b[i]) for i in range(3)]


def _dot(a, b):
    return sum(float(a[i]) * float(b[i]) for i in range(3))


def _length(v):
    return math.sqrt(_dot(v, v))


def _closest_on_segment(point, a, b):
    ab = _sub(b, a)
    denom = _dot(ab, ab)
    if denom <= 1e-18:
        raise ValueError("zero-length trunk segment")
    t = _dot(_sub(point, a), ab) / denom
    t = max(0.0, min(1.0, t))
    closest = [float(a[i]) + t * ab[i] for i in range(3)]
    distance = _length(_sub(point, closest))
    return t, closest, distance


def _vector_matches(a, b, tolerance=TOLERANCE):
    return (
        isinstance(a, list)
        and isinstance(b, list)
        and len(a) == len(b) == 3
        and all(abs(float(a[i]) - float(b[i])) <= tolerance for i in range(3))
    )


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
                "closest_centerline_point": closest,
                "centerline_distance_m": distance,
                "local_trunk_radius_m": radius,
            }
        )
    return min(candidates, key=lambda item: (item["centerline_distance_m"], item["segment_index"]))


def evaluate(source: dict) -> dict:
    trunk = source.get("trunk", [])
    branches = source.get("branches", [])
    flex_zones = source.get("flex_zones", [])
    if len(trunk) < 2:
        raise ValueError("deformation-readiness evidence requires at least two trunk points")
    if not branches:
        raise ValueError("deformation-readiness evidence requires authored branches")

    branch_reports = []
    all_neutral_support = True
    covered_branch_roots = 0

    for branch in branches:
        points = branch.get("points", [])
        radii = branch.get("radii", [])
        if not points or not radii:
            raise ValueError(f"branch {branch.get('id')} is missing root geometry")
        root = [float(value) for value in points[0]]
        root_radius = float(radii[0])
        if root_radius <= 0.0:
            raise ValueError(f"branch {branch.get('id')} root radius must be positive")

        support = _nearest_trunk_support(trunk, root)
        support_margin = support["local_trunk_radius_m"] - support["centerline_distance_m"] - root_radius
        center_inside = support["centerline_distance_m"] <= support["local_trunk_radius_m"] + TOLERANCE
        full_root_radius_supported = support_margin >= -TOLERANCE
        all_neutral_support = all_neutral_support and center_inside and full_root_radius_supported

        matching_zones = [
            zone
            for zone in flex_zones
            if _vector_matches(zone.get("center"), root)
        ]
        if len(matching_zones) > 1:
            raise ValueError(f"branch {branch.get('id')} has multiple flex zones at its exact root")
        flex_zone = matching_zones[0] if matching_zones else None
        if flex_zone is not None:
            covered_branch_roots += 1

        branch_reports.append(
            {
                "branch_id": branch.get("id"),
                "root_point_m": root,
                "root_radius_m": root_radius,
                "nearest_trunk_segment": support["segment"],
                "nearest_trunk_segment_t": support["segment_t"],
                "nearest_trunk_centerline_point_m": support["closest_centerline_point"],
                "centerline_distance_m": support["centerline_distance_m"],
                "local_trunk_radius_m": support["local_trunk_radius_m"],
                "neutral_support_margin_after_branch_radius_m": support_margin,
                "root_center_inside_local_trunk_radius": center_inside,
                "full_branch_root_radius_supported_in_neutral_form": full_root_radius_supported,
                "exact_root_flex_zone_id": flex_zone.get("id") if flex_zone else None,
                "exact_root_flex_zone_radius_m": float(flex_zone["radius"]) if flex_zone else None,
                "exact_root_flex_zone_status": flex_zone.get("status") if flex_zone else None,
            }
        )

    flex_statuses_safe = all(zone.get("status") == FLEX_STATUS for zone in flex_zones)
    branch_count = len(branch_reports)
    full_flex_coverage = covered_branch_roots == branch_count
    minimum_support_margin = min(
        report["neutral_support_margin_after_branch_radius_m"] for report in branch_reports
    )

    checks = {
        "all_branch_roots_have_neutral_trunk_support": all_neutral_support,
        "all_declared_flex_zones_remain_unproven": flex_statuses_safe,
        "all_primary_branch_roots_have_exact_declared_flex_zone": full_flex_coverage,
    }

    if not all_neutral_support or not flex_statuses_safe:
        state = "FAIL"
    elif not full_flex_coverage:
        state = "HOLD_BRANCH_ROOT_FLEX_ZONE_COVERAGE"
    else:
        state = "PASS_NEUTRAL_BRANCH_ROOT_SUPPORT__DEFORMATION_UNTESTED"

    missing = [
        report["branch_id"]
        for report in branch_reports
        if report["exact_root_flex_zone_id"] is None
    ]

    return {
        "schema": SCHEMA,
        "study_id": source.get("study_id"),
        "state": state,
        "branch_roots": branch_reports,
        "branch_count": branch_count,
        "branch_roots_with_exact_flex_zone": covered_branch_roots,
        "branch_roots_missing_exact_flex_zone": missing,
        "minimum_neutral_support_margin_after_branch_radius_m": minimum_support_margin,
        "checks": checks,
        "truth_boundary": {
            "neutral_form_relationships_measured": True,
            "source_geometry_changed": False,
            "flex_zone_metadata_changed": False,
            "deformation_simulated": False,
            "rigging_tested": False,
            "wind_physics_tested": False,
            "botanical_correctness_claimed": False,
            "runtime_tested": False,
            "art_direction_accepted": False,
        },
    }

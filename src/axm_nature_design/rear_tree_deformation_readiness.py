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


def _evaluate_declared_trunk_flex_zones(trunk: list[dict], flex_zones: list[dict]) -> dict:
    """Bind declared trunk flex metadata to exact authored neutral trunk points only.

    This is intentionally not a bend/deformation test. It asks only whether each
    source-declared ``trunk-*`` flex envelope is anchored to one exact authored trunk
    control point and encloses that point's authored neutral cross-section radius.
    """

    trunk_zones = [
        zone for zone in flex_zones if str(zone.get("id", "")).startswith("trunk-")
    ]
    reports = []
    all_exact = True
    all_cover = True

    for zone in trunk_zones:
        center = zone.get("center")
        matches = [point for point in trunk if _vector_matches(point.get("position"), center)]
        if len(matches) > 1:
            raise ValueError(f"trunk flex zone {zone.get('id')} matches multiple exact trunk points")

        zone_radius = float(zone.get("radius", 0.0))
        if zone_radius <= 0.0:
            raise ValueError(f"trunk flex zone {zone.get('id')} radius must be positive")

        point = matches[0] if matches else None
        exact_anchor = point is not None
        all_exact = all_exact and exact_anchor

        trunk_radius = float(point["radius"]) if point is not None else None
        margin = zone_radius - trunk_radius if trunk_radius is not None else None
        covers_cross_section = margin is not None and margin >= -TOLERANCE
        all_cover = all_cover and covers_cross_section

        reports.append(
            {
                "flex_zone_id": zone.get("id"),
                "center_m": [float(value) for value in center] if isinstance(center, list) else center,
                "flex_zone_radius_m": zone_radius,
                "flex_zone_status": zone.get("status"),
                "trunk_point_id": point.get("id") if point is not None else None,
                "trunk_point_radius_m": trunk_radius,
                "neutral_cross_section_envelope_margin_m": margin,
                "exact_trunk_point_anchor": exact_anchor,
                "covers_authored_trunk_cross_section": covers_cross_section,
            }
        )

    margins = [
        row["neutral_cross_section_envelope_margin_m"]
        for row in reports
        if row["neutral_cross_section_envelope_margin_m"] is not None
    ]

    if not trunk_zones:
        state = "HOLD_TRUNK_FLEX_ZONE_COVERAGE"
    elif not all_exact or not all_cover:
        state = "FAIL_TRUNK_FLEX_ENVELOPE_BINDING"
    else:
        state = "PASS_DECLARED_TRUNK_FLEX_ENVELOPES_BOUND__DEFORMATION_UNTESTED"

    return {
        "state": state,
        "count": len(trunk_zones),
        "zones": reports,
        "minimum_neutral_cross_section_envelope_margin_m": min(margins) if margins else None,
        "checks": {
            "declared_trunk_flex_zones_present": bool(trunk_zones),
            "all_declared_trunk_flex_zones_match_exact_trunk_point": bool(trunk_zones) and all_exact,
            "all_declared_trunk_flex_zones_cover_authored_trunk_cross_section": bool(trunk_zones) and all_cover,
        },
    }


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

    trunk_flex = _evaluate_declared_trunk_flex_zones(trunk, flex_zones)
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
        **trunk_flex["checks"],
    }

    if (
        not all_neutral_support
        or not flex_statuses_safe
        or trunk_flex["state"] == "FAIL_TRUNK_FLEX_ENVELOPE_BINDING"
    ):
        state = "FAIL"
    elif trunk_flex["state"] == "HOLD_TRUNK_FLEX_ZONE_COVERAGE":
        state = "HOLD_TRUNK_FLEX_ZONE_COVERAGE"
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
        "trunk_flex_state": trunk_flex["state"],
        "trunk_flex_zone_count": trunk_flex["count"],
        "trunk_flex_zones": trunk_flex["zones"],
        "minimum_trunk_flex_envelope_margin_m": trunk_flex[
            "minimum_neutral_cross_section_envelope_margin_m"
        ],
        "checks": checks,
        "truth_boundary": {
            "neutral_form_relationships_measured": True,
            "trunk_flex_envelopes_measured": True,
            "source_geometry_changed": False,
            "flex_zone_metadata_changed": False,
            "deformation_simulated": False,
            "rigging_tested": False,
            "trunk_deformation_tested": False,
            "wind_physics_tested": False,
            "botanical_correctness_claimed": False,
            "runtime_tested": False,
            "art_direction_accepted": False,
        },
    }

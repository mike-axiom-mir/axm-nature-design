"""Exact source-owned interaction classes for east/rear tree flex declarations.

This observer is intentionally narrower than rigging. It classifies authored neutral-space
relationships between trunk flex envelopes and exact branch-root flex envelopes, binds
each branch root to its authored neutral trunk support, and records whether each trunk
flex envelope actually reaches the neutral trunk cross-section at that attachment locus.
It does not choose hierarchy, weights, constraints, motion range, or any physical or
biological interpretation.
"""
from __future__ import annotations

from axm_nature_design.rear_tree_deformation_readiness import (
    FLEX_STATUS,
    TOLERANCE,
    _length,
    _nearest_trunk_support,
    _sub,
    _vector_matches,
)

SCHEMA = "axm.nature-trunk-branch-flex-interaction-classification/v0.2"

ROOT_CENTER_CONTAINED = "ROOT_CENTER_CONTAINED_IN_TRUNK_FLEX"
FLEX_ENVELOPE_OVERLAP_ONLY = "FLEX_ENVELOPE_OVERLAP_ONLY"
DISJOINT = "DISJOINT"


def _classify(center_margin_m: float, envelope_margin_m: float) -> str:
    if center_margin_m >= -TOLERANCE:
        return ROOT_CENTER_CONTAINED
    if envelope_margin_m >= -TOLERANCE:
        return FLEX_ENVELOPE_OVERLAP_ONLY
    return DISJOINT


def evaluate(source: dict) -> dict:
    trunk = source.get("trunk", [])
    branches = source.get("branches", [])
    flex_zones = source.get("flex_zones", [])

    if len(trunk) < 2:
        raise ValueError("interaction classification requires at least two trunk points")
    if not branches:
        raise ValueError("interaction classification requires authored branches")

    trunk_zones = [
        zone for zone in flex_zones if str(zone.get("id", "")).startswith("trunk-")
    ]
    if not trunk_zones:
        raise ValueError("interaction classification requires declared trunk flex zones")

    if any(zone.get("status") != FLEX_STATUS for zone in flex_zones):
        raise ValueError("interaction classification requires all flex declarations to remain unproven")

    rows = []
    for branch in branches:
        points = branch.get("points", [])
        radii = branch.get("radii", [])
        if not points or not radii:
            raise ValueError(f"branch {branch.get('id')} is missing root geometry")

        root = [float(value) for value in points[0]]
        root_radius = float(radii[0])
        if root_radius <= 0.0:
            raise ValueError(f"branch {branch.get('id')} root radius must be positive")

        matching_zones = [
            zone for zone in flex_zones if _vector_matches(zone.get("center"), root)
        ]
        if len(matching_zones) != 1:
            raise ValueError(
                f"branch {branch.get('id')} requires exactly one flex declaration at its exact root"
            )
        branch_zone = matching_zones[0]
        branch_flex_radius = float(branch_zone.get("radius", 0.0))
        if branch_flex_radius <= 0.0:
            raise ValueError(f"branch flex zone {branch_zone.get('id')} radius must be positive")

        support = _nearest_trunk_support(trunk, root)
        support_margin = (
            support["local_trunk_radius_m"]
            - support["centerline_distance_m"]
            - root_radius
        )
        full_neutral_support = support_margin >= -TOLERANCE

        for trunk_zone in trunk_zones:
            trunk_flex_radius = float(trunk_zone.get("radius", 0.0))
            if trunk_flex_radius <= 0.0:
                raise ValueError(f"trunk flex zone {trunk_zone.get('id')} radius must be positive")

            center_distance = _length(_sub(root, trunk_zone.get("center")))
            center_margin = trunk_flex_radius - center_distance
            envelope_margin = trunk_flex_radius + branch_flex_radius - center_distance
            interaction_class = _classify(center_margin, envelope_margin)

            attachment_centerline_distance = _length(
                _sub(support["closest_centerline_point"], trunk_zone.get("center"))
            )
            attachment_cross_section_boundary_signed = (
                attachment_centerline_distance
                - trunk_flex_radius
                - support["local_trunk_radius_m"]
            )
            attachment_cross_section_intersects = (
                attachment_cross_section_boundary_signed <= TOLERANCE
            )

            rows.append(
                {
                    "trunk_flex_zone_id": trunk_zone.get("id"),
                    "branch_id": branch.get("id"),
                    "branch_flex_zone_id": branch_zone.get("id"),
                    "interaction_class": interaction_class,
                    "trunk_flex_to_branch_root_center_distance_m": center_distance,
                    "branch_root_to_trunk_flex_boundary_signed_m": (
                        center_distance - trunk_flex_radius
                    ),
                    "declared_flex_envelope_boundary_signed_m": (
                        center_distance - trunk_flex_radius - branch_flex_radius
                    ),
                    "trunk_flex_zone_radius_m": trunk_flex_radius,
                    "branch_flex_zone_radius_m": branch_flex_radius,
                    "branch_root_radius_m": root_radius,
                    "nearest_neutral_trunk_segment": support["segment"],
                    "nearest_neutral_trunk_segment_t": support["segment_t"],
                    "nearest_neutral_trunk_centerline_point_m": support[
                        "closest_centerline_point_m"
                    ] if "closest_centerline_point_m" in support else support["closest_centerline_point"],
                    "neutral_root_centerline_distance_m": support["centerline_distance_m"],
                    "neutral_local_trunk_radius_m": support["local_trunk_radius_m"],
                    "neutral_support_margin_after_branch_radius_m": support_margin,
                    "full_branch_root_radius_supported_in_neutral_form": full_neutral_support,
                    "trunk_flex_to_neutral_attachment_centerline_distance_m": (
                        attachment_centerline_distance
                    ),
                    "neutral_attachment_cross_section_to_trunk_flex_boundary_signed_m": (
                        attachment_cross_section_boundary_signed
                    ),
                    "trunk_flex_intersects_neutral_attachment_cross_section": (
                        attachment_cross_section_intersects
                    ),
                }
            )

    class_counts = {
        ROOT_CENTER_CONTAINED: sum(
            row["interaction_class"] == ROOT_CENTER_CONTAINED for row in rows
        ),
        FLEX_ENVELOPE_OVERLAP_ONLY: sum(
            row["interaction_class"] == FLEX_ENVELOPE_OVERLAP_ONLY for row in rows
        ),
        DISJOINT: sum(row["interaction_class"] == DISJOINT for row in rows),
    }
    overlap_only_pairs = [
        {
            "trunk_flex_zone_id": row["trunk_flex_zone_id"],
            "branch_id": row["branch_id"],
            "branch_flex_zone_id": row["branch_flex_zone_id"],
        }
        for row in rows
        if row["interaction_class"] == FLEX_ENVELOPE_OVERLAP_ONLY
    ]
    contained_pairs = [
        {
            "trunk_flex_zone_id": row["trunk_flex_zone_id"],
            "branch_id": row["branch_id"],
            "branch_flex_zone_id": row["branch_flex_zone_id"],
        }
        for row in rows
        if row["interaction_class"] == ROOT_CENTER_CONTAINED
    ]
    attachment_cross_section_intersection_pairs = [
        {
            "trunk_flex_zone_id": row["trunk_flex_zone_id"],
            "branch_id": row["branch_id"],
            "branch_flex_zone_id": row["branch_flex_zone_id"],
        }
        for row in rows
        if row["trunk_flex_intersects_neutral_attachment_cross_section"]
    ]

    if not all(row["full_branch_root_radius_supported_in_neutral_form"] for row in rows):
        state = "FAIL_NEUTRAL_BRANCH_ROOT_SUPPORT"
    else:
        state = "PASS_EXACT_TRUNK_BRANCH_FLEX_INTERACTION_CLASSES__DEFORMATION_UNTESTED"

    return {
        "schema": SCHEMA,
        "study_id": source.get("study_id"),
        "state": state,
        "pair_count": len(rows),
        "interaction_class_counts": class_counts,
        "root_center_contained_pairs": contained_pairs,
        "flex_envelope_overlap_only_pairs": overlap_only_pairs,
        "neutral_attachment_cross_section_intersection_pair_count": len(
            attachment_cross_section_intersection_pairs
        ),
        "neutral_attachment_cross_section_intersection_pairs": (
            attachment_cross_section_intersection_pairs
        ),
        "pairs": rows,
        "truth_boundary": {
            "source_metadata_spatial_relations_measured": True,
            "neutral_attachment_support_measured": True,
            "neutral_attachment_cross_section_relation_to_trunk_flex_measured": True,
            "interaction_classes_are_source_geometry_only": True,
            "source_geometry_changed": False,
            "flex_zone_metadata_changed": False,
            "interaction_class_assigns_rig_policy": False,
            "attachment_cross_section_intersection_assigns_rig_policy": False,
            "neutral_attachment_support_is_deformation_proof": False,
            "neutral_attachment_cross_section_intersection_is_deformation_proof": False,
            "deformation_simulated": False,
            "hierarchy_or_weighting_inferred": False,
            "biological_interpretation_claimed": False,
            "runtime_readiness_claimed": False,
        },
    }

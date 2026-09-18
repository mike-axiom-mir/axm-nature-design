"""Rigging-owned exclusion gate for north-low parent influence on the east/rear tree.

Organic source evidence distinguishes declared flex-envelope overlap from actual neutral
trunk cross-section reach.  For the exact current source, ``north-low`` overlaps the
``trunk-upper-flex`` declaration, but its neutral attachment cross-section remains
outside that trunk flex sphere.  This module turns that fresh source fact into one
bounded Rigging safety constraint: the existing north-low child socket must not silently
inherit the upper-trunk parent frame in this diagnostic receiver while that exact
cross-section relation remains disjoint.

The gate is verification-only.  It is not a production skin weight, botanical model,
source-authored ROM, Animation, wind, Runtime, collision, or aesthetic acceptance.
"""
from __future__ import annotations

from . import rear_tree_rigging as historical
from . import rear_tree_rigging_primary_branch_family as family
from .organic_form import build_mesh, digest, validate_source
from .rear_tree_deformation_readiness import _nearest_trunk_support

SCHEMA = "axm.nature-north-low-upper-trunk-parent-influence-gate-rigging-evidence/v0.1"
RESULT = "PASS_NORTH_LOW_UPPER_TRUNK_PARENT_INFLUENCE_EXCLUSION_GATE_DIAGNOSTIC"
STUDY_ID = family.STUDY_ID
SOURCE_OWNER_HEAD = family.SOURCE_OWNER_HEAD
EXPECTED_SOURCE_DIGEST = family.EXPECTED_SOURCE_DIGEST
EXPECTED_MIGRATED_MESH_DIGEST = family.EXPECTED_MIGRATED_MESH_DIGEST
RIGGING_PREDECESSOR_HEAD = "6cf64925f0ea00737e4d3f2d4f15979c773f309d"
ORGANIC_INTERACTION_DONOR_HEAD = "925715d2f0491e2bcbc493b93dc6d14ab3dcb2a6"
ORGANIC_SOURCE_BLOB = "fb12b759e1abfd0455bf46fd39a0eba27095796b"
ORGANIC_INTERACTION_MODULE_BLOB = "be31e22283d43dcb4e6e8bda870760fa67ab1628"

TRUNK_POINT_ID = "upper"
TRUNK_FLEX_ID = "trunk-upper-flex"
TRUNK_FLEX_RADIUS_M = 0.22
CHILD_BRANCH_ID = "north-low"
CHILD_FLEX_ID = "north-low-branch-flex"
CHILD_FLEX_RADIUS_M = 0.14
PARENT_DIAGNOSTIC_MIN_DEG = -2.5
PARENT_DIAGNOSTIC_MAX_DEG = 2.5
PARENT_REPRESENTATIVE_ANGLES_DEG = (-2.5, 0.0, 2.5)
CHILD_REPRESENTATIVE_ANGLES_DEG = (-5.0, 0.0, 5.0)
TOL = historical.TOL

EXPECTED_DECLARED_ENVELOPE_OVERLAP_M = 0.028488310914984383
EXPECTED_ATTACHMENT_CROSS_SECTION_GAP_M = 0.009079537802862594
EXPECTED_NEUTRAL_SUPPORT_MARGIN_M = 0.040773804595473605
EXPECTED_ATTACHMENT_CENTERLINE_DISTANCE_M = 0.33144612713000876


def _single(rows, label: str) -> dict:
    values = list(rows)
    if len(values) != 1:
        raise ValueError(f"{label} must resolve exactly once")
    return values[0]


def _close_scalar(a, b, tolerance=1e-12):
    return abs(float(a) - float(b)) <= tolerance


def _rotate_vector(vector, axis, angle_deg):
    return historical._rotate_about_axis(vector, [0.0, 0.0, 0.0], axis, angle_deg)


def evaluate(
    source: dict,
    *,
    requested_rigging_predecessor_head: str = RIGGING_PREDECESSOR_HEAD,
    requested_organic_interaction_head: str = ORGANIC_INTERACTION_DONOR_HEAD,
    parent_diagnostic_min_deg: float = PARENT_DIAGNOSTIC_MIN_DEG,
    parent_diagnostic_max_deg: float = PARENT_DIAGNOSTIC_MAX_DEG,
    force_parent_influence: bool = False,
    claim_source_rom: bool = False,
    claim_production_weighting: bool = False,
    claim_surface_attachment: bool = False,
    claim_animation_acceptance: bool = False,
    claim_runtime_acceptance: bool = False,
) -> dict:
    """Apply a fail-closed, source-relation gate to the existing north-low child socket."""
    validate_source(source)
    if source.get("study_id") != STUDY_ID:
        raise ValueError("unexpected Nature study identity")
    source_digest = digest(source)
    if source_digest != EXPECTED_SOURCE_DIGEST:
        raise ValueError("exact Organic source identity drift")
    if requested_rigging_predecessor_head != RIGGING_PREDECESSOR_HEAD:
        raise ValueError("exact Rigging predecessor head drift")
    if requested_organic_interaction_head != ORGANIC_INTERACTION_DONOR_HEAD:
        raise ValueError("exact Organic interaction donor head drift")
    if (
        abs(float(parent_diagnostic_min_deg) - PARENT_DIAGNOSTIC_MIN_DEG) > TOL
        or abs(float(parent_diagnostic_max_deg) - PARENT_DIAGNOSTIC_MAX_DEG) > TOL
    ):
        raise ValueError("parent diagnostic interval may not be widened or retimed")
    if force_parent_influence:
        raise ValueError("north-low parent influence is held while the exact attachment cross-section is disjoint")
    if claim_source_rom:
        raise ValueError("Rigging diagnostic intervals must not be promoted to source/biological ROM")
    if claim_production_weighting:
        raise ValueError("this exclusion gate is not production skin weighting")
    if claim_surface_attachment:
        raise ValueError("this lane does not prove branch/trunk surface attachment")
    if claim_animation_acceptance:
        raise ValueError("Rigging evidence cannot claim Animation acceptance")
    if claim_runtime_acceptance:
        raise ValueError("Rigging evidence cannot claim Runtime acceptance")

    trunk = source["trunk"]
    upper_index = next((i for i, row in enumerate(trunk) if row.get("id") == TRUNK_POINT_ID), None)
    if upper_index is None or upper_index <= 0 or upper_index >= len(trunk) - 1:
        raise ValueError("upper trunk point must have exact incoming and outgoing source segments")
    previous = trunk[upper_index - 1]
    upper = trunk[upper_index]
    following = trunk[upper_index + 1]
    parent_pivot = [float(value) for value in upper["position"]]

    parent_flex = _single(
        (row for row in source["flex_zones"] if row.get("id") == TRUNK_FLEX_ID),
        TRUNK_FLEX_ID,
    )
    if parent_flex.get("status") != "DECLARED_NOT_DEFORMATION_TESTED":
        raise ValueError("upper-trunk source flex status drift")
    if not historical._close_vec(parent_flex["center"], parent_pivot):
        raise ValueError("upper-trunk flex center is not the exact authored trunk point")
    if not _close_scalar(parent_flex["radius"], TRUNK_FLEX_RADIUS_M):
        raise ValueError("upper-trunk source flex radius drift")

    incoming = historical._norm(historical._sub(parent_pivot, previous["position"]))
    outgoing = historical._norm(historical._sub(following["position"], parent_pivot))
    parent_axis_raw = historical._cross(incoming, outgoing)
    if historical._length(parent_axis_raw) <= 1e-9:
        raise ValueError("source-derived upper-trunk bend-plane axis is degenerate")
    parent_axis = historical._norm(parent_axis_raw)

    family_result = family.evaluate(source)
    if family_result["result"] != family.RESULT:
        raise ValueError("exact five-branch Rigging predecessor no longer passes")
    child_probe = _single(
        (row for row in family_result["rigging_family"]["probes"] if row["branch_id"] == CHILD_BRANCH_ID),
        CHILD_BRANCH_ID,
    )
    child_pivot = [float(value) for value in child_probe["joint_pivot_m"]]
    child_axis = [float(value) for value in child_probe["source_derived_axis"]]

    child_flex = _single(
        (row for row in source["flex_zones"] if row.get("id") == CHILD_FLEX_ID),
        CHILD_FLEX_ID,
    )
    if child_flex.get("status") != "DECLARED_NOT_DEFORMATION_TESTED":
        raise ValueError("north-low source flex status drift")
    if not historical._close_vec(child_flex["center"], child_pivot):
        raise ValueError("north-low flex center is not the existing exact Rigging child pivot")
    if not _close_scalar(child_flex["radius"], CHILD_FLEX_RADIUS_M):
        raise ValueError("north-low source flex radius drift")

    support = _nearest_trunk_support(trunk, child_pivot)
    attachment_centerline_distance = historical._distance(
        support["closest_centerline_point"], parent_pivot
    )
    attachment_gap = (
        attachment_centerline_distance
        - TRUNK_FLEX_RADIUS_M
        - float(support["local_trunk_radius_m"])
    )
    neutral_support_margin = (
        float(support["local_trunk_radius_m"])
        - float(support["centerline_distance_m"])
        - float(source["branches"][1]["radii"][0])
    )
    root_center_distance = historical._distance(child_pivot, parent_pivot)
    declared_overlap = TRUNK_FLEX_RADIUS_M + CHILD_FLEX_RADIUS_M - root_center_distance

    if support["segment"] != "mid->upper":
        raise ValueError("north-low neutral attachment segment drift")
    if not _close_scalar(attachment_centerline_distance, EXPECTED_ATTACHMENT_CENTERLINE_DISTANCE_M):
        raise ValueError("Organic north-low attachment centerline distance drift")
    if not _close_scalar(attachment_gap, EXPECTED_ATTACHMENT_CROSS_SECTION_GAP_M):
        raise ValueError("Organic north-low attachment cross-section gap drift")
    if not _close_scalar(neutral_support_margin, EXPECTED_NEUTRAL_SUPPORT_MARGIN_M):
        raise ValueError("Organic north-low neutral support margin drift")
    if not _close_scalar(declared_overlap, EXPECTED_DECLARED_ENVELOPE_OVERLAP_M):
        raise ValueError("Organic north-low declared envelope overlap drift")
    if declared_overlap <= 0.0:
        raise ValueError("north-low declared flex envelopes no longer overlap")

    parent_influence_enabled = attachment_gap <= TOL
    if parent_influence_enabled:
        raise ValueError("north-low attachment cross-section now reaches parent flex; exclusion gate must be re-reviewed")

    mesh = build_mesh(source)
    mesh_digest = digest(mesh)
    if mesh_digest != EXPECTED_MIGRATED_MESH_DIGEST:
        raise ValueError("exact Geometry migrated receiver identity drift")
    neutral_vertices = [[float(value) for value in vertex] for vertex in mesh["vertices"]]
    selected_indices = list(child_probe["selected_vertex_indices"])
    neutral_selected = [neutral_vertices[index] for index in selected_indices]
    neutral_pairwise = historical._pairwise_distances(neutral_selected)

    witnesses = []
    max_pairwise_drift = 0.0
    max_parent_command_leak = 0.0
    max_counterfactual_parent_socket_travel = 0.0
    max_counterfactual_output_delta = 0.0
    outputs_by_child_angle = {}

    for parent_angle in PARENT_REPRESENTATIVE_ANGLES_DEG:
        counterfactual_pivot = historical._rotate_about_axis(
            child_pivot, parent_pivot, parent_axis, parent_angle
        )
        counterfactual_axis = historical._norm(_rotate_vector(child_axis, parent_axis, parent_angle))
        counterfactual_socket_travel = historical._distance(counterfactual_pivot, child_pivot)
        max_counterfactual_parent_socket_travel = max(
            max_counterfactual_parent_socket_travel, counterfactual_socket_travel
        )

        for child_angle in CHILD_REPRESENTATIVE_ANGLES_DEG:
            gated = [
                historical._rotate_about_axis(
                    neutral_vertices[index], child_pivot, child_axis, child_angle
                )
                for index in selected_indices
            ]
            counterfactual = []
            for index in selected_indices:
                parented = historical._rotate_about_axis(
                    neutral_vertices[index], parent_pivot, parent_axis, parent_angle
                )
                counterfactual.append(
                    historical._rotate_about_axis(
                        parented, counterfactual_pivot, counterfactual_axis, child_angle
                    )
                )

            pairwise_drift = historical._max_abs_delta(
                historical._pairwise_distances(gated), neutral_pairwise
            )
            max_pairwise_drift = max(max_pairwise_drift, pairwise_drift)

            baseline = outputs_by_child_angle.setdefault(child_angle, gated)
            parent_leak = max(
                (historical._distance(gated[i], baseline[i]) for i in range(len(gated))),
                default=0.0,
            )
            max_parent_command_leak = max(max_parent_command_leak, parent_leak)

            counterfactual_delta = max(
                (
                    historical._distance(gated[i], counterfactual[i])
                    for i in range(len(gated))
                ),
                default=0.0,
            )
            if abs(parent_angle) > TOL:
                max_counterfactual_output_delta = max(
                    max_counterfactual_output_delta, counterfactual_delta
                )

            witnesses.append(
                {
                    "parent_angle_deg": float(parent_angle),
                    "child_angle_deg": float(child_angle),
                    "parent_influence_enabled": False,
                    "gated_child_pivot_m": child_pivot,
                    "gated_child_axis": child_axis,
                    "counterfactual_inherited_child_pivot_m": counterfactual_pivot,
                    "counterfactual_parent_socket_travel_m": counterfactual_socket_travel,
                    "gated_rigid_child_pairwise_distance_drift_m": pairwise_drift,
                    "gated_parent_command_leak_m": parent_leak,
                    "counterfactual_inherited_output_delta_m": counterfactual_delta,
                }
            )

    if max_counterfactual_parent_socket_travel <= 1e-6:
        raise ValueError("counterfactual inherited-parent socket travel is not discriminating")
    if max_counterfactual_output_delta <= 1e-6:
        raise ValueError("counterfactual inherited-parent output is not discriminating")

    checks = {
        "exact_source_identity": source_digest == EXPECTED_SOURCE_DIGEST,
        "exact_geometry_receiver_identity": mesh_digest == EXPECTED_MIGRATED_MESH_DIGEST,
        "exact_five_branch_rigging_predecessor_reexecuted": family_result["result"] == family.RESULT,
        "declared_flex_envelopes_overlap": declared_overlap > 0.0,
        "neutral_attachment_cross_section_is_outside_parent_flex": attachment_gap > TOL,
        "parent_influence_is_fail_closed": parent_influence_enabled is False,
        "north_low_existing_child_socket_preserved": historical._close_vec(child_flex["center"], child_pivot),
        "gated_child_rigidity_preserved": max_pairwise_drift <= TOL,
        "parent_command_does_not_leak_through_exclusion_gate": max_parent_command_leak <= TOL,
        "counterfactual_parent_inheritance_is_materially_different": max_counterfactual_output_delta > 1e-6,
    }
    if not all(checks.values()):
        raise ValueError("north-low parent-influence gate invariant failed")

    return {
        "schema": SCHEMA,
        "result": RESULT,
        "study_id": STUDY_ID,
        "source_owner_head": SOURCE_OWNER_HEAD,
        "source_digest": source_digest,
        "geometry_receiver_head": family.GEOMETRY_RECEIVER_HEAD,
        "geometry_receiver_mesh_digest": mesh_digest,
        "rigging_predecessor_head": RIGGING_PREDECESSOR_HEAD,
        "organic_interaction_donor_head": ORGANIC_INTERACTION_DONOR_HEAD,
        "parent_frame": {
            "trunk_point_id": TRUNK_POINT_ID,
            "flex_zone_id": TRUNK_FLEX_ID,
            "pivot_m": parent_pivot,
            "source_derived_axis": parent_axis,
            "diagnostic_interval_deg": [PARENT_DIAGNOSTIC_MIN_DEG, PARENT_DIAGNOSTIC_MAX_DEG],
            "representative_angles_deg": list(PARENT_REPRESENTATIVE_ANGLES_DEG),
        },
        "child_socket": {
            "branch_id": CHILD_BRANCH_ID,
            "flex_zone_id": CHILD_FLEX_ID,
            "pivot_m": child_pivot,
            "source_derived_axis": child_axis,
            "selected_vertices": child_probe["selected_vertices"],
            "selected_triangles": child_probe["selected_triangles"],
            "diagnostic_interval_deg": child_probe["diagnostic_interval_deg"],
            "representative_angles_deg": list(CHILD_REPRESENTATIVE_ANGLES_DEG),
        },
        "organic_interaction_consumed": {
            "interaction_class": "FLEX_ENVELOPE_OVERLAP_ONLY",
            "declared_flex_envelope_overlap_margin_m": declared_overlap,
            "nearest_neutral_trunk_segment": support["segment"],
            "nearest_neutral_trunk_segment_t": support["segment_t"],
            "neutral_root_centerline_distance_m": support["centerline_distance_m"],
            "neutral_local_trunk_radius_m": support["local_trunk_radius_m"],
            "neutral_support_margin_after_branch_radius_m": neutral_support_margin,
            "trunk_flex_to_neutral_attachment_centerline_distance_m": attachment_centerline_distance,
            "neutral_attachment_cross_section_to_trunk_flex_boundary_signed_m": attachment_gap,
            "trunk_flex_intersects_neutral_attachment_cross_section": False,
        },
        "rigging_constraint": {
            "mode": "INTERSECTION_GATED_DIAGNOSTIC_ONLY",
            "upper_trunk_parent_influence_enabled_for_north_low": False,
            "diagnostic_parent_weight": 0.0,
            "reason": "neutral attachment cross-section lies outside exact upper-trunk flex sphere",
            "reopen_condition": "source/receiver evidence changes the exact attachment relation or a separate weighting owner supplies grounded influence evidence",
        },
        "measurements": {
            "representative_parent_child_pose_count": len(witnesses),
            "maximum_gated_rigid_child_pairwise_distance_drift_m": max_pairwise_drift,
            "maximum_gated_parent_command_leak_m": max_parent_command_leak,
            "maximum_counterfactual_inherited_parent_socket_travel_m": max_counterfactual_parent_socket_travel,
            "maximum_counterfactual_inherited_output_delta_m": max_counterfactual_output_delta,
        },
        "witnesses": witnesses,
        "continuous_product_domain_certificate": {
            "parent_domain_deg": [PARENT_DIAGNOSTIC_MIN_DEG, PARENT_DIAGNOSTIC_MAX_DEG],
            "child_domain_deg": [family.DIAGNOSTIC_MIN_DEG, family.DIAGNOSTIC_MAX_DEG],
            "continuous_for_every_real_parent_child_pair_under_gate": True,
            "reason": "the exclusion gate maps every parent command to identity on north-low while the existing child rotation remains a continuous rigid Rodrigues transform",
            "parent_influence_weight_is_production_skin_weight": False,
            "source_or_biological_rom_proven": False,
        },
        "checks": checks,
        "truth_boundary": {
            "source_geometry_changed": False,
            "geometry_receiver_changed": False,
            "existing_north_low_child_socket_changed": False,
            "parent_frame_authored_as_production_hierarchy": False,
            "production_skin_weighting_claimed": False,
            "surface_attachment_or_stress_claimed": False,
            "simultaneous_whole_tree_deformation_claimed": False,
            "collision_or_self_intersection_claimed": False,
            "animation_timing_interpolation_or_playback_claimed": False,
            "technical_art_target_host_claimed": False,
            "runtime_controller_or_device_claimed": False,
            "art_or_visual_qa_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }

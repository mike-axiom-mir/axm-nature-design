"""Rigging-owned parent/child socket rebase proof for the east/rear Nature tree.

This successor consumes the exact Organic source plus the existing five-primary-branch
Rigging family. It answers one narrow question exposed by Organic's neutral flex
interaction map: when the exact east-mid branch socket is inside the declared
upper-trunk flex envelope, can its child frame inherit a source-derived parent
trunk-frame rotation without double-applying or losing the child articulation?

The parent interval below is a Rigging verification probe only. It is not plant
biomechanics, source-authored ROM, Animation, wind, Runtime, collision or a
production skinning policy.
"""
from __future__ import annotations

import math

from . import rear_tree_rigging as historical
from . import rear_tree_rigging_primary_branch_family as family
from .organic_form import build_mesh, digest, validate_source

SCHEMA = "axm.nature-upper-trunk-east-mid-hierarchical-socket-rigging-evidence/v0.1"
RESULT = "PASS_UPPER_TRUNK_EAST_MID_PARENT_CHILD_SOCKET_REBASE_CONTINUOUS_PRODUCT_DOMAIN_DIAGNOSTIC"
STUDY_ID = family.STUDY_ID
SOURCE_OWNER_HEAD = family.SOURCE_OWNER_HEAD
EXPECTED_SOURCE_DIGEST = family.EXPECTED_SOURCE_DIGEST
EXPECTED_MIGRATED_MESH_DIGEST = family.EXPECTED_MIGRATED_MESH_DIGEST
RIGGING_PREDECESSOR_HEAD = "b4b480b415047fea90b4740f7702ced0dba9142d"
ORGANIC_READINESS_DONOR_HEAD = "f8d103a9f0a1e457539919a45c605c1edb8b9a7f"
ORGANIC_SOURCE_BLOB = "fb12b759e1abfd0455bf46fd39a0eba27095796b"
ORGANIC_READINESS_MODULE_BLOB = "0e787e5724c29878a86a425b43a39d5120bf1086"
ORGANIC_INTERACTION_DOC_BLOB = "d103856df817d1b3c3ea7938fe8ac4067d7de0c9"

TRUNK_POINT_ID = "upper"
TRUNK_FLEX_ID = "trunk-upper-flex"
TRUNK_FLEX_RADIUS_M = 0.22
CHILD_BRANCH_ID = "east-mid"
CHILD_FLEX_ID = "east-mid-branch-flex"
CHILD_FLEX_RADIUS_M = 0.12

PARENT_DIAGNOSTIC_MIN_DEG = -2.5
PARENT_DIAGNOSTIC_MAX_DEG = 2.5
PARENT_REPRESENTATIVE_ANGLES_DEG = (-2.5, 0.0, 2.5)
CHILD_REPRESENTATIVE_ANGLES_DEG = (-5.0, 0.0, 5.0)
TOL = historical.TOL

EXPECTED_CENTER_DISTANCE_M = 0.10630145812734658
EXPECTED_CONTAINMENT_MARGIN_M = 0.11369854187265342
EXPECTED_ENVELOPE_OVERLAP_MARGIN_M = 0.23369854187265338


def _single(rows, label: str) -> dict:
    values = list(rows)
    if len(values) != 1:
        raise ValueError(f"{label} must resolve exactly once")
    return values[0]


def _rotate_vector(vector, axis, angle_deg):
    return historical._rotate_about_axis(vector, [0.0, 0.0, 0.0], axis, angle_deg)


def _close_scalar(a, b, tolerance=TOL):
    return abs(float(a) - float(b)) <= tolerance


def evaluate(
    source: dict,
    *,
    requested_rigging_predecessor_head: str = RIGGING_PREDECESSOR_HEAD,
    requested_organic_readiness_head: str = ORGANIC_READINESS_DONOR_HEAD,
    parent_diagnostic_min_deg: float = PARENT_DIAGNOSTIC_MIN_DEG,
    parent_diagnostic_max_deg: float = PARENT_DIAGNOSTIC_MAX_DEG,
    claim_source_rom: bool = False,
    claim_trunk_mesh_deformation: bool = False,
    claim_surface_attachment: bool = False,
    claim_north_low_overlap_resolved: bool = False,
    claim_animation_acceptance: bool = False,
    claim_runtime_acceptance: bool = False,
) -> dict:
    """Prove one exact parent-frame -> child-socket rebase without authority promotion."""
    validate_source(source)
    if source.get("study_id") != STUDY_ID:
        raise ValueError("unexpected Nature study identity")
    source_digest = digest(source)
    if source_digest != EXPECTED_SOURCE_DIGEST:
        raise ValueError("exact Organic source identity drift")
    if requested_rigging_predecessor_head != RIGGING_PREDECESSOR_HEAD:
        raise ValueError("exact Rigging predecessor head drift")
    if requested_organic_readiness_head != ORGANIC_READINESS_DONOR_HEAD:
        raise ValueError("exact Organic readiness donor head drift")
    if (
        abs(float(parent_diagnostic_min_deg) - PARENT_DIAGNOSTIC_MIN_DEG) > TOL
        or abs(float(parent_diagnostic_max_deg) - PARENT_DIAGNOSTIC_MAX_DEG) > TOL
    ):
        raise ValueError("parent diagnostic interval may not be widened or retimed")
    if claim_source_rom:
        raise ValueError("Rigging diagnostic interval must not be promoted to source/biological ROM")
    if claim_trunk_mesh_deformation:
        raise ValueError("this lane does not prove trunk mesh deformation or skin weighting")
    if claim_surface_attachment:
        raise ValueError("this lane does not prove branch/trunk surface attachment")
    if claim_north_low_overlap_resolved:
        raise ValueError("north-low envelope overlap remains a separate unresolved Rigging question")
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
        raise ValueError("east-mid source flex status drift")
    if not historical._close_vec(child_flex["center"], child_pivot):
        raise ValueError("east-mid flex center is not the existing exact Rigging child pivot")
    if not _close_scalar(child_flex["radius"], CHILD_FLEX_RADIUS_M):
        raise ValueError("east-mid source flex radius drift")

    center_distance = historical._distance(child_pivot, parent_pivot)
    containment_margin = TRUNK_FLEX_RADIUS_M - center_distance
    envelope_overlap_margin = TRUNK_FLEX_RADIUS_M + CHILD_FLEX_RADIUS_M - center_distance
    if not _close_scalar(center_distance, EXPECTED_CENTER_DISTANCE_M, 1e-12):
        raise ValueError("Organic upper-trunk/east-mid center-distance relation drift")
    if not _close_scalar(containment_margin, EXPECTED_CONTAINMENT_MARGIN_M, 1e-12):
        raise ValueError("Organic east-mid containment margin drift")
    if not _close_scalar(envelope_overlap_margin, EXPECTED_ENVELOPE_OVERLAP_MARGIN_M, 1e-12):
        raise ValueError("Organic upper-trunk/east-mid flex-overlap margin drift")
    if containment_margin <= 0.0:
        raise ValueError("east-mid root is no longer contained by upper-trunk flex envelope")

    mesh = build_mesh(source)
    mesh_digest = digest(mesh)
    if mesh_digest != EXPECTED_MIGRATED_MESH_DIGEST:
        raise ValueError("exact Geometry migrated receiver identity drift")
    neutral_vertices = [[float(value) for value in vertex] for vertex in mesh["vertices"]]
    selected_indices = list(child_probe["selected_vertex_indices"])
    neutral_selected = [neutral_vertices[index] for index in selected_indices]
    neutral_pairwise = historical._pairwise_distances(neutral_selected)

    witnesses = []
    max_equivalence_delta = 0.0
    max_pairwise_drift = 0.0
    max_axis_projection_drift = 0.0
    max_center_distance_drift = 0.0
    max_containment_margin_drift = 0.0
    max_envelope_overlap_margin_drift = 0.0
    max_stale_frame_error = 0.0
    max_parent_socket_displacement = 0.0

    for parent_angle in PARENT_REPRESENTATIVE_ANGLES_DEG:
        transported_pivot = historical._rotate_about_axis(
            child_pivot, parent_pivot, parent_axis, parent_angle
        )
        transported_axis = historical._norm(_rotate_vector(child_axis, parent_axis, parent_angle))
        transported_center_distance = historical._distance(transported_pivot, parent_pivot)
        transported_containment_margin = TRUNK_FLEX_RADIUS_M - transported_center_distance
        transported_overlap_margin = (
            TRUNK_FLEX_RADIUS_M + CHILD_FLEX_RADIUS_M - transported_center_distance
        )
        parent_socket_displacement = historical._distance(transported_pivot, child_pivot)

        max_center_distance_drift = max(
            max_center_distance_drift, abs(transported_center_distance - center_distance)
        )
        max_containment_margin_drift = max(
            max_containment_margin_drift, abs(transported_containment_margin - containment_margin)
        )
        max_envelope_overlap_margin_drift = max(
            max_envelope_overlap_margin_drift,
            abs(transported_overlap_margin - envelope_overlap_margin),
        )
        max_parent_socket_displacement = max(max_parent_socket_displacement, parent_socket_displacement)

        for child_angle in CHILD_REPRESENTATIVE_ANGLES_DEG:
            correct = []
            equivalent = []
            stale = []
            for index in selected_indices:
                neutral = neutral_vertices[index]
                parented = historical._rotate_about_axis(
                    neutral, parent_pivot, parent_axis, parent_angle
                )
                correct.append(
                    historical._rotate_about_axis(
                        parented, transported_pivot, transported_axis, child_angle
                    )
                )
                child_local = historical._rotate_about_axis(
                    neutral, child_pivot, child_axis, child_angle
                )
                equivalent.append(
                    historical._rotate_about_axis(
                        child_local, parent_pivot, parent_axis, parent_angle
                    )
                )
                stale.append(
                    historical._rotate_about_axis(
                        parented, child_pivot, child_axis, child_angle
                    )
                )

            equivalence_delta = max(
                (
                    historical._distance(correct[offset], equivalent[offset])
                    for offset in range(len(correct))
                ),
                default=0.0,
            )
            pairwise_drift = historical._max_abs_delta(
                historical._pairwise_distances(correct), neutral_pairwise
            )
            axis_projection_drift = max(
                (
                    abs(
                        historical._dot(
                            historical._sub(correct[offset], transported_pivot),
                            transported_axis,
                        )
                        - historical._dot(
                            historical._sub(neutral_vertices[index], child_pivot),
                            child_axis,
                        )
                    )
                    for offset, index in enumerate(selected_indices)
                ),
                default=0.0,
            )
            stale_frame_error = max(
                (
                    historical._distance(correct[offset], stale[offset])
                    for offset in range(len(correct))
                ),
                default=0.0,
            )

            max_equivalence_delta = max(max_equivalence_delta, equivalence_delta)
            max_pairwise_drift = max(max_pairwise_drift, pairwise_drift)
            max_axis_projection_drift = max(max_axis_projection_drift, axis_projection_drift)
            if abs(parent_angle) > TOL and abs(child_angle) > TOL:
                max_stale_frame_error = max(max_stale_frame_error, stale_frame_error)

            witnesses.append(
                {
                    "parent_angle_deg": float(parent_angle),
                    "child_angle_deg": float(child_angle),
                    "transported_child_pivot_m": transported_pivot,
                    "transported_child_axis": transported_axis,
                    "trunk_to_child_center_distance_m": transported_center_distance,
                    "containment_margin_m": transported_containment_margin,
                    "declared_flex_envelope_overlap_margin_m": transported_overlap_margin,
                    "parent_socket_displacement_m": parent_socket_displacement,
                    "hierarchy_conjugation_residual_m": equivalence_delta,
                    "rigid_child_pairwise_distance_drift_m": pairwise_drift,
                    "transported_child_axis_projection_drift_m": axis_projection_drift,
                    "stale_neutral_child_frame_error_m": stale_frame_error,
                }
            )

    if max_stale_frame_error <= 1e-6:
        raise ValueError("stale-neutral-frame negative control is not discriminating")

    checks = {
        "exact_source_identity": source_digest == EXPECTED_SOURCE_DIGEST,
        "exact_geometry_receiver_identity": mesh_digest == EXPECTED_MIGRATED_MESH_DIGEST,
        "exact_five_branch_rigging_predecessor_reexecuted": family_result["result"] == family.RESULT,
        "upper_trunk_flex_center_is_exact_source_point": historical._close_vec(
            parent_flex["center"], parent_pivot
        ),
        "upper_trunk_flex_remains_declared_unproven": parent_flex["status"]
        == "DECLARED_NOT_DEFORMATION_TESTED",
        "east_mid_child_socket_is_existing_rigging_socket": historical._close_vec(
            child_flex["center"], child_pivot
        ),
        "east_mid_flex_remains_declared_unproven": child_flex["status"]
        == "DECLARED_NOT_DEFORMATION_TESTED",
        "east_mid_root_is_inside_upper_trunk_flex_envelope": containment_margin > 0.0,
        "source_derived_parent_axis_is_unit": abs(historical._length(parent_axis) - 1.0) <= TOL,
        "source_derived_parent_axis_is_perpendicular_to_incoming": abs(
            historical._dot(parent_axis, incoming)
        )
        <= TOL,
        "source_derived_parent_axis_is_perpendicular_to_outgoing": abs(
            historical._dot(parent_axis, outgoing)
        )
        <= TOL,
        "hierarchy_rebase_matches_parent_after_child_continuously_by_rigid_conjugation":
            max_equivalence_delta <= TOL,
        "child_rigidity_preserved_at_representatives": max_pairwise_drift <= TOL,
        "child_axis_projection_preserved_at_representatives": max_axis_projection_drift <= TOL,
        "trunk_child_center_distance_preserved_at_representatives": max_center_distance_drift <= TOL,
        "containment_margin_preserved_at_representatives": max_containment_margin_drift <= TOL,
        "flex_overlap_margin_preserved_at_representatives": max_envelope_overlap_margin_drift <= TOL,
        "stale_neutral_child_frame_control_rejected": max_stale_frame_error > 1e-6,
        "diagnostic_interval_not_promoted_to_source_rom": not claim_source_rom,
        "trunk_mesh_deformation_not_claimed": not claim_trunk_mesh_deformation,
        "surface_attachment_not_claimed": not claim_surface_attachment,
        "north_low_overlap_not_claimed_resolved": not claim_north_low_overlap_resolved,
        "animation_acceptance_not_claimed": not claim_animation_acceptance,
        "runtime_acceptance_not_claimed": not claim_runtime_acceptance,
    }

    return {
        "schema": SCHEMA,
        "result": RESULT if all(checks.values()) else "FAIL",
        "lineage": {
            "repository": "mike-axiom-mir/axm-nature-design",
            "organic_source_owner_pr": 8,
            "organic_source_owner_head": SOURCE_OWNER_HEAD,
            "organic_readiness_donor_head": ORGANIC_READINESS_DONOR_HEAD,
            "organic_source_blob": ORGANIC_SOURCE_BLOB,
            "organic_readiness_module_blob": ORGANIC_READINESS_MODULE_BLOB,
            "organic_interaction_doc_blob": ORGANIC_INTERACTION_DOC_BLOB,
            "geometry_receiver_pr": 9,
            "geometry_receiver_head": family.GEOMETRY_RECEIVER_HEAD,
            "rigging_pr": 14,
            "rigging_predecessor_head": RIGGING_PREDECESSOR_HEAD,
            "source_digest": source_digest,
            "geometry_migrated_mesh_digest": mesh_digest,
        },
        "organic_interaction_consumed": {
            "trunk_flex_zone_id": TRUNK_FLEX_ID,
            "trunk_flex_radius_m": TRUNK_FLEX_RADIUS_M,
            "child_branch_id": CHILD_BRANCH_ID,
            "child_flex_zone_id": CHILD_FLEX_ID,
            "child_flex_radius_m": CHILD_FLEX_RADIUS_M,
            "neutral_center_distance_m": center_distance,
            "neutral_containment_margin_m": containment_margin,
            "neutral_declared_flex_envelope_overlap_margin_m": envelope_overlap_margin,
            "north_low_overlap_policy_resolved": False,
        },
        "rigging_constraint": {
            "parent_trunk_point_id": TRUNK_POINT_ID,
            "parent_pivot_m": parent_pivot,
            "source_derived_parent_axis": parent_axis,
            "parent_diagnostic_interval_deg": [
                PARENT_DIAGNOSTIC_MIN_DEG,
                PARENT_DIAGNOSTIC_MAX_DEG,
            ],
            "parent_representative_angles_deg": list(PARENT_REPRESENTATIVE_ANGLES_DEG),
            "child_branch_id": CHILD_BRANCH_ID,
            "neutral_child_pivot_m": child_pivot,
            "neutral_child_axis": child_axis,
            "child_diagnostic_interval_deg": [
                family.DIAGNOSTIC_MIN_DEG,
                family.DIAGNOSTIC_MAX_DEG,
            ],
            "child_representative_angles_deg": list(CHILD_REPRESENTATIVE_ANGLES_DEG),
            "selected_child_vertices": len(selected_indices),
            "selected_child_triangles": int(child_probe["selected_triangles"]),
            "policy": (
                "TRANSPORT_CHILD_PIVOT_AND_AXIS_THROUGH_PARENT_TRUNK_FRAME_BEFORE_APPLYING_"
                "EXISTING_CHILD_LOCAL_ROTATION"
            ),
            "parent_interval_semantics": (
                "RIGGING_HIERARCHY_VERIFICATION_PROBE_ONLY_NOT_SOURCE_OR_BIOLOGICAL_ROM"
            ),
        },
        "measurements": {
            "representative_parent_child_pose_count": len(witnesses),
            "maximum_hierarchy_conjugation_residual_m": max_equivalence_delta,
            "maximum_rigid_child_pairwise_distance_drift_m": max_pairwise_drift,
            "maximum_transported_child_axis_projection_drift_m": max_axis_projection_drift,
            "maximum_trunk_child_center_distance_drift_m": max_center_distance_drift,
            "maximum_containment_margin_drift_m": max_containment_margin_drift,
            "maximum_declared_flex_envelope_overlap_margin_drift_m":
                max_envelope_overlap_margin_drift,
            "maximum_parent_socket_displacement_m": max_parent_socket_displacement,
            "maximum_stale_neutral_child_frame_error_m": max_stale_frame_error,
        },
        "representative_witnesses": witnesses,
        "continuous_product_domain_certificate": {
            "parent_interval_deg": [
                PARENT_DIAGNOSTIC_MIN_DEG,
                PARENT_DIAGNOSTIC_MAX_DEG,
            ],
            "child_interval_deg": [
                family.DIAGNOSTIC_MIN_DEG,
                family.DIAGNOSTIC_MAX_DEG,
            ],
            "continuous_for_every_real_parent_child_pair_in_closed_product_domain": True,
            "reason": (
                "Rigid parent rotation preserves the parent-pivot-to-child-socket distance; "
                "the child frame is transported by that same rotation; Rodrigues rotations are "
                "continuous; and rigid-transform conjugation makes child-local-then-parent exactly "
                "equivalent to parent-then-child-about-the-transported-frame."
            ),
            "east_mid_containment_preserved_for_every_parent_angle": True,
            "declared_flex_overlap_margin_preserved_for_every_parent_angle": True,
            "child_rigidity_preserved_for_every_parent_child_pair": True,
            "trunk_mesh_deformation_or_skin_weights_proven": False,
            "surface_attachment_proven": False,
            "north_low_overlap_policy_proven": False,
            "collision_or_self_intersection_proven": False,
            "simultaneous_whole_tree_motion_proven": False,
            "source_or_biological_rom_proven": False,
        },
        "checks": checks,
        "truth_boundary": {
            "organic_source_rewritten": False,
            "geometry_receiver_rewritten": False,
            "existing_east_mid_child_socket_rewritten": False,
            "trunk_mesh_deformation_claimed": False,
            "production_skin_weights_claimed": False,
            "surface_attachment_claimed": False,
            "north_low_overlap_claimed_resolved": False,
            "simultaneous_whole_tree_motion_claimed": False,
            "collision_or_self_intersection_claimed": False,
            "physical_wind_or_biomechanics_claimed": False,
            "animation_timing_interpolation_or_playback_claimed": False,
            "technical_art_target_host_claimed": False,
            "runtime_controller_or_device_claimed": False,
            "visual_acceptance_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }

"""Explicit Geometry-receiver rebind for the east/rear Nature Rigging socket.

The historical Rigging implementation remains frozen in ``rear_tree_rigging`` at
predecessor head 87ce8b2f.  This successor reuses its exact articulation math and
ownership rules while binding the proof to Geometry PR #9's migrated-winding
receiver.  No historical PASS is transferred without re-execution.
"""
from __future__ import annotations

import copy

from . import rear_tree_rigging as historical
from .organic_form import build_mesh, digest, validate_source
from .source_topology_migration import evaluate as evaluate_topology_migration

SCHEMA = "axm.nature-east-rear-root-socket-geometry-rebind-evidence/v0.1"
RESULT = "PASS_NORTH_TOP_ROOT_SOCKET_GEOMETRY_MIGRATED_RECEIVER_REBIND_DIAGNOSTIC_MINUS5_TO_PLUS5"
SOURCE_OWNER_HEAD = "fdc9d2b6ee729728551e22fd3eafa23ad60b6c7a"
GEOMETRY_RECEIVER_HEAD = "9b451ba1f65281f550a6754e18574f7ab2951e28"
RIGGING_PREDECESSOR_HEAD = "87ce8b2ff10937abec4432e1c6d5a7114a076cdb"
EXPECTED_SOURCE_DIGEST = historical.EXPECTED_SOURCE_DIGEST
HISTORICAL_ORGANIC_MESH_DIGEST = historical.EXPECTED_MESH_DIGEST
EXPECTED_MIGRATED_MESH_DIGEST = "aa9d450a78fef722672ea9af0f9aca98b4c1a0ca3705661784f5f61f3e9b6a31"
BRANCH_ID = historical.BRANCH_ID
LEAF_CLUSTER_ID = historical.LEAF_CLUSTER_ID
FLEX_ZONE_ID = historical.FLEX_ZONE_ID
EXPECTED_FLEX_RADIUS_M = historical.EXPECTED_FLEX_RADIUS_M
DIAGNOSTIC_MIN_DEG = historical.DIAGNOSTIC_MIN_DEG
DIAGNOSTIC_MAX_DEG = historical.DIAGNOSTIC_MAX_DEG
REPRESENTATIVE_ANGLES_DEG = historical.REPRESENTATIVE_ANGLES_DEG
TOL = historical.TOL


def evaluate(
    source: dict,
    *,
    requested_branch_id: str = BRANCH_ID,
    requested_geometry_receiver_head: str = GEOMETRY_RECEIVER_HEAD,
    joint_pivot_override=None,
    diagnostic_min_deg: float = DIAGNOSTIC_MIN_DEG,
    diagnostic_max_deg: float = DIAGNOSTIC_MAX_DEG,
    claim_source_rom: bool = False,
    claim_geometry_acceptance_transfer: bool = False,
    claim_animation_acceptance: bool = False,
    claim_runtime_acceptance: bool = False,
) -> dict:
    validate_source(source)
    if source.get("study_id") != historical.STUDY_ID:
        raise ValueError("unexpected Nature study identity")
    source_digest = digest(source)
    if source_digest != EXPECTED_SOURCE_DIGEST:
        raise ValueError("exact Organic source identity drift")
    if requested_geometry_receiver_head != GEOMETRY_RECEIVER_HEAD:
        raise ValueError("exact Geometry receiver head drift")
    if requested_branch_id != BRANCH_ID:
        raise ValueError("this bounded lane owns only north-top")
    if abs(float(diagnostic_min_deg) - DIAGNOSTIC_MIN_DEG) > TOL or abs(float(diagnostic_max_deg) - DIAGNOSTIC_MAX_DEG) > TOL:
        raise ValueError("diagnostic probe interval may not be widened or retimed")
    if claim_source_rom:
        raise ValueError("diagnostic probe must not be promoted to source/biological ROM")
    if claim_geometry_acceptance_transfer:
        raise ValueError("Rigging cannot transfer Geometry acceptance")
    if claim_animation_acceptance:
        raise ValueError("Rigging evidence cannot claim Animation acceptance")
    if claim_runtime_acceptance:
        raise ValueError("Rigging evidence cannot claim Runtime acceptance")

    migration = evaluate_topology_migration(source)
    if migration["status"] != "PASS_SOURCE_GENERATOR_WINDING_MIGRATION":
        raise ValueError("pinned Geometry topology migration did not pass")
    if migration["migrated_mesh_digest"] != EXPECTED_MIGRATED_MESH_DIGEST:
        raise ValueError("exact Geometry migrated receiver identity drift")
    if migration["historical_mesh_digest"] != HISTORICAL_ORGANIC_MESH_DIGEST:
        raise ValueError("historical Organic receiver identity drift")

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
    if not historical._close_vec(pivot, flex_center):
        raise ValueError("owner flex center is not the exact branch root")
    if joint_pivot_override is not None and not historical._close_vec([float(x) for x in joint_pivot_override], pivot):
        raise ValueError("Rigging pivot must remain the exact source-owned flex center")

    nearest_distance, trunk_segment_index, trunk_t, trunk_tangent, trunk_nearest = historical._closest_segment_and_tangent(
        pivot, source["trunk"]
    )
    branch_tangent = historical._norm(historical._sub(branch["points"][1], pivot))
    axis_raw = historical._cross(trunk_tangent, branch_tangent)
    if historical._length(axis_raw) <= 1e-9:
        raise ValueError("source-derived bend-plane axis is degenerate")
    axis = historical._norm(axis_raw)

    mesh = build_mesh(source)
    mesh_digest = digest(mesh)
    if mesh_digest != EXPECTED_MIGRATED_MESH_DIGEST:
        raise ValueError("exact Geometry migrated mesh identity drift")

    selected_region_ids = [
        f"branch:{BRANCH_ID}:0",
        f"branch:{BRANCH_ID}:1",
        *[f"leaf:{LEAF_CLUSTER_ID}:{i}" for i in range(len(cluster["blades"]))],
    ]
    selected_indices, selected_triangle_count = historical._region_vertex_indices(mesh, selected_region_ids)
    if len(selected_indices) != 52 or selected_triangle_count != 72:
        raise ValueError("north-top generated subtree identity drift")
    selected_set = set(selected_indices)
    fixed_indices = [i for i in range(len(mesh["vertices"])) if i not in selected_set]
    if len(fixed_indices) != 338:
        raise ValueError("fixed receiver partition drift")

    neutral_vertices = [[float(x) for x in v] for v in mesh["vertices"]]
    neutral_selected = [neutral_vertices[i] for i in selected_indices]
    neutral_pairwise = historical._pairwise_distances(neutral_selected)
    pivot_indices = [i for i in selected_indices if historical._distance(neutral_vertices[i], pivot) <= TOL]
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
            deformed[index] = historical._rotate_about_axis(neutral_vertices[index], pivot, axis, angle)

        fixed_drift = max((historical._distance(deformed[i], neutral_vertices[i]) for i in fixed_indices), default=0.0)
        pivot_drift = max((historical._distance(deformed[i], neutral_vertices[i]) for i in pivot_indices), default=0.0)
        selected = [deformed[i] for i in selected_indices]
        pairwise_drift = historical._max_abs_delta(historical._pairwise_distances(selected), neutral_pairwise)
        axis_projection_drift = max(
            (
                abs(
                    historical._dot(historical._sub(deformed[i], pivot), axis)
                    - historical._dot(historical._sub(neutral_vertices[i], pivot), axis)
                )
                for i in selected_indices
            ),
            default=0.0,
        )
        selected_displacement = max(
            (historical._distance(deformed[i], neutral_vertices[i]) for i in selected_indices), default=0.0
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
        "exact_geometry_receiver_identity": mesh_digest == EXPECTED_MIGRATED_MESH_DIGEST,
        "geometry_migration_receipt_passes": migration["status"] == "PASS_SOURCE_GENERATOR_WINDING_MIGRATION",
        "historical_and_migrated_receivers_remain_distinct": HISTORICAL_ORGANIC_MESH_DIGEST != EXPECTED_MIGRATED_MESH_DIGEST,
        "geometry_reports_vertex_positions_preserved": migration["truth_boundary"]["vertex_positions_changed_from_proven_candidate"] is False,
        "geometry_reports_triangle_membership_preserved": migration["truth_boundary"]["triangle_membership_changed_from_proven_candidate"] is False,
        "exact_root_flex_metadata": historical._close_vec(flex_center, pivot)
        and abs(float(flex["radius"]) - EXPECTED_FLEX_RADIUS_M) <= TOL
        and flex["status"] == "DECLARED_NOT_DEFORMATION_TESTED",
        "source_derived_axis_is_unit": abs(historical._length(axis) - 1.0) <= TOL,
        "source_derived_axis_perpendicular_to_local_trunk": abs(historical._dot(axis, trunk_tangent)) <= TOL,
        "source_derived_axis_perpendicular_to_branch_tangent": abs(historical._dot(axis, branch_tangent)) <= TOL,
        "exact_generated_child_partition": len(selected_indices) == 52 and selected_triangle_count == 72 and len(fixed_indices) == 338,
        "fixed_receiver_is_exact": maximum_fixed_drift <= TOL,
        "source_owned_pivot_is_exact": maximum_pivot_drift <= TOL,
        "rigid_child_pairwise_distances_preserved": maximum_pairwise_drift <= TOL,
        "rotation_axis_projection_preserved": maximum_axis_projection_drift <= TOL,
        "diagnostic_interval_not_promoted_to_rom": not claim_source_rom,
        "geometry_acceptance_not_transferred": not claim_geometry_acceptance_transfer,
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
            "geometry_receiver_pr": 9,
            "geometry_receiver_head": GEOMETRY_RECEIVER_HEAD,
            "rigging_pr": 14,
            "rigging_predecessor_head": RIGGING_PREDECESSOR_HEAD,
            "source_digest": source_digest,
            "historical_organic_mesh_digest": HISTORICAL_ORGANIC_MESH_DIGEST,
            "geometry_migrated_mesh_digest": mesh_digest,
            "receiver_rebind_semantics": "EXPLICIT_GEOMETRY_RECEIVER_REBIND__NO_PASS_TRANSFER",
        },
        "geometry_receiver": {
            "shared_edge_orientation_conflicts": migration["topology"]["shared_edge_orientation_conflicts"],
            "boundary_edges": migration["topology"]["boundary_edges"],
            "nonmanifold_edges": migration["topology"]["nonmanifold_edges"],
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
                "For every real angle in the diagnostic interval, the selected child uses the same rigid "
                "Rodrigues transform around the exact source-owned pivot/axis while all unselected vertices "
                "are identity-mapped. Pivot, fixed receiver, selected pairwise distances and selected axis "
                "projection are therefore invariant continuously."
            ),
            "scope_deg": [DIAGNOSTIC_MIN_DEG, DIAGNOSTIC_MAX_DEG],
            "collision_or_clearance_proven": False,
            "surface_attachment_or_blended_weighting_proven": False,
            "biological_range_of_motion_proven": False,
        },
        "checks": checks,
        "truth_boundary": {
            "organic_source_rewritten": False,
            "geometry_receiver_explicitly_rebound": True,
            "historical_rigging_pass_transferred_without_retest": False,
            "topology_authorship_claimed_by_rigging": False,
            "production_skin_weights_tested": False,
            "surface_attachment_proven": False,
            "collision_or_self_intersection_proven": False,
            "stress_strength_or_botanical_validity_proven": False,
            "wind_or_vfx_behavior_claimed": False,
            "animation_timing_or_playback_claimed": False,
            "technical_art_target_host_claimed": False,
            "runtime_controller_or_device_claimed": False,
            "visual_acceptance_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }

"""Rigging-owned diagnostic articulation family for the east/rear Nature tree.

This successor consumes the exact Organic source, Geometry migrated receiver, the
existing north-top Rigging proof, and one exact Procedural child-partition handoff.
Procedural only identifies deterministic child selections; this module independently
re-runs Rigging articulation/deformation evidence for all five primary branch roots.

The ±5 degree interval is a Rigging verification probe only.  It is not source ROM,
plant biomechanics, Animation acceptance, wind/VFX behavior, or Runtime acceptance.
"""
from __future__ import annotations

import copy
from typing import Iterable

from . import rear_tree_rigging as historical
from . import rear_tree_rigging_geometry_rebind as predecessor
from .organic_form import build_mesh, digest, validate_source
from .source_topology_migration import evaluate as evaluate_topology_migration

SCHEMA = "axm.nature-east-rear-primary-branch-root-socket-rigging-family-evidence/v0.1"
RESULT = "PASS_FIVE_PRIMARY_BRANCH_ROOT_SOCKET_RIGID_CHILD_FAMILY_GEOMETRY_RECEIVER_DIAGNOSTIC_MINUS5_TO_PLUS5"
STUDY_ID = historical.STUDY_ID
SOURCE_OWNER_HEAD = predecessor.SOURCE_OWNER_HEAD
GEOMETRY_RECEIVER_HEAD = predecessor.GEOMETRY_RECEIVER_HEAD
RIGGING_PREDECESSOR_HEAD = "f792d2369675d532be478e17c7a07f441d817c7c"
PROCEDURAL_DONOR_HEAD = "342385c867050dc8e8f7312c63235a68bdd92d3d"
PROCEDURAL_REBIND_CONTRACT_PATH = "examples/rear_tree_branch_child_partition_geometry_rebind_002.json"
PROCEDURAL_REBIND_CONTRACT_BLOB = "73e38d08f426efb742e1d66b992ede04737ed576"
PROCEDURAL_PARTITION_MODULE_PATH = "src/axm_nature_design/branch_partition_geometry_rebind.py"
PROCEDURAL_PARTITION_MODULE_BLOB = "7b522f6c379d8cae1d1e9d95e941ac108cfc003b"
PROCEDURAL_FAMILY_MODULE_PATH = "src/axm_nature_design/branch_partition_family.py"
PROCEDURAL_FAMILY_MODULE_BLOB = "3c502029900916bb62cda8c501144e0a5ea5c076"
EXPECTED_SOURCE_DIGEST = predecessor.EXPECTED_SOURCE_DIGEST
EXPECTED_MIGRATED_MESH_DIGEST = predecessor.EXPECTED_MIGRATED_MESH_DIGEST
HISTORICAL_ORGANIC_MESH_DIGEST = predecessor.HISTORICAL_ORGANIC_MESH_DIGEST
BRANCH_IDS = ("south-low", "north-low", "east-mid", "west-high", "north-top")
EXPECTED_FLEX_RADII_M = {
    "south-low": 0.14,
    "north-low": 0.14,
    "east-mid": 0.12,
    "west-high": 0.12,
    "north-top": 0.12,
}
DIAGNOSTIC_MIN_DEG = historical.DIAGNOSTIC_MIN_DEG
DIAGNOSTIC_MAX_DEG = historical.DIAGNOSTIC_MAX_DEG
REPRESENTATIVE_ANGLES_DEG = historical.REPRESENTATIVE_ANGLES_DEG
TOL = historical.TOL


def _single(rows: Iterable[dict], label: str) -> dict:
    values = list(rows)
    if len(values) != 1:
        raise ValueError(f"{label} must resolve exactly once")
    return values[0]


def _probe_branch(source: dict, mesh: dict, branch_id: str, pivot_override=None) -> dict:
    branch = _single((row for row in source["branches"] if row.get("id") == branch_id), f"branch {branch_id}")
    cluster_id = f"{branch_id}-leaves"
    flex_id = f"{branch_id}-branch-flex"
    cluster = _single((row for row in source["leaf_clusters"] if row.get("id") == cluster_id), f"cluster {cluster_id}")
    flex = _single((row for row in source["flex_zones"] if row.get("id") == flex_id), f"flex {flex_id}")

    if flex.get("status") != "DECLARED_NOT_DEFORMATION_TESTED":
        raise ValueError(f"source flex metadata truth boundary changed: {branch_id}")
    expected_radius = EXPECTED_FLEX_RADII_M[branch_id]
    if abs(float(flex["radius"]) - expected_radius) > TOL:
        raise ValueError(f"source flex radius drift: {branch_id}")

    pivot = [float(value) for value in branch["points"][0]]
    flex_center = [float(value) for value in flex["center"]]
    if not historical._close_vec(pivot, flex_center):
        raise ValueError(f"source flex center is not exact branch root: {branch_id}")
    if pivot_override is not None and not historical._close_vec([float(value) for value in pivot_override], pivot):
        raise ValueError(f"Rigging pivot drift: {branch_id}")

    nearest_distance, trunk_segment_index, trunk_t, trunk_tangent, trunk_nearest = historical._closest_segment_and_tangent(
        pivot, source["trunk"]
    )
    branch_tangent = historical._norm(historical._sub(branch["points"][1], pivot))
    axis_raw = historical._cross(trunk_tangent, branch_tangent)
    if historical._length(axis_raw) <= 1e-9:
        raise ValueError(f"source-derived bend-plane axis is degenerate: {branch_id}")
    axis = historical._norm(axis_raw)

    selected_region_ids = [
        f"branch:{branch_id}:0",
        f"branch:{branch_id}:1",
        *[f"leaf:{cluster_id}:{index}" for index in range(len(cluster["blades"]))],
    ]
    selected_indices, selected_triangle_count = historical._region_vertex_indices(mesh, selected_region_ids)
    if len(selected_indices) != 52 or selected_triangle_count != 72:
        raise ValueError(f"generated primary-branch child partition drift: {branch_id}")
    selected_set = set(selected_indices)
    fixed_indices = [index for index in range(len(mesh["vertices"])) if index not in selected_set]
    if len(fixed_indices) != 338:
        raise ValueError(f"fixed receiver partition drift: {branch_id}")

    neutral_vertices = [[float(value) for value in vertex] for vertex in mesh["vertices"]]
    neutral_selected = [neutral_vertices[index] for index in selected_indices]
    neutral_pairwise = historical._pairwise_distances(neutral_selected)
    pivot_indices = [index for index in selected_indices if historical._distance(neutral_vertices[index], pivot) <= TOL]
    if len(pivot_indices) != 1:
        raise ValueError(f"expected one exact generated pivot-center vertex: {branch_id}")

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

        fixed_drift = max((historical._distance(deformed[index], neutral_vertices[index]) for index in fixed_indices), default=0.0)
        pivot_drift = max((historical._distance(deformed[index], neutral_vertices[index]) for index in pivot_indices), default=0.0)
        selected = [deformed[index] for index in selected_indices]
        pairwise_drift = historical._max_abs_delta(historical._pairwise_distances(selected), neutral_pairwise)
        axis_projection_drift = max(
            (
                abs(
                    historical._dot(historical._sub(deformed[index], pivot), axis)
                    - historical._dot(historical._sub(neutral_vertices[index], pivot), axis)
                )
                for index in selected_indices
            ),
            default=0.0,
        )
        selected_displacement = max(
            (historical._distance(deformed[index], neutral_vertices[index]) for index in selected_indices),
            default=0.0,
        )

        maximum_fixed_drift = max(maximum_fixed_drift, fixed_drift)
        maximum_pivot_drift = max(maximum_pivot_drift, pivot_drift)
        maximum_pairwise_drift = max(maximum_pairwise_drift, pairwise_drift)
        maximum_axis_projection_drift = max(maximum_axis_projection_drift, axis_projection_drift)
        maximum_selected_displacement = max(maximum_selected_displacement, selected_displacement)
        poses.append(
            {
                "angle_deg": float(angle),
                "fixed_vertex_drift_m": fixed_drift,
                "pivot_vertex_drift_m": pivot_drift,
                "selected_pairwise_distance_drift_m": pairwise_drift,
                "selected_axis_projection_drift_m": axis_projection_drift,
                "maximum_selected_vertex_displacement_m": selected_displacement,
            }
        )

    checks = {
        "exact_root_flex_metadata": historical._close_vec(flex_center, pivot)
        and abs(float(flex["radius"]) - expected_radius) <= TOL
        and flex["status"] == "DECLARED_NOT_DEFORMATION_TESTED",
        "source_derived_axis_is_unit": abs(historical._length(axis) - 1.0) <= TOL,
        "source_derived_axis_perpendicular_to_local_trunk": abs(historical._dot(axis, trunk_tangent)) <= TOL,
        "source_derived_axis_perpendicular_to_branch_tangent": abs(historical._dot(axis, branch_tangent)) <= TOL,
        "exact_generated_child_partition": len(selected_indices) == 52
        and selected_triangle_count == 72
        and len(fixed_indices) == 338,
        "fixed_receiver_is_exact": maximum_fixed_drift <= TOL,
        "source_owned_pivot_is_exact": maximum_pivot_drift <= TOL,
        "rigid_child_pairwise_distances_preserved": maximum_pairwise_drift <= TOL,
        "rotation_axis_projection_preserved": maximum_axis_projection_drift <= TOL,
    }
    if not all(checks.values()):
        raise ValueError(f"Rigging diagnostic invariant failed: {branch_id}")

    return {
        "branch_id": branch_id,
        "leaf_cluster_id": cluster_id,
        "flex_zone_id": flex_id,
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
        "selected_vertex_indices": selected_indices,
        "selected_vertices": len(selected_indices),
        "selected_triangles": selected_triangle_count,
        "fixed_vertices": len(fixed_indices),
        "generated_pivot_vertex_indices": pivot_indices,
        "measurements": {
            "maximum_fixed_vertex_drift_m": maximum_fixed_drift,
            "maximum_pivot_vertex_drift_m": maximum_pivot_drift,
            "maximum_selected_pairwise_distance_drift_m": maximum_pairwise_drift,
            "maximum_selected_axis_projection_drift_m": maximum_axis_projection_drift,
            "maximum_selected_vertex_displacement_m": maximum_selected_displacement,
        },
        "poses": poses,
        "checks": checks,
    }


def evaluate(
    source: dict,
    *,
    requested_branch_ids=BRANCH_IDS,
    requested_geometry_receiver_head: str = GEOMETRY_RECEIVER_HEAD,
    requested_procedural_donor_head: str = PROCEDURAL_DONOR_HEAD,
    joint_pivot_overrides: dict | None = None,
    diagnostic_min_deg: float = DIAGNOSTIC_MIN_DEG,
    diagnostic_max_deg: float = DIAGNOSTIC_MAX_DEG,
    claim_source_rom: bool = False,
    claim_procedural_authority_transfer: bool = False,
    claim_geometry_acceptance_transfer: bool = False,
    claim_animation_acceptance: bool = False,
    claim_runtime_acceptance: bool = False,
) -> dict:
    """Independently retest all five source-declared primary branch root sockets."""
    validate_source(source)
    if source.get("study_id") != STUDY_ID:
        raise ValueError("unexpected Nature study identity")
    source_digest = digest(source)
    if source_digest != EXPECTED_SOURCE_DIGEST:
        raise ValueError("exact Organic source identity drift")
    if requested_geometry_receiver_head != GEOMETRY_RECEIVER_HEAD:
        raise ValueError("exact Geometry receiver head drift")
    if requested_procedural_donor_head != PROCEDURAL_DONOR_HEAD:
        raise ValueError("exact Procedural donor head drift")
    if tuple(requested_branch_ids) != BRANCH_IDS:
        raise ValueError("Rigging family requires the exact five authorized primary branch identities in canonical order")
    if abs(float(diagnostic_min_deg) - DIAGNOSTIC_MIN_DEG) > TOL or abs(float(diagnostic_max_deg) - DIAGNOSTIC_MAX_DEG) > TOL:
        raise ValueError("diagnostic probe interval may not be widened or retimed")
    if claim_source_rom:
        raise ValueError("diagnostic probe must not be promoted to source/biological ROM")
    if claim_procedural_authority_transfer:
        raise ValueError("Rigging may consume a Procedural selection handoff but may not transfer Procedural authority")
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

    mesh = build_mesh(source)
    mesh_digest = digest(mesh)
    if mesh_digest != EXPECTED_MIGRATED_MESH_DIGEST:
        raise ValueError("exact Geometry migrated mesh identity drift")

    overrides = joint_pivot_overrides or {}
    unknown_overrides = set(overrides) - set(BRANCH_IDS)
    if unknown_overrides:
        raise ValueError(f"unknown Rigging pivot override branch: {sorted(unknown_overrides)}")

    probes = [_probe_branch(source, mesh, branch_id, overrides.get(branch_id)) for branch_id in BRANCH_IDS]
    selected_sets = [set(row["selected_vertex_indices"]) for row in probes]
    pairwise_disjoint = all(
        not (selected_sets[left] & selected_sets[right])
        for left in range(len(selected_sets))
        for right in range(left + 1, len(selected_sets))
    )
    if not pairwise_disjoint:
        raise ValueError("primary branch child partitions overlap in generated vertex identity")

    predecessor_north = predecessor.evaluate(source)
    north = next(row for row in probes if row["branch_id"] == "north-top")
    prior_probe = predecessor_north["rigging_probe"]
    if not historical._close_vec(north["joint_pivot_m"], prior_probe["joint_pivot_m"]):
        raise ValueError("north-top family pivot does not reproduce Rigging predecessor")
    if not historical._close_vec(north["source_derived_axis"], prior_probe["source_derived_axis"]):
        raise ValueError("north-top family axis does not reproduce Rigging predecessor")
    if north["selected_vertices"] != prior_probe["selected_vertices"] or north["selected_triangles"] != prior_probe["selected_triangles"]:
        raise ValueError("north-top family partition does not reproduce Rigging predecessor")
    for key, value in predecessor_north["measurements"].items():
        if abs(float(north["measurements"][key]) - float(value)) > TOL:
            raise ValueError(f"north-top family measurement does not reproduce Rigging predecessor: {key}")

    maximums = {
        "maximum_fixed_vertex_drift_m": max(row["measurements"]["maximum_fixed_vertex_drift_m"] for row in probes),
        "maximum_pivot_vertex_drift_m": max(row["measurements"]["maximum_pivot_vertex_drift_m"] for row in probes),
        "maximum_selected_pairwise_distance_drift_m": max(
            row["measurements"]["maximum_selected_pairwise_distance_drift_m"] for row in probes
        ),
        "maximum_selected_axis_projection_drift_m": max(
            row["measurements"]["maximum_selected_axis_projection_drift_m"] for row in probes
        ),
        "maximum_selected_vertex_displacement_m": max(
            row["measurements"]["maximum_selected_vertex_displacement_m"] for row in probes
        ),
    }

    checks = {
        "exact_source_identity": source_digest == EXPECTED_SOURCE_DIGEST,
        "exact_geometry_receiver_identity": mesh_digest == EXPECTED_MIGRATED_MESH_DIGEST,
        "geometry_migration_receipt_passes": migration["status"] == "PASS_SOURCE_GENERATOR_WINDING_MIGRATION",
        "five_exact_branch_roots_retested": len(probes) == 5 and [row["branch_id"] for row in probes] == list(BRANCH_IDS),
        "five_exact_source_flex_declarations_remain_unpromoted": all(
            row["source_flex_status"] == "DECLARED_NOT_DEFORMATION_TESTED" for row in probes
        ),
        "procedural_child_partitions_pairwise_disjoint": pairwise_disjoint,
        "north_top_predecessor_reproduced": predecessor_north["result"] == predecessor.RESULT,
        "all_branch_structural_checks_pass": all(all(row["checks"].values()) for row in probes),
        "diagnostic_interval_not_promoted_to_rom": not claim_source_rom,
        "procedural_authority_not_transferred": not claim_procedural_authority_transfer,
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
            "procedural_pr": 4,
            "procedural_donor_head": PROCEDURAL_DONOR_HEAD,
            "procedural_rebind_contract_path": PROCEDURAL_REBIND_CONTRACT_PATH,
            "procedural_rebind_contract_blob": PROCEDURAL_REBIND_CONTRACT_BLOB,
            "procedural_partition_module_path": PROCEDURAL_PARTITION_MODULE_PATH,
            "procedural_partition_module_blob": PROCEDURAL_PARTITION_MODULE_BLOB,
            "procedural_family_module_path": PROCEDURAL_FAMILY_MODULE_PATH,
            "procedural_family_module_blob": PROCEDURAL_FAMILY_MODULE_BLOB,
            "source_digest": source_digest,
            "historical_organic_mesh_digest": HISTORICAL_ORGANIC_MESH_DIGEST,
            "geometry_migrated_mesh_digest": mesh_digest,
            "receiver_relation": "EXACT_PROCEDURAL_SELECTION_HANDOFF_CONSUMED_BY_INDEPENDENT_RIGGING_RETEST",
        },
        "geometry_receiver": {
            "shared_edge_orientation_conflicts": migration["topology"]["shared_edge_orientation_conflicts"],
            "boundary_edges": migration["topology"]["boundary_edges"],
            "nonmanifold_edges": migration["topology"]["nonmanifold_edges"],
        },
        "rigging_family": {
            "branch_ids": list(BRANCH_IDS),
            "branch_count": len(probes),
            "representative_angles_deg": list(REPRESENTATIVE_ANGLES_DEG),
            "diagnostic_interval_deg": [DIAGNOSTIC_MIN_DEG, DIAGNOSTIC_MAX_DEG],
            "diagnostic_interval_semantics": "RIGGING_VERIFICATION_PROBE_ONLY_NOT_SOURCE_OR_BIOLOGICAL_ROM",
            "pairwise_child_vertex_disjoint": pairwise_disjoint,
            "total_representative_pose_evaluations": len(probes) * len(REPRESENTATIVE_ANGLES_DEG),
            "probes": probes,
        },
        "measurements": maximums,
        "continuous_invariant": {
            "statement": (
                "For each of the five independently probed primary branch roots, every real angle in the "
                "declared diagnostic interval uses one rigid Rodrigues transform around that branch's exact "
                "source-owned root and source-derived bend-plane axis while all unselected vertices for that "
                "single-branch probe are identity-mapped. Pivot location, fixed receiver positions, selected "
                "pairwise distances, and selected axis projection are therefore invariant continuously for "
                "each branch considered independently."
            ),
            "scope_deg": [DIAGNOSTIC_MIN_DEG, DIAGNOSTIC_MAX_DEG],
            "branches": list(BRANCH_IDS),
            "simultaneous_multi_branch_motion_proven": False,
            "collision_or_self_intersection_proven": False,
            "surface_attachment_or_blended_weighting_proven": False,
            "biological_range_of_motion_proven": False,
        },
        "checks": checks,
        "truth_boundary": {
            "organic_source_rewritten": False,
            "geometry_receiver_explicitly_preserved": True,
            "procedural_selection_authority_transferred": False,
            "historical_north_top_pass_transferred_without_retest": False,
            "sibling_branch_deformation_inferred_without_test": False,
            "production_skin_weights_tested": False,
            "surface_attachment_proven": False,
            "simultaneous_multi_branch_motion_proven": False,
            "collision_or_self_intersection_proven": False,
            "stress_strength_or_botanical_validity_proven": False,
            "wind_or_vfx_behavior_claimed": False,
            "animation_timing_interpolation_or_playback_claimed": False,
            "technical_art_target_host_claimed": False,
            "runtime_controller_or_device_claimed": False,
            "visual_acceptance_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }

"""Rigging-owned attachment-representation gate for the north-low diagnostic socket.

Geometry classified the exact current north-low child as a detached diagnostic/proxy
selection: six indexed components, with zero indexed vertices shared with the trunk.
Rigging consumes that exact Geometry-owned fact without duplicating topology analysis.
The existing socket transform and parent-influence exclusion remain unchanged; this
module only prevents those valid transform-policy results from being promoted into a
welded/connected skinning claim.

This is diagnostic evidence only. It does not establish production attachment, weights,
Animation, target-host transport, Runtime, collision, botanical mechanics, or CANON.
"""
from __future__ import annotations

import hashlib
import json

from . import rear_tree_rigging_north_low_parent_influence_gate as predecessor

SCHEMA = "axm.nature-north-low-attachment-representation-rigging-evidence/v0.1"
RESULT = "PASS_NORTH_LOW_DETACHED_CHILD_SOCKET_ATTACHMENT_REPRESENTATION_GATE_DIAGNOSTIC"
RIGGING_PREDECESSOR_HEAD = "975931b11555d156e04e2ab12e9756fc6c9598a3"
GEOMETRY_ATTACHMENT_DONOR_HEAD = "d32a41558910d78595042fb638a785714f825806"
GEOMETRY_ATTACHMENT_CONTRACT_BLOB = "127502ae50c7b442c88edd8454c9a74ba053da71"
GEOMETRY_ATTACHMENT_OBSERVER_BLOB = "279bd95a80208f346bd654e300e4b02aff34cf47"
GEOMETRY_RESULT = "PASS_NORTH_LOW_DIAGNOSTIC_CHILD_TOPOLOGY_CLASSIFIED__HOLD_CONNECTED_BRANCH_TRUNK_ATTACHMENT"
GEOMETRY_CONTRACT_SCHEMA = "axm.nature-north-low-attachment-topology-geometry-contract/v0.1"
GEOMETRY_CONTRACT_PATH = "contracts/east-rear-north-low-attachment-topology-geometry-005.json"
EXPECTED_COMPONENT_COUNT = 6
EXPECTED_CLOSED_COMPONENTS = 2
EXPECTED_OPEN_COMPONENTS = 4
EXPECTED_SHARED_INDEXED_VERTICES = 0
EXPECTED_SELECTED_VERTICES = 52
EXPECTED_SELECTED_TRIANGLES = 72
EXPECTED_ROOT_SEGMENT = {
    "vertices": 18,
    "triangles": 32,
    "edges": 48,
    "boundary_edges": 0,
    "euler_characteristic": 2,
    "closed_edge_manifold": True,
}


def expected_geometry_contract() -> dict:
    """Return the exact Geometry-owned contract shape consumed by this gate."""
    return {
        "schema": GEOMETRY_CONTRACT_SCHEMA,
        "study_id": predecessor.STUDY_ID,
        "repository": "mike-axiom-mir/axm-nature-design",
        "geometry_predecessor_head": "200ab4b60b8a54460f1265b0ee52eb111f1b280a",
        "rigging_owner_head": RIGGING_PREDECESSOR_HEAD,
        "source_owner_head": predecessor.SOURCE_OWNER_HEAD,
        "source_digest": predecessor.EXPECTED_SOURCE_DIGEST,
        "geometry_receiver_mesh_digest": predecessor.EXPECTED_MIGRATED_MESH_DIGEST,
        "branch_id": predecessor.CHILD_BRANCH_ID,
        "expected": {
            "selected_vertices": EXPECTED_SELECTED_VERTICES,
            "selected_triangles": EXPECTED_SELECTED_TRIANGLES,
            "edge_connected_components": EXPECTED_COMPONENT_COUNT,
            "closed_edge_manifold_components": EXPECTED_CLOSED_COMPONENTS,
            "open_components": EXPECTED_OPEN_COMPONENTS,
            "shared_indexed_vertices_with_trunk": EXPECTED_SHARED_INDEXED_VERTICES,
            "root_branch_segment": dict(EXPECTED_ROOT_SEGMENT),
        },
        "reusable_rule": "SPATIAL_OR_RIGGING_ATTACHMENT_EVIDENCE_MUST_DECLARE_INDEXED_CONNECTIVITY_CLASS_BEFORE_CONNECTED_TOPOLOGY_PASS_TRANSFER",
        "truth_boundary": {
            "mutates_source": False,
            "mutates_rigging": False,
            "proves_connected_branch_trunk_attachment": False,
            "proves_production_topology": False,
            "proves_skinning": False,
            "proves_target_host_or_runtime": False,
            "proves_collision_or_gameplay": False,
            "claims_canon_or_production_readiness": False,
        },
    }


def _canonical_digest(value) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def evaluate(
    source: dict,
    geometry_contract: dict,
    *,
    requested_rigging_predecessor_head: str = RIGGING_PREDECESSOR_HEAD,
    requested_geometry_donor_head: str = GEOMETRY_ATTACHMENT_DONOR_HEAD,
    claim_connected_branch_trunk_attachment: bool = False,
    claim_production_skinning: bool = False,
    claim_production_parent_weight: bool = False,
    claim_animation_acceptance: bool = False,
    claim_technical_art_acceptance: bool = False,
    claim_runtime_acceptance: bool = False,
) -> dict:
    """Bind the exact Geometry attachment class to the existing Rigging socket policy."""
    if requested_rigging_predecessor_head != RIGGING_PREDECESSOR_HEAD:
        raise ValueError("exact Rigging predecessor head drift")
    if requested_geometry_donor_head != GEOMETRY_ATTACHMENT_DONOR_HEAD:
        raise ValueError("exact Geometry attachment donor head drift")
    if claim_connected_branch_trunk_attachment:
        raise ValueError("detached diagnostic child may not be promoted to connected branch/trunk attachment")
    if claim_production_skinning:
        raise ValueError("attachment representation gate is not production skinning acceptance")
    if claim_production_parent_weight:
        raise ValueError("diagnostic parent weight zero is not a production weight")
    if claim_animation_acceptance:
        raise ValueError("Rigging evidence cannot claim Animation acceptance")
    if claim_technical_art_acceptance:
        raise ValueError("Rigging evidence cannot claim Technical Art target-host acceptance")
    if claim_runtime_acceptance:
        raise ValueError("Rigging evidence cannot claim Runtime acceptance")

    exact_geometry = expected_geometry_contract()
    if geometry_contract != exact_geometry:
        raise ValueError("exact Geometry attachment contract drift")

    prior = predecessor.evaluate(source)
    if prior["result"] != predecessor.RESULT:
        raise ValueError("north-low parent-influence predecessor no longer passes")
    if prior["rigging_constraint"]["upper_trunk_parent_influence_enabled_for_north_low"] is not False:
        raise ValueError("north-low parent-influence exclusion state drift")
    if prior["rigging_constraint"]["diagnostic_parent_weight"] != 0.0:
        raise ValueError("north-low diagnostic parent weight drift")

    topology = geometry_contract["expected"]
    if topology["shared_indexed_vertices_with_trunk"] != 0:
        raise ValueError("Geometry no longer reports a detached indexed branch/trunk receiver")
    if topology["edge_connected_components"] != EXPECTED_COMPONENT_COUNT:
        raise ValueError("north-low Geometry component count drift")
    if topology["root_branch_segment"] != EXPECTED_ROOT_SEGMENT:
        raise ValueError("north-low root segment topology identity drift")

    witness_digest = _canonical_digest(prior["witnesses"])
    measurements = prior["measurements"]
    if measurements["representative_parent_child_pose_count"] != 9:
        raise ValueError("north-low representative pose schedule drift")
    if measurements["maximum_gated_parent_command_leak_m"] > predecessor.TOL:
        raise ValueError("parent command leaked through preserved exclusion gate")
    if measurements["maximum_gated_rigid_child_pairwise_distance_drift_m"] > predecessor.TOL:
        raise ValueError("preserved child rigid transform drift")

    checks = {
        "exact_rigging_predecessor_reexecuted": prior["result"] == predecessor.RESULT,
        "exact_geometry_contract_consumed_without_topology_recomputation": geometry_contract == exact_geometry,
        "north_low_child_is_detached_from_trunk_by_index_identity": topology["shared_indexed_vertices_with_trunk"] == 0,
        "north_low_child_component_class_preserved": topology["edge_connected_components"] == 6,
        "existing_socket_identity_preserved": prior["child_socket"]["branch_id"] == predecessor.CHILD_BRANCH_ID,
        "existing_parent_exclusion_preserved": prior["rigging_constraint"]["diagnostic_parent_weight"] == 0.0,
        "representative_pose_field_preserved": measurements["representative_parent_child_pose_count"] == 9,
        "continuous_transform_domain_remains_diagnostic_only": prior["continuous_product_domain_certificate"]["continuous_for_every_real_parent_child_pair_under_gate"] is True,
    }
    if not all(checks.values()):
        raise ValueError(f"north-low attachment representation gate invariant failed: {checks}")

    return {
        "schema": SCHEMA,
        "result": RESULT,
        "study_id": predecessor.STUDY_ID,
        "source_owner_head": predecessor.SOURCE_OWNER_HEAD,
        "source_digest": predecessor.EXPECTED_SOURCE_DIGEST,
        "geometry_receiver_head": prior["geometry_receiver_head"],
        "geometry_receiver_mesh_digest": predecessor.EXPECTED_MIGRATED_MESH_DIGEST,
        "rigging_predecessor_head": RIGGING_PREDECESSOR_HEAD,
        "geometry_attachment_donor_head": GEOMETRY_ATTACHMENT_DONOR_HEAD,
        "geometry_attachment_contract_blob": GEOMETRY_ATTACHMENT_CONTRACT_BLOB,
        "geometry_attachment_observer_blob": GEOMETRY_ATTACHMENT_OBSERVER_BLOB,
        "geometry_result_consumed": GEOMETRY_RESULT,
        "geometry_contract_digest": _canonical_digest(geometry_contract),
        "attachment_representation_constraint": {
            "mode": "DETACHED_DIAGNOSTIC_CHILD_SOCKET_ONLY",
            "branch_id": predecessor.CHILD_BRANCH_ID,
            "indexed_branch_trunk_connection_proven": False,
            "production_connected_skinning_allowed": False,
            "upper_trunk_parent_influence_enabled": False,
            "diagnostic_parent_weight": 0.0,
            "reopen_condition": "a new exact Geometry/source receiver proves a connected attachment identity and Rigging explicitly rebinds it",
        },
        "geometry_attachment_class": {
            "selected_vertices": topology["selected_vertices"],
            "selected_triangles": topology["selected_triangles"],
            "edge_connected_components": topology["edge_connected_components"],
            "closed_edge_manifold_components": topology["closed_edge_manifold_components"],
            "open_components": topology["open_components"],
            "shared_indexed_vertices_with_trunk": topology["shared_indexed_vertices_with_trunk"],
            "root_branch_segment": topology["root_branch_segment"],
        },
        "preserved_rigging_motion_evidence": {
            "parent_domain_deg": prior["continuous_product_domain_certificate"]["parent_domain_deg"],
            "child_domain_deg": prior["continuous_product_domain_certificate"]["child_domain_deg"],
            "representative_parent_child_pose_count": measurements["representative_parent_child_pose_count"],
            "maximum_gated_parent_command_leak_m": measurements["maximum_gated_parent_command_leak_m"],
            "maximum_gated_rigid_child_pairwise_distance_drift_m": measurements["maximum_gated_rigid_child_pairwise_distance_drift_m"],
            "maximum_counterfactual_inherited_parent_socket_travel_m": measurements["maximum_counterfactual_inherited_parent_socket_travel_m"],
            "maximum_counterfactual_inherited_output_delta_m": measurements["maximum_counterfactual_inherited_output_delta_m"],
            "witness_digest": witness_digest,
            "continuous_transform_domain_preserved": True,
            "connected_surface_continuity_proven": False,
        },
        "checks": checks,
        "truth_boundary": {
            "source_or_geometry_mutated": False,
            "socket_pivot_axis_or_angle_domain_changed": False,
            "production_parent_weight_claimed": False,
            "connected_branch_trunk_attachment_claimed": False,
            "production_skinning_claimed": False,
            "botanical_or_strength_validity_claimed": False,
            "continuous_collision_or_surface_continuity_claimed": False,
            "animation_timing_interpolation_or_playback_claimed": False,
            "technical_art_target_host_claimed": False,
            "runtime_controller_or_device_claimed": False,
            "art_or_visual_qa_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }

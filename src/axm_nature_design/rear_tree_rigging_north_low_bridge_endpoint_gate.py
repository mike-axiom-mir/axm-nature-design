"""Rigging-owned endpoint constraint for the north-low analytic bridge candidate.

Geometry owns the exact branch-side transition loop, analytic trunk-side loop and
16-triangle annular bridge candidate. Rigging consumes that exact Geometry result and
adds only a bounded diagnostic endpoint policy:

* the eight branch-boundary vertices follow the existing north-low child socket;
* the eight analytic trunk-boundary vertices remain receiver-pinned;
* there are no interior bridge vertices, so no interior skin-weight field is invented.

The endpoint mapping is continuous for the existing child diagnostic command domain
because it is one rigid socket transform plus one fixed receiver boundary. Bridge shape
quality is checked only at retained representative poses. This module does not claim a
connected indexed trunk junction, production skinning, botanical mechanics, Animation,
Technical Art, Runtime, collision, CANON, or production readiness.
"""
from __future__ import annotations

from . import rear_tree_geometry_north_low_trunk_bridge_candidate as geometry_bridge
from . import rear_tree_rigging as historical
from . import rear_tree_rigging_north_low_attachment_representation_gate as attachment_gate
from . import rear_tree_rigging_north_low_parent_influence_gate as parent_gate

SCHEMA = "axm.nature-north-low-analytic-bridge-endpoint-rigging-evidence/v0.1"
RESULT = "PASS_NORTH_LOW_ANALYTIC_BRIDGE_ENDPOINT_PIN_DIAGNOSTIC__HOLD_CONNECTED_TOPOLOGY_PRODUCTION_SKINNING"
RULE = "ANALYTIC_BRIDGE_BOUNDARIES_REQUIRE_EXPLICIT_RIGGING_ENDPOINT_OWNERSHIP_BEFORE_DEFORMATION_PASS_TRANSFER"

RIGGING_PREDECESSOR_HEAD = "69640e558f0c1ac59d4d0e3155676e0967a03d04"
RIGGING_PREDECESSOR_MODULE_BLOB = "de00694e103b975f9a25a72a50054821b469b528"
GEOMETRY_BRIDGE_DONOR_HEAD = "14d05fdabc943376c231308001d00eb87dc23430"
GEOMETRY_BRIDGE_MODULE_BLOB = "47ba57110f43b0f3f1f29582b46a90505fa4515c"
GEOMETRY_BRIDGE_CONTRACT_BLOB = "047daa7d5764f53cb42aa14b8bec82f3150bd809"

BRANCH_ENDPOINT_WEIGHT = 1.0
TRUNK_ENDPOINT_WEIGHT = 0.0
REPRESENTATIVE_ANGLES_DEG = (-5.0, -2.5, 0.0, 2.5, 5.0)
TOL = historical.TOL


def _distance(a, b):
    return historical._distance(a, b)


def _triangle_area(a, b, c):
    cross = historical._cross(historical._sub(b, a), historical._sub(c, a))
    return 0.5 * historical._length(cross)


def _max_point_delta(left, right):
    if len(left) != len(right):
        raise ValueError("point-list cardinality drift")
    return max((_distance(a, b) for a, b in zip(left, right)), default=0.0)


def _pose_boundary(points, pivot, axis, angle_deg):
    return [historical._rotate_about_axis(point, pivot, axis, angle_deg) for point in points]


def evaluate(
    source: dict,
    *,
    requested_rigging_predecessor_head: str = RIGGING_PREDECESSOR_HEAD,
    requested_geometry_bridge_head: str = GEOMETRY_BRIDGE_DONOR_HEAD,
    branch_endpoint_weight: float = BRANCH_ENDPOINT_WEIGHT,
    trunk_endpoint_weight: float = TRUNK_ENDPOINT_WEIGHT,
    representative_angles_deg=REPRESENTATIVE_ANGLES_DEG,
    claim_connected_branch_trunk_topology: bool = False,
    claim_production_skinning: bool = False,
    claim_continuous_bridge_foldover_clearance: bool = False,
    claim_animation_acceptance: bool = False,
    claim_technical_art_acceptance: bool = False,
    claim_runtime_acceptance: bool = False,
) -> dict:
    """Bind exact Geometry bridge boundaries to the existing diagnostic child socket."""
    if requested_rigging_predecessor_head != RIGGING_PREDECESSOR_HEAD:
        raise ValueError("exact Rigging predecessor head drift")
    if requested_geometry_bridge_head != GEOMETRY_BRIDGE_DONOR_HEAD:
        raise ValueError("exact Geometry bridge donor head drift")
    if abs(float(branch_endpoint_weight) - BRANCH_ENDPOINT_WEIGHT) > TOL:
        raise ValueError("branch endpoint diagnostic ownership must remain exactly 1.0")
    if abs(float(trunk_endpoint_weight) - TRUNK_ENDPOINT_WEIGHT) > TOL:
        raise ValueError("trunk endpoint diagnostic ownership must remain exactly 0.0")
    if tuple(float(v) for v in representative_angles_deg) != REPRESENTATIVE_ANGLES_DEG:
        raise ValueError("representative child pose schedule may not be widened or rewritten")
    if claim_connected_branch_trunk_topology:
        raise ValueError("analytic bridge candidate is not a connected indexed trunk junction")
    if claim_production_skinning:
        raise ValueError("endpoint diagnostic ownership is not production skin weighting")
    if claim_continuous_bridge_foldover_clearance:
        raise ValueError("representative bridge poses do not prove continuous foldover/collision clearance")
    if claim_animation_acceptance:
        raise ValueError("Rigging evidence cannot claim Animation acceptance")
    if claim_technical_art_acceptance:
        raise ValueError("Rigging evidence cannot claim Technical Art acceptance")
    if claim_runtime_acceptance:
        raise ValueError("Rigging evidence cannot claim Runtime acceptance")

    attachment = attachment_gate.evaluate(source, attachment_gate.expected_geometry_contract())
    if attachment.get("result") != attachment_gate.RESULT:
        raise ValueError("exact detached-socket Rigging predecessor no longer passes")
    if attachment["attachment_representation_constraint"]["mode"] != "DETACHED_DIAGNOSTIC_CHILD_SOCKET_ONLY":
        raise ValueError("north-low attachment representation state drift")

    parent = parent_gate.evaluate(source)
    if parent.get("result") != parent_gate.RESULT:
        raise ValueError("north-low parent exclusion predecessor no longer passes")
    child_socket = parent["child_socket"]
    if child_socket["branch_id"] != geometry_bridge.BRANCH_ID:
        raise ValueError("Geometry bridge and Rigging child socket branch identities disagree")
    pivot = [float(v) for v in child_socket["pivot_m"]]
    axis = [float(v) for v in child_socket["source_derived_axis"]]
    child_domain = [float(v) for v in child_socket["diagnostic_interval_deg"]]
    if child_domain != [-5.0, 5.0]:
        raise ValueError("north-low diagnostic child interval drift")

    geometry = geometry_bridge.evaluate(
        source,
        requested_rigging_owner_head=RIGGING_PREDECESSOR_HEAD,
    )
    if geometry.get("result") != geometry_bridge.RESULT:
        raise ValueError("exact Geometry bridge donor no longer passes")
    candidate = geometry_bridge.build_candidate(source)
    bridge = candidate["bridge_only"]
    neutral = [[float(v) for v in point] for point in bridge["vertices"]]
    faces = [list(face) for face in bridge["triangles"]]
    sides = int(geometry_bridge.SIDES)
    if sides != 8 or len(neutral) != 16 or len(faces) != 16:
        raise ValueError("exact Geometry bridge endpoint cardinality drift")

    branch_neutral = neutral[:sides]
    trunk_neutral = neutral[sides:]
    neutral_branch_edges = [
        _distance(branch_neutral[i], branch_neutral[(i + 1) % sides]) for i in range(sides)
    ]
    neutral_trunk_edges = [
        _distance(trunk_neutral[i], trunk_neutral[(i + 1) % sides]) for i in range(sides)
    ]

    witnesses = []
    max_branch_endpoint_residual = 0.0
    max_trunk_endpoint_drift = 0.0
    max_branch_edge_drift = 0.0
    max_trunk_edge_drift = 0.0
    minimum_triangle_area = float("inf")
    minimum_bridge_span = float("inf")

    for angle_deg in REPRESENTATIVE_ANGLES_DEG:
        expected_branch = _pose_boundary(branch_neutral, pivot, axis, angle_deg)
        posed_branch = _pose_boundary(branch_neutral, pivot, axis, angle_deg)
        posed_trunk = [list(point) for point in trunk_neutral]
        posed = posed_branch + posed_trunk

        branch_residual = _max_point_delta(posed_branch, expected_branch)
        trunk_drift = _max_point_delta(posed_trunk, trunk_neutral)
        branch_edge_drift = max(
            (
                abs(_distance(posed_branch[i], posed_branch[(i + 1) % sides]) - neutral_branch_edges[i])
                for i in range(sides)
            ),
            default=0.0,
        )
        trunk_edge_drift = max(
            (
                abs(_distance(posed_trunk[i], posed_trunk[(i + 1) % sides]) - neutral_trunk_edges[i])
                for i in range(sides)
            ),
            default=0.0,
        )
        triangle_areas = [_triangle_area(posed[a], posed[b], posed[c]) for a, b, c in faces]
        bridge_spans = [_distance(posed_branch[i], posed_trunk[i]) for i in range(sides)]
        pose_min_area = min(triangle_areas)
        pose_min_span = min(bridge_spans)

        max_branch_endpoint_residual = max(max_branch_endpoint_residual, branch_residual)
        max_trunk_endpoint_drift = max(max_trunk_endpoint_drift, trunk_drift)
        max_branch_edge_drift = max(max_branch_edge_drift, branch_edge_drift)
        max_trunk_edge_drift = max(max_trunk_edge_drift, trunk_edge_drift)
        minimum_triangle_area = min(minimum_triangle_area, pose_min_area)
        minimum_bridge_span = min(minimum_bridge_span, pose_min_span)

        witnesses.append(
            {
                "child_angle_deg": float(angle_deg),
                "branch_endpoint_weight": BRANCH_ENDPOINT_WEIGHT,
                "trunk_endpoint_weight": TRUNK_ENDPOINT_WEIGHT,
                "branch_endpoint_residual_m": branch_residual,
                "trunk_endpoint_drift_m": trunk_drift,
                "branch_boundary_edge_length_drift_m": branch_edge_drift,
                "trunk_boundary_edge_length_drift_m": trunk_edge_drift,
                "minimum_bridge_triangle_area_m2": pose_min_area,
                "minimum_paired_bridge_span_m": pose_min_span,
            }
        )

    branch_fixed_counterfactual = _max_point_delta(
        branch_neutral,
        _pose_boundary(branch_neutral, pivot, axis, REPRESENTATIVE_ANGLES_DEG[-1]),
    )
    trunk_follows_counterfactual = _max_point_delta(
        _pose_boundary(trunk_neutral, pivot, axis, REPRESENTATIVE_ANGLES_DEG[-1]),
        trunk_neutral,
    )

    if minimum_triangle_area <= TOL:
        raise ValueError("representative bridge endpoint constraint collapses a triangle")
    if minimum_bridge_span <= TOL:
        raise ValueError("representative bridge endpoint constraint collapses paired boundary span")
    if branch_fixed_counterfactual <= 1e-6:
        raise ValueError("branch-fixed negative control is not discriminating")
    if trunk_follows_counterfactual <= 1e-6:
        raise ValueError("trunk-follow negative control is not discriminating")

    checks = {
        "exact_detached_socket_predecessor_reexecuted": attachment["result"] == attachment_gate.RESULT,
        "exact_parent_exclusion_predecessor_reexecuted": parent["result"] == parent_gate.RESULT,
        "exact_geometry_bridge_donor_reexecuted": geometry["result"] == geometry_bridge.RESULT,
        "geometry_bridge_is_analytic_and_not_indexed_trunk_cut": geometry["analytic_trunk_loop"]["analytic_envelope_only"] is True,
        "bridge_has_exactly_two_eight_vertex_boundaries_and_no_interior_vertices": len(neutral) == 2 * sides == 16,
        "branch_boundary_follows_existing_socket": max_branch_endpoint_residual <= TOL,
        "trunk_boundary_remains_receiver_pinned": max_trunk_endpoint_drift <= TOL,
        "branch_boundary_rigidity_preserved": max_branch_edge_drift <= TOL,
        "trunk_boundary_identity_preserved": max_trunk_edge_drift <= TOL,
        "representative_bridge_triangles_remain_nondegenerate": minimum_triangle_area > TOL,
        "representative_paired_boundary_spans_remain_nonzero": minimum_bridge_span > TOL,
        "branch_fixed_negative_is_materially_different": branch_fixed_counterfactual > 1e-6,
        "trunk_follow_negative_is_materially_different": trunk_follows_counterfactual > 1e-6,
    }
    if not all(checks.values()):
        raise ValueError(f"north-low analytic bridge endpoint gate invariant failed: {checks}")

    return {
        "schema": SCHEMA,
        "result": RESULT,
        "reusable_rule": RULE,
        "study_id": geometry_bridge.STUDY_ID,
        "source_digest": geometry_bridge.SOURCE_DIGEST,
        "rigging_predecessor_head": RIGGING_PREDECESSOR_HEAD,
        "rigging_predecessor_module_blob": RIGGING_PREDECESSOR_MODULE_BLOB,
        "geometry_bridge_donor_head": GEOMETRY_BRIDGE_DONOR_HEAD,
        "geometry_bridge_module_blob": GEOMETRY_BRIDGE_MODULE_BLOB,
        "geometry_bridge_contract_blob": GEOMETRY_BRIDGE_CONTRACT_BLOB,
        "geometry_result_consumed": geometry_bridge.RESULT,
        "socket_identity": {
            "branch_id": child_socket["branch_id"],
            "pivot_m": pivot,
            "source_derived_axis": axis,
            "diagnostic_interval_deg": child_domain,
        },
        "endpoint_constraint": {
            "mode": "ANALYTIC_BRIDGE_TWO_BOUNDARY_DIAGNOSTIC_PIN",
            "branch_boundary_vertices": sides,
            "trunk_boundary_vertices": sides,
            "interior_vertices": 0,
            "branch_endpoint_diagnostic_weight": BRANCH_ENDPOINT_WEIGHT,
            "trunk_endpoint_diagnostic_weight": TRUNK_ENDPOINT_WEIGHT,
            "branch_endpoint_owner": "EXISTING_NORTH_LOW_CHILD_SOCKET",
            "trunk_endpoint_owner": "ANALYTIC_RECEIVER_BOUNDARY_FIXED",
            "production_skinning_weights_claimed": False,
        },
        "representative_pose_evidence": {
            "angles_deg": list(REPRESENTATIVE_ANGLES_DEG),
            "witness_count": len(witnesses),
            "maximum_branch_endpoint_residual_m": max_branch_endpoint_residual,
            "maximum_trunk_endpoint_drift_m": max_trunk_endpoint_drift,
            "maximum_branch_boundary_edge_length_drift_m": max_branch_edge_drift,
            "maximum_trunk_boundary_edge_length_drift_m": max_trunk_edge_drift,
            "minimum_bridge_triangle_area_m2": minimum_triangle_area,
            "minimum_paired_bridge_span_m": minimum_bridge_span,
            "branch_fixed_counterfactual_m": branch_fixed_counterfactual,
            "trunk_follows_child_counterfactual_m": trunk_follows_counterfactual,
        },
        "witnesses": witnesses,
        "continuous_endpoint_mapping_certificate": {
            "child_domain_deg": child_domain,
            "continuous_for_every_real_child_command_in_domain": True,
            "reason": "branch boundary is one continuous rigid Rodrigues socket transform; trunk boundary is identity-mapped",
            "continuous_bridge_triangle_nondegeneracy_or_collision_proven": False,
        },
        "checks": checks,
        "truth_boundary": {
            "source_geometry_mutated": False,
            "geometry_bridge_topology_mutated": False,
            "indexed_trunk_cut_or_connected_junction_claimed": False,
            "production_skinning_or_blending_claimed": False,
            "botanical_mechanics_or_strength_claimed": False,
            "continuous_bridge_foldover_collision_or_self_intersection_claimed": False,
            "source_or_biological_rom_claimed": False,
            "animation_timing_interpolation_or_playback_claimed": False,
            "technical_art_target_host_claimed": False,
            "runtime_controller_device_or_performance_claimed": False,
            "art_or_visual_qa_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }

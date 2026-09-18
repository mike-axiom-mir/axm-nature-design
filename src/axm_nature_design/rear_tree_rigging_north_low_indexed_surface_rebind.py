"""Rigging rebind of north-low endpoint ownership to Geometry's indexed receiver.

Geometry PR #30 moves the diagnostic trunk-side bridge loop from the smooth analytic
trunk envelope onto exact indexed receiver faces. That changes the fixed endpoints, so
the earlier analytic Rigging span certificate cannot transfer silently.

This successor keeps the existing north-low child socket, pivot, axis, endpoint weights
and [-5,+5] degree diagnostic domain unchanged. It consumes an exact Geometry-owned
report/candidate, proves representative pose behavior, and re-certifies all eight
moving-to-fixed paired spans continuously with the predecessor stationary-point method.
"""
from __future__ import annotations

from . import rear_tree_rigging_north_low_bridge_continuous_span as analytic_span

SCHEMA = "axm.nature-north-low-indexed-surface-rigging-rebind-evidence/v0.1"
RESULT = "PASS_NORTH_LOW_INDEXED_SURFACE_RECEIVER_RIGGING_REBIND_AND_CONTINUOUS_PAIRED_SPAN_NONCOLLAPSE_MINUS5_TO_PLUS5__HOLD_INDEXED_CUT_CONNECTED_JUNCTION_TRIANGLE_FOLDOVER_COLLISION"
RULE = "GEOMETRY_RECEIVER_IDENTITY_CHANGE_REQUIRES_EXPLICIT_RIGGING_ENDPOINT_REBIND_BEFORE_DEFORMATION_PASS_TRANSFER"
CONSTRAINT = "INDEXED_SURFACE_RECEIVER_PIN_WITH_CONTINUOUS_PAIRED_SPAN_CERTIFICATE"
RIGGING_PREDECESSOR_HEAD = "efe99261459858636dbe65b16cbe1d5ad2b93a56"
RIGGING_PREDECESSOR_MODULE_BLOB = "96e9078afc9925dd9261ca9b3c03939fbd0e7aa2"
GEOMETRY_DONOR_HEAD = "8ab552710df21567cfd601af99181918e2cfadb3"
GEOMETRY_DONOR_MODULE_BLOB = "af43e49bf6f14c050a3930d3258bc4ee50c0a9f3"
GEOMETRY_DONOR_CONTRACT_BLOB = "081e2a610a6938cb12c501b7f8a907e590a7214c"
GEOMETRY_DONOR_RESULT = "PASS_NORTH_LOW_EXACT_INDEXED_TRUNK_SURFACE_REBIND__HOLD_INDEXED_CUT_CONNECTED_JUNCTION"
SOURCE_BLOB = analytic_span.SOURCE_BLOB
DOMAIN_DEG = analytic_span.DOMAIN_DEG
REPRESENTATIVE_ANGLES_DEG = analytic_span.REPRESENTATIVE_ANGLES_DEG
BRANCH_ENDPOINT_WEIGHT = 1.0
TRUNK_ENDPOINT_WEIGHT = 0.0
TOL = analytic_span.TOL


def _distance(a, b):
    return analytic_span._distance(a, b)


def _triangle_area(a, b, c):
    h = analytic_span.endpoint_gate.historical
    return 0.5 * h._length(h._cross(h._sub(b, a), h._sub(c, a)))


def _max_point_delta(left, right):
    if len(left) != len(right):
        raise ValueError("point-list cardinality drift")
    return max((_distance(a, b) for a, b in zip(left, right)), default=0.0)


def _geometry_truth_gate(report: dict) -> None:
    if report.get("result") != GEOMETRY_DONOR_RESULT:
        raise ValueError("exact indexed-surface Geometry donor result drift")
    truth = report.get("truth_boundary", {})
    if truth.get("neutral_indexed_surface_membership_proven") is not True:
        raise ValueError("Geometry donor no longer proves indexed-surface membership")
    if truth.get("indexed_trunk_cut_integrated") is not False:
        raise ValueError("Geometry donor unexpectedly promotes indexed trunk cutting")
    if truth.get("connected_branch_trunk_indexed_topology_proven") is not False:
        raise ValueError("Geometry donor unexpectedly promotes connected topology")
    if truth.get("analytic_rigging_pass_transferred") is not False:
        raise ValueError("Geometry donor must not transfer Rigging acceptance")
    binding = report.get("indexed_surface_binding", {})
    if binding.get("loop_vertices") != 8 or len(binding.get("memberships", [])) != 8:
        raise ValueError("Geometry donor indexed loop cardinality drift")
    if binding.get("parameter_space_self_intersections") != 0:
        raise ValueError("Geometry donor indexed loop self-intersection drift")


def evaluate(
    source: dict,
    geometry_report: dict,
    geometry_candidate: dict,
    *,
    requested_rigging_predecessor_head: str = RIGGING_PREDECESSOR_HEAD,
    requested_geometry_donor_head: str = GEOMETRY_DONOR_HEAD,
    requested_geometry_donor_module_blob: str = GEOMETRY_DONOR_MODULE_BLOB,
    requested_domain_deg=DOMAIN_DEG,
    branch_endpoint_weight: float = BRANCH_ENDPOINT_WEIGHT,
    trunk_endpoint_weight: float = TRUNK_ENDPOINT_WEIGHT,
    claim_indexed_trunk_cut_integrated: bool = False,
    claim_connected_topology: bool = False,
    claim_continuous_triangle_nondegeneracy: bool = False,
    claim_continuous_foldover_or_collision_clearance: bool = False,
    claim_production_skinning: bool = False,
    claim_animation_acceptance: bool = False,
    claim_technical_art_acceptance: bool = False,
    claim_runtime_acceptance: bool = False,
) -> dict:
    if requested_rigging_predecessor_head != RIGGING_PREDECESSOR_HEAD:
        raise ValueError("exact Rigging predecessor head drift")
    if requested_geometry_donor_head != GEOMETRY_DONOR_HEAD:
        raise ValueError("exact indexed-surface Geometry donor head drift")
    if requested_geometry_donor_module_blob != GEOMETRY_DONOR_MODULE_BLOB:
        raise ValueError("exact indexed-surface Geometry donor module blob drift")
    domain = tuple(float(v) for v in requested_domain_deg)
    if domain != DOMAIN_DEG:
        raise ValueError("indexed receiver rebind may not widen or rewrite the child domain")
    if abs(float(branch_endpoint_weight) - BRANCH_ENDPOINT_WEIGHT) > TOL:
        raise ValueError("branch endpoint diagnostic ownership must remain exactly 1.0")
    if abs(float(trunk_endpoint_weight) - TRUNK_ENDPOINT_WEIGHT) > TOL:
        raise ValueError("trunk endpoint diagnostic ownership must remain exactly 0.0")
    if claim_indexed_trunk_cut_integrated:
        raise ValueError("indexed receiver rebind does not cut the trunk")
    if claim_connected_topology:
        raise ValueError("indexed receiver rebind does not prove connected topology")
    if claim_continuous_triangle_nondegeneracy:
        raise ValueError("paired-span proof does not prove continuous triangle nondegeneracy")
    if claim_continuous_foldover_or_collision_clearance:
        raise ValueError("paired-span proof does not prove foldover/collision clearance")
    if claim_production_skinning:
        raise ValueError("diagnostic endpoint ownership is not production skinning")
    if claim_animation_acceptance:
        raise ValueError("Rigging evidence cannot claim Animation acceptance")
    if claim_technical_art_acceptance:
        raise ValueError("Rigging evidence cannot claim Technical Art acceptance")
    if claim_runtime_acceptance:
        raise ValueError("Rigging evidence cannot claim Runtime acceptance")

    predecessor = analytic_span.evaluate(source)
    if predecessor.get("result") != analytic_span.RESULT:
        raise ValueError("exact analytic Rigging predecessor no longer passes")
    if predecessor["continuous_paired_span_certificate"]["child_domain_deg"] != list(DOMAIN_DEG):
        raise ValueError("analytic Rigging predecessor domain drift")

    _geometry_truth_gate(geometry_report)
    if geometry_report.get("source_digest") != predecessor.get("source_digest"):
        raise ValueError("Geometry donor source identity disagrees with Rigging predecessor")
    donor_provenance = geometry_report.get("provenance", {})
    if donor_provenance.get("rigging_owner_head") != RIGGING_PREDECESSOR_HEAD:
        raise ValueError("Geometry donor was not bound to the exact Rigging predecessor")

    bridge = geometry_candidate.get("bridge_only", {})
    neutral = [[float(v) for v in point] for point in bridge.get("vertices", [])]
    faces = [list(face) for face in bridge.get("triangles", [])]
    sides = 8
    if len(neutral) != 16 or len(faces) != 16:
        raise ValueError("indexed Geometry bridge cardinality drift")
    if any(len(face) != 3 or min(face) < 0 or max(face) >= 16 for face in faces):
        raise ValueError("indexed Geometry bridge triangle index drift")
    branch_neutral = neutral[:sides]
    trunk_neutral = neutral[sides:]

    analytic_candidate = analytic_span.endpoint_gate.geometry_bridge.build_candidate(source)
    analytic_neutral = [[float(v) for v in point] for point in analytic_candidate["bridge_only"]["vertices"]]
    if len(analytic_neutral) != 16:
        raise ValueError("analytic predecessor bridge cardinality drift")
    analytic_branch = analytic_neutral[:sides]
    analytic_trunk = analytic_neutral[sides:]
    branch_rebind_delta = _max_point_delta(branch_neutral, analytic_branch)
    receiver_surface_deltas = [_distance(a, b) for a, b in zip(trunk_neutral, analytic_trunk)]
    minimum_receiver_rebind_delta = min(receiver_surface_deltas)
    maximum_receiver_rebind_delta = max(receiver_surface_deltas)
    if branch_rebind_delta > TOL:
        raise ValueError("indexed Geometry donor changed Rigging-owned branch endpoints")
    if minimum_receiver_rebind_delta <= 1e-6:
        raise ValueError("indexed receiver rebind is not materially distinct from analytic receiver")

    socket = predecessor["socket_identity"]
    pivot = [float(v) for v in socket["pivot_m"]]
    axis = [float(v) for v in socket["source_derived_axis"]]
    if [float(v) for v in socket["diagnostic_interval_deg"]] != list(DOMAIN_DEG):
        raise ValueError("north-low socket interval drift")

    h = analytic_span.endpoint_gate.historical
    neutral_branch_edges = [_distance(branch_neutral[i], branch_neutral[(i + 1) % sides]) for i in range(sides)]
    neutral_trunk_edges = [_distance(trunk_neutral[i], trunk_neutral[(i + 1) % sides]) for i in range(sides)]
    witnesses = []
    max_branch_edge_drift = 0.0
    max_fixed_receiver_drift = 0.0
    max_trunk_edge_drift = 0.0
    representative_minimum_area = float("inf")
    representative_minimum_span = float("inf")

    for angle_deg in REPRESENTATIVE_ANGLES_DEG:
        posed_branch = [h._rotate_about_axis(p, pivot, axis, angle_deg) for p in branch_neutral]
        posed_trunk = [list(p) for p in trunk_neutral]
        posed = posed_branch + posed_trunk
        branch_edge_drift = max(abs(_distance(posed_branch[i], posed_branch[(i + 1) % sides]) - neutral_branch_edges[i]) for i in range(sides))
        trunk_edge_drift = max(abs(_distance(posed_trunk[i], posed_trunk[(i + 1) % sides]) - neutral_trunk_edges[i]) for i in range(sides))
        fixed_drift = _max_point_delta(posed_trunk, trunk_neutral)
        areas = [_triangle_area(posed[a], posed[b], posed[c]) for a, b, c in faces]
        spans = [_distance(posed_branch[i], posed_trunk[i]) for i in range(sides)]
        pose_min_area = min(areas)
        pose_min_span = min(spans)
        max_branch_edge_drift = max(max_branch_edge_drift, branch_edge_drift)
        max_fixed_receiver_drift = max(max_fixed_receiver_drift, fixed_drift)
        max_trunk_edge_drift = max(max_trunk_edge_drift, trunk_edge_drift)
        representative_minimum_area = min(representative_minimum_area, pose_min_area)
        representative_minimum_span = min(representative_minimum_span, pose_min_span)
        witnesses.append({
            "child_angle_deg": float(angle_deg),
            "branch_endpoint_weight": BRANCH_ENDPOINT_WEIGHT,
            "trunk_endpoint_weight": TRUNK_ENDPOINT_WEIGHT,
            "fixed_indexed_receiver_drift_m": fixed_drift,
            "branch_boundary_edge_length_drift_m": branch_edge_drift,
            "trunk_boundary_edge_length_drift_m": trunk_edge_drift,
            "minimum_bridge_triangle_area_m2": pose_min_area,
            "minimum_paired_bridge_span_m": pose_min_span,
        })

    pair_certificates = []
    global_minimum_span = float("inf")
    global_minimum_pair = None
    global_minimum_angle = None
    maximum_closed_form_residual = 0.0
    for index, (moving, fixed) in enumerate(zip(branch_neutral, trunk_neutral)):
        cert = analytic_span._continuous_minimum_span(moving, fixed, pivot, axis, *DOMAIN_DEG)
        k = cert["squared_span_coefficients"]["k"]
        a = cert["squared_span_coefficients"]["cosine"]
        b = cert["squared_span_coefficients"]["sine"]
        direct_witnesses = []
        for angle_deg in REPRESENTATIVE_ANGLES_DEG:
            posed = h._rotate_about_axis(moving, pivot, axis, angle_deg)
            direct = _distance(posed, fixed)
            closed = analytic_span.math.sqrt(analytic_span._squared_span_from_coefficients(k, a, b, analytic_span.math.radians(angle_deg)))
            residual = abs(direct - closed)
            maximum_closed_form_residual = max(maximum_closed_form_residual, residual)
            direct_witnesses.append({"child_angle_deg": float(angle_deg), "direct_span_m": direct, "closed_form_span_m": closed, "closed_form_residual_m": residual})
        row = {"pair_index": index, **cert, "representative_witnesses": direct_witnesses}
        pair_certificates.append(row)
        if cert["minimum_span_m"] < global_minimum_span:
            global_minimum_span = cert["minimum_span_m"]
            global_minimum_pair = index
            global_minimum_angle = cert["minimum_angle_deg"]

    if representative_minimum_area <= TOL:
        raise ValueError("representative indexed bridge pose collapses a triangle")
    if global_minimum_span <= TOL:
        raise ValueError("indexed receiver paired span collapses inside the child domain")
    if maximum_closed_form_residual > 1e-10:
        raise ValueError("indexed closed-form paired-span proof disagrees with direct poses")
    if global_minimum_span > representative_minimum_span + 1e-12:
        raise ValueError("continuous indexed span minimum cannot exceed retained representative minimum")

    checks = {
        "analytic_rigging_predecessor_reexecuted": predecessor["result"] == analytic_span.RESULT,
        "geometry_indexed_surface_membership_consumed_without_transfer": geometry_report["truth_boundary"]["analytic_rigging_pass_transferred"] is False,
        "branch_endpoint_identity_preserved": branch_rebind_delta <= TOL,
        "indexed_receiver_materially_differs_from_analytic_receiver": minimum_receiver_rebind_delta > 1e-6,
        "fixed_indexed_receiver_remains_identity_mapped": max_fixed_receiver_drift <= TOL,
        "branch_boundary_rigidity_preserved": max_branch_edge_drift <= TOL,
        "trunk_boundary_identity_preserved": max_trunk_edge_drift <= TOL,
        "five_representative_pose_triangles_nondegenerate": representative_minimum_area > TOL,
        "eight_continuous_paired_spans_strictly_positive": len(pair_certificates) == 8 and all(row["minimum_span_m"] > TOL for row in pair_certificates),
        "closed_form_matches_direct_representative_poses": maximum_closed_form_residual <= 1e-10,
        "continuous_minimum_not_hidden_by_sampling": global_minimum_span <= representative_minimum_span + 1e-12,
    }
    if not all(checks.values()):
        raise ValueError(f"indexed receiver Rigging rebind invariant failed: {checks}")

    return {
        "schema": SCHEMA,
        "result": RESULT,
        "reusable_rule": RULE,
        "constraint": CONSTRAINT,
        "study_id": predecessor["study_id"],
        "source_digest": predecessor["source_digest"],
        "provenance": {
            "rigging_predecessor_head": RIGGING_PREDECESSOR_HEAD,
            "rigging_predecessor_module_blob": RIGGING_PREDECESSOR_MODULE_BLOB,
            "geometry_indexed_surface_donor_head": GEOMETRY_DONOR_HEAD,
            "geometry_indexed_surface_module_blob": GEOMETRY_DONOR_MODULE_BLOB,
            "geometry_indexed_surface_contract_blob": GEOMETRY_DONOR_CONTRACT_BLOB,
            "source_blob": SOURCE_BLOB,
        },
        "socket_identity": socket,
        "receiver_rebind": {
            "branch_endpoint_delta_from_analytic_m": branch_rebind_delta,
            "minimum_fixed_receiver_delta_from_analytic_m": minimum_receiver_rebind_delta,
            "maximum_fixed_receiver_delta_from_analytic_m": maximum_receiver_rebind_delta,
            "fixed_receiver_kind": "EXACT_INDEXED_TRUNK_SURFACE_LOOP_FROM_GEOMETRY_DONOR",
            "indexed_trunk_cut_or_connected_junction": False,
        },
        "representative_pose_evidence": {
            "angles_deg": list(REPRESENTATIVE_ANGLES_DEG),
            "witness_count": len(witnesses),
            "maximum_fixed_indexed_receiver_drift_m": max_fixed_receiver_drift,
            "maximum_branch_boundary_edge_length_drift_m": max_branch_edge_drift,
            "maximum_trunk_boundary_edge_length_drift_m": max_trunk_edge_drift,
            "minimum_bridge_triangle_area_m2": representative_minimum_area,
            "minimum_paired_bridge_span_m": representative_minimum_span,
        },
        "continuous_paired_span_certificate": {
            "child_domain_deg": list(DOMAIN_DEG),
            "paired_span_count": 8,
            "global_minimum_span_m": global_minimum_span,
            "global_minimum_pair_index": global_minimum_pair,
            "global_minimum_angle_deg": global_minimum_angle,
            "representative_minimum_span_m": representative_minimum_span,
            "maximum_closed_form_vs_direct_residual_m": maximum_closed_form_residual,
            "continuous_for_every_real_child_command_in_domain": True,
            "proof_method": "stationary-point minimum of K + 2*A*cos(theta) + 2*B*sin(theta), rebound to Geometry's exact indexed fixed endpoints",
        },
        "witnesses": witnesses,
        "pair_certificates": pair_certificates,
        "checks": checks,
        "truth_boundary": {
            "source_geometry_mutated": False,
            "socket_pivot_axis_or_domain_mutated": False,
            "diagnostic_endpoint_weights_mutated": False,
            "geometry_receiver_topology_mutated_by_rigging": False,
            "indexed_trunk_cut_or_connected_junction_claimed": False,
            "production_skinning_or_blending_claimed": False,
            "continuous_triangle_nondegeneracy_claimed": False,
            "continuous_triangle_orientation_foldover_collision_or_self_intersection_claimed": False,
            "botanical_mechanics_or_biological_rom_claimed": False,
            "animation_timing_interpolation_or_playback_claimed": False,
            "technical_art_target_host_claimed": False,
            "runtime_controller_device_or_performance_claimed": False,
            "art_or_visual_qa_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }

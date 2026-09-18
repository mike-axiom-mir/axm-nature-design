"""Rigging-owned continuous non-collapse certificate for north-low bridge paired spans.

The predecessor Rigging gate owns the exact diagnostic endpoint mapping for Geometry's
16-vertex analytic bridge: eight branch-boundary vertices follow the existing north-low
socket while eight analytic trunk-boundary vertices stay fixed.  This successor proves
one narrower continuous property that the predecessor deliberately left sampled only:
each one-to-one branch/trunk connector span stays strictly non-zero for every real child
command in the already-owned [-5,+5] degree diagnostic interval.

For one moving branch endpoint p and fixed trunk endpoint q, Rodrigues rotation about
the exact socket axis makes squared span length

    d(theta)^2 = K + 2*A*cos(theta) + 2*B*sin(theta).

The minimum over the closed interval therefore occurs at an interval endpoint or at a
stationary angle atan2(B, A) + k*pi.  Evaluating that finite exact candidate set closes
the paired-span non-collapse question without pretending to prove continuous triangle
orientation, bridge foldover, collision/self-intersection freedom, connected topology,
production skinning, Animation, Technical Art, Runtime, CANON, or production readiness.
"""
from __future__ import annotations

import math

from . import rear_tree_rigging_north_low_bridge_endpoint_gate as endpoint_gate

SCHEMA = "axm.nature-north-low-analytic-bridge-continuous-paired-span-rigging-evidence/v0.1"
RESULT = "PASS_NORTH_LOW_ANALYTIC_BRIDGE_PAIRED_SPAN_CONTINUOUS_NONCOLLAPSE_MINUS5_TO_PLUS5__HOLD_TRIANGLE_FOLDOVER_COLLISION"
RULE = "RIGID_ENDPOINT_TO_FIXED_ENDPOINT_SPAN_MINIMUM_CAN_BE_CERTIFIED_CONTINUOUSLY_FROM_TRIGONOMETRIC_STATIONARY_POINTS"
CONSTRAINT = "ANALYTIC_BRIDGE_PAIRED_SPAN_CONTINUOUS_NONCOLLAPSE_CERTIFICATE"

RIGGING_ENDPOINT_PREDECESSOR_HEAD = "5ca11b1577b6f4f4a2ee2b34f08ae02aa23aa079"
RIGGING_ENDPOINT_MODULE_BLOB = "352e7c83e57779aef327390f5250875e26a7b610"
SOURCE_BLOB = "fb12b759e1abfd0455bf46fd39a0eba27095796b"
DOMAIN_DEG = (-5.0, 5.0)
REPRESENTATIVE_ANGLES_DEG = endpoint_gate.REPRESENTATIVE_ANGLES_DEG
TOL = endpoint_gate.TOL


def _dot(a, b):
    return sum(float(a[i]) * float(b[i]) for i in range(3))


def _sub(a, b):
    return [float(a[i]) - float(b[i]) for i in range(3)]


def _add(a, b):
    return [float(a[i]) + float(b[i]) for i in range(3)]


def _mul(a, scalar):
    return [float(a[i]) * float(scalar) for i in range(3)]


def _length(v):
    return math.sqrt(max(0.0, _dot(v, v)))


def _norm(v):
    size = _length(v)
    if size <= 1e-18:
        raise ValueError("zero-length axis")
    return [float(value) / size for value in v]


def _cross(a, b):
    return [
        float(a[1]) * float(b[2]) - float(a[2]) * float(b[1]),
        float(a[2]) * float(b[0]) - float(a[0]) * float(b[2]),
        float(a[0]) * float(b[1]) - float(a[1]) * float(b[0]),
    ]


def _distance(a, b):
    return _length(_sub(a, b))


def _squared_span_coefficients(moving, fixed, pivot, axis):
    """Return K,A,B for d(theta)^2 = K + 2*A*cos + 2*B*sin."""
    unit_axis = _norm(axis)
    radial = _sub(moving, pivot)
    parallel = _mul(unit_axis, _dot(radial, unit_axis))
    cosine_vector = _sub(radial, parallel)
    sine_vector = _cross(unit_axis, cosine_vector)
    constant_vector = _sub(_add(pivot, parallel), fixed)

    # For a unit axis, cosine_vector and sine_vector are orthogonal and equal length.
    orthogonality_residual = abs(_dot(cosine_vector, sine_vector))
    equal_length_residual = abs(_dot(cosine_vector, cosine_vector) - _dot(sine_vector, sine_vector))
    if max(orthogonality_residual, equal_length_residual) > 1e-10:
        raise ValueError("Rodrigues coefficient basis drift")

    k = _dot(cosine_vector, cosine_vector) + _dot(constant_vector, constant_vector)
    a = _dot(cosine_vector, constant_vector)
    b = _dot(sine_vector, constant_vector)
    return k, a, b


def _squared_span_from_coefficients(k, a, b, angle_rad):
    value = float(k) + 2.0 * float(a) * math.cos(angle_rad) + 2.0 * float(b) * math.sin(angle_rad)
    if value < -1e-12:
        raise ValueError("negative squared span beyond floating tolerance")
    return max(0.0, value)


def _critical_angles_rad(a, b, lower_rad, upper_rad):
    """Return all derivative-zero angles inside the closed interval."""
    if abs(a) <= 1e-18 and abs(b) <= 1e-18:
        return []
    base = math.atan2(float(b), float(a))
    first_k = math.floor((lower_rad - base) / math.pi) - 1
    last_k = math.ceil((upper_rad - base) / math.pi) + 1
    values = []
    for k in range(first_k, last_k + 1):
        theta = base + k * math.pi
        if lower_rad - 1e-15 <= theta <= upper_rad + 1e-15:
            values.append(max(lower_rad, min(upper_rad, theta)))
    return values


def _continuous_minimum_span(moving, fixed, pivot, axis, lower_deg, upper_deg):
    k, a, b = _squared_span_coefficients(moving, fixed, pivot, axis)
    lower_rad = math.radians(float(lower_deg))
    upper_rad = math.radians(float(upper_deg))
    if lower_rad >= upper_rad:
        raise ValueError("continuous child domain must have positive width")
    candidates = [lower_rad, upper_rad] + _critical_angles_rad(a, b, lower_rad, upper_rad)
    # Deduplicate only numerically identical candidate angles; no sampling is used.
    unique = []
    for value in sorted(candidates):
        if not unique or abs(value - unique[-1]) > 1e-14:
            unique.append(value)
    evaluations = [
        (theta, _squared_span_from_coefficients(k, a, b, theta)) for theta in unique
    ]
    theta, squared = min(evaluations, key=lambda item: item[1])
    return {
        "minimum_span_m": math.sqrt(squared),
        "minimum_angle_deg": math.degrees(theta),
        "candidate_angles_deg": [math.degrees(value) for value in unique],
        "candidate_count": len(unique),
        "squared_span_coefficients": {"k": k, "cosine": a, "sine": b},
    }


def evaluate(
    source: dict,
    *,
    requested_rigging_endpoint_predecessor_head: str = RIGGING_ENDPOINT_PREDECESSOR_HEAD,
    requested_domain_deg=DOMAIN_DEG,
    claim_continuous_triangle_nondegeneracy: bool = False,
    claim_continuous_foldover_or_collision_clearance: bool = False,
    claim_connected_topology: bool = False,
    claim_production_skinning: bool = False,
    claim_animation_acceptance: bool = False,
    claim_technical_art_acceptance: bool = False,
    claim_runtime_acceptance: bool = False,
) -> dict:
    if requested_rigging_endpoint_predecessor_head != RIGGING_ENDPOINT_PREDECESSOR_HEAD:
        raise ValueError("exact Rigging endpoint predecessor head drift")
    domain = tuple(float(value) for value in requested_domain_deg)
    if domain != DOMAIN_DEG:
        raise ValueError("continuous paired-span certificate may not widen or rewrite the child domain")
    if claim_continuous_triangle_nondegeneracy:
        raise ValueError("paired-span non-collapse does not prove continuous triangle nondegeneracy")
    if claim_continuous_foldover_or_collision_clearance:
        raise ValueError("paired-span non-collapse does not prove foldover/collision clearance")
    if claim_connected_topology:
        raise ValueError("analytic bridge remains disconnected from the indexed trunk mesh")
    if claim_production_skinning:
        raise ValueError("diagnostic endpoint ownership is not production skinning")
    if claim_animation_acceptance:
        raise ValueError("Rigging evidence cannot claim Animation acceptance")
    if claim_technical_art_acceptance:
        raise ValueError("Rigging evidence cannot claim Technical Art acceptance")
    if claim_runtime_acceptance:
        raise ValueError("Rigging evidence cannot claim Runtime acceptance")

    predecessor = endpoint_gate.evaluate(source)
    if predecessor.get("result") != endpoint_gate.RESULT:
        raise ValueError("exact endpoint predecessor no longer passes")
    if predecessor["continuous_endpoint_mapping_certificate"]["continuous_for_every_real_child_command_in_domain"] is not True:
        raise ValueError("endpoint predecessor no longer owns a continuous child mapping")

    candidate = endpoint_gate.geometry_bridge.build_candidate(source)
    neutral = [[float(v) for v in point] for point in candidate["bridge_only"]["vertices"]]
    sides = int(endpoint_gate.geometry_bridge.SIDES)
    if sides != 8 or len(neutral) != 16:
        raise ValueError("analytic bridge endpoint cardinality drift")
    branch_neutral = neutral[:sides]
    trunk_neutral = neutral[sides:]
    pivot = [float(v) for v in predecessor["socket_identity"]["pivot_m"]]
    axis = _norm(predecessor["socket_identity"]["source_derived_axis"])
    if [float(v) for v in predecessor["socket_identity"]["diagnostic_interval_deg"]] != list(DOMAIN_DEG):
        raise ValueError("predecessor diagnostic child interval drift")

    pair_certificates = []
    global_minimum_span = float("inf")
    global_minimum_pair = None
    global_minimum_angle = None
    maximum_closed_form_residual = 0.0
    representative_minimum_span = float("inf")

    for index, (moving, fixed) in enumerate(zip(branch_neutral, trunk_neutral)):
        certificate = _continuous_minimum_span(moving, fixed, pivot, axis, *DOMAIN_DEG)
        k = certificate["squared_span_coefficients"]["k"]
        a = certificate["squared_span_coefficients"]["cosine"]
        b = certificate["squared_span_coefficients"]["sine"]
        representative = []
        for angle_deg in REPRESENTATIVE_ANGLES_DEG:
            posed = endpoint_gate.historical._rotate_about_axis(moving, pivot, axis, angle_deg)
            direct = _distance(posed, fixed)
            closed = math.sqrt(_squared_span_from_coefficients(k, a, b, math.radians(angle_deg)))
            residual = abs(direct - closed)
            maximum_closed_form_residual = max(maximum_closed_form_residual, residual)
            representative_minimum_span = min(representative_minimum_span, direct)
            representative.append({
                "child_angle_deg": float(angle_deg),
                "direct_span_m": direct,
                "closed_form_span_m": closed,
                "closed_form_residual_m": residual,
            })
        row = {
            "pair_index": index,
            **certificate,
            "representative_witnesses": representative,
        }
        pair_certificates.append(row)
        if certificate["minimum_span_m"] < global_minimum_span:
            global_minimum_span = certificate["minimum_span_m"]
            global_minimum_pair = index
            global_minimum_angle = certificate["minimum_angle_deg"]

    if global_minimum_span <= TOL:
        raise ValueError("at least one paired analytic bridge span collapses inside the child domain")
    if maximum_closed_form_residual > 1e-10:
        raise ValueError("closed-form paired-span certificate disagrees with direct Rodrigues witnesses")
    if global_minimum_span > representative_minimum_span + 1e-12:
        raise ValueError("continuous minimum cannot exceed retained representative minimum")

    checks = {
        "exact_endpoint_predecessor_reexecuted": predecessor["result"] == endpoint_gate.RESULT,
        "exact_eight_paired_spans_certified": len(pair_certificates) == sides == 8,
        "continuous_child_domain_preserved": list(DOMAIN_DEG) == predecessor["socket_identity"]["diagnostic_interval_deg"],
        "closed_form_matches_representative_rodrigues_witnesses": maximum_closed_form_residual <= 1e-10,
        "all_continuous_paired_span_minima_strictly_positive": all(row["minimum_span_m"] > TOL for row in pair_certificates),
        "continuous_minimum_not_hidden_by_representative_sampling": global_minimum_span <= representative_minimum_span + 1e-12,
    }
    if not all(checks.values()):
        raise ValueError(f"continuous paired-span certificate invariant failed: {checks}")

    return {
        "schema": SCHEMA,
        "result": RESULT,
        "reusable_rule": RULE,
        "constraint": CONSTRAINT,
        "study_id": predecessor["study_id"],
        "source_digest": predecessor["source_digest"],
        "provenance": {
            "rigging_endpoint_predecessor_head": RIGGING_ENDPOINT_PREDECESSOR_HEAD,
            "rigging_endpoint_module_blob": RIGGING_ENDPOINT_MODULE_BLOB,
            "source_blob": SOURCE_BLOB,
            "geometry_bridge_donor_head": predecessor["geometry_bridge_donor_head"],
            "geometry_bridge_module_blob": predecessor["geometry_bridge_module_blob"],
        },
        "socket_identity": predecessor["socket_identity"],
        "continuous_paired_span_certificate": {
            "child_domain_deg": list(DOMAIN_DEG),
            "paired_span_count": sides,
            "global_minimum_span_m": global_minimum_span,
            "global_minimum_pair_index": global_minimum_pair,
            "global_minimum_angle_deg": global_minimum_angle,
            "representative_minimum_span_m": representative_minimum_span,
            "maximum_closed_form_vs_direct_residual_m": maximum_closed_form_residual,
            "continuous_for_every_real_child_command_in_domain": True,
            "proof_method": "finite stationary-point evaluation of K + 2*A*cos(theta) + 2*B*sin(theta) for each rigid-moving/fixed endpoint pair",
        },
        "pair_certificates": pair_certificates,
        "checks": checks,
        "truth_boundary": {
            "source_geometry_mutated": False,
            "geometry_bridge_topology_mutated": False,
            "endpoint_weights_or_socket_identity_mutated": False,
            "indexed_trunk_cut_or_connected_junction_claimed": False,
            "production_skinning_or_blending_claimed": False,
            "continuous_triangle_nondegeneracy_claimed": False,
            "continuous_foldover_collision_or_self_intersection_claimed": False,
            "botanical_mechanics_or_biological_rom_claimed": False,
            "animation_timing_interpolation_or_playback_claimed": False,
            "technical_art_target_host_claimed": False,
            "runtime_controller_device_or_performance_claimed": False,
            "art_or_visual_qa_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }

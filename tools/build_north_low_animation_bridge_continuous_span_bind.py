#!/usr/bin/env python3
"""Compose frozen north-low Animation timing with current Rigging bridge-span evidence.

This is an Animation-owned evidence bridge. It does not change the source clip or the
Rigging endpoint/bridge implementation. It re-runs the exact current Rigging certificate,
checks that the frozen Animation socket identity still matches that owner, directly
replays every authored Animation child angle over the current analytic bridge endpoints,
and then composes the closed Animation curve range with Rigging's continuous paired-span
certificate.

The result is deliberately narrow: temporal compatibility with one Rigging-owned
continuous non-collapse predicate. It is not connected-topology, production-skinning,
target-host, Runtime/controller, collision/gameplay, Art/QA, CANON, or production proof.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from axm_nature_design import rear_tree_rigging_north_low_bridge_continuous_span as span_subject
from axm_nature_design import rear_tree_rigging_north_low_bridge_endpoint_gate as endpoint_gate

SCHEMA = "axm.nature-animation-north-low-bridge-continuous-span-bind/v0.1"
STATUS = "PASS_NATURE_NORTH_LOW_ANIMATION_CURVE_INSIDE_CURRENT_BRIDGE_CONTINUOUS_SPAN_DOMAIN"

ANIMATION_LANE_PREDECESSOR_HEAD = "20d04d70845c51455cedfb8541e2eb4e4784b433"
ANIMATION_SEMANTIC_OWNER_HEAD = "5cacd61e22433b0c33f29111827283b81cc0ba0d"
ANIMATION_PARENT_RIGGING_HEAD = "69640e558f0c1ac59d4d0e3155676e0967a03d04"
CURRENT_RIGGING_HEAD = "efe99261459858636dbe65b16cbe1d5ad2b93a56"
EXPECTED_ANIMATION_RESULT = "PASS_NORTH_LOW_PARENT_EXCLUSION_TEMPORAL_REBIND_SAMPLED_DIAGNOSTIC_MOTION"
EXPECTED_DURATION_S = 1.0
EXPECTED_HZ = 40
EXPECTED_SAMPLE_COUNT = 41
EXPECTED_VISIBLE_REPEAT_SAMPLES = 40
EXPECTED_CURVE = "sin(2*pi*t)^3"
EXPECTED_CHILD_AMPLITUDE_DEG = 5.0
EXPECTED_PARENT_STRESS_AMPLITUDE_DEG = 2.5
EXPECTED_CURVE_RANGE_DEG = [-5.0, 5.0]
TOL = 1e-12


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _distance(a, b) -> float:
    return math.sqrt(sum((float(a[i]) - float(b[i])) ** 2 for i in range(3)))


def _max_vector_delta(a, b) -> float:
    _require(len(a) == len(b), "vector cardinality mismatch")
    return max((abs(float(a[i]) - float(b[i])) for i in range(len(a))), default=0.0)


def _validate_animation(animation: dict) -> None:
    _require(animation["result"] == EXPECTED_ANIMATION_RESULT, "frozen Animation prerequisite is not green")
    _require(animation["current_rigging_owner_head"] == ANIMATION_PARENT_RIGGING_HEAD, "frozen Animation parent Rigging identity drift")
    _require(animation["timing"]["duration_s"] == EXPECTED_DURATION_S, "Animation duration drift")
    _require(animation["timing"]["sample_rate_hz"] == EXPECTED_HZ, "Animation authored cadence drift")
    _require(animation["timing"]["endpoint_inclusive_samples"] == EXPECTED_SAMPLE_COUNT, "Animation sample-count drift")
    _require(animation["timing"]["visible_repeat_samples"] == EXPECTED_VISIBLE_REPEAT_SAMPLES, "Animation visible-repeat count drift")
    _require(animation["timing"]["curve"] == EXPECTED_CURVE, "Animation curve identity drift")
    _require(animation["motion_scope"]["branch_id"] == "north-low", "Animation branch identity drift")
    _require(animation["motion_scope"]["attachment_mode"] == "DETACHED_DIAGNOSTIC_CHILD_SOCKET_ONLY", "Animation attachment identity drift")
    _require(animation["motion_scope"]["child_amplitude_deg"] == EXPECTED_CHILD_AMPLITUDE_DEG, "Animation child amplitude drift")
    _require(animation["motion_scope"]["parent_stress_amplitude_deg"] == EXPECTED_PARENT_STRESS_AMPLITUDE_DEG, "Animation parent-stress amplitude drift")
    _require(animation["motion_scope"]["diagnostic_parent_weight"] == 0.0, "Animation detached-parent weight drift")
    _require(animation["measurements"]["sample_count"] == EXPECTED_SAMPLE_COUNT, "Animation measured sample-count drift")
    _require(animation.get("all_failure_controls_rejected") is True, "Animation fail-closed controls are not green")
    _require(len(animation["samples"]) == EXPECTED_SAMPLE_COUNT, "Animation retained sample cardinality drift")


def _validate_rigging(rigging: dict) -> None:
    _require(rigging["result"] == span_subject.RESULT, "current Rigging continuous-span prerequisite is not green")
    cert = rigging["continuous_paired_span_certificate"]
    _require(cert["child_domain_deg"] == EXPECTED_CURVE_RANGE_DEG, "Rigging continuous child domain drift")
    _require(cert["paired_span_count"] == 8, "Rigging paired-span cardinality drift")
    _require(cert["continuous_for_every_real_child_command_in_domain"] is True, "Rigging lacks all-real-command certificate")
    _require(cert["global_minimum_span_m"] > span_subject.TOL, "Rigging continuous paired-span minimum collapsed")
    _require(len(rigging["pair_certificates"]) == 8, "Rigging pair-certificate cardinality drift")
    _require(rigging["truth_boundary"]["animation_timing_interpolation_or_playback_claimed"] is False, "Rigging authority inflation into Animation")
    _require(rigging["truth_boundary"]["technical_art_target_host_claimed"] is False, "Rigging authority inflation into Technical Art")
    _require(rigging["truth_boundary"]["runtime_controller_device_or_performance_claimed"] is False, "Rigging authority inflation into Runtime")


def _validate_socket_identity(animation_socket: dict, rigging: dict) -> dict:
    current = rigging["socket_identity"]
    branch_match = animation_socket["branch_id"] == current["branch_id"] == "north-low"
    pivot_delta = _max_vector_delta(animation_socket["pivot_m"], current["pivot_m"])
    axis_delta = _max_vector_delta(animation_socket["source_derived_axis"], current["source_derived_axis"])
    interval_match = [float(x) for x in animation_socket["diagnostic_interval_deg"]] == EXPECTED_CURVE_RANGE_DEG == [float(x) for x in current["diagnostic_interval_deg"]]
    _require(branch_match, "Animation/Rigging branch identity mismatch")
    _require(pivot_delta <= TOL, f"Animation/Rigging socket pivot drift: {pivot_delta}")
    _require(axis_delta <= TOL, f"Animation/Rigging socket axis drift: {axis_delta}")
    _require(interval_match, "Animation/Rigging diagnostic interval mismatch")
    return {
        "branch_id_match": branch_match,
        "pivot_max_abs_delta_m": pivot_delta,
        "axis_max_abs_delta": axis_delta,
        "diagnostic_interval_match": interval_match,
    }


def build(animation_receipt: Path, animation_socket_path: Path, rigging_receipt: Path, source_path: Path, output: Path) -> dict:
    animation = _load(animation_receipt)
    animation_socket = _load(animation_socket_path)
    rigging = _load(rigging_receipt)
    source = _load(source_path)

    _validate_animation(animation)
    _validate_rigging(rigging)
    _require(animation["source_digest"] == rigging["source_digest"], "Animation/Rigging source digest mismatch")

    # Re-run the exact current Rigging owner implementation in-process; the retained
    # receipt must be exactly reproducible before Animation composes with it.
    rebuilt_rigging = span_subject.evaluate(source)
    _require(rebuilt_rigging == rigging, "current Rigging receipt is not exactly reproducible")
    identity_checks = _validate_socket_identity(animation_socket, rigging)

    # Continuous Animation range proof. sin(t) is in [-1,1], cubing is monotone on R,
    # and the exact child mapping is -5*sin(...)^3, so every real time lies in [-5,+5].
    animation_curve_range = list(EXPECTED_CURVE_RANGE_DEG)
    rigging_domain = [float(x) for x in rigging["continuous_paired_span_certificate"]["child_domain_deg"]]
    continuous_range_contained = animation_curve_range[0] >= rigging_domain[0] and animation_curve_range[1] <= rigging_domain[1]
    _require(continuous_range_contained, "continuous Animation curve escapes current Rigging certificate domain")

    # Direct actual-motion witnesses at every retained authored sample: move each of
    # the eight current Rigging branch endpoints with the current socket transform,
    # keep its exact paired trunk endpoint fixed, and compare against Rigging's closed form.
    candidate = endpoint_gate.geometry_bridge.build_candidate(source)
    sides = int(endpoint_gate.geometry_bridge.SIDES)
    _require(sides == 8, "current analytic bridge side count drift")
    vertices = [[float(v) for v in p] for p in candidate["bridge_only"]["vertices"]]
    _require(len(vertices) == 16, "current analytic bridge endpoint cardinality drift")
    branch_neutral = vertices[:sides]
    trunk_neutral = vertices[sides:]
    pivot = [float(v) for v in rigging["socket_identity"]["pivot_m"]]
    axis = [float(v) for v in rigging["socket_identity"]["source_derived_axis"]]
    cert_by_pair = {int(row["pair_index"]): row for row in rigging["pair_certificates"]}

    temporal_rows = []
    maximum_closed_form_residual = 0.0
    minimum_sampled_span = float("inf")
    minimum_sampled_pair = None
    minimum_sampled_index = None
    minimum_sampled_angle = None

    for sample in animation["samples"]:
        sample_index = int(sample["index"])
        angle_deg = float(sample["north_low_child_angle_deg"])
        _require(animation_curve_range[0] - TOL <= angle_deg <= animation_curve_range[1] + TOL, "retained Animation sample escaped frozen curve range")
        pair_rows = []
        sample_min = float("inf")
        for pair_index, (moving, fixed) in enumerate(zip(branch_neutral, trunk_neutral)):
            posed = endpoint_gate.historical._rotate_about_axis(moving, pivot, axis, angle_deg)
            direct_span = _distance(posed, fixed)
            cert = cert_by_pair[pair_index]
            coeff = cert["squared_span_coefficients"]
            closed_sq = span_subject._squared_span_from_coefficients(
                coeff["k"], coeff["cosine"], coeff["sine"], math.radians(angle_deg)
            )
            closed_span = math.sqrt(closed_sq)
            residual = abs(direct_span - closed_span)
            maximum_closed_form_residual = max(maximum_closed_form_residual, residual)
            _require(direct_span > span_subject.TOL, "authored Animation sample collapsed a current Rigging paired span")
            _require(residual <= 1e-10, "direct Animation-time bridge motion disagrees with Rigging closed form")
            sample_min = min(sample_min, direct_span)
            pair_rows.append({
                "pair_index": pair_index,
                "direct_span_m": direct_span,
                "closed_form_span_m": closed_span,
                "closed_form_residual_m": residual,
            })
            if direct_span < minimum_sampled_span:
                minimum_sampled_span = direct_span
                minimum_sampled_pair = pair_index
                minimum_sampled_index = sample_index
                minimum_sampled_angle = angle_deg
        temporal_rows.append({
            "sample_index": sample_index,
            "time_s": float(sample["time_s"]),
            "child_angle_deg": angle_deg,
            "minimum_direct_paired_span_m": sample_min,
            "pairs": pair_rows,
        })

    _require(len(temporal_rows) == EXPECTED_SAMPLE_COUNT, "direct temporal bridge witness count drift")
    _require(maximum_closed_form_residual <= 1e-10, "temporal direct/closed-form residual exceeded tolerance")
    continuous_minimum = float(rigging["continuous_paired_span_certificate"]["global_minimum_span_m"])
    _require(continuous_minimum > span_subject.TOL, "continuous Rigging span certificate is not positive")
    _require(continuous_minimum <= minimum_sampled_span + 1e-12, "continuous minimum cannot exceed authored-sample minimum")

    # Proof-local negatives. They must fail without touching the source motion or Rigging data.
    widened_curve = [-5.0, 5.01]
    widened_rejected = not (widened_curve[0] >= rigging_domain[0] and widened_curve[1] <= rigging_domain[1])
    _require(widened_rejected, "widened Animation range control should escape Rigging domain")
    perturbed_pivot = list(animation_socket["pivot_m"])
    perturbed_pivot[0] = float(perturbed_pivot[0]) + 1e-4
    pivot_mismatch_rejected = _max_vector_delta(perturbed_pivot, rigging["socket_identity"]["pivot_m"]) > TOL
    _require(pivot_mismatch_rejected, "socket-identity mismatch control should reject")

    result = {
        "schema": SCHEMA,
        "status": STATUS,
        "exact_identity": {
            "animation_lane_predecessor_head": ANIMATION_LANE_PREDECESSOR_HEAD,
            "animation_semantic_owner_head": ANIMATION_SEMANTIC_OWNER_HEAD,
            "animation_parent_rigging_head": ANIMATION_PARENT_RIGGING_HEAD,
            "current_rigging_continuous_span_head": CURRENT_RIGGING_HEAD,
            "source_digest": animation["source_digest"],
            "socket_identity_checks": identity_checks,
            "source_animation_or_rigging_reauthored": False,
        },
        "animation_curve": {
            "duration_s": EXPECTED_DURATION_S,
            "authored_hz": EXPECTED_HZ,
            "endpoint_inclusive_samples": EXPECTED_SAMPLE_COUNT,
            "visible_repeat_samples": EXPECTED_VISIBLE_REPEAT_SAMPLES,
            "curve": EXPECTED_CURVE,
            "child_angle_range_deg": animation_curve_range,
            "range_reason": "sin is in [-1,1] for every real time; x^3 is monotone; exact child mapping is -5*sin(2*pi*t)^3",
            "retimed_or_reauthored": False,
        },
        "current_rigging_continuous_span": rigging["continuous_paired_span_certificate"],
        "composition": {
            "animation_curve_range_deg": animation_curve_range,
            "rigging_closed_domain_deg": rigging_domain,
            "continuous_range_contained": continuous_range_contained,
            "lower_margin_deg": animation_curve_range[0] - rigging_domain[0],
            "upper_margin_deg": rigging_domain[1] - animation_curve_range[1],
            "boundary_equality_is_covered": True,
            "reason": "Rigging certificate is explicitly closed over every real child command in [-5,+5] deg; the frozen Animation curve reaches but never exceeds those endpoints.",
        },
        "direct_temporal_bridge_witness": {
            "authored_samples_checked": len(temporal_rows),
            "paired_spans_per_sample": 8,
            "minimum_sampled_span_m": minimum_sampled_span,
            "minimum_sampled_pair_index": minimum_sampled_pair,
            "minimum_sampled_sample_index": minimum_sampled_index,
            "minimum_sampled_angle_deg": minimum_sampled_angle,
            "continuous_owner_minimum_span_m": continuous_minimum,
            "maximum_direct_vs_closed_form_residual_m": maximum_closed_form_residual,
            "samples": temporal_rows,
        },
        "negative_controls": {
            "widened_plus5p01_curve_rejected": widened_rejected,
            "socket_pivot_identity_mismatch_rejected": pivot_mismatch_rejected,
        },
        "gates": {
            "current_rigging_paired_span_continuous_noncollapse": "PASS_COMPOSED_BY_EXACT_IDENTITY_AND_CLOSED_RANGE_INCLUSION",
            "authored_animation_time_bridge_endpoint_motion": "PASS_DIRECT_41_SAMPLE_REPLAY",
            "continuous_triangle_nondegeneracy_or_orientation": "NOT_EVALUATED",
            "foldover_collision_or_self_intersection": "NOT_EVALUATED",
            "connected_topology_or_production_skinning": "NOT_EVALUATED",
            "technical_art_target_host_current_pair": "NOT_EVALUATED",
            "runtime_controller_state_machine_input_device": "NOT_EVALUATED",
            "gameplay_collision_physics": "NOT_EVALUATED",
            "art_or_visual_qa": "NOT_EVALUATED",
        },
        "truth_boundary": [
            "This proves only that the exact frozen north-low Animation scalar curve remains inside the exact current Rigging closed interval for which all eight branch/trunk paired spans are continuously non-zero.",
            "Direct actual endpoint motion is replayed for all 41 authored Animation samples, but the all-time claim comes from composing the analytic Animation range with Rigging's continuous certificate, not from sample density.",
            "Zero degree margin is intentional: the Animation reaches +/-5 deg exactly and Rigging's certificate includes both closed-interval endpoints.",
            "No continuous bridge triangle orientation/nondegeneracy, foldover/collision/self-intersection, connected topology, production skinning, physical wind, target-host playback for the current pair, wall-clock cadence, Runtime/controller/device, gameplay, Art/QA, CANON, game-readiness, or production-readiness acceptance is claimed.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--animation-receipt", type=Path, required=True)
    parser.add_argument("--animation-socket", type=Path, required=True)
    parser.add_argument("--rigging-receipt", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.animation_receipt, args.animation_socket, args.rigging_receipt, args.source, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

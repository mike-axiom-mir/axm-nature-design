#!/usr/bin/env python3
"""Animation-owned sampled-motion proof over the exact Rigging five-branch family.

The owner Rigging worktree is injected explicitly so this verifier can consume one
exact downstream owner revision without copying or silently adopting Rigging code.
Each branch is animated independently. This file never proves simultaneous branch
motion, wind response, Runtime/controller behavior, gameplay, or natural timing.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

RIGGING_HEAD = "898529f602893c8f6be179bd3e9b6821fc099904"
RIGGING_RESULT = "PASS_FIVE_PRIMARY_BRANCH_ROOT_SOCKET_RIGID_CHILD_FAMILY_GEOMETRY_RECEIVER_DIAGNOSTIC_MINUS5_TO_PLUS5"
RESULT = "PASS_FIVE_PRIMARY_BRANCH_ROOT_SOCKET_INDEPENDENT_DIAGNOSTIC_PULSE_FAMILY_SAMPLED_MOTION"
SCHEMA = "axm.nature-animation-root-socket-diagnostic-pulse-family/v0.2"
TRUTH_LABEL = "ANIMATION_INDEPENDENT_SOCKET_PULSE_FAMILY_NOT_WIND_NOT_BIOLOGICAL_ROM_NOT_CONTROLLER_NOT_SIMULTANEOUS_ACCEPTANCE"
BRANCH_IDS = ("south-low", "north-low", "east-mid", "west-high", "north-top")
DURATION_S = 1.0
SAMPLE_RATE_HZ = 40
SAMPLE_COUNT = 41
VISIBLE_REPEAT_SAMPLES = 40
AMPLITUDE_DEG = 5.0
TOL = 1e-12


def _sub(a, b):
    return [float(a[i]) - float(b[i]) for i in range(3)]


def _dot(a, b):
    return sum(float(a[i]) * float(b[i]) for i in range(3))


def _length(v):
    return math.sqrt(_dot(v, v))


def _distance(a, b):
    return _length(_sub(a, b))


def _pairwise_distances(vertices):
    values = []
    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            values.append(_distance(vertices[i], vertices[j]))
    return values


def _max_abs_delta(a, b):
    if len(a) != len(b):
        raise ValueError("mismatched evidence vectors")
    return max((abs(float(x) - float(y)) for x, y in zip(a, b)), default=0.0)


def _angle_for_index(index: int) -> float:
    if index < 0 or index >= SAMPLE_COUNT:
        raise ValueError("sample index outside endpoint-inclusive family clip")
    if index in (0, 20, 40):
        return 0.0
    if index == 10:
        return AMPLITUDE_DEG
    if index == 30:
        return -AMPLITUDE_DEG
    t = index / float(SAMPLE_RATE_HZ)
    return AMPLITUDE_DEG * (math.sin(2.0 * math.pi * t) ** 3)


def _motion_metrics(neutral, posed, selected, fixed, pivot_indices, pivot, axis):
    neutral_selected = [neutral[i] for i in selected]
    posed_selected = [posed[i] for i in selected]
    return {
        "fixed_vertex_drift_m": max((_distance(posed[i], neutral[i]) for i in fixed), default=0.0),
        "pivot_vertex_drift_m": max((_distance(posed[i], neutral[i]) for i in pivot_indices), default=0.0),
        "selected_pairwise_distance_drift_m": _max_abs_delta(
            _pairwise_distances(posed_selected), _pairwise_distances(neutral_selected)
        ),
        "selected_axis_projection_drift_m": max(
            (abs(_dot(_sub(posed[i], pivot), axis) - _dot(_sub(neutral[i], pivot), axis)) for i in selected),
            default=0.0,
        ),
        "maximum_selected_vertex_displacement_m": max((_distance(posed[i], neutral[i]) for i in selected), default=0.0),
    }


def _evaluate_branch(owner_family, neutral, probe):
    branch_id = probe["branch_id"]
    selected = [int(i) for i in probe["selected_vertex_indices"]]
    selected_set = set(selected)
    fixed = [i for i in range(len(neutral)) if i not in selected_set]
    pivot = [float(v) for v in probe["joint_pivot_m"]]
    axis = [float(v) for v in probe["source_derived_axis"]]
    pivot_indices = [int(i) for i in probe["generated_pivot_vertex_indices"]]

    if len(selected) != 52 or len(fixed) != 338 or len(pivot_indices) != 1:
        raise ValueError(f"exact Rigging partition drift: {branch_id}")
    if probe["diagnostic_interval_semantics"] != "RIGGING_VERIFICATION_PROBE_ONLY_NOT_SOURCE_OR_BIOLOGICAL_ROM":
        raise ValueError(f"Rigging truth-boundary drift: {branch_id}")
    if [float(v) for v in probe["diagnostic_interval_deg"]] != [-5.0, 5.0]:
        raise ValueError(f"Rigging diagnostic interval drift: {branch_id}")

    frames = []
    samples = []
    max_fixed = max_pivot = max_pairwise = max_axis = max_displacement = max_step = 0.0

    for index in range(SAMPLE_COUNT):
        angle = _angle_for_index(index)
        if angle < -AMPLITUDE_DEG - TOL or angle > AMPLITUDE_DEG + TOL:
            raise ValueError(f"Animation sample escaped Rigging probe: {branch_id}")
        posed = [[float(v) for v in row] for row in neutral]
        for vertex_index in selected:
            posed[vertex_index] = owner_family.historical._rotate_about_axis(neutral[vertex_index], pivot, axis, angle)
        metrics = _motion_metrics(neutral, posed, selected, fixed, pivot_indices, pivot, axis)
        step = 0.0
        if frames:
            step = max((_distance(posed[i], frames[-1][i]) for i in selected), default=0.0)
        max_fixed = max(max_fixed, metrics["fixed_vertex_drift_m"])
        max_pivot = max(max_pivot, metrics["pivot_vertex_drift_m"])
        max_pairwise = max(max_pairwise, metrics["selected_pairwise_distance_drift_m"])
        max_axis = max(max_axis, metrics["selected_axis_projection_drift_m"])
        max_displacement = max(max_displacement, metrics["maximum_selected_vertex_displacement_m"])
        max_step = max(max_step, step)
        samples.append({
            "index": index,
            "time_s": index / float(SAMPLE_RATE_HZ),
            "angle_deg": angle,
            "maximum_selected_step_from_previous_m": step,
            **metrics,
        })
        frames.append(posed)

    endpoint_closure = max((_distance(frames[0][i], frames[-1][i]) for i in range(len(neutral))), default=0.0)
    visible_wrap = max((_distance(frames[39][i], frames[0][i]) for i in selected), default=0.0)
    authored_final_step = max((_distance(frames[39][i], frames[40][i]) for i in selected), default=0.0)
    wrap_residual = abs(visible_wrap - authored_final_step)
    antisymmetry = max((abs(samples[i]["angle_deg"] + samples[40 - i]["angle_deg"]) for i in range(SAMPLE_COUNT)), default=0.0)

    owner_pose_by_angle = {float(row["angle_deg"]): row for row in probe["poses"]}
    owner_metric_keys = (
        "fixed_vertex_drift_m",
        "pivot_vertex_drift_m",
        "selected_pairwise_distance_drift_m",
        "selected_axis_projection_drift_m",
        "maximum_selected_vertex_displacement_m",
    )
    max_owner_witness_residual = 0.0
    for angle in (-5.0, -2.5, 0.0, 2.5, 5.0):
        posed = [[float(v) for v in row] for row in neutral]
        for vertex_index in selected:
            posed[vertex_index] = owner_family.historical._rotate_about_axis(neutral[vertex_index], pivot, axis, angle)
        metrics = _motion_metrics(neutral, posed, selected, fixed, pivot_indices, pivot, axis)
        owner_pose = owner_pose_by_angle[angle]
        for key in owner_metric_keys:
            max_owner_witness_residual = max(max_owner_witness_residual, abs(float(metrics[key]) - float(owner_pose[key])))

    checks = {
        "exact_sample_count": len(samples) == SAMPLE_COUNT,
        "exact_landmarks": samples[0]["angle_deg"] == 0.0 and samples[10]["angle_deg"] == 5.0 and samples[20]["angle_deg"] == 0.0 and samples[30]["angle_deg"] == -5.0 and samples[40]["angle_deg"] == 0.0,
        "fixed_receiver_exact": max_fixed <= TOL,
        "pivot_exact": max_pivot <= TOL,
        "rigid_child_preserved": max_pairwise <= TOL,
        "axis_projection_preserved": max_axis <= TOL,
        "endpoint_neutral_closure": endpoint_closure <= TOL,
        "repeat_wrap_matches_authored_final_step": wrap_residual <= TOL,
        "bidirectional_curve_is_antisymmetric": antisymmetry <= TOL,
        "animation_replay_matches_owner_witnesses": max_owner_witness_residual <= TOL,
    }
    if not all(checks.values()):
        raise ValueError(f"Animation family invariant failed: {branch_id}")

    return {
        "branch_id": branch_id,
        "clip_id": f"{branch_id}-root-socket-diagnostic-pulse-002",
        "owner_joint_pivot_m": pivot,
        "owner_source_derived_axis": axis,
        "selected_vertices": len(selected),
        "fixed_vertices": len(fixed),
        "samples": samples,
        "measurements": {
            "maximum_fixed_vertex_drift_m": max_fixed,
            "maximum_pivot_vertex_drift_m": max_pivot,
            "maximum_selected_pairwise_distance_drift_m": max_pairwise,
            "maximum_selected_axis_projection_drift_m": max_axis,
            "maximum_selected_vertex_displacement_m": max_displacement,
            "maximum_adjacent_selected_step_m": max_step,
            "endpoint_closure_m": endpoint_closure,
            "visible_repeat_wrap_step_m": visible_wrap,
            "authored_final_adjacent_step_m": authored_final_step,
            "wrap_step_residual_m": wrap_residual,
            "maximum_owner_witness_metric_residual": max_owner_witness_residual,
            "angular_antisymmetry_error_deg": antisymmetry,
        },
        "checks": checks,
    }


def _write_svg(path: Path, branch_rows):
    width, height = 980, 620
    margin_left, margin_top = 80, 60
    panel_h = 95
    plot_w = 820
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="40" y="30" font-family="monospace" font-size="18">AXM Nature Animation — five independent Rigging-socket diagnostic pulses</text>',
        '<text x="40" y="50" font-family="monospace" font-size="12">review plot: maximum selected-vertex displacement from neutral; not wind / not simultaneous motion / not runtime</text>',
    ]
    for row_index, row in enumerate(branch_rows):
        y0 = margin_top + row_index * panel_h
        values = [float(sample["maximum_selected_vertex_displacement_m"]) for sample in row["samples"]]
        vmax = max(values) or 1.0
        points = []
        for i, value in enumerate(values):
            x = margin_left + plot_w * (i / 40.0)
            y = y0 + 60.0 - 50.0 * (value / vmax)
            points.append(f"{x:.3f},{y:.3f}")
        lines.extend([
            f'<text x="20" y="{y0 + 18}" font-family="monospace" font-size="13">{row["branch_id"]}</text>',
            f'<line x1="{margin_left}" y1="{y0 + 60}" x2="{margin_left + plot_w}" y2="{y0 + 60}" stroke="black" stroke-width="1"/>',
            f'<polyline points="{" ".join(points)}" fill="none" stroke="black" stroke-width="2"/>',
            f'<text x="{margin_left + plot_w + 10}" y="{y0 + 20}" font-family="monospace" font-size="11">peak={vmax:.6f} m</text>',
            f'<text x="{margin_left + plot_w + 10}" y="{y0 + 38}" font-family="monospace" font-size="11">41 samples</text>',
        ])
    lines.append('</svg>')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def evaluate(args):
    if args.requested_rigging_head != RIGGING_HEAD:
        raise ValueError("exact Rigging family head drift")
    if abs(float(args.duration_s) - DURATION_S) > TOL:
        raise ValueError("Animation family duration drift")
    if int(args.sample_rate_hz) != SAMPLE_RATE_HZ:
        raise ValueError("Animation family sample-rate drift")
    if abs(float(args.amplitude_deg) - AMPLITUDE_DEG) > TOL:
        raise ValueError("Animation may not widen or relabel the Rigging diagnostic interval")
    if args.claim_wind_motion:
        raise ValueError("Animation diagnostic family is not a wind-motion claim")
    if args.claim_biological_rom:
        raise ValueError("Rigging diagnostic interval is not biological/source ROM")
    if args.claim_runtime_controller:
        raise ValueError("Animation evidence cannot claim Runtime controller acceptance")
    if args.claim_gameplay_acceptance:
        raise ValueError("Animation evidence cannot claim gameplay acceptance")
    if args.claim_simultaneous_motion_acceptance:
        raise ValueError("independent socket clips do not prove simultaneous multi-branch motion")

    worktree = Path(args.rigging_worktree).resolve()
    owner_src = worktree / "src"
    source_path = worktree / "examples" / "east_rear_tree_neutral_001.json"
    if not owner_src.is_dir() or not source_path.is_file():
        raise ValueError("exact Rigging worktree is missing required source surfaces")
    sys.path.insert(0, str(owner_src))
    from axm_nature_design import organic_form as owner_organic  # type: ignore
    from axm_nature_design import rear_tree_rigging_primary_branch_family as owner_family  # type: ignore

    source = json.loads(source_path.read_text(encoding="utf-8"))
    owner = owner_family.evaluate(source)
    if owner.get("result") != RIGGING_RESULT:
        raise ValueError("exact Rigging family prerequisite is not green")

    mesh = owner_organic.build_mesh(source)
    neutral = [[float(v) for v in row] for row in mesh["vertices"]]
    branches = []
    for branch_id in BRANCH_IDS:
        probe = owner_family._probe_branch(source, mesh, branch_id)
        if probe["branch_id"] != branch_id:
            raise ValueError("owner branch identity/order drift")
        branches.append(_evaluate_branch(owner_family, neutral, probe))

    family_checks = {
        "exact_rigging_family_result": owner.get("result") == RIGGING_RESULT,
        "exact_branch_order": [row["branch_id"] for row in branches] == list(BRANCH_IDS),
        "five_independent_clips": len(branches) == 5,
        "all_branch_checks_green": all(all(row["checks"].values()) for row in branches),
        "no_simultaneous_motion_claim": not args.claim_simultaneous_motion_acceptance,
        "wind_not_claimed": not args.claim_wind_motion,
        "biological_rom_not_claimed": not args.claim_biological_rom,
        "runtime_controller_not_claimed": not args.claim_runtime_controller,
        "gameplay_not_claimed": not args.claim_gameplay_acceptance,
    }
    if not all(family_checks.values()):
        raise ValueError("Animation family-level invariant failed")

    return {
        "schema": SCHEMA,
        "result": RESULT,
        "truth_label": TRUTH_LABEL,
        "owner": {
            "repository": "mike-axiom-mir/axm-nature-design",
            "pr": 14,
            "exact_head": RIGGING_HEAD,
            "result": RIGGING_RESULT,
        },
        "motion_method": {
            "execution_mode": "INDEPENDENT_ONE_BRANCH_AT_A_TIME__NO_SIMULTANEOUS_MOTION_ACCEPTANCE",
            "duration_s": DURATION_S,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "endpoint_inclusive_samples_per_clip": SAMPLE_COUNT,
            "visible_repeating_samples_per_clip": VISIBLE_REPEAT_SAMPLES,
            "curve": "angle_deg = 5 * sin(2*pi*t)^3; exact landmarks clamped at 0/0.25/0.5/0.75/1.0 s",
            "landmarks": [
                {"time_s": 0.0, "angle_deg": 0.0},
                {"time_s": 0.25, "angle_deg": 5.0},
                {"time_s": 0.5, "angle_deg": 0.0},
                {"time_s": 0.75, "angle_deg": -5.0},
                {"time_s": 1.0, "angle_deg": 0.0},
            ],
            "timing_semantics": "ANIMATION_DIAGNOSTIC_CANDIDATE_ONLY_NOT_NATURAL_VEGETATION_TIMING",
            "amplitude_semantics": "EXACT_RIGGING_DIAGNOSTIC_BOUND_ONLY_NOT_SOURCE_OR_BIOLOGICAL_ROM",
        },
        "branches": branches,
        "family_measurements": {
            "maximum_fixed_vertex_drift_m": max(row["measurements"]["maximum_fixed_vertex_drift_m"] for row in branches),
            "maximum_pivot_vertex_drift_m": max(row["measurements"]["maximum_pivot_vertex_drift_m"] for row in branches),
            "maximum_selected_pairwise_distance_drift_m": max(row["measurements"]["maximum_selected_pairwise_distance_drift_m"] for row in branches),
            "maximum_selected_axis_projection_drift_m": max(row["measurements"]["maximum_selected_axis_projection_drift_m"] for row in branches),
            "maximum_selected_vertex_displacement_m": max(row["measurements"]["maximum_selected_vertex_displacement_m"] for row in branches),
            "maximum_adjacent_selected_step_m": max(row["measurements"]["maximum_adjacent_selected_step_m"] for row in branches),
            "maximum_endpoint_closure_m": max(row["measurements"]["endpoint_closure_m"] for row in branches),
            "maximum_wrap_step_residual_m": max(row["measurements"]["wrap_step_residual_m"] for row in branches),
            "maximum_owner_witness_metric_residual": max(row["measurements"]["maximum_owner_witness_metric_residual"] for row in branches),
        },
        "checks": family_checks,
        "truth_boundary": {
            "source_or_biological_rom_claimed": False,
            "physical_wind_or_biomechanics_claimed": False,
            "vfx_motion_adoption_claimed": False,
            "simultaneous_multi_branch_motion_acceptance_claimed": False,
            "target_engine_playback_claimed": False,
            "wall_clock_or_display_delivery_claimed": False,
            "runtime_controller_or_state_machine_claimed": False,
            "gameplay_input_collision_claimed": False,
            "target_device_performance_claimed": False,
            "art_or_visual_qa_acceptance_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rigging-worktree", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--svg-output", required=True)
    parser.add_argument("--requested-rigging-head", default=RIGGING_HEAD)
    parser.add_argument("--duration-s", type=float, default=DURATION_S)
    parser.add_argument("--sample-rate-hz", type=int, default=SAMPLE_RATE_HZ)
    parser.add_argument("--amplitude-deg", type=float, default=AMPLITUDE_DEG)
    parser.add_argument("--claim-wind-motion", action="store_true")
    parser.add_argument("--claim-biological-rom", action="store_true")
    parser.add_argument("--claim-runtime-controller", action="store_true")
    parser.add_argument("--claim-gameplay-acceptance", action="store_true")
    parser.add_argument("--claim-simultaneous-motion-acceptance", action="store_true")
    args = parser.parse_args()

    payload = evaluate(args)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    svg = Path(args.svg_output)
    svg.parent.mkdir(parents=True, exist_ok=True)
    _write_svg(svg, payload["branches"])
    print(json.dumps({"result": payload["result"], "family_measurements": payload["family_measurements"]}, sort_keys=True))


if __name__ == "__main__":
    main()

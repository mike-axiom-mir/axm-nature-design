#!/usr/bin/env python3
"""Review exact north-low analytic-bridge Animation motion in Weather's visual frame.

This VFX-owned observer consumes exact Animation, Rigging and Weather owner outputs.
It measures source-space visual response only. It does not author timing, rigging,
weather physics, target-host behavior, gameplay, or aesthetic acceptance.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from axm_nature_design import rear_tree_rigging_north_low_bridge_continuous_span as span_subject
from axm_nature_design import rear_tree_rigging_north_low_bridge_endpoint_gate as endpoint_gate

SCHEMA = "axm.nature-vfx-north-low-analytic-bridge-animation-weather-temporal/v0.1"
RESULT = "PASS_NORTH_LOW_ANALYTIC_BRIDGE_TEMPORAL_WEATHER_VISUAL_RESPONSE"
ANIMATION_HEAD = "d4442cbbe6dcdcde1abadfcd358bb7a6bcdc3701"
ANIMATION_SEMANTIC_OWNER = "5cacd61e22433b0c33f29111827283b81cc0ba0d"
CURRENT_RIGGING_HEAD = "efe99261459858636dbe65b16cbe1d5ad2b93a56"
WEATHER_HEAD = "ca2eaba519e8449835b0ea6ef944b7080c3caa6a"
WEATHER_WIND_XY = (1.0, 0.35)
WEATHER_SEMANTICS = "VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED"
EXPECTED_ANIMATION_RESULT = "PASS_NORTH_LOW_PARENT_EXCLUSION_TEMPORAL_REBIND_SAMPLED_DIAGNOSTIC_MOTION"
EXPECTED_BIND_SCHEMA = "axm.nature-animation-north-low-bridge-continuous-span-bind/v0.1"
TOL = 1e-12


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def centroid(points):
    require(bool(points), "empty point set")
    n = float(len(points))
    return [sum(float(p[i]) for p in points) / n for i in range(3)]


def sub(a, b):
    return [float(a[i]) - float(b[i]) for i in range(3)]


def length(v):
    return math.sqrt(sum(float(x) * float(x) for x in v))


def normalize_xy(wind):
    x, y = float(wind[0]), float(wind[1])
    mag = math.hypot(x, y)
    require(mag > TOL, "Weather visual direction must be non-zero")
    return (x / mag, y / mag)


def project_xy(delta, wind):
    return float(delta[0]) * wind[0] + float(delta[1]) * wind[1]


def cross_xy(delta, wind):
    return -float(delta[0]) * wind[1] + float(delta[1]) * wind[0]


def build_report(
    animation_evidence: dict,
    animation_bind: dict,
    source: dict,
    *,
    requested_animation_head: str = ANIMATION_HEAD,
    requested_rigging_head: str = CURRENT_RIGGING_HEAD,
    wind_xy=WEATHER_WIND_XY,
    claim_physical_wind: bool = False,
    claim_target_host: bool = False,
    claim_runtime: bool = False,
    claim_gameplay_or_physics: bool = False,
    claim_art_or_qa: bool = False,
) -> dict:
    require(requested_animation_head == ANIMATION_HEAD, "exact Animation owner head drift")
    require(requested_rigging_head == CURRENT_RIGGING_HEAD, "exact current Rigging owner head drift")
    wind_xy = tuple(float(v) for v in wind_xy)
    require(wind_xy == WEATHER_WIND_XY, "Weather visual-direction donor drift")
    if claim_physical_wind:
        raise ValueError("Weather donor is visual-direction evidence only")
    if claim_target_host:
        raise ValueError("source-space VFX observer cannot claim target-host acceptance")
    if claim_runtime:
        raise ValueError("VFX observer cannot claim Runtime acceptance")
    if claim_gameplay_or_physics:
        raise ValueError("VFX observer cannot claim gameplay or physics behavior")
    if claim_art_or_qa:
        raise ValueError("VFX observer cannot claim Art Direction or independent Visual QA acceptance")

    require(animation_bind.get("schema") == EXPECTED_BIND_SCHEMA, "Animation bridge-bind contract schema drift")
    require(animation_bind.get("animation_semantic_owner_head") == ANIMATION_SEMANTIC_OWNER, "Animation semantic owner drift")
    require(animation_bind.get("current_rigging_continuous_span_head") == CURRENT_RIGGING_HEAD, "Animation current Rigging bind drift")
    frozen = animation_bind["frozen_animation"]
    require(frozen["duration_s"] == 1.0, "Animation duration drift")
    require(frozen["authored_hz"] == 40, "Animation cadence drift")
    require(frozen["endpoint_inclusive_samples"] == 41, "Animation sample count drift")
    require(frozen["visible_repeat_samples"] == 40, "Animation visible repeat count drift")
    require(frozen["curve"] == "sin(2*pi*t)^3", "Animation curve identity drift")
    require(frozen["north_low_child_range_deg"] == [-5.0, 5.0], "Animation child range drift")
    require(frozen["retimed_or_reauthored"] is False, "Animation owner reports retiming/reauthoring")

    require(animation_evidence.get("result") == EXPECTED_ANIMATION_RESULT, "frozen Animation receipt is not green")
    require(animation_evidence["timing"]["duration_s"] == 1.0, "Animation receipt duration drift")
    require(animation_evidence["timing"]["sample_rate_hz"] == 40, "Animation receipt cadence drift")
    require(animation_evidence["timing"]["endpoint_inclusive_samples"] == 41, "Animation receipt sample-count drift")
    require(animation_evidence["motion_scope"]["branch_id"] == "north-low", "Animation branch identity drift")
    require(animation_evidence["motion_scope"]["diagnostic_parent_weight"] == 0.0, "detached parent gate drift")
    samples = animation_evidence["samples"]
    require(len(samples) == 41, "Animation retained sample cardinality drift")

    rigging = span_subject.evaluate(source)
    require(rigging.get("result") == span_subject.RESULT, "current Rigging continuous-span prerequisite is not green")
    cert = rigging["continuous_paired_span_certificate"]
    require(cert["child_domain_deg"] == [-5.0, 5.0], "Rigging closed child domain drift")
    require(cert["paired_span_count"] == 8, "Rigging paired-span count drift")
    require(cert["continuous_for_every_real_child_command_in_domain"] is True, "Rigging continuous-domain certificate missing")

    candidate = endpoint_gate.geometry_bridge.build_candidate(source)
    sides = int(endpoint_gate.geometry_bridge.SIDES)
    require(sides == 8, "analytic bridge side count drift")
    vertices = [[float(v) for v in p] for p in candidate["bridge_only"]["vertices"]]
    require(len(vertices) == 16, "analytic bridge endpoint cardinality drift")
    branch_neutral = vertices[:sides]
    trunk_neutral = vertices[sides:]
    neutral_all = branch_neutral + trunk_neutral
    pivot = [float(v) for v in rigging["socket_identity"]["pivot_m"]]
    axis = [float(v) for v in rigging["socket_identity"]["source_derived_axis"]]
    wind = normalize_xy(wind_xy)

    neutral_branch_centroid = centroid(branch_neutral)
    neutral_trunk_centroid = centroid(trunk_neutral)
    neutral_bridge_centroid = centroid(neutral_all)

    rows = []
    polarity_violations = 0
    max_trunk_drift = 0.0
    max_half_response_residual = 0.0
    max_endpoint_span_residual = 0.0
    min_direct_span = float("inf")
    cert_by_pair = {int(row["pair_index"]): row for row in rigging["pair_certificates"]}

    for sample in samples:
        index = int(sample["index"])
        time_s = float(sample["time_s"])
        angle = float(sample["north_low_child_angle_deg"])
        require(-5.0 - TOL <= angle <= 5.0 + TOL, "Animation sample escaped Rigging/VFX child domain")
        branch = [endpoint_gate.historical._rotate_about_axis(point, pivot, axis, angle) for point in branch_neutral]
        trunk = [list(point) for point in trunk_neutral]
        all_points = branch + trunk
        branch_delta = sub(centroid(branch), neutral_branch_centroid)
        trunk_delta = sub(centroid(trunk), neutral_trunk_centroid)
        bridge_delta = sub(centroid(all_points), neutral_bridge_centroid)
        half_residual = length(sub(bridge_delta, [0.5 * x for x in branch_delta]))
        trunk_drift = length(trunk_delta)
        parallel = project_xy(branch_delta, wind)
        bridge_parallel = project_xy(bridge_delta, wind)
        if angle < -1e-10 and parallel <= 0.0:
            polarity_violations += 1
        elif angle > 1e-10 and parallel >= 0.0:
            polarity_violations += 1
        elif abs(angle) <= 1e-10 and abs(parallel) > TOL:
            polarity_violations += 1

        sample_min_span = float("inf")
        for pair_index, (moving, fixed) in enumerate(zip(branch, trunk)):
            direct = length(sub(moving, fixed))
            coeff = cert_by_pair[pair_index]["squared_span_coefficients"]
            closed_sq = span_subject._squared_span_from_coefficients(
                coeff["k"], coeff["cosine"], coeff["sine"], math.radians(angle)
            )
            closed = math.sqrt(closed_sq)
            residual = abs(direct - closed)
            max_endpoint_span_residual = max(max_endpoint_span_residual, residual)
            sample_min_span = min(sample_min_span, direct)
            min_direct_span = min(min_direct_span, direct)

        max_trunk_drift = max(max_trunk_drift, trunk_drift)
        max_half_response_residual = max(max_half_response_residual, half_residual)
        rows.append({
            "sample_index": index,
            "time_s": time_s,
            "child_angle_deg": angle,
            "branch_weather_parallel_m": parallel,
            "bridge_weather_parallel_m": bridge_parallel,
            "branch_weather_cross_m": cross_xy(branch_delta, wind),
            "bridge_weather_cross_m": cross_xy(bridge_delta, wind),
            "branch_vertical_m": branch_delta[2],
            "bridge_vertical_m": bridge_delta[2],
            "trunk_centroid_drift_m": trunk_drift,
            "bridge_vs_half_branch_response_residual_m": half_residual,
            "minimum_direct_paired_span_m": sample_min_span,
        })

    require(polarity_violations == 0, "Weather visual-direction polarity violation in authored Animation samples")
    require(max_trunk_drift <= TOL, "pinned analytic trunk endpoint drift")
    require(max_half_response_residual <= TOL, "analytic bridge centroid no longer tracks half branch response")
    require(max_endpoint_span_residual <= 1e-10, "direct endpoint motion disagrees with current Rigging closed form")

    by_index = {row["sample_index"]: row for row in rows}
    require(abs(by_index[0]["branch_weather_parallel_m"]) <= TOL, "loop start is not neutral")
    require(abs(by_index[20]["branch_weather_parallel_m"]) <= TOL, "half-loop landmark is not neutral")
    require(abs(by_index[40]["branch_weather_parallel_m"]) <= TOL, "loop endpoint is not neutral")
    require(abs(by_index[10]["child_angle_deg"] + 5.0) <= 1e-10, "quarter-cycle -5 degree landmark drift")
    require(abs(by_index[30]["child_angle_deg"] - 5.0) <= 1e-10, "three-quarter-cycle +5 degree landmark drift")
    require(by_index[10]["branch_weather_parallel_m"] > 0.0, "-5 degree landmark is not downwind")
    require(by_index[30]["branch_weather_parallel_m"] < 0.0, "+5 degree landmark is not upwind")
    closure_error = length([
        by_index[40]["branch_weather_parallel_m"] - by_index[0]["branch_weather_parallel_m"],
        by_index[40]["branch_weather_cross_m"] - by_index[0]["branch_weather_cross_m"],
        by_index[40]["branch_vertical_m"] - by_index[0]["branch_vertical_m"],
    ])
    require(closure_error <= TOL, "Animation loop visual response does not close")

    return {
        "schema": SCHEMA,
        "result": RESULT,
        "owner_identity": {
            "animation_head": ANIMATION_HEAD,
            "animation_semantic_owner_head": ANIMATION_SEMANTIC_OWNER,
            "current_rigging_head": CURRENT_RIGGING_HEAD,
            "weather_head": WEATHER_HEAD,
        },
        "weather_visual_direction": {
            "wind_xy": list(WEATHER_WIND_XY),
            "normalized_wind_xy": list(wind),
            "semantics": WEATHER_SEMANTICS,
        },
        "animation": {
            "duration_s": 1.0,
            "authored_hz": 40,
            "endpoint_inclusive_samples": 41,
            "visible_repeat_samples": 40,
            "curve": "sin(2*pi*t)^3",
            "retimed_or_reauthored_by_vfx": False,
        },
        "rigging_continuous_span": {
            "closed_child_domain_deg": cert["child_domain_deg"],
            "paired_span_count": cert["paired_span_count"],
            "continuous_owner_minimum_span_m": cert["global_minimum_span_m"],
            "continuous_owner_minimum_angle_deg": cert["global_minimum_angle_deg"],
        },
        "measurements": {
            "rows": rows,
            "weather_polarity_sign_violations": polarity_violations,
            "maximum_trunk_centroid_drift_m": max_trunk_drift,
            "maximum_bridge_vs_half_branch_response_residual_m": max_half_response_residual,
            "maximum_direct_vs_rigging_closed_form_span_residual_m": max_endpoint_span_residual,
            "minimum_authored_sample_paired_span_m": min_direct_span,
            "loop_closure_response_error_m": closure_error,
            "minus5_branch_weather_parallel_m": by_index[10]["branch_weather_parallel_m"],
            "minus5_bridge_weather_parallel_m": by_index[10]["bridge_weather_parallel_m"],
            "plus5_branch_weather_parallel_m": by_index[30]["branch_weather_parallel_m"],
            "plus5_bridge_weather_parallel_m": by_index[30]["bridge_weather_parallel_m"],
        },
        "decision": "KEEP_EXACT_ANIMATION_TO_WEATHER_VISUAL_RESPONSE_CONTINUITY_ON_ANALYTIC_BRIDGE__NO_TARGET_RUNTIME_OR_PHYSICAL_WIND_ADOPTION",
        "truth_boundary": {
            "source_space_temporal_visual_response_evidence_only": True,
            "physical_wind_force_speed_drag_or_turbulence_claimed": False,
            "connected_topology_or_production_skinning_claimed": False,
            "continuous_triangle_foldover_collision_or_self_intersection_claimed": False,
            "animation_timing_or_motion_authorship_claimed_by_vfx": False,
            "technical_art_target_host_playback_claimed": False,
            "wall_clock_40hz_delivery_claimed": False,
            "runtime_controller_device_or_performance_claimed": False,
            "gameplay_damage_collision_or_physics_claimed": False,
            "art_direction_or_independent_visual_qa_acceptance_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }


def build_svg(report: dict) -> str:
    rows = report["measurements"]["rows"]
    width, height = 1100, 520
    left, right, top, bottom = 80, 40, 70, 70
    plot_w, plot_h = width - left - right, height - top - bottom
    values = [1000.0 * row["branch_weather_parallel_m"] for row in rows]
    values += [1000.0 * row["bridge_weather_parallel_m"] for row in rows]
    bound = max(max(abs(v) for v in values), 0.001) * 1.15

    def sx(t):
        return left + float(t) * plot_w

    def sy(mm):
        return top + (bound - float(mm)) / (2.0 * bound) * plot_h

    branch_points = " ".join(f"{sx(r['time_s']):.2f},{sy(1000*r['branch_weather_parallel_m']):.2f}" for r in rows)
    bridge_points = " ".join(f"{sx(r['time_s']):.2f},{sy(1000*r['bridge_weather_parallel_m']):.2f}" for r in rows)
    zero_y = sy(0.0)
    pieces = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:monospace;fill:#111}.axis{stroke:#777;stroke-width:1}.branch{fill:none;stroke:#111;stroke-width:3}.bridge{fill:none;stroke:#777;stroke-width:2;stroke-dasharray:7 5}.note{font-size:12px;fill:#555}</style>',
        '<text x="24" y="28" font-size="17px">north-low analytic bridge — exact Animation loop in Weather visual-direction frame</text>',
        '<text x="24" y="48" class="note">source-space temporal visual evidence only; Weather [1.0, 0.35] is not physical wind speed/force</text>',
        f'<line class="axis" x1="{left}" y1="{zero_y:.2f}" x2="{width-right}" y2="{zero_y:.2f}"/>',
        f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}"/>',
        f'<polyline class="branch" points="{branch_points}"/>',
        f'<polyline class="bridge" points="{bridge_points}"/>',
    ]
    for t, label in ((0.0, "0.00"), (0.25, "0.25"), (0.5, "0.50"), (0.75, "0.75"), (1.0, "1.00")):
        x = sx(t)
        pieces.append(f'<line class="axis" x1="{x:.2f}" y1="{height-bottom}" x2="{x:.2f}" y2="{height-bottom+6}"/>')
        pieces.append(f'<text x="{x-18:.2f}" y="{height-bottom+24}" class="note">{label}s</text>')
    pieces.extend([
        f'<text x="{left+10}" y="{top+18}" class="note">branch boundary centroid — solid</text>',
        f'<text x="{left+10}" y="{top+36}" class="note">full 16-vertex bridge centroid — dashed</text>',
        f'<text x="{left+10}" y="{height-24}" class="note">Weather-parallel response (mm), range ±{bound:.3f}; neutral landmarks at 0.00 / 0.50 / 1.00 s</text>',
        '</svg>',
    ])
    return "\n".join(pieces)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--animation-evidence", required=True)
    parser.add_argument("--animation-bind-contract", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--svg", required=True)
    parser.add_argument("--animation-head", default=ANIMATION_HEAD)
    parser.add_argument("--rigging-head", default=CURRENT_RIGGING_HEAD)
    parser.add_argument("--weather-x", type=float, default=1.0)
    parser.add_argument("--weather-y", type=float, default=0.35)
    parser.add_argument("--claim-physical-wind", action="store_true")
    parser.add_argument("--claim-target-host", action="store_true")
    parser.add_argument("--claim-runtime", action="store_true")
    parser.add_argument("--claim-gameplay-or-physics", action="store_true")
    parser.add_argument("--claim-art-or-qa", action="store_true")
    args = parser.parse_args()

    report = build_report(
        load_json(Path(args.animation_evidence)),
        load_json(Path(args.animation_bind_contract)),
        load_json(Path(args.source)),
        requested_animation_head=args.animation_head,
        requested_rigging_head=args.rigging_head,
        wind_xy=(args.weather_x, args.weather_y),
        claim_physical_wind=args.claim_physical_wind,
        claim_target_host=args.claim_target_host,
        claim_runtime=args.claim_runtime,
        claim_gameplay_or_physics=args.claim_gameplay_or_physics,
        claim_art_or_qa=args.claim_art_or_qa,
    )
    output = Path(args.output)
    svg = Path(args.svg)
    output.parent.mkdir(parents=True, exist_ok=True)
    svg.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    svg.write_text(build_svg(report), encoding="utf-8")
    print(RESULT)
    print(json.dumps(report["measurements"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""VFX-owned Weather-direction observer for the north-low analytic bridge endpoint gate.

Rigging owns the endpoint map and Geometry owns the analytic bridge candidate. VFX only
measures how that exact diagnostic receiver reads in Weather's exact visual-direction
frame. This is source-space visual-response evidence, not physical wind, production
skinning, continuous surface safety, Animation, target-host, Runtime, gameplay, or
Art/Visual-QA acceptance.
"""
from __future__ import annotations

import math

from . import rear_tree_geometry_north_low_trunk_bridge_candidate as geometry_bridge
from . import rear_tree_rigging_north_low_bridge_endpoint_gate as rigging_bridge

SCHEMA = "axm.nature-vfx-north-low-analytic-bridge-weather-response/v0.1"
RESULT = "PASS_NORTH_LOW_ANALYTIC_BRIDGE_WEATHER_VISUAL_RESPONSE_GRADIENT"
RULE = "PINNED_TRUNK_ENDPOINT_PLUS_SOCKET_DRIVEN_BRANCH_ENDPOINT_CREATES_A_MEASURED_VISUAL_RESPONSE_GRADIENT__NOT_PRODUCTION_SKINNING"

RIGGING_OWNER_HEAD = "0bb186b4e22ab8911dd93675754690b68da99802"
RIGGING_OWNER_MODULE_BLOB = "352e7c83e57779aef327390f5250875e26a7b610"
RIGGING_OWNER_CONTRACT_BLOB = "c82794fb44daee0889782ce1a30294b17a3ce94a"
VFX_POLARITY_PREDECESSOR_HEAD = "687a81590db35b1b06fa3d436a726cc272a8ea77"
WEATHER_REPOSITORY = "mike-axiom-mir/axm-weather-design"
WEATHER_PR = 2
WEATHER_HEAD = "ca2eaba519e8449835b0ea6ef944b7080c3caa6a"
WEATHER_SOURCE_BLOB_SHA = "11298d447f262da8a78e43e2df68bc0346c99a2c"
WEATHER_WIND_XY = (1.0, 0.35)
WEATHER_SEMANTICS = "VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED"
TOL = 1e-12


def _centroid(points):
    if not points:
        raise ValueError("empty point set")
    n = float(len(points))
    return [sum(float(p[i]) for p in points) / n for i in range(3)]


def _sub(a, b):
    return [float(a[i]) - float(b[i]) for i in range(3)]


def _length(v):
    return math.sqrt(sum(float(x) * float(x) for x in v))


def _normalize_xy(value):
    x, y = float(value[0]), float(value[1])
    length = math.hypot(x, y)
    if length <= TOL:
        raise ValueError("Weather visual direction must be non-zero")
    return (x / length, y / length)


def _project_xy(delta, unit_wind):
    return float(delta[0]) * unit_wind[0] + float(delta[1]) * unit_wind[1]


def _cross_xy(delta, unit_wind):
    return -float(delta[0]) * unit_wind[1] + float(delta[1]) * unit_wind[0]


def _pose(source: dict, angle_deg: float):
    owner = rigging_bridge.evaluate(source)
    candidate = geometry_bridge.build_candidate(source)
    neutral = [[float(v) for v in point] for point in candidate["bridge_only"]["vertices"]]
    sides = int(geometry_bridge.SIDES)
    branch_neutral = neutral[:sides]
    trunk_neutral = neutral[sides:]
    pivot = [float(v) for v in owner["socket_identity"]["pivot_m"]]
    axis = [float(v) for v in owner["socket_identity"]["source_derived_axis"]]
    branch = rigging_bridge._pose_boundary(branch_neutral, pivot, axis, float(angle_deg))
    trunk = [list(point) for point in trunk_neutral]
    return {
        "owner": owner,
        "neutral": neutral,
        "branch_neutral": branch_neutral,
        "trunk_neutral": trunk_neutral,
        "branch": branch,
        "trunk": trunk,
        "all": branch + trunk,
    }


def evaluate(
    source: dict,
    *,
    requested_rigging_owner_head: str = RIGGING_OWNER_HEAD,
    wind_xy=WEATHER_WIND_XY,
    claim_physical_wind: bool = False,
    claim_production_skinning: bool = False,
    claim_continuous_foldover_or_collision: bool = False,
    claim_animation_acceptance: bool = False,
    claim_target_host_acceptance: bool = False,
    claim_runtime_acceptance: bool = False,
    claim_gameplay_or_physics: bool = False,
    claim_art_or_qa_acceptance: bool = False,
) -> dict:
    if requested_rigging_owner_head != RIGGING_OWNER_HEAD:
        raise ValueError("exact Rigging analytic-bridge owner head drift")
    wind = tuple(float(v) for v in wind_xy)
    if wind != WEATHER_WIND_XY:
        raise ValueError("Weather visual-direction donor drift")
    if claim_physical_wind:
        raise ValueError("Weather donor is visual direction only, not physical wind")
    if claim_production_skinning:
        raise ValueError("VFX review cannot promote diagnostic endpoints into production skinning")
    if claim_continuous_foldover_or_collision:
        raise ValueError("representative visual review cannot claim continuous foldover/collision safety")
    if claim_animation_acceptance:
        raise ValueError("static VFX review cannot claim Animation acceptance")
    if claim_target_host_acceptance:
        raise ValueError("source-space VFX review cannot claim target-host acceptance")
    if claim_runtime_acceptance:
        raise ValueError("VFX review cannot claim Runtime acceptance")
    if claim_gameplay_or_physics:
        raise ValueError("VFX review cannot claim gameplay or physics semantics")
    if claim_art_or_qa_acceptance:
        raise ValueError("VFX review cannot claim Art Direction or independent Visual QA acceptance")

    owner = rigging_bridge.evaluate(source)
    if owner.get("result") != rigging_bridge.RESULT:
        raise ValueError("exact Rigging bridge endpoint prerequisite is not green")
    constraint = owner["endpoint_constraint"]
    if constraint["mode"] != "ANALYTIC_BRIDGE_TWO_BOUNDARY_DIAGNOSTIC_PIN":
        raise ValueError("Rigging endpoint mode drift")
    if constraint["branch_endpoint_diagnostic_weight"] != 1.0 or constraint["trunk_endpoint_diagnostic_weight"] != 0.0:
        raise ValueError("Rigging diagnostic endpoint ownership drift")
    if constraint["interior_vertices"] != 0:
        raise ValueError("unexpected bridge interior vertex field")

    unit_wind = _normalize_xy(wind)
    angles = tuple(float(v) for v in owner["representative_pose_evidence"]["angles_deg"])
    if angles != rigging_bridge.REPRESENTATIVE_ANGLES_DEG:
        raise ValueError("Rigging representative pose schedule drift")

    neutral_pose = _pose(source, 0.0)
    neutral_branch_centroid = _centroid(neutral_pose["branch_neutral"])
    neutral_trunk_centroid = _centroid(neutral_pose["trunk_neutral"])
    neutral_bridge_centroid = _centroid(neutral_pose["neutral"])

    rows = []
    polarity_violations = 0
    max_trunk_drift = 0.0
    max_half_gradient_residual = 0.0
    for angle in angles:
        posed = _pose(source, angle)
        branch_delta = _sub(_centroid(posed["branch"]), neutral_branch_centroid)
        trunk_delta = _sub(_centroid(posed["trunk"]), neutral_trunk_centroid)
        bridge_delta = _sub(_centroid(posed["all"]), neutral_bridge_centroid)
        half_branch_delta = [0.5 * value for value in branch_delta]
        half_gradient_residual = _length(_sub(bridge_delta, half_branch_delta))
        trunk_drift = _length(trunk_delta)

        branch_parallel = _project_xy(branch_delta, unit_wind)
        bridge_parallel = _project_xy(bridge_delta, unit_wind)
        branch_cross = _cross_xy(branch_delta, unit_wind)
        bridge_cross = _cross_xy(bridge_delta, unit_wind)

        if angle < -TOL and branch_parallel <= 0.0:
            polarity_violations += 1
        if angle > TOL and branch_parallel >= 0.0:
            polarity_violations += 1
        if abs(angle) <= TOL and abs(branch_parallel) > TOL:
            polarity_violations += 1

        max_trunk_drift = max(max_trunk_drift, trunk_drift)
        max_half_gradient_residual = max(max_half_gradient_residual, half_gradient_residual)
        rows.append({
            "child_angle_deg": angle,
            "branch_boundary_centroid_delta_m": branch_delta,
            "branch_weather_parallel_m": branch_parallel,
            "branch_weather_cross_m": branch_cross,
            "branch_vertical_m": branch_delta[2],
            "bridge_vertex_centroid_delta_m": bridge_delta,
            "bridge_weather_parallel_m": bridge_parallel,
            "bridge_weather_cross_m": bridge_cross,
            "bridge_vertical_m": bridge_delta[2],
            "trunk_boundary_centroid_delta_m": trunk_delta,
            "trunk_centroid_drift_m": trunk_drift,
            "bridge_vs_half_branch_centroid_residual_m": half_gradient_residual,
        })

    by_angle = {row["child_angle_deg"]: row for row in rows}
    minus5 = by_angle[-5.0]
    neutral = by_angle[0.0]
    plus5 = by_angle[5.0]
    checks = {
        "exact_rigging_bridge_owner_reexecuted": owner["result"] == rigging_bridge.RESULT,
        "exact_five_owner_witnesses_reused": len(rows) == 5,
        "weather_semantics_remain_visual_only": WEATHER_SEMANTICS == "VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED",
        "north_low_minus_five_points_downwind": minus5["branch_weather_parallel_m"] > 0.0,
        "north_low_plus_five_points_upwind": plus5["branch_weather_parallel_m"] < 0.0,
        "all_owner_witnesses_preserve_prior_weather_polarity": polarity_violations == 0,
        "neutral_branch_weather_response_is_zero": abs(neutral["branch_weather_parallel_m"]) <= TOL,
        "pinned_trunk_centroid_remains_fixed": max_trunk_drift <= TOL,
        "sixteen_vertex_bridge_centroid_tracks_exact_half_branch_endpoint_response": max_half_gradient_residual <= TOL,
        "bridge_response_is_materially_nonzero_at_both_extremes": abs(minus5["bridge_weather_parallel_m"]) > 1e-6 and abs(plus5["bridge_weather_parallel_m"]) > 1e-6,
    }
    if not all(checks.values()):
        raise ValueError(f"north-low analytic bridge Weather visual-response invariant failed: {checks}")

    return {
        "schema": SCHEMA,
        "result": RESULT,
        "reusable_rule": RULE,
        "rigging_owner": {
            "pull_request": 14,
            "head": RIGGING_OWNER_HEAD,
            "module_blob": RIGGING_OWNER_MODULE_BLOB,
            "contract_blob": RIGGING_OWNER_CONTRACT_BLOB,
            "result": owner["result"],
        },
        "vfx_polarity_predecessor": {"pull_request": 25, "head": VFX_POLARITY_PREDECESSOR_HEAD},
        "weather_visual_direction_donor": {
            "repository": WEATHER_REPOSITORY,
            "pull_request": WEATHER_PR,
            "head": WEATHER_HEAD,
            "source_blob_sha": WEATHER_SOURCE_BLOB_SHA,
            "wind_xy": list(WEATHER_WIND_XY),
            "normalized_wind_xy": list(unit_wind),
            "semantics": WEATHER_SEMANTICS,
        },
        "receiver": {
            "geometry_result": owner["geometry_result_consumed"],
            "endpoint_mode": constraint["mode"],
            "branch_boundary_vertices": constraint["branch_boundary_vertices"],
            "trunk_boundary_vertices": constraint["trunk_boundary_vertices"],
            "interior_vertices": constraint["interior_vertices"],
            "branch_endpoint_diagnostic_weight": constraint["branch_endpoint_diagnostic_weight"],
            "trunk_endpoint_diagnostic_weight": constraint["trunk_endpoint_diagnostic_weight"],
        },
        "measurements": {
            "rows": rows,
            "weather_polarity_sign_violations": polarity_violations,
            "maximum_trunk_centroid_drift_m": max_trunk_drift,
            "maximum_bridge_vs_half_branch_centroid_residual_m": max_half_gradient_residual,
            "minus5_branch_downwind_parallel_m": minus5["branch_weather_parallel_m"],
            "minus5_bridge_downwind_parallel_m": minus5["bridge_weather_parallel_m"],
            "plus5_branch_upwind_parallel_m": plus5["branch_weather_parallel_m"],
            "plus5_bridge_upwind_parallel_m": plus5["bridge_weather_parallel_m"],
            "owner_minimum_sampled_bridge_triangle_area_m2": owner["representative_pose_evidence"]["minimum_bridge_triangle_area_m2"],
            "owner_minimum_sampled_paired_bridge_span_m": owner["representative_pose_evidence"]["minimum_paired_bridge_span_m"],
        },
        "decision": {
            "state": "KEEP_VISUAL_DIRECTION_CONTINUITY_ACROSS_ANALYTIC_BRIDGE_DIAGNOSTIC__NO_AUTOMATIC_SKINNING_OR_MOTION_ADOPTION",
            "automatic_weather_motion_adoption": False,
            "automatic_rigging_change": False,
            "automatic_geometry_change": False,
            "automatic_animation_change": False,
            "automatic_target_host_or_runtime_adoption": False,
        },
        "checks": checks,
        "truth_boundary": {
            "source_space_visual_response_evidence_only": True,
            "physical_wind_speed_force_drag_or_turbulence_claimed": False,
            "production_skinning_or_blending_claimed": False,
            "indexed_connected_junction_claimed": False,
            "continuous_bridge_foldover_collision_or_self_intersection_claimed": False,
            "botanical_mechanics_or_biological_rom_claimed": False,
            "animation_timing_interpolation_or_playback_claimed": False,
            "technical_art_target_host_claimed": False,
            "runtime_controller_device_or_performance_claimed": False,
            "gameplay_damage_collision_or_physics_claimed": False,
            "art_direction_or_independent_visual_qa_acceptance_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }


def build_review_svg(source: dict) -> str:
    report = evaluate(source)
    angles = (-5.0, 0.0, 5.0)
    width, height = 1200, 430
    panel_w = 380
    margin = 30
    weather = _normalize_xy(WEATHER_WIND_XY)

    poses = {angle: _pose(source, angle) for angle in angles}
    all_xy = []
    for pose in poses.values():
        all_xy.extend((float(v[0]), float(v[1])) for v in pose["branch"] + pose["trunk"])
    min_x = min(x for x, _ in all_xy)
    max_x = max(x for x, _ in all_xy)
    min_y = min(y for _, y in all_xy)
    max_y = max(y for _, y in all_xy)
    span = max(max_x - min_x, max_y - min_y, 1e-6)
    scale = 260.0 / span
    cx = (min_x + max_x) * 0.5
    cy = (min_y + max_y) * 0.5

    pieces = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:monospace;fill:#111}.trunk{fill:none;stroke:#555;stroke-width:2}.branch{fill:none;stroke:#111;stroke-width:3}.span{stroke:#aaa;stroke-width:1}.wind{stroke:#222;stroke-width:3}.note{font-size:12px;fill:#555}</style>',
        '<text x="24" y="28" font-size="17px">north-low analytic bridge Weather-direction review — source-space diagnostic only</text>',
        '<text x="24" y="48" class="note">branch boundary moves with Rigging socket; analytic trunk boundary stays pinned; lines show eight paired bridge spans</text>',
    ]

    for panel_index, angle in enumerate(angles):
        x0 = 20 + panel_index * panel_w
        y0 = 75
        pose = poses[angle]

        def map_point(p):
            px = x0 + panel_w * 0.5 + (float(p[0]) - cx) * scale
            py = y0 + 160.0 - (float(p[1]) - cy) * scale
            return px, py

        branch_pts = [map_point(p) for p in pose["branch"]]
        trunk_pts = [map_point(p) for p in pose["trunk"]]
        pieces.append(f'<rect x="{x0}" y="{y0}" width="350" height="285" fill="none" stroke="#ddd"/>')
        for b, t in zip(branch_pts, trunk_pts):
            pieces.append(f'<line class="span" x1="{b[0]:.2f}" y1="{b[1]:.2f}" x2="{t[0]:.2f}" y2="{t[1]:.2f}"/>')
        pieces.append('<polyline class="trunk" points="' + ' '.join(f'{x:.2f},{y:.2f}' for x, y in trunk_pts + [trunk_pts[0]]) + '"/>')
        pieces.append('<polyline class="branch" points="' + ' '.join(f'{x:.2f},{y:.2f}' for x, y in branch_pts + [branch_pts[0]]) + '"/>')
        row = next(row for row in report["measurements"]["rows"] if row["child_angle_deg"] == angle)
        pieces.append(f'<text x="{x0+14}" y="{y0+25}" font-size="14px">child {angle:+.1f} deg</text>')
        pieces.append(f'<text x="{x0+14}" y="{y0+258}" class="note">branch parallel {row["branch_weather_parallel_m"]*1000:+.3f} mm</text>')
        pieces.append(f'<text x="{x0+14}" y="{y0+276}" class="note">bridge centroid {row["bridge_weather_parallel_m"]*1000:+.3f} mm</text>')
        arrow_x = x0 + 250
        arrow_y = y0 + 35
        pieces.append(f'<line class="wind" x1="{arrow_x}" y1="{arrow_y}" x2="{arrow_x + weather[0]*55:.2f}" y2="{arrow_y - weather[1]*55:.2f}"/>')
        pieces.append(f'<text x="{arrow_x}" y="{arrow_y+18}" class="note">Weather visual dir</text>')

    pieces.append('<text x="24" y="405" class="note">Top-down XY review. This does not prove physical wind, connected production skinning, continuous foldover/collision safety, target-host playback, gameplay, or aesthetic acceptance.</text>')
    pieces.append('</svg>')
    return "\n".join(pieces) + "\n"

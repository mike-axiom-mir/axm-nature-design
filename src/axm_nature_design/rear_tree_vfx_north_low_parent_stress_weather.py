"""VFX-owned Weather-direction review for the detached north-low Animation rebind.

Consumes the exact current Animation parent-stress loop and Weather's exact visual XY
direction.  This module does not author wind physics, Animation timing, Rigging,
Runtime/controller behavior, gameplay/physics, botanical motion, or aesthetic acceptance.
"""
from __future__ import annotations

import math

from . import rear_tree_animation_north_low_parent_exclusion_temporal_rebind as animation
from . import rear_tree_rigging as historical
from . import rear_tree_rigging_north_low_parent_influence_gate as rig_gate
from . import rear_tree_rigging_primary_branch_family as family
from .organic_form import build_mesh, digest, validate_source

SCHEMA = "axm.nature-vfx-north-low-parent-stress-weather-response/v0.1"
RESULT = "PASS_NORTH_LOW_DETACHED_TEMPORAL_WEATHER_RESPONSE_PARENT_STRESS_DISCRIMINATION"
ANIMATION_OWNER_HEAD = "5cacd61e22433b0c33f29111827283b81cc0ba0d"
RIGGING_OWNER_HEAD = "69640e558f0c1ac59d4d0e3155676e0967a03d04"
VFX_STATIC_PREDECESSOR_HEAD = "687a81590db35b1b06fa3d436a726cc272a8ea77"
WEATHER_REPOSITORY = "mike-axiom-mir/axm-weather-design"
WEATHER_PR = 2
WEATHER_HEAD = "ca2eaba519e8449835b0ea6ef944b7080c3caa6a"
WEATHER_SOURCE_BLOB_SHA = "11298d447f262da8a78e43e2df68bc0346c99a2c"
WEATHER_WIND_XY = (1.0, 0.35)
WEATHER_SEMANTICS = "VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED"
TOL = 1e-12


def _normalize_xy(v):
    x, y = float(v[0]), float(v[1])
    length = math.hypot(x, y)
    if length <= TOL:
        raise ValueError("Weather visual direction must be non-zero")
    return (x / length, y / length)


def _centroid(vertices):
    if not vertices:
        raise ValueError("empty selected child partition")
    n = float(len(vertices))
    return [sum(float(v[i]) for v in vertices) / n for i in range(3)]


def _sub(a, b):
    return [float(a[i]) - float(b[i]) for i in range(3)]


def _distance(a, b):
    return math.sqrt(sum((float(a[i]) - float(b[i])) ** 2 for i in range(3)))


def _project_xy(delta, unit_wind):
    return float(delta[0]) * unit_wind[0] + float(delta[1]) * unit_wind[1]


def _cross_xy(delta, unit_wind):
    return -float(delta[0]) * unit_wind[1] + float(delta[1]) * unit_wind[0]


def evaluate(
    source: dict,
    geometry_contract: dict,
    *,
    wind_xy=WEATHER_WIND_XY,
    claim_physical_wind: bool = False,
    claim_botanical_motion: bool = False,
    claim_animation_authorship: bool = False,
    claim_target_engine_playback: bool = False,
    claim_runtime_acceptance: bool = False,
    claim_gameplay_or_physics: bool = False,
    claim_art_or_qa_acceptance: bool = False,
) -> dict:
    """Measure the exact accepted Animation frames in Weather's visual frame."""
    validate_source(source)
    wind = tuple(float(x) for x in wind_xy)
    if wind != WEATHER_WIND_XY:
        raise ValueError("Weather visual-direction donor drift")
    if claim_physical_wind:
        raise ValueError("Weather source is visual direction only, not physical wind")
    if claim_botanical_motion:
        raise ValueError("diagnostic articulation is not botanical motion acceptance")
    if claim_animation_authorship:
        raise ValueError("VFX may not author or adopt Animation timing")
    if claim_target_engine_playback:
        raise ValueError("source-space VFX evidence cannot claim target-engine playback")
    if claim_runtime_acceptance:
        raise ValueError("VFX evidence cannot claim Runtime acceptance")
    if claim_gameplay_or_physics:
        raise ValueError("VFX evidence cannot claim gameplay or physics")
    if claim_art_or_qa_acceptance:
        raise ValueError("VFX evidence cannot claim Art or QA acceptance")

    owner = animation.evaluate(source, geometry_contract)
    if owner["result"] != animation.RESULT:
        raise ValueError("current Animation north-low parent-stress prerequisite is not green")
    if owner["motion_scope"]["attachment_mode"] != "DETACHED_DIAGNOSTIC_CHILD_SOCKET_ONLY":
        raise ValueError("current Animation attachment mode drift")
    if owner["measurements"]["maximum_parent_command_leak_m"] > TOL:
        raise ValueError("Animation owner reports accepted parent-command leakage")

    rig = rig_gate.evaluate(source)
    if rig["result"] != rig_gate.RESULT:
        raise ValueError("current Rigging north-low parent gate prerequisite is not green")

    mesh = build_mesh(source)
    if digest(mesh) != family.EXPECTED_MIGRATED_MESH_DIGEST:
        raise ValueError("exact Geometry-migrated receiver identity drift")
    neutral = [[float(value) for value in vertex] for vertex in mesh["vertices"]]
    probe = family._probe_branch(source, mesh, rig_gate.CHILD_BRANCH_ID)
    selected = [int(value) for value in probe["selected_vertex_indices"]]
    if len(selected) != 52 or int(probe["selected_triangles"]) != 72:
        raise ValueError("north-low selected partition drift")

    child_pivot = [float(value) for value in probe["joint_pivot_m"]]
    child_axis = [float(value) for value in probe["source_derived_axis"]]
    parent_pivot = [float(value) for value in rig["parent_frame"]["pivot_m"]]
    parent_axis = [float(value) for value in rig["parent_frame"]["source_derived_axis"]]
    neutral_selected = [neutral[index] for index in selected]
    neutral_centroid = _centroid(neutral_selected)
    unit_wind = _normalize_xy(wind)

    rows = []
    max_owner_pose_digest_mismatches = 0
    max_accepted_vs_counterfactual_parallel_delta = 0.0
    max_accepted_vs_counterfactual_cross_delta = 0.0
    max_accepted_vs_counterfactual_vertical_delta = 0.0
    max_accepted_vs_counterfactual_vertex_delta = 0.0
    sign_violation_count = 0

    for owner_row in owner["samples"]:
        child_angle = float(owner_row["north_low_child_angle_deg"])
        parent_command = float(owner_row["upper_trunk_parent_stress_command_deg"])
        accepted = [
            historical._rotate_about_axis(neutral[index], child_pivot, child_axis, child_angle)
            for index in selected
        ]
        accepted_digest = digest({"vertices": accepted, "selected_vertex_indices": selected})
        if accepted_digest != owner_row["pose_digest"]:
            max_owner_pose_digest_mismatches += 1

        counter_pivot = historical._rotate_about_axis(
            child_pivot, parent_pivot, parent_axis, parent_command
        )
        counter_axis = animation._rotate_axis(child_axis, parent_axis, parent_command)
        counterfactual = []
        for index in selected:
            parented = historical._rotate_about_axis(
                neutral[index], parent_pivot, parent_axis, parent_command
            )
            counterfactual.append(
                historical._rotate_about_axis(
                    parented, counter_pivot, counter_axis, child_angle
                )
            )

        accepted_delta = _sub(_centroid(accepted), neutral_centroid)
        counter_delta = _sub(_centroid(counterfactual), neutral_centroid)
        accepted_parallel = _project_xy(accepted_delta, unit_wind)
        accepted_cross = _cross_xy(accepted_delta, unit_wind)
        counter_parallel = _project_xy(counter_delta, unit_wind)
        counter_cross = _cross_xy(counter_delta, unit_wind)

        if abs(child_angle) > TOL:
            if child_angle < 0.0 and accepted_parallel <= 0.0:
                sign_violation_count += 1
            if child_angle > 0.0 and accepted_parallel >= 0.0:
                sign_violation_count += 1

        vertex_delta = max(
            (_distance(accepted[i], counterfactual[i]) for i in range(len(selected))),
            default=0.0,
        )
        max_accepted_vs_counterfactual_parallel_delta = max(
            max_accepted_vs_counterfactual_parallel_delta,
            abs(accepted_parallel - counter_parallel),
        )
        max_accepted_vs_counterfactual_cross_delta = max(
            max_accepted_vs_counterfactual_cross_delta,
            abs(accepted_cross - counter_cross),
        )
        max_accepted_vs_counterfactual_vertical_delta = max(
            max_accepted_vs_counterfactual_vertical_delta,
            abs(accepted_delta[2] - counter_delta[2]),
        )
        max_accepted_vs_counterfactual_vertex_delta = max(
            max_accepted_vs_counterfactual_vertex_delta,
            vertex_delta,
        )
        rows.append(
            {
                "index": int(owner_row["index"]),
                "time_s": float(owner_row["time_s"]),
                "child_angle_deg": child_angle,
                "parent_stress_command_deg": parent_command,
                "accepted_centroid_delta_m": accepted_delta,
                "accepted_weather_parallel_m": accepted_parallel,
                "accepted_weather_cross_m": accepted_cross,
                "accepted_vertical_m": accepted_delta[2],
                "counterfactual_weather_parallel_m": counter_parallel,
                "counterfactual_weather_cross_m": counter_cross,
                "counterfactual_vertical_m": counter_delta[2],
                "accepted_vs_counterfactual_vertex_delta_m": vertex_delta,
                "owner_pose_digest": owner_row["pose_digest"],
                "reconstructed_pose_digest": accepted_digest,
            }
        )

    by_index = {row["index"]: row for row in rows}
    neutral_indices = (0, 20, 40)
    neutral_parallel_error = max(abs(by_index[i]["accepted_weather_parallel_m"]) for i in neutral_indices)
    endpoint_parallel_error = abs(rows[0]["accepted_weather_parallel_m"] - rows[-1]["accepted_weather_parallel_m"])
    peak_downwind = by_index[10]["accepted_weather_parallel_m"]
    peak_upwind = by_index[30]["accepted_weather_parallel_m"]

    checks = {
        "exact_animation_owner_reexecuted": owner["result"] == animation.RESULT,
        "owner_pose_digests_reproduced_exactly": max_owner_pose_digest_mismatches == 0,
        "sample_count_is_41": len(rows) == 41,
        "detached_parent_exclusion_remains_zero_leak": owner["measurements"]["maximum_parent_command_leak_m"] <= TOL,
        "weather_source_semantics_remain_visual_only": WEATHER_SEMANTICS == "VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED",
        "all_nonzero_samples_preserve_static_weather_polarity": sign_violation_count == 0,
        "neutral_landmarks_are_weather_parallel_zero": neutral_parallel_error <= TOL,
        "endpoint_weather_parallel_closure": endpoint_parallel_error <= TOL,
        "minus5_peak_points_downwind": peak_downwind > 0.0,
        "plus5_peak_points_upwind": peak_upwind < 0.0,
        "wrong_parent_counterfactual_is_visually_direction_discriminating": max_accepted_vs_counterfactual_parallel_delta > 1e-6,
        "wrong_parent_counterfactual_is_geometry_discriminating": max_accepted_vs_counterfactual_vertex_delta > 1e-6,
    }
    if not all(checks.values()):
        raise ValueError(f"north-low temporal Weather-response invariant failed: {checks}")

    return {
        "schema": SCHEMA,
        "result": RESULT,
        "animation_owner": {
            "pull_request": 26,
            "head": ANIMATION_OWNER_HEAD,
            "result": owner["result"],
            "timing": owner["timing"],
            "motion_scope": owner["motion_scope"],
        },
        "rigging_owner": {"pull_request": 14, "head": RIGGING_OWNER_HEAD},
        "vfx_static_predecessor": {"pull_request": 25, "head": VFX_STATIC_PREDECESSOR_HEAD},
        "weather_visual_direction_donor": {
            "repository": WEATHER_REPOSITORY,
            "pull_request": WEATHER_PR,
            "head": WEATHER_HEAD,
            "source_blob_sha": WEATHER_SOURCE_BLOB_SHA,
            "wind_xy": list(WEATHER_WIND_XY),
            "normalized_wind_xy": list(unit_wind),
            "semantics": WEATHER_SEMANTICS,
        },
        "measurements": {
            "sample_count": len(rows),
            "rows": rows,
            "owner_pose_digest_mismatches": max_owner_pose_digest_mismatches,
            "weather_polarity_sign_violations": sign_violation_count,
            "neutral_weather_parallel_error_m": neutral_parallel_error,
            "endpoint_weather_parallel_error_m": endpoint_parallel_error,
            "minus5_peak_downwind_parallel_m": peak_downwind,
            "plus5_peak_upwind_parallel_m": peak_upwind,
            "maximum_accepted_vs_wrong_parent_weather_parallel_delta_m": max_accepted_vs_counterfactual_parallel_delta,
            "maximum_accepted_vs_wrong_parent_weather_cross_delta_m": max_accepted_vs_counterfactual_cross_delta,
            "maximum_accepted_vs_wrong_parent_vertical_delta_m": max_accepted_vs_counterfactual_vertical_delta,
            "maximum_accepted_vs_wrong_parent_vertex_delta_m": max_accepted_vs_counterfactual_vertex_delta,
        },
        "decision": {
            "state": "KEEP_DETACHED_CHILD_WEATHER_POLARITY_THROUGH_ANIMATION_PARENT_STRESS__REJECT_PARENT_INHERITANCE_FOR_THIS_RECEIVER",
            "automatic_weather_motion_adoption": False,
            "automatic_animation_change": False,
            "automatic_runtime_adoption": False,
        },
        "checks": checks,
        "truth_boundary": {
            "source_space_visual_response_evidence_only": True,
            "physical_wind_claimed": False,
            "botanical_or_biological_motion_claimed": False,
            "animation_authorship_or_timing_change_claimed": False,
            "target_engine_playback_claimed": False,
            "runtime_controller_or_device_claimed": False,
            "gameplay_or_physics_claimed": False,
            "art_direction_or_visual_qa_acceptance_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }


def build_review_svg(source: dict, geometry_contract: dict) -> str:
    report = evaluate(source, geometry_contract)
    rows = report["measurements"]["rows"]
    width, height = 980, 500
    left, right = 70, 930
    top, bottom = 80, 420
    xscale = (right - left) / animation.DURATION_S
    values = [row["accepted_weather_parallel_m"] for row in rows] + [
        row["counterfactual_weather_parallel_m"] for row in rows
    ]
    vmax = max(max(abs(v) for v in values), 1e-9)
    yscale = (bottom - top) / (2.2 * vmax)
    y0 = (top + bottom) / 2.0

    def points(key):
        return " ".join(
            f"{left + row['time_s'] * xscale:.2f},{y0 - row[key] * yscale:.2f}" for row in rows
        )

    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:monospace;font-size:13px;fill:#111}.axis{stroke:#999;stroke-width:1}.accepted{fill:none;stroke:#111;stroke-width:3}.wrong{fill:none;stroke:#777;stroke-width:2;stroke-dasharray:7 5}</style>',
        '<text x="24" y="28">north-low temporal Weather-parallel response under parent stress (review only)</text>',
        '<text x="24" y="50">solid = accepted detached child; dashed = forbidden inherited-parent counterfactual</text>',
        f'<line class="axis" x1="{left}" y1="{y0:.2f}" x2="{right}" y2="{y0:.2f}"/>',
        f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" y2="{bottom}"/>',
        f'<polyline class="accepted" points="{points("accepted_weather_parallel_m")}"/>',
        f'<polyline class="wrong" points="{points("counterfactual_weather_parallel_m")}"/>',
        f'<text x="{left}" y="{bottom + 28}">0.0 s</text>',
        f'<text x="{right - 40}" y="{bottom + 28}">1.0 s</text>',
        f'<text x="{left + 8}" y="{top + 16}">downwind +</text>',
        f'<text x="{left + 8}" y="{bottom - 8}">upwind -</text>',
        '<text x="680" y="470">Weather direction [1.0, 0.35] visual-only</text>',
        '</svg>',
        '',
    ])

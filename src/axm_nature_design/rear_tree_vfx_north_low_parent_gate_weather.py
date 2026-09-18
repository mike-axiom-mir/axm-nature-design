"""VFX review-only Weather-direction continuity for gated north-low articulation.

Consumes the exact Rigging parent-influence exclusion gate and Weather's exact visual
XY direction. This module does not author physical wind, Animation timing, Runtime
behavior, gameplay/physics, biological motion, or aesthetic acceptance.
"""
from __future__ import annotations

import math

from . import rear_tree_rigging as historical
from . import rear_tree_rigging_north_low_parent_influence_gate as gate
from . import rear_tree_rigging_primary_branch_family as family
from .organic_form import build_mesh, validate_source

SCHEMA = "axm.nature-vfx-north-low-parent-gate-weather-direction/v0.1"
RESULT = "PASS_NORTH_LOW_WEATHER_VISUAL_DIRECTION_PARENT_EXCLUSION_STABILITY"
RIGGING_OWNER_HEAD = "975931b11555d156e04e2ab12e9756fc6c9598a3"
VFX_SIGN_PREDECESSOR_HEAD = "ef7b35af27d5ca98a6447c1e33be07863e387305"
WEATHER_REPOSITORY = "mike-axiom-mir/axm-weather-design"
WEATHER_PR = 2
WEATHER_HEAD = "ca2eaba519e8449835b0ea6ef944b7080c3caa6a"
WEATHER_SOURCE_BLOB_SHA = "11298d447f262da8a78e43e2df68bc0346c99a2c"
WEATHER_WIND_XY = (1.0, 0.35)
WEATHER_SEMANTICS = "VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED"
PARENT_ANGLES_DEG = gate.PARENT_REPRESENTATIVE_ANGLES_DEG
CHILD_ANGLES_DEG = gate.CHILD_REPRESENTATIVE_ANGLES_DEG
TOL = 1e-12

# Exact predecessor values from VFX PR #17 for the same north-low socket while
# the upper-trunk parent was neutral.
PREDECESSOR_NORTH_LOW = {
    "preferred_angle_deg": -5.0,
    "negative_projection_m": 0.017583768804344528,
    "neutral_projection_m": 0.0,
    "positive_projection_m": -0.015876223842106312,
    "separation_m": 0.03345999264645084,
}


def _normalize_xy(v):
    x, y = float(v[0]), float(v[1])
    length = math.hypot(x, y)
    if length <= TOL:
        raise ValueError("Weather visual direction must be non-zero")
    return (x / length, y / length)


def _centroid(vertices):
    if not vertices:
        raise ValueError("empty selected child partition")
    n = len(vertices)
    return [sum(float(v[i]) for v in vertices) / n for i in range(3)]


def _project_xy(delta, unit_wind):
    return float(delta[0]) * unit_wind[0] + float(delta[1]) * unit_wind[1]


def _cross_xy(delta, unit_wind):
    return -float(delta[0]) * unit_wind[1] + float(delta[1]) * unit_wind[0]


def _selected_pose(neutral_vertices, selected_indices, pivot, axis, angle_deg):
    return [
        historical._rotate_about_axis(neutral_vertices[index], pivot, axis, angle_deg)
        for index in selected_indices
    ]


def evaluate(
    source: dict,
    *,
    wind_xy=WEATHER_WIND_XY,
    parent_angles_deg=PARENT_ANGLES_DEG,
    child_angles_deg=CHILD_ANGLES_DEG,
    claim_physical_wind: bool = False,
    claim_animation_adoption: bool = False,
    claim_runtime_acceptance: bool = False,
    claim_gameplay_or_physics: bool = False,
    claim_biological_motion: bool = False,
    claim_art_or_qa_acceptance: bool = False,
) -> dict:
    validate_source(source)
    wind = tuple(float(x) for x in wind_xy)
    if wind != WEATHER_WIND_XY:
        raise ValueError("Weather visual-direction donor drift")
    parents = tuple(float(x) for x in parent_angles_deg)
    children = tuple(float(x) for x in child_angles_deg)
    if parents != PARENT_ANGLES_DEG:
        raise ValueError("VFX may not widen or retime Rigging parent witnesses")
    if children != CHILD_ANGLES_DEG:
        raise ValueError("VFX may not widen or retime Rigging child witnesses")
    if claim_physical_wind:
        raise ValueError("Weather source is visual direction only, not physical wind")
    if claim_animation_adoption:
        raise ValueError("VFX coordinate evidence cannot adopt Animation motion")
    if claim_runtime_acceptance:
        raise ValueError("VFX coordinate evidence cannot claim Runtime acceptance")
    if claim_gameplay_or_physics:
        raise ValueError("VFX coordinate evidence cannot claim gameplay or physics")
    if claim_biological_motion:
        raise ValueError("Rigging diagnostic articulation is not biological motion")
    if claim_art_or_qa_acceptance:
        raise ValueError("VFX coordinate evidence cannot claim Art or QA acceptance")

    gate_report = gate.evaluate(source)
    if gate_report["result"] != gate.RESULT:
        raise ValueError("exact Rigging parent-influence gate is not green")
    if gate_report["rigging_constraint"]["upper_trunk_parent_influence_enabled_for_north_low"]:
        raise ValueError("north-low parent influence is no longer gated")
    if gate_report["measurements"]["maximum_gated_parent_command_leak_m"] > TOL:
        raise ValueError("Rigging gate reports parent-command leakage")

    rig = family.evaluate(source)
    if rig["result"] != family.RESULT:
        raise ValueError("exact five-socket Rigging family prerequisite is not green")
    mesh = build_mesh(source)
    neutral = [[float(x) for x in row] for row in mesh["vertices"]]
    probe = family._probe_branch(source, mesh, "north-low")
    selected = list(probe["selected_vertex_indices"])
    if len(selected) != 52 or int(probe["selected_triangles"]) != 72:
        raise ValueError("north-low exact Rigging child partition drift")
    pivot = [float(x) for x in probe["joint_pivot_m"]]
    axis = [float(x) for x in probe["source_derived_axis"]]
    neutral_selected = [neutral[index] for index in selected]
    neutral_centroid = _centroid(neutral_selected)
    unit_wind = _normalize_xy(wind)

    rows = []
    baseline_by_child = {}
    maximum_parent_projection_drift = 0.0
    maximum_parent_cross_drift = 0.0
    maximum_parent_vertical_drift = 0.0

    for parent_angle in parents:
        witnesses = []
        for child_angle in children:
            posed = _selected_pose(neutral, selected, pivot, axis, child_angle)
            centroid = _centroid(posed)
            delta = [centroid[i] - neutral_centroid[i] for i in range(3)]
            parallel = _project_xy(delta, unit_wind)
            cross = _cross_xy(delta, unit_wind)
            vertical = delta[2]
            witness = {
                "parent_angle_deg": parent_angle,
                "child_angle_deg": child_angle,
                "centroid_delta_m": delta,
                "weather_parallel_m": parallel,
                "weather_cross_m": cross,
                "vertical_m": vertical,
            }
            witnesses.append(witness)
            previous = baseline_by_child.setdefault(child_angle, witness)
            maximum_parent_projection_drift = max(
                maximum_parent_projection_drift,
                abs(parallel - previous["weather_parallel_m"]),
            )
            maximum_parent_cross_drift = max(
                maximum_parent_cross_drift,
                abs(cross - previous["weather_cross_m"]),
            )
            maximum_parent_vertical_drift = max(
                maximum_parent_vertical_drift,
                abs(vertical - previous["vertical_m"]),
            )
        rows.append({"parent_angle_deg": parent_angle, "witnesses": witnesses})

    neutral_parent = next(row for row in rows if abs(row["parent_angle_deg"]) <= TOL)
    by_child = {float(row["child_angle_deg"]): row for row in neutral_parent["witnesses"]}
    neg = by_child[-5.0]["weather_parallel_m"]
    zero = by_child[0.0]["weather_parallel_m"]
    pos = by_child[5.0]["weather_parallel_m"]
    separation = abs(pos - neg)
    preferred = -5.0 if neg > pos else 5.0

    predecessor_reproduced = (
        preferred == PREDECESSOR_NORTH_LOW["preferred_angle_deg"]
        and abs(neg - PREDECESSOR_NORTH_LOW["negative_projection_m"]) <= TOL
        and abs(zero - PREDECESSOR_NORTH_LOW["neutral_projection_m"]) <= TOL
        and abs(pos - PREDECESSOR_NORTH_LOW["positive_projection_m"]) <= TOL
        and abs(separation - PREDECESSOR_NORTH_LOW["separation_m"]) <= TOL
    )
    if not predecessor_reproduced:
        raise ValueError("north-low Weather-sign predecessor did not reproduce")
    if maximum_parent_projection_drift > TOL:
        raise ValueError("Weather-parallel child response changed across gated parent commands")
    if maximum_parent_cross_drift > TOL or maximum_parent_vertical_drift > TOL:
        raise ValueError("gated child response changed across parent commands")

    checks = {
        "exact_rigging_gate_reexecuted": gate_report["result"] == gate.RESULT,
        "parent_influence_remains_disabled": not gate_report["rigging_constraint"]["upper_trunk_parent_influence_enabled_for_north_low"],
        "parent_command_leak_is_zero": gate_report["measurements"]["maximum_gated_parent_command_leak_m"] <= TOL,
        "counterfactual_parent_inheritance_is_discriminating": gate_report["measurements"]["maximum_counterfactual_inherited_output_delta_m"] > 0.01,
        "north_low_partition_preserved": len(selected) == 52 and int(probe["selected_triangles"]) == 72,
        "exact_weather_visual_direction": wind == WEATHER_WIND_XY,
        "visual_only_weather_semantics": WEATHER_SEMANTICS == "VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED",
        "neutral_projection_is_zero": abs(zero) <= TOL,
        "predecessor_sign_map_reproduced": predecessor_reproduced,
        "preferred_sign_remains_negative_five": preferred == -5.0,
        "weather_parallel_response_parent_invariant": maximum_parent_projection_drift <= TOL,
        "full_centroid_response_parent_invariant": maximum_parent_cross_drift <= TOL and maximum_parent_vertical_drift <= TOL,
    }
    if not all(checks.values()):
        raise ValueError("north-low Weather-direction parent-gate invariant failed")

    return {
        "schema": SCHEMA,
        "result": RESULT,
        "nature_rigging_owner": {
            "pull_request": 14,
            "head": RIGGING_OWNER_HEAD,
            "result": gate_report["result"],
        },
        "vfx_sign_predecessor": {
            "pull_request": 17,
            "head": VFX_SIGN_PREDECESSOR_HEAD,
            "north_low": PREDECESSOR_NORTH_LOW,
            "reproduced": predecessor_reproduced,
        },
        "weather_visual_direction_donor": {
            "repository": WEATHER_REPOSITORY,
            "pull_request": WEATHER_PR,
            "head": WEATHER_HEAD,
            "source_blob_sha": WEATHER_SOURCE_BLOB_SHA,
            "wind_xy": list(WEATHER_WIND_XY),
            "normalized_wind_xy": list(unit_wind),
            "semantics": WEATHER_SEMANTICS,
        },
        "north_low_socket": {
            "pivot_m": pivot,
            "source_derived_axis": axis,
            "selected_vertices": len(selected),
            "selected_triangles": int(probe["selected_triangles"]),
            "diagnostic_interval_deg": list(probe["diagnostic_interval_deg"]),
        },
        "measurements": {
            "parent_child_representative_count": len(parents) * len(children),
            "parent_rows": rows,
            "neutral_parent_negative_child_parallel_m": neg,
            "neutral_parent_zero_child_parallel_m": zero,
            "neutral_parent_positive_child_parallel_m": pos,
            "signed_parallel_separation_m": separation,
            "review_only_downwind_alignment_angle_deg": preferred,
            "maximum_weather_parallel_response_drift_across_parent_commands_m": maximum_parent_projection_drift,
            "maximum_weather_cross_response_drift_across_parent_commands_m": maximum_parent_cross_drift,
            "maximum_vertical_response_drift_across_parent_commands_m": maximum_parent_vertical_drift,
            "rigging_counterfactual_parent_inheritance_max_output_delta_m": gate_report["measurements"]["maximum_counterfactual_inherited_output_delta_m"],
        },
        "decision": {
            "state": "KEEP_NORTH_LOW_MINUS5_REVIEW_POLARITY_WITH_PARENT_INFLUENCE_GATED",
            "automatic_motion_adoption": False,
            "automatic_weather_force_adoption": False,
            "automatic_animation_adoption": False,
            "automatic_runtime_adoption": False,
        },
        "checks": checks,
        "truth_boundary": {
            "visual_coordinate_compatibility_only": True,
            "physical_wind_claimed": False,
            "wind_force_speed_drag_or_turbulence_claimed": False,
            "biological_motion_claimed": False,
            "animation_timing_or_playback_claimed": False,
            "runtime_or_target_device_claimed": False,
            "gameplay_or_physics_claimed": False,
            "art_direction_or_visual_qa_acceptance_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }


def build_review_svg(source: dict) -> str:
    report = evaluate(source)
    unit_wind = report["weather_visual_direction_donor"]["normalized_wind_xy"]
    rows = report["measurements"]["parent_rows"]
    width, height = 900, 430
    cx, base_y = 150, 95
    scale = 3500.0
    chunks = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:monospace;font-size:13px;fill:#111}.axis{stroke:#777;stroke-width:1}.wind{stroke:#111;stroke-width:2}.neg{stroke:#111;stroke-width:3}.pos{stroke:#777;stroke-width:3}.zero{fill:#111}</style>',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="#111"/></marker></defs>',
        '<text x="20" y="28">north-low gated parent response vs Weather visual direction (review only)</text>',
        f'<line class="wind" x1="610" y1="45" x2="{610 + 90*unit_wind[0]:.2f}" y2="{45 - 90*unit_wind[1]:.2f}" marker-end="url(#arrow)"/>',
        '<text x="610" y="28">Weather [1.0, 0.35]</text>',
    ]
    for r, row in enumerate(rows):
        y = base_y + r * 105
        chunks.append(f'<text x="20" y="{y-18}">parent {row["parent_angle_deg"]:+.1f} deg (gated)</text>')
        chunks.append(f'<line class="axis" x1="{cx-30}" y1="{y}" x2="{cx+380}" y2="{y}"/>')
        chunks.append(f'<circle class="zero" cx="{cx}" cy="{y}" r="4"/>')
        for witness in row["witnesses"]:
            dx, dy, _ = witness["centroid_delta_m"]
            x2 = cx + dx * scale
            y2 = y - dy * scale
            cls = "neg" if witness["child_angle_deg"] < 0 else "pos"
            if abs(witness["child_angle_deg"]) <= TOL:
                continue
            chunks.append(f'<line class="{cls}" x1="{cx}" y1="{y}" x2="{x2:.2f}" y2="{y2:.2f}" marker-end="url(#arrow)"/>')
            chunks.append(f'<text x="{x2+8:.2f}" y="{y2:.2f}">{witness["child_angle_deg"]:+.0f} deg / parallel {witness["weather_parallel_m"]*1000:+.2f} mm</text>')
    chunks.append('<text x="20" y="410">Identical rows are expected: Rigging gates upper-trunk parent influence for north-low in this exact diagnostic receiver.</text>')
    chunks.append('</svg>')
    return "\n".join(chunks) + "\n"

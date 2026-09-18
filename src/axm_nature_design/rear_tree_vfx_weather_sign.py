"""VFX review evidence for Weather visual-direction alignment on the east-rear tree socket.

This module does not author wind motion. It asks one smaller receiving question:
which sign of the exact Rigging diagnostic +/-5 degree north-top socket moves the
actual generated child geometry more downwind in XY relative to the exact
source-owned Weather *visual* direction?

The answer is review-only sign compatibility. It does not adopt amplitude,
timing, biological response, physical force, Runtime control or gameplay.
"""
from __future__ import annotations

import math

from .organic_form import build_mesh, validate_source
from .rear_tree_animation import (
    RESULT as ANIMATION_RESULT,
    _pose,
    _selected_indices,
    evaluate as evaluate_animation,
)
from .rear_tree_rigging import evaluate as evaluate_rigging

SCHEMA = "axm.nature-vfx-weather-direction-socket-sign/v0.1"
RESULT = "PASS_EAST_REAR_WEATHER_VISUAL_DIRECTION_SOCKET_SIGN_COMPATIBILITY"
ANIMATION_HEAD = "74354ff851538d4d8aba9332900ae40218415eaf"
WEATHER_REPOSITORY = "mike-axiom-mir/axm-weather-design"
WEATHER_PR = 2
WEATHER_HEAD = "ca2eaba519e8449835b0ea6ef944b7080c3caa6a"
WEATHER_SOURCE_PATH = "examples/wind_atmosphere_baseline_001.json"
WEATHER_SOURCE_BLOB_SHA = "11298d447f262da8a78e43e2df68bc0346c99a2c"
WEATHER_SOURCE_DIGEST = "b33feba47b0a0f9a99ec439e32a87ff6d4cb2dacffe33ba78f8b646c3a1be8d6"
WEATHER_WIND_XY = (1.0, 0.35)
WEATHER_SEMANTICS = "VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED"
DIAGNOSTIC_ANGLES_DEG = (-5.0, 0.0, 5.0)
TOL = 1e-12


def _normalize_xy(v):
    x, y = float(v[0]), float(v[1])
    length = math.hypot(x, y)
    if length <= TOL:
        raise ValueError("Weather visual direction must be non-zero")
    return (x / length, y / length)


def _centroid_xy(vertices, indices):
    count = len(indices)
    if count == 0:
        raise ValueError("empty selected child partition")
    return (
        sum(float(vertices[i][0]) for i in indices) / count,
        sum(float(vertices[i][1]) for i in indices) / count,
    )


def _project_xy(delta_xy, unit_wind_xy):
    return float(delta_xy[0]) * float(unit_wind_xy[0]) + float(delta_xy[1]) * float(unit_wind_xy[1])


def _crosswind_xy(delta_xy, unit_wind_xy):
    # Signed perpendicular projection in the XY plane.
    return -float(delta_xy[0]) * float(unit_wind_xy[1]) + float(delta_xy[1]) * float(unit_wind_xy[0])


def evaluate(
    source: dict,
    *,
    wind_xy=WEATHER_WIND_XY,
    diagnostic_angles_deg=DIAGNOSTIC_ANGLES_DEG,
    claim_physical_wind: bool = False,
    claim_biological_response: bool = False,
    claim_animation_adoption: bool = False,
    claim_runtime_controller: bool = False,
    claim_gameplay: bool = False,
) -> dict:
    """Resolve only the signed visual-direction relationship for the exact socket."""
    validate_source(source)

    wind = tuple(float(x) for x in wind_xy)
    if len(wind) != 2 or any(abs(wind[i] - WEATHER_WIND_XY[i]) > TOL for i in range(2)):
        raise ValueError("Weather visual-direction donor drift")
    angles = tuple(float(x) for x in diagnostic_angles_deg)
    if angles != DIAGNOSTIC_ANGLES_DEG:
        raise ValueError("VFX may not widen or retime the exact Rigging diagnostic witnesses")
    if claim_physical_wind:
        raise ValueError("source-owned Weather direction is visual-only, not physical wind")
    if claim_biological_response:
        raise ValueError("diagnostic socket evidence is not biological response evidence")
    if claim_animation_adoption:
        raise ValueError("sign compatibility does not adopt an Animation motion")
    if claim_runtime_controller:
        raise ValueError("VFX sign evidence cannot claim Runtime controller acceptance")
    if claim_gameplay:
        raise ValueError("VFX sign evidence cannot claim gameplay acceptance")

    animation = evaluate_animation(source)
    if animation["result"] != ANIMATION_RESULT:
        raise ValueError("exact Animation prerequisite is not green")
    if animation["motion"]["truth_label"] != "ANIMATION_DIAGNOSTIC_SOCKET_PULSE_NOT_WIND_NOT_BIOLOGICAL_ROM_NOT_CONTROLLER":
        raise ValueError("Animation truth-boundary drift")

    rig = evaluate_rigging(source)
    mesh = build_mesh(source)
    neutral = [[float(x) for x in vertex] for vertex in mesh["vertices"]]
    rig_probe = rig["rigging_probe"]
    selected = _selected_indices(mesh, rig_probe["selected_regions"])
    if len(selected) != 52:
        raise ValueError("exact Rigging child partition drift")

    pivot = [float(x) for x in rig_probe["joint_pivot_m"]]
    axis = [float(x) for x in rig_probe["source_derived_axis"]]
    unit_wind = _normalize_xy(wind)
    neutral_centroid = _centroid_xy(neutral, selected)

    rows = []
    frames = {}
    for angle in angles:
        posed = _pose(neutral, selected, pivot, axis, angle)
        frames[angle] = posed
        centroid = _centroid_xy(posed, selected)
        delta = (centroid[0] - neutral_centroid[0], centroid[1] - neutral_centroid[1])
        per_vertex_downwind = []
        for i in selected:
            vdelta = (posed[i][0] - neutral[i][0], posed[i][1] - neutral[i][1])
            per_vertex_downwind.append(_project_xy(vdelta, unit_wind))
        rows.append(
            {
                "angle_deg": angle,
                "centroid_xy_m": [centroid[0], centroid[1]],
                "centroid_delta_xy_m": [delta[0], delta[1]],
                "centroid_downwind_projection_m": _project_xy(delta, unit_wind),
                "centroid_crosswind_projection_m": _crosswind_xy(delta, unit_wind),
                "mean_vertex_downwind_projection_m": sum(per_vertex_downwind) / len(per_vertex_downwind),
                "minimum_vertex_downwind_projection_m": min(per_vertex_downwind),
                "maximum_vertex_downwind_projection_m": max(per_vertex_downwind),
            }
        )

    by_angle = {float(row["angle_deg"]): row for row in rows}
    negative = by_angle[-5.0]["centroid_downwind_projection_m"]
    neutral_projection = by_angle[0.0]["centroid_downwind_projection_m"]
    positive = by_angle[5.0]["centroid_downwind_projection_m"]
    separation = abs(positive - negative)
    if separation <= 1e-9:
        raise ValueError("diagnostic socket signs are not separable against Weather visual direction")

    preferred_angle = 5.0 if positive > negative else -5.0
    alternate_angle = -preferred_angle
    preferred_projection = by_angle[preferred_angle]["centroid_downwind_projection_m"]
    alternate_projection = by_angle[alternate_angle]["centroid_downwind_projection_m"]

    checks = {
        "exact_animation_prerequisite": animation["result"] == ANIMATION_RESULT,
        "exact_weather_visual_direction": wind == WEATHER_WIND_XY,
        "visual_direction_semantics_preserved": WEATHER_SEMANTICS == "VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED",
        "exact_rigging_diagnostic_witnesses_only": angles == DIAGNOSTIC_ANGLES_DEG,
        "exact_selected_child_partition": len(selected) == 52,
        "neutral_projection_is_zero": abs(neutral_projection) <= TOL,
        "signed_witnesses_are_separable": separation > 1e-9,
        "selection_rule_is_ordered": preferred_projection > alternate_projection,
        "no_physical_wind_claim": not claim_physical_wind,
        "no_biological_response_claim": not claim_biological_response,
        "no_animation_adoption_claim": not claim_animation_adoption,
        "no_runtime_controller_claim": not claim_runtime_controller,
        "no_gameplay_claim": not claim_gameplay,
    }

    return {
        "schema": SCHEMA,
        "result": RESULT if all(checks.values()) else "FAIL",
        "nature_animation_owner": {
            "repository": "mike-axiom-mir/axm-nature-design",
            "pull_request": 15,
            "head": ANIMATION_HEAD,
            "result": animation["result"],
            "truth_label": animation["motion"]["truth_label"],
        },
        "weather_visual_direction_donor": {
            "repository": WEATHER_REPOSITORY,
            "pull_request": WEATHER_PR,
            "head": WEATHER_HEAD,
            "source_path": WEATHER_SOURCE_PATH,
            "source_blob_sha": WEATHER_SOURCE_BLOB_SHA,
            "source_digest": WEATHER_SOURCE_DIGEST,
            "wind_xy": list(WEATHER_WIND_XY),
            "normalized_wind_xy": [unit_wind[0], unit_wind[1]],
            "wind_semantics": WEATHER_SEMANTICS,
        },
        "rigging_receiver": {
            "joint_pivot_m": pivot,
            "source_derived_axis": axis,
            "selected_regions": rig_probe["selected_regions"],
            "selected_vertices": len(selected),
            "diagnostic_interval_deg": rig_probe["diagnostic_interval_deg"],
            "diagnostic_interval_semantics": rig_probe["diagnostic_interval_semantics"],
        },
        "measurements": {
            "neutral_selected_child_centroid_xy_m": [neutral_centroid[0], neutral_centroid[1]],
            "diagnostic_witnesses": rows,
            "signed_centroid_projection_separation_m": separation,
            "review_only_downwind_alignment_angle_deg": preferred_angle,
            "review_only_alternate_angle_deg": alternate_angle,
            "preferred_centroid_downwind_projection_m": preferred_projection,
            "alternate_centroid_downwind_projection_m": alternate_projection,
        },
        "decision": {
            "state": "PASS_SIGN_COMPATIBILITY_ONLY_NO_MOTION_ADOPTION",
            "review_only_downwind_alignment_angle_deg": preferred_angle,
            "automatic_animation_adoption": False,
            "automatic_vfx_motion_adoption": False,
        },
        "checks": checks,
        "truth_boundary": {
            "wind_strength_or_force_authored": False,
            "wind_timing_authored": False,
            "socket_amplitude_adopted": False,
            "animation_motion_adopted": False,
            "biological_response_claimed": False,
            "physical_wind_claimed": False,
            "runtime_controller_claimed": False,
            "gameplay_claimed": False,
            "art_direction_or_visual_qa_acceptance_claimed": False,
            "target_device_performance_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }


def build_review_svg(source: dict) -> str:
    """Three-pose XY projection with the exact Weather visual-direction arrow."""
    evidence = evaluate(source)
    rig = evaluate_rigging(source)
    mesh = build_mesh(source)
    neutral = [[float(x) for x in vertex] for vertex in mesh["vertices"]]
    selected = _selected_indices(mesh, rig["rigging_probe"]["selected_regions"])
    pivot = [float(x) for x in rig["rigging_probe"]["joint_pivot_m"]]
    axis = [float(x) for x in rig["rigging_probe"]["source_derived_axis"]]
    unit_wind = tuple(evidence["weather_visual_direction_donor"]["normalized_wind_xy"])
    pose_angles = [-5.0, 0.0, 5.0]
    posed = [_pose(neutral, selected, pivot, axis, angle) for angle in pose_angles]

    xs = [frame[i][0] for frame in posed for i in selected]
    ys = [frame[i][1] for frame in posed for i in selected]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    xspan = max(xmax - xmin, 1e-9)
    yspan = max(ymax - ymin, 1e-9)
    panel_w, panel_h, margin = 260, 260, 28
    width = panel_w * len(posed)
    height = panel_h + 78

    chunks = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:monospace;font-size:12px}.p{fill:#111}.pivot{fill:none;stroke:#111;stroke-width:1.5}.wind{stroke:#111;stroke-width:2}</style>',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="#111"/></marker></defs>',
    ]
    for panel, (angle, frame) in enumerate(zip(pose_angles, posed)):
        x0 = panel * panel_w
        chunks.append(f'<rect x="{x0 + 1}" y="1" width="{panel_w - 2}" height="{panel_h - 2}" fill="none" stroke="#bbb"/>')
        for i in selected:
            x, y = frame[i][0], frame[i][1]
            px = x0 + margin + ((x - xmin) / xspan) * (panel_w - 2 * margin)
            py = margin + (1.0 - (y - ymin) / yspan) * (panel_h - 2 * margin)
            chunks.append(f'<circle class="p" cx="{px:.3f}" cy="{py:.3f}" r="1.2"/>')
        ppx = x0 + margin + ((pivot[0] - xmin) / xspan) * (panel_w - 2 * margin)
        ppy = margin + (1.0 - (pivot[1] - ymin) / yspan) * (panel_h - 2 * margin)
        chunks.append(f'<circle class="pivot" cx="{ppx:.3f}" cy="{ppy:.3f}" r="4"/>')
        ax0, ay0 = x0 + 36, 34
        ax1 = ax0 + unit_wind[0] * 58.0
        ay1 = ay0 - unit_wind[1] * 58.0
        chunks.append(f'<line class="wind" x1="{ax0:.3f}" y1="{ay0:.3f}" x2="{ax1:.3f}" y2="{ay1:.3f}" marker-end="url(#arrow)"/>')
        row = next(r for r in evidence["measurements"]["diagnostic_witnesses"] if float(r["angle_deg"]) == angle)
        proj = row["centroid_downwind_projection_m"]
        chunks.append(f'<text x="{x0 + 10}" y="{panel_h + 20}">{angle:+.1f} deg  centroid downwind={proj:+.6f} m</text>')
    preferred = evidence["decision"]["review_only_downwind_alignment_angle_deg"]
    chunks.append(f'<text x="10" y="{panel_h + 46}">Weather visual direction only; review-only downwind-alignment sign: {preferred:+.1f} deg</text>')
    chunks.append(f'<text x="10" y="{panel_h + 64}">No wind strength/timing/amplitude/Animation/Runtime/gameplay adoption.</text>')
    chunks.append('</svg>')
    return "\n".join(chunks)

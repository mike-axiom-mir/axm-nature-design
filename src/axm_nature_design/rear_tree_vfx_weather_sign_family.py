"""VFX review-only Weather-direction sign map across five Nature branch sockets.

This module consumes exact Rigging-owned diagnostic articulation and one source-owned
Weather visual direction. It does not author wind motion, timing, amplitude, force,
biological response, Runtime policy or gameplay.
"""
from __future__ import annotations

import math

from . import rear_tree_rigging as historical
from . import rear_tree_rigging_primary_branch_family as rigging_family
from .organic_form import build_mesh, validate_source

SCHEMA = "axm.nature-vfx-weather-direction-socket-sign-family/v0.2"
RESULT = "PASS_FIVE_SOCKET_WEATHER_VISUAL_DIRECTION_SIGN_MAP"
RIGGING_OWNER_HEAD = "898529f602893c8f6be179bd3e9b6821fc099904"
VFX_PREDECESSOR_HEAD = "1976c5a4ff0a51b5f3ee4bfd323dbb6f89c34787"
WEATHER_REPOSITORY = "mike-axiom-mir/axm-weather-design"
WEATHER_PR = 2
WEATHER_HEAD = "ca2eaba519e8449835b0ea6ef944b7080c3caa6a"
WEATHER_SOURCE_PATH = "examples/wind_atmosphere_baseline_001.json"
WEATHER_SOURCE_BLOB_SHA = "11298d447f262da8a78e43e2df68bc0346c99a2c"
WEATHER_WIND_XY = (1.0, 0.35)
WEATHER_SEMANTICS = "VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED"
DIAGNOSTIC_ANGLES_DEG = (-5.0, 0.0, 5.0)
BRANCH_IDS = rigging_family.BRANCH_IDS
TOL = 1e-12

PREDECESSOR_NORTH_TOP = {
    "preferred_angle_deg": 5.0,
    "negative_projection_m": -0.02123402396152125,
    "neutral_projection_m": 0.0,
    "positive_projection_m": 0.019556427432932226,
    "separation_m": 0.040790451394453475,
}


def _normalize_xy(v):
    x, y = float(v[0]), float(v[1])
    length = math.hypot(x, y)
    if length <= TOL:
        raise ValueError("Weather visual direction must be non-zero")
    return (x / length, y / length)


def _centroid_xy(vertices, indices):
    if not indices:
        raise ValueError("empty selected child partition")
    count = len(indices)
    return (
        sum(float(vertices[i][0]) for i in indices) / count,
        sum(float(vertices[i][1]) for i in indices) / count,
    )


def _project_xy(delta_xy, unit_wind_xy):
    return (
        float(delta_xy[0]) * float(unit_wind_xy[0])
        + float(delta_xy[1]) * float(unit_wind_xy[1])
    )


def _crosswind_xy(delta_xy, unit_wind_xy):
    return (
        -float(delta_xy[0]) * float(unit_wind_xy[1])
        + float(delta_xy[1]) * float(unit_wind_xy[0])
    )


def _pose(neutral, selected, pivot, axis, angle_deg):
    posed = [list(v) for v in neutral]
    for index in selected:
        posed[index] = historical._rotate_about_axis(
            neutral[index], pivot, axis, angle_deg
        )
    return posed


def evaluate(
    source: dict,
    *,
    wind_xy=WEATHER_WIND_XY,
    branch_ids=BRANCH_IDS,
    diagnostic_angles_deg=DIAGNOSTIC_ANGLES_DEG,
    claim_physical_wind: bool = False,
    claim_biological_response: bool = False,
    claim_animation_adoption: bool = False,
    claim_runtime_controller: bool = False,
    claim_gameplay: bool = False,
    claim_simultaneous_motion: bool = False,
) -> dict:
    """Resolve one review-only Weather visual-direction sign per exact Rigging socket."""
    validate_source(source)

    wind = tuple(float(x) for x in wind_xy)
    if len(wind) != 2 or any(
        abs(wind[i] - WEATHER_WIND_XY[i]) > TOL for i in range(2)
    ):
        raise ValueError("Weather visual-direction donor drift")
    requested_branches = tuple(branch_ids)
    if requested_branches != BRANCH_IDS:
        raise ValueError("VFX sign map requires the exact five Rigging branch identities")
    angles = tuple(float(x) for x in diagnostic_angles_deg)
    if angles != DIAGNOSTIC_ANGLES_DEG:
        raise ValueError("VFX may not widen or retime the exact Rigging diagnostic witnesses")
    if claim_physical_wind:
        raise ValueError("source-owned Weather direction is visual-only, not physical wind")
    if claim_biological_response:
        raise ValueError("Rigging diagnostic sockets are not biological response evidence")
    if claim_animation_adoption:
        raise ValueError("sign compatibility does not adopt Animation motion")
    if claim_runtime_controller:
        raise ValueError("VFX sign evidence cannot claim Runtime controller acceptance")
    if claim_gameplay:
        raise ValueError("VFX sign evidence cannot claim gameplay acceptance")
    if claim_simultaneous_motion:
        raise ValueError("independent Rigging sockets do not prove simultaneous multi-branch motion")

    rig = rigging_family.evaluate(source)
    if rig["result"] != rigging_family.RESULT:
        raise ValueError("exact five-socket Rigging prerequisite is not green")
    if tuple(rig["rigging_family"]["branch_ids"]) != BRANCH_IDS:
        raise ValueError("Rigging branch family identity drift")

    mesh = build_mesh(source)
    neutral = [[float(x) for x in vertex] for vertex in mesh["vertices"]]
    unit_wind = _normalize_xy(wind)

    branch_rows = []
    for branch_id in BRANCH_IDS:
        probe = rigging_family._probe_branch(source, mesh, branch_id)
        selected = list(probe["selected_vertex_indices"])
        if len(selected) != 52:
            raise ValueError(f"exact Rigging child partition drift: {branch_id}")
        pivot = [float(x) for x in probe["joint_pivot_m"]]
        axis = [float(x) for x in probe["source_derived_axis"]]
        neutral_centroid = _centroid_xy(neutral, selected)

        witnesses = []
        for angle in angles:
            posed = _pose(neutral, selected, pivot, axis, angle)
            centroid = _centroid_xy(posed, selected)
            delta = (
                centroid[0] - neutral_centroid[0],
                centroid[1] - neutral_centroid[1],
            )
            per_vertex = []
            for index in selected:
                vdelta = (
                    posed[index][0] - neutral[index][0],
                    posed[index][1] - neutral[index][1],
                )
                per_vertex.append(_project_xy(vdelta, unit_wind))
            witnesses.append(
                {
                    "angle_deg": angle,
                    "centroid_xy_m": [centroid[0], centroid[1]],
                    "centroid_delta_xy_m": [delta[0], delta[1]],
                    "centroid_downwind_projection_m": _project_xy(delta, unit_wind),
                    "centroid_crosswind_projection_m": _crosswind_xy(delta, unit_wind),
                    "mean_vertex_downwind_projection_m": sum(per_vertex) / len(per_vertex),
                    "minimum_vertex_downwind_projection_m": min(per_vertex),
                    "maximum_vertex_downwind_projection_m": max(per_vertex),
                }
            )

        by_angle = {float(row["angle_deg"]): row for row in witnesses}
        negative = by_angle[-5.0]["centroid_downwind_projection_m"]
        zero = by_angle[0.0]["centroid_downwind_projection_m"]
        positive = by_angle[5.0]["centroid_downwind_projection_m"]
        separation = abs(positive - negative)
        if abs(zero) > TOL:
            raise ValueError(f"neutral Weather projection drift: {branch_id}")
        if separation <= 1e-9:
            raise ValueError(
                f"diagnostic socket signs are not separable against Weather visual direction: {branch_id}"
            )
        preferred = 5.0 if positive > negative else -5.0
        alternate = -preferred

        branch_rows.append(
            {
                "branch_id": branch_id,
                "joint_pivot_m": pivot,
                "source_derived_axis": axis,
                "selected_vertices": len(selected),
                "selected_triangles": int(probe["selected_triangles"]),
                "diagnostic_interval_deg": list(probe["diagnostic_interval_deg"]),
                "diagnostic_interval_semantics": probe["diagnostic_interval_semantics"],
                "neutral_selected_child_centroid_xy_m": [
                    neutral_centroid[0],
                    neutral_centroid[1],
                ],
                "diagnostic_witnesses": witnesses,
                "signed_centroid_projection_separation_m": separation,
                "review_only_downwind_alignment_angle_deg": preferred,
                "review_only_alternate_angle_deg": alternate,
                "preferred_centroid_downwind_projection_m": by_angle[preferred][
                    "centroid_downwind_projection_m"
                ],
                "alternate_centroid_downwind_projection_m": by_angle[alternate][
                    "centroid_downwind_projection_m"
                ],
            }
        )

    north = next(row for row in branch_rows if row["branch_id"] == "north-top")
    north_by_angle = {
        float(row["angle_deg"]): row for row in north["diagnostic_witnesses"]
    }
    predecessor_north_reproduced = (
        north["review_only_downwind_alignment_angle_deg"]
        == PREDECESSOR_NORTH_TOP["preferred_angle_deg"]
        and abs(
            north_by_angle[-5.0]["centroid_downwind_projection_m"]
            - PREDECESSOR_NORTH_TOP["negative_projection_m"]
        )
        <= TOL
        and abs(
            north_by_angle[0.0]["centroid_downwind_projection_m"]
            - PREDECESSOR_NORTH_TOP["neutral_projection_m"]
        )
        <= TOL
        and abs(
            north_by_angle[5.0]["centroid_downwind_projection_m"]
            - PREDECESSOR_NORTH_TOP["positive_projection_m"]
        )
        <= TOL
        and abs(
            north["signed_centroid_projection_separation_m"]
            - PREDECESSOR_NORTH_TOP["separation_m"]
        )
        <= TOL
    )
    if not predecessor_north_reproduced:
        raise ValueError("north-top VFX predecessor sign evidence did not reproduce")

    sign_map = {
        row["branch_id"]: row["review_only_downwind_alignment_angle_deg"]
        for row in branch_rows
    }
    unique_signs = sorted(set(sign_map.values()))
    family_polarity = "UNIFORM_SIGN" if len(unique_signs) == 1 else "PER_SOCKET_SIGN_MAP_REQUIRED"

    checks = {
        "exact_rigging_family_prerequisite": rig["result"] == rigging_family.RESULT,
        "exact_five_branch_identity": tuple(sign_map) == BRANCH_IDS,
        "exact_weather_visual_direction": wind == WEATHER_WIND_XY,
        "visual_direction_semantics_preserved": WEATHER_SEMANTICS
        == "VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED",
        "exact_rigging_diagnostic_witnesses_only": angles == DIAGNOSTIC_ANGLES_DEG,
        "all_child_partitions_52_vertices": all(
            row["selected_vertices"] == 52 for row in branch_rows
        ),
        "all_neutral_projections_zero": all(
            abs(
                next(
                    w["centroid_downwind_projection_m"]
                    for w in row["diagnostic_witnesses"]
                    if float(w["angle_deg"]) == 0.0
                )
            )
            <= TOL
            for row in branch_rows
        ),
        "all_signed_witnesses_separable": all(
            row["signed_centroid_projection_separation_m"] > 1e-9
            for row in branch_rows
        ),
        "north_top_predecessor_reproduced": predecessor_north_reproduced,
        "no_physical_wind_claim": not claim_physical_wind,
        "no_biological_response_claim": not claim_biological_response,
        "no_animation_adoption_claim": not claim_animation_adoption,
        "no_runtime_controller_claim": not claim_runtime_controller,
        "no_gameplay_claim": not claim_gameplay,
        "no_simultaneous_motion_claim": not claim_simultaneous_motion,
    }

    return {
        "schema": SCHEMA,
        "result": RESULT if all(checks.values()) else "FAIL",
        "nature_rigging_owner": {
            "repository": "mike-axiom-mir/axm-nature-design",
            "pull_request": 14,
            "head": RIGGING_OWNER_HEAD,
            "result": rig["result"],
        },
        "vfx_predecessor": {
            "pull_request": 16,
            "head": VFX_PREDECESSOR_HEAD,
            "north_top": PREDECESSOR_NORTH_TOP,
            "reproduced": predecessor_north_reproduced,
        },
        "weather_visual_direction_donor": {
            "repository": WEATHER_REPOSITORY,
            "pull_request": WEATHER_PR,
            "head": WEATHER_HEAD,
            "source_path": WEATHER_SOURCE_PATH,
            "source_blob_sha": WEATHER_SOURCE_BLOB_SHA,
            "wind_xy": list(WEATHER_WIND_XY),
            "normalized_wind_xy": [unit_wind[0], unit_wind[1]],
            "wind_semantics": WEATHER_SEMANTICS,
        },
        "measurements": {
            "branch_signs": branch_rows,
            "review_only_downwind_alignment_angle_deg_by_branch": sign_map,
            "family_polarity": family_polarity,
        },
        "decision": {
            "state": "PASS_REVIEW_ONLY_FIVE_SOCKET_SIGN_MAP_NO_MOTION_ADOPTION",
            "family_polarity": family_polarity,
            "review_only_downwind_alignment_angle_deg_by_branch": sign_map,
            "automatic_animation_adoption": False,
            "automatic_vfx_motion_adoption": False,
        },
        "checks": checks,
        "truth_boundary": {
            "wind_strength_or_force_authored": False,
            "wind_timing_or_cadence_authored": False,
            "socket_amplitude_adopted": False,
            "animation_motion_adopted": False,
            "simultaneous_multi_branch_motion_claimed": False,
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
    """Five-row, three-pose XY review using actual selected generated vertices."""
    evidence = evaluate(source)
    mesh = build_mesh(source)
    neutral = [[float(x) for x in vertex] for vertex in mesh["vertices"]]
    unit_wind = tuple(
        evidence["weather_visual_direction_donor"]["normalized_wind_xy"]
    )

    panel_w, panel_h = 240, 180
    margin = 22
    label_h = 48
    cols = len(DIAGNOSTIC_ANGLES_DEG)
    rows = len(BRANCH_IDS)
    width = panel_w * cols
    height = rows * (panel_h + label_h) + 50

    chunks = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:monospace;font-size:11px}.p{fill:#111}.pivot{fill:none;stroke:#111;stroke-width:1.4}.wind{stroke:#111;stroke-width:2}.box{fill:none;stroke:#bbb}</style>',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="#111"/></marker></defs>',
    ]

    measurement_by_branch = {
        row["branch_id"]: row for row in evidence["measurements"]["branch_signs"]
    }
    for row_index, branch_id in enumerate(BRANCH_IDS):
        probe = rigging_family._probe_branch(source, mesh, branch_id)
        selected = list(probe["selected_vertex_indices"])
        pivot = [float(x) for x in probe["joint_pivot_m"]]
        axis = [float(x) for x in probe["source_derived_axis"]]
        posed = {
            angle: _pose(neutral, selected, pivot, axis, angle)
            for angle in DIAGNOSTIC_ANGLES_DEG
        }
        xs = [posed[a][i][0] for a in DIAGNOSTIC_ANGLES_DEG for i in selected]
        ys = [posed[a][i][1] for a in DIAGNOSTIC_ANGLES_DEG for i in selected]
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        xspan = max(xmax - xmin, 1e-9)
        yspan = max(ymax - ymin, 1e-9)
        row_y = row_index * (panel_h + label_h)

        for col_index, angle in enumerate(DIAGNOSTIC_ANGLES_DEG):
            x0 = col_index * panel_w
            y0 = row_y
            chunks.append(
                f'<rect class="box" x="{x0 + 1}" y="{y0 + 1}" width="{panel_w - 2}" height="{panel_h - 2}"/>'
            )
            frame = posed[angle]
            for index in selected:
                x, y = frame[index][0], frame[index][1]
                px = x0 + margin + ((x - xmin) / xspan) * (panel_w - 2 * margin)
                py = y0 + margin + (1.0 - (y - ymin) / yspan) * (
                    panel_h - 2 * margin
                )
                chunks.append(
                    f'<circle class="p" cx="{px:.3f}" cy="{py:.3f}" r="1.1"/>'
                )
            ppx = x0 + margin + ((pivot[0] - xmin) / xspan) * (
                panel_w - 2 * margin
            )
            ppy = y0 + margin + (1.0 - (pivot[1] - ymin) / yspan) * (
                panel_h - 2 * margin
            )
            chunks.append(
                f'<circle class="pivot" cx="{ppx:.3f}" cy="{ppy:.3f}" r="3.5"/>'
            )

            ax0, ay0 = x0 + 30, y0 + 28
            ax1 = ax0 + unit_wind[0] * 44.0
            ay1 = ay0 - unit_wind[1] * 44.0
            chunks.append(
                f'<line class="wind" x1="{ax0:.3f}" y1="{ay0:.3f}" x2="{ax1:.3f}" y2="{ay1:.3f}" marker-end="url(#arrow)"/>'
            )
            measurement = measurement_by_branch[branch_id]
            witness = next(
                w
                for w in measurement["diagnostic_witnesses"]
                if float(w["angle_deg"]) == angle
            )
            proj = witness["centroid_downwind_projection_m"]
            chunks.append(
                f'<text x="{x0 + 8}" y="{y0 + panel_h + 16}">{branch_id} {angle:+.1f} deg downwind={proj:+.6f} m</text>'
            )

        preferred = measurement_by_branch[branch_id][
            "review_only_downwind_alignment_angle_deg"
        ]
        chunks.append(
            f'<text x="8" y="{row_y + panel_h + 34}">review-only downwind sign: {preferred:+.1f} deg</text>'
        )

    chunks.append(
        f'<text x="8" y="{height - 24}">Weather visual direction only; family polarity: {evidence["measurements"]["family_polarity"]}.</text>'
    )
    chunks.append(
        f'<text x="8" y="{height - 8}">No wind force/timing/amplitude/Animation/Runtime/gameplay adoption.</text>'
    )
    chunks.append("</svg>")
    return "\n".join(chunks)

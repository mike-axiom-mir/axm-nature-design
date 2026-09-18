"""VFX-owned Weather-direction compatibility review for the Nature east-mid hierarchy.

Consumes the exact Rigging upper-trunk -> east-mid parent/child diagnostic and the
source-owned Weather visual direction. It measures whether the established east-mid
child polarity remains downwind when its pivot/axis are transported by the parent
frame. It does not author physical wind, motion timing, plant biomechanics, runtime
controller behavior, gameplay, or final visual acceptance.
"""
from __future__ import annotations

import math

from . import rear_tree_rigging as historical
from . import rear_tree_rigging_primary_branch_family as family
from . import rear_tree_rigging_upper_trunk_east_mid_hierarchy as hierarchy
from .organic_form import build_mesh, validate_source

SCHEMA = "axm.nature-vfx-upper-trunk-east-mid-weather-direction-hierarchy/v0.1"
PASS_RESULT = "PASS_EAST_MID_HIERARCHICAL_WEATHER_VISUAL_DIRECTION_SIGN_STABILITY"
HOLD_RESULT = "HOLD_EAST_MID_HIERARCHICAL_WEATHER_VISUAL_DIRECTION_REQUIRES_PARENT_AWARE_POLARITY"
RIGGING_OWNER_HEAD = "6cf64925f0ea00737e4d3f2d4f15979c773f309d"
VFX_SIGN_PREDECESSOR_HEAD = "ef7b35af27d5ca98a6447c1e33be07863e387305"
WEATHER_REPOSITORY = "mike-axiom-mir/axm-weather-design"
WEATHER_PR = 2
WEATHER_HEAD = "ca2eaba519e8449835b0ea6ef944b7080c3caa6a"
WEATHER_SOURCE_PATH = "examples/wind_atmosphere_baseline_001.json"
WEATHER_SOURCE_BLOB_SHA = "11298d447f262da8a78e43e2df68bc0346c99a2c"
WEATHER_WIND_XY = (1.0, 0.35)
WEATHER_SEMANTICS = "VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED"
PARENT_ANGLES_DEG = (-2.5, 0.0, 2.5)
CHILD_ANGLES_DEG = (-5.0, 0.0, 5.0)
TOL = 1e-12

PREDECESSOR_EAST_MID = {
    "negative_projection_m": -0.03635336017118686,
    "neutral_projection_m": 0.0,
    "positive_projection_m": 0.03324277426140488,
    "separation_m": 0.06959613443259174,
    "preferred_angle_deg": 5.0,
}


def _normalize_xy(value):
    x, y = float(value[0]), float(value[1])
    length = math.hypot(x, y)
    if length <= TOL:
        raise ValueError("Weather visual direction must be non-zero")
    return (x / length, y / length)


def _centroid(vertices, indices):
    n = len(indices)
    if n == 0:
        raise ValueError("empty east-mid child partition")
    return [sum(float(vertices[i][axis]) for i in indices) / n for axis in range(3)]


def _project_xy(delta, unit_wind):
    return float(delta[0]) * unit_wind[0] + float(delta[1]) * unit_wind[1]


def _cross_xy(delta, unit_wind):
    return -float(delta[0]) * unit_wind[1] + float(delta[1]) * unit_wind[0]


def _frame(source):
    trunk = source["trunk"]
    upper_index = next(i for i, row in enumerate(trunk) if row.get("id") == hierarchy.TRUNK_POINT_ID)
    previous, upper, following = trunk[upper_index - 1], trunk[upper_index], trunk[upper_index + 1]
    parent_pivot = [float(v) for v in upper["position"]]
    incoming = historical._norm(historical._sub(parent_pivot, previous["position"]))
    outgoing = historical._norm(historical._sub(following["position"], parent_pivot))
    parent_axis = historical._norm(historical._cross(incoming, outgoing))

    rig = family.evaluate(source)
    probe = next(row for row in rig["rigging_family"]["probes"] if row["branch_id"] == hierarchy.CHILD_BRANCH_ID)
    return {
        "parent_pivot": parent_pivot,
        "parent_axis": parent_axis,
        "child_pivot": [float(v) for v in probe["joint_pivot_m"]],
        "child_axis": [float(v) for v in probe["source_derived_axis"]],
        "selected": list(probe["selected_vertex_indices"]),
        "selected_triangles": int(probe["selected_triangles"]),
    }


def _pose_selected(neutral, frame, parent_angle, child_angle):
    parent_pivot = frame["parent_pivot"]
    parent_axis = frame["parent_axis"]
    child_pivot = frame["child_pivot"]
    child_axis = frame["child_axis"]
    transported_pivot = historical._rotate_about_axis(child_pivot, parent_pivot, parent_axis, parent_angle)
    transported_axis = historical._norm(hierarchy._rotate_vector(child_axis, parent_axis, parent_angle))
    posed = [list(v) for v in neutral]
    for index in frame["selected"]:
        parented = historical._rotate_about_axis(neutral[index], parent_pivot, parent_axis, parent_angle)
        posed[index] = historical._rotate_about_axis(
            parented, transported_pivot, transported_axis, child_angle
        )
    return posed, transported_pivot, transported_axis


def evaluate(
    source: dict,
    *,
    wind_xy=WEATHER_WIND_XY,
    parent_angles_deg=PARENT_ANGLES_DEG,
    child_angles_deg=CHILD_ANGLES_DEG,
    claim_physical_wind: bool = False,
    claim_animation_adoption: bool = False,
    claim_runtime_controller: bool = False,
    claim_gameplay: bool = False,
    claim_art_acceptance: bool = False,
) -> dict:
    validate_source(source)
    if tuple(float(v) for v in wind_xy) != WEATHER_WIND_XY:
        raise ValueError("Weather visual-direction donor drift")
    if tuple(float(v) for v in parent_angles_deg) != PARENT_ANGLES_DEG:
        raise ValueError("VFX may not widen the exact Rigging parent diagnostic witnesses")
    if tuple(float(v) for v in child_angles_deg) != CHILD_ANGLES_DEG:
        raise ValueError("VFX may not widen the exact Rigging child diagnostic witnesses")
    if claim_physical_wind:
        raise ValueError("Weather direction is visual-only, not physical wind")
    if claim_animation_adoption:
        raise ValueError("VFX compatibility does not adopt Animation timing or motion")
    if claim_runtime_controller:
        raise ValueError("VFX compatibility cannot claim Runtime/controller acceptance")
    if claim_gameplay:
        raise ValueError("VFX compatibility cannot claim gameplay")
    if claim_art_acceptance:
        raise ValueError("VFX compatibility cannot claim Art Direction or Visual QA acceptance")

    owner = hierarchy.evaluate(source)
    if owner["result"] != hierarchy.RESULT:
        raise ValueError("exact Rigging hierarchy owner is not green")

    mesh = build_mesh(source)
    neutral = [[float(v) for v in row] for row in mesh["vertices"]]
    frame = _frame(source)
    if len(frame["selected"]) != 52 or frame["selected_triangles"] != 72:
        raise ValueError("east-mid Rigging child partition drift")
    unit_wind = _normalize_xy(wind_xy)
    neutral_world_centroid = _centroid(neutral, frame["selected"])

    parent_rows = []
    for parent_angle in PARENT_ANGLES_DEG:
        same_parent = {}
        for child_angle in CHILD_ANGLES_DEG:
            posed, transported_pivot, transported_axis = _pose_selected(
                neutral, frame, parent_angle, child_angle
            )
            centroid = _centroid(posed, frame["selected"])
            same_parent[child_angle] = {
                "child_angle_deg": child_angle,
                "centroid_m": centroid,
                "transported_child_pivot_m": transported_pivot,
                "transported_child_axis": transported_axis,
            }
        base = same_parent[0.0]["centroid_m"]
        parent_delta = [base[i] - neutral_world_centroid[i] for i in range(3)]
        witnesses = []
        for child_angle in CHILD_ANGLES_DEG:
            centroid = same_parent[child_angle]["centroid_m"]
            delta = [centroid[i] - base[i] for i in range(3)]
            witnesses.append({
                **same_parent[child_angle],
                "incremental_centroid_delta_m": delta,
                "incremental_downwind_projection_m": _project_xy(delta, unit_wind),
                "incremental_crosswind_projection_m": _cross_xy(delta, unit_wind),
                "incremental_vertical_response_m": delta[2],
            })
        by_angle = {row["child_angle_deg"]: row for row in witnesses}
        negative = by_angle[-5.0]["incremental_downwind_projection_m"]
        neutral_projection = by_angle[0.0]["incremental_downwind_projection_m"]
        positive = by_angle[5.0]["incremental_downwind_projection_m"]
        separation = positive - negative
        if abs(neutral_projection) > TOL:
            raise ValueError("same-parent neutral child projection drift")
        if abs(separation) <= 1e-9:
            raise ValueError("east-mid signed child witnesses are not Weather-separable")
        preferred = 5.0 if positive > negative else -5.0
        parent_rows.append({
            "parent_angle_deg": parent_angle,
            "parent_only_centroid_delta_m": parent_delta,
            "parent_only_downwind_projection_m": _project_xy(parent_delta, unit_wind),
            "parent_only_crosswind_projection_m": _cross_xy(parent_delta, unit_wind),
            "parent_only_vertical_response_m": parent_delta[2],
            "child_witnesses": witnesses,
            "preferred_child_angle_deg": preferred,
            "signed_child_projection_separation_m": abs(separation),
            "negative_child_projection_m": negative,
            "positive_child_projection_m": positive,
        })

    center = next(row for row in parent_rows if row["parent_angle_deg"] == 0.0)
    predecessor_reproduced = (
        center["preferred_child_angle_deg"] == PREDECESSOR_EAST_MID["preferred_angle_deg"]
        and abs(center["negative_child_projection_m"] - PREDECESSOR_EAST_MID["negative_projection_m"]) <= TOL
        and abs(center["positive_child_projection_m"] - PREDECESSOR_EAST_MID["positive_projection_m"]) <= TOL
        and abs(center["signed_child_projection_separation_m"] - PREDECESSOR_EAST_MID["separation_m"]) <= TOL
    )
    if not predecessor_reproduced:
        raise ValueError("neutral-parent east-mid VFX predecessor did not reproduce")

    signs = [row["preferred_child_angle_deg"] for row in parent_rows]
    stable = len(set(signs)) == 1 and signs[0] == 5.0
    checks = {
        "exact_rigging_hierarchy_prerequisite": owner["result"] == hierarchy.RESULT,
        "exact_weather_visual_direction": tuple(float(v) for v in wind_xy) == WEATHER_WIND_XY,
        "weather_semantics_visual_only": WEATHER_SEMANTICS == "VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED",
        "exact_parent_witnesses_only": tuple(parent_angles_deg) == PARENT_ANGLES_DEG,
        "exact_child_witnesses_only": tuple(child_angles_deg) == CHILD_ANGLES_DEG,
        "east_mid_partition_52v_72t": len(frame["selected"]) == 52 and frame["selected_triangles"] == 72,
        "neutral_parent_vfx_predecessor_reproduced": predecessor_reproduced,
        "all_same_parent_neutral_child_responses_zero": all(
            abs(next(w for w in row["child_witnesses"] if w["child_angle_deg"] == 0.0)["incremental_downwind_projection_m"]) <= TOL
            for row in parent_rows
        ),
        "all_signed_child_witnesses_separable": all(row["signed_child_projection_separation_m"] > 1e-9 for row in parent_rows),
        "no_physical_wind_claim": not claim_physical_wind,
        "no_animation_adoption_claim": not claim_animation_adoption,
        "no_runtime_controller_claim": not claim_runtime_controller,
        "no_gameplay_claim": not claim_gameplay,
        "no_art_acceptance_claim": not claim_art_acceptance,
    }
    result = PASS_RESULT if stable and all(checks.values()) else HOLD_RESULT
    return {
        "schema": SCHEMA,
        "result": result,
        "decision": {
            "state": "KEEP_EAST_MID_POSITIVE_CHILD_POLARITY_ACROSS_PARENT_REPRESENTATIVES__NO_WIND_OR_MOTION_ADOPTION" if stable else "PARENT_AWARE_CHILD_POLARITY_REQUIRED__NO_WIND_OR_MOTION_ADOPTION",
            "stable_positive_child_polarity": stable,
            "preferred_child_angle_deg_by_parent": {str(row["parent_angle_deg"]): row["preferred_child_angle_deg"] for row in parent_rows},
            "automatic_animation_adoption": False,
            "automatic_vfx_motion_adoption": False,
        },
        "rigging_owner": {"repository": "mike-axiom-mir/axm-nature-design", "pull_request": 14, "head": RIGGING_OWNER_HEAD, "result": owner["result"]},
        "vfx_predecessor": {"pull_request": 17, "head": VFX_SIGN_PREDECESSOR_HEAD, "east_mid": PREDECESSOR_EAST_MID, "reproduced": predecessor_reproduced},
        "weather_visual_direction_donor": {"repository": WEATHER_REPOSITORY, "pull_request": WEATHER_PR, "head": WEATHER_HEAD, "source_path": WEATHER_SOURCE_PATH, "source_blob_sha": WEATHER_SOURCE_BLOB_SHA, "wind_xy": list(WEATHER_WIND_XY), "normalized_wind_xy": list(unit_wind), "semantics": WEATHER_SEMANTICS},
        "measurements": {"parent_rows": parent_rows},
        "checks": checks,
        "truth_boundary": {
            "physical_wind_claimed": False,
            "wind_strength_force_drag_or_turbulence_authored": False,
            "animation_timing_or_motion_adopted": False,
            "plant_biomechanics_or_biological_rom_claimed": False,
            "whole_tree_simultaneous_motion_claimed": False,
            "continuous_collision_or_self_intersection_claimed": False,
            "target_host_playback_claimed": False,
            "runtime_controller_or_device_claimed": False,
            "gameplay_or_physics_claimed": False,
            "art_direction_or_visual_qa_acceptance_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }

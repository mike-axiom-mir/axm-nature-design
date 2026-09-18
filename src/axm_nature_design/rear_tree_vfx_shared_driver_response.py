"""VFX-owned spatial response review for the five Nature branch sockets.

This module consumes the exact Rigging shared-driver polarity adapter and evaluates
only a static spatial-response envelope against Weather's exact visual direction.
It does not author timing, cadence, physical wind, plant biomechanics, Animation,
Runtime behavior, gameplay, or production adoption.
"""
from __future__ import annotations

import copy
import math
from typing import Iterable

from .organic_form import build_mesh
from . import rear_tree_rigging as historical
from . import rear_tree_rigging_primary_branch_family as rigging_family
from . import rear_tree_rigging_shared_driver_polarity as shared_driver

SCHEMA = "axm.nature-vfx-shared-driver-spatial-response-envelope/v0.1"
RESULT = "PASS_FIVE_SOCKET_SHARED_DRIVER_VISUAL_RESPONSE_ENVELOPE"
RIGGING_OWNER_HEAD = "754797a815266a643c6b08f1606eb76ba95dd8c6"
VFX_SIGN_DONOR_HEAD = "ef7b35af27d5ca98a6447c1e33be07863e387305"
WEATHER_HEAD = "ca2eaba519e8449835b0ea6ef944b7080c3caa6a"
WEATHER_SOURCE_BLOB_SHA = "11298d447f262da8a78e43e2df68bc0346c99a2c"
WEATHER_WIND_XY = (1.0, 0.35)
WEATHER_SEMANTICS = "VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED"
BRANCH_IDS = shared_driver.BRANCH_IDS
SHARED_DRIVER_VALUES_DEG = (-5.0, -2.5, 0.0, 2.5, 5.0)
TOL = rigging_family.TOL


def _centroid(points: Iterable[Iterable[float]]) -> list[float]:
    rows = [tuple(float(value) for value in point) for point in points]
    if not rows:
        raise ValueError("centroid requires at least one point")
    return [sum(point[i] for point in rows) / len(rows) for i in range(3)]


def _normalize_xy(vector: Iterable[float]) -> tuple[float, float]:
    x, y = (float(value) for value in vector)
    length = math.hypot(x, y)
    if length <= 1e-12:
        raise ValueError("Weather visual direction must be non-zero")
    return (x / length, y / length)


def _project_xy(delta: Iterable[float], direction_xy: tuple[float, float]) -> float:
    dx, dy = float(delta[0]), float(delta[1])
    return dx * direction_xy[0] + dy * direction_xy[1]


def _lateral_xy(delta: Iterable[float], direction_xy: tuple[float, float]) -> float:
    dx, dy = float(delta[0]), float(delta[1])
    return dx * (-direction_xy[1]) + dy * direction_xy[0]


def _simultaneous_pose(source: dict, shared_driver_deg: float) -> dict:
    """Build one static simultaneous pose from unchanged Rigging child partitions."""
    rigging = rigging_family.evaluate(source)
    binding = shared_driver.evaluate(source)
    if binding["result"] != shared_driver.RESULT:
        raise ValueError("exact Rigging shared-driver polarity adapter is not green")

    mesh = build_mesh(source)
    neutral = [[float(value) for value in vertex] for vertex in mesh["vertices"]]
    deformed = copy.deepcopy(neutral)
    probe_by_branch = {
        row["branch_id"]: row for row in rigging["rigging_family"]["probes"]
    }

    selected_union: set[int] = set()
    branch_rows = []
    direction_xy = _normalize_xy(WEATHER_WIND_XY)

    for branch_id in BRANCH_IDS:
        probe = probe_by_branch[branch_id]
        selected = tuple(int(index) for index in probe["selected_vertex_indices"])
        overlap = selected_union.intersection(selected)
        if overlap:
            raise ValueError(f"Rigging child partitions overlap during VFX response review: {branch_id}")
        selected_union.update(selected)

        pivot = [float(value) for value in probe["joint_pivot_m"]]
        axis = [float(value) for value in probe["source_derived_axis"]]
        local_angle = shared_driver.local_angle_for_shared_driver(branch_id, shared_driver_deg)
        for index in selected:
            deformed[index] = historical._rotate_about_axis(neutral[index], pivot, axis, local_angle)

        neutral_centroid = _centroid(neutral[index] for index in selected)
        deformed_centroid = _centroid(deformed[index] for index in selected)
        delta = [deformed_centroid[i] - neutral_centroid[i] for i in range(3)]
        projection = _project_xy(delta, direction_xy)
        lateral = _lateral_xy(delta, direction_xy)
        branch_rows.append(
            {
                "branch_id": branch_id,
                "command_sign_multiplier": shared_driver.COMMAND_SIGN_MULTIPLIER[branch_id],
                "shared_driver_deg": float(shared_driver_deg),
                "mapped_local_angle_deg": float(local_angle),
                "selected_vertices": len(selected),
                "neutral_centroid_m": neutral_centroid,
                "deformed_centroid_m": deformed_centroid,
                "centroid_delta_m": delta,
                "weather_direction_projection_m": projection,
                "weather_lateral_projection_m": lateral,
            }
        )

    selected_ordered = sorted(selected_union)
    neutral_family_centroid = _centroid(neutral[index] for index in selected_ordered)
    deformed_family_centroid = _centroid(deformed[index] for index in selected_ordered)
    family_delta = [
        deformed_family_centroid[i] - neutral_family_centroid[i] for i in range(3)
    ]

    fixed = [index for index in range(len(neutral)) if index not in selected_union]
    max_fixed_drift = max(
        (historical._distance(deformed[index], neutral[index]) for index in fixed),
        default=0.0,
    )

    return {
        "shared_driver_deg": float(shared_driver_deg),
        "branch_rows": branch_rows,
        "selected_vertex_union": len(selected_union),
        "fixed_vertices": len(fixed),
        "maximum_fixed_vertex_drift_m": max_fixed_drift,
        "family_neutral_centroid_m": neutral_family_centroid,
        "family_deformed_centroid_m": deformed_family_centroid,
        "family_centroid_delta_m": family_delta,
        "family_weather_direction_projection_m": _project_xy(family_delta, direction_xy),
        "family_weather_lateral_projection_m": _lateral_xy(family_delta, direction_xy),
        "neutral_vertices": neutral,
        "deformed_vertices": deformed,
        "probe_by_branch": probe_by_branch,
    }


def evaluate(
    source: dict,
    *,
    wind_xy=WEATHER_WIND_XY,
    shared_driver_values_deg=SHARED_DRIVER_VALUES_DEG,
    claim_physical_wind: bool = False,
    claim_animation_motion: bool = False,
    claim_runtime_acceptance: bool = False,
    claim_gameplay: bool = False,
    claim_final_amplitude: bool = False,
    claim_simultaneous_motion: bool = False,
) -> dict:
    """Evaluate the exact static VFX response envelope over the Rigging probe interval."""
    requested_wind = tuple(float(value) for value in wind_xy)
    if requested_wind != WEATHER_WIND_XY:
        raise ValueError("exact Weather visual direction drift")
    drivers = tuple(float(value) for value in shared_driver_values_deg)
    if drivers != SHARED_DRIVER_VALUES_DEG:
        raise ValueError("shared-driver review field may not be widened, reduced, or retimed")
    if claim_physical_wind:
        raise ValueError("Weather visual direction is not physical wind")
    if claim_animation_motion:
        raise ValueError("static VFX response review cannot claim Animation motion")
    if claim_runtime_acceptance:
        raise ValueError("static VFX response review cannot claim Runtime acceptance")
    if claim_gameplay:
        raise ValueError("static VFX response review cannot claim gameplay semantics")
    if claim_final_amplitude:
        raise ValueError("Rigging diagnostic endpoints are not final vegetation amplitude")
    if claim_simultaneous_motion:
        raise ValueError("simultaneous static poses do not prove simultaneous motion")

    binding = shared_driver.evaluate(source)
    if binding["result"] != shared_driver.RESULT:
        raise ValueError("exact Rigging shared-driver polarity binding did not pass")
    if binding["lineage"]["vfx_donor_head"] != VFX_SIGN_DONOR_HEAD:
        raise ValueError("VFX sign-map donor identity drift")

    poses = [_simultaneous_pose(source, value) for value in drivers]
    by_driver = {float(row["shared_driver_deg"]): row for row in poses}
    neutral = by_driver[0.0]
    positive_half = by_driver[2.5]
    positive_full = by_driver[5.0]
    negative_half = by_driver[-2.5]
    negative_full = by_driver[-5.0]

    def branch_projection(pose: dict, branch_id: str) -> float:
        row = next(item for item in pose["branch_rows"] if item["branch_id"] == branch_id)
        return float(row["weather_direction_projection_m"])

    checks = {
        "exact_rigging_shared_driver_binding_green": binding["result"] == shared_driver.RESULT,
        "exact_branch_family": tuple(row["branch_id"] for row in neutral["branch_rows"]) == BRANCH_IDS,
        "selected_partitions_are_disjoint_and_complete": neutral["selected_vertex_union"] == 260,
        "fixed_receiver_count_is_expected": neutral["fixed_vertices"] == 130,
        "fixed_receiver_remains_exact": all(row["maximum_fixed_vertex_drift_m"] <= TOL for row in poses),
        "neutral_family_projection_is_zero": abs(neutral["family_weather_direction_projection_m"]) <= TOL,
        "neutral_branch_projections_are_zero": all(abs(branch_projection(neutral, branch_id)) <= TOL for branch_id in BRANCH_IDS),
        "positive_half_driver_moves_every_branch_downwind": all(branch_projection(positive_half, branch_id) > TOL for branch_id in BRANCH_IDS),
        "positive_full_driver_moves_every_branch_downwind": all(branch_projection(positive_full, branch_id) > TOL for branch_id in BRANCH_IDS),
        "negative_half_driver_moves_every_branch_upwind": all(branch_projection(negative_half, branch_id) < -TOL for branch_id in BRANCH_IDS),
        "negative_full_driver_moves_every_branch_upwind": all(branch_projection(negative_full, branch_id) < -TOL for branch_id in BRANCH_IDS),
        "positive_family_centroid_is_downwind": positive_half["family_weather_direction_projection_m"] > TOL
        and positive_full["family_weather_direction_projection_m"] > TOL,
        "negative_family_centroid_is_upwind": negative_half["family_weather_direction_projection_m"] < -TOL
        and negative_full["family_weather_direction_projection_m"] < -TOL,
        "full_positive_response_exceeds_half_positive_response": positive_full["family_weather_direction_projection_m"] > positive_half["family_weather_direction_projection_m"] > 0.0,
        "full_negative_response_exceeds_half_negative_response": abs(negative_full["family_weather_direction_projection_m"]) > abs(negative_half["family_weather_direction_projection_m"]) > 0.0,
        "no_physical_wind_claim": not claim_physical_wind,
        "no_animation_motion_claim": not claim_animation_motion,
        "no_runtime_acceptance_claim": not claim_runtime_acceptance,
        "no_gameplay_claim": not claim_gameplay,
        "no_final_amplitude_claim": not claim_final_amplitude,
        "no_simultaneous_motion_claim": not claim_simultaneous_motion,
    }
    if not all(checks.values()):
        failed = [name for name, ok in checks.items() if not ok]
        raise ValueError(f"VFX shared-driver spatial-response checks failed: {failed}")

    stripped_poses = []
    for pose in poses:
        stripped_poses.append({key: value for key, value in pose.items() if key not in {"neutral_vertices", "deformed_vertices", "probe_by_branch"}})

    return {
        "schema": SCHEMA,
        "result": RESULT,
        "lineage": {
            "rigging_owner_head": RIGGING_OWNER_HEAD,
            "rigging_shared_driver_result": shared_driver.RESULT,
            "vfx_sign_donor_head": VFX_SIGN_DONOR_HEAD,
            "weather_head": WEATHER_HEAD,
            "weather_source_blob_sha": WEATHER_SOURCE_BLOB_SHA,
            "weather_visual_direction_xy": list(WEATHER_WIND_XY),
            "weather_semantics": WEATHER_SEMANTICS,
            "source_owner_head": rigging_family.SOURCE_OWNER_HEAD,
            "geometry_receiver_head": rigging_family.GEOMETRY_RECEIVER_HEAD,
            "source_digest": rigging_family.EXPECTED_SOURCE_DIGEST,
            "migrated_mesh_digest": rigging_family.EXPECTED_MIGRATED_MESH_DIGEST,
        },
        "review": {
            "branch_ids": list(BRANCH_IDS),
            "shared_driver_values_deg": list(drivers),
            "pose_semantics": "STATIC_SIMULTANEOUS_VISUAL_RESPONSE_REVIEW_NOT_MOTION",
            "poses": stripped_poses,
        },
        "checks": checks,
        "truth_boundary": {
            "physical_wind_claimed": False,
            "animation_timing_cadence_or_motion_claimed": False,
            "runtime_controller_or_device_claimed": False,
            "gameplay_or_collision_claimed": False,
            "final_vegetation_amplitude_adopted": False,
            "simultaneous_multi_branch_motion_claimed": False,
            "technical_art_target_host_acceptance_claimed": False,
            "art_direction_or_visual_qa_acceptance_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }


def build_review_svg(source: dict) -> str:
    """Render a deterministic top-down centroid-vector review from actual geometry."""
    positive = _simultaneous_pose(source, 5.0)
    negative = _simultaneous_pose(source, -5.0)
    direction = _normalize_xy(WEATHER_WIND_XY)

    all_points = []
    for pose in (positive, negative):
        for row in pose["branch_rows"]:
            all_points.append(row["neutral_centroid_m"][:2])
            all_points.append(row["deformed_centroid_m"][:2])
    xs = [point[0] for point in all_points]
    ys = [point[1] for point in all_points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    pad = 0.18
    min_x -= pad
    max_x += pad
    min_y -= pad
    max_y += pad
    width, height = 1040, 520
    panel_w = 500
    margin = 42

    def project(point, x_offset):
        x, y = point
        span_x = max(max_x - min_x, 1e-9)
        span_y = max(max_y - min_y, 1e-9)
        px = x_offset + margin + (x - min_x) / span_x * (panel_w - 2 * margin)
        py = height - margin - (y - min_y) / span_y * (height - 2 * margin)
        return px, py

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#101318"/>',
        '<text x="20" y="26" fill="#f3f5f7" font-family="monospace" font-size="16">Nature VFX shared-driver response envelope — centroid vectors from actual generated geometry</text>',
    ]

    for panel_index, (pose, label) in enumerate(((negative, "shared -5°"), (positive, "shared +5°"))):
        x_offset = 10 + panel_index * 515
        parts.append(f'<rect x="{x_offset}" y="42" width="500" height="466" fill="#171c22" stroke="#3a4652"/>')
        parts.append(f'<text x="{x_offset + 16}" y="66" fill="#f3f5f7" font-family="monospace" font-size="15">{label}</text>')
        origin = project((0.0, 0.0), x_offset)
        arrow_end = (origin[0] + direction[0] * 70.0, origin[1] - direction[1] * 70.0)
        parts.append(f'<line x1="{origin[0]:.2f}" y1="{origin[1]:.2f}" x2="{arrow_end[0]:.2f}" y2="{arrow_end[1]:.2f}" stroke="#7fd7ff" stroke-width="3"/>')
        parts.append(f'<text x="{arrow_end[0] + 5:.2f}" y="{arrow_end[1] - 4:.2f}" fill="#7fd7ff" font-family="monospace" font-size="11">Weather visual dir</text>')
        for row in pose["branch_rows"]:
            neutral_xy = project(row["neutral_centroid_m"][:2], x_offset)
            deformed_xy = project(row["deformed_centroid_m"][:2], x_offset)
            projection_mm = row["weather_direction_projection_m"] * 1000.0
            parts.append(f'<line x1="{neutral_xy[0]:.2f}" y1="{neutral_xy[1]:.2f}" x2="{deformed_xy[0]:.2f}" y2="{deformed_xy[1]:.2f}" stroke="#ffca6a" stroke-width="2"/>')
            parts.append(f'<circle cx="{neutral_xy[0]:.2f}" cy="{neutral_xy[1]:.2f}" r="4" fill="#d8e0e8"/>')
            parts.append(f'<circle cx="{deformed_xy[0]:.2f}" cy="{deformed_xy[1]:.2f}" r="5" fill="#ffca6a"/>')
            parts.append(f'<text x="{deformed_xy[0] + 7:.2f}" y="{deformed_xy[1] - 5:.2f}" fill="#f3f5f7" font-family="monospace" font-size="10">{row["branch_id"]} {projection_mm:+.2f} mm</text>')

    parts.append('<text x="20" y="514" fill="#9da8b3" font-family="monospace" font-size="10">Review geometry only — not physical wind, Animation, Runtime, collision, Art/QA acceptance, or final amplitude.</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"

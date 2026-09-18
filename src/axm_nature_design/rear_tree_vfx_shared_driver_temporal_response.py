"""VFX-owned temporal Weather-direction review over the exact Animation shared driver.

This module consumes Nature Animation PR #22 and the exact Weather visual direction as
read-only donors. It does not retime Animation, change Rigging geometry, choose a
physical wind model, or adopt the diagnostic loop as final vegetation motion.

The bounded VFX question is narrower: across the already-authored 41-sample
simultaneous five-socket loop, does each generated branch and the selected family as a
whole keep a coherent signed world-space response along the exact Weather visual
 direction? Cross-direction and vertical motion are measured descriptively rather than
forced to zero because the five source-derived Rigging axes are intentionally distinct.
"""
from __future__ import annotations

import math
from typing import Iterable

from .organic_form import build_mesh, digest, validate_source
from . import rear_tree_animation_shared_driver as animation
from . import rear_tree_rigging_primary_branch_family as rig_family
from . import rear_tree_rigging_shared_driver_composition as rig_composition

SCHEMA = "axm.nature-vfx-shared-driver-temporal-weather-direction-response/v0.1"
RESULT = "PASS_FIVE_SOCKET_SHARED_DRIVER_TEMPORAL_VISUAL_DIRECTION_RESPONSE_REVIEW"
ANIMATION_OWNER_HEAD = "bfb66da82bc358b14e52711bbdef7b58e4c943af"
ANIMATION_MODULE_BLOB = "ac4e652948de4c7422f4f0ae8534e3be5937b896"
RIGGING_OWNER_HEAD = "b4b480b415047fea90b4740f7702ced0dba9142d"
VFX_STATIC_RESPONSE_HEAD = "ba1c12dd527f1ecc6a0eb4bc0b4322f15ccad475"
WEATHER_REPOSITORY = "mike-axiom-mir/axm-weather-design"
WEATHER_PULL_REQUEST = 2
WEATHER_OWNER_HEAD = "ca2eaba519e8449835b0ea6ef944b7080c3caa6a"
WEATHER_SOURCE_BLOB = "11298d447f262da8a78e43e2df68bc0346c99a2c"
WEATHER_VISUAL_DIRECTION_XY = (1.0, 0.35)
WEATHER_SEMANTICS = "VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED"
TOL = 1e-12


def _centroid(vertices: list[list[float]], indices: Iterable[int]) -> list[float]:
    selected = [vertices[int(index)] for index in indices]
    if not selected:
        raise ValueError("cannot measure an empty VFX receiver partition")
    count = float(len(selected))
    return [sum(float(vertex[axis]) for vertex in selected) / count for axis in range(3)]


def _sub(a: Iterable[float], b: Iterable[float]) -> list[float]:
    return [float(x) - float(y) for x, y in zip(a, b)]


def _normalized_weather_basis(direction_xy: Iterable[float]) -> tuple[tuple[float, float], tuple[float, float]]:
    values = tuple(float(value) for value in direction_xy)
    if len(values) != 2:
        raise ValueError("Weather visual direction must be a 2D vector")
    length = math.hypot(values[0], values[1])
    if length <= TOL:
        raise ValueError("Weather visual direction cannot be zero")
    parallel = (values[0] / length, values[1] / length)
    cross = (-parallel[1], parallel[0])
    return parallel, cross


def _project(delta: Iterable[float], parallel: tuple[float, float], cross: tuple[float, float]) -> dict:
    dx, dy, dz = (float(value) for value in delta)
    return {
        "parallel_m": dx * parallel[0] + dy * parallel[1],
        "cross_m": dx * cross[0] + dy * cross[1],
        "vertical_m": dz,
    }


def _expected_sign(value: float) -> int:
    if abs(float(value)) <= TOL:
        return 0
    return 1 if value > 0.0 else -1


def _sign_matches_driver(shared_driver_deg: float, parallel_m: float) -> bool:
    sign = _expected_sign(shared_driver_deg)
    if sign == 0:
        return abs(float(parallel_m)) <= TOL
    return float(parallel_m) * float(sign) > TOL


def evaluate(
    source: dict,
    *,
    requested_animation_head: str = ANIMATION_OWNER_HEAD,
    requested_weather_owner_head: str = WEATHER_OWNER_HEAD,
    requested_weather_direction_xy: Iterable[float] = WEATHER_VISUAL_DIRECTION_XY,
    claim_vfx_motion_adoption: bool = False,
    claim_physical_wind: bool = False,
    claim_natural_vegetation_motion: bool = False,
    claim_continuous_collision_clearance: bool = False,
    claim_target_engine_playback: bool = False,
    claim_runtime_acceptance: bool = False,
    claim_gameplay_acceptance: bool = False,
    claim_art_or_visual_qa_acceptance: bool = False,
) -> dict:
    """Measure the exact sampled Animation loop in the Weather visual-direction frame."""
    validate_source(source)
    if requested_animation_head != ANIMATION_OWNER_HEAD:
        raise ValueError("exact Animation owner head drift")
    if requested_weather_owner_head != WEATHER_OWNER_HEAD:
        raise ValueError("exact Weather owner head drift")
    requested_direction = tuple(float(value) for value in requested_weather_direction_xy)
    if requested_direction != WEATHER_VISUAL_DIRECTION_XY:
        raise ValueError("exact Weather visual direction drift")
    if claim_vfx_motion_adoption:
        raise ValueError("review evidence cannot adopt the diagnostic loop as VFX motion")
    if claim_physical_wind:
        raise ValueError("Weather donor is visual direction only, not physical wind")
    if claim_natural_vegetation_motion:
        raise ValueError("diagnostic Animation is not natural vegetation motion")
    if claim_continuous_collision_clearance:
        raise ValueError("sampled VFX response cannot claim continuous collision clearance")
    if claim_target_engine_playback:
        raise ValueError("source-space VFX review cannot claim target-engine playback")
    if claim_runtime_acceptance:
        raise ValueError("VFX review cannot claim Runtime or device acceptance")
    if claim_gameplay_acceptance:
        raise ValueError("VFX review cannot claim gameplay acceptance")
    if claim_art_or_visual_qa_acceptance:
        raise ValueError("VFX evidence cannot grant Art Direction or Visual QA acceptance")

    animation_evidence = animation.evaluate(source)
    if animation_evidence["result"] != animation.RESULT:
        raise ValueError("exact Animation shared-driver prerequisite is not green")
    if animation.RIGGING_OWNER_HEAD != RIGGING_OWNER_HEAD:
        raise ValueError("Animation no longer binds the exact expected Rigging owner")
    if rig_composition.VFX_STATIC_RESPONSE_HEAD != VFX_STATIC_RESPONSE_HEAD:
        raise ValueError("Rigging no longer binds the expected VFX static-response predecessor")

    mesh = build_mesh(source)
    if digest(mesh) != rig_family.EXPECTED_MIGRATED_MESH_DIGEST:
        raise ValueError("exact Geometry-migrated receiver identity drift")
    neutral = [[float(value) for value in vertex] for vertex in mesh["vertices"]]
    probes = [
        rig_family._probe_branch(source, mesh, branch_id)
        for branch_id in rig_composition.BRANCH_IDS
    ]
    probes_by_branch = {probe["branch_id"]: probe for probe in probes}
    selected_sets = {
        branch_id: set(int(index) for index in probes_by_branch[branch_id]["selected_vertex_indices"])
        for branch_id in rig_composition.BRANCH_IDS
    }
    selected_union = set().union(*(selected_sets[branch_id] for branch_id in rig_composition.BRANCH_IDS))
    fixed_indices = [index for index in range(len(neutral)) if index not in selected_union]
    if len(selected_union) != 260 or len(fixed_indices) != 130:
        raise ValueError("five-child receiver partition identity drift")

    parallel_axis, cross_axis = _normalized_weather_basis(requested_direction)
    neutral_branch_centroids = {
        branch_id: _centroid(neutral, selected_sets[branch_id])
        for branch_id in rig_composition.BRANCH_IDS
    }
    neutral_family_centroid = _centroid(neutral, selected_union)

    samples = []
    all_branch_parallel_signs_match = True
    all_family_parallel_signs_match = True
    maximum_family_parallel_abs = 0.0
    maximum_family_cross_abs = 0.0
    maximum_family_vertical_abs = 0.0
    maximum_branch_parallel_abs = 0.0
    maximum_branch_cross_abs = 0.0
    maximum_branch_vertical_abs = 0.0

    for index in range(animation.SAMPLE_COUNT):
        animation_sample = animation_evidence["samples"][index]
        shared_driver_deg = float(animation_sample["shared_driver_deg"])
        if abs(shared_driver_deg - animation._shared_driver_for_index(index)) > TOL:
            raise ValueError("Animation sample field no longer matches its exact authored driver")

        posed = rig_composition._compose(
            neutral,
            probes_by_branch,
            shared_driver_deg,
            rig_composition.BRANCH_IDS,
        )
        branches = {}
        for branch_id in rig_composition.BRANCH_IDS:
            posed_centroid = _centroid(posed, selected_sets[branch_id])
            displacement = _sub(posed_centroid, neutral_branch_centroids[branch_id])
            projected = _project(displacement, parallel_axis, cross_axis)
            sign_match = _sign_matches_driver(shared_driver_deg, projected["parallel_m"])
            all_branch_parallel_signs_match = all_branch_parallel_signs_match and sign_match
            maximum_branch_parallel_abs = max(maximum_branch_parallel_abs, abs(projected["parallel_m"]))
            maximum_branch_cross_abs = max(maximum_branch_cross_abs, abs(projected["cross_m"]))
            maximum_branch_vertical_abs = max(maximum_branch_vertical_abs, abs(projected["vertical_m"]))
            branches[branch_id] = {
                **projected,
                "parallel_sign_matches_shared_driver": sign_match,
            }

        posed_family_centroid = _centroid(posed, selected_union)
        family_displacement = _sub(posed_family_centroid, neutral_family_centroid)
        family = _project(family_displacement, parallel_axis, cross_axis)
        family_sign_match = _sign_matches_driver(shared_driver_deg, family["parallel_m"])
        all_family_parallel_signs_match = all_family_parallel_signs_match and family_sign_match
        maximum_family_parallel_abs = max(maximum_family_parallel_abs, abs(family["parallel_m"]))
        maximum_family_cross_abs = max(maximum_family_cross_abs, abs(family["cross_m"]))
        maximum_family_vertical_abs = max(maximum_family_vertical_abs, abs(family["vertical_m"]))

        samples.append(
            {
                "index": index,
                "time_s": float(animation_sample["time_s"]),
                "shared_driver_deg": shared_driver_deg,
                "family": {
                    **family,
                    "parallel_sign_matches_shared_driver": family_sign_match,
                },
                "branches": branches,
            }
        )

    neutral_indices = (0, 20, 40)
    neutral_samples_exact = all(
        abs(samples[index]["family"][component]) <= TOL
        and all(
            abs(samples[index]["branches"][branch_id][component]) <= TOL
            for branch_id in rig_composition.BRANCH_IDS
        )
        for index in neutral_indices
        for component in ("parallel_m", "cross_m", "vertical_m")
    )
    endpoint_response_closure = max(
        abs(samples[0]["family"][component] - samples[-1]["family"][component])
        for component in ("parallel_m", "cross_m", "vertical_m")
    )
    all_values_finite = all(
        math.isfinite(float(value))
        for sample in samples
        for value in (
            sample["shared_driver_deg"],
            sample["family"]["parallel_m"],
            sample["family"]["cross_m"],
            sample["family"]["vertical_m"],
        )
    ) and all(
        math.isfinite(float(branch[component]))
        for sample in samples
        for branch in sample["branches"].values()
        for component in ("parallel_m", "cross_m", "vertical_m")
    )

    checks = {
        "exact_animation_prerequisite_green": animation_evidence["result"] == animation.RESULT,
        "exact_animation_sample_count": len(samples) == 41,
        "exact_five_socket_receiver_partition": len(selected_union) == 260 and len(fixed_indices) == 130,
        "exact_weather_visual_direction_preserved": requested_direction == WEATHER_VISUAL_DIRECTION_XY,
        "all_branch_parallel_response_signs_follow_shared_driver": all_branch_parallel_signs_match,
        "family_parallel_response_sign_follows_shared_driver": all_family_parallel_signs_match,
        "neutral_landmarks_have_zero_visual_response": neutral_samples_exact,
        "endpoint_visual_response_closes": endpoint_response_closure <= TOL,
        "all_temporal_response_measurements_finite": all_values_finite,
    }
    if not all(checks.values()):
        raise ValueError("temporal Weather-direction VFX response checks failed")

    return {
        "schema": SCHEMA,
        "result": RESULT,
        "lineage": {
            "animation_owner_head": ANIMATION_OWNER_HEAD,
            "animation_module_blob": ANIMATION_MODULE_BLOB,
            "animation_result": animation.RESULT,
            "rigging_owner_head": RIGGING_OWNER_HEAD,
            "vfx_static_response_head": VFX_STATIC_RESPONSE_HEAD,
            "weather_repository": WEATHER_REPOSITORY,
            "weather_pull_request": WEATHER_PULL_REQUEST,
            "weather_owner_head": WEATHER_OWNER_HEAD,
            "weather_source_blob": WEATHER_SOURCE_BLOB,
            "weather_visual_direction_xy": list(WEATHER_VISUAL_DIRECTION_XY),
            "weather_semantics": WEATHER_SEMANTICS,
        },
        "review": {
            "sample_count": len(samples),
            "duration_s": animation.DURATION_S,
            "sample_rate_hz": animation.SAMPLE_RATE_HZ,
            "branch_ids": list(rig_composition.BRANCH_IDS),
            "selected_vertex_union": len(selected_union),
            "globally_fixed_vertices": len(fixed_indices),
            "weather_parallel_unit_xy": list(parallel_axis),
            "weather_cross_unit_xy": list(cross_axis),
            "pose_semantics": "EXACT_ANIMATION_SAMPLES_MEASURED_IN_WEATHER_VISUAL_DIRECTION_FRAME_NOT_NEW_MOTION",
            "samples": samples,
        },
        "measurements": {
            "maximum_family_parallel_abs_m": maximum_family_parallel_abs,
            "maximum_family_cross_abs_m": maximum_family_cross_abs,
            "maximum_family_vertical_abs_m": maximum_family_vertical_abs,
            "maximum_branch_parallel_abs_m": maximum_branch_parallel_abs,
            "maximum_branch_cross_abs_m": maximum_branch_cross_abs,
            "maximum_branch_vertical_abs_m": maximum_branch_vertical_abs,
            "endpoint_visual_response_closure_m": endpoint_response_closure,
        },
        "checks": checks,
        "truth_boundary": {
            "source_space_temporal_visual_direction_response_proven": True,
            "vfx_motion_adopted": False,
            "natural_vegetation_motion_claimed": False,
            "physical_wind_force_speed_or_turbulence_claimed": False,
            "continuous_collision_or_self_intersection_claimed": False,
            "technical_art_target_host_playback_claimed": False,
            "runtime_controller_or_device_claimed": False,
            "physics_or_gameplay_claimed": False,
            "art_direction_or_visual_qa_acceptance_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }

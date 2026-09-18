"""Animation-owned sampled loop over the exact five-socket Rigging shared driver.

This successor consumes the Rigging-owned simultaneous kinematic composition from
PR #14 without changing source geometry, pivots, axes, child partitions, the mixed
command-sign map, or the diagnostic -5..+5 degree interval. Animation contributes
only timing, sampled replay, loop/seam checks, and motion evidence.

The diagnostic parameter remains non-physical. This module does not claim wind,
source/biological ROM, continuous collision clearance, target-engine playback,
Runtime/controller behavior, gameplay, visual acceptance, CANON, or production
readiness.
"""
from __future__ import annotations

import math
from typing import Iterable

from .organic_form import build_mesh, digest, validate_source
from . import rear_tree_rigging as historical
from . import rear_tree_rigging_primary_branch_family as rig_family
from . import rear_tree_rigging_shared_driver_composition as rig_composition
from . import rear_tree_rigging_shared_driver_polarity as polarity

SCHEMA = "axm.nature-animation-five-socket-shared-driver-loop/v0.1"
RESULT = "PASS_FIVE_SOCKET_SHARED_DRIVER_SIMULTANEOUS_DIAGNOSTIC_LOOP_SAMPLED_MOTION"
RIGGING_OWNER_HEAD = "bbc6584accb91204b02b8d11193768556da036e5"
RIGGING_RESULT = rig_composition.RESULT
PREVIOUS_ANIMATION_HEAD = "b0771b3319b783103c8e4677d062c00419df7559"
TRUTH_LABEL = "ANIMATION_SHARED_DRIVER_DIAGNOSTIC_LOOP_NOT_WIND_NOT_BIOLOGICAL_ROM_NOT_COLLISION_NOT_CONTROLLER"
DURATION_S = 1.0
SAMPLE_RATE_HZ = 40
SAMPLE_COUNT = 41
VISIBLE_REPEAT_SAMPLES = 40
AMPLITUDE_DEG = 5.0
TOL = 1e-12


def _distance(a: Iterable[float], b: Iterable[float]) -> float:
    return math.sqrt(sum((float(x) - float(y)) ** 2 for x, y in zip(a, b)))


def _shared_driver_for_index(index: int) -> float:
    if index < 0 or index >= SAMPLE_COUNT:
        raise ValueError("sample index outside endpoint-inclusive shared-driver loop")
    if index in (0, 20, 40):
        return 0.0
    if index == 10:
        return AMPLITUDE_DEG
    if index == 30:
        return -AMPLITUDE_DEG
    t = float(index) / float(SAMPLE_RATE_HZ)
    return AMPLITUDE_DEG * (math.sin(2.0 * math.pi * t) ** 3)


def _pairwise_distances(vertices: list[list[float]]) -> list[float]:
    values = []
    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            values.append(_distance(vertices[i], vertices[j]))
    return values


def _max_abs_delta(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("mismatched evidence vector lengths")
    return max((abs(float(x) - float(y)) for x, y in zip(a, b)), default=0.0)


def _state_metrics(
    neutral: list[list[float]],
    posed: list[list[float]],
    probes_by_branch: dict[str, dict],
    fixed_indices: list[int],
) -> dict:
    maximum_fixed_drift = max((_distance(posed[i], neutral[i]) for i in fixed_indices), default=0.0)
    maximum_pivot_drift = 0.0
    maximum_pairwise_drift = 0.0
    maximum_axis_projection_drift = 0.0
    maximum_selected_displacement = 0.0
    per_branch = {}

    for branch_id in rig_composition.BRANCH_IDS:
        probe = probes_by_branch[branch_id]
        selected_indices = [int(i) for i in probe["selected_vertex_indices"]]
        pivot_indices = [int(i) for i in probe["generated_pivot_vertex_indices"]]
        pivot = [float(x) for x in probe["joint_pivot_m"]]
        axis = [float(x) for x in probe["source_derived_axis"]]

        pivot_drift = max((_distance(posed[i], neutral[i]) for i in pivot_indices), default=0.0)
        pairwise_drift = _max_abs_delta(
            _pairwise_distances([posed[i] for i in selected_indices]),
            _pairwise_distances([neutral[i] for i in selected_indices]),
        )
        axis_projection_drift = max(
            (
                abs(
                    historical._dot(historical._sub(posed[i], pivot), axis)
                    - historical._dot(historical._sub(neutral[i], pivot), axis)
                )
                for i in selected_indices
            ),
            default=0.0,
        )
        displacement = max((_distance(posed[i], neutral[i]) for i in selected_indices), default=0.0)

        maximum_pivot_drift = max(maximum_pivot_drift, pivot_drift)
        maximum_pairwise_drift = max(maximum_pairwise_drift, pairwise_drift)
        maximum_axis_projection_drift = max(maximum_axis_projection_drift, axis_projection_drift)
        maximum_selected_displacement = max(maximum_selected_displacement, displacement)
        per_branch[branch_id] = {
            "pivot_vertex_drift_m": pivot_drift,
            "rigid_child_pairwise_distance_drift_m": pairwise_drift,
            "child_axis_projection_drift_m": axis_projection_drift,
            "maximum_selected_vertex_displacement_m": displacement,
        }

    return {
        "globally_fixed_vertex_drift_m": maximum_fixed_drift,
        "maximum_pivot_vertex_drift_m": maximum_pivot_drift,
        "maximum_rigid_child_pairwise_distance_drift_m": maximum_pairwise_drift,
        "maximum_child_axis_projection_drift_m": maximum_axis_projection_drift,
        "maximum_selected_vertex_displacement_m": maximum_selected_displacement,
        "per_branch": per_branch,
    }


def evaluate(
    source: dict,
    *,
    duration_s: float = DURATION_S,
    sample_rate_hz: int = SAMPLE_RATE_HZ,
    amplitude_deg: float = AMPLITUDE_DEG,
    claim_wind_motion: bool = False,
    claim_physical_wind: bool = False,
    claim_biological_rom: bool = False,
    claim_continuous_collision_clearance: bool = False,
    claim_target_engine_playback: bool = False,
    claim_runtime_controller: bool = False,
    claim_gameplay_acceptance: bool = False,
) -> dict:
    """Sample one synchronized five-socket diagnostic loop over exact Rigging composition."""
    validate_source(source)
    if abs(float(duration_s) - DURATION_S) > TOL:
        raise ValueError("shared-driver Animation duration drift")
    if int(sample_rate_hz) != SAMPLE_RATE_HZ:
        raise ValueError("shared-driver Animation sample-rate drift")
    if abs(float(amplitude_deg) - AMPLITUDE_DEG) > TOL:
        raise ValueError("Animation may not widen or relabel the Rigging diagnostic interval")
    if claim_wind_motion or claim_physical_wind:
        raise ValueError("shared-driver diagnostic loop is not a wind-motion or physical-wind claim")
    if claim_biological_rom:
        raise ValueError("Rigging diagnostic interval is not source or biological ROM")
    if claim_continuous_collision_clearance:
        raise ValueError("Animation sampled motion cannot claim continuous collision clearance")
    if claim_target_engine_playback:
        raise ValueError("sampled source-mesh Animation evidence cannot claim target-engine playback")
    if claim_runtime_controller:
        raise ValueError("Animation evidence cannot claim Runtime controller acceptance")
    if claim_gameplay_acceptance:
        raise ValueError("Animation evidence cannot claim gameplay acceptance")

    rig = rig_composition.evaluate(source)
    if rig["result"] != RIGGING_RESULT:
        raise ValueError("exact Rigging shared-driver composition prerequisite is not green")
    certificate = rig["continuous_parameter_certificate"]
    if certificate["timing_or_playback_defined"]:
        raise ValueError("Rigging prerequisite unexpectedly owns timing/playback")
    if certificate["continuous_collision_clearance_proven"]:
        raise ValueError("Rigging prerequisite unexpectedly promotes continuous collision clearance")

    mesh = build_mesh(source)
    if digest(mesh) != rig_family.EXPECTED_MIGRATED_MESH_DIGEST:
        raise ValueError("exact Geometry-migrated receiver identity drift")
    neutral = [[float(value) for value in vertex] for vertex in mesh["vertices"]]
    probes = [rig_family._probe_branch(source, mesh, branch_id) for branch_id in rig_composition.BRANCH_IDS]
    probes_by_branch = {probe["branch_id"]: probe for probe in probes}
    selected_sets = {
        branch_id: set(int(i) for i in probes_by_branch[branch_id]["selected_vertex_indices"])
        for branch_id in rig_composition.BRANCH_IDS
    }
    selected_union = set().union(*(selected_sets[branch_id] for branch_id in rig_composition.BRANCH_IDS))
    fixed_indices = [index for index in range(len(neutral)) if index not in selected_union]
    if len(selected_union) != 260 or len(fixed_indices) != 130:
        raise ValueError("five-child receiver partition identity drift")

    samples = []
    posed_frames = []
    maximum_order_delta = 0.0
    maximum_fixed_drift = 0.0
    maximum_pivot_drift = 0.0
    maximum_pairwise_drift = 0.0
    maximum_axis_projection_drift = 0.0
    maximum_selected_displacement = 0.0
    maximum_adjacent_selected_step = 0.0

    for index in range(SAMPLE_COUNT):
        shared_driver_deg = _shared_driver_for_index(index)
        if shared_driver_deg < -AMPLITUDE_DEG - TOL or shared_driver_deg > AMPLITUDE_DEG + TOL:
            raise ValueError("sample escaped exact Rigging shared-driver interval")
        canonical = rig_composition._compose(
            neutral, probes_by_branch, shared_driver_deg, rig_composition.BRANCH_IDS
        )
        reverse = rig_composition._compose(
            neutral, probes_by_branch, shared_driver_deg, reversed(rig_composition.BRANCH_IDS)
        )
        order_delta = max((_distance(a, b) for a, b in zip(canonical, reverse)), default=0.0)
        metrics = _state_metrics(neutral, canonical, probes_by_branch, fixed_indices)
        if posed_frames:
            adjacent_step = max(
                (_distance(canonical[i], posed_frames[-1][i]) for i in selected_union),
                default=0.0,
            )
        else:
            adjacent_step = 0.0

        maximum_order_delta = max(maximum_order_delta, order_delta)
        maximum_fixed_drift = max(maximum_fixed_drift, metrics["globally_fixed_vertex_drift_m"])
        maximum_pivot_drift = max(maximum_pivot_drift, metrics["maximum_pivot_vertex_drift_m"])
        maximum_pairwise_drift = max(
            maximum_pairwise_drift, metrics["maximum_rigid_child_pairwise_distance_drift_m"]
        )
        maximum_axis_projection_drift = max(
            maximum_axis_projection_drift, metrics["maximum_child_axis_projection_drift_m"]
        )
        maximum_selected_displacement = max(
            maximum_selected_displacement, metrics["maximum_selected_vertex_displacement_m"]
        )
        maximum_adjacent_selected_step = max(maximum_adjacent_selected_step, adjacent_step)
        local_angles = {
            branch_id: polarity.local_angle_for_shared_driver(branch_id, shared_driver_deg)
            for branch_id in rig_composition.BRANCH_IDS
        }
        samples.append(
            {
                "index": index,
                "time_s": index / float(SAMPLE_RATE_HZ),
                "shared_driver_deg": shared_driver_deg,
                "local_angles_deg": local_angles,
                "composition_order_max_vertex_delta_m": order_delta,
                "maximum_selected_step_from_previous_m": adjacent_step,
                "pose_digest": digest({"vertices": canonical, "triangles": mesh["triangles"]}),
                **metrics,
            }
        )
        posed_frames.append(canonical)

    endpoint_closure = max(
        (_distance(posed_frames[0][i], posed_frames[-1][i]) for i in range(len(neutral))),
        default=0.0,
    )
    visible_wrap = max(
        (_distance(posed_frames[39][i], posed_frames[0][i]) for i in selected_union),
        default=0.0,
    )
    authored_final_step = max(
        (_distance(posed_frames[39][i], posed_frames[40][i]) for i in selected_union),
        default=0.0,
    )
    wrap_residual = abs(visible_wrap - authored_final_step)
    shared_driver_antisymmetry_error = max(
        (
            abs(samples[i]["shared_driver_deg"] + samples[40 - i]["shared_driver_deg"])
            for i in range(SAMPLE_COUNT)
        ),
        default=0.0,
    )

    owner_state_by_driver = {
        float(row["shared_driver_deg"]): row for row in rig["composition"]["states"]
    }
    representative_replay = []
    maximum_owner_metric_residual = 0.0
    for shared_driver_deg in rig_composition.REPRESENTATIVE_SHARED_DRIVER_DEG:
        posed = rig_composition._compose(
            neutral, probes_by_branch, shared_driver_deg, rig_composition.BRANCH_IDS
        )
        reverse = rig_composition._compose(
            neutral, probes_by_branch, shared_driver_deg, reversed(rig_composition.BRANCH_IDS)
        )
        metrics = _state_metrics(neutral, posed, probes_by_branch, fixed_indices)
        owner = owner_state_by_driver[float(shared_driver_deg)]
        residuals = {
            "composition_order_max_vertex_delta_m": abs(
                max((_distance(a, b) for a, b in zip(posed, reverse)), default=0.0)
                - float(owner["composition_order_max_vertex_delta_m"])
            ),
            "globally_fixed_vertex_drift_m": abs(
                metrics["globally_fixed_vertex_drift_m"]
                - float(owner["globally_fixed_vertex_max_drift_m"])
            ),
            "pivot_vertex_drift_m": abs(
                metrics["maximum_pivot_vertex_drift_m"] - float(owner["pivot_vertex_max_drift_m"])
            ),
            "rigid_child_pairwise_distance_drift_m": abs(
                metrics["maximum_rigid_child_pairwise_distance_drift_m"]
                - float(owner["rigid_child_pairwise_distance_max_drift_m"])
            ),
            "child_axis_projection_drift_m": abs(
                metrics["maximum_child_axis_projection_drift_m"]
                - float(owner["child_axis_projection_max_drift_m"])
            ),
            "maximum_selected_vertex_displacement_m": abs(
                metrics["maximum_selected_vertex_displacement_m"]
                - float(owner["maximum_selected_vertex_displacement_m"])
            ),
        }
        maximum_owner_metric_residual = max(
            maximum_owner_metric_residual, *residuals.values()
        )
        representative_replay.append(
            {"shared_driver_deg": shared_driver_deg, "metric_residuals": residuals}
        )

    expected_plus = {
        "south-low": 5.0,
        "north-low": -5.0,
        "east-mid": 5.0,
        "west-high": -5.0,
        "north-top": 5.0,
    }
    expected_minus = {branch_id: -value for branch_id, value in expected_plus.items()}

    checks = {
        "exact_rigging_prerequisite": rig["result"] == RIGGING_RESULT,
        "exact_sample_count": len(samples) == SAMPLE_COUNT,
        "exact_landmarks": samples[0]["shared_driver_deg"] == 0.0
        and samples[10]["shared_driver_deg"] == 5.0
        and samples[20]["shared_driver_deg"] == 0.0
        and samples[30]["shared_driver_deg"] == -5.0
        and samples[40]["shared_driver_deg"] == 0.0,
        "mixed_local_sign_landmarks_exact": samples[10]["local_angles_deg"] == expected_plus
        and samples[30]["local_angles_deg"] == expected_minus,
        "all_samples_inside_rigging_probe": all(
            -5.0 - TOL <= row["shared_driver_deg"] <= 5.0 + TOL for row in samples
        ),
        "sampled_composition_order_invariant": maximum_order_delta <= TOL,
        "sampled_globally_fixed_receiver_exact": maximum_fixed_drift <= TOL,
        "sampled_pivots_exact": maximum_pivot_drift <= TOL,
        "sampled_children_rigid": maximum_pairwise_drift <= TOL,
        "sampled_axis_projection_preserved": maximum_axis_projection_drift <= TOL,
        "endpoint_neutral_closure": endpoint_closure <= TOL,
        "repeat_wrap_matches_authored_final_step": wrap_residual <= TOL,
        "bidirectional_shared_driver_is_antisymmetric": shared_driver_antisymmetry_error <= TOL,
        "animation_replay_matches_rigging_representatives": maximum_owner_metric_residual <= TOL,
        "all_five_children_move_at_positive_peak": all(
            samples[10]["per_branch"][branch_id]["maximum_selected_vertex_displacement_m"] > 0.0
            for branch_id in rig_composition.BRANCH_IDS
        ),
        "wind_not_claimed": not claim_wind_motion and not claim_physical_wind,
        "biological_rom_not_claimed": not claim_biological_rom,
        "continuous_collision_not_claimed": not claim_continuous_collision_clearance,
        "target_engine_playback_not_claimed": not claim_target_engine_playback,
        "runtime_controller_not_claimed": not claim_runtime_controller,
        "gameplay_not_claimed": not claim_gameplay_acceptance,
    }

    return {
        "schema": SCHEMA,
        "result": RESULT if all(checks.values()) else "FAIL",
        "lineage": {
            "rigging_owner_head": RIGGING_OWNER_HEAD,
            "rigging_result": RIGGING_RESULT,
            "previous_animation_head": PREVIOUS_ANIMATION_HEAD,
            "geometry_receiver_head": rig_family.GEOMETRY_RECEIVER_HEAD,
            "source_owner_head": rig_family.SOURCE_OWNER_HEAD,
            "source_digest": rig_family.EXPECTED_SOURCE_DIGEST,
            "migrated_mesh_digest": rig_family.EXPECTED_MIGRATED_MESH_DIGEST,
            "vfx_static_response_head": rig_composition.VFX_STATIC_RESPONSE_HEAD,
        },
        "motion": {
            "clip_id": "east-rear-five-socket-shared-driver-diagnostic-loop-003",
            "truth_label": TRUTH_LABEL,
            "duration_s": DURATION_S,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "endpoint_inclusive_samples": SAMPLE_COUNT,
            "visible_repeating_samples": VISIBLE_REPEAT_SAMPLES,
            "curve": "shared_driver_deg = 5 * sin(2*pi*t)^3; exact landmarks clamped at 0/0.25/0.5/0.75/1.0 s",
            "shared_driver_interval_deg": [-5.0, 5.0],
            "command_sign_multiplier_by_branch": dict(rig_composition.COMMAND_SIGN_MULTIPLIER),
            "amplitude_semantics": "EXACT_RIGGING_DIAGNOSTIC_BOUND_ONLY_NOT_SOURCE_OR_BIOLOGICAL_ROM_OR_WIND_STRENGTH",
        },
        "receiver": {
            "branch_ids": list(rig_composition.BRANCH_IDS),
            "selected_vertex_union": len(selected_union),
            "globally_fixed_vertices": len(fixed_indices),
            "simultaneous_kinematic_composition_owner": "RIGGING_PR14",
        },
        "samples": samples,
        "representative_owner_replay": representative_replay,
        "measurements": {
            "maximum_composition_order_vertex_delta_m": maximum_order_delta,
            "maximum_globally_fixed_vertex_drift_m": maximum_fixed_drift,
            "maximum_pivot_vertex_drift_m": maximum_pivot_drift,
            "maximum_rigid_child_pairwise_distance_drift_m": maximum_pairwise_drift,
            "maximum_child_axis_projection_drift_m": maximum_axis_projection_drift,
            "maximum_selected_vertex_displacement_m": maximum_selected_displacement,
            "maximum_adjacent_selected_vertex_step_m": maximum_adjacent_selected_step,
            "endpoint_closure_m": endpoint_closure,
            "visible_wrap_step_m": visible_wrap,
            "authored_final_step_m": authored_final_step,
            "wrap_step_residual_m": wrap_residual,
            "shared_driver_antisymmetry_error_deg": shared_driver_antisymmetry_error,
            "maximum_owner_replay_metric_residual": maximum_owner_metric_residual,
        },
        "checks": checks,
        "truth_boundary": {
            "sampled_simultaneous_kinematic_motion_proven": True,
            "natural_vegetation_motion_claimed": False,
            "source_or_biological_rom_claimed": False,
            "physical_wind_or_biomechanics_claimed": False,
            "continuous_collision_or_self_intersection_claimed": False,
            "finite_geometry_collision_witnesses_promoted_to_continuous": False,
            "vfx_motion_adoption_claimed": False,
            "target_engine_or_godot_playback_claimed": False,
            "wall_clock_or_display_delivery_claimed": False,
            "runtime_controller_state_machine_or_device_claimed": False,
            "physics_or_gameplay_claimed": False,
            "art_direction_or_visual_qa_acceptance_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }

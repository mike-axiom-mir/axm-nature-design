"""Animation-owned temporal rebind for the current north-low Rigging exclusion gate.

The previous Nature Animation loop owns a frozen 1 s / 40 Hz / 41-sample sin^3 timing
identity.  Current Rigging now says the exact ``north-low`` diagnostic child is detached
from the trunk by indexed topology and must not inherit the upper-trunk diagnostic
parent frame while the exact attachment relation remains disjoint.

This module preserves the previous north-low child timing exactly and adds only a
same-phase bounded parent-command stress track.  The accepted child motion must remain
identical to the child-only reference at every sample; a deliberately inherited parent
frame is retained only as a discriminating counterfactual.

This is sampled diagnostic source-mesh motion, not wind, botanical mechanics, connected
skinning, target-host playback, Runtime/controller behavior, gameplay, CANON, or
production readiness.
"""
from __future__ import annotations

import math
from typing import Iterable

from .organic_form import build_mesh, digest, validate_source
from . import rear_tree_rigging as historical
from . import rear_tree_rigging_primary_branch_family as family
from . import rear_tree_rigging_north_low_parent_influence_gate as rig_gate
from . import rear_tree_rigging_north_low_attachment_representation_gate as attachment_gate

SCHEMA = "axm.nature-animation-north-low-parent-exclusion-temporal-rebind/v0.1"
RESULT = "PASS_NORTH_LOW_PARENT_EXCLUSION_TEMPORAL_REBIND_SAMPLED_DIAGNOSTIC_MOTION"
CURRENT_RIGGING_OWNER_HEAD = "69640e558f0c1ac59d4d0e3155676e0967a03d04"
CURRENT_RIGGING_SEMANTIC_HEAD = "061cf3235f177a2998bd5925d4e631d4d66cdf85"
PREVIOUS_ANIMATION_HEAD = "e89db4cd53387a477fc98353caa1cdbd47b82ac6"
TRUTH_LABEL = "DETACHED_DIAGNOSTIC_CHILD_TEMPORAL_REBIND_NOT_WIND_NOT_SKINNING_NOT_CONTROLLER"
DURATION_S = 1.0
SAMPLE_RATE_HZ = 40
SAMPLE_COUNT = 41
VISIBLE_REPEAT_SAMPLES = 40
CHILD_AMPLITUDE_DEG = 5.0
PARENT_STRESS_AMPLITUDE_DEG = 2.5
TOL = 1e-12


def _distance(a: Iterable[float], b: Iterable[float]) -> float:
    return math.sqrt(sum((float(x) - float(y)) ** 2 for x, y in zip(a, b)))


def _pairwise(vertices: list[list[float]]) -> list[float]:
    values = []
    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            values.append(_distance(vertices[i], vertices[j]))
    return values


def _max_abs_delta(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("mismatched evidence vector lengths")
    return max((abs(float(x) - float(y)) for x, y in zip(a, b)), default=0.0)


def _normalized_driver(index: int) -> float:
    if index < 0 or index >= SAMPLE_COUNT:
        raise ValueError("sample index outside endpoint-inclusive diagnostic loop")
    if index in (0, 20, 40):
        return 0.0
    if index == 10:
        return 1.0
    if index == 30:
        return -1.0
    t = float(index) / float(SAMPLE_RATE_HZ)
    return math.sin(2.0 * math.pi * t) ** 3


def _rotate_axis(axis: list[float], parent_axis: list[float], angle_deg: float) -> list[float]:
    rotated = historical._rotate_about_axis(axis, [0.0, 0.0, 0.0], parent_axis, angle_deg)
    return historical._norm(rotated)


def evaluate(
    source: dict,
    geometry_contract: dict,
    *,
    duration_s: float = DURATION_S,
    sample_rate_hz: int = SAMPLE_RATE_HZ,
    child_amplitude_deg: float = CHILD_AMPLITUDE_DEG,
    parent_stress_amplitude_deg: float = PARENT_STRESS_AMPLITUDE_DEG,
    inherit_parent_frame: bool = False,
    claim_wind_motion: bool = False,
    claim_biological_rom: bool = False,
    claim_connected_attachment: bool = False,
    claim_production_skinning: bool = False,
    claim_target_engine_playback: bool = False,
    claim_runtime_controller: bool = False,
    claim_gameplay_acceptance: bool = False,
) -> dict:
    """Sample the frozen north-low timing through the current Rigging exclusion gate."""
    validate_source(source)
    if abs(float(duration_s) - DURATION_S) > TOL:
        raise ValueError("Animation duration drift")
    if int(sample_rate_hz) != SAMPLE_RATE_HZ:
        raise ValueError("Animation sample-rate drift")
    if abs(float(child_amplitude_deg) - CHILD_AMPLITUDE_DEG) > TOL:
        raise ValueError("Animation may not widen or narrow the preserved child diagnostic amplitude")
    if abs(float(parent_stress_amplitude_deg) - PARENT_STRESS_AMPLITUDE_DEG) > TOL:
        raise ValueError("Animation parent stress track must stay inside the exact Rigging diagnostic interval")
    if claim_wind_motion:
        raise ValueError("diagnostic timing is not a wind-motion claim")
    if claim_biological_rom:
        raise ValueError("Rigging diagnostic intervals are not biological/source ROM")
    if claim_connected_attachment:
        raise ValueError("detached diagnostic child may not be promoted to connected attachment")
    if claim_production_skinning:
        raise ValueError("this Animation rebind is not production skinning")
    if claim_target_engine_playback:
        raise ValueError("source-mesh sampled evidence cannot claim target-engine playback")
    if claim_runtime_controller:
        raise ValueError("Animation evidence cannot claim Runtime controller acceptance")
    if claim_gameplay_acceptance:
        raise ValueError("Animation evidence cannot claim gameplay acceptance")

    attachment = attachment_gate.evaluate(source, geometry_contract)
    if attachment["result"] != attachment_gate.RESULT:
        raise ValueError("current Rigging attachment-representation prerequisite is not green")
    constraint = attachment["attachment_representation_constraint"]
    if constraint["mode"] != "DETACHED_DIAGNOSTIC_CHILD_SOCKET_ONLY":
        raise ValueError("north-low attachment representation drift")
    if constraint["upper_trunk_parent_influence_enabled"] is not False:
        raise ValueError("north-low parent exclusion drift")
    if constraint["diagnostic_parent_weight"] != 0.0:
        raise ValueError("north-low diagnostic parent weight drift")

    rig = rig_gate.evaluate(source)
    if rig["result"] != rig_gate.RESULT:
        raise ValueError("current north-low parent-influence gate prerequisite is not green")

    mesh = build_mesh(source)
    if digest(mesh) != family.EXPECTED_MIGRATED_MESH_DIGEST:
        raise ValueError("exact Geometry-migrated receiver identity drift")
    neutral = [[float(value) for value in vertex] for vertex in mesh["vertices"]]
    probe = family._probe_branch(source, mesh, rig_gate.CHILD_BRANCH_ID)
    selected_indices = [int(value) for value in probe["selected_vertex_indices"]]
    if len(selected_indices) != 52:
        raise ValueError("north-low selected vertex identity drift")

    child_pivot = [float(value) for value in probe["joint_pivot_m"]]
    child_axis = [float(value) for value in probe["source_derived_axis"]]
    parent_pivot = [float(value) for value in rig["parent_frame"]["pivot_m"]]
    parent_axis = [float(value) for value in rig["parent_frame"]["source_derived_axis"]]
    neutral_selected = [neutral[index] for index in selected_indices]
    neutral_pairwise = _pairwise(neutral_selected)

    samples = []
    accepted_frames = []
    maximum_parent_leak = 0.0
    maximum_pairwise_drift = 0.0
    maximum_axis_projection_drift = 0.0
    maximum_selected_displacement = 0.0
    maximum_adjacent_step = 0.0
    maximum_counterfactual_delta = 0.0
    maximum_counterfactual_socket_travel = 0.0

    for index in range(SAMPLE_COUNT):
        driver = _normalized_driver(index)
        previous_shared_driver_deg = CHILD_AMPLITUDE_DEG * driver
        child_angle_deg = -previous_shared_driver_deg
        parent_command_deg = PARENT_STRESS_AMPLITUDE_DEG * driver

        child_only = [
            historical._rotate_about_axis(neutral[i], child_pivot, child_axis, child_angle_deg)
            for i in selected_indices
        ]
        counter_pivot = historical._rotate_about_axis(
            child_pivot, parent_pivot, parent_axis, parent_command_deg
        )
        counter_axis = _rotate_axis(child_axis, parent_axis, parent_command_deg)
        counterfactual = []
        for i in selected_indices:
            parented = historical._rotate_about_axis(
                neutral[i], parent_pivot, parent_axis, parent_command_deg
            )
            counterfactual.append(
                historical._rotate_about_axis(
                    parented, counter_pivot, counter_axis, child_angle_deg
                )
            )

        accepted = counterfactual if inherit_parent_frame else child_only
        parent_leak = max(
            (_distance(accepted[i], child_only[i]) for i in range(len(selected_indices))),
            default=0.0,
        )
        counterfactual_delta = max(
            (_distance(counterfactual[i], child_only[i]) for i in range(len(selected_indices))),
            default=0.0,
        )
        counter_socket_travel = _distance(counter_pivot, child_pivot)
        pairwise_drift = _max_abs_delta(_pairwise(accepted), neutral_pairwise)
        axis_projection_drift = max(
            (
                abs(
                    historical._dot(historical._sub(accepted[j], child_pivot), child_axis)
                    - historical._dot(historical._sub(neutral[selected_indices[j]], child_pivot), child_axis)
                )
                for j in range(len(selected_indices))
            ),
            default=0.0,
        )
        displacement = max(
            (_distance(accepted[j], neutral[selected_indices[j]]) for j in range(len(selected_indices))),
            default=0.0,
        )
        adjacent_step = 0.0
        if accepted_frames:
            adjacent_step = max(
                (_distance(accepted[j], accepted_frames[-1][j]) for j in range(len(selected_indices))),
                default=0.0,
            )

        maximum_parent_leak = max(maximum_parent_leak, parent_leak)
        maximum_pairwise_drift = max(maximum_pairwise_drift, pairwise_drift)
        maximum_axis_projection_drift = max(maximum_axis_projection_drift, axis_projection_drift)
        maximum_selected_displacement = max(maximum_selected_displacement, displacement)
        maximum_adjacent_step = max(maximum_adjacent_step, adjacent_step)
        maximum_counterfactual_delta = max(maximum_counterfactual_delta, counterfactual_delta)
        maximum_counterfactual_socket_travel = max(
            maximum_counterfactual_socket_travel, counter_socket_travel
        )

        samples.append(
            {
                "index": index,
                "time_s": index / float(SAMPLE_RATE_HZ),
                "normalized_driver": driver,
                "previous_shared_driver_deg": previous_shared_driver_deg,
                "north_low_child_angle_deg": child_angle_deg,
                "upper_trunk_parent_stress_command_deg": parent_command_deg,
                "parent_command_leak_m": parent_leak,
                "rigid_child_pairwise_distance_drift_m": pairwise_drift,
                "child_axis_projection_drift_m": axis_projection_drift,
                "maximum_selected_vertex_displacement_m": displacement,
                "maximum_step_from_previous_m": adjacent_step,
                "counterfactual_inherited_parent_socket_travel_m": counter_socket_travel,
                "counterfactual_inherited_parent_output_delta_m": counterfactual_delta,
                "pose_digest": digest({"vertices": accepted, "selected_vertex_indices": selected_indices}),
            }
        )
        accepted_frames.append(accepted)

    endpoint_closure = max(
        (_distance(accepted_frames[0][j], accepted_frames[-1][j]) for j in range(len(selected_indices))),
        default=0.0,
    )
    visible_wrap = max(
        (_distance(accepted_frames[39][j], accepted_frames[0][j]) for j in range(len(selected_indices))),
        default=0.0,
    )
    authored_final_step = max(
        (_distance(accepted_frames[39][j], accepted_frames[40][j]) for j in range(len(selected_indices))),
        default=0.0,
    )
    wrap_residual = abs(visible_wrap - authored_final_step)
    antisymmetry_error = max(
        (
            abs(samples[i]["north_low_child_angle_deg"] + samples[40 - i]["north_low_child_angle_deg"])
            for i in range(SAMPLE_COUNT)
        ),
        default=0.0,
    )

    exact_landmarks = (
        samples[0]["north_low_child_angle_deg"] == 0.0
        and samples[10]["north_low_child_angle_deg"] == -5.0
        and samples[20]["north_low_child_angle_deg"] == 0.0
        and samples[30]["north_low_child_angle_deg"] == 5.0
        and samples[40]["north_low_child_angle_deg"] == 0.0
        and samples[10]["upper_trunk_parent_stress_command_deg"] == 2.5
        and samples[30]["upper_trunk_parent_stress_command_deg"] == -2.5
    )
    checks = {
        "exact_current_attachment_representation_gate_reexecuted": attachment["result"] == attachment_gate.RESULT,
        "exact_current_parent_exclusion_gate_reexecuted": rig["result"] == rig_gate.RESULT,
        "detached_diagnostic_child_identity_preserved": constraint["mode"] == "DETACHED_DIAGNOSTIC_CHILD_SOCKET_ONLY",
        "previous_animation_child_timing_landmarks_preserved": exact_landmarks,
        "all_samples_inside_child_rigging_interval": all(
            -5.0 - TOL <= row["north_low_child_angle_deg"] <= 5.0 + TOL for row in samples
        ),
        "all_parent_stress_commands_inside_rigging_interval": all(
            -2.5 - TOL <= row["upper_trunk_parent_stress_command_deg"] <= 2.5 + TOL for row in samples
        ),
        "parent_exclusion_temporally_preserved": maximum_parent_leak <= TOL,
        "rigid_child_motion_preserved": maximum_pairwise_drift <= TOL,
        "child_axis_projection_preserved": maximum_axis_projection_drift <= TOL,
        "loop_endpoint_closes": endpoint_closure <= TOL,
        "repeat_seam_matches_authored_final_step": wrap_residual <= TOL,
        "child_track_antisymmetric": antisymmetry_error <= TOL,
        "counterfactual_parent_inheritance_is_discriminating": maximum_counterfactual_delta > 1e-6,
        "counterfactual_socket_motion_is_discriminating": maximum_counterfactual_socket_travel > 1e-6,
    }
    if not all(checks.values()):
        raise ValueError(f"north-low Animation temporal rebind invariant failed: {checks}")

    return {
        "schema": SCHEMA,
        "result": RESULT,
        "truth_label": TRUTH_LABEL,
        "study_id": rig_gate.STUDY_ID,
        "current_rigging_owner_head": CURRENT_RIGGING_OWNER_HEAD,
        "current_rigging_semantic_head": CURRENT_RIGGING_SEMANTIC_HEAD,
        "previous_animation_head": PREVIOUS_ANIMATION_HEAD,
        "source_owner_head": rig_gate.SOURCE_OWNER_HEAD,
        "source_digest": rig_gate.EXPECTED_SOURCE_DIGEST,
        "geometry_receiver_mesh_digest": family.EXPECTED_MIGRATED_MESH_DIGEST,
        "timing": {
            "duration_s": DURATION_S,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "endpoint_inclusive_samples": SAMPLE_COUNT,
            "visible_repeat_samples": VISIBLE_REPEAT_SAMPLES,
            "curve": "sin(2*pi*t)^3",
            "preserves_previous_north_low_child_track": True,
        },
        "motion_scope": {
            "branch_id": rig_gate.CHILD_BRANCH_ID,
            "attachment_mode": constraint["mode"],
            "child_amplitude_deg": CHILD_AMPLITUDE_DEG,
            "parent_stress_amplitude_deg": PARENT_STRESS_AMPLITUDE_DEG,
            "parent_stress_is_command_only_not_trunk_deformation": True,
            "upper_trunk_parent_influence_enabled_for_north_low": False,
            "diagnostic_parent_weight": 0.0,
        },
        "measurements": {
            "sample_count": len(samples),
            "maximum_parent_command_leak_m": maximum_parent_leak,
            "maximum_rigid_child_pairwise_distance_drift_m": maximum_pairwise_drift,
            "maximum_child_axis_projection_drift_m": maximum_axis_projection_drift,
            "maximum_selected_vertex_displacement_m": maximum_selected_displacement,
            "maximum_adjacent_selected_step_m": maximum_adjacent_step,
            "endpoint_closure_m": endpoint_closure,
            "repeat_seam_residual_m": wrap_residual,
            "child_track_antisymmetry_error_deg": antisymmetry_error,
            "maximum_counterfactual_inherited_parent_socket_travel_m": maximum_counterfactual_socket_travel,
            "maximum_counterfactual_inherited_parent_output_delta_m": maximum_counterfactual_delta,
        },
        "samples": samples,
        "checks": checks,
        "truth_boundary": {
            "source_or_geometry_mutated": False,
            "rigging_socket_or_gate_mutated": False,
            "previous_child_timing_retimed": False,
            "connected_branch_trunk_attachment_claimed": False,
            "production_skinning_or_parent_weight_claimed": False,
            "wind_or_biological_motion_claimed": False,
            "continuous_collision_or_surface_continuity_claimed": False,
            "target_engine_playback_claimed": False,
            "wall_clock_40hz_delivery_claimed": False,
            "runtime_controller_state_machine_input_or_device_claimed": False,
            "physics_or_gameplay_claimed": False,
            "art_or_visual_qa_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }

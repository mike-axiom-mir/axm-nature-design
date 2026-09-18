"""Runtime-owned position-update budget proof for the east/rear Nature receiver.

The exact five-socket Rigging/VFX receiver has 390 generated vertices. This module
checks whether the 260 vertices that move in the pinned shared-driver review field are
already one contiguous source-index window, so Runtime can prepare a smaller position
packet without reindexing geometry at all.

This is a position-packet / proof-host preparation study only. It does not prove a
particular target-host partial-buffer API, target-device performance, draw-call change,
Animation or wind semantics, Art/QA acceptance, gameplay, or generic vegetation policy.
"""
from __future__ import annotations

import copy
import statistics
import time
from typing import Iterable

from .organic_form import build_mesh
from . import rear_tree_rigging as historical
from . import rear_tree_rigging_primary_branch_family as rigging_family
from . import rear_tree_rigging_shared_driver_polarity as shared_driver
from . import rear_tree_vfx_shared_driver_response as vfx_response

SCHEMA = "axm.nature-runtime-east-rear-existing-dynamic-window/v0.2"
RESULT = "PASS_EAST_REAR_EXISTING_DYNAMIC_WINDOW_POSITION_PACKET_REDUCTION"
VFX_OWNER_HEAD = "ba1c12dd527f1ecc6a0eb4bc0b4322f15ccad475"
BRANCH_IDS = vfx_response.BRANCH_IDS
DRIVER_VALUES_DEG = vfx_response.SHARED_DRIVER_VALUES_DEG
POSITION_VERTEX_BYTES = 3 * 4
EXPECTED_TOTAL_VERTICES = 390
EXPECTED_DYNAMIC_VERTICES = 260
EXPECTED_FIXED_VERTICES = 130
EXPECTED_DYNAMIC_WINDOW = (110, 370)
TOL = rigging_family.TOL


def _contiguous_runs(indices: Iterable[int]) -> list[tuple[int, int]]:
    ordered = sorted(set(int(index) for index in indices))
    if not ordered:
        return []
    runs: list[tuple[int, int]] = []
    start = previous = ordered[0]
    for index in ordered[1:]:
        if index == previous + 1:
            previous = index
        else:
            runs.append((start, previous + 1))
            start = previous = index
    runs.append((start, previous + 1))
    return runs


def _prepare(source: dict) -> dict:
    vfx = vfx_response.evaluate(source)
    if vfx["result"] != vfx_response.RESULT:
        raise ValueError("exact VFX shared-driver response prerequisite is not green")

    rigging = rigging_family.evaluate(source)
    probes = {row["branch_id"]: row for row in rigging["rigging_family"]["probes"]}
    mesh = build_mesh(source)
    neutral = [[float(value) for value in vertex] for vertex in mesh["vertices"]]
    if len(neutral) != EXPECTED_TOTAL_VERTICES:
        raise ValueError("east-rear receiver vertex count drift")

    dynamic_by_branch: dict[str, tuple[int, ...]] = {}
    dynamic_union: set[int] = set()
    for branch_id in BRANCH_IDS:
        selected = tuple(int(index) for index in probes[branch_id]["selected_vertex_indices"])
        if len(selected) != 52:
            raise ValueError(f"exact Rigging child size drift: {branch_id}")
        if dynamic_union.intersection(selected):
            raise ValueError(f"Rigging child partitions overlap: {branch_id}")
        dynamic_union.update(selected)
        dynamic_by_branch[branch_id] = selected

    if len(dynamic_union) != EXPECTED_DYNAMIC_VERTICES:
        raise ValueError("dynamic vertex union drift")
    fixed = tuple(index for index in range(EXPECTED_TOTAL_VERTICES) if index not in dynamic_union)
    if len(fixed) != EXPECTED_FIXED_VERTICES:
        raise ValueError("fixed vertex count drift")

    runs = _contiguous_runs(dynamic_union)
    if runs != [EXPECTED_DYNAMIC_WINDOW]:
        raise ValueError(f"moving vertices are no longer the exact contiguous window: {runs}")

    return {
        "vfx": vfx,
        "probes": probes,
        "neutral": neutral,
        "triangles": [[int(value) for value in triangle] for triangle in mesh["triangles"]],
        "dynamic_by_branch": dynamic_by_branch,
        "dynamic_union": tuple(sorted(dynamic_union)),
        "fixed": fixed,
        "dynamic_runs": runs,
    }


def build_layout(source: dict) -> dict:
    """Return the exact existing source-index dynamic window; no reindexing occurs."""
    prepared = _prepare(source)
    start, end = EXPECTED_DYNAMIC_WINDOW
    branch_ranges: dict[str, list[int]] = {}
    for branch_id in BRANCH_IDS:
        selected = prepared["dynamic_by_branch"][branch_id]
        branch_ranges[branch_id] = [min(selected) - start, max(selected) - start + 1]
    return {
        "dynamic_window_original_indices": [start, end],
        "branch_ranges_inside_window": branch_ranges,
        "static_prefix_original_indices": [0, start],
        "static_suffix_original_indices": [end, EXPECTED_TOTAL_VERTICES],
        "geometry_reindexed": False,
        "index_buffer_changed": False,
    }


def verify_layout(source: dict, layout: dict) -> dict:
    prepared = _prepare(source)
    if layout.get("dynamic_window_original_indices") != list(EXPECTED_DYNAMIC_WINDOW):
        raise ValueError("dynamic window boundary drift")
    if layout.get("static_prefix_original_indices") != [0, EXPECTED_DYNAMIC_WINDOW[0]]:
        raise ValueError("static prefix boundary drift")
    if layout.get("static_suffix_original_indices") != [EXPECTED_DYNAMIC_WINDOW[1], EXPECTED_TOTAL_VERTICES]:
        raise ValueError("static suffix boundary drift")
    if layout.get("geometry_reindexed") is not False or layout.get("index_buffer_changed") is not False:
        raise ValueError("existing contiguous window proof must not reindex geometry")

    start, end = EXPECTED_DYNAMIC_WINDOW
    if prepared["dynamic_union"] != tuple(range(start, end)):
        raise ValueError("dynamic union is not the complete exact window")
    for branch_id in BRANCH_IDS:
        selected = prepared["dynamic_by_branch"][branch_id]
        expected = [min(selected) - start, max(selected) - start + 1]
        if layout["branch_ranges_inside_window"].get(branch_id) != expected:
            raise ValueError(f"branch range drift inside dynamic window: {branch_id}")

    control_bytes = EXPECTED_TOTAL_VERTICES * POSITION_VERTEX_BYTES
    candidate_bytes = EXPECTED_DYNAMIC_VERTICES * POSITION_VERTEX_BYTES
    saved = control_bytes - candidate_bytes
    return {
        "total_vertices": EXPECTED_TOTAL_VERTICES,
        "dynamic_vertices": EXPECTED_DYNAMIC_VERTICES,
        "fixed_vertices": EXPECTED_FIXED_VERTICES,
        "dynamic_window_start_vertex": start,
        "dynamic_window_end_vertex_exclusive": end,
        "dynamic_window_regions": 1,
        "geometry_reindexed": False,
        "index_buffer_changed": False,
        "control_full_position_packet_bytes": control_bytes,
        "candidate_dynamic_window_position_packet_bytes": candidate_bytes,
        "position_packet_bytes_saved": saved,
        "position_packet_reduction_fraction": saved / control_bytes,
        "position_packet_reduction_percent": saved / control_bytes * 100.0,
    }


def _control_pose(prepared: dict, driver: float) -> list[list[float]]:
    deformed = copy.deepcopy(prepared["neutral"])
    for branch_id in BRANCH_IDS:
        probe = prepared["probes"][branch_id]
        pivot = [float(value) for value in probe["joint_pivot_m"]]
        axis = [float(value) for value in probe["source_derived_axis"]]
        angle = shared_driver.local_angle_for_shared_driver(branch_id, driver)
        for index in prepared["dynamic_by_branch"][branch_id]:
            deformed[index] = historical._rotate_about_axis(prepared["neutral"][index], pivot, axis, angle)
    return deformed


def _candidate_window_pose(prepared: dict, driver: float) -> list[list[float]]:
    start, end = EXPECTED_DYNAMIC_WINDOW
    dynamic = [copy.deepcopy(vertex) for vertex in prepared["neutral"][start:end]]
    for branch_id in BRANCH_IDS:
        probe = prepared["probes"][branch_id]
        pivot = [float(value) for value in probe["joint_pivot_m"]]
        axis = [float(value) for value in probe["source_derived_axis"]]
        angle = shared_driver.local_angle_for_shared_driver(branch_id, driver)
        for original_index in prepared["dynamic_by_branch"][branch_id]:
            local_index = original_index - start
            dynamic[local_index] = historical._rotate_about_axis(
                prepared["neutral"][original_index], pivot, axis, angle
            )
    return dynamic


def _expand_candidate(prepared: dict, dynamic: list[list[float]]) -> list[list[float]]:
    start, end = EXPECTED_DYNAMIC_WINDOW
    if len(dynamic) != end - start:
        raise ValueError("candidate dynamic-window packet length drift")
    expanded = copy.deepcopy(prepared["neutral"])
    expanded[start:end] = copy.deepcopy(dynamic)
    return expanded


def _max_component_delta(left: list[list[float]], right: list[list[float]]) -> float:
    if len(left) != len(right):
        raise ValueError("vertex array length mismatch")
    return max(
        (abs(left[index][component] - right[index][component])
         for index in range(len(left)) for component in range(3)),
        default=0.0,
    )


def evaluate(
    source: dict,
    *,
    requested_branch_ids=BRANCH_IDS,
    claim_generic_vegetation_policy: bool = False,
    claim_target_host_upload: bool = False,
    claim_target_device_performance: bool = False,
    claim_art_or_qa_acceptance: bool = False,
    claim_animation_or_wind_semantics: bool = False,
) -> dict:
    if tuple(requested_branch_ids) != BRANCH_IDS:
        raise ValueError("Runtime proof requires the exact five Rigging branch identities")
    if claim_generic_vegetation_policy:
        raise ValueError("one east-rear receiver cannot authorize a generic vegetation layout policy")
    if claim_target_host_upload:
        raise ValueError("position-window proof is not target-host partial-buffer evidence")
    if claim_target_device_performance:
        raise ValueError("proof-host evidence cannot claim target-device performance")
    if claim_art_or_qa_acceptance:
        raise ValueError("Runtime evidence cannot claim Art/QA acceptance")
    if claim_animation_or_wind_semantics:
        raise ValueError("Runtime representation does not author Animation or wind semantics")

    prepared = _prepare(source)
    layout = build_layout(source)
    metrics = verify_layout(source, layout)

    pose_rows = []
    max_delta = 0.0
    for driver in DRIVER_VALUES_DEG:
        control = _control_pose(prepared, float(driver))
        dynamic = _candidate_window_pose(prepared, float(driver))
        candidate = _expand_candidate(prepared, dynamic)
        delta = _max_component_delta(control, candidate)
        max_delta = max(max_delta, delta)
        pose_rows.append({
            "shared_driver_deg": float(driver),
            "control_candidate_max_vertex_component_delta_m": delta,
            "candidate_dynamic_position_count": len(dynamic),
        })

    checks = {
        "exact_vfx_prerequisite_green": prepared["vfx"]["result"] == vfx_response.RESULT,
        "exact_branch_family": tuple(prepared["dynamic_by_branch"]) == BRANCH_IDS,
        "exact_dynamic_fixed_partition": len(prepared["dynamic_union"]) == 260 and len(prepared["fixed"]) == 130,
        "moving_vertices_already_one_contiguous_window": prepared["dynamic_runs"] == [EXPECTED_DYNAMIC_WINDOW],
        "no_geometry_reindex_required": metrics["geometry_reindexed"] is False and metrics["index_buffer_changed"] is False,
        "all_five_driver_witnesses_position_exact": max_delta <= TOL,
        "candidate_position_packet_is_smaller": metrics["candidate_dynamic_window_position_packet_bytes"] < metrics["control_full_position_packet_bytes"],
        "no_generic_policy_claim": not claim_generic_vegetation_policy,
        "no_target_host_upload_claim": not claim_target_host_upload,
        "no_target_device_performance_claim": not claim_target_device_performance,
        "no_art_or_qa_acceptance_claim": not claim_art_or_qa_acceptance,
        "no_animation_or_wind_semantics_claim": not claim_animation_or_wind_semantics,
    }
    if not all(checks.values()):
        failed = [name for name, ok in checks.items() if not ok]
        raise ValueError(f"Runtime existing-window checks failed: {failed}")

    return {
        "schema": SCHEMA,
        "result": RESULT,
        "lineage": {
            "vfx_owner_head": VFX_OWNER_HEAD,
            "vfx_result": vfx_response.RESULT,
            "rigging_owner_head": vfx_response.RIGGING_OWNER_HEAD,
            "source_owner_head": rigging_family.SOURCE_OWNER_HEAD,
            "geometry_receiver_head": rigging_family.GEOMETRY_RECEIVER_HEAD,
            "source_digest": rigging_family.EXPECTED_SOURCE_DIGEST,
            "migrated_mesh_digest": rigging_family.EXPECTED_MIGRATED_MESH_DIGEST,
        },
        "representation": {
            "semantics": "POSITION_ONLY_EXISTING_SOURCE_INDEX_WINDOW_NOT_TARGET_HOST_BUFFER_UPLOAD",
            "branch_ids": list(BRANCH_IDS),
            **layout,
        },
        "measurements": {
            **metrics,
            "maximum_control_candidate_vertex_component_delta_m": max_delta,
            "pose_rows": pose_rows,
        },
        "visual_tradeoff": {
            "source_geometry_changed": False,
            "index_buffer_changed": False,
            "five_static_pose_position_delta_m": max_delta,
            "target_host_shaded_a_b_measured": False,
            "art_direction_review_state": "HOLD_TARGET_HOST_SHADED_OR_RECEIVING_SCENE_REVIEW",
        },
        "checks": checks,
        "truth_boundary": {
            "generic_vegetation_policy_claimed": False,
            "target_host_partial_buffer_upload_claimed": False,
            "target_device_performance_claimed": False,
            "draw_call_or_gpu_time_improvement_claimed": False,
            "animation_or_physical_wind_semantics_claimed": False,
            "art_direction_or_visual_qa_acceptance_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }


def benchmark(source: dict, *, iterations: int = 1200, warmup: int = 100) -> dict:
    """Observe Python proof-host preparation only; timing never gates PASS."""
    if iterations < 20 or warmup < 0:
        raise ValueError("benchmark requires at least 20 iterations and non-negative warmup")
    prepared = _prepare(source)
    drivers = tuple(float(value) for value in DRIVER_VALUES_DEG)
    for index in range(warmup):
        driver = drivers[index % len(drivers)]
        _control_pose(prepared, driver)
        _candidate_window_pose(prepared, driver)

    control_ns: list[int] = []
    candidate_ns: list[int] = []
    for index in range(iterations):
        driver = drivers[index % len(drivers)]
        order = ("control", "candidate") if index % 2 == 0 else ("candidate", "control")
        for mode in order:
            start = time.perf_counter_ns()
            if mode == "control":
                _control_pose(prepared, driver)
                control_ns.append(time.perf_counter_ns() - start)
            else:
                _candidate_window_pose(prepared, driver)
                candidate_ns.append(time.perf_counter_ns() - start)

    def percentile(values: list[int], fraction: float) -> int:
        ordered = sorted(values)
        return int(ordered[int(round((len(ordered) - 1) * fraction))])

    control_median = int(statistics.median(control_ns))
    candidate_median = int(statistics.median(candidate_ns))
    return {
        "semantics": "PYTHON_PROOF_HOST_CPU_PREPARATION_OBSERVATION_NOT_TARGET_DEVICE",
        "iterations": iterations,
        "warmup": warmup,
        "control_median_ns": control_median,
        "candidate_median_ns": candidate_median,
        "control_p95_ns": percentile(control_ns, 0.95),
        "candidate_p95_ns": percentile(candidate_ns, 0.95),
        "median_delta_ns": candidate_median - control_median,
        "candidate_over_control_median_ratio": candidate_median / control_median if control_median else None,
        "timing_used_as_acceptance_gate": False,
    }

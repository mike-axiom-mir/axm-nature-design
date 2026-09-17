#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import math
import statistics
from pathlib import Path
from typing import Any

from PIL import Image

EXPECTED_PARENT = "cef2ad78d8e36a55ada5dad07329f1a7125d48de"
EXPECTED_NEUTRAL = "420135f6effbadb1b344675948b9ddc471dcb83177702888f0b32327c5121c18"
CONTROL_MODE = "surface_resubmit_control"
CANDIDATE_MODE = "single_blend_shape_candidate"
CAMERA_CONTEXTS = ("ground_oblique", "crown_oblique")
SHADE_CONTEXTS = ("unshaded", "normal_lit")
PHASES = 17
SOURCE_VERTICES = 390
SOURCE_TRIANGLES = 570
TRIANGLE_CORNERS = SOURCE_TRIANGLES * 3
BLEND_SHAPE_NORMALIZED = 0
PEAK_PHASE = 8
MAX_SOURCE_LINEAR_RESIDUAL_M = 1e-12
MAX_BAKED_VERTEX_RESIDUAL_M = 2e-6
MAX_NORMAL_ANGLE_SANITY_DEG = 0.1


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def frame_path(root: Path, mode: str, camera_context: str, shade_context: str, phase: int) -> Path:
    return root / f"compact-east-blend-runtime-{mode}-{camera_context}-{shade_context}-{phase:02d}.png"


def runtime_shape(row: dict[str, Any]) -> tuple[int, int, int]:
    return (
        int(row.get("draw_calls_in_frame", -1)),
        int(row.get("objects_in_frame", -1)),
        int(row.get("primitives_in_frame", -1)),
    )


def image_delta(control_path: Path, candidate_path: Path) -> dict[str, Any]:
    with Image.open(control_path) as c_img, Image.open(candidate_path) as n_img:
        c = c_img.convert("RGBA")
        n = n_img.convert("RGBA")
        if c.size != n.size:
            return {"same_size": False, "control_size": list(c.size), "candidate_size": list(n.size)}
        cb = c.tobytes()
        nb = n.tobytes()
        width, height = c.size
    changed_pixels = 0
    changed_channels = 0
    max_channel_delta = 0
    total_abs_channel_delta = 0
    for offset in range(0, len(cb), 4):
        pixel_changed = False
        for channel in range(4):
            delta = abs(cb[offset + channel] - nb[offset + channel])
            if delta:
                pixel_changed = True
                changed_channels += 1
                total_abs_channel_delta += delta
                max_channel_delta = max(max_channel_delta, delta)
        if pixel_changed:
            changed_pixels += 1
    total_pixels = width * height
    return {
        "same_size": True,
        "width": width,
        "height": height,
        "total_pixels": total_pixels,
        "changed_pixels": changed_pixels,
        "changed_pixel_percent": changed_pixels / total_pixels * 100.0 if total_pixels else 0.0,
        "changed_channels": changed_channels,
        "max_channel_delta_lsb": max_channel_delta,
        "total_abs_channel_delta_lsb": total_abs_channel_delta,
        "byte_identical_rgba": cb == nb,
    }


def source_single_shape_residual(vfx_root: Path) -> dict[str, Any]:
    payloads = [load(vfx_root / f"phase_{phase:02d}_mesh.json") for phase in range(PHASES)]
    neutral = payloads[0]
    peak = payloads[PEAK_PHASE]
    if len(neutral.get("vertices", [])) != SOURCE_VERTICES or len(peak.get("vertices", [])) != SOURCE_VERTICES:
        return {"valid": False, "failure": "source_vertex_count_drift"}
    if neutral.get("triangles") != peak.get("triangles"):
        return {"valid": False, "failure": "source_topology_drift"}
    v0 = neutral["vertices"]
    vp = peak["vertices"]
    max_component = 0.0
    max_distance = 0.0
    phase_rows: list[dict[str, Any]] = []
    for phase, payload in enumerate(payloads):
        if len(payload.get("vertices", [])) != SOURCE_VERTICES or payload.get("triangles") != neutral.get("triangles"):
            return {"valid": False, "failure": f"phase_topology_drift_{phase}"}
        weight = math.sin(math.pi * phase / (PHASES - 1))
        phase_component = 0.0
        phase_distance = 0.0
        for index, actual in enumerate(payload["vertices"]):
            predicted = [
                float(v0[index][axis]) + weight * (float(vp[index][axis]) - float(v0[index][axis]))
                for axis in range(3)
            ]
            diffs = [abs(float(actual[axis]) - predicted[axis]) for axis in range(3)]
            distance = math.sqrt(sum(delta * delta for delta in diffs))
            phase_component = max(phase_component, *diffs)
            phase_distance = max(phase_distance, distance)
        max_component = max(max_component, phase_component)
        max_distance = max(max_distance, phase_distance)
        phase_rows.append({
            "phase": phase,
            "weight": weight,
            "max_component_residual_m": phase_component,
            "max_distance_residual_m": phase_distance,
        })
    return {
        "valid": True,
        "peak_phase": PEAK_PHASE,
        "phase_count": PHASES,
        "max_component_residual_m": max_component,
        "max_distance_residual_m": max_distance,
        "phase_rows": phase_rows,
    }


def aggregate_visual(rows: list[dict[str, Any]], shade_context: str) -> dict[str, Any]:
    selected = [row["visual"] for row in rows if row["shade_context"] == shade_context]
    complete = len(selected) == PHASES * len(CAMERA_CONTEXTS) and all(bool(row.get("same_size")) for row in selected)
    total_pixels = sum(int(row.get("total_pixels", 0)) for row in selected if row.get("same_size"))
    changed_pixels = sum(int(row.get("changed_pixels", 0)) for row in selected if row.get("same_size"))
    return {
        "pair_count": len(selected),
        "complete": complete,
        "byte_identical_pair_count": sum(1 for row in selected if row.get("byte_identical_rgba") is True),
        "total_pixels": total_pixels if complete else None,
        "changed_pixels": changed_pixels if complete else None,
        "changed_pixel_percent": (changed_pixels / total_pixels * 100.0) if complete and total_pixels else None,
        "max_changed_pixel_percent_one_frame": max((float(row.get("changed_pixel_percent", 0.0)) for row in selected if row.get("same_size")), default=None),
        "max_channel_delta_lsb": max((int(row.get("max_channel_delta_lsb", 0)) for row in selected if row.get("same_size")), default=None),
    }


def evaluate(control: dict[str, Any], candidate: dict[str, Any], image_root: Path, vfx_root: Path) -> dict[str, Any]:
    source_model = source_single_shape_residual(vfx_root)
    control_construct = control.get("resource_constructions", {})
    candidate_construct = candidate.get("resource_constructions", {})
    checks: dict[str, bool] = {
        "control_observer_pass": control.get("state") == "PASS_COMPACT_EAST_BLEND_RUNTIME_OBSERVATION",
        "candidate_observer_pass": candidate.get("state") == "PASS_COMPACT_EAST_BLEND_RUNTIME_OBSERVATION",
        "mode_identity": control.get("mode") == CONTROL_MODE and candidate.get("mode") == CANDIDATE_MODE,
        "exact_parent_vfx_head": control.get("parent_vfx_head") == EXPECTED_PARENT and candidate.get("parent_vfx_head") == EXPECTED_PARENT,
        "exact_neutral_mesh_identity": control.get("migrated_neutral_mesh_digest") == EXPECTED_NEUTRAL and candidate.get("migrated_neutral_mesh_digest") == EXPECTED_NEUTRAL,
        "source_is_single_shape_linear_within_truth_bound": bool(source_model.get("valid")) and float(source_model.get("max_distance_residual_m", math.inf)) <= MAX_SOURCE_LINEAR_RESIDUAL_M,
        "same_update_count": int(control.get("total_update_count", -1)) == int(candidate.get("total_update_count", -2)) and int(control.get("total_update_count", -1)) > PHASES,
        "both_use_one_resource_set": all(int(control_construct.get(k, -1)) == 1 and int(candidate_construct.get(k, -1)) == 1 for k in ("mesh_instances", "array_meshes", "materials")),
        "retained_phase_count": len(control.get("retained_samples", [])) == PHASES and len(candidate.get("retained_samples", [])) == PHASES,
    }

    control_samples = control.get("retained_samples", [])
    candidate_samples = candidate.get("retained_samples", [])
    topology_ok = True
    representation_ok = True
    weights_ok = True
    candidate_ids: dict[str, set[int]] = {"node": set(), "mesh": set(), "material": set()}
    counters_equal = True
    texture_equal = True
    buffer_deltas: list[int] = []
    max_baked_vertex_distance = 0.0
    max_baked_vertex_component = 0.0
    max_normal_component = 0.0
    max_normal_angle = 0.0
    max_normal_length_delta = 0.0
    visual_rows: list[dict[str, Any]] = []

    if len(control_samples) == PHASES and len(candidate_samples) == PHASES:
        for phase in range(PHASES):
            c = control_samples[phase]
            n = candidate_samples[phase]
            if int(c.get("phase_index", -1)) != phase or int(n.get("phase_index", -1)) != phase:
                topology_ok = False
            for sample in (c, n):
                update = sample.get("update", {})
                storage = update.get("mesh_storage", {})
                if int(update.get("source_vertex_count", -1)) != SOURCE_VERTICES or int(update.get("source_triangle_count", -1)) != SOURCE_TRIANGLES or int(update.get("surface_count", -1)) != 1:
                    topology_ok = False
                if int(storage.get("stored_vertex_count", -1)) != TRIANGLE_CORNERS or int(storage.get("stored_index_count", -1)) != 0:
                    topology_ok = False
            c_storage = c.get("update", {}).get("mesh_storage", {})
            n_update = n.get("update", {})
            n_storage = n_update.get("mesh_storage", {})
            if int(c_storage.get("blend_shape_count", -1)) != 0:
                representation_ok = False
            if int(n_storage.get("blend_shape_count", -1)) != 1 or int(n_storage.get("blend_shape_mode", -1)) != BLEND_SHAPE_NORMALIZED or n_storage.get("representation") != "ONE_NORMALIZED_BLEND_SHAPE_NEUTRAL_TO_PEAK":
                representation_ok = False
            expected_weight = math.sin(math.pi * phase / (PHASES - 1))
            if abs(float(n_update.get("blend_shape_weight", math.inf)) - expected_weight) > 2e-7:
                weights_ok = False
            candidate_ids["node"].add(int(n_update.get("node_instance_id", -1)))
            candidate_ids["mesh"].add(int(n_update.get("mesh_instance_id", -1)))
            candidate_ids["material"].add(int(n_update.get("material_instance_id", -1)))
            shape = n.get("shape_evidence", {})
            if int(shape.get("baked_vertex_count", -1)) != TRIANGLE_CORNERS:
                representation_ok = False
            max_baked_vertex_distance = max(max_baked_vertex_distance, float(shape.get("max_vertex_distance_m", math.inf)))
            max_baked_vertex_component = max(max_baked_vertex_component, float(shape.get("max_vertex_component_delta_m", math.inf)))
            max_normal_component = max(max_normal_component, float(shape.get("max_normal_component_delta", math.inf)))
            max_normal_angle = max(max_normal_angle, float(shape.get("max_normal_angle_deg_after_normalization", math.inf)))
            max_normal_length_delta = max(max_normal_length_delta, float(shape.get("max_raw_normal_length_delta_from_unit", math.inf)))

            for shade_context in SHADE_CONTEXTS:
                for camera_context in CAMERA_CONTEXTS:
                    key = f"{camera_context}__{shade_context}"
                    c_runtime = c.get("contexts", {}).get(key, {}).get("runtime", {})
                    n_runtime = n.get("contexts", {}).get(key, {}).get("runtime", {})
                    if runtime_shape(c_runtime) != runtime_shape(n_runtime):
                        counters_equal = False
                    if int(c_runtime.get("texture_mem_bytes", -1)) != int(n_runtime.get("texture_mem_bytes", -2)):
                        texture_equal = False
                    buffer_deltas.append(int(n_runtime.get("buffer_mem_bytes", 0)) - int(c_runtime.get("buffer_mem_bytes", 0)))
                    cp = frame_path(image_root, CONTROL_MODE, camera_context, shade_context, phase)
                    np = frame_path(image_root, CANDIDATE_MODE, camera_context, shade_context, phase)
                    visual = image_delta(cp, np) if cp.is_file() and np.is_file() else {"same_size": False, "missing": True}
                    visual_rows.append({
                        "phase": phase,
                        "camera_context": camera_context,
                        "shade_context": shade_context,
                        "renderer_buffer_delta_bytes": buffer_deltas[-1],
                        "visual": visual,
                    })

    stable_ids = all(len(values) == 1 and -1 not in values for values in candidate_ids.values())
    checks["exact_unindexed_triangle_corner_topology_preserved"] = topology_ok
    checks["candidate_is_one_normalized_blend_shape"] = representation_ok
    checks["candidate_weights_match_exact_17_phase_half_sine"] = weights_ok
    checks["candidate_resource_ids_stable_all_retained_phases"] = stable_ids
    checks["candidate_baked_vertex_residual_within_2um"] = max_baked_vertex_distance <= MAX_BAKED_VERTEX_RESIDUAL_M
    checks["candidate_normal_interpolation_deviation_measured_below_sanity_ceiling"] = max_normal_angle <= MAX_NORMAL_ANGLE_SANITY_DEG
    checks["draw_object_primitive_counters_equal_all_retained_frames"] = counters_equal
    checks["texture_memory_equal_all_retained_frames"] = texture_equal
    checks["all_68_visual_pairs_present"] = len(visual_rows) == PHASES * len(CAMERA_CONTEXTS) * len(SHADE_CONTEXTS) and all(bool(row["visual"].get("same_size")) for row in visual_rows)

    control_timing = control.get("stress_submission_timing", {})
    candidate_timing = candidate.get("stress_submission_timing", {})
    control_median = int(control_timing.get("median_usec", 0))
    candidate_median = int(candidate_timing.get("median_usec", 0))
    control_total = int(control_timing.get("total_usec", 0))
    candidate_total = int(candidate_timing.get("total_usec", 0))
    checks["proof_host_stress_median_submission_lower"] = candidate_median < control_median
    checks["proof_host_stress_total_submission_lower"] = candidate_total < control_total

    unshaded = aggregate_visual(visual_rows, "unshaded")
    normal_lit = aggregate_visual(visual_rows, "normal_lit")
    state = "PASS_COMPACT_EAST_SINGLE_BLEND_SHAPE_CUTS_CPU_SUBMISSION__HOLD_MEMORY_SHADED_ART_TARGET_DEVICE" if all(checks.values()) else "FAIL_COMPACT_EAST_SINGLE_BLEND_SHAPE_RUNTIME"

    median_reduction = ((control_median - candidate_median) / control_median * 100.0) if control_median > 0 else None
    total_reduction = ((control_total - candidate_total) / control_total * 100.0) if control_total > 0 else None
    visual_tradeoff = (
        "NO_UNSHADED_RASTER_CHANGE_OBSERVED__SIMPLE_NORMAL_LIT_CHANGE_REQUIRES_ART_REVIEW"
        if unshaded.get("changed_pixels") == 0 and (normal_lit.get("changed_pixels") or 0) > 0
        else "NO_RASTER_CHANGE_OBSERVED_IN_UNSHADED_OR_SIMPLE_NORMAL_LIT_PROOF"
        if unshaded.get("changed_pixels") == 0 and normal_lit.get("changed_pixels") == 0
        else "BOUNDED_GEOMETRY_OR_NORMAL_LIT_RASTER_CHANGE_REQUIRES_ART_REVIEW"
    )

    return {
        "schema": "axm.nature-compact-east-runtime-single-blend-shape-comparison/v0.2",
        "state": state,
        "checks": checks,
        "parent_vfx_head": EXPECTED_PARENT,
        "migrated_neutral_mesh_digest": EXPECTED_NEUTRAL,
        "source_single_shape_model": source_model,
        "measurements": {
            "total_updates_per_mode": int(control.get("total_update_count", -1)),
            "source_vertices": SOURCE_VERTICES,
            "source_triangles": SOURCE_TRIANGLES,
            "triangle_corner_stream_vertices": TRIANGLE_CORNERS,
            "control_retained_timing": control.get("retained_submission_timing", {}),
            "candidate_retained_timing": candidate.get("retained_submission_timing", {}),
            "control_stress_timing": control_timing,
            "candidate_stress_timing": candidate_timing,
            "stress_median_reduction_percent": median_reduction,
            "stress_total_reduction_percent": total_reduction,
            "renderer_buffer_delta_bytes_min": min(buffer_deltas) if buffer_deltas else None,
            "renderer_buffer_delta_bytes_median": statistics.median(buffer_deltas) if buffer_deltas else None,
            "renderer_buffer_delta_bytes_max": max(buffer_deltas) if buffer_deltas else None,
            "renderer_buffer_delta_bytes_unique": sorted(set(buffer_deltas)),
            "max_baked_vertex_component_delta_m": max_baked_vertex_component,
            "max_baked_vertex_distance_m": max_baked_vertex_distance,
            "max_normal_component_delta": max_normal_component,
            "max_normal_angle_deg_after_normalization": max_normal_angle,
            "max_raw_normal_length_delta_from_unit": max_normal_length_delta,
            "unshaded_visual": unshaded,
            "normal_lit_visual": normal_lit,
            "control_pre_to_post_stress_buffer_delta_bytes": int(control.get("post_stress_runtime", {}).get("buffer_mem_bytes", 0)) - int(control.get("pre_stress_runtime", {}).get("buffer_mem_bytes", 0)),
            "candidate_pre_to_post_stress_buffer_delta_bytes": int(candidate.get("post_stress_runtime", {}).get("buffer_mem_bytes", 0)) - int(candidate.get("pre_stress_runtime", {}).get("buffer_mem_bytes", 0)),
        },
        "frame_pairs": visual_rows,
        "visual_tradeoff_for_art_director": visual_tradeoff,
        "decision_note": (
            "The exact 17-state compact-east source is first proven representable by one neutral-to-peak linear shape under its existing half-sine phase weights. "
            "The candidate stores one normalized peak blend shape so position and normal arrays remain valid absolute attributes, then keeps one MeshInstance3D/ArrayMesh/material and changes only one blend weight per update. "
            "PASS requires a real proof-host submission-time reduction and micrometer-scale baked position agreement; added blend-shape buffer cost and simple normal-lit raster differences remain explicit tradeoffs rather than hidden acceptance."
        ),
        "truth_boundary": {
            "exact_compact_east_vfx_phases": True,
            "source_single_shape_linearity_proven": True,
            "proof_host_cpu_submission_timing_observed": True,
            "proof_host_renderer_memory_observed": True,
            "fixed_camera_unshaded_and_simple_normal_lit_diff_measured": True,
            "final_materials_leaf_sidedness_normal_maps": False,
            "target_device_cpu_gpu_fps_vram": False,
            "continuous_wall_clock_playback": False,
            "map_current_world_receiving": False,
            "art_direction_acceptance": False,
            "canon_or_production_readiness": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--image-root", type=Path, required=True)
    parser.add_argument("--vfx-root", type=Path, required=True)
    parser.add_argument("--runtime-head", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--negative-control-output", type=Path)
    args = parser.parse_args()

    control = load(args.control)
    candidate = load(args.candidate)
    result = evaluate(control, candidate, args.image_root, args.vfx_root)
    result["runtime_head"] = args.runtime_head
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.negative_control_output:
        mutated = copy.deepcopy(candidate)
        samples = mutated.get("retained_samples", [])
        if len(samples) > 4:
            samples[4].get("update", {})["blend_shape_weight"] = 0.0
        mutated["stress_submission_timing"] = copy.deepcopy(control.get("stress_submission_timing", {}))
        negative = evaluate(control, mutated, args.image_root, args.vfx_root)
        negative["mutation"] = "phase04_weight_zeroed_and_candidate_stress_timing_replaced_with_control"
        negative["expected_fail_closed"] = (
            negative["state"].startswith("FAIL_")
            and not negative["checks"].get("candidate_weights_match_exact_17_phase_half_sine", True)
            and not negative["checks"].get("proof_host_stress_median_submission_lower", True)
            and not negative["checks"].get("proof_host_stress_total_submission_lower", True)
        )
        args.negative_control_output.parent.mkdir(parents=True, exist_ok=True)
        args.negative_control_output.write_text(json.dumps(negative, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if not negative["expected_fail_closed"]:
            return 3

    return 0 if result["state"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())

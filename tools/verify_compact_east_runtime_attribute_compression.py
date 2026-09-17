#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import statistics
from pathlib import Path
from typing import Any

from PIL import Image

EXPECTED_PARENT = "cef2ad78d8e36a55ada5dad07329f1a7125d48de"
EXPECTED_NEUTRAL = "420135f6effbadb1b344675948b9ddc471dcb83177702888f0b32327c5121c18"
CONTROL_MODE = "reuse_arraymesh_candidate"
CANDIDATE_MODE = "reuse_arraymesh_compressed_attributes_candidate"
COMPRESS_FLAG = 536870912
CONTEXTS = ("ground_oblique", "crown_oblique")
PHASES = 17
SOURCE_VERTICES = 390
SOURCE_TRIANGLES = 570
TRIANGLE_CORNERS = SOURCE_TRIANGLES * 3


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def frame_path(root: Path, mode: str, context: str, phase: int) -> Path:
    return root / f"compact-east-runtime-{mode}-{context}-{phase:02d}.png"


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
    changed_pixels = 0
    max_channel_delta = 0
    changed_channels = 0
    total_abs_channel_delta = 0
    for offset in range(0, len(cb), 4):
        pixel_changed = False
        for channel in range(4):
            delta = abs(cb[offset + channel] - nb[offset + channel])
            if delta:
                pixel_changed = True
                changed_channels += 1
                total_abs_channel_delta += delta
                if delta > max_channel_delta:
                    max_channel_delta = delta
        if pixel_changed:
            changed_pixels += 1
    total_pixels = c.size[0] * c.size[1]
    return {
        "same_size": True,
        "width": c.size[0],
        "height": c.size[1],
        "total_pixels": total_pixels,
        "changed_pixels": changed_pixels,
        "changed_pixel_percent": (changed_pixels / total_pixels * 100.0) if total_pixels else 0.0,
        "changed_channels": changed_channels,
        "max_channel_delta_lsb": max_channel_delta,
        "total_abs_channel_delta_lsb": total_abs_channel_delta,
        "byte_identical_rgba": cb == nb,
    }


def evaluate(control: dict[str, Any], candidate: dict[str, Any], image_root: Path) -> dict[str, Any]:
    control_construct = control.get("resource_constructions", {})
    candidate_construct = candidate.get("resource_constructions", {})
    checks: dict[str, bool] = {
        "control_observer_pass": control.get("state") == "PASS_COMPACT_EAST_RUNTIME_RESOURCE_OBSERVATION",
        "candidate_observer_pass": candidate.get("state") == "PASS_COMPACT_EAST_RUNTIME_RESOURCE_OBSERVATION",
        "mode_identity": control.get("mode") == CONTROL_MODE and candidate.get("mode") == CANDIDATE_MODE,
        "exact_parent_vfx_head": control.get("parent_vfx_head") == EXPECTED_PARENT and candidate.get("parent_vfx_head") == EXPECTED_PARENT,
        "exact_neutral_mesh_identity": control.get("migrated_neutral_mesh_digest") == EXPECTED_NEUTRAL and candidate.get("migrated_neutral_mesh_digest") == EXPECTED_NEUTRAL,
        "same_update_count": int(control.get("total_update_count", -1)) == int(candidate.get("total_update_count", -2)) and int(control.get("total_update_count", -1)) > PHASES,
        "both_reuse_one_resource_set": all(int(control_construct.get(k, -1)) == 1 and int(candidate_construct.get(k, -1)) == 1 for k in ("mesh_instances", "array_meshes", "materials")),
        "retained_phase_count": len(control.get("retained_samples", [])) == PHASES and len(candidate.get("retained_samples", [])) == PHASES,
    }

    topology_ok = True
    control_format_ok = True
    candidate_format_ok = True
    stable_ids = True
    candidate_ids: dict[str, set[int]] = {"node": set(), "mesh": set(), "material": set()}
    counters_equal = True
    texture_equal = True
    buffer_deltas: list[int] = []
    frame_rows: list[dict[str, Any]] = []
    control_samples = control.get("retained_samples", [])
    candidate_samples = candidate.get("retained_samples", [])

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

            cs = c.get("update", {}).get("mesh_storage", {})
            ns = n.get("update", {}).get("mesh_storage", {})
            if bool(cs.get("requested_compressed_attributes", True)) or bool(cs.get("compressed_attributes_flag_present", True)) or (int(cs.get("surface_format", 0)) & COMPRESS_FLAG) != 0:
                control_format_ok = False
            if not bool(ns.get("requested_compressed_attributes", False)) or not bool(ns.get("compressed_attributes_flag_present", False)) or (int(ns.get("surface_format", 0)) & COMPRESS_FLAG) == 0:
                candidate_format_ok = False

            nu = n.get("update", {})
            candidate_ids["node"].add(int(nu.get("node_instance_id", -1)))
            candidate_ids["mesh"].add(int(nu.get("mesh_instance_id", -1)))
            candidate_ids["material"].add(int(nu.get("material_instance_id", -1)))

            for context in CONTEXTS:
                c_context = c.get("contexts", {}).get(context, {})
                n_context = n.get("contexts", {}).get(context, {})
                c_runtime = c_context.get("runtime", {})
                n_runtime = n_context.get("runtime", {})
                if runtime_shape(c_runtime) != runtime_shape(n_runtime):
                    counters_equal = False
                if int(c_runtime.get("texture_mem_bytes", -1)) != int(n_runtime.get("texture_mem_bytes", -2)):
                    texture_equal = False
                buffer_delta = int(n_runtime.get("buffer_mem_bytes", 0)) - int(c_runtime.get("buffer_mem_bytes", 0))
                buffer_deltas.append(buffer_delta)

                cp = frame_path(image_root, CONTROL_MODE, context, phase)
                np = frame_path(image_root, CANDIDATE_MODE, context, phase)
                if cp.is_file() and np.is_file():
                    visual = image_delta(cp, np)
                else:
                    visual = {"same_size": False, "missing": True}
                frame_rows.append({
                    "phase": phase,
                    "context": context,
                    "renderer_buffer_delta_bytes": buffer_delta,
                    "visual": visual,
                })

    stable_ids = all(len(values) == 1 and -1 not in values for values in candidate_ids.values())
    checks["exact_source_topology_and_unindexed_stream_preserved"] = topology_ok
    checks["control_uncompressed_surface_format"] = control_format_ok
    checks["candidate_compressed_surface_format"] = candidate_format_ok
    checks["candidate_resource_ids_stable_all_retained_phases"] = stable_ids
    checks["draw_object_primitive_counters_equal_all_retained_frames"] = counters_equal
    checks["texture_memory_equal_all_retained_frames"] = texture_equal
    checks["renderer_buffer_memory_lower_all_34_retained_frames"] = len(buffer_deltas) == PHASES * len(CONTEXTS) and all(delta < 0 for delta in buffer_deltas)

    visual_rows = [row["visual"] for row in frame_rows]
    visual_complete = len(visual_rows) == PHASES * len(CONTEXTS) and all(bool(row.get("same_size")) for row in visual_rows)
    changed_pixels = sum(int(row.get("changed_pixels", 0)) for row in visual_rows if row.get("same_size"))
    total_pixels = sum(int(row.get("total_pixels", 0)) for row in visual_rows if row.get("same_size"))
    max_lsb = max((int(row.get("max_channel_delta_lsb", 0)) for row in visual_rows if row.get("same_size")), default=None)
    max_changed_percent = max((float(row.get("changed_pixel_percent", 0.0)) for row in visual_rows if row.get("same_size")), default=None)
    byte_identical_count = sum(1 for row in visual_rows if row.get("byte_identical_rgba") is True)

    control_timing = control.get("stress_submission_timing", {})
    candidate_timing = candidate.get("stress_submission_timing", {})
    c_med = int(control_timing.get("median_usec", 0))
    n_med = int(candidate_timing.get("median_usec", 0))
    timing_tradeoff = "COMPRESSION_FASTER_ON_PROOF_HOST" if n_med < c_med else "COMPRESSION_SAME_MEDIAN_ON_PROOF_HOST" if n_med == c_med else "COMPRESSION_COSTS_CPU_ON_PROOF_HOST"

    state = "PASS_COMPACT_EAST_ATTRIBUTE_COMPRESSION_REDUCES_RENDERER_BUFFER__HOLD_VISUAL_CPU_AND_TARGET_DEVICE" if all(checks.values()) else "FAIL_COMPACT_EAST_ATTRIBUTE_COMPRESSION_REDUCES_RENDERER_BUFFER"
    if visual_complete and changed_pixels == 0:
        visual_tradeoff = "NONE_OBSERVED_34_MATCHED_UNSHADED_FRAMES_PIXEL_IDENTICAL__FINAL_SHADED_REVIEW_STILL_REQUIRED"
    elif visual_complete:
        visual_tradeoff = "BOUNDED_RASTER_CHANGE_REQUIRES_ART_REVIEW"
    else:
        visual_tradeoff = "VISUAL_COMPARISON_INCOMPLETE__HOLD"

    return {
        "schema": "axm.nature-compact-east-runtime-attribute-compression-comparison/v0.1",
        "state": state,
        "checks": checks,
        "parent_vfx_head": EXPECTED_PARENT,
        "migrated_neutral_mesh_digest": EXPECTED_NEUTRAL,
        "measurements": {
            "total_updates_per_mode": int(control.get("total_update_count", -1)),
            "source_vertices": SOURCE_VERTICES,
            "source_triangles": SOURCE_TRIANGLES,
            "triangle_corner_stream_vertices": TRIANGLE_CORNERS,
            "renderer_buffer_delta_bytes_min": min(buffer_deltas) if buffer_deltas else None,
            "renderer_buffer_delta_bytes_median": statistics.median(buffer_deltas) if buffer_deltas else None,
            "renderer_buffer_delta_bytes_max": max(buffer_deltas) if buffer_deltas else None,
            "renderer_buffer_delta_bytes_unique": sorted(set(buffer_deltas)),
            "control_retained_timing": control.get("retained_submission_timing", {}),
            "candidate_retained_timing": candidate.get("retained_submission_timing", {}),
            "control_stress_timing": control_timing,
            "candidate_stress_timing": candidate_timing,
            "stress_median_delta_usec": n_med - c_med,
            "stress_total_delta_usec": int(candidate_timing.get("total_usec", 0)) - int(control_timing.get("total_usec", 0)),
            "proof_host_cpu_tradeoff": timing_tradeoff,
            "visual_pair_count": len(frame_rows),
            "visual_byte_identical_pair_count": byte_identical_count,
            "visual_changed_pixels_total": changed_pixels if visual_complete else None,
            "visual_total_pixels": total_pixels if visual_complete else None,
            "visual_changed_pixel_percent_total": (changed_pixels / total_pixels * 100.0) if visual_complete and total_pixels else None,
            "visual_max_changed_pixel_percent_one_frame": max_changed_percent,
            "visual_max_channel_delta_lsb": max_lsb,
        },
        "frame_pairs": frame_rows,
        "visual_tradeoff_for_art_director": visual_tradeoff,
        "decision_note": "The candidate changes only the receiving ArrayMesh attribute representation by requesting Mesh.ARRAY_FLAG_COMPRESS_ATTRIBUTES after the same triangle-corner geometry and generated normals. PASS requires an actual lower RenderingServer buffer allocation in all 34 retained observations; proof-host CPU timing and raster differences are reported as tradeoffs, not hidden acceptance gates.",
        "truth_boundary": {
            "exact_compact_east_vfx_phases": True,
            "stable_resource_lifecycle_preserved": True,
            "attribute_compression_only": True,
            "proof_host_renderer_memory_observed": True,
            "proof_host_cpu_submission_timing_observed": True,
            "fixed_camera_unshaded_raster_diff_measured": True,
            "final_shaded_normal_equivalence": False,
            "target_device_cpu_gpu_fps_vram": False,
            "continuous_wall_clock_playback": False,
            "map_current_world_receiving": False,
            "final_materials_leaf_sidedness": False,
            "art_direction_acceptance": False,
            "canon_or_production_readiness": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--image-root", type=Path, required=True)
    parser.add_argument("--runtime-head", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--negative-control-output", type=Path)
    args = parser.parse_args()

    control = load(args.control)
    candidate = load(args.candidate)
    result = evaluate(control, candidate, args.image_root)
    result["runtime_head"] = args.runtime_head
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.negative_control_output:
        mutated = copy.deepcopy(candidate)
        for phase, sample in enumerate(mutated.get("retained_samples", [])):
            storage = sample.get("update", {}).get("mesh_storage", {})
            storage["requested_compressed_attributes"] = False
            storage["compressed_attributes_flag_present"] = False
            storage["surface_format"] = int(storage.get("surface_format", 0)) & ~COMPRESS_FLAG
            control_sample = control.get("retained_samples", [])[phase]
            for context in CONTEXTS:
                c_runtime = control_sample.get("contexts", {}).get(context, {}).get("runtime", {})
                n_runtime = sample.get("contexts", {}).get(context, {}).get("runtime", {})
                n_runtime["buffer_mem_bytes"] = int(c_runtime.get("buffer_mem_bytes", 0))
        negative = evaluate(control, mutated, args.image_root)
        negative["mutation"] = "remove_compression_format_flag_and_replace_candidate_renderer_buffer_with_control"
        negative["expected_fail_closed"] = negative["state"].startswith("FAIL_") and not negative["checks"].get("candidate_compressed_surface_format", True) and not negative["checks"].get("renderer_buffer_memory_lower_all_34_retained_frames", True)
        args.negative_control_output.parent.mkdir(parents=True, exist_ok=True)
        args.negative_control_output.write_text(json.dumps(negative, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if not negative["expected_fail_closed"]:
            return 3

    return 0 if result["state"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())

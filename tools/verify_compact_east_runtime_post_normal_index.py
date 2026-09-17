#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import statistics
from pathlib import Path
from typing import Any

EXPECTED_PARENT = "cef2ad78d8e36a55ada5dad07329f1a7125d48de"
EXPECTED_NEUTRAL = "420135f6effbadb1b344675948b9ddc471dcb83177702888f0b32327c5121c18"
CONTROL_MODE = "reuse_arraymesh_candidate"
CANDIDATE_MODE = "reuse_arraymesh_post_normal_index_candidate"
CONTEXTS = ("ground_oblique", "crown_oblique")
PHASES = 17
SOURCE_VERTICES = 390
SOURCE_TRIANGLES = 570
TRIANGLE_CORNERS = SOURCE_TRIANGLES * 3


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def frame_path(root: Path, mode: str, context: str, phase: int) -> Path:
    return root / f"compact-east-runtime-{mode}-{context}-{phase:02d}.png"


def runtime_shape(row: dict[str, Any]) -> tuple[int, int, int]:
    return (
        int(row.get("draw_calls_in_frame", -1)),
        int(row.get("objects_in_frame", -1)),
        int(row.get("primitives_in_frame", -1)),
    )


def pct_reduction(before: float, after: float) -> float | None:
    if before <= 0:
        return None
    return (before - after) / before * 100.0


def evaluate(control: dict[str, Any], candidate: dict[str, Any], image_root: Path) -> dict[str, Any]:
    total = int(control.get("total_update_count", -1))
    candidate_total = int(candidate.get("total_update_count", -2))
    control_construct = control.get("resource_constructions", {})
    candidate_construct = candidate.get("resource_constructions", {})

    checks: dict[str, bool] = {
        "control_observer_pass": control.get("state") == "PASS_COMPACT_EAST_RUNTIME_RESOURCE_OBSERVATION",
        "candidate_observer_pass": candidate.get("state") == "PASS_COMPACT_EAST_RUNTIME_RESOURCE_OBSERVATION",
        "mode_identity": control.get("mode") == CONTROL_MODE and candidate.get("mode") == CANDIDATE_MODE,
        "exact_parent_vfx_head": control.get("parent_vfx_head") == EXPECTED_PARENT and candidate.get("parent_vfx_head") == EXPECTED_PARENT,
        "exact_neutral_mesh_identity": control.get("migrated_neutral_mesh_digest") == EXPECTED_NEUTRAL and candidate.get("migrated_neutral_mesh_digest") == EXPECTED_NEUTRAL,
        "same_update_count": total == candidate_total and total > PHASES,
        "both_reuse_one_resource_set": all(int(control_construct.get(k, -1)) == 1 and int(candidate_construct.get(k, -1)) == 1 for k in ("mesh_instances", "array_meshes", "materials")),
        "retained_phase_count": len(control.get("retained_samples", [])) == PHASES and len(candidate.get("retained_samples", [])) == PHASES,
    }

    control_samples = control.get("retained_samples", [])
    candidate_samples = candidate.get("retained_samples", [])
    topology_ok = True
    control_unindexed_ok = True
    candidate_indexed_ok = True
    storage_reduced_every_phase = True
    candidate_ids: dict[str, set[int]] = {"node": set(), "mesh": set(), "material": set()}
    counters_equal = True
    texture_equal = True
    frames_equal = True
    phase_rows: list[dict[str, Any]] = []
    frame_rows: list[dict[str, Any]] = []
    renderer_buffer_deltas: list[int] = []

    if len(control_samples) == PHASES and len(candidate_samples) == PHASES:
        for phase in range(PHASES):
            c = control_samples[phase]
            n = candidate_samples[phase]
            if int(c.get("phase_index", -1)) != phase or int(n.get("phase_index", -1)) != phase:
                topology_ok = False
            for sample in (c, n):
                update = sample.get("update", {})
                if int(update.get("source_vertex_count", -1)) != SOURCE_VERTICES or int(update.get("source_triangle_count", -1)) != SOURCE_TRIANGLES or int(update.get("surface_count", -1)) != 1:
                    topology_ok = False

            cu = c.get("update", {})
            nu = n.get("update", {})
            cs = cu.get("mesh_storage", {})
            ns = nu.get("mesh_storage", {})
            c_vertices = int(cs.get("stored_vertex_count", -1))
            c_indices = int(cs.get("stored_index_count", -1))
            n_vertices = int(ns.get("stored_vertex_count", -1))
            n_indices = int(ns.get("stored_index_count", -1))
            c_bytes = int(cs.get("position_normal_index_model_bytes", -1))
            n_bytes = int(ns.get("position_normal_index_model_bytes", -1))

            if bool(cs.get("index_after_normals", True)) or c_vertices != TRIANGLE_CORNERS or c_indices != 0 or int(cs.get("pre_index_vertex_count", -1)) != TRIANGLE_CORNERS:
                control_unindexed_ok = False
            if not bool(ns.get("index_after_normals", False)) or n_indices != TRIANGLE_CORNERS or int(ns.get("pre_index_vertex_count", -1)) != TRIANGLE_CORNERS or int(ns.get("post_index_vertex_count", -1)) != n_vertices:
                candidate_indexed_ok = False
            if not (0 < n_vertices < c_vertices and 0 < n_bytes < c_bytes):
                storage_reduced_every_phase = False

            candidate_ids["node"].add(int(nu.get("node_instance_id", -1)))
            candidate_ids["mesh"].add(int(nu.get("mesh_instance_id", -1)))
            candidate_ids["material"].add(int(nu.get("material_instance_id", -1)))

            phase_rows.append({
                "phase": phase,
                "control_stored_vertices": c_vertices,
                "candidate_stored_vertices": n_vertices,
                "candidate_indices": n_indices,
                "control_position_normal_index_model_bytes": c_bytes,
                "candidate_position_normal_index_model_bytes": n_bytes,
                "model_bytes_reduction": c_bytes - n_bytes,
                "model_bytes_reduction_percent": pct_reduction(c_bytes, n_bytes),
            })

            for context in CONTEXTS:
                c_runtime = c.get("contexts", {}).get(context, {}).get("runtime", {})
                n_runtime = n.get("contexts", {}).get(context, {}).get("runtime", {})
                if runtime_shape(c_runtime) != runtime_shape(n_runtime):
                    counters_equal = False
                if int(c_runtime.get("texture_mem_bytes", -1)) != int(n_runtime.get("texture_mem_bytes", -2)):
                    texture_equal = False
                renderer_buffer_deltas.append(int(n_runtime.get("buffer_mem_bytes", 0)) - int(c_runtime.get("buffer_mem_bytes", 0)))

                cp = frame_path(image_root, CONTROL_MODE, context, phase)
                np = frame_path(image_root, CANDIDATE_MODE, context, phase)
                if not cp.is_file() or not np.is_file():
                    frames_equal = False
                    frame_rows.append({"phase": phase, "context": context, "present": False})
                    continue
                ch = sha256(cp)
                nh = sha256(np)
                same = ch == nh
                frames_equal = frames_equal and same
                frame_rows.append({
                    "phase": phase,
                    "context": context,
                    "present": True,
                    "control_sha256": ch,
                    "candidate_sha256": nh,
                    "byte_identical": same,
                    "renderer_buffer_delta_bytes": int(n_runtime.get("buffer_mem_bytes", 0)) - int(c_runtime.get("buffer_mem_bytes", 0)),
                })

    checks["exact_source_topology_all_retained_phases"] = topology_ok
    checks["control_is_exact_unindexed_post_normal_stream"] = control_unindexed_ok
    checks["candidate_indexes_exact_post_normal_stream"] = candidate_indexed_ok
    checks["stored_vertex_and_model_bytes_reduced_every_phase"] = storage_reduced_every_phase
    checks["candidate_resource_ids_stable_all_retained_phases"] = all(len(v) == 1 and -1 not in v for v in candidate_ids.values())
    checks["draw_object_primitive_counters_equal_all_retained_frames"] = counters_equal
    checks["texture_memory_equal_all_retained_frames"] = texture_equal
    checks["all_34_matched_frames_byte_identical"] = frames_equal and len(frame_rows) == PHASES * len(CONTEXTS)

    control_timing = control.get("stress_submission_timing", {})
    candidate_timing = candidate.get("stress_submission_timing", {})
    c_med = int(control_timing.get("median_usec", 0))
    n_med = int(candidate_timing.get("median_usec", 0))
    timing_tradeoff = "INDEXING_FASTER_ON_PROOF_HOST" if n_med < c_med else "INDEXING_SAME_MEDIAN_ON_PROOF_HOST" if n_med == c_med else "INDEXING_COSTS_CPU_ON_PROOF_HOST"

    reductions = [int(row["model_bytes_reduction"]) for row in phase_rows if int(row["model_bytes_reduction"]) > 0]
    reduction_pcts = [float(row["model_bytes_reduction_percent"]) for row in phase_rows if row["model_bytes_reduction_percent"] is not None]
    vertex_counts = [int(row["candidate_stored_vertices"]) for row in phase_rows]

    state = "PASS_COMPACT_EAST_POST_NORMAL_INDEX_REDUCES_REUSED_SURFACE_STORAGE__HOLD_CPU_AND_FINAL_SHADING_REVIEW" if all(checks.values()) else "FAIL_COMPACT_EAST_POST_NORMAL_INDEX_REDUCES_REUSED_SURFACE_STORAGE"
    result = {
        "schema": "axm.nature-compact-east-runtime-post-normal-index-comparison/v0.1",
        "state": state,
        "checks": checks,
        "parent_vfx_head": EXPECTED_PARENT,
        "migrated_neutral_mesh_digest": EXPECTED_NEUTRAL,
        "measurements": {
            "total_updates_per_mode": total,
            "source_vertices": SOURCE_VERTICES,
            "source_triangles": SOURCE_TRIANGLES,
            "triangle_corner_stream_vertices": TRIANGLE_CORNERS,
            "candidate_stored_vertex_count_min": min(vertex_counts) if vertex_counts else None,
            "candidate_stored_vertex_count_max": max(vertex_counts) if vertex_counts else None,
            "model_bytes_saved_min": min(reductions) if reductions else None,
            "model_bytes_saved_max": max(reductions) if reductions else None,
            "model_bytes_reduction_percent_min": min(reduction_pcts) if reduction_pcts else None,
            "model_bytes_reduction_percent_max": max(reduction_pcts) if reduction_pcts else None,
            "renderer_buffer_delta_bytes_min": min(renderer_buffer_deltas) if renderer_buffer_deltas else None,
            "renderer_buffer_delta_bytes_median": statistics.median(renderer_buffer_deltas) if renderer_buffer_deltas else None,
            "renderer_buffer_delta_bytes_max": max(renderer_buffer_deltas) if renderer_buffer_deltas else None,
            "renderer_buffer_delta_bytes_all_negative": bool(renderer_buffer_deltas) and all(v < 0 for v in renderer_buffer_deltas),
            "control_retained_timing": control.get("retained_submission_timing", {}),
            "candidate_retained_timing": candidate.get("retained_submission_timing", {}),
            "control_stress_timing": control_timing,
            "candidate_stress_timing": candidate_timing,
            "stress_median_delta_usec": n_med - c_med,
            "stress_total_delta_usec": int(candidate_timing.get("total_usec", 0)) - int(control_timing.get("total_usec", 0)),
            "proof_host_cpu_tradeoff": timing_tradeoff,
        },
        "phase_storage": phase_rows,
        "frame_pairs": frame_rows,
        "visual_tradeoff_for_art_director": "NONE_OBSERVED_34_MATCHED_UNSHADED_FRAMES_BYTE_IDENTICAL__FINAL_SHADED_NORMAL_REVIEW_STILL_REQUIRED" if frames_equal else "REVIEW_REQUIRED_FRAME_BYTES_DIFFER",
        "decision_note": "Indexing is applied only after the historical triangle-corner stream has generated normals. This PASS requires lower stored vertex/model bytes for every retained phase and exact proof-frame identity. Proof-host CPU timing is reported as a tradeoff, not hidden or converted into a universal win.",
        "truth_boundary": {
            "exact_compact_east_vfx_phases": True,
            "post_normal_indexing_only": True,
            "stable_resource_lifecycle_preserved": True,
            "proof_host_renderer_counters_observed": True,
            "proof_host_cpu_submission_timing_observed": True,
            "final_shaded_normal_equivalence": False,
            "target_device_cpu_gpu_fps_vram": False,
            "continuous_wall_clock_playback": False,
            "map_current_world_receiving": False,
            "final_materials_leaf_sidedness": False,
            "art_direction_acceptance": False,
            "canon_or_production_readiness": False,
        },
    }
    return result


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
        for sample in mutated.get("retained_samples", []):
            storage = sample.get("update", {}).get("mesh_storage", {})
            storage["stored_vertex_count"] = TRIANGLE_CORNERS
            storage["stored_index_count"] = 0
            storage["position_normal_index_model_bytes"] = TRIANGLE_CORNERS * 24
            storage["index_after_normals"] = False
            storage["post_index_vertex_count"] = TRIANGLE_CORNERS
        negative = evaluate(control, mutated, args.image_root)
        negative["mutation"] = "candidate_post_normal_index_storage_replaced_with_unindexed_triangle_corner_stream"
        negative["expected_fail_closed"] = negative["state"].startswith("FAIL_") and not negative["checks"].get("candidate_indexes_exact_post_normal_stream", True)
        args.negative_control_output.parent.mkdir(parents=True, exist_ok=True)
        args.negative_control_output.write_text(json.dumps(negative, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if not negative["expected_fail_closed"]:
            return 3

    return 0 if result["state"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())

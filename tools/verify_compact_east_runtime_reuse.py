#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

EXPECTED_PARENT = "cef2ad78d8e36a55ada5dad07329f1a7125d48de"
EXPECTED_NEUTRAL = "420135f6effbadb1b344675948b9ddc471dcb83177702888f0b32327c5121c18"
CONTROL_MODE = "rebuild_resources_control"
CANDIDATE_MODE = "reuse_arraymesh_candidate"
CONTEXTS = ("ground_oblique", "crown_oblique")
PHASES = 17


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
        int(row["draw_calls_in_frame"]),
        int(row["objects_in_frame"]),
        int(row["primitives_in_frame"]),
    )


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
        "control_rebuilds_each_update": all(int(control_construct.get(k, -1)) == total for k in ("mesh_instances", "array_meshes", "materials")),
        "candidate_reuses_one_resource_set": all(int(candidate_construct.get(k, -1)) == 1 for k in ("mesh_instances", "array_meshes", "materials")),
        "retained_phase_count": len(control.get("retained_samples", [])) == PHASES and len(candidate.get("retained_samples", [])) == PHASES,
    }

    control_samples = control.get("retained_samples", [])
    candidate_samples = candidate.get("retained_samples", [])
    topology_ok = True
    candidate_ids: dict[str, set[int]] = {"node": set(), "mesh": set(), "material": set()}
    counters_equal = True
    frames_equal = True
    frame_rows: list[dict[str, Any]] = []

    if len(control_samples) == PHASES and len(candidate_samples) == PHASES:
        for phase in range(PHASES):
            c = control_samples[phase]
            n = candidate_samples[phase]
            if int(c.get("phase_index", -1)) != phase or int(n.get("phase_index", -1)) != phase:
                topology_ok = False
            for sample in (c, n):
                update = sample.get("update", {})
                if int(update.get("source_vertex_count", -1)) != 390 or int(update.get("source_triangle_count", -1)) != 570 or int(update.get("surface_count", -1)) != 1:
                    topology_ok = False
            n_update = n.get("update", {})
            candidate_ids["node"].add(int(n_update.get("node_instance_id", -1)))
            candidate_ids["mesh"].add(int(n_update.get("mesh_instance_id", -1)))
            candidate_ids["material"].add(int(n_update.get("material_instance_id", -1)))
            for context in CONTEXTS:
                c_runtime = c.get("contexts", {}).get(context, {}).get("runtime", {})
                n_runtime = n.get("contexts", {}).get(context, {}).get("runtime", {})
                if runtime_shape(c_runtime) != runtime_shape(n_runtime):
                    counters_equal = False
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
                frame_rows.append({"phase": phase, "context": context, "present": True, "control_sha256": ch, "candidate_sha256": nh, "byte_identical": same})

    checks["exact_source_topology_all_retained_phases"] = topology_ok
    checks["candidate_resource_ids_stable_all_retained_phases"] = all(len(v) == 1 and -1 not in v for v in candidate_ids.values())
    checks["draw_object_primitive_counters_equal_all_retained_frames"] = counters_equal
    checks["all_34_matched_frames_byte_identical"] = frames_equal and len(frame_rows) == PHASES * len(CONTEXTS)

    reduction = None
    if total > 0 and all(int(candidate_construct.get(k, -1)) == 1 for k in ("mesh_instances", "array_meshes", "materials")):
        reduction = (total - 1) / total * 100.0

    control_timing = control.get("stress_submission_timing", {})
    candidate_timing = candidate.get("stress_submission_timing", {})
    timing = {
        "control_retained": control.get("retained_submission_timing", {}),
        "candidate_retained": candidate.get("retained_submission_timing", {}),
        "control_stress": control_timing,
        "candidate_stress": candidate_timing,
        "stress_total_delta_usec": int(candidate_timing.get("total_usec", 0)) - int(control_timing.get("total_usec", 0)),
        "stress_median_delta_usec": int(candidate_timing.get("median_usec", 0)) - int(control_timing.get("median_usec", 0)),
    }

    result = {
        "schema": "axm.nature-compact-east-runtime-resource-reuse-comparison/v0.1",
        "state": "PASS_COMPACT_EAST_ARRAYMESH_RESOURCE_REUSE" if all(checks.values()) else "FAIL_COMPACT_EAST_ARRAYMESH_RESOURCE_REUSE",
        "checks": checks,
        "parent_vfx_head": EXPECTED_PARENT,
        "migrated_neutral_mesh_digest": EXPECTED_NEUTRAL,
        "measurements": {
            "total_updates_per_mode": total,
            "control_resource_constructions": control_construct,
            "candidate_resource_constructions": candidate_construct,
            "resource_construction_reduction_percent": reduction,
            "matched_render_pairs": len(frame_rows),
            "timing": timing,
            "control_pre_to_post_stress_buffer_delta_bytes": int(control.get("post_stress_runtime", {}).get("buffer_mem_bytes", 0)) - int(control.get("pre_stress_runtime", {}).get("buffer_mem_bytes", 0)),
            "candidate_pre_to_post_stress_buffer_delta_bytes": int(candidate.get("post_stress_runtime", {}).get("buffer_mem_bytes", 0)) - int(candidate.get("pre_stress_runtime", {}).get("buffer_mem_bytes", 0)),
            "control_pre_to_post_stress_texture_delta_bytes": int(control.get("post_stress_runtime", {}).get("texture_mem_bytes", 0)) - int(control.get("pre_stress_runtime", {}).get("texture_mem_bytes", 0)),
            "candidate_pre_to_post_stress_texture_delta_bytes": int(candidate.get("post_stress_runtime", {}).get("texture_mem_bytes", 0)) - int(candidate.get("pre_stress_runtime", {}).get("texture_mem_bytes", 0)),
        },
        "frame_pairs": frame_rows,
        "visual_tradeoff_for_art_director": "NONE_OBSERVED_34_MATCHED_FRAMES_BYTE_IDENTICAL" if frames_equal else "REVIEW_REQUIRED_FRAME_BYTES_DIFFER",
        "truth_boundary": {
            "exact_compact_east_vfx_phases": True,
            "proof_host_resource_lifecycle_reuse": True,
            "proof_host_cpu_submission_timing_observed": True,
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
        mutated["resource_constructions"] = copy.deepcopy(control.get("resource_constructions", {}))
        negative = evaluate(control, mutated, args.image_root)
        negative["mutation"] = "candidate_resource_constructions_replaced_with_control_counts"
        negative["expected_fail_closed"] = negative["state"] == "FAIL_COMPACT_EAST_ARRAYMESH_RESOURCE_REUSE" and not negative["checks"].get("candidate_reuses_one_resource_set", True)
        args.negative_control_output.parent.mkdir(parents=True, exist_ok=True)
        args.negative_control_output.write_text(json.dumps(negative, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if not negative["expected_fail_closed"]:
            return 3

    return 0 if result["state"] == "PASS_COMPACT_EAST_ARRAYMESH_RESOURCE_REUSE" else 2


if __name__ == "__main__":
    raise SystemExit(main())

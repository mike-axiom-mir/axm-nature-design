#!/usr/bin/env python3
"""Build a bounded Runtime shader-driver oracle for the exact east/rear receiver.

The first pass deliberately tested whether each authorized rigid child group was one
VERTEX_ID range. Real evidence falsified that assumption. This successor preserves the
failure and instead emits the exact small set of contiguous VERTEX_ID runs belonging
to each already-authorized Rigging group. No vertex identity, topology, motion
semantics, or owner authority is changed.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any, Iterable

from axm_nature_design.organic_form import load_source
from axm_nature_design import rear_tree_runtime_dynamic_prefix as runtime
from axm_nature_design import rear_tree_rigging_shared_driver_polarity as shared_driver

RUNTIME_OWNER_HEAD = "6d89e1fc0f8dc5e2ef6c57fc99c1dc6b1727780f"
EXPECTED_WINDOW = (110, 370)
EXPECTED_GROUP_SIZE = 52
EXPECTED_GROUP_COUNT = 5
EXPECTED_TOTAL_VERTICES = 390
EXPECTED_MOVING_VERTICES = 260
MAX_SHADER_VERTEX_ID_RUNS = 64


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def git_head(root: Path) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()


def contiguous_runs(indices: Iterable[int]) -> list[list[int]]:
    ordered = sorted(set(int(index) for index in indices))
    if not ordered:
        return []
    runs: list[list[int]] = []
    start = previous = ordered[0]
    for index in ordered[1:]:
        if index == previous + 1:
            previous = index
            continue
        runs.append([start, previous + 1])
        start = previous = index
    runs.append([start, previous + 1])
    return runs


def f(value: float) -> str:
    text = format(float(value), ".17g")
    if "." not in text and "e" not in text.lower():
        text += ".0"
    return text


def vec3(values: list[float]) -> str:
    return "vec3(%s, %s, %s)" % tuple(f(float(v)) for v in values)


def shader_source(groups: list[dict[str, Any]]) -> str:
    ranges: list[dict[str, Any]] = []
    for group in groups:
        for start, end in group["vertex_id_runs"]:
            ranges.append({**group, "run_start": start, "run_end": end})
    ranges.sort(key=lambda row: int(row["run_start"]))
    lines = [
        "shader_type spatial;",
        "uniform float driver_deg = 0.0;",
        "uniform float apply_driver = 1.0;",
        "vec3 source_from_target(vec3 p) { return vec3(p.x, p.z, p.y); }",
        "vec3 target_from_source(vec3 p) { return vec3(p.x, p.z, p.y); }",
        "vec3 rotate_about_axis(vec3 p, vec3 pivot, vec3 axis, float a) {",
        "    vec3 v = p - pivot;",
        "    float c = cos(a);",
        "    float s = sin(a);",
        "    return pivot + v * c + cross(axis, v) * s + axis * dot(axis, v) * (1.0 - c);",
        "}",
        "void vertex() {",
        "    if (apply_driver >= 0.5) {",
        "        vec3 p = source_from_target(VERTEX);",
        "        vec3 pivot = vec3(0.0);",
        "        vec3 axis = vec3(0.0, 1.0, 0.0);",
        "        float sign_multiplier = 0.0;",
    ]
    for index, row in enumerate(ranges):
        prefix = "if" if index == 0 else "else if"
        lines.extend([
            f"        {prefix} (VERTEX_ID >= {row['run_start']} && VERTEX_ID < {row['run_end']}) {{",
            f"            pivot = {vec3(row['pivot_source_m'])};",
            f"            axis = normalize({vec3(row['axis_source'])});",
            f"            sign_multiplier = {f(row['command_sign_multiplier'])};",
            "        }",
        ])
    lines.extend([
        "        if (sign_multiplier != 0.0) {",
        "            float a = driver_deg * sign_multiplier * PI / 180.0;",
        "            VERTEX = target_from_source(rotate_about_axis(p, pivot, axis, a));",
        "        }",
        "    }",
        "}",
        "void fragment() {",
        "    ALBEDO = vec3(0.42, 0.61, 0.31);",
        "    ROUGHNESS = 0.82;",
        "}",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--mutate-first-range-start", type=int)
    parser.add_argument("--claim-target-device-performance", action="store_true")
    args = parser.parse_args()
    if args.claim_target_device_performance:
        raise ValueError("shader-driver proof-host evidence cannot claim target-device performance")

    runtime_root = args.runtime_root.resolve()
    if git_head(runtime_root) != RUNTIME_OWNER_HEAD:
        raise ValueError("exact pass-52 Runtime owner head drift")
    source = load_source(runtime_root / "examples/east_rear_tree_neutral_001.json")
    prepared = runtime._prepare(source)
    start, end = EXPECTED_WINDOW
    if tuple(prepared["dynamic_union"]) != tuple(range(start, end)):
        raise ValueError("exact Runtime moving union no longer equals [110,370)")

    groups: list[dict[str, Any]] = []
    for branch_id in runtime.BRANCH_IDS:
        selected = sorted(int(v) for v in prepared["dynamic_by_branch"][branch_id])
        if len(selected) != EXPECTED_GROUP_SIZE:
            raise ValueError(f"branch group size drift: {branch_id}")
        runs = contiguous_runs(selected)
        if sum(run_end - run_start for run_start, run_end in runs) != EXPECTED_GROUP_SIZE:
            raise ValueError(f"branch run coverage drift: {branch_id}")
        probe = prepared["probes"][branch_id]
        groups.append({
            "branch_id": branch_id,
            "vertex_count": len(selected),
            "vertex_id_runs": runs,
            "run_count": len(runs),
            "pivot_source_m": [float(v) for v in probe["joint_pivot_m"]],
            "axis_source": [float(v) for v in probe["source_derived_axis"]],
            "command_sign_multiplier": float(shared_driver.COMMAND_SIGN_MULTIPLIER[branch_id]),
        })

    if len(groups) != EXPECTED_GROUP_COUNT:
        raise ValueError("shader group count drift")
    flat_runs = [
        {"branch_id": group["branch_id"], "start": run[0], "end": run[1]}
        for group in groups for run in group["vertex_id_runs"]
    ]
    flat_runs.sort(key=lambda row: row["start"])
    if args.mutate_first_range_start is not None:
        flat_runs[0]["start"] = int(args.mutate_first_range_start)
    total_runs = len(flat_runs)
    if total_runs > MAX_SHADER_VERTEX_ID_RUNS:
        raise ValueError(f"fragmented VERTEX_ID lookup exceeds bounded shader-run budget: {total_runs}")
    cursor = start
    for run in flat_runs:
        if int(run["start"]) != cursor or int(run["end"]) <= int(run["start"]):
            raise ValueError("shader VERTEX_ID runs no longer tile exact moving window")
        cursor = int(run["end"])
    if cursor != end:
        raise ValueError("shader VERTEX_ID runs do not terminate at exact moving-window end")

    # Apply the optional negative mutation to groups too, only after proving the real layout.
    if args.mutate_first_range_start is not None:
        for group in groups:
            for run in group["vertex_id_runs"]:
                if run[0] == start:
                    run[0] = int(args.mutate_first_range_start)
                    break
            else:
                continue
            break
        raise ValueError("mutated VERTEX_ID run intentionally rejected")

    semantic_driver_bytes = 4
    pass53_partial_bytes = EXPECTED_MOVING_VERTICES * 3 * 4
    pass53_mutable_position_bytes = EXPECTED_TOTAL_VERTICES * 3 * 4
    imported_compressed_position_bytes = EXPECTED_TOTAL_VERTICES * 8
    oracle = {
        "schema": "axm.nature-runtime-east-rear-vertex-id-shader-driver/v0.2",
        "result": "PASS_FRAGMENTED_VERTEX_ID_RUNS_TILE_EXACT_DYNAMIC_WINDOW",
        "runtime_owner_head": RUNTIME_OWNER_HEAD,
        "vertex_count": EXPECTED_TOTAL_VERTICES,
        "moving_window": [start, end],
        "moving_vertices": EXPECTED_MOVING_VERTICES,
        "groups": groups,
        "vertex_id_run_count": total_runs,
        "maximum_authorized_vertex_id_runs": MAX_SHADER_VERTEX_ID_RUNS,
        "flat_vertex_id_runs": flat_runs,
        "representative_driver_deg": [float(v) for v in runtime.DRIVER_VALUES_DEG],
        "representation_budget": {
            "pass53_partial_float32_position_packet_bytes": pass53_partial_bytes,
            "pass53_mutable_float32_position_storage_bytes": pass53_mutable_position_bytes,
            "godot_imported_compressed_position_storage_bytes": imported_compressed_position_bytes,
            "shader_semantic_driver_payload_bytes": semantic_driver_bytes,
            "semantic_payload_bytes_saved_vs_pass53_partial": pass53_partial_bytes - semantic_driver_bytes,
            "semantic_payload_reduction_percent_vs_pass53_partial": (pass53_partial_bytes - semantic_driver_bytes) / pass53_partial_bytes * 100.0,
            "compressed_position_storage_bytes_saved_vs_pass53_mutable": pass53_mutable_position_bytes - imported_compressed_position_bytes,
            "compressed_position_storage_reduction_percent_vs_pass53_mutable": (pass53_mutable_position_bytes - imported_compressed_position_bytes) / pass53_mutable_position_bytes * 100.0,
        },
        "visual_tradeoff": {
            "additional_vertex_shader_control_flow": True,
            "vertex_id_range_tests_per_vertex_upper_bound": total_runs,
            "normal_or_tangent_deformation_unchanged_from_pass53_proof_material": True,
            "art_direction_review_state": "HOLD_FIXED_VIEW_A_B_AND_FINAL_LOOKDEV",
        },
        "truth_boundary": {
            "first_single_range_per_branch_hypothesis_was_falsified_and_preserved": True,
            "semantic_driver_payload_is_not_measured_gpu_command_transport": True,
            "vertex_shader_range_tests_are_not_free_gpu_work": True,
            "target_device_cpu_gpu_fps_vram_thermal_battery_proven": False,
            "animation_timing_or_wind_semantics_adopted": False,
            "normal_or_tangent_deformation_correctness_proven": False,
            "art_or_visual_qa_acceptance_proven": False,
            "generic_vegetation_policy_proven": False,
            "canon_or_production_readiness_proven": False,
        },
    }
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "runtime-shader-driver-oracle.json").write_text(canonical(oracle) + "\n", encoding="utf-8")
    (out / "runtime-shader-driver.gdshader").write_text(shader_source(groups), encoding="utf-8")
    print(json.dumps(oracle, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

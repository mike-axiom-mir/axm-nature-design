#!/usr/bin/env python3
"""Build a Runtime-only shader-driver oracle for the exact east/rear receiver.

The proof asks one narrow question: can the five already-authorized rigid child groups
be addressed by VERTEX_ID ranges so Runtime can retain Godot's compressed imported
position buffer and drive the representation with one scalar instead of uploading a
260-vertex position packet? It does not author motion timing, widen Rigging authority,
or claim target-device performance.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from axm_nature_design.organic_form import load_source
from axm_nature_design import rear_tree_runtime_dynamic_prefix as runtime
from axm_nature_design import rear_tree_rigging_shared_driver_polarity as shared_driver

RUNTIME_OWNER_HEAD = "6d89e1fc0f8dc5e2ef6c57fc99c1dc6b1727780f"
EXPECTED_WINDOW = (110, 370)
EXPECTED_GROUP_SIZE = 52
EXPECTED_GROUP_COUNT = 5
EXPECTED_TOTAL_VERTICES = 390
EXPECTED_MOVING_VERTICES = 260


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def git_head(root: Path) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()


def f(value: float) -> str:
    text = format(float(value), ".17g")
    if "." not in text and "e" not in text.lower():
        text += ".0"
    return text


def vec3(values: list[float]) -> str:
    return "vec3(%s, %s, %s)" % tuple(f(float(v)) for v in values)


def shader_source(groups: list[dict[str, Any]]) -> str:
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
        "    if (apply_driver < 0.5) { return; }",
        "    vec3 p = source_from_target(VERTEX);",
        "    vec3 pivot = vec3(0.0);",
        "    vec3 axis = vec3(0.0, 1.0, 0.0);",
        "    float sign_multiplier = 0.0;",
    ]
    for index, group in enumerate(groups):
        prefix = "if" if index == 0 else "else if"
        lines.extend(
            [
                f"    {prefix} (VERTEX_ID >= {group['start_vertex']} && VERTEX_ID < {group['end_vertex_exclusive']}) {{",
                f"        pivot = {vec3(group['pivot_source_m'])};",
                f"        axis = normalize({vec3(group['axis_source'])});",
                f"        sign_multiplier = {f(group['command_sign_multiplier'])};",
                "    }",
            ]
        )
    lines.extend(
        [
            "    if (sign_multiplier != 0.0) {",
            "        float a = driver_deg * sign_multiplier * PI / 180.0;",
            "        VERTEX = target_from_source(rotate_about_axis(p, pivot, axis, a));",
            "    }",
            "}",
            "void fragment() {",
            "    ALBEDO = vec3(0.42, 0.61, 0.31);",
            "    ROUGHNESS = 0.82;",
            "}",
            "",
        ]
    )
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
        group_start = selected[0]
        group_end = selected[-1] + 1
        if selected != list(range(group_start, group_end)):
            raise ValueError(f"branch vertices are not one exact VERTEX_ID range: {branch_id}")
        probe = prepared["probes"][branch_id]
        groups.append(
            {
                "branch_id": branch_id,
                "start_vertex": group_start,
                "end_vertex_exclusive": group_end,
                "vertex_count": len(selected),
                "pivot_source_m": [float(v) for v in probe["joint_pivot_m"]],
                "axis_source": [float(v) for v in probe["source_derived_axis"]],
                "command_sign_multiplier": float(shared_driver.COMMAND_SIGN_MULTIPLIER[branch_id]),
            }
        )

    groups.sort(key=lambda row: row["start_vertex"])
    if len(groups) != EXPECTED_GROUP_COUNT:
        raise ValueError("shader group count drift")
    if args.mutate_first_range_start is not None:
        groups[0]["start_vertex"] = int(args.mutate_first_range_start)

    cursor = start
    for group in groups:
        if int(group["start_vertex"]) != cursor:
            raise ValueError("shader VERTEX_ID ranges no longer tile the exact moving window")
        if int(group["end_vertex_exclusive"]) - int(group["start_vertex"]) != EXPECTED_GROUP_SIZE:
            raise ValueError("shader VERTEX_ID range width drift")
        cursor = int(group["end_vertex_exclusive"])
    if cursor != end:
        raise ValueError("shader VERTEX_ID ranges do not terminate at exact moving-window end")

    semantic_driver_bytes = 4
    pass53_partial_bytes = EXPECTED_MOVING_VERTICES * 3 * 4
    pass53_mutable_position_bytes = EXPECTED_TOTAL_VERTICES * 3 * 4
    imported_compressed_position_bytes = EXPECTED_TOTAL_VERTICES * 8
    oracle = {
        "schema": "axm.nature-runtime-east-rear-vertex-id-shader-driver/v0.1",
        "result": "PASS_VERTEX_ID_GROUPS_TILE_EXACT_DYNAMIC_WINDOW",
        "runtime_owner_head": RUNTIME_OWNER_HEAD,
        "vertex_count": EXPECTED_TOTAL_VERTICES,
        "moving_window": [start, end],
        "moving_vertices": EXPECTED_MOVING_VERTICES,
        "groups": groups,
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
        "truth_boundary": {
            "semantic_driver_payload_is_not_measured_gpu_command_transport": True,
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

#!/usr/bin/env python3
"""Bind the exact Runtime shader-driver carrier to Technical Art proof normals.

This stays Nature-local.  Runtime owns the fragmented VERTEX_ID carrier and motion
semantics; Technical Art owns only the renderer-facing attribute handoff.  Universal
Creation remains a generic surface/GLB publisher and receives no Nature policy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from axm_nature_design.uc_dynamic_window_receiver import build_dynamic_window_surface
from axm_uc.procedural_3d import publish_glb, verify_glb

RUNTIME_OWNER_HEAD = "6d89e1fc0f8dc5e2ef6c57fc99c1dc6b1727780f"
RUNTIME_CANDIDATE_HEAD = "520068e1167f369b24e749831954f9bda1cd7aec"
UC_HEAD = "520584c87071837e8dc1ff9a39da140f5efa229d"
UC_PROCEDURAL3D_BLOB = "cdb654d4d0f68a4ca7539d98a985d7a70cf7ee36"
RUNTIME_RESULT = "PASS_EAST_REAR_EXISTING_DYNAMIC_WINDOW_POSITION_PACKET_REDUCTION"
RUNTIME_SHADER_RESULT = "PASS_FRAGMENTED_VERTEX_ID_RUNS_TILE_EXACT_DYNAMIC_WINDOW"
RESULT = "PASS_NATURE_RUNTIME_SHADER_NORMAL_TRANSPORT_PACKET_READY"
SCHEMA = "axm.nature-runtime-shader-normal-transport/v0.1"
EXPECTED_VERTICES = 390
EXPECTED_TRIANGLES = 570


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def git_head(root: Path) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()


def git_blob(root: Path, path: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", f"HEAD:{path}"], text=True).strip()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_donor(runtime_root: Path) -> dict[str, Any]:
    code = r'''
import json
from pathlib import Path
from axm_nature_design.organic_form import build_mesh, load_source
from axm_nature_design import rear_tree_runtime_dynamic_prefix as runtime
root=Path('.').resolve()
source=load_source(root/'examples/east_rear_tree_neutral_001.json')
mesh=build_mesh(source)
receipt=runtime.evaluate(source)
print(json.dumps({'source':source,'mesh':mesh,'runtime_receipt':receipt},sort_keys=True,separators=(',',':')))
'''
    env = dict(os.environ)
    env["PYTHONPATH"] = str(runtime_root / "src")
    return json.loads(subprocess.check_output([sys.executable, "-c", code], cwd=runtime_root, env=env, text=True))


def diagnostic_shader(runtime_shader: str, *, rotate_normal: bool) -> str:
    if runtime_shader.count("VERTEX = target_from_source(rotate_about_axis(p, pivot, axis, a));") != 1:
        raise ValueError("exact Runtime shader vertex transform shape drift")
    if "NORMAL =" in runtime_shader:
        raise ValueError("Runtime shader already writes NORMAL; Technical Art rebind must be re-evaluated")
    if "void fragment()" not in runtime_shader or not runtime_shader.startswith("shader_type spatial;"):
        raise ValueError("exact Runtime shader grammar drift")

    shader = runtime_shader.replace(
        "shader_type spatial;",
        "shader_type spatial;\nrender_mode unshaded, cull_disabled;",
        1,
    )
    shader = shader[: shader.index("void fragment()")]
    shader += (
        "void fragment() {\n"
        "    vec3 debug_normal = normalize(NORMAL);\n"
        "    ALBEDO = debug_normal * 0.5 + vec3(0.5);\n"
        "}\n"
    )
    if not rotate_normal:
        return shader

    vertex_marker = "void vertex() {"
    rotate_direction = (
        "vec3 rotate_direction(vec3 v, vec3 axis, float a) {\n"
        "    float c = cos(a);\n"
        "    float s = sin(a);\n"
        "    return v * c + cross(axis, v) * s + axis * dot(axis, v) * (1.0 - c);\n"
        "}\n"
    )
    shader = shader.replace(vertex_marker, rotate_direction + vertex_marker, 1)
    old = "            VERTEX = target_from_source(rotate_about_axis(p, pivot, axis, a));"
    new = (
        "            VERTEX = target_from_source(rotate_about_axis(p, pivot, axis, a));\n"
        "            vec3 source_normal = source_from_target(NORMAL);\n"
        "            NORMAL = normalize(target_from_source(rotate_direction(source_normal, axis, a)));"
    )
    shader = shader.replace(old, new, 1)
    if shader.count("NORMAL = normalize(target_from_source(rotate_direction") != 1:
        raise ValueError("normal transport patch did not bind exactly once")
    return shader


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-owner-root", type=Path, required=True)
    parser.add_argument("--runtime-candidate-root", type=Path, required=True)
    parser.add_argument("--uc-root", type=Path, required=True)
    parser.add_argument("--runtime-oracle", type=Path, required=True)
    parser.add_argument("--runtime-shader", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--claim-generic-nature-normal-policy", action="store_true")
    args = parser.parse_args()

    if args.claim_generic_nature_normal_policy:
        raise ValueError("bounded Technical Art proof normals cannot become generic Nature/UC policy")

    runtime_owner = args.runtime_owner_root.resolve()
    runtime_candidate = args.runtime_candidate_root.resolve()
    uc_root = args.uc_root.resolve()
    if git_head(runtime_owner) != RUNTIME_OWNER_HEAD:
        raise ValueError("exact Runtime owner head drift")
    if git_head(runtime_candidate) != RUNTIME_CANDIDATE_HEAD:
        raise ValueError("exact Runtime shader candidate head drift")
    if git_head(uc_root) != UC_HEAD:
        raise ValueError("exact fresh UC head drift")
    if git_blob(uc_root, "src/axm_uc/procedural_3d.py") != UC_PROCEDURAL3D_BLOB:
        raise ValueError("fresh UC procedural_3d executable blob drift")

    runtime_oracle = json.loads(args.runtime_oracle.read_text(encoding="utf-8"))
    if runtime_oracle.get("result") != RUNTIME_SHADER_RESULT:
        raise ValueError("Runtime shader-driver oracle is not green")
    if runtime_oracle.get("runtime_owner_head") != RUNTIME_OWNER_HEAD:
        raise ValueError("Runtime shader oracle owner lineage drift")
    if int(runtime_oracle.get("vertex_count", -1)) != EXPECTED_VERTICES:
        raise ValueError("Runtime shader oracle vertex-count drift")
    if int(runtime_oracle.get("vertex_id_run_count", -1)) != 10:
        raise ValueError("Runtime fragmented-run count drift")

    donor = runtime_donor(runtime_owner)
    receipt = donor["runtime_receipt"]
    if receipt.get("result") != RUNTIME_RESULT:
        raise ValueError("exact Runtime owner prerequisite is not green")
    receiver = build_dynamic_window_surface(donor["source"], donor["mesh"], receipt)
    if receiver["source_vertex_count"] != EXPECTED_VERTICES or receiver["source_triangle_count"] != EXPECTED_TRIANGLES:
        raise ValueError("Technical Art receiver geometry identity drift")

    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    glb_path = out / "nature-east-rear-runtime-normal-receiver.glb"
    publication = publish_glb(glb_path, receiver["surface"], replace=True)
    verification = verify_glb(glb_path.read_bytes(), expected_spec_digest=publication["specification_sha256"])
    primitive = publication["specification"]["primitives"][0]
    if len(primitive["positions"]) != EXPECTED_VERTICES or len(primitive["normals"]) != EXPECTED_VERTICES:
        raise ValueError("fresh UC did not retain one proof normal per receiver vertex")
    if verification.get("triangles") != EXPECTED_TRIANGLES:
        raise ValueError("fresh UC receiver triangle count drift")

    runtime_shader_text = args.runtime_shader.read_text(encoding="utf-8")
    negative = diagnostic_shader(runtime_shader_text, rotate_normal=False)
    corrected = diagnostic_shader(runtime_shader_text, rotate_normal=True)
    (out / "runtime-position-only-normal-debug.gdshader").write_text(negative, encoding="utf-8")
    (out / "technical-art-position-plus-normal-debug.gdshader").write_text(corrected, encoding="utf-8")

    packet = {
        "schema": SCHEMA,
        "result": RESULT,
        "heads": {
            "runtime_owner": RUNTIME_OWNER_HEAD,
            "runtime_shader_candidate": RUNTIME_CANDIDATE_HEAD,
            "uc": UC_HEAD,
        },
        "uc": {
            "procedural_3d_blob": UC_PROCEDURAL3D_BLOB,
            "glb_sha256": sha256_file(glb_path),
            "vertices": EXPECTED_VERTICES,
            "triangles": EXPECTED_TRIANGLES,
            "normal_count": EXPECTED_VERTICES,
            "product_code_modified_by_technical_art": False,
        },
        "runtime_carrier": {
            "vertex_id_run_count": int(runtime_oracle["vertex_id_run_count"]),
            "moving_window": runtime_oracle["moving_window"],
            "group_count": len(runtime_oracle["groups"]),
            "position_only_shader_sha256": hashlib.sha256(runtime_shader_text.encode("utf-8")).hexdigest(),
        },
        "technical_art_adapter": {
            "coordinate_map": "source_[x,y,z]_to_target_[x,z,y]",
            "position_transform_preserved_from_runtime_shader": True,
            "normal_direction_rotated_by_same_source_axis_angle": True,
            "normal_rotation_uses_no_pivot_translation": True,
            "diagnostic_material_scope": "TECHNICAL_ART_NORMAL_DIRECTION_DEBUG_ONLY_NOT_NATURE_LOOKDEV",
        },
        "truth_boundary": {
            "proof_normals_are_source_or_materials_authority": False,
            "tangent_transport_proven": False,
            "physical_wind_or_animation_timing_proven": False,
            "target_device_performance_proven": False,
            "art_or_visual_qa_acceptance_proven": False,
            "generic_uc_normal_deformation_policy_created": False,
            "canon_or_production_readiness_proven": False,
        },
    }
    (out / "technical-art-normal-transport-packet.json").write_bytes(canonical(packet) + b"\n")
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

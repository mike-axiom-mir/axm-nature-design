#!/usr/bin/env python3
"""Build the bounded Nature Runtime dynamic-window -> current UC target receiver packet."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from axm_nature_design.uc_dynamic_window_receiver import (
    EXPECTED_DYNAMIC_WINDOW,
    EXPECTED_TOTAL_VERTICES,
    build_dynamic_window_surface,
)
from axm_uc.procedural_3d import publish_glb, verify_glb

RUNTIME_HEAD = "6d89e1fc0f8dc5e2ef6c57fc99c1dc6b1727780f"
VFX_HEAD = "ba1c12dd527f1ecc6a0eb4bc0b4322f15ccad475"
RIGGING_HEAD = "754797a815266a643c6b08f1606eb76ba95dd8c6"
UC_HEAD = "5c5d2cfdc3aa4e9462fd4d5ec5bc7874f12674a4"
SOURCE_DIGEST = "178cd8cfb1a859bff411f60e13154109528062cf0ad2384b343d406cc0cc9d61"
MESH_DIGEST = "aa9d450a78fef722672ea9af0f9aca98b4c1a0ca3705661784f5f61f3e9b6a31"
RUNTIME_RESULT = "PASS_EAST_REAR_EXISTING_DYNAMIC_WINDOW_POSITION_PACKET_REDUCTION"
RESULT = "PASS_NATURE_EAST_REAR_RUNTIME_WINDOW_CURRENT_UC_TARGET_RECEIVER_READY"
SCHEMA = "axm.nature-east-rear-runtime-window-current-uc-target/v0.1"
DRIVERS = (-5.0, -2.5, 0.0, 2.5, 5.0)


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head(root: Path) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()


def git_blob(root: Path, path: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", f"HEAD:{path}"], text=True).strip()


def source_to_uc(row: list[float]) -> list[float]:
    return [round(float(row[0]), 9), round(float(row[2]), 9), round(float(row[1]), 9)]


def donor_payload(runtime_root: Path) -> dict[str, Any]:
    code = r'''
import json
from pathlib import Path
from axm_nature_design.organic_form import build_mesh, digest, load_source
from axm_nature_design import rear_tree_runtime_dynamic_prefix as runtime
root=Path('.').resolve()
source=load_source(root/'examples/east_rear_tree_neutral_001.json')
mesh=build_mesh(source)
receipt=runtime.evaluate(source)
prepared=runtime._prepare(source)
poses=[]
for driver in runtime.DRIVER_VALUES_DEG:
    control=runtime._control_pose(prepared,float(driver))
    candidate_dynamic=runtime._candidate_window_pose(prepared,float(driver))
    candidate=runtime._expand_candidate(prepared,candidate_dynamic)
    poses.append({
        'shared_driver_deg':float(driver),
        'control_source_positions_m':control,
        'candidate_dynamic_source_positions_m':candidate_dynamic,
        'expanded_candidate_source_positions_m':candidate,
    })
print(json.dumps({
    'source':source,
    'mesh':mesh,
    'source_digest':digest(source),
    'mesh_digest':digest(mesh),
    'runtime_receipt':receipt,
    'poses':poses,
},sort_keys=True,separators=(',',':')))
'''
    env = dict(os.environ)
    env["PYTHONPATH"] = str(runtime_root / "src")
    raw = subprocess.check_output([sys.executable, "-c", code], cwd=runtime_root, env=env, text=True)
    value = json.loads(raw)
    if value["source_digest"] != SOURCE_DIGEST or value["mesh_digest"] != MESH_DIGEST:
        raise ValueError("exact Nature source/mesh identity drift")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--uc-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--claim-target-device-performance", action="store_true")
    parser.add_argument("--mutate-window-end", type=int)
    args = parser.parse_args()

    if args.claim_target_device_performance:
        raise ValueError("Technical Art target-host transport cannot claim target-device performance")

    runtime_root = args.runtime_root.resolve()
    uc_root = args.uc_root.resolve()
    if git_head(runtime_root) != RUNTIME_HEAD:
        raise ValueError("exact Runtime owner head drift")
    if git_head(uc_root) != UC_HEAD:
        raise ValueError("exact current UC head drift")

    donor = donor_payload(runtime_root)
    runtime_receipt = donor["runtime_receipt"]
    if runtime_receipt.get("result") != RUNTIME_RESULT:
        raise ValueError("exact Runtime prerequisite is not green")
    lineage = runtime_receipt.get("lineage") or {}
    if lineage.get("vfx_owner_head") != VFX_HEAD or lineage.get("rigging_owner_head") != RIGGING_HEAD:
        raise ValueError("Runtime VFX/Rigging lineage drift")
    if runtime_receipt.get("representation", {}).get("dynamic_window_original_indices") != [110, 370]:
        raise ValueError("Runtime dynamic window drift")

    if args.mutate_window_end is not None:
        runtime_receipt = json.loads(json.dumps(runtime_receipt))
        runtime_receipt["representation"]["dynamic_window_original_indices"][1] = int(args.mutate_window_end)

    receiver = build_dynamic_window_surface(donor["source"], donor["mesh"], runtime_receipt)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    surface_path = out / "nature-east-rear-dynamic-window.surface.json"
    glb_path = out / "nature-east-rear-dynamic-window.glb"
    oracle_path = out / "nature-east-rear-dynamic-window-target-oracle.json"
    receipt_path = out / "nature-east-rear-dynamic-window-uc-target-receipt.json"

    surface_path.write_bytes(canonical(receiver["surface"]) + b"\n")
    publication = publish_glb(glb_path, receiver["surface"], replace=True)
    verification = verify_glb(glb_path.read_bytes(), expected_spec_digest=publication["specification_sha256"])
    published_vertices = sum(len(primitive["positions"]) for primitive in publication["specification"]["primitives"])
    if published_vertices != EXPECTED_TOTAL_VERTICES:
        raise ValueError(f"current UC published surface vertex identity drift: {published_vertices}")
    if verification.get("triangles") != receiver["source_triangle_count"]:
        raise ValueError("current UC GLB triangle count drift")

    poses = []
    start, end = EXPECTED_DYNAMIC_WINDOW
    for row in donor["poses"]:
        driver = float(row["shared_driver_deg"])
        if driver not in DRIVERS:
            raise ValueError("Runtime driver witness drift")
        control = [source_to_uc(point) for point in row["control_source_positions_m"]]
        candidate_dynamic = [source_to_uc(point) for point in row["candidate_dynamic_source_positions_m"]]
        expanded = [source_to_uc(point) for point in row["expanded_candidate_source_positions_m"]]
        if len(control) != EXPECTED_TOTAL_VERTICES or len(expanded) != EXPECTED_TOTAL_VERTICES:
            raise ValueError("Runtime pose vertex count drift")
        if len(candidate_dynamic) != end - start:
            raise ValueError("Runtime dynamic-window packet length drift")
        if control != expanded:
            raise ValueError("Runtime full/candidate source positions are no longer exact")
        if candidate_dynamic != control[start:end]:
            raise ValueError("Runtime dynamic packet no longer equals exact contiguous control window")
        poses.append({
            "shared_driver_deg": driver,
            "control_target_positions_m": control,
            "candidate_dynamic_target_positions_m": candidate_dynamic,
        })

    oracle = {
        "schema": "axm.nature-east-rear-dynamic-window-godot-oracle/v0.1",
        "receiver_glb_sha256": sha256_file(glb_path),
        "vertex_count": EXPECTED_TOTAL_VERTICES,
        "triangle_count": receiver["source_triangle_count"],
        "dynamic_window_vertices": list(EXPECTED_DYNAMIC_WINDOW),
        "position_stride_bytes": receiver["target_vertex_stride_bytes"],
        "dynamic_byte_offset": receiver["target_dynamic_byte_offset"],
        "dynamic_byte_length": receiver["target_dynamic_byte_length"],
        "full_position_bytes": receiver["target_full_position_bytes"],
        "poses": poses,
        "target_material_scope": "GODOT_RECEIVER_PROOF_SHADED_CULL_DISABLED_NOT_NATURE_LOOKDEV",
    }
    oracle_path.write_bytes(canonical(oracle) + b"\n")

    uc_blob = git_blob(uc_root, "src/axm_uc/procedural_3d.py")
    receipt = {
        "schema": SCHEMA,
        "result": RESULT,
        "heads": {"runtime": RUNTIME_HEAD, "vfx": VFX_HEAD, "rigging": RIGGING_HEAD, "uc": UC_HEAD},
        "source_digest": SOURCE_DIGEST,
        "mesh_digest": MESH_DIGEST,
        "runtime_result": RUNTIME_RESULT,
        "receiver": {
            key: receiver[key]
            for key in (
                "source_vertex_count", "source_triangle_count", "source_vertex_to_uc_vertex_identity",
                "dynamic_window_target_vertex_indices", "target_vertex_stride_bytes",
                "target_dynamic_byte_offset", "target_dynamic_byte_length", "target_full_position_bytes",
                "coordinate_handedness_determinant", "triangle_winding_reversed_exactly_once",
                "normal_scope", "material_scope", "foliage_sidedness_scope"
            )
        },
        "uc": {
            "procedural_3d_blob": uc_blob,
            "glb_sha256": sha256_file(glb_path),
            "surface_sha256": sha256_file(surface_path),
            "vertices": published_vertices,
            "triangles": verification.get("triangles"),
            "product_code_modified_by_technical_art": False,
            "nature_or_runtime_domain_semantics_moved_to_uc": False,
        },
        "pose_count": len(poses),
        "truth_boundary": {
            "real_target_host_partial_vertex_update_proven": False,
            "target_host_shaded_control_candidate_identity_proven": False,
            "target_device_performance_proven": False,
            "physical_wind_or_animation_timing_proven": False,
            "art_or_visual_qa_acceptance_proven": False,
            "canon_or_production_readiness_proven": False,
        },
    }
    receipt_path.write_bytes(canonical(receipt) + b"\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

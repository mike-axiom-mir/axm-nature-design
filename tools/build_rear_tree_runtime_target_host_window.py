#!/usr/bin/env python3
"""Assemble Runtime target-host evidence from exact pass-52 + Technical Art receiver.

This is intentionally Runtime-owned evidence assembly. Technical Art owns the receiver
adapter/transport contract; Universal Creation owns the generic GLB publisher. Runtime
only binds their exact identities and emits the full-vs-window position-update oracle.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
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

RUNTIME_OWNER_HEAD = "6d89e1fc0f8dc5e2ef6c57fc99c1dc6b1727780f"
TECHNICAL_ART_HEAD = "b96f794325f825188b6fd9a920e3fb575e43e467"
TECHNICAL_ART_RECEIVER_BLOB = "a18d568d45324488f52f2a05159e927450ae2b84"
VFX_HEAD = "ba1c12dd527f1ecc6a0eb4bc0b4322f15ccad475"
RIGGING_HEAD = "754797a815266a643c6b08f1606eb76ba95dd8c6"
UC_HEAD = "5c5d2cfdc3aa4e9462fd4d5ec5bc7874f12674a4"
SOURCE_DIGEST = "178cd8cfb1a859bff411f60e13154109528062cf0ad2384b343d406cc0cc9d61"
MESH_DIGEST = "aa9d450a78fef722672ea9af0f9aca98b4c1a0ca3705661784f5f61f3e9b6a31"
RUNTIME_RESULT = "PASS_EAST_REAR_EXISTING_DYNAMIC_WINDOW_POSITION_PACKET_REDUCTION"
RESULT = "PASS_RUNTIME_CONSUMED_TECHNICAL_ART_CURRENT_UC_DYNAMIC_WINDOW_RECEIVER_READY"
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
    # Exact Technical Art receiver transport pinned by its target contract.
    return [round(float(row[0]), 9), round(float(row[2]), 9), round(float(row[1]), 9)]


def glb_json(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if len(data) < 20 or data[:4] != b"glTF":
        raise ValueError("published target receiver is not GLB")
    _, version, total_length = struct.unpack_from("<III", data, 0)
    if version != 2 or total_length != len(data):
        raise ValueError("published target receiver GLB header drift")
    json_length, json_type = struct.unpack_from("<II", data, 12)
    if json_type != 0x4E4F534A:
        raise ValueError("published target receiver GLB JSON chunk missing")
    raw = data[20 : 20 + json_length].rstrip(b" \t\r\n\x00")
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("published target receiver GLB JSON is not an object")
    return value


def glb_position_accessor_count(path: Path) -> int:
    value = glb_json(path)
    meshes = value.get("meshes") or []
    if len(meshes) != 1:
        raise ValueError("Runtime target proof requires exactly one GLB mesh")
    primitives = meshes[0].get("primitives") or []
    if len(primitives) != 1:
        raise ValueError("Runtime target proof requires exactly one GLB primitive")
    position_accessor = (primitives[0].get("attributes") or {}).get("POSITION")
    if not isinstance(position_accessor, int):
        raise ValueError("Runtime target GLB POSITION accessor missing")
    accessors = value.get("accessors") or []
    if position_accessor < 0 or position_accessor >= len(accessors):
        raise ValueError("Runtime target GLB POSITION accessor index drift")
    return int(accessors[position_accessor].get("count", -1))


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
    dynamic=runtime._candidate_window_pose(prepared,float(driver))
    expanded=runtime._expand_candidate(prepared,dynamic)
    poses.append({
        'shared_driver_deg':float(driver),
        'control_source_positions_m':control,
        'candidate_dynamic_source_positions_m':dynamic,
        'expanded_candidate_source_positions_m':expanded,
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
        raise ValueError("exact pass-52 source/mesh identity drift")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--technical-art-root", type=Path, required=True)
    parser.add_argument("--uc-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--mutate-window-end", type=int)
    parser.add_argument("--claim-target-device-performance", action="store_true")
    args = parser.parse_args()

    if args.claim_target_device_performance:
        raise ValueError("proof-host Runtime target evidence cannot claim target-device performance")

    runtime_root = args.runtime_root.resolve()
    technical_art_root = args.technical_art_root.resolve()
    uc_root = args.uc_root.resolve()
    if git_head(runtime_root) != RUNTIME_OWNER_HEAD:
        raise ValueError("exact pass-52 Runtime owner head drift")
    if git_head(technical_art_root) != TECHNICAL_ART_HEAD:
        raise ValueError("exact Technical Art receiver head drift")
    if git_blob(technical_art_root, "src/axm_nature_design/uc_dynamic_window_receiver.py") != TECHNICAL_ART_RECEIVER_BLOB:
        raise ValueError("exact Technical Art receiver implementation blob drift")
    if git_head(uc_root) != UC_HEAD:
        raise ValueError("exact Universal Creation donor head drift")

    donor = donor_payload(runtime_root)
    runtime_receipt = donor["runtime_receipt"]
    if runtime_receipt.get("result") != RUNTIME_RESULT:
        raise ValueError("exact pass-52 Runtime prerequisite is not green")
    lineage = runtime_receipt.get("lineage") or {}
    if lineage.get("vfx_owner_head") != VFX_HEAD or lineage.get("rigging_owner_head") != RIGGING_HEAD:
        raise ValueError("pass-52 VFX/Rigging lineage drift")
    if runtime_receipt.get("representation", {}).get("dynamic_window_original_indices") != [110, 370]:
        raise ValueError("pass-52 dynamic-window identity drift")

    receiver_receipt = json.loads(json.dumps(runtime_receipt))
    if args.mutate_window_end is not None:
        receiver_receipt["representation"]["dynamic_window_original_indices"][1] = int(args.mutate_window_end)
    receiver = build_dynamic_window_surface(donor["source"], donor["mesh"], receiver_receipt)

    start, end = EXPECTED_DYNAMIC_WINDOW
    if receiver["dynamic_window_target_vertex_indices"] != [start, end]:
        raise ValueError("Technical Art receiver target-window identity drift")
    if receiver["target_vertex_stride_bytes"] != 12:
        raise ValueError("Technical Art receiver target position stride drift")
    if receiver["target_dynamic_byte_offset"] != 1320 or receiver["target_dynamic_byte_length"] != 3120:
        raise ValueError("Technical Art receiver target byte-window drift")
    positions = receiver["surface"]["primitives"][0]["positions"]
    if len(positions) != EXPECTED_TOTAL_VERTICES:
        raise ValueError("Technical Art receiver surface vertex count drift")

    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    surface_path = out / "nature-east-rear-dynamic-window.surface.json"
    glb_path = out / "nature-east-rear-dynamic-window.glb"
    oracle_path = out / "nature-east-rear-dynamic-window-target-oracle.json"
    receipt_path = out / "runtime-target-preflight-receipt.json"

    surface_path.write_bytes(canonical(receiver["surface"]) + b"\n")
    publication = publish_glb(glb_path, receiver["surface"], replace=True)
    verification = verify_glb(glb_path.read_bytes(), expected_spec_digest=publication["specification_sha256"])
    if verification.get("passed") is not True or verification.get("triangles") != receiver["source_triangle_count"]:
        raise ValueError(f"current UC GLB verification failed: {verification}")
    if glb_position_accessor_count(glb_path) != EXPECTED_TOTAL_VERTICES:
        raise ValueError("published current-UC GLB POSITION accessor count drift")

    poses = []
    max_source_delta = 0.0
    for row in donor["poses"]:
        driver = float(row["shared_driver_deg"])
        if driver not in DRIVERS:
            raise ValueError("pass-52 driver witness drift")
        control_source = row["control_source_positions_m"]
        expanded_source = row["expanded_candidate_source_positions_m"]
        dynamic_source = row["candidate_dynamic_source_positions_m"]
        if len(control_source) != EXPECTED_TOTAL_VERTICES or len(expanded_source) != EXPECTED_TOTAL_VERTICES:
            raise ValueError("pass-52 pose vertex count drift")
        if len(dynamic_source) != end - start:
            raise ValueError("pass-52 dynamic-window packet length drift")
        for left, right in zip(control_source, expanded_source):
            for component in range(3):
                max_source_delta = max(max_source_delta, abs(float(left[component]) - float(right[component])))
        if dynamic_source != control_source[start:end]:
            raise ValueError("pass-52 dynamic packet no longer equals exact control window")
        poses.append({
            "shared_driver_deg": driver,
            "control_target_positions_m": [source_to_uc(point) for point in control_source],
            "candidate_dynamic_target_positions_m": [source_to_uc(point) for point in dynamic_source],
        })
    if max_source_delta != 0.0:
        raise ValueError("pass-52 full/candidate source reconstruction is no longer exact")

    oracle = {
        "schema": "axm.nature-east-rear-runtime-window-godot-oracle/v0.1",
        "receiver_glb_sha256": sha256_file(glb_path),
        "vertex_count": EXPECTED_TOTAL_VERTICES,
        "triangle_count": receiver["source_triangle_count"],
        "dynamic_window_vertices": [start, end],
        "position_stride_bytes": receiver["target_vertex_stride_bytes"],
        "dynamic_byte_offset": receiver["target_dynamic_byte_offset"],
        "dynamic_byte_length": receiver["target_dynamic_byte_length"],
        "full_position_bytes": receiver["target_full_position_bytes"],
        "poses": poses,
        "target_material_scope": "TECHNICAL_ART_PROOF_MATERIAL_NOT_NATURE_LOOKDEV",
    }
    oracle_path.write_bytes(canonical(oracle) + b"\n")

    receipt = {
        "schema": "axm.nature-runtime-target-host-window-preflight/v0.1",
        "result": RESULT,
        "heads": {
            "runtime_owner": RUNTIME_OWNER_HEAD,
            "technical_art": TECHNICAL_ART_HEAD,
            "vfx": VFX_HEAD,
            "rigging": RIGGING_HEAD,
            "uc": UC_HEAD,
        },
        "technical_art_receiver_blob": TECHNICAL_ART_RECEIVER_BLOB,
        "source_digest": SOURCE_DIGEST,
        "mesh_digest": MESH_DIGEST,
        "receiver": {
            "source_vertex_count": receiver["source_vertex_count"],
            "source_triangle_count": receiver["source_triangle_count"],
            "source_vertex_to_uc_vertex_identity": receiver["source_vertex_to_uc_vertex_identity"],
            "dynamic_window_target_vertex_indices": receiver["dynamic_window_target_vertex_indices"],
            "target_vertex_stride_bytes": receiver["target_vertex_stride_bytes"],
            "target_dynamic_byte_offset": receiver["target_dynamic_byte_offset"],
            "target_dynamic_byte_length": receiver["target_dynamic_byte_length"],
            "target_full_position_bytes": receiver["target_full_position_bytes"],
            "coordinate_handedness_determinant": receiver["coordinate_handedness_determinant"],
            "triangle_winding_reversed_exactly_once": receiver["triangle_winding_reversed_exactly_once"],
        },
        "uc": {
            "glb_sha256": sha256_file(glb_path),
            "surface_sha256": sha256_file(surface_path),
            "glb_position_accessor_count": glb_position_accessor_count(glb_path),
            "triangles": verification.get("triangles"),
            "product_code_modified_by_runtime": False,
            "nature_or_runtime_domain_semantics_moved_to_uc": False,
        },
        "pose_count": len(poses),
        "maximum_pass52_full_candidate_source_component_delta_m": max_source_delta,
        "truth_boundary": {
            "real_target_host_partial_vertex_update_proven": False,
            "target_host_shaded_control_candidate_identity_proven": False,
            "normal_or_tangent_deformation_correctness_proven": False,
            "target_device_performance_proven": False,
            "art_or_visual_qa_acceptance_proven": False,
            "canon_or_production_readiness_proven": False,
        },
    }
    receipt_path.write_bytes(canonical(receipt) + b"\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build exact indexed-surface Rigging -> generic UC target receiver evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from axm_nature_design.uc_indexed_bridge_receiver import (
    EXPECTED_MOVING_VERTICES,
    EXPECTED_TRIANGLES,
    EXPECTED_VERTICES,
    build_indexed_bridge_surface,
)
from axm_uc.procedural_3d import publish_glb, verify_glb

GEOMETRY_HEAD = "8ab552710df21567cfd601af99181918e2cfadb3"
GEOMETRY_MODULE_BLOB = "af43e49bf6f14c050a3930d3258bc4ee50c0a9f3"
GEOMETRY_CONTRACT_BLOB = "081e2a610a6938cb12c501b7f8a907e590a7214c"
RIGGING_HEAD = "5c0c06be96996bad464846071b2a55622be14620"
RIGGING_MODULE_BLOB = "538f03e4b1bd84fdde2711b866f890aa396188a3"
RIGGING_CONTRACT_BLOB = "097933b32ecb2cf3f4e0e99d8863036341024646"
SOURCE_BLOB = "fb12b759e1abfd0455bf46fd39a0eba27095796b"
UC_HEAD = "f7434152295bc9a3d57c59767481b2ef042ec675"
UC_PROCEDURAL_BLOB = "cdb654d4d0f68a4ca7539d98a985d7a70cf7ee36"
GEOMETRY_RESULT = "PASS_NORTH_LOW_EXACT_INDEXED_TRUNK_SURFACE_REBIND__HOLD_INDEXED_CUT_CONNECTED_JUNCTION"
RIGGING_RESULT = "PASS_NORTH_LOW_INDEXED_SURFACE_RECEIVER_RIGGING_REBIND_AND_CONTINUOUS_PAIRED_SPAN_NONCOLLAPSE_MINUS5_TO_PLUS5__HOLD_INDEXED_CUT_CONNECTED_JUNCTION_TRIANGLE_FOLDOVER_COLLISION"
RESULT = "PASS_NATURE_NORTH_LOW_INDEXED_BRIDGE_CURRENT_UC_TARGET_RECEIVER_READY"
SCHEMA = "axm.nature-north-low-indexed-bridge-current-uc-target/v0.1"
REPRESENTATIVE_ANGLES = (-5.0, -2.5, 0.0, 2.5, 5.0)


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head(root: Path) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()


def git_blob(root: Path, path: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", f"HEAD:{path}"], text=True).strip()


def run_payload(root: Path, code: str) -> dict[str, Any]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(root / "src")
    raw = subprocess.check_output([sys.executable, "-c", code], cwd=root, env=env, text=True)
    return json.loads(raw)


def geometry_payload(root: Path) -> dict[str, Any]:
    code = r'''
import json
from pathlib import Path
from axm_nature_design.organic_form import load_source
from axm_nature_design import rear_tree_geometry_north_low_indexed_surface_rebind as geometry
root=Path('.').resolve()
source=load_source(root/'examples/east_rear_tree_neutral_001.json')
report=geometry.evaluate(source)
candidate=geometry.build_candidate(source)
print(json.dumps({'source':source,'report':report,'bridge_only':candidate['bridge_only']},sort_keys=True,separators=(',',':')))
'''
    return run_payload(root, code)


def rigging_payload(root: Path) -> dict[str, Any]:
    code = r'''
import json
from pathlib import Path
from axm_nature_design.organic_form import load_source
from axm_nature_design import rear_tree_geometry_north_low_indexed_surface_rebind as geometry
from axm_nature_design import rear_tree_rigging_north_low_indexed_surface_rebind as rigging
root=Path('.').resolve()
source=load_source(root/'examples/east_rear_tree_neutral_001.json')
g_report=geometry.evaluate(source)
g_candidate=geometry.build_candidate(source)
r=rigging.evaluate(source,g_report,g_candidate)
bridge=g_candidate['bridge_only']
neutral=[[float(v) for v in p] for p in bridge['vertices']]
branch=neutral[:8]
fixed=neutral[8:]
socket=r['socket_identity']
pivot=[float(v) for v in socket['pivot_m']]
axis=[float(v) for v in socket['source_derived_axis']]
h=rigging.analytic_span.endpoint_gate.historical
poses=[]
for angle in rigging.REPRESENTATIVE_ANGLES_DEG:
    moving=[h._rotate_about_axis(p,pivot,axis,float(angle)) for p in branch]
    full=moving+[list(p) for p in fixed]
    spans=[h._distance(moving[i],fixed[i]) for i in range(8)]
    poses.append({'child_angle_deg':float(angle),'source_positions_m':full,'minimum_paired_span_m':min(spans)})
print(json.dumps({'source':source,'geometry_report':g_report,'bridge_only':bridge,'rigging_receipt':r,'poses':poses},sort_keys=True,separators=(',',':')))
'''
    return run_payload(root, code)


def source_to_uc(row: list[float]) -> list[float]:
    return [round(float(row[0]), 9), round(float(row[2]), 9), round(float(row[1]), 9)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--geometry-root", type=Path, required=True)
    parser.add_argument("--rigging-root", type=Path, required=True)
    parser.add_argument("--uc-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--mutate-moving-vertex-end", type=int)
    parser.add_argument("--claim-connected-topology", action="store_true")
    parser.add_argument("--claim-animation-transfer", action="store_true")
    args = parser.parse_args()

    if args.claim_connected_topology:
        raise ValueError("Technical Art endpoint transport cannot claim Geometry connected topology")
    if args.claim_animation_transfer:
        raise ValueError("Technical Art endpoint transport cannot claim Animation adoption/playback")

    geometry_root = args.geometry_root.resolve()
    rigging_root = args.rigging_root.resolve()
    uc_root = args.uc_root.resolve()
    if git_head(geometry_root) != GEOMETRY_HEAD:
        raise ValueError("exact Geometry donor head drift")
    if git_head(rigging_root) != RIGGING_HEAD:
        raise ValueError("exact Rigging owner head drift")
    if git_head(uc_root) != UC_HEAD:
        raise ValueError("exact current UC head drift")

    expected_blobs = {
        "geometry_module": (geometry_root, "src/axm_nature_design/rear_tree_geometry_north_low_indexed_surface_rebind.py", GEOMETRY_MODULE_BLOB),
        "geometry_contract": (geometry_root, "contracts/east-rear-north-low-indexed-surface-rebind-geometry-008.json", GEOMETRY_CONTRACT_BLOB),
        "geometry_source": (geometry_root, "examples/east_rear_tree_neutral_001.json", SOURCE_BLOB),
        "rigging_module": (rigging_root, "src/axm_nature_design/rear_tree_rigging_north_low_indexed_surface_rebind.py", RIGGING_MODULE_BLOB),
        "rigging_contract": (rigging_root, "contracts/east-rear-north-low-indexed-surface-rebind-rigging-011.json", RIGGING_CONTRACT_BLOB),
        "rigging_source": (rigging_root, "examples/east_rear_tree_neutral_001.json", SOURCE_BLOB),
        "uc_procedural_3d": (uc_root, "src/axm_uc/procedural_3d.py", UC_PROCEDURAL_BLOB),
    }
    observed_blobs = {}
    for key, (root, path, expected) in expected_blobs.items():
        observed = git_blob(root, path)
        observed_blobs[key] = observed
        if observed != expected:
            raise ValueError(f"exact blob drift for {key}: {observed} != {expected}")

    geometry = geometry_payload(geometry_root)
    rigging = rigging_payload(rigging_root)
    if geometry["report"].get("result") != GEOMETRY_RESULT:
        raise ValueError("exact Geometry donor no longer passes")
    if rigging["rigging_receipt"].get("result") != RIGGING_RESULT:
        raise ValueError("exact Rigging owner no longer passes")
    if canonical(geometry["bridge_only"]) != canonical(rigging["bridge_only"]):
        raise ValueError("Rigging-embedded indexed bridge differs from exact Geometry donor")
    if canonical(geometry["report"]) != canonical(rigging["geometry_report"]):
        raise ValueError("Rigging-embedded Geometry report differs from exact donor execution")
    if canonical(geometry["source"]) != canonical(rigging["source"]):
        raise ValueError("Geometry/Rigging source bytes parse to different source state")

    moving_end = EXPECTED_MOVING_VERTICES if args.mutate_moving_vertex_end is None else int(args.mutate_moving_vertex_end)
    receiver = build_indexed_bridge_surface(
        geometry["source"], geometry["report"], {"bridge_only": geometry["bridge_only"]}, rigging["rigging_receipt"],
        moving_vertex_end=moving_end,
    )

    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    surface_path = out / "nature-north-low-indexed-bridge.surface.json"
    glb_path = out / "nature-north-low-indexed-bridge.glb"
    oracle_path = out / "nature-north-low-indexed-bridge-target-oracle.json"
    receipt_path = out / "nature-north-low-indexed-bridge-uc-target-receipt.json"

    surface_path.write_bytes(canonical(receiver["surface"]) + b"\n")
    publication = publish_glb(glb_path, receiver["surface"], replace=True)
    verification = verify_glb(glb_path.read_bytes(), expected_spec_digest=publication["specification_sha256"])
    published_vertices = sum(len(row["positions"]) for row in publication["specification"]["primitives"])
    if published_vertices != EXPECTED_VERTICES or verification.get("triangles") != EXPECTED_TRIANGLES:
        raise ValueError("current UC publication changed indexed bridge cardinality")

    poses = []
    for row in rigging["poses"]:
        angle = float(row["child_angle_deg"])
        if angle not in REPRESENTATIVE_ANGLES:
            raise ValueError("Rigging representative angle drift")
        full = [source_to_uc(point) for point in row["source_positions_m"]]
        if len(full) != EXPECTED_VERTICES:
            raise ValueError("Rigging bridge pose cardinality drift")
        poses.append({
            "child_angle_deg": angle,
            "control_target_positions_m": full,
            "moving_target_positions_m": full[:EXPECTED_MOVING_VERTICES],
            "owner_minimum_paired_span_m": float(row["minimum_paired_span_m"]),
        })
    if tuple(row["child_angle_deg"] for row in poses) != REPRESENTATIVE_ANGLES:
        raise ValueError("exact Rigging representative witness family drift")

    oracle = {
        "schema": "axm.nature-north-low-indexed-bridge-godot-oracle/v0.1",
        "receiver_glb_sha256": sha256_file(glb_path),
        "vertex_count": EXPECTED_VERTICES,
        "triangle_count": EXPECTED_TRIANGLES,
        "moving_vertex_region": [0, EXPECTED_MOVING_VERTICES],
        "fixed_vertex_region": [EXPECTED_MOVING_VERTICES, EXPECTED_VERTICES],
        "position_stride_bytes": receiver["target_vertex_stride_bytes"],
        "moving_byte_offset": receiver["target_moving_byte_offset"],
        "moving_byte_length": receiver["target_moving_byte_length"],
        "full_position_bytes": receiver["target_full_position_bytes"],
        "poses": poses,
        "owner_continuous_minimum_span_m": rigging["rigging_receipt"]["continuous_paired_span_certificate"]["global_minimum_span_m"],
        "owner_continuous_minimum_angle_deg": rigging["rigging_receipt"]["continuous_paired_span_certificate"]["global_minimum_angle_deg"],
        "target_material_scope": "TECHNICAL_ART_GODOT_RECEIVER_PROOF_ONLY_NOT_NATURE_LOOKDEV",
    }
    oracle_path.write_bytes(canonical(oracle) + b"\n")

    receipt = {
        "schema": SCHEMA,
        "result": RESULT,
        "heads": {"geometry": GEOMETRY_HEAD, "rigging": RIGGING_HEAD, "uc": UC_HEAD},
        "blobs": observed_blobs,
        "geometry_result": GEOMETRY_RESULT,
        "rigging_result": RIGGING_RESULT,
        "receiver": {
            key: receiver[key]
            for key in (
                "source_vertex_count", "source_triangle_count", "moving_source_vertex_region",
                "fixed_source_vertex_region", "moving_target_vertex_region", "fixed_target_vertex_region",
                "source_vertex_to_uc_vertex_identity", "target_vertex_stride_bytes", "target_moving_byte_offset",
                "target_moving_byte_length", "target_full_position_bytes", "coordinate_handedness_determinant",
                "triangle_winding_reversed_exactly_once", "normal_scope", "material_scope"
            )
        },
        "owner": {
            "representative_angles_deg": list(REPRESENTATIVE_ANGLES),
            "representative_minimum_span_m": rigging["rigging_receipt"]["representative_pose_evidence"]["minimum_paired_bridge_span_m"],
            "continuous_minimum_span_m": rigging["rigging_receipt"]["continuous_paired_span_certificate"]["global_minimum_span_m"],
            "continuous_minimum_angle_deg": rigging["rigging_receipt"]["continuous_paired_span_certificate"]["global_minimum_angle_deg"],
            "indexed_trunk_cut_or_connected_junction": False,
        },
        "uc": {
            "procedural_3d_blob": observed_blobs["uc_procedural_3d"],
            "glb_sha256": sha256_file(glb_path),
            "surface_sha256": sha256_file(surface_path),
            "vertices": published_vertices,
            "triangles": verification.get("triangles"),
            "product_code_modified_by_technical_art": False,
            "nature_geometry_or_rigging_semantics_moved_to_uc": False,
        },
        "pose_count": len(poses),
        "truth_boundary": {
            "geometry_and_rigging_reexecuted": True,
            "exact_geometry_donor_matches_rigging_embedded_donor": True,
            "real_target_host_endpoint_region_update_proven": False,
            "animation_transfer_or_playback_proven": False,
            "indexed_cut_or_connected_topology_proven": False,
            "continuous_triangle_foldover_collision_proven": False,
            "production_skinning_proven": False,
            "runtime_controller_device_or_performance_proven": False,
            "art_or_visual_qa_acceptance_proven": False,
            "canon_or_production_readiness_proven": False,
        },
    }
    receipt_path.write_bytes(canonical(receipt) + b"\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

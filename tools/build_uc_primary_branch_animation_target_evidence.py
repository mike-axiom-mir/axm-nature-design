#!/usr/bin/env python3
"""Build and verify the bounded Nature five-branch Animation -> TA -> UC receiver handoff."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from axm_nature_design.uc_primary_branch_receiver import BRANCH_IDS, build_primary_branch_receiver
from axm_nature_design.uc_surface_bridge import adapt_mesh_for_uc
from axm_uc.procedural_3d import publish_glb, verify_glb
from axm_uc.rigid_scene_graph import rebind_rigid_scene_graph, verify_rigid_scene_graph

ANIMATION_HEAD = "b0771b3319b783103c8e4677d062c00419df7559"
RIGGING_HEAD = "898529f602893c8f6be179bd3e9b6821fc099904"
UC_HEAD = "5c772b65eeba75abd0eb7a6c9c471b2d9975019d"
SOURCE_DIGEST = "178cd8cfb1a859bff411f60e13154109528062cf0ad2384b343d406cc0cc9d61"
MESH_DIGEST = "aa9d450a78fef722672ea9af0f9aca98b4c1a0ca3705661784f5f61f3e9b6a31"
ANIMATION_RESULT = "PASS_FIVE_PRIMARY_BRANCH_ROOT_SOCKET_INDEPENDENT_DIAGNOSTIC_PULSE_FAMILY_SAMPLED_MOTION"
RIGGING_RESULT = "PASS_FIVE_PRIMARY_BRANCH_ROOT_SOCKET_RIGID_CHILD_FAMILY_GEOMETRY_RECEIVER_DIAGNOSTIC_MINUS5_TO_PLUS5"
RESULT = "PASS_NATURE_FIVE_PRIMARY_BRANCH_ANIMATION_CURRENT_UC_TARGET_RECEIVER_READY"
SCHEMA = "axm.nature-five-branch-animation-uc-target-receiver/v0.1"


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git_head(root: Path) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()


def git_blob(root: Path, path: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", f"HEAD:{path}"], text=True).strip()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def donor_source_mesh(rigging_root: Path) -> dict[str, Any]:
    code = r'''
import json
from pathlib import Path
from axm_nature_design.organic_form import build_mesh, digest, load_source
root = Path(".").resolve()
source = load_source(root / "examples/east_rear_tree_neutral_001.json")
mesh = build_mesh(source)
print(json.dumps({
    "source": source,
    "mesh": mesh,
    "source_digest": digest(source),
    "mesh_digest": digest(mesh),
}, sort_keys=True, separators=(",", ":")))
'''
    env = dict(os.environ)
    env["PYTHONPATH"] = str(rigging_root / "src")
    raw = subprocess.check_output([sys.executable, "-c", code], cwd=rigging_root, env=env, text=True)
    value = json.loads(raw)
    if value["source_digest"] != SOURCE_DIGEST or value["mesh_digest"] != MESH_DIGEST:
        raise ValueError("exact source / migrated mesh identity drift")
    return value


def rotate_about_axis(point: list[float], pivot: list[float], axis: list[float], angle_deg: float) -> list[float]:
    px, py, pz = [float(point[i]) - float(pivot[i]) for i in range(3)]
    ax, ay, az = [float(value) for value in axis]
    length = math.sqrt(ax * ax + ay * ay + az * az)
    if length <= 1e-12:
        raise ValueError("rotation axis is degenerate")
    ax, ay, az = ax / length, ay / length, az / length
    angle = math.radians(float(angle_deg))
    c, s = math.cos(angle), math.sin(angle)
    dot = ax * px + ay * py + az * pz
    cross = (ay * pz - az * py, az * px - ax * pz, ax * py - ay * px)
    relative = [
        px * c + cross[0] * s + ax * dot * (1.0 - c),
        py * c + cross[1] * s + ay * dot * (1.0 - c),
        pz * c + cross[2] * s + az * dot * (1.0 - c),
    ]
    return [relative[i] + float(pivot[i]) for i in range(3)]


def source_to_uc(point: list[float]) -> list[float]:
    return [float(point[0]), float(point[2]), float(point[1])]


def target_rotate_local(local: list[float], axis: list[float], angle_deg: float) -> list[float]:
    return rotate_about_axis(local, [0.0, 0.0, 0.0], axis, angle_deg)


def distance(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((float(a[i]) - float(b[i])) ** 2 for i in range(3)))


def build_oracle(receiver: dict[str, Any], animation: dict[str, Any], *, use_negated_target_angle: bool) -> dict[str, Any]:
    animation_by_branch = {row["branch_id"]: row for row in animation["branches"]}
    branches: dict[str, Any] = {}
    maximum_expected_transport_residual = 0.0
    maximum_wrong_sign_residual = 0.0
    for branch_id in BRANCH_IDS:
        witness = receiver["branch_witnesses"][branch_id]
        animation_row = animation_by_branch[branch_id]
        source_point = [float(value) for value in witness["source_neutral_world_m"]]
        pivot_source = [float(value) for value in witness["owner_pivot_source_m"]]
        axis_source = [float(value) for value in witness["owner_axis_source"]]
        pivot_uc = [float(value) for value in witness["target_pivot_uc_m"]]
        axis_uc = [float(value) for value in witness["target_axis_uc"]]
        local_uc = [float(value) for value in witness["local_position_uc_m"]]
        samples: list[dict[str, Any]] = []
        for sample in animation_row["samples"]:
            source_angle = float(sample["angle_deg"])
            target_angle = -source_angle if use_negated_target_angle else source_angle
            expected_source = rotate_about_axis(source_point, pivot_source, axis_source, source_angle)
            expected_uc = source_to_uc(expected_source)
            target_local = target_rotate_local(local_uc, axis_uc, target_angle)
            target_world = [pivot_uc[i] + target_local[i] for i in range(3)]
            residual = distance(expected_uc, target_world)
            maximum_expected_transport_residual = max(maximum_expected_transport_residual, residual)

            wrong_local = target_rotate_local(local_uc, axis_uc, source_angle)
            wrong_world = [pivot_uc[i] + wrong_local[i] for i in range(3)]
            wrong_residual = distance(expected_uc, wrong_world)
            maximum_wrong_sign_residual = max(maximum_wrong_sign_residual, wrong_residual)
            samples.append({
                "index": int(sample["index"]),
                "time_s": float(sample["time_s"]),
                "source_owner_angle_deg": source_angle,
                "target_receiver_angle_deg": target_angle,
                "expected_witness_world_uc_m": expected_uc,
                "analytic_target_world_uc_m": target_world,
                "analytic_transport_residual_m": residual,
            })
        branches[branch_id] = {
            "primitive_id": witness["primitive_id"],
            "source_vertex_index": int(witness["source_vertex_index"]),
            "witness_local_uc_m": local_uc,
            "target_pivot_uc_m": pivot_uc,
            "target_axis_uc": axis_uc,
            "radial_distance_m": float(witness["radial_distance_m"]),
            "samples": samples,
        }
    return {
        "schema": "axm.nature-five-branch-animation-target-oracle/v0.1",
        "branch_ids": list(BRANCH_IDS),
        "target_angle_rule": "target_angle_deg = -source_owner_angle_deg",
        "maximum_analytic_transport_residual_m": maximum_expected_transport_residual,
        "maximum_unnegated_angle_residual_m": maximum_wrong_sign_residual,
        "branches": branches,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--animation-root", type=Path, required=True)
    parser.add_argument("--rigging-root", type=Path, required=True)
    parser.add_argument("--uc-root", type=Path, required=True)
    parser.add_argument("--animation-evidence", type=Path, required=True)
    parser.add_argument("--rigging-evidence", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--claim-simultaneous-motion", action="store_true")
    parser.add_argument("--disable-angle-negation", action="store_true")
    args = parser.parse_args()

    if args.claim_simultaneous_motion:
        raise ValueError("Technical Art target transport does not grant simultaneous multi-branch motion acceptance")

    animation_root = args.animation_root.resolve()
    rigging_root = args.rigging_root.resolve()
    uc_root = args.uc_root.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    observed = {"animation": git_head(animation_root), "rigging": git_head(rigging_root), "uc": git_head(uc_root)}
    expected = {"animation": ANIMATION_HEAD, "rigging": RIGGING_HEAD, "uc": UC_HEAD}
    if observed != expected:
        raise ValueError(f"exact cross-repo head drift: observed={observed}, expected={expected}")

    animation = load_json(args.animation_evidence)
    rigging = load_json(args.rigging_evidence)
    if animation.get("result") != ANIMATION_RESULT:
        raise ValueError("exact Animation prerequisite is not green")
    if animation.get("owner", {}).get("exact_head") != RIGGING_HEAD:
        raise ValueError("Animation evidence no longer binds the exact Rigging family owner")
    if [row.get("branch_id") for row in animation.get("branches", [])] != list(BRANCH_IDS):
        raise ValueError("Animation branch family/order drift")
    if any(len(row.get("samples", [])) != 41 for row in animation["branches"]):
        raise ValueError("Animation sample field drift")
    if animation.get("truth_boundary", {}).get("target_engine_playback_claimed") is not False:
        raise ValueError("Animation prerequisite must not pre-claim target-engine playback")
    if rigging.get("result") != RIGGING_RESULT:
        raise ValueError("exact Rigging prerequisite is not green")

    donor = donor_source_mesh(rigging_root)
    source, mesh = donor["source"], donor["mesh"]
    baseline = adapt_mesh_for_uc(source, mesh, mesh_relation=f"EXACT_RIGGING_OWNER_MESH@{RIGGING_HEAD}")
    receiver = build_primary_branch_receiver(source, mesh, rigging, baseline_surface=baseline["surface"])

    surface_path = out / "nature-primary-branch-receiver.surface.json"
    flat_glb_path = out / "nature-primary-branch-receiver-flat.glb"
    rebound_glb_path = out / "nature-primary-branch-receiver-rigid.glb"
    manifest_path = out / "nature-primary-branch-receiver.manifest.json"
    oracle_path = out / "nature-primary-branch-animation-target-oracle.json"
    receipt_path = out / "nature-primary-branch-animation-uc-target-receipt.json"

    surface_path.write_bytes(canonical(receiver["surface"]) + b"\n")
    manifest_path.write_bytes(canonical(receiver["manifest"]) + b"\n")
    publication = publish_glb(flat_glb_path, receiver["surface"], replace=True)
    flat_verification = verify_glb(flat_glb_path.read_bytes(), expected_spec_digest=publication["specification_sha256"])
    rebound = rebind_rigid_scene_graph(flat_glb_path.read_bytes(), receiver["manifest"], expected_spec_digest=publication["specification_sha256"])
    rebound_glb_path.write_bytes(rebound["body"])
    rebound_verification = verify_glb(rebound["body"], expected_spec_digest=publication["specification_sha256"])
    graph_verification = verify_rigid_scene_graph(rebound["body"], expected_manifest_digest=rebound["manifest_sha256"])

    if not rebound["receipt"]["binary_geometry_payload_identical"]:
        raise ValueError("UC rigid-scene rebind changed geometry payload")
    if flat_verification["triangles"] != receiver["emitted_triangles"]:
        raise ValueError("flat UC GLB triangle count drift")
    if rebound_verification["triangles"] != receiver["emitted_triangles"]:
        raise ValueError("rebound UC GLB triangle count drift")
    if graph_verification["result"] != "PASS_RIGID_SCENE_GRAPH_STRUCTURE":
        raise ValueError("UC rigid scene graph verification did not pass")

    oracle = build_oracle(receiver, animation, use_negated_target_angle=not args.disable_angle_negation)
    if args.disable_angle_negation:
        if oracle["maximum_analytic_transport_residual_m"] <= 1e-4:
            raise ValueError("negative angle-sign control unexpectedly remained equivalent")
        raise ValueError("PASS_REJECTED_UNNEGATED_TARGET_ANGLE__MAX_RESIDUAL_%.9f_M" % oracle["maximum_analytic_transport_residual_m"])
    if oracle["maximum_analytic_transport_residual_m"] > 1e-9:
        raise ValueError(f"analytic handedness transport residual too large: {oracle['maximum_analytic_transport_residual_m']}")
    if oracle["maximum_unnegated_angle_residual_m"] <= 1e-3:
        raise ValueError("handedness negative control lacks a discriminating witness")
    oracle_path.write_bytes(canonical(oracle) + b"\n")

    uc_blobs = {
        "src/axm_uc/procedural_3d.py": git_blob(uc_root, "src/axm_uc/procedural_3d.py"),
        "src/axm_uc/rigid_scene_graph.py": git_blob(uc_root, "src/axm_uc/rigid_scene_graph.py"),
    }
    receipt = {
        "schema": SCHEMA,
        "result": RESULT,
        "heads": observed,
        "source_digest": donor["source_digest"],
        "mesh_digest": donor["mesh_digest"],
        "uc_executable_blobs": uc_blobs,
        "receiver": {
            "branch_ids": list(BRANCH_IDS),
            "surface_primitive_count": len(receiver["surface"]["primitives"]),
            "emitted_triangles": receiver["emitted_triangles"],
            "baseline_emitted_triangles": receiver["baseline_emitted_triangles"],
            "neutral_world_geometry_equivalent_to_static_bridge": receiver["neutral_world_geometry_equivalent_to_static_bridge"],
            "branch_front_triangle_counts": receiver["branch_front_triangle_counts"],
            "surface_sha256": sha256_file(surface_path),
            "flat_glb_sha256": sha256_file(flat_glb_path),
            "rebound_glb_sha256": sha256_file(rebound_glb_path),
            "manifest_sha256": rebound["manifest_sha256"],
            "binary_geometry_payload_identical_through_uc_graph_rebind": rebound["receipt"]["binary_geometry_payload_identical"],
            "nodes_rebound": rebound["receipt"]["nodes_rebound"],
            "parent_edges": rebound["receipt"]["parent_edges"],
        },
        "animation": {
            "result": animation["result"],
            "branch_count": len(animation["branches"]),
            "samples_per_branch": [len(row["samples"]) for row in animation["branches"]],
            "motion_method": animation["motion_method"],
        },
        "handedness_transport": {
            "source_to_uc": "[x,y,z] -> [x,z,y]",
            "determinant": -1,
            "target_angle_rule": "target_angle_deg = -source_owner_angle_deg",
            "maximum_analytic_transport_residual_m": oracle["maximum_analytic_transport_residual_m"],
            "maximum_unnegated_angle_residual_m": oracle["maximum_unnegated_angle_residual_m"],
        },
        "uc": {
            "product_code_modified_by_technical_art": False,
            "nature_domain_semantics_moved_to_uc": False,
            "generic_surface_publisher_used": True,
            "generic_rigid_scene_graph_rebind_used": True,
        },
        "truth_boundary": {
            "target_host_import_proven": False,
            "target_engine_sample_playback_proven": False,
            "simultaneous_multi_branch_motion_proven": False,
            "wind_or_vfx_behavior_proven": False,
            "source_or_biological_rom_proven": False,
            "runtime_controller_or_device_proven": False,
            "gameplay_or_physics_proven": False,
            "art_or_visual_qa_acceptance_proven": False,
            "canon_or_production_readiness_proven": False,
        },
    }
    receipt_path.write_bytes(canonical(receipt) + b"\n")
    (out / "exact-animation-head.txt").write_text(ANIMATION_HEAD + "\n", encoding="utf-8")
    (out / "exact-rigging-head.txt").write_text(RIGGING_HEAD + "\n", encoding="utf-8")
    (out / "exact-uc-head.txt").write_text(UC_HEAD + "\n", encoding="utf-8")
    (out / "exact-uc-procedural-3d-blob.txt").write_text(uc_blobs["src/axm_uc/procedural_3d.py"] + "\n", encoding="utf-8")
    (out / "exact-uc-rigid-scene-graph-blob.txt").write_text(uc_blobs["src/axm_uc/rigid_scene_graph.py"] + "\n", encoding="utf-8")
    print(json.dumps({
        "result": RESULT,
        "receiver_glb_sha256": receipt["receiver"]["rebound_glb_sha256"],
        "emitted_triangles": receiver["emitted_triangles"],
        "maximum_analytic_transport_residual_m": oracle["maximum_analytic_transport_residual_m"],
        "maximum_unnegated_angle_residual_m": oracle["maximum_unnegated_angle_residual_m"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

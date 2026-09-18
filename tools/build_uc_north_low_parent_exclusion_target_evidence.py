#!/usr/bin/env python3
"""Bind current north-low Animation/Rigging evidence to the existing TA -> UC receiver.

This stays Nature-local.  Universal Creation receives only generic surface + rigid-scene
inputs; detached-child semantics and the parent-exclusion rule remain owned by Nature
Rigging/Animation.
"""
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

from axm_nature_design.uc_primary_branch_receiver import build_primary_branch_receiver
from axm_nature_design.uc_surface_bridge import adapt_mesh_for_uc
from axm_uc.procedural_3d import publish_glb, verify_glb
from axm_uc.rigid_scene_graph import rebind_rigid_scene_graph, verify_rigid_scene_graph

ANIMATION_HEAD = "5cacd61e22433b0c33f29111827283b81cc0ba0d"
RIGGING_HEAD = "69640e558f0c1ac59d4d0e3155676e0967a03d04"
UC_HEAD = "7ddefca57b153fab02c1f54f38de22148cb52c1b"
GEOMETRY_DONOR_HEAD = "d32a41558910d78595042fb638a785714f825806"
SOURCE_DIGEST = "178cd8cfb1a859bff411f60e13154109528062cf0ad2384b343d406cc0cc9d61"
MESH_DIGEST = "aa9d450a78fef722672ea9af0f9aca98b4c1a0ca3705661784f5f61f3e9b6a31"
ANIMATION_RESULT = "PASS_NORTH_LOW_PARENT_EXCLUSION_TEMPORAL_REBIND_SAMPLED_DIAGNOSTIC_MOTION"
RIGGING_FAMILY_RESULT = "PASS_FIVE_PRIMARY_BRANCH_ROOT_SOCKET_RIGID_CHILD_FAMILY_GEOMETRY_RECEIVER_DIAGNOSTIC_MINUS5_TO_PLUS5"
ATTACHMENT_MODE = "DETACHED_DIAGNOSTIC_CHILD_SOCKET_ONLY"
RESULT = "PASS_NATURE_NORTH_LOW_PARENT_EXCLUSION_CURRENT_UC_TARGET_RECEIVER_READY"
SCHEMA = "axm.nature-north-low-parent-exclusion-uc-target-receiver/v0.1"
BRANCH_ID = "north-low"
POSITION_TOL_M = 5e-6


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    relative = [float(point[i]) - float(pivot[i]) for i in range(3)]
    ax, ay, az = [float(v) for v in axis]
    length = math.sqrt(ax * ax + ay * ay + az * az)
    if length <= 1e-12:
        raise ValueError("rotation axis is degenerate")
    ax, ay, az = ax / length, ay / length, az / length
    angle = math.radians(float(angle_deg))
    c, s = math.cos(angle), math.sin(angle)
    px, py, pz = relative
    dot = ax * px + ay * py + az * pz
    cross = (ay * pz - az * py, az * px - ax * pz, ax * py - ay * px)
    rotated = [
        px * c + cross[0] * s + ax * dot * (1.0 - c),
        py * c + cross[1] * s + ay * dot * (1.0 - c),
        pz * c + cross[2] * s + az * dot * (1.0 - c),
    ]
    return [rotated[i] + float(pivot[i]) for i in range(3)]


def source_to_uc(point: list[float]) -> list[float]:
    return [float(point[0]), float(point[2]), float(point[1])]


def distance(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((float(a[i]) - float(b[i])) ** 2 for i in range(3)))


def build_oracle(receiver: dict[str, Any], animation: dict[str, Any], *, leak_parent_command: bool) -> dict[str, Any]:
    witness = receiver["branch_witnesses"][BRANCH_ID]
    source_point = [float(v) for v in witness["source_neutral_world_m"]]
    pivot_source = [float(v) for v in witness["owner_pivot_source_m"]]
    axis_source = [float(v) for v in witness["owner_axis_source"]]
    pivot_uc = [float(v) for v in witness["target_pivot_uc_m"]]
    axis_uc = [float(v) for v in witness["target_axis_uc"]]
    local_uc = [float(v) for v in witness["local_position_uc_m"]]

    samples = animation.get("samples")
    if not isinstance(samples, list) or len(samples) != 41:
        raise ValueError("current Animation sample field drift")

    rows: list[dict[str, Any]] = []
    max_residual = 0.0
    max_forbidden_parent_command_as_child_residual = 0.0
    max_parent_stress_abs = 0.0
    for sample in samples:
        child_angle = float(sample["north_low_child_angle_deg"])
        parent_command = float(sample["upper_trunk_parent_stress_command_deg"])
        if abs(float(sample["parent_command_leak_m"])) > 1e-12:
            raise ValueError("Animation evidence reports parent-command leak")
        expected_source = rotate_about_axis(source_point, pivot_source, axis_source, child_angle)
        expected_uc = source_to_uc(expected_source)

        transported_source_angle = child_angle + parent_command if leak_parent_command else child_angle
        target_angle = -transported_source_angle
        local_rotated = rotate_about_axis(local_uc, [0.0, 0.0, 0.0], axis_uc, target_angle)
        target_world = [pivot_uc[i] + local_rotated[i] for i in range(3)]
        residual = distance(expected_uc, target_world)
        max_residual = max(max_residual, residual)

        forbidden_angle = -(child_angle + parent_command)
        forbidden_local = rotate_about_axis(local_uc, [0.0, 0.0, 0.0], axis_uc, forbidden_angle)
        forbidden_world = [pivot_uc[i] + forbidden_local[i] for i in range(3)]
        forbidden_residual = distance(expected_uc, forbidden_world)
        max_forbidden_parent_command_as_child_residual = max(
            max_forbidden_parent_command_as_child_residual, forbidden_residual
        )
        max_parent_stress_abs = max(max_parent_stress_abs, abs(parent_command))

        rows.append({
            "index": int(sample["index"]),
            "time_s": float(sample["time_s"]),
            "north_low_child_angle_deg": child_angle,
            "upper_trunk_parent_stress_command_deg": parent_command,
            "target_receiver_angle_deg": target_angle,
            "expected_witness_world_uc_m": expected_uc,
            "analytic_target_world_uc_m": target_world,
            "analytic_transport_residual_m": residual,
        })

    return {
        "schema": "axm.nature-north-low-parent-exclusion-target-oracle/v0.1",
        "branch_id": BRANCH_ID,
        "primitive_id": witness["primitive_id"],
        "source_vertex_index": int(witness["source_vertex_index"]),
        "witness_local_uc_m": local_uc,
        "target_pivot_uc_m": pivot_uc,
        "target_axis_uc": axis_uc,
        "target_angle_rule": "target_angle_deg = -north_low_child_angle_deg",
        "parent_stress_rule": "upper_trunk_parent_stress_command_deg is command-only and is not applied to the detached child receiver",
        "maximum_analytic_transport_residual_m": max_residual,
        "maximum_parent_stress_command_abs_deg": max_parent_stress_abs,
        "maximum_forbidden_parent_command_as_child_rotation_residual_m": max_forbidden_parent_command_as_child_residual,
        "samples": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--animation-root", type=Path, required=True)
    parser.add_argument("--rigging-root", type=Path, required=True)
    parser.add_argument("--uc-root", type=Path, required=True)
    parser.add_argument("--animation-evidence", type=Path, required=True)
    parser.add_argument("--rigging-evidence", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--apply-parent-command-as-child-rotation", action="store_true")
    parser.add_argument("--claim-production-skinning", action="store_true")
    args = parser.parse_args()

    if args.claim_production_skinning:
        raise ValueError("Technical Art target transport cannot promote detached diagnostic motion to production skinning")

    animation_root = args.animation_root.resolve()
    rigging_root = args.rigging_root.resolve()
    uc_root = args.uc_root.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    observed = {
        "animation": git_head(animation_root),
        "rigging": git_head(rigging_root),
        "uc": git_head(uc_root),
    }
    expected = {"animation": ANIMATION_HEAD, "rigging": RIGGING_HEAD, "uc": UC_HEAD}
    if observed != expected:
        raise ValueError(f"exact cross-repo head drift: observed={observed}, expected={expected}")

    animation = load_json(args.animation_evidence)
    rigging = load_json(args.rigging_evidence)
    if animation.get("result") != ANIMATION_RESULT:
        raise ValueError("exact current Animation prerequisite is not green")
    if animation.get("current_rigging_owner_head") != RIGGING_HEAD:
        raise ValueError("Animation evidence no longer binds exact current Rigging owner")
    scope = animation.get("motion_scope") or {}
    if scope.get("branch_id") != BRANCH_ID:
        raise ValueError("Animation branch identity drift")
    if scope.get("attachment_mode") != ATTACHMENT_MODE:
        raise ValueError("current detached attachment-mode gate drift")
    if scope.get("upper_trunk_parent_influence_enabled_for_north_low") is not False:
        raise ValueError("current Rigging parent-exclusion gate drift")
    if float(scope.get("diagnostic_parent_weight", 999.0)) != 0.0:
        raise ValueError("current diagnostic parent weight drift")
    timing = animation.get("timing") or {}
    if int(timing.get("endpoint_inclusive_samples", -1)) != 41 or int(timing.get("visible_repeat_samples", -1)) != 40:
        raise ValueError("current Animation timing identity drift")
    truth = animation.get("truth_boundary") or {}
    if truth.get("target_engine_playback_claimed") is not False:
        raise ValueError("Animation prerequisite must not pre-claim target playback")
    measurements = animation.get("measurements") or {}
    if float(measurements.get("maximum_parent_command_leak_m", 999.0)) > 1e-12:
        raise ValueError("Animation parent exclusion is not exact")
    if float(measurements.get("maximum_counterfactual_inherited_parent_output_delta_m", 0.0)) <= 1e-6:
        raise ValueError("Animation parent-inheritance negative is not discriminating")

    if rigging.get("result") != RIGGING_FAMILY_RESULT:
        raise ValueError("exact current Rigging family prerequisite is not green")

    donor = donor_source_mesh(rigging_root)
    source, mesh = donor["source"], donor["mesh"]
    baseline = adapt_mesh_for_uc(source, mesh, mesh_relation=f"EXACT_CURRENT_RIGGING_OWNER_MESH@{RIGGING_HEAD}")
    receiver = build_primary_branch_receiver(source, mesh, rigging, baseline_surface=baseline["surface"])

    surface_path = out / "nature-north-low-parent-exclusion-receiver.surface.json"
    flat_glb_path = out / "nature-north-low-parent-exclusion-receiver-flat.glb"
    rigid_glb_path = out / "nature-north-low-parent-exclusion-receiver-rigid.glb"
    manifest_path = out / "nature-north-low-parent-exclusion-receiver.manifest.json"
    oracle_path = out / "nature-north-low-parent-exclusion-target-oracle.json"
    receipt_path = out / "nature-north-low-parent-exclusion-uc-target-receipt.json"

    surface_path.write_bytes(canonical(receiver["surface"]) + b"\n")
    manifest_path.write_bytes(canonical(receiver["manifest"]) + b"\n")
    publication = publish_glb(flat_glb_path, receiver["surface"], replace=True)
    flat_verification = verify_glb(flat_glb_path.read_bytes(), expected_spec_digest=publication["specification_sha256"])
    rebound = rebind_rigid_scene_graph(
        flat_glb_path.read_bytes(),
        receiver["manifest"],
        expected_spec_digest=publication["specification_sha256"],
    )
    rigid_glb_path.write_bytes(rebound["body"])
    rigid_verification = verify_glb(rebound["body"], expected_spec_digest=publication["specification_sha256"])
    graph_verification = verify_rigid_scene_graph(
        rebound["body"], expected_manifest_digest=rebound["manifest_sha256"]
    )
    if not rebound["receipt"]["binary_geometry_payload_identical"]:
        raise ValueError("UC rigid scene rebind changed geometry payload")
    if flat_verification["triangles"] != receiver["emitted_triangles"] or rigid_verification["triangles"] != receiver["emitted_triangles"]:
        raise ValueError("UC published receiver triangle count drift")
    if graph_verification["result"] != "PASS_RIGID_SCENE_GRAPH_STRUCTURE":
        raise ValueError("UC rigid scene graph verification did not pass")

    oracle = build_oracle(receiver, animation, leak_parent_command=args.apply_parent_command_as_child_rotation)
    if args.apply_parent_command_as_child_rotation:
        if oracle["maximum_analytic_transport_residual_m"] <= 1e-3:
            raise ValueError("parent-command leak negative unexpectedly remained equivalent")
        raise ValueError(
            "PASS_REJECTED_PARENT_COMMAND_AS_CHILD_ROTATION__MAX_RESIDUAL_%.9f_M"
            % oracle["maximum_analytic_transport_residual_m"]
        )
    if oracle["maximum_analytic_transport_residual_m"] > 1e-9:
        raise ValueError(f"analytic target transport residual too large: {oracle['maximum_analytic_transport_residual_m']}")
    if oracle["maximum_parent_stress_command_abs_deg"] < 2.49:
        raise ValueError("parent stress command lost its discriminating amplitude")
    if oracle["maximum_forbidden_parent_command_as_child_rotation_residual_m"] <= 1e-3:
        raise ValueError("parent-command-as-child-rotation negative is not discriminating")
    oracle_path.write_bytes(canonical(oracle) + b"\n")

    uc_blobs = {
        "src/axm_uc/procedural_3d.py": git_blob(uc_root, "src/axm_uc/procedural_3d.py"),
        "src/axm_uc/rigid_scene_graph.py": git_blob(uc_root, "src/axm_uc/rigid_scene_graph.py"),
    }
    rigging_blobs = {
        "src/axm_nature_design/rear_tree_rigging_primary_branch_family.py": git_blob(rigging_root, "src/axm_nature_design/rear_tree_rigging_primary_branch_family.py"),
        "src/axm_nature_design/rear_tree_rigging_north_low_parent_influence_gate.py": git_blob(rigging_root, "src/axm_nature_design/rear_tree_rigging_north_low_parent_influence_gate.py"),
        "src/axm_nature_design/rear_tree_rigging_north_low_attachment_representation_gate.py": git_blob(rigging_root, "src/axm_nature_design/rear_tree_rigging_north_low_attachment_representation_gate.py"),
    }
    animation_blobs = {
        "src/axm_nature_design/rear_tree_animation_north_low_parent_exclusion_temporal_rebind.py": git_blob(animation_root, "src/axm_nature_design/rear_tree_animation_north_low_parent_exclusion_temporal_rebind.py"),
    }

    receipt = {
        "schema": SCHEMA,
        "result": RESULT,
        "heads": observed,
        "geometry_attachment_donor_head": GEOMETRY_DONOR_HEAD,
        "source_digest": donor["source_digest"],
        "mesh_digest": donor["mesh_digest"],
        "animation_executable_blobs": animation_blobs,
        "rigging_executable_blobs": rigging_blobs,
        "uc_executable_blobs": uc_blobs,
        "receiver": {
            "surface_primitive_count": len(receiver["surface"]["primitives"]),
            "emitted_triangles": receiver["emitted_triangles"],
            "baseline_emitted_triangles": receiver["baseline_emitted_triangles"],
            "neutral_world_geometry_equivalent_to_static_bridge": receiver["neutral_world_geometry_equivalent_to_static_bridge"],
            "branch_front_triangle_counts": receiver["branch_front_triangle_counts"],
            "surface_sha256": sha256_file(surface_path),
            "flat_glb_sha256": sha256_file(flat_glb_path),
            "rigid_glb_sha256": sha256_file(rigid_glb_path),
            "manifest_sha256": rebound["manifest_sha256"],
            "binary_geometry_payload_identical_through_uc_graph_rebind": rebound["receipt"]["binary_geometry_payload_identical"],
            "nodes_rebound": rebound["receipt"]["nodes_rebound"],
            "parent_edges": rebound["receipt"]["parent_edges"],
        },
        "animation": {
            "result": animation["result"],
            "branch_id": BRANCH_ID,
            "attachment_mode": scope["attachment_mode"],
            "diagnostic_parent_weight": scope["diagnostic_parent_weight"],
            "upper_trunk_parent_influence_enabled": scope["upper_trunk_parent_influence_enabled_for_north_low"],
            "sample_count": len(animation["samples"]),
            "visible_repeat_samples": timing["visible_repeat_samples"],
            "maximum_parent_command_leak_m": measurements["maximum_parent_command_leak_m"],
            "maximum_counterfactual_inherited_parent_output_delta_m": measurements["maximum_counterfactual_inherited_parent_output_delta_m"],
        },
        "handedness_transport": {
            "source_to_uc": "[x,y,z] -> [x,z,y]",
            "determinant": -1,
            "target_angle_rule": oracle["target_angle_rule"],
            "maximum_analytic_transport_residual_m": oracle["maximum_analytic_transport_residual_m"],
        },
        "parent_exclusion_transport": {
            "parent_stress_rule": oracle["parent_stress_rule"],
            "maximum_parent_stress_command_abs_deg": oracle["maximum_parent_stress_command_abs_deg"],
            "maximum_forbidden_parent_command_as_child_rotation_residual_m": oracle["maximum_forbidden_parent_command_as_child_rotation_residual_m"],
        },
        "uc": {
            "product_code_modified_by_technical_art": False,
            "nature_domain_semantics_moved_to_uc": False,
        },
        "truth_boundary": {
            "target_host_import_proven": False,
            "detached_child_target_transport_prepared": True,
            "upper_trunk_deformation_receiver_proven": False,
            "connected_attachment_or_production_skinning_proven": False,
            "wind_or_vfx_behavior_proven": False,
            "runtime_controller_or_target_device_proven": False,
            "collision_gameplay_or_physics_proven": False,
            "art_or_visual_qa_acceptance_proven": False,
            "canon_or_production_readiness_proven": False,
        },
    }
    receipt_path.write_bytes(canonical(receipt) + b"\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

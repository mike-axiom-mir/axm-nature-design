#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from axm_nature_design.uc_surface_bridge import adapt_mesh_for_uc
from axm_uc.mesh_topology import inspect_mesh_topology
from axm_uc.procedural_3d import publish_glb, verify_glb

GEOMETRY_COMMIT = "e2224d4bf88f7e68503072c884e5a726b8d0c53d"
REAR_SOURCE_COMMIT = "a4e5ee011e1d87f47866a7e6c6f4e66f57b6af12"
UC_COMMIT = "4ad22937779d569b0b5f96ff23f597af2727db19"
EXPECTED = {
    "sapling-neutral-001": {
        "source": "a61207b23c441b2cc0becd165fa62289bb7e51065ae0d6fa56bf9f3cab036cc1",
        "baseline": "89b835bd8f3e728206543d210787f1bbd1cc1bacb6d01f6695caf3ea1a63fa4c",
        "candidate": "47dd4d82651138299d05071df3e8a410f21f673ab8d42b936d7222eb5351b862",
        "path": "examples/sapling_neutral_001.json",
        "source_relation": "GEOMETRY_BRANCH",
    },
    "compact-east-tree-neutral-001": {
        "source": "9c87cf26f02f7adee832908652942218ec779c9029a0611aae1fb66eb0f62f54",
        "baseline": "c7367ed5dcea6ebe39869c48fd653845b25c9a8725a2e637a1d6f2fbee1fa32f",
        "candidate": "420135f6effbadb1b344675948b9ddc471dcb83177702888f0b32327c5121c18",
        "path": "examples/compact_east_tree_neutral_001.json",
        "source_relation": "GEOMETRY_BRANCH",
    },
    "east-rear-tree-neutral-001": {
        "source": "0adf2cde8cfc355ec21b6fb06c6759b753300164b5f72ba029dc1b8c6d2ef307",
        "baseline": "d7fc5deaa1c12d1d8c7d7b6dc95bf1e8544ce26140ee2e4a7d2c67a2c4133e48",
        "candidate": "aa9d450a78fef722672ea9af0f9aca98b4c1a0ca3705661784f5f61f3e9b6a31",
        "path": "examples/east_rear_tree_neutral_001.json",
        "source_relation": "EXACT_ORGANIC_REAR_DONOR",
    },
}


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head(root: Path) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()


def geometry_payload(geometry_root: Path, rear_source_root: Path) -> dict[str, Any]:
    code = r'''
import json
import os
from pathlib import Path
from axm_nature_design.organic_form import build_mesh, digest, load_source
from axm_nature_design.topology_repair import inspect_index_topology, repair_tapered_segment_cap_winding

root = Path.cwd()
rear_root = Path(os.environ["AXM_REAR_SOURCE_ROOT"])
paths = [
    (root / "examples/sapling_neutral_001.json", "GEOMETRY_BRANCH"),
    (root / "examples/compact_east_tree_neutral_001.json", "GEOMETRY_BRANCH"),
    (rear_root / "examples/east_rear_tree_neutral_001.json", "EXACT_ORGANIC_REAR_DONOR"),
]
out = {"studies": {}}
for path, source_relation in paths:
    source = load_source(path)
    baseline = build_mesh(source)
    candidate, flipped = repair_tapered_segment_cap_winding(baseline)
    out["studies"][source["study_id"]] = {
        "source": source,
        "source_relation": source_relation,
        "baseline_mesh": baseline,
        "candidate_mesh": candidate,
        "source_digest": digest(source),
        "baseline_mesh_digest": digest(baseline),
        "candidate_mesh_digest": digest(candidate),
        "flipped_triangle_count": len(flipped),
        "baseline_topology": inspect_index_topology(baseline),
        "candidate_topology": inspect_index_topology(candidate),
    }
print(json.dumps(out, sort_keys=True, separators=(",", ":")))
'''
    env = dict(os.environ)
    env["PYTHONPATH"] = str(geometry_root / "src")
    env["AXM_REAR_SOURCE_ROOT"] = str(rear_source_root)
    raw = subprocess.check_output(
        [sys.executable, "-c", code],
        cwd=geometry_root,
        env=env,
        text=True,
    )
    return json.loads(raw)


def topology_report(mesh: dict[str, Any]) -> dict[str, Any]:
    return inspect_mesh_topology(
        mesh["vertices"],
        [index for triangle in mesh["triangles"] for index in triangle],
    )


def primitive_topology(surface: dict[str, Any], primitive_id: str) -> dict[str, Any]:
    primitive = next(item for item in surface["primitives"] if item["id"] == primitive_id)
    return inspect_mesh_topology(primitive["positions"], primitive["indices"])


def publish_pair(out: Path, study_id: str, relation: str, bridge: dict[str, Any]) -> dict[str, Any]:
    stem = f"{study_id}-{relation}"
    surface_path = out / f"{stem}.surface.json"
    glb_path = out / f"{stem}.glb"
    surface_path.write_text(canonical(bridge["surface"]) + "\n", encoding="utf-8")
    publication = publish_glb(glb_path, bridge["surface"], replace=True)
    verification = verify_glb(
        glb_path.read_bytes(),
        expected_spec_digest=publication["specification_sha256"],
    )
    return {
        "surface_path": surface_path.name,
        "surface_sha256": sha256(surface_path),
        "glb_path": glb_path.name,
        "glb_sha256": sha256(glb_path),
        "publication": publication,
        "verification": verification,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--geometry-root", type=Path, required=True)
    parser.add_argument("--rear-source-root", type=Path, required=True)
    parser.add_argument("--uc-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    geometry_root = args.geometry_root.resolve()
    rear_source_root = args.rear_source_root.resolve()
    uc_root = args.uc_root.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    observed_geometry = git_head(geometry_root)
    observed_rear_source = git_head(rear_source_root)
    observed_uc = git_head(uc_root)
    if observed_geometry != GEOMETRY_COMMIT:
        raise SystemExit(f"Geometry donor drifted: {observed_geometry}")
    if observed_rear_source != REAR_SOURCE_COMMIT:
        raise SystemExit(f"rear Organic donor drifted: {observed_rear_source}")
    if observed_uc != UC_COMMIT:
        raise SystemExit(f"UC donor drifted: {observed_uc}")

    donor = geometry_payload(geometry_root, rear_source_root)
    study_receipts: dict[str, Any] = {}

    for study_id, expected in EXPECTED.items():
        item = donor["studies"][study_id]
        for key, donor_key in (("source", "source_digest"), ("baseline", "baseline_mesh_digest"), ("candidate", "candidate_mesh_digest")):
            if item[donor_key] != expected[key]:
                raise SystemExit(f"{study_id} {donor_key} drifted: {item[donor_key]}")
        if item["source_relation"] != expected["source_relation"]:
            raise SystemExit(f"{study_id} source relation drifted: {item['source_relation']}")
        if item["flipped_triangle_count"] != 260:
            raise SystemExit(f"{study_id} expected 260 cap flips")
        if item["baseline_topology"]["shared_edge_orientation_conflicts"] != 260:
            raise SystemExit(f"{study_id} Geometry baseline conflict count drifted")
        if item["candidate_topology"]["shared_edge_orientation_conflicts"] != 0:
            raise SystemExit(f"{study_id} Geometry candidate conflict count drifted")

        source = item["source"]
        baseline_mesh = item["baseline_mesh"]
        candidate_mesh = item["candidate_mesh"]
        uc_source_baseline = topology_report(baseline_mesh)
        uc_source_candidate = topology_report(candidate_mesh)
        if uc_source_baseline["orientation_conflict_edge_count"] != 260:
            raise SystemExit(f"{study_id} UC source preflight did not reproduce 260 conflicts")
        if uc_source_candidate["orientation_conflict_edge_count"] != 0:
            raise SystemExit(f"{study_id} UC source preflight did not clear candidate conflicts")

        baseline_bridge = adapt_mesh_for_uc(
            source,
            baseline_mesh,
            mesh_relation=f"GEOMETRY_PR7_BASELINE@{GEOMETRY_COMMIT}",
        )
        candidate_bridge = adapt_mesh_for_uc(
            source,
            candidate_mesh,
            mesh_relation=f"GEOMETRY_PR7_REINDEX_ONLY_CANDIDATE@{GEOMETRY_COMMIT}",
        )
        if baseline_bridge["source_mesh_digest"] != expected["baseline"]:
            raise SystemExit(f"{study_id} bridge baseline digest mismatch")
        if candidate_bridge["source_mesh_digest"] != expected["candidate"]:
            raise SystemExit(f"{study_id} bridge candidate digest mismatch")

        uc_surface_baseline = primitive_topology(baseline_bridge["surface"], "woody")
        uc_surface_candidate = primitive_topology(candidate_bridge["surface"], "woody")
        if uc_surface_baseline["orientation_conflict_edge_count"] != 260:
            raise SystemExit(f"{study_id} emitted woody surface lost baseline conflict evidence")
        if uc_surface_candidate["orientation_conflict_edge_count"] != 0:
            raise SystemExit(f"{study_id} emitted woody surface did not preserve repair")

        baseline_publish = publish_pair(out, study_id, "baseline", baseline_bridge)
        candidate_publish = publish_pair(out, study_id, "candidate", candidate_bridge)
        for relation, payload in (("baseline", baseline_publish), ("candidate", candidate_publish)):
            verification = payload["verification"]
            if verification["triangles"] != baseline_bridge["emitted_triangles"]:
                raise SystemExit(f"{study_id} {relation} UC triangle verification drifted")
            if not verification["geometry_validation"]["winding_matches_vertex_normals"]:
                raise SystemExit(f"{study_id} {relation} UC per-triangle winding/normal verification failed")

        receipt = {
            "study_id": study_id,
            "source_relation": item["source_relation"],
            "source_digest": item["source_digest"],
            "baseline_mesh_digest": item["baseline_mesh_digest"],
            "candidate_mesh_digest": item["candidate_mesh_digest"],
            "flipped_triangle_count": item["flipped_triangle_count"],
            "geometry_index_topology": {
                "baseline": item["baseline_topology"],
                "candidate": item["candidate_topology"],
            },
            "uc_source_topology_preflight": {
                "baseline": uc_source_baseline,
                "candidate": uc_source_candidate,
            },
            "uc_emitted_woody_topology_preflight": {
                "baseline": uc_surface_baseline,
                "candidate": uc_surface_candidate,
            },
            "uc_glb": {
                "baseline": baseline_publish,
                "candidate": candidate_publish,
            },
            "result": "PASS_REINDEX_ONLY_CANDIDATE_PRESERVES_TOPOLOGY_REPAIR_THROUGH_UC_GLB",
        }
        receipt_path = out / f"{study_id}-topology-preflight-receipt.json"
        receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        study_receipts[study_id] = receipt

    receiving_head = git_head(Path.cwd())
    overall = {
        "schema": "axm.nature-uc-topology-preflight-run/v0.2",
        "state": "PASS_EXACT_THREE_SOURCE_NATURE_TOPOLOGY_PREFLIGHT_THROUGH_CURRENT_UC_GLB",
        "receiving_repository": "mike-axiom-mir/axm-nature-design",
        "receiving_head": receiving_head,
        "geometry_repository": "mike-axiom-mir/axm-nature-design",
        "geometry_pr": 7,
        "geometry_commit": observed_geometry,
        "rear_source_repository": "mike-axiom-mir/axm-nature-design",
        "rear_source_pr": 8,
        "rear_source_commit": observed_rear_source,
        "uc_repository": "mike-axiom-mir/axm-universal-creation",
        "uc_commit": observed_uc,
        "studies": study_receipts,
        "pipeline_decision": {
            "uc_core_change_required": False,
            "nature_domain_semantics_moved_to_uc": False,
            "required_order": [
                "retain exact source and donor identity",
                "run generic UC seam-welded topology preflight while source adjacency is attributable",
                "apply source-owned reindex-only candidate when explicitly selected",
                "translate coordinates and flat normals in Nature bridge",
                "rerun generic UC topology preflight on emitted woody surface",
                "publish and verify exact GLB bytes",
                "observe exact rear-tree GLBs separately in the target host before any source migration",
            ],
            "reason": "Current UC already owns the reusable domain-neutral topology inspector and GLB publisher. Nature owns source semantics and the coordinate/winding adapter; the missing integration evidence is the newer exact rear source and target-host culling consequence, not a new UC abstraction.",
        },
        "truth_boundary": {
            "organic_source_rewritten": False,
            "geometry_candidate_promoted_to_source": False,
            "uc_core_modified": False,
            "shared_edge_orientation_checked": True,
            "exact_uc_glb_bytes_published_and_verified": True,
            "target_engine_culling_rendered": False,
            "normals_tangents_uvs_finalized": False,
            "wind_or_deformation_tested": False,
            "source_migration_approved": False,
            "visual_acceptance_claimed": False,
            "runtime_or_gameplay_acceptance_claimed": False,
        },
        "non_claims": [
            "No Organic source migration is authorized by this receipt; exact digest-bound consumers must be rebuilt deliberately if Geometry PR #7 is later adopted.",
            "Target-host culling is a separate retained observer receipt, not inferred from this structural preflight.",
            "No foliage manifold claim is made because the existing proof-only explicit opposite-winding leaf backfaces intentionally create two-sided geometry.",
            "No outward-normal correctness, final normals, tangents, UVs, materials, deformation, runtime budget, gameplay, CANON, production-readiness, or Technical-Art mastery claim.",
        ],
    }
    overall_path = out / "uc-topology-preflight-overall.json"
    overall_path.write_text(json.dumps(overall, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "state": overall["state"],
        "receiving_head": receiving_head,
        "geometry_commit": observed_geometry,
        "rear_source_commit": observed_rear_source,
        "uc_commit": observed_uc,
        "studies": {
            key: {
                "baseline_conflicts": value["uc_source_topology_preflight"]["baseline"]["orientation_conflict_edge_count"],
                "candidate_conflicts": value["uc_source_topology_preflight"]["candidate"]["orientation_conflict_edge_count"],
                "baseline_glb": value["uc_glb"]["baseline"]["glb_sha256"],
                "candidate_glb": value["uc_glb"]["candidate"]["glb_sha256"],
            }
            for key, value in study_receipts.items()
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()

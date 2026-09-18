#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axm_nature_design.organic_form import build_mesh, digest, load_source
from axm_nature_design.procedural_family import generate_accepted_variant, load_family
from axm_nature_design.source_topology_migration import inspect_shared_edge_orientation

SCHEMA = "axm.nature-procedural-leaf-backface-family-evidence/v0.1"
PASS_STATE = "PASS_PROCEDURAL_VARIANTS_EXPLICIT_LEAF_BACKFACE_DERIVATION"
CONTRACT_PATH = ROOT / "examples/procedural_leaf_backface_family_001.json"
EXPECTED_MUTATOR_BLOB = "2e405aa3a7a85228d61cc1f1d3dd76e06aaa2341"
EXPECTED_FAMILY_BLOBS = {
    "examples/sapling_variation_family_001.json": "ce06ab419e8866a28448618af69b35d8cea60311",
    "examples/compact_tree_variation_family_001.json": "72ed799e2e7b35aad7cec1a35b09c3d7134fbd4e",
    "examples/east_rear_tree_variation_family_001.json": "51ad3dd368b7a73fc5cf50c6ade63ceddc85ce53",
}


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _git_head(root: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


def _git_blob(root: Path, relative_path: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "hash-object", relative_path],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


def _bounds(vertices: list[list[float]]) -> list[list[float]]:
    return [
        [min(float(v[a]) for v in vertices) for a in range(3)],
        [max(float(v[a]) for v in vertices) for a in range(3)],
    ]


def _provider_call(geometry_root: Path, mesh: dict, *, expect_success: bool = True) -> dict | None:
    program = r'''
import json, sys
from axm_nature_design.leaf_backface_candidate import add_explicit_leaf_backfaces, inspect_leaf_pairs
from axm_nature_design.organic_form import digest, structural_checks
from axm_nature_design.source_topology_migration import inspect_shared_edge_orientation
mesh = json.load(sys.stdin)
candidate = add_explicit_leaf_backfaces(mesh)
json.dump({
    "candidate": candidate,
    "candidate_digest": digest(candidate),
    "pairs": inspect_leaf_pairs(mesh, candidate),
    "structural": structural_checks(candidate),
    "topology": inspect_shared_edge_orientation(candidate),
}, sys.stdout, sort_keys=True, separators=(",", ":"))
'''
    env = os.environ.copy()
    env["PYTHONPATH"] = str((geometry_root / "src").resolve())
    run = subprocess.run(
        [sys.executable, "-c", program],
        input=json.dumps(mesh, sort_keys=True, separators=(",", ":")),
        text=True,
        capture_output=True,
        cwd=geometry_root,
        env=env,
    )
    if expect_success:
        if run.returncode != 0:
            raise RuntimeError(f"Geometry provider failed: {run.stderr.strip()}")
        return json.loads(run.stdout)
    if run.returncode == 0:
        raise RuntimeError("malformed leaf-region control unexpectedly succeeded")
    return {"returncode": run.returncode, "stderr": run.stderr.strip()[-800:]}


def _validate_provider(geometry_root: Path, contract: dict) -> dict:
    provider = contract["geometry_provider"]
    observed_head = _git_head(geometry_root)
    if observed_head != provider["ref"]:
        raise RuntimeError(f"Geometry provider head drift: {observed_head} != {provider['ref']}")
    observed_blob = _git_blob(geometry_root, provider["path"])
    if observed_blob != provider["git_blob"]:
        raise RuntimeError(f"Geometry provider helper drift: {observed_blob} != {provider['git_blob']}")
    return {"repository": provider["repository"], "head": observed_head, "path": provider["path"], "git_blob": observed_blob}


def _validate_local_procedural_identity(contract: dict) -> dict:
    mutator_blob = _git_blob(ROOT, "src/axm_nature_design/procedural_family.py")
    if mutator_blob != EXPECTED_MUTATOR_BLOB:
        raise RuntimeError(f"procedural mutator drift: {mutator_blob} != {EXPECTED_MUTATOR_BLOB}")
    family_blobs = {}
    for path, expected in EXPECTED_FAMILY_BLOBS.items():
        observed = _git_blob(ROOT, path)
        if observed != expected:
            raise RuntimeError(f"procedural family drift: {path}: {observed} != {expected}")
        family_blobs[path] = observed
    if len(contract["cases"]) != int(contract["expected_source_case_count"]):
        raise RuntimeError("contract source-case count drift")
    return {"mutator_blob": mutator_blob, "family_blobs": family_blobs}


def _build_variant(case: dict, seed: int, geometry_root: Path, contract: dict, out: Path) -> dict:
    source = load_source(ROOT / case["source_path"])
    family = load_family(ROOT / case["family_path"])
    result = generate_accepted_variant(source, family, int(seed))
    receipt = result["receipt"]
    candidate_source = result["candidate"]
    if receipt["state"] != "PASS_BOUNDED_VARIANT" or candidate_source is None:
        raise RuntimeError(f"{case['case_id']} seed {seed}: procedural variant did not PASS")
    metrics = receipt["metrics"]
    if not all((metrics["organic_checks_pass"], metrics["envelope_ok"], metrics["attachments_preserved"], metrics["immutable_fields_preserved"])):
        raise RuntimeError(f"{case['case_id']} seed {seed}: inherited procedural gates failed")

    baseline = build_mesh(candidate_source)
    baseline_digest = digest(baseline)
    if len(baseline["vertices"]) != int(contract["expected_baseline_vertices"]) or len(baseline["triangles"]) != int(contract["expected_baseline_triangles"]):
        raise RuntimeError(f"{case['case_id']} seed {seed}: baseline mesh budget drift")
    baseline_topology = inspect_shared_edge_orientation(baseline)
    if baseline_topology["shared_edge_orientation_conflicts"] != 0 or baseline_topology["nonmanifold_edges"] != 0:
        raise RuntimeError(f"{case['case_id']} seed {seed}: migrated baseline topology regressed")

    provider = _provider_call(geometry_root, baseline)
    assert provider is not None
    derived = provider["candidate"]
    pairs = provider["pairs"]
    leaf_count = int(contract["expected_leaf_blades_per_output"])
    checks = {
        "baseline_vertices_exact_prefix": derived["vertices"][:len(baseline["vertices"])] == baseline["vertices"],
        "baseline_triangles_exact_prefix": derived["triangles"][:len(baseline["triangles"])] == baseline["triangles"],
        "baseline_regions_exact_prefix": derived["regions"][:len(baseline["regions"])] == baseline["regions"],
        "leaf_count_exact": pairs["leaf_blades"] == leaf_count,
        "one_backface_per_leaf": pairs["backface_regions"] == leaf_count,
        "all_leaf_positions_exact": pairs["exact_position_pairs"] == leaf_count,
        "all_winding_opposed": pairs["opposite_winding_pairs"] == leaf_count,
        "candidate_vertex_budget_exact": len(derived["vertices"]) == int(contract["expected_candidate_vertices"]),
        "candidate_triangle_budget_exact": len(derived["triangles"]) == int(contract["expected_candidate_triangles"]),
        "bounds_unchanged": _bounds(derived["vertices"]) == _bounds(baseline["vertices"]),
        "structural_checks_pass": bool(provider["structural"]["pass"]),
        "nonmanifold_edges_zero": provider["topology"]["nonmanifold_edges"] == 0,
        "orientation_conflicts_zero": provider["topology"]["shared_edge_orientation_conflicts"] == 0,
        "candidate_distinct_from_baseline": provider["candidate_digest"] != baseline_digest,
    }
    if not all(checks.values()):
        failed = [name for name, ok in checks.items() if not ok]
        raise RuntimeError(f"{case['case_id']} seed {seed}: derived candidate checks failed: {failed}")

    mesh_name = f"{case['case_id']}-seed-{seed}-leaf-backface.mesh.json"
    _write_json(out / "meshes" / mesh_name, derived)
    return {
        "case_id": case["case_id"],
        "seed": int(seed),
        "accepted_attempt": int(receipt["accepted_attempt"]),
        "variant_source_digest": digest(candidate_source),
        "baseline_mesh_digest": baseline_digest,
        "candidate_mesh_digest": provider["candidate_digest"],
        "baseline_vertices": len(baseline["vertices"]),
        "baseline_triangles": len(baseline["triangles"]),
        "candidate_vertices": len(derived["vertices"]),
        "candidate_triangles": len(derived["triangles"]),
        "leaf_pairs": pairs,
        "topology": provider["topology"],
        "checks": checks,
        "retained_mesh": f"meshes/{mesh_name}",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--geometry-root", required=True, type=Path)
    args = parser.parse_args()

    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if contract.get("schema") != "axm.nature-procedural-leaf-backface-family/v0.1":
        raise RuntimeError("unsupported procedural leaf-backface contract schema")
    provider_identity = _validate_provider(args.geometry_root.resolve(), contract)
    procedural_identity = _validate_local_procedural_identity(contract)

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    outputs = []
    malformed_controls = []
    for case in contract["cases"]:
        family = load_family(ROOT / case["family_path"])
        seeds = [int(value) for value in family["evidence_seeds"]]
        if len(seeds) != int(contract["expected_variants_per_source"]):
            raise RuntimeError(f"{case['case_id']}: evidence seed count drift")
        for seed in seeds:
            outputs.append(_build_variant(case, seed, args.geometry_root.resolve(), contract, out))

        # One provider-level fail-closed mutation per materially different source family.
        source = load_source(ROOT / case["source_path"])
        first = generate_accepted_variant(source, family, seeds[0])
        bad_mesh = build_mesh(first["candidate"])
        bad_mesh = copy.deepcopy(bad_mesh)
        leaf = next(region for region in bad_mesh["regions"] if region.get("kind") == "leaf-blade")
        leaf["triangle_count"] = 1
        failure = _provider_call(args.geometry_root.resolve(), bad_mesh, expect_success=False)
        malformed_controls.append({"case_id": case["case_id"], "seed": seeds[0], "provider_rejected": True, "provider_failure": failure})

    expected_total = int(contract["expected_total_outputs"])
    if len(outputs) != expected_total:
        raise RuntimeError(f"retained output count drift: {len(outputs)} != {expected_total}")
    baseline_digests = {row["baseline_mesh_digest"] for row in outputs}
    candidate_digests = {row["candidate_mesh_digest"] for row in outputs}
    source_digests = {row["variant_source_digest"] for row in outputs}
    if len(baseline_digests) != expected_total or len(candidate_digests) != expected_total or len(source_digests) != expected_total:
        raise RuntimeError("procedural outputs collapsed to duplicate identity")
    if any(row["baseline_mesh_digest"] == row["candidate_mesh_digest"] for row in outputs):
        raise RuntimeError("derived candidate collapsed to baseline identity")

    summary = {
        "schema": SCHEMA,
        "state": PASS_STATE,
        "procedural_head": _git_head(ROOT),
        "contract": contract,
        "geometry_provider": provider_identity,
        "procedural_identity": procedural_identity,
        "source_case_count": len(contract["cases"]),
        "retained_output_count": len(outputs),
        "distinct_variant_source_digests": len(source_digests),
        "distinct_baseline_mesh_digests": len(baseline_digests),
        "distinct_candidate_mesh_digests": len(candidate_digests),
        "all_outputs_materially_distinct": len(candidate_digests) == expected_total,
        "all_candidate_checks_pass": all(all(row["checks"].values()) for row in outputs),
        "all_failure_bounds_hold": all(row["provider_rejected"] for row in malformed_controls),
        "outputs": outputs,
        "failure_controls": malformed_controls,
        "decision": "PASS_DERIVED_REVIEW_FAMILY_ONLY__NO_SOURCE_OR_RECEIVER_ADOPTION",
        "truth_boundary": contract["truth_boundary"],
    }
    _write_json(out / "summary.json", summary)
    (out / "exact-head.txt").write_text(summary["procedural_head"] + "\n", encoding="utf-8")
    (out / "geometry-provider-head.txt").write_text(provider_identity["head"] + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in (
        "state", "procedural_head", "source_case_count", "retained_output_count",
        "distinct_candidate_mesh_digests", "all_candidate_checks_pass", "all_failure_bounds_hold", "decision"
    )}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

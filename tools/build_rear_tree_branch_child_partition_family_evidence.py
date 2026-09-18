#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from axm_nature_design.branch_partition_family import (
    assemble_family,
    derive_partition,
    digest,
    validate_contract,
)

CONTRACT_PATH = ROOT / "examples" / "rear_tree_branch_child_partition_family_001.json"
PASS_STATE = "PASS_BOUNDED_PRIMARY_BRANCH_CHILD_PARTITION_FAMILY"
DECISION = "PASS_DERIVED_REGION_PARTITIONS_ONLY__NO_SOURCE_OR_RIGGING_ADOPTION"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_head(root: Path) -> str:
    return subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()


def git_blob(root: Path, relpath: str) -> str:
    return subprocess.run(["git", "-C", str(root), "rev-parse", f"HEAD:{relpath}"], check=True, capture_output=True, text=True).stdout.strip()


def load_exact_organic_builder(organic_root: Path, relpath: str):
    path = organic_root / relpath
    spec = importlib.util.spec_from_file_location("axm_exact_organic_form_partition_provider", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load exact Organic form builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_provider(organic_root: Path, contract: dict):
    validate_contract(contract)
    provider = contract["organic_provider"]
    observed_head = git_head(organic_root)
    if observed_head != provider["ref"]:
        raise ValueError(f"Organic provider head drift: {observed_head} != {provider['ref']}")
    if git_blob(organic_root, provider["source_path"]) != provider["source_blob"]:
        raise ValueError("Organic source blob drift")
    if git_blob(organic_root, provider["builder_path"]) != provider["builder_blob"]:
        raise ValueError("Organic builder blob drift")
    source = load_json(organic_root / provider["source_path"])
    builder = load_exact_organic_builder(organic_root, provider["builder_path"])
    if builder.digest(source) != provider["source_digest"]:
        raise ValueError("Organic source canonical digest drift")
    mesh = builder.build_mesh(source)
    if builder.digest(mesh) != provider["generated_mesh_digest"]:
        raise ValueError("Organic generated mesh digest drift")
    return source, mesh, builder


def expect_rejection(label: str, action) -> dict:
    try:
        action()
    except Exception as exc:
        return {"label": label, "rejected": True, "error": f"{type(exc).__name__}: {exc}"}
    raise AssertionError(f"negative control unexpectedly passed: {label}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--organic-root", type=Path, required=True)
    args = parser.parse_args()

    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    organic_root = args.organic_root.resolve()
    contract = load_json(CONTRACT_PATH)
    source, mesh, builder = validate_provider(organic_root, contract)

    expected_mesh = contract["expected_generated_mesh"]
    if len(mesh["vertices"]) != int(expected_mesh["vertices"]) or len(mesh["triangles"]) != int(expected_mesh["triangles"]):
        raise RuntimeError("exact Organic generated mesh count drift")

    family = assemble_family(source, mesh, contract)
    reverse_family = assemble_family(source, mesh, contract, list(reversed(contract["branch_ids"])))
    if family["family_digest"] != reverse_family["family_digest"]:
        raise RuntimeError("family digest depends on branch declaration order")

    expected_partition = contract["expected_partition"]
    for row in family["partitions"]:
        if len(row["branch_region_ids"]) != int(expected_partition["branch_regions"]):
            raise RuntimeError(f"branch-region count drift: {row['branch_id']}")
        if len(row["leaf_region_ids"]) != int(expected_partition["leaf_regions"]):
            raise RuntimeError(f"leaf-region count drift: {row['branch_id']}")
        if row["vertex_count"] != int(expected_partition["vertices"]):
            raise RuntimeError(f"child vertex count drift: {row['branch_id']}")
        if row["triangle_count"] != int(expected_partition["triangles"]):
            raise RuntimeError(f"child triangle count drift: {row['branch_id']}")
        if row["fixed_vertex_count"] != int(expected_partition["fixed_vertices"]):
            raise RuntimeError(f"fixed vertex count drift: {row['branch_id']}")
        if row["deformation_tested"] or row["rigging_authorized"] or row["source_authorized"]:
            raise RuntimeError("partition family attempted authority expansion")

    witness = contract["rigging_receiver_witness"]
    north_top = next(row for row in family["partitions"] if row["branch_id"] == witness["branch_id"])
    if north_top["vertex_count"] != int(witness["selected_vertices"]) or north_top["triangle_count"] != int(witness["selected_triangles"]):
        raise RuntimeError("north-top partition no longer reproduces exact Rigging receiver witness counts")

    controls = []
    drift_head = copy.deepcopy(contract)
    drift_head["organic_provider"]["ref"] = "0" * 40
    controls.append(expect_rejection("organic-provider-head-drift", lambda: validate_provider(organic_root, drift_head)))

    drift_source_blob = copy.deepcopy(contract)
    drift_source_blob["organic_provider"]["source_blob"] = "0" * 40
    controls.append(expect_rejection("organic-source-blob-drift", lambda: validate_provider(organic_root, drift_source_blob)))

    drift_builder_blob = copy.deepcopy(contract)
    drift_builder_blob["organic_provider"]["builder_blob"] = "0" * 40
    controls.append(expect_rejection("organic-builder-blob-drift", lambda: validate_provider(organic_root, drift_builder_blob)))

    drift_mesh = copy.deepcopy(contract)
    drift_mesh["organic_provider"]["generated_mesh_digest"] = "0" * 64
    controls.append(expect_rejection("organic-generated-mesh-drift", lambda: validate_provider(organic_root, drift_mesh)))

    duplicate_ids = list(contract["branch_ids"])
    duplicate_ids[-1] = duplicate_ids[0]
    controls.append(expect_rejection("duplicate-branch-selector", lambda: assemble_family(source, mesh, contract, duplicate_ids)))

    controls.append(expect_rejection("unknown-branch-selector", lambda: derive_partition(source, mesh, contract, "unknown-branch")))

    adoption = copy.deepcopy(contract)
    adoption["automatic_rigging_adoption"] = True
    controls.append(expect_rejection("automatic-rigging-adoption", lambda: validate_contract(adoption)))

    promoted_source = copy.deepcopy(source)
    next(zone for zone in promoted_source["flex_zones"] if zone["id"] == "north-top-branch-flex")["status"] = "DEFORMATION_READY"
    controls.append(expect_rejection("flex-status-promotion", lambda: derive_partition(promoted_source, mesh, contract, "north-top")))

    off_root_source = copy.deepcopy(source)
    next(zone for zone in off_root_source["flex_zones"] if zone["id"] == "north-top-branch-flex")["center"][0] += 0.001
    controls.append(expect_rejection("off-root-flex-center", lambda: derive_partition(off_root_source, mesh, contract, "north-top")))

    region_drift_mesh = copy.deepcopy(mesh)
    region_drift_mesh["regions"] = [row for row in region_drift_mesh["regions"] if row["id"] != "leaf:north-top-leaves:3"]
    controls.append(expect_rejection("generated-region-identity-drift", lambda: derive_partition(source, region_drift_mesh, contract, "north-top")))

    partition_digests = [row["partition_digest"] for row in family["partitions"]]
    vertex_index_digests = [row["vertex_index_digest"] for row in family["partitions"]]
    summary = {
        "schema": "axm.nature-branch-child-partition-family-evidence/v0.1",
        "state": PASS_STATE,
        "decision": DECISION,
        "procedural_head": git_head(ROOT),
        "organic_provider_head": contract["organic_provider"]["ref"],
        "organic_source_blob": contract["organic_provider"]["source_blob"],
        "organic_builder_blob": contract["organic_provider"]["builder_blob"],
        "organic_source_digest": builder.digest(source),
        "organic_generated_mesh_digest": builder.digest(mesh),
        "generated_vertices": len(mesh["vertices"]),
        "generated_triangles": len(mesh["triangles"]),
        "branch_count": family["branch_count"],
        "partition_count": len(family["partitions"]),
        "distinct_partition_digest_count": len(set(partition_digests)),
        "distinct_vertex_index_digest_count": len(set(vertex_index_digests)),
        "pairwise_vertex_disjoint": family["pairwise_vertex_disjoint"],
        "partitions": family["partitions"],
        "family_digest": family["family_digest"],
        "reverse_order_family_digest": reverse_family["family_digest"],
        "rigging_receiver_witness": witness,
        "failure_controls": controls,
        "all_failure_controls_rejected": all(row["rejected"] for row in controls),
        "truth_boundary": contract["truth_boundary"],
    }
    write_json(out / "summary.json", summary)
    write_json(out / "family.json", family)
    write_json(out / "contract.json", contract)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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

from axm_nature_design.branch_partition_family import assemble_family as assemble_partition_family
from axm_nature_design.branch_partition_family import validate_contract as validate_partition_contract
from axm_nature_design.branch_subset_family import (
    assemble_subset_family,
    compose_subset,
    validate_contract as validate_subset_contract,
)

PARTITION_CONTRACT_PATH = ROOT / "examples" / "rear_tree_branch_child_partition_family_001.json"
SUBSET_CONTRACT_PATH = ROOT / "examples" / "rear_tree_branch_child_subset_family_001.json"
PASS_STATE = "PASS_NATURE_BRANCH_CHILD_SUBSET_COMPOSITION_FAMILY"
DECISION = "PASS_DERIVED_PARTITION_SUBSETS_ONLY__NO_SOURCE_KINEMATIC_MOTION_VFX_RUNTIME_OR_DOWNSTREAM_ADOPTION"


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
    spec = importlib.util.spec_from_file_location("axm_exact_organic_form_subset_provider", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load exact Organic form builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_provider(organic_root: Path, partition_contract: dict):
    validate_partition_contract(partition_contract)
    provider = partition_contract["organic_provider"]
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
    partition_contract = load_json(PARTITION_CONTRACT_PATH)
    subset_contract = load_json(SUBSET_CONTRACT_PATH)
    validate_subset_contract(subset_contract)

    if subset_contract["authorized_branch_ids"] != partition_contract["branch_ids"]:
        raise RuntimeError("subset authorized branch order drift from exact Procedural partition owner")
    source, mesh, builder = validate_provider(organic_root, partition_contract)
    if len(mesh["vertices"]) != int(subset_contract["total_vertices"]):
        raise RuntimeError("subset receiver total vertex count drift")

    partition_family = assemble_partition_family(source, mesh, partition_contract)
    if partition_family["family_digest"] != subset_contract["expected_partition_family_digest"]:
        raise RuntimeError("exact retained Procedural partition family digest drift")

    family = assemble_subset_family(partition_family, subset_contract)
    reverse_specs = [copy.deepcopy(spec) for spec in reversed(subset_contract["subset_specs"])]
    for spec in reverse_specs:
        spec["branch_ids"] = list(reversed(spec["branch_ids"]))
    reverse_family = assemble_subset_family(partition_family, subset_contract, reverse_specs)
    if family["family_digest"] != reverse_family["family_digest"]:
        raise RuntimeError("subset family digest depends on declaration or selector order")

    expected_outputs = subset_contract["expected_outputs"]
    observed = {row["subset_id"]: row for row in family["outputs"]}
    if set(observed) != set(expected_outputs):
        raise RuntimeError("retained subset identity set drift")
    for subset_id, expected in expected_outputs.items():
        row = observed[subset_id]
        if len(row["branch_ids"]) != int(expected["branches"]):
            raise RuntimeError(f"branch count drift: {subset_id}")
        if row["vertex_count"] != int(expected["vertices"]):
            raise RuntimeError(f"vertex count drift: {subset_id}")
        if row["triangle_count"] != int(expected["triangles"]):
            raise RuntimeError(f"triangle count drift: {subset_id}")
        if row["fixed_vertex_count"] != int(expected["fixed_vertices"]):
            raise RuntimeError(f"fixed vertex count drift: {subset_id}")
        if any(row[key] for key in (
            "source_authorized", "rigging_authorized", "animation_authorized", "vfx_authorized", "runtime_authorized"
        )):
            raise RuntimeError("subset family attempted authority expansion")

    if len({row["vertex_count"] for row in family["outputs"]}) < 3:
        raise RuntimeError("retained outputs are not materially different in selected geometry size")
    if len({row["selection_digest"] for row in family["outputs"]}) != len(family["outputs"]):
        raise RuntimeError("retained outputs collapsed to duplicate selections")

    controls = []
    digest_drift = copy.deepcopy(subset_contract)
    digest_drift["expected_partition_family_digest"] = "0" * 64
    controls.append(expect_rejection(
        "partition-family-digest-drift",
        lambda: compose_subset(partition_family, digest_drift, digest_drift["subset_specs"][0]),
    ))

    unknown = copy.deepcopy(subset_contract)
    unknown["subset_specs"][0]["branch_ids"] = ["unknown-branch"]
    controls.append(expect_rejection("unknown-branch-selector", lambda: validate_subset_contract(unknown)))

    duplicate = copy.deepcopy(subset_contract)
    duplicate["subset_specs"][0]["branch_ids"] = ["south-low", "south-low"]
    controls.append(expect_rejection("duplicate-branch-selector", lambda: validate_subset_contract(duplicate)))

    empty = copy.deepcopy(subset_contract)
    empty["subset_specs"][0]["branch_ids"] = []
    controls.append(expect_rejection("empty-subset", lambda: validate_subset_contract(empty)))

    duplicate_selection = copy.deepcopy(subset_contract)
    duplicate_selection["subset_specs"][1]["branch_ids"] = ["south-low"]
    controls.append(expect_rejection("duplicate-material-selection", lambda: validate_subset_contract(duplicate_selection)))

    total_vertex_drift = copy.deepcopy(subset_contract)
    total_vertex_drift["total_vertices"] = 200
    controls.append(expect_rejection(
        "total-vertex-count-drift",
        lambda: compose_subset(partition_family, total_vertex_drift, total_vertex_drift["subset_specs"][-1]),
    ))

    overlap_family = copy.deepcopy(partition_family)
    a = next(row for row in overlap_family["partitions"] if row["branch_id"] == "south-low")
    b = next(row for row in overlap_family["partitions"] if row["branch_id"] == "north-low")
    b["vertex_indices"][0] = a["vertex_indices"][0]
    controls.append(expect_rejection(
        "selected-partition-vertex-overlap",
        lambda: compose_subset(overlap_family, subset_contract, subset_contract["subset_specs"][1]),
    ))

    for key in (
        "source_mutation_authorized",
        "automatic_rigging_adoption",
        "automatic_animation_adoption",
        "automatic_vfx_adoption",
        "automatic_runtime_adoption",
    ):
        promoted = copy.deepcopy(subset_contract)
        promoted[key] = True
        controls.append(expect_rejection(f"authority-expansion-{key}", lambda value=promoted: validate_subset_contract(value)))

    summary = {
        "schema": "axm.nature-branch-child-subset-family-evidence/v0.1",
        "state": PASS_STATE,
        "decision": DECISION,
        "procedural_head": git_head(ROOT),
        "organic_provider_head": partition_contract["organic_provider"]["ref"],
        "organic_source_digest": builder.digest(source),
        "organic_generated_mesh_digest": builder.digest(mesh),
        "partition_family_digest": partition_family["family_digest"],
        "subset_family_digest": family["family_digest"],
        "reverse_order_subset_family_digest": reverse_family["family_digest"],
        "output_count": family["output_count"],
        "outputs": family["outputs"],
        "distinct_selection_digest_count": len({row["selection_digest"] for row in family["outputs"]}),
        "distinct_vertex_index_digest_count": len({row["vertex_index_digest"] for row in family["outputs"]}),
        "failure_controls": controls,
        "all_failure_controls_rejected": all(row["rejected"] for row in controls),
        "truth_boundary": subset_contract["truth_boundary"],
    }
    write_json(out / "summary.json", summary)
    write_json(out / "subset_family.json", family)
    write_json(out / "subset_contract.json", subset_contract)
    write_json(out / "partition_family.json", partition_family)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

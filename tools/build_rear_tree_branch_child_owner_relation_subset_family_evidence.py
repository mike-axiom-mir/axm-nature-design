#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from axm_nature_design.branch_relation_subset_family import (
    assemble_relation_family,
    validate_contract,
)

CONTRACT_PATH = ROOT / "examples" / "rear_tree_branch_child_owner_relation_subset_family_001.json"
PARTITION_BUILDER = ROOT / "tools" / "build_rear_tree_branch_child_partition_family_evidence.py"
PASS_STATE = "PASS_BOUNDED_OWNER_RELATION_BRANCH_SUBSET_FAMILY"
DECISION = "PASS_DERIVED_OWNER_RELATION_SUBSETS_ONLY__NO_SOURCE_RIGGING_WEIGHT_MOTION_OR_DOWNSTREAM_ADOPTION"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_head(root: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def git_blob(root: Path, relpath: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", f"HEAD:{relpath}"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def validate_owner_checkout(owner_root: Path, contract: dict) -> None:
    owner = contract["organic_owner"]
    if git_head(owner_root) != owner["head"]:
        raise ValueError("Organic interaction owner head drift")
    if git_blob(owner_root, owner["classifier_path"]) != owner["classifier_blob"]:
        raise ValueError("Organic interaction classifier blob drift")
    if git_blob(owner_root, owner["source_path"]) != owner["source_blob"]:
        raise ValueError("Organic source blob drift at interaction owner head")


def build_owner_report(owner_root: Path, contract: dict) -> dict:
    validate_owner_checkout(owner_root, contract)
    source_path = contract["organic_owner"]["source_path"]
    script = r'''
import json
import sys
from pathlib import Path
root = Path(sys.argv[1]).resolve()
source_path = sys.argv[2]
sys.path.insert(0, str(root / "src"))
from axm_nature_design.rear_tree_flex_interaction_classification import evaluate
source = json.loads((root / source_path).read_text(encoding="utf-8"))
print(json.dumps(evaluate(source), sort_keys=True))
'''
    result = subprocess.run(
        [sys.executable, "-c", script, str(owner_root), source_path],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def build_partition_family(partition_organic_root: Path, output_root: Path) -> dict:
    subprocess.run(
        [
            sys.executable,
            str(PARTITION_BUILDER),
            str(output_root),
            "--organic-root",
            str(partition_organic_root),
        ],
        check=True,
    )
    return load_json(output_root / "family.json")


def expect_rejection(label: str, action) -> dict:
    try:
        action()
    except Exception as exc:
        return {"label": label, "rejected": True, "error": f"{type(exc).__name__}: {exc}"}
    raise AssertionError(f"negative control unexpectedly passed: {label}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--partition-organic-root", type=Path, required=True)
    parser.add_argument("--owner-organic-root", type=Path, required=True)
    args = parser.parse_args()

    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    contract = load_json(CONTRACT_PATH)
    validate_contract(contract)

    partition_root = args.partition_organic_root.resolve()
    owner_root = args.owner_organic_root.resolve()
    with tempfile.TemporaryDirectory(prefix="axm-partition-evidence-") as temp_dir:
        partition_family = build_partition_family(partition_root, Path(temp_dir))

    if partition_family.get("family_digest") != contract["expected_partition_family_digest"]:
        raise RuntimeError("exact predecessor partition-family digest drift")

    owner_report = build_owner_report(owner_root, contract)
    family = assemble_relation_family(partition_family, owner_report, contract)

    reverse_report = copy.deepcopy(owner_report)
    reverse_report["pairs"] = list(reversed(reverse_report["pairs"]))
    reverse_contract = copy.deepcopy(contract)
    reverse_contract["output_specs"] = list(reversed(reverse_contract["output_specs"]))
    reverse_family = assemble_relation_family(partition_family, reverse_report, reverse_contract)
    if family["family_digest"] != reverse_family["family_digest"]:
        raise RuntimeError("owner relation family identity depends on declaration or report row order")

    outputs = {row["subset_id"]: row for row in family["outputs"]}
    expected_counts = {
        "neutral-attachment-intersecting": (52, 72, 338),
        "declared-overlap-neutral-disjoint": (52, 72, 338),
        "neutral-attachment-disjoint": (208, 288, 182),
    }
    for output_id, counts in expected_counts.items():
        row = outputs.get(output_id)
        if row is None:
            raise RuntimeError(f"missing retained owner-relation output: {output_id}")
        if (row["vertex_count"], row["triangle_count"], row["fixed_vertex_count"]) != counts:
            raise RuntimeError(f"material output count drift: {output_id}")
        if row["source_authorized"] or row["rigging_authorized"] or row["production_weight_authorized"]:
            raise RuntimeError("owner-relation subset attempted authority expansion")

    if len({row["selection_digest"] for row in family["outputs"]}) != 3:
        raise RuntimeError("retained owner-relation outputs are not materially distinct selections")
    if len({row["vertex_index_digest"] for row in family["outputs"]}) != 3:
        raise RuntimeError("retained owner-relation outputs are not materially distinct vertex identities")

    controls = []
    bad_owner_head = copy.deepcopy(contract)
    bad_owner_head["organic_owner"]["head"] = "0" * 40
    controls.append(expect_rejection("organic-owner-head-drift", lambda: validate_owner_checkout(owner_root, bad_owner_head)))

    bad_classifier = copy.deepcopy(contract)
    bad_classifier["organic_owner"]["classifier_blob"] = "0" * 40
    controls.append(expect_rejection("organic-classifier-blob-drift", lambda: validate_owner_checkout(owner_root, bad_classifier)))

    bad_source = copy.deepcopy(contract)
    bad_source["organic_owner"]["source_blob"] = "0" * 40
    controls.append(expect_rejection("organic-source-blob-drift", lambda: validate_owner_checkout(owner_root, bad_source)))

    bad_state = copy.deepcopy(owner_report)
    bad_state["state"] = "FAIL_NEUTRAL_BRANCH_ROOT_SUPPORT"
    controls.append(expect_rejection("owner-report-state-drift", lambda: assemble_relation_family(partition_family, bad_state, contract)))

    bad_pair_count = copy.deepcopy(owner_report)
    bad_pair_count["pairs"].pop()
    bad_pair_count["pair_count"] -= 1
    controls.append(expect_rejection("owner-pair-count-drift", lambda: assemble_relation_family(partition_family, bad_pair_count, contract)))

    changed_relation = copy.deepcopy(owner_report)
    for row in changed_relation["pairs"]:
        if row["branch_id"] == "north-low" and row["trunk_flex_zone_id"] == "trunk-upper-flex":
            row["trunk_flex_intersects_neutral_attachment_cross_section"] = True
    controls.append(expect_rejection("owner-relation-selection-drift", lambda: assemble_relation_family(partition_family, changed_relation, contract)))

    bad_partition = copy.deepcopy(partition_family)
    bad_partition["family_digest"] = "0" * 64
    controls.append(expect_rejection("partition-family-digest-drift", lambda: assemble_relation_family(bad_partition, owner_report, contract)))

    weight_promotion = copy.deepcopy(contract)
    weight_promotion["production_weight_authorized"] = True
    controls.append(expect_rejection("production-weight-authority-promotion", lambda: validate_contract(weight_promotion)))

    rig_promotion = copy.deepcopy(contract)
    rig_promotion["automatic_rigging_adoption"] = True
    controls.append(expect_rejection("automatic-rigging-adoption", lambda: validate_contract(rig_promotion)))

    widened_truth = copy.deepcopy(owner_report)
    widened_truth["truth_boundary"]["hierarchy_or_weighting_inferred"] = True
    controls.append(expect_rejection("owner-hierarchy-truth-boundary-promotion", lambda: assemble_relation_family(partition_family, widened_truth, contract)))

    summary = {
        "schema": "axm.nature-branch-child-owner-relation-subset-family-evidence/v0.1",
        "state": PASS_STATE,
        "decision": DECISION,
        "procedural_head": git_head(ROOT),
        "partition_organic_head": git_head(partition_root),
        "organic_interaction_owner_head": git_head(owner_root),
        "organic_interaction_classifier_blob": contract["organic_owner"]["classifier_blob"],
        "organic_source_blob": contract["organic_owner"]["source_blob"],
        "organic_source_digest": contract["organic_owner"]["source_digest"],
        "owner_report_state": owner_report["state"],
        "owner_pair_count": owner_report["pair_count"],
        "owner_attachment_intersection_pair_count": owner_report["neutral_attachment_cross_section_intersection_pair_count"],
        "partition_family_digest": partition_family["family_digest"],
        "output_count": family["output_count"],
        "outputs": family["outputs"],
        "distinct_selection_digest_count": len({row["selection_digest"] for row in family["outputs"]}),
        "distinct_vertex_index_digest_count": len({row["vertex_index_digest"] for row in family["outputs"]}),
        "family_digest": family["family_digest"],
        "reverse_order_family_digest": reverse_family["family_digest"],
        "failure_controls": controls,
        "all_failure_controls_rejected": all(row["rejected"] for row in controls),
        "truth_boundary": contract["truth_boundary"],
    }
    write_json(out / "summary.json", summary)
    write_json(out / "family.json", family)
    write_json(out / "owner_report.json", owner_report)
    write_json(out / "partition_family.json", partition_family)
    write_json(out / "contract.json", contract)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

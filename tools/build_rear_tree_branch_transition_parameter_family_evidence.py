#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from axm_nature_design.branch_transition_parameter_family import (
    assemble_transition_parameter_family,
    validate_contract,
)

CONTRACT_PATH = ROOT / "examples" / "rear_tree_branch_transition_parameter_family_001.json"
PASS_STATE = "PASS_BOUNDED_OWNER_TRANSITION_PARAMETER_FAMILY"
DECISION = "PASS_DERIVED_OWNER_TRANSITION_PARAMETER_WINDOWS__NO_JUNCTION_RIGGING_WEIGHT_OR_DOWNSTREAM_ADOPTION"
EVIDENCE_TOLERANCE = 1e-12


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_head(root: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


def git_blob(root: Path, relpath: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", f"HEAD:{relpath}"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


def validate_owner_checkout(owner_root: Path, contract: dict) -> None:
    owner = contract["organic_owner"]
    if git_head(owner_root) != owner["head"]:
        raise ValueError("Organic transition owner head drift")
    if git_blob(owner_root, owner["observer_path"]) != owner["observer_blob"]:
        raise ValueError("Organic transition observer blob drift")
    if git_blob(owner_root, owner["source_path"]) != owner["source_blob"]:
        raise ValueError("Organic transition source blob drift")


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
from axm_nature_design.rear_tree_root_transition_readiness import evaluate
source = json.loads((root / source_path).read_text(encoding="utf-8"))
print(json.dumps(evaluate(source), sort_keys=True))
'''
    result = subprocess.run(
        [sys.executable, "-c", script, str(owner_root), source_path],
        check=True, capture_output=True, text=True,
    )
    return json.loads(result.stdout)


def expect_rejection(label: str, action) -> dict:
    try:
        action()
    except Exception as exc:
        return {"label": label, "rejected": True, "error": f"{type(exc).__name__}: {exc}"}
    raise AssertionError(f"negative control unexpectedly passed: {label}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--owner-organic-root", type=Path, required=True)
    args = parser.parse_args()

    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    contract = load_json(CONTRACT_PATH)
    validate_contract(contract)

    owner_root = args.owner_organic_root.resolve()
    owner_report = build_owner_report(owner_root, contract)
    family = assemble_transition_parameter_family(owner_report, contract)

    reversed_report = copy.deepcopy(owner_report)
    reversed_report["branches"] = list(reversed(reversed_report["branches"]))
    reversed_contract = copy.deepcopy(contract)
    reversed_contract["authorized_branch_ids"] = list(reversed(reversed_contract["authorized_branch_ids"]))
    reverse_family = assemble_transition_parameter_family(reversed_report, reversed_contract)
    if family["family_digest"] != reverse_family["family_digest"]:
        raise RuntimeError("transition parameter family identity depends on owner/declaration order")

    outputs = {row["branch_id"]: row for row in family["outputs"]}
    for branch_id, expected in contract["expected_transitions"].items():
        row = outputs.get(branch_id)
        if row is None:
            raise RuntimeError(f"missing retained transition output: {branch_id}")
        if abs(row["transition_length_m"] - expected["embedded_length_along_first_segment_m"]) > EVIDENCE_TOLERANCE:
            raise RuntimeError(f"retained transition length drift: {branch_id}")
        if abs(row["transition_u_max"] - expected["embedded_fraction_of_first_segment"]) > EVIDENCE_TOLERANCE:
            raise RuntimeError(f"retained transition fraction drift: {branch_id}")
        if row["sample_u"][0] != 0.0 or row["sample_u"][-1] != row["transition_u_max"]:
            raise RuntimeError(f"transition sampling anchors drift: {branch_id}")
        if any((
            row["source_authorized"],
            row["junction_strategy_authorized"],
            row["connected_topology_claim_authorized"],
            row["rigging_authorized"],
            row["production_weight_authorized"],
            row["downstream_adoption_authorized"],
        )):
            raise RuntimeError("transition parameter output attempted authority expansion")

    if len({row["parameter_digest"] for row in family["outputs"]}) != 5:
        raise RuntimeError("five owner branch transition outputs are not materially distinct")
    if len({row["transition_length_m"] for row in family["outputs"]}) != 5:
        raise RuntimeError("five owner branch transition lengths are not materially distinct")
    if len({row["transition_u_max"] for row in family["outputs"]}) != 5:
        raise RuntimeError("five owner branch normalized windows are not materially distinct")

    controls = []
    bad_head = copy.deepcopy(contract)
    bad_head["organic_owner"]["head"] = "0" * 40
    controls.append(expect_rejection("organic-owner-head-drift", lambda: validate_owner_checkout(owner_root, bad_head)))

    bad_observer = copy.deepcopy(contract)
    bad_observer["organic_owner"]["observer_blob"] = "0" * 40
    controls.append(expect_rejection("organic-observer-blob-drift", lambda: validate_owner_checkout(owner_root, bad_observer)))

    bad_source = copy.deepcopy(contract)
    bad_source["organic_owner"]["source_blob"] = "0" * 40
    controls.append(expect_rejection("organic-source-blob-drift", lambda: validate_owner_checkout(owner_root, bad_source)))

    bad_state = copy.deepcopy(owner_report)
    bad_state["state"] = "FAIL_NEUTRAL_BRANCH_ROOT_SUPPORT"
    controls.append(expect_rejection("owner-report-state-drift", lambda: assemble_transition_parameter_family(bad_state, contract)))

    missing_branch = copy.deepcopy(owner_report)
    missing_branch["branches"].pop()
    missing_branch["branch_count"] -= 1
    controls.append(expect_rejection("owner-branch-count-drift", lambda: assemble_transition_parameter_family(missing_branch, contract)))

    length_drift = copy.deepcopy(owner_report)
    length_drift["branches"][0]["embedded_length_along_first_segment_m"] += 0.001
    controls.append(expect_rejection("owner-transition-length-drift", lambda: assemble_transition_parameter_family(length_drift, contract)))

    fraction_drift = copy.deepcopy(owner_report)
    fraction_drift["branches"][1]["embedded_fraction_of_first_segment"] += 0.01
    controls.append(expect_rejection("owner-transition-fraction-drift", lambda: assemble_transition_parameter_family(fraction_drift, contract)))

    topology_promotion = copy.deepcopy(owner_report)
    topology_promotion["truth_boundary"]["connected_branch_trunk_topology_proven"] = True
    controls.append(expect_rejection("connected-topology-promotion", lambda: assemble_transition_parameter_family(topology_promotion, contract)))

    junction_promotion = copy.deepcopy(owner_report)
    junction_promotion["handoff"]["junction_strategy_selected"] = True
    controls.append(expect_rejection("junction-strategy-promotion", lambda: assemble_transition_parameter_family(junction_promotion, contract)))

    rig_promotion = copy.deepcopy(contract)
    rig_promotion["automatic_rigging_adoption"] = True
    controls.append(expect_rejection("automatic-rigging-adoption", lambda: validate_contract(rig_promotion)))

    weight_promotion = copy.deepcopy(contract)
    weight_promotion["production_weight_authorized"] = True
    controls.append(expect_rejection("production-weight-authority-promotion", lambda: validate_contract(weight_promotion)))

    summary = {
        "schema": "axm.nature-branch-transition-parameter-family-evidence/v0.1",
        "state": PASS_STATE,
        "decision": DECISION,
        "procedural_head": git_head(ROOT),
        "organic_transition_owner_head": git_head(owner_root),
        "organic_transition_observer_blob": contract["organic_owner"]["observer_blob"],
        "organic_source_blob": contract["organic_owner"]["source_blob"],
        "organic_source_digest": contract["organic_owner"]["source_digest"],
        "owner_report_state": owner_report["state"],
        "owner_branch_count": owner_report["branch_count"],
        "minimum_embedded_length_m": owner_report["minimum_embedded_length_along_first_segment_m"],
        "maximum_embedded_length_m": owner_report["maximum_embedded_length_along_first_segment_m"],
        "output_count": family["output_count"],
        "outputs": family["outputs"],
        "distinct_parameter_digest_count": len({row["parameter_digest"] for row in family["outputs"]}),
        "distinct_transition_length_count": len({row["transition_length_m"] for row in family["outputs"]}),
        "distinct_transition_fraction_count": len({row["transition_u_max"] for row in family["outputs"]}),
        "family_digest": family["family_digest"],
        "reverse_order_family_digest": reverse_family["family_digest"],
        "failure_controls": controls,
        "all_failure_controls_rejected": all(row["rejected"] for row in controls),
        "truth_boundary": contract["truth_boundary"],
    }
    write_json(out / "summary.json", summary)
    write_json(out / "family.json", family)
    write_json(out / "owner_report.json", owner_report)
    write_json(out / "contract.json", contract)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

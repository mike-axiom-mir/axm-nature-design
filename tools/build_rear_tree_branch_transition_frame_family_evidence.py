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

from axm_nature_design.branch_transition_frame_family import (
    assemble_transition_frame_family,
    validate_contract,
)
from axm_nature_design.branch_transition_parameter_family import assemble_transition_parameter_family

CONTRACT_PATH = ROOT / "examples" / "rear_tree_branch_transition_frame_family_001.json"
PREDECESSOR_CONTRACT_PATH = ROOT / "examples" / "rear_tree_branch_transition_parameter_family_001.json"
PASS_STATE = "PASS_BOUNDED_OWNER_TRANSITION_FRAME_PARAMETER_FAMILY"
DECISION = (
    "PASS_DERIVED_OWNER_EXIT_FRAME_PARAMETERS__PREDECESSOR_SCALAR_FAMILY_PRESERVED__"
    "NO_WELD_SURFACE_NORMAL_RIGGING_WEIGHT_OR_DOWNSTREAM_ADOPTION"
)


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
        raise ValueError("Organic transition-frame owner head drift")
    if git_blob(owner_root, owner["frame_observer_path"]) != owner["frame_observer_blob"]:
        raise ValueError("Organic transition-frame observer blob drift")
    if git_blob(owner_root, owner["transition_observer_path"]) != owner["transition_observer_blob"]:
        raise ValueError("Organic transition observer blob drift")
    if git_blob(owner_root, owner["source_path"]) != owner["source_blob"]:
        raise ValueError("Organic source blob drift")


def build_owner_reports(owner_root: Path, contract: dict) -> tuple[dict, dict]:
    validate_owner_checkout(owner_root, contract)
    source_path = contract["organic_owner"]["source_path"]
    script = r'''
import json
import sys
from pathlib import Path
root = Path(sys.argv[1]).resolve()
source_path = sys.argv[2]
sys.path.insert(0, str(root / "src"))
from axm_nature_design.rear_tree_root_transition_readiness import evaluate as evaluate_transitions
from axm_nature_design.rear_tree_transition_exit_frames import evaluate as evaluate_frames
source = json.loads((root / source_path).read_text(encoding="utf-8"))
print(json.dumps({"transition": evaluate_transitions(source), "frames": evaluate_frames(source)}, sort_keys=True))
'''
    result = subprocess.run(
        [sys.executable, "-c", script, str(owner_root), source_path],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    return payload["transition"], payload["frames"]


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
    predecessor_contract = load_json(PREDECESSOR_CONTRACT_PATH)
    validate_contract(contract)

    owner_root = args.owner_organic_root.resolve()
    transition_report, frame_report = build_owner_reports(owner_root, contract)

    predecessor_family = assemble_transition_parameter_family(transition_report, predecessor_contract)
    if predecessor_family["family_digest"] != contract["predecessor_transition_family_digest"]:
        raise RuntimeError("predecessor scalar transition family no longer reproduces its retained digest")

    family = assemble_transition_frame_family(frame_report, contract)

    reverse_report = copy.deepcopy(frame_report)
    reverse_report["frames"] = list(reversed(reverse_report["frames"]))
    reverse_contract = copy.deepcopy(contract)
    reverse_contract["authorized_branch_ids"] = list(reversed(reverse_contract["authorized_branch_ids"]))
    reverse_family = assemble_transition_frame_family(reverse_report, reverse_contract)
    if family["family_digest"] != reverse_family["family_digest"]:
        raise RuntimeError("transition frame family identity depends on owner/declaration order")

    outputs = {row["branch_id"]: row for row in family["outputs"]}
    for branch_id, expected in contract["expected_transitions"].items():
        row = outputs.get(branch_id)
        if row is None:
            raise RuntimeError(f"missing retained transition frame output: {branch_id}")
        if abs(row["transition_u"] - expected["transition_u"]) > 1e-12:
            raise RuntimeError(f"retained transition u drift: {branch_id}")
        if abs(row["transition_length_m"] - expected["transition_length_m"]) > 1e-12:
            raise RuntimeError(f"retained transition length drift: {branch_id}")
        matrix = row["local_to_source_matrix_4x4_column_basis"]
        if len(matrix) != 4 or any(len(matrix_row) != 4 for matrix_row in matrix):
            raise RuntimeError(f"transition frame matrix shape drift: {branch_id}")
        if matrix[3] != [0.0, 0.0, 0.0, 1.0]:
            raise RuntimeError(f"transition frame homogeneous row drift: {branch_id}")
        if any((
            row["source_authorized"],
            row["junction_strategy_authorized"],
            row["weld_ring_authorized"],
            row["surface_normal_authorized"],
            row["connected_topology_claim_authorized"],
            row["rigging_authorized"],
            row["production_weight_authorized"],
            row["downstream_adoption_authorized"],
        )):
            raise RuntimeError("transition frame output attempted authority expansion")

    distinct_parameter_digests = len({row["parameter_digest"] for row in family["outputs"]})
    distinct_origin_digests = len({row["origin_digest"] for row in family["outputs"]})
    distinct_basis_digests = len({row["basis_digest"] for row in family["outputs"]})
    if min(distinct_parameter_digests, distinct_origin_digests, distinct_basis_digests) < 3:
        raise RuntimeError("transition frame family lacks three materially different outputs")

    controls = []
    bad_head = copy.deepcopy(contract)
    bad_head["organic_owner"]["head"] = "0" * 40
    controls.append(expect_rejection("organic-owner-head-drift", lambda: validate_owner_checkout(owner_root, bad_head)))

    bad_frame_blob = copy.deepcopy(contract)
    bad_frame_blob["organic_owner"]["frame_observer_blob"] = "0" * 40
    controls.append(expect_rejection("organic-frame-observer-blob-drift", lambda: validate_owner_checkout(owner_root, bad_frame_blob)))

    bad_transition_blob = copy.deepcopy(contract)
    bad_transition_blob["organic_owner"]["transition_observer_blob"] = "0" * 40
    controls.append(expect_rejection("organic-transition-observer-blob-drift", lambda: validate_owner_checkout(owner_root, bad_transition_blob)))

    bad_source = copy.deepcopy(contract)
    bad_source["organic_owner"]["source_blob"] = "0" * 40
    controls.append(expect_rejection("organic-source-blob-drift", lambda: validate_owner_checkout(owner_root, bad_source)))

    bad_predecessor = copy.deepcopy(contract)
    bad_predecessor["predecessor_transition_family_digest"] = "0" * 64
    controls.append(expect_rejection(
        "predecessor-scalar-family-digest-drift",
        lambda: (
            None
            if predecessor_family["family_digest"] == bad_predecessor["predecessor_transition_family_digest"]
            else (_ for _ in ()).throw(ValueError("predecessor scalar family digest drift"))
        ),
    ))

    bad_state = copy.deepcopy(frame_report)
    bad_state["state"] = "HOLD_FRAME_REVIEW"
    controls.append(expect_rejection("owner-frame-state-drift", lambda: assemble_transition_frame_family(bad_state, contract)))

    missing_frame = copy.deepcopy(frame_report)
    missing_frame["frames"].pop()
    missing_frame["branch_count"] -= 1
    controls.append(expect_rejection("owner-frame-count-drift", lambda: assemble_transition_frame_family(missing_frame, contract)))

    scalar_drift = copy.deepcopy(frame_report)
    scalar_drift["frames"][0]["transition_u"] += 0.001
    controls.append(expect_rejection("predecessor-transition-scalar-drift", lambda: assemble_transition_frame_family(scalar_drift, contract)))

    handedness_drift = copy.deepcopy(frame_report)
    handedness_drift["frames"][0]["exit_azimuth_unit"] = [
        -value for value in handedness_drift["frames"][0]["exit_azimuth_unit"]
    ]
    controls.append(expect_rejection("owner-frame-handedness-drift", lambda: assemble_transition_frame_family(handedness_drift, contract)))

    unit_drift = copy.deepcopy(frame_report)
    unit_drift["frames"][1]["trunk_centerline_to_exit_radial_unit"] = [2.0, 0.0, 0.0]
    controls.append(expect_rejection("owner-frame-unit-length-drift", lambda: assemble_transition_frame_family(unit_drift, contract)))

    flex_promotion = copy.deepcopy(frame_report)
    flex_promotion["frames"][0]["exact_root_flex_zone_status"] = "DEFORMATION_PROVEN"
    controls.append(expect_rejection("owner-flex-status-promotion", lambda: assemble_transition_frame_family(flex_promotion, contract)))

    topology_promotion = copy.deepcopy(frame_report)
    topology_promotion["truth_boundary"]["connected_branch_trunk_topology_proven"] = True
    controls.append(expect_rejection("connected-topology-promotion", lambda: assemble_transition_frame_family(topology_promotion, contract)))

    weld_promotion = copy.deepcopy(contract)
    weld_promotion["weld_ring_authorized"] = True
    controls.append(expect_rejection("weld-ring-authority-promotion", lambda: validate_contract(weld_promotion)))

    surface_normal_promotion = copy.deepcopy(contract)
    surface_normal_promotion["surface_normal_authorized"] = True
    controls.append(expect_rejection("surface-normal-authority-promotion", lambda: validate_contract(surface_normal_promotion)))

    rig_promotion = copy.deepcopy(contract)
    rig_promotion["automatic_rigging_adoption"] = True
    controls.append(expect_rejection("automatic-rigging-adoption", lambda: validate_contract(rig_promotion)))

    summary = {
        "schema": "axm.nature-branch-transition-frame-parameter-family-evidence/v0.1",
        "state": PASS_STATE,
        "decision": DECISION,
        "procedural_head": git_head(ROOT),
        "organic_frame_owner_head": git_head(owner_root),
        "organic_frame_observer_blob": contract["organic_owner"]["frame_observer_blob"],
        "organic_transition_observer_blob": contract["organic_owner"]["transition_observer_blob"],
        "organic_source_blob": contract["organic_owner"]["source_blob"],
        "organic_source_digest": contract["organic_owner"]["source_digest"],
        "owner_frame_state": frame_report["state"],
        "owner_frame_count": frame_report["branch_count"],
        "owner_minimum_departure_angle_deg": frame_report["minimum_departure_angle_deg"],
        "owner_maximum_departure_angle_deg": frame_report["maximum_departure_angle_deg"],
        "predecessor_transition_family_digest": predecessor_family["family_digest"],
        "output_count": family["output_count"],
        "outputs": family["outputs"],
        "distinct_parameter_digest_count": distinct_parameter_digests,
        "distinct_origin_digest_count": distinct_origin_digests,
        "distinct_basis_digest_count": distinct_basis_digests,
        "family_digest": family["family_digest"],
        "reverse_order_family_digest": reverse_family["family_digest"],
        "failure_controls": controls,
        "all_failure_controls_rejected": all(row["rejected"] for row in controls),
        "truth_boundary": contract["truth_boundary"],
    }
    write_json(out / "summary.json", summary)
    write_json(out / "family.json", family)
    write_json(out / "owner_frame_report.json", frame_report)
    write_json(out / "owner_transition_report.json", transition_report)
    write_json(out / "predecessor_transition_family.json", predecessor_family)
    write_json(out / "contract.json", contract)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

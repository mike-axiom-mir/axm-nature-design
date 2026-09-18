#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from axm_nature_design.rear_tree_rigging_primary_branch_family import (
    BRANCH_IDS,
    GEOMETRY_RECEIVER_HEAD,
    PROCEDURAL_DONOR_HEAD,
    RESULT,
    evaluate,
)

SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"
CONTRACT_PATH = ROOT / "contracts" / "east-rear-primary-branch-root-socket-rigging-family-003.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def expect_rejection(label: str, action) -> dict:
    try:
        action()
    except Exception as exc:
        return {"label": label, "rejected": True, "error": f"{type(exc).__name__}: {exc}"}
    raise AssertionError(f"negative control unexpectedly passed: {label}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source = load_json(SOURCE_PATH)
    source_before = copy.deepcopy(source)
    contract = load_json(CONTRACT_PATH)
    evidence = evaluate(source)
    if source != source_before:
        raise RuntimeError("Rigging evaluator mutated Organic source")
    if evidence["result"] != RESULT:
        raise RuntimeError(f"unexpected Rigging result: {evidence['result']}")
    if evidence["lineage"]["geometry_receiver_head"] != GEOMETRY_RECEIVER_HEAD:
        raise RuntimeError("Geometry receiver head drift")
    if evidence["lineage"]["procedural_donor_head"] != PROCEDURAL_DONOR_HEAD:
        raise RuntimeError("Procedural donor head drift")
    if evidence["rigging_family"]["branch_ids"] != list(BRANCH_IDS):
        raise RuntimeError("Rigging branch family identity drift")
    if evidence["rigging_family"]["total_representative_pose_evaluations"] != 25:
        raise RuntimeError("representative pose count drift")
    if not evidence["rigging_family"]["pairwise_child_vertex_disjoint"]:
        raise RuntimeError("primary branch child partitions overlap")
    if not all(evidence["checks"].values()):
        raise RuntimeError("Rigging family checks did not all pass")

    controls = [
        expect_rejection(
            "procedural-donor-head-drift",
            lambda: evaluate(source, requested_procedural_donor_head="0" * 40),
        ),
        expect_rejection(
            "geometry-receiver-head-drift",
            lambda: evaluate(source, requested_geometry_receiver_head="0" * 40),
        ),
        expect_rejection(
            "branch-family-reduction",
            lambda: evaluate(source, requested_branch_ids=BRANCH_IDS[:-1]),
        ),
        expect_rejection(
            "diagnostic-interval-widening",
            lambda: evaluate(source, diagnostic_min_deg=-10.0, diagnostic_max_deg=10.0),
        ),
        expect_rejection(
            "pivot-drift",
            lambda: evaluate(source, joint_pivot_overrides={"east-mid": [-0.009, 0.0, 2.45]}),
        ),
        expect_rejection(
            "source-rom-promotion",
            lambda: evaluate(source, claim_source_rom=True),
        ),
        expect_rejection(
            "procedural-authority-transfer",
            lambda: evaluate(source, claim_procedural_authority_transfer=True),
        ),
        expect_rejection(
            "animation-acceptance-promotion",
            lambda: evaluate(source, claim_animation_acceptance=True),
        ),
        expect_rejection(
            "runtime-acceptance-promotion",
            lambda: evaluate(source, claim_runtime_acceptance=True),
        ),
    ]

    payload = {
        **evidence,
        "contract": contract,
        "failure_controls": controls,
        "all_failure_controls_rejected": all(row["rejected"] for row in controls),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

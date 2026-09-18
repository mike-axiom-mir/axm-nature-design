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

from axm_nature_design.rear_tree_geometry_shared_driver_continuous_clearance import (
    EXPECTED_CROSS_TRIANGLE_PAIR_COUNT,
    HOLD_BUDGET,
    PRIOR_GEOMETRY_HEAD,
    RESULT,
    RIGGING_CONTINUOUS_HEAD,
    SCHEMA,
    SHARED_DRIVER_MAX_DEG,
    SHARED_DRIVER_MIN_DEG,
    evaluate,
)

SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"
CONTRACT_PATH = ROOT / "contracts" / "east-rear-shared-driver-continuous-clearance-003.json"


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
    if contract.get("schema") != SCHEMA:
        raise RuntimeError("continuous Geometry contract schema drift")
    if contract.get("prior_geometry_head") != PRIOR_GEOMETRY_HEAD:
        raise RuntimeError("continuous Geometry contract prior-head drift")
    if contract.get("rigging_continuous_owner_head") != RIGGING_CONTINUOUS_HEAD:
        raise RuntimeError("continuous Geometry contract Rigging-head drift")
    if tuple(float(v) for v in contract.get("shared_driver_interval_deg", [])) != (
        SHARED_DRIVER_MIN_DEG,
        SHARED_DRIVER_MAX_DEG,
    ):
        raise RuntimeError("continuous Geometry contract interval drift")

    evidence = evaluate(source)
    if source != source_before:
        raise RuntimeError("continuous Geometry verifier mutated Organic source")

    budget_hold = evaluate(
        source,
        max_triangle_pair_certificates=EXPECTED_CROSS_TRIANGLE_PAIR_COUNT - 1,
    )
    if budget_hold.get("result") != HOLD_BUDGET:
        raise RuntimeError("insufficient continuous-certificate work budget did not HOLD")
    if budget_hold.get("work", {}).get("triangle_pair_certificates_performed") != 0:
        raise RuntimeError("budget HOLD performed a partial continuous-clearance scan")
    if budget_hold.get("work", {}).get("partial_clearance_verdict_exposed") is not False:
        raise RuntimeError("budget HOLD exposed a partial continuous-clearance verdict")

    controls = [
        expect_rejection(
            "continuous-rigging-head-drift",
            lambda: evaluate(source, requested_rigging_head="0" * 40),
        ),
        expect_rejection(
            "interval-widening",
            lambda: evaluate(source, requested_interval_deg=(-5.0, 5.1)),
        ),
        expect_rejection(
            "child-fixed-receiver-promotion",
            lambda: evaluate(source, claim_child_fixed_receiver_clearance=True),
        ),
        expect_rejection(
            "physical-collision-gameplay-promotion",
            lambda: evaluate(source, claim_physical_collision_or_gameplay=True),
        ),
        expect_rejection(
            "target-host-runtime-promotion",
            lambda: evaluate(source, claim_target_host_or_runtime=True),
        ),
    ]

    payload = {
        **evidence,
        "contract": contract,
        "budget_hold_control": budget_hold,
        "failure_controls": controls,
        "all_failure_controls_rejected": all(row["rejected"] for row in controls),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "result": payload["result"],
                "triangle_pair_trajectories": payload["scope"]["cross_branch_triangle_pair_trajectories"],
                "certificates_performed": payload["measurements"]["triangle_pair_certificates_performed"],
                "uncertified_triangle_pairs": payload["measurements"]["uncertified_triangle_pair_count"],
                "minimum_certified_slack_m": payload["measurements"]["minimum_certified_slack_m"],
                "maximum_full_interval_combined_motion_bound_m": payload["measurements"]["maximum_full_interval_combined_motion_bound_m"],
                "tightest_pair": payload["measurements"]["tightest_pair"],
                "budget_hold_result": budget_hold["result"],
            },
            indent=2,
            sort_keys=True,
        )
    )

    if payload["result"] != RESULT:
        return 2
    if payload["measurements"]["triangle_pair_certificates_performed"] != EXPECTED_CROSS_TRIANGLE_PAIR_COUNT:
        return 3
    if payload["measurements"]["uncertified_triangle_pair_count"] != 0:
        return 4
    if payload["measurements"]["minimum_certified_slack_m"] <= 0.02:
        return 5
    if payload["truth_boundary"]["continuous_cross_branch_separation_proven"] is not True:
        return 6
    if payload["all_failure_controls_rejected"] is not True:
        return 7
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

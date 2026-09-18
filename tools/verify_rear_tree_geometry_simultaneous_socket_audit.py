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

from axm_nature_design.rear_tree_geometry_simultaneous_socket_audit import (
    RIGGING_PARENT_HEAD,
    evaluate,
)

SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"
CONTRACT_PATH = ROOT / "contracts" / "east-rear-simultaneous-primary-branch-geometry-audit-001.json"
UC_HEAD = "ce70d717e381df6ca8a27c0c9fabe9d48bb1b23c"
PAIR_BUDGET = 200_000
EXPECTED_PAIR_CHECKS = 570 * 569 // 2


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
    parser.add_argument("--uc-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    uc_src = args.uc_root / "src"
    observer_path = uc_src / "axm_uc" / "mesh_self_intersection.py"
    if not observer_path.is_file():
        raise RuntimeError(f"missing exact UC observer: {observer_path}")
    sys.path.insert(0, str(uc_src))
    from axm_uc.mesh_self_intersection import inspect_triangle_self_intersections

    source = load_json(SOURCE_PATH)
    source_before = copy.deepcopy(source)
    contract = load_json(CONTRACT_PATH)
    evidence = evaluate(source, include_positions=True)
    if source != source_before:
        raise RuntimeError("Geometry evaluator mutated Organic source")
    if evidence["lineage"]["rigging_parent_head"] != RIGGING_PARENT_HEAD:
        raise RuntimeError("Rigging parent identity drift")
    if evidence["witness_family"]["total_state_count"] != 33:
        raise RuntimeError("simultaneous witness family cardinality drift")

    mesh = __import__(
        "axm_nature_design.organic_form", fromlist=["build_mesh"]
    ).build_mesh(source)
    flat_indices = [int(index) for triangle in mesh["triangles"] for index in triangle]
    if len(flat_indices) != 570 * 3:
        raise RuntimeError("exact receiver triangle stream drift")

    budget_hold = inspect_triangle_self_intersections(
        evidence["witness_family"]["states"][0]["positions"],
        flat_indices,
        max_triangle_pair_checks=EXPECTED_PAIR_CHECKS - 1,
    )
    if budget_hold.get("status") != "HOLD_TRIANGLE_PAIR_BUDGET_EXCEEDED":
        raise RuntimeError("UC self-intersection observer did not fail closed below exact pair budget")
    if budget_hold.get("inspection_complete") is not False:
        raise RuntimeError("budget HOLD was mislabeled complete")
    if budget_hold.get("triangle_pair_checks_performed") != 0:
        raise RuntimeError("budget HOLD performed a partial pair scan")
    if budget_hold.get("self_intersection_pair_count") is not None:
        raise RuntimeError("budget HOLD exposed a partial intersection verdict")

    observed_states = []
    for state in evidence["witness_family"]["states"]:
        positions = state.pop("positions")
        report = inspect_triangle_self_intersections(
            positions,
            flat_indices,
            max_triangle_pair_checks=PAIR_BUDGET,
        )
        if report.get("inspection_complete") is not True:
            raise RuntimeError(f"UC observer incomplete for {state['state_id']}")
        if report.get("triangle_pair_checks_required") != EXPECTED_PAIR_CHECKS:
            raise RuntimeError(f"pair-work identity drift for {state['state_id']}")
        observed_states.append(
            {
                "state_id": state["state_id"],
                "angles_deg": state["angles_deg"],
                "self_intersection_pair_count": report["self_intersection_pair_count"],
                "skipped_topological_neighbor_pairs": report["skipped_topological_neighbor_pairs"],
                "broad_phase_candidate_pairs": report["broad_phase_candidate_pairs"],
                "examples": report["examples"],
            }
        )

    neutral = next(row for row in observed_states if row["state_id"] == "neutral")
    corners = [row for row in observed_states if row["state_id"].startswith("corner-")]
    if len(corners) != 32:
        raise RuntimeError("corner witness count drift")
    neutral_count = int(neutral["self_intersection_pair_count"])
    corner_counts = [int(row["self_intersection_pair_count"]) for row in corners]
    max_corner_count = max(corner_counts)
    states_with_intersections = [
        row["state_id"] for row in observed_states if int(row["self_intersection_pair_count"]) > 0
    ]

    if neutral_count == 0 and max_corner_count == 0:
        observer_result = "PASS_32_EXTREME_CORNERS_NO_NONADJACENT_TRIANGLE_SELF_INTERSECTION"
    else:
        observer_result = "HOLD_BOUNDED_CORNER_WITNESS_INTERSECTION_PRESENT"

    controls = [
        expect_rejection(
            "rigging-parent-head-drift",
            lambda: evaluate(source, requested_rigging_parent_head="0" * 40),
        ),
        expect_rejection(
            "continuous-clearance-promotion",
            lambda: evaluate(source, claim_continuous_deformation_clearance=True),
        ),
        expect_rejection(
            "collision-gameplay-promotion",
            lambda: evaluate(source, claim_collision_or_gameplay=True),
        ),
    ]

    payload = {
        **evidence,
        "contract": contract,
        "uc_observer": {
            "repository": "mike-axiom-mir/axm-universal-creation",
            "commit": UC_HEAD,
            "path": "src/axm_uc/mesh_self_intersection.py",
            "pair_budget": PAIR_BUDGET,
            "exact_pair_checks_per_state": EXPECTED_PAIR_CHECKS,
            "budget_hold_control": budget_hold,
            "result": observer_result,
            "neutral_self_intersection_pair_count": neutral_count,
            "minimum_corner_self_intersection_pair_count": min(corner_counts),
            "maximum_corner_self_intersection_pair_count": max_corner_count,
            "states_with_intersections": states_with_intersections,
            "observed_states": observed_states,
            "continuous_interval_checked": False,
            "collision_or_gameplay_checked": False,
            "repair_or_adoption_authorized": False,
        },
        "failure_controls": controls,
        "all_failure_controls_rejected": all(row["rejected"] for row in controls),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "geometry_result": payload["result"],
        "uc_observer_result": observer_result,
        "neutral_self_intersections": neutral_count,
        "min_corner_self_intersections": min(corner_counts),
        "max_corner_self_intersections": max_corner_count,
        "states_with_intersections": states_with_intersections,
        "triangle_partition": payload["receiver"]["triangle_partition"],
        "max_order_delta_m": payload["witness_family"]["maximum_composition_order_vertex_delta_m"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

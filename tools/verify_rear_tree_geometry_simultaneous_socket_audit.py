#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from axm_nature_design import rear_tree_rigging_primary_branch_family as rig_family
from axm_nature_design.organic_form import build_mesh
from axm_nature_design.rear_tree_geometry_simultaneous_socket_audit import (
    BRANCH_IDS,
    RIGGING_PARENT_HEAD,
    evaluate,
)

SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"
CONTRACT_PATH = ROOT / "contracts" / "east-rear-simultaneous-primary-branch-geometry-audit-001.json"
UC_HEAD = "ce70d717e381df6ca8a27c0c9fabe9d48bb1b23c"
FULL_RECEIVER_PAIR_CHECKS = 570 * 569 // 2
SOLO_TRIANGLES = 72
PAIR_TRIANGLES = 144
SOLO_PAIR_CHECKS = SOLO_TRIANGLES * (SOLO_TRIANGLES - 1) // 2
PAIR_PAIR_CHECKS = PAIR_TRIANGLES * (PAIR_TRIANGLES - 1) // 2
PAIR_BUDGET = 12_000


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def expect_rejection(label: str, action) -> dict:
    try:
        action()
    except Exception as exc:
        return {"label": label, "rejected": True, "error": f"{type(exc).__name__}: {exc}"}
    raise AssertionError(f"negative control unexpectedly passed: {label}")


def flatten_triangles(mesh: dict, triangle_indices: list[int]) -> list[int]:
    return [
        int(vertex_index)
        for triangle_index in triangle_indices
        for vertex_index in mesh["triangles"][triangle_index]
    ]


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
    if evidence["receiver"]["triangle_partition"]["triangle_closed_child_partitions"] is not True:
        raise RuntimeError("cross-branch observer requires triangle-closed child partitions")

    mesh = build_mesh(source)
    flat_full_indices = [int(index) for triangle in mesh["triangles"] for index in triangle]
    if len(flat_full_indices) != 570 * 3:
        raise RuntimeError("exact receiver triangle stream drift")

    # Fail-closed work-budget control on the full receiver.  The full receiver is
    # deliberately NOT used as the simultaneous child-child verdict because this
    # Nature body contains many disconnected components that intentionally meet at
    # authored attachments.  A whole-mesh count cannot separate those baseline
    # contacts from new cross-child contacts.
    budget_hold = inspect_triangle_self_intersections(
        evidence["witness_family"]["states"][0]["positions"],
        flat_full_indices,
        max_triangle_pair_checks=FULL_RECEIVER_PAIR_CHECKS - 1,
    )
    if budget_hold.get("status") != "HOLD_TRIANGLE_PAIR_BUDGET_EXCEEDED":
        raise RuntimeError("UC self-intersection observer did not fail closed below exact pair budget")
    if budget_hold.get("inspection_complete") is not False:
        raise RuntimeError("budget HOLD was mislabeled complete")
    if budget_hold.get("triangle_pair_checks_performed") != 0:
        raise RuntimeError("budget HOLD performed a partial pair scan")
    if budget_hold.get("self_intersection_pair_count") is not None:
        raise RuntimeError("budget HOLD exposed a partial intersection verdict")

    probes = [rig_family._probe_branch(source, mesh, branch_id) for branch_id in BRANCH_IDS]
    selected_sets = {
        probe["branch_id"]: set(int(index) for index in probe["selected_vertex_indices"])
        for probe in probes
    }
    owned_triangles: dict[str, list[int]] = {branch_id: [] for branch_id in BRANCH_IDS}
    for triangle_index, triangle in enumerate(mesh["triangles"]):
        face = set(int(index) for index in triangle)
        owners = [branch_id for branch_id in BRANCH_IDS if face.issubset(selected_sets[branch_id])]
        if len(owners) == 1:
            owned_triangles[owners[0]].append(triangle_index)
    if any(len(indices) != SOLO_TRIANGLES for indices in owned_triangles.values()):
        raise RuntimeError("exact 72-triangle child ownership drift")

    pair_ids = list(itertools.combinations(BRANCH_IDS, 2))
    if len(pair_ids) != 10:
        raise RuntimeError("five-child pair family cardinality drift")

    observed_states = []
    maximum_cross_branch_intersections = 0
    states_with_cross_branch_intersections: list[str] = []
    pair_state_cross_hits: list[dict] = []

    for state in evidence["witness_family"]["states"]:
        positions = state.pop("positions")
        solo_counts: dict[str, int] = {}
        for branch_id in BRANCH_IDS:
            report = inspect_triangle_self_intersections(
                positions,
                flatten_triangles(mesh, owned_triangles[branch_id]),
                max_triangle_pair_checks=PAIR_BUDGET,
            )
            if report.get("inspection_complete") is not True:
                raise RuntimeError(f"UC solo observer incomplete for {state['state_id']} / {branch_id}")
            if report.get("triangle_pair_checks_required") != SOLO_PAIR_CHECKS:
                raise RuntimeError(f"solo pair-work drift for {state['state_id']} / {branch_id}")
            solo_counts[branch_id] = int(report["self_intersection_pair_count"])

        pair_rows = []
        state_cross_total = 0
        for left, right in pair_ids:
            combined_triangle_indices = owned_triangles[left] + owned_triangles[right]
            report = inspect_triangle_self_intersections(
                positions,
                flatten_triangles(mesh, combined_triangle_indices),
                max_triangle_pair_checks=PAIR_BUDGET,
            )
            if report.get("inspection_complete") is not True:
                raise RuntimeError(f"UC pair observer incomplete for {state['state_id']} / {left}+{right}")
            if report.get("triangle_pair_checks_required") != PAIR_PAIR_CHECKS:
                raise RuntimeError(f"combined pair-work drift for {state['state_id']} / {left}+{right}")
            combined_count = int(report["self_intersection_pair_count"])
            cross_count = combined_count - solo_counts[left] - solo_counts[right]
            if cross_count < 0:
                raise RuntimeError("cross-branch subtraction produced an impossible negative count")
            state_cross_total += cross_count
            maximum_cross_branch_intersections = max(maximum_cross_branch_intersections, cross_count)
            if cross_count:
                pair_state_cross_hits.append(
                    {
                        "state_id": state["state_id"],
                        "left": left,
                        "right": right,
                        "cross_branch_intersection_pair_count": cross_count,
                    }
                )
            pair_rows.append(
                {
                    "left": left,
                    "right": right,
                    "left_internal_intersection_pair_count": solo_counts[left],
                    "right_internal_intersection_pair_count": solo_counts[right],
                    "combined_intersection_pair_count": combined_count,
                    "cross_branch_intersection_pair_count": cross_count,
                }
            )

        if state_cross_total:
            states_with_cross_branch_intersections.append(state["state_id"])
        observed_states.append(
            {
                "state_id": state["state_id"],
                "angles_deg": state["angles_deg"],
                "cross_branch_intersection_pair_count_total": state_cross_total,
                "pair_rows": pair_rows,
            }
        )

    if maximum_cross_branch_intersections == 0:
        observer_result = "PASS_33_WITNESSES_NO_CROSS_BRANCH_NONADJACENT_TRIANGLE_INTERSECTION"
    else:
        observer_result = "HOLD_CROSS_BRANCH_INTERSECTION_OBSERVED_IN_BOUNDED_WITNESS_FAMILY"

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
            "method": "PAIRWISE_CHILD_COMBINED_COUNT_MINUS_EXACT_SOLO_COUNTS",
            "full_receiver_pair_checks": FULL_RECEIVER_PAIR_CHECKS,
            "solo_triangle_count": SOLO_TRIANGLES,
            "solo_pair_checks": SOLO_PAIR_CHECKS,
            "combined_child_pair_triangle_count": PAIR_TRIANGLES,
            "combined_child_pair_checks": PAIR_PAIR_CHECKS,
            "pair_budget": PAIR_BUDGET,
            "budget_hold_control": budget_hold,
            "result": observer_result,
            "branch_pair_count": len(pair_ids),
            "state_count": len(observed_states),
            "branch_pair_state_observations": len(pair_ids) * len(observed_states),
            "maximum_cross_branch_intersection_pair_count_in_any_pair_state": maximum_cross_branch_intersections,
            "states_with_cross_branch_intersections": states_with_cross_branch_intersections,
            "pair_state_cross_hits": pair_state_cross_hits,
            "observed_states": observed_states,
            "whole_receiver_intersection_verdict_used": False,
            "whole_receiver_reason": "Disconnected authored Nature components create baseline contacts that a global count cannot attribute to simultaneous child-child motion.",
            "continuous_interval_checked": False,
            "adjacent_foldover_or_contact_checked": False,
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
        "branch_pair_state_observations": payload["uc_observer"]["branch_pair_state_observations"],
        "maximum_cross_branch_intersection_pair_count_in_any_pair_state": maximum_cross_branch_intersections,
        "states_with_cross_branch_intersections": states_with_cross_branch_intersections,
        "triangle_partition": payload["receiver"]["triangle_partition"],
        "max_order_delta_m": payload["witness_family"]["maximum_composition_order_vertex_delta_m"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

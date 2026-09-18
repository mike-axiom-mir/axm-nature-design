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
from axm_nature_design.rear_tree_geometry_shared_driver_static_rebind import (
    BRANCH_IDS,
    COMMAND_SIGN_MULTIPLIER_BY_BRANCH,
    PRIOR_GEOMETRY_HEAD,
    RIGGING_SHARED_DRIVER_HEAD,
    SHARED_DRIVER_VALUES_DEG,
    VFX_STATIC_RESPONSE_HEAD,
    evaluate,
)

SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"
CONTRACT_PATH = ROOT / "contracts" / "east-rear-shared-driver-static-geometry-rebind-002.json"
RIGGING_CONTRACT_REL = Path("contracts/east-rear-primary-branch-shared-driver-polarity-rigging-004.json")
VFX_CONTRACT_REL = Path("contracts/east-rear-shared-driver-vfx-response-envelope-003.json")
UC_HEAD = "ce70d717e381df6ca8a27c0c9fabe9d48bb1b23c"
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


def validate_donor_contracts(rigging: dict, vfx: dict) -> None:
    if rigging.get("schema") != "axm.nature-five-socket-shared-driver-polarity-binding/v0.1":
        raise RuntimeError("Rigging shared-driver contract schema drift")
    if tuple(float(v) for v in rigging.get("representative_shared_driver_deg", [])) != SHARED_DRIVER_VALUES_DEG:
        raise RuntimeError("Rigging shared-driver witness set drift")
    if rigging.get("command_sign_multiplier_by_branch") != COMMAND_SIGN_MULTIPLIER_BY_BRANCH:
        raise RuntimeError("Rigging shared-driver sign map drift")
    if rigging.get("simultaneous_multi_branch_motion_claimed") is not False:
        raise RuntimeError("Rigging donor unexpectedly claims simultaneous motion")
    if rigging.get("source_or_geometry_mutated") is not False:
        raise RuntimeError("Rigging donor unexpectedly mutates source/Geometry")

    if vfx.get("schema") != "axm.nature-vfx-shared-driver-spatial-response-envelope/v0.1":
        raise RuntimeError("VFX shared-driver contract schema drift")
    if vfx.get("rigging_owner", {}).get("head") != RIGGING_SHARED_DRIVER_HEAD:
        raise RuntimeError("VFX donor no longer binds exact Rigging shared-driver head")
    if tuple(float(v) for v in vfx.get("shared_driver_values_deg", [])) != SHARED_DRIVER_VALUES_DEG:
        raise RuntimeError("VFX static witness set drift")
    if vfx.get("pose_semantics") != "STATIC_SIMULTANEOUS_VISUAL_RESPONSE_REVIEW_NOT_MOTION":
        raise RuntimeError("VFX pose semantics drift")
    if vfx.get("simultaneous_multi_branch_motion_claimed") is not False:
        raise RuntimeError("VFX donor unexpectedly claims simultaneous motion")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--uc-root", type=Path, required=True)
    parser.add_argument("--rigging-root", type=Path, required=True)
    parser.add_argument("--vfx-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    uc_src = args.uc_root / "src"
    observer_path = uc_src / "axm_uc" / "mesh_self_intersection.py"
    if not observer_path.is_file():
        raise RuntimeError(f"missing exact UC observer: {observer_path}")
    sys.path.insert(0, str(uc_src))
    from axm_uc.mesh_self_intersection import inspect_triangle_self_intersections

    rigging_contract = load_json(args.rigging_root / RIGGING_CONTRACT_REL)
    vfx_contract = load_json(args.vfx_root / VFX_CONTRACT_REL)
    validate_donor_contracts(rigging_contract, vfx_contract)

    source = load_json(SOURCE_PATH)
    source_before = copy.deepcopy(source)
    contract = load_json(CONTRACT_PATH)
    evidence = evaluate(source, include_positions=True)
    if source != source_before:
        raise RuntimeError("Geometry rebind mutated Organic source")
    if evidence["lineage"]["prior_geometry_head"] != PRIOR_GEOMETRY_HEAD:
        raise RuntimeError("prior Geometry head drift")
    if evidence["lineage"]["rigging_shared_driver_head"] != RIGGING_SHARED_DRIVER_HEAD:
        raise RuntimeError("Rigging donor identity drift")
    if evidence["lineage"]["vfx_static_response_head"] != VFX_STATIC_RESPONSE_HEAD:
        raise RuntimeError("VFX donor identity drift")
    if evidence["receiver"]["triangle_partition"]["triangle_closed_child_partitions"] is not True:
        raise RuntimeError("shared-driver observer requires triangle-closed child partitions")

    mesh = build_mesh(source)
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

    first_positions = evidence["shared_driver"]["states"][0]["positions"]
    budget_hold = inspect_triangle_self_intersections(
        first_positions,
        flatten_triangles(mesh, owned_triangles[pair_ids[0][0]] + owned_triangles[pair_ids[0][1]]),
        max_triangle_pair_checks=PAIR_PAIR_CHECKS - 1,
    )
    if budget_hold.get("status") != "HOLD_TRIANGLE_PAIR_BUDGET_EXCEEDED":
        raise RuntimeError("UC pair observer did not fail closed below exact work budget")
    if budget_hold.get("triangle_pair_checks_performed") != 0:
        raise RuntimeError("budget HOLD performed a partial scan")
    if budget_hold.get("self_intersection_pair_count") is not None:
        raise RuntimeError("budget HOLD exposed a partial verdict")

    observed_states = []
    pair_state_hits = []
    maximum_cross = 0
    for state in evidence["shared_driver"]["states"]:
        positions = state.pop("positions")
        solo_counts: dict[str, int] = {}
        for branch_id in BRANCH_IDS:
            report = inspect_triangle_self_intersections(
                positions,
                flatten_triangles(mesh, owned_triangles[branch_id]),
                max_triangle_pair_checks=PAIR_BUDGET,
            )
            if report.get("inspection_complete") is not True:
                raise RuntimeError(f"incomplete UC solo observer: {state['state_id']} / {branch_id}")
            if report.get("triangle_pair_checks_required") != SOLO_PAIR_CHECKS:
                raise RuntimeError(f"solo pair-work drift: {state['state_id']} / {branch_id}")
            solo_counts[branch_id] = int(report["self_intersection_pair_count"])

        state_cross_total = 0
        pair_rows = []
        for left, right in pair_ids:
            report = inspect_triangle_self_intersections(
                positions,
                flatten_triangles(mesh, owned_triangles[left] + owned_triangles[right]),
                max_triangle_pair_checks=PAIR_BUDGET,
            )
            if report.get("inspection_complete") is not True:
                raise RuntimeError(f"incomplete UC pair observer: {state['state_id']} / {left}+{right}")
            if report.get("triangle_pair_checks_required") != PAIR_PAIR_CHECKS:
                raise RuntimeError(f"combined pair-work drift: {state['state_id']} / {left}+{right}")
            combined = int(report["self_intersection_pair_count"])
            cross = combined - solo_counts[left] - solo_counts[right]
            if cross < 0:
                raise RuntimeError("cross-branch attribution produced impossible negative count")
            maximum_cross = max(maximum_cross, cross)
            state_cross_total += cross
            if cross:
                pair_state_hits.append(
                    {
                        "state_id": state["state_id"],
                        "left": left,
                        "right": right,
                        "cross_branch_intersection_pair_count": cross,
                    }
                )
            pair_rows.append(
                {
                    "left": left,
                    "right": right,
                    "left_internal_intersection_pair_count": solo_counts[left],
                    "right_internal_intersection_pair_count": solo_counts[right],
                    "combined_intersection_pair_count": combined,
                    "cross_branch_intersection_pair_count": cross,
                }
            )
        observed_states.append(
            {
                "state_id": state["state_id"],
                "shared_driver_deg": state["shared_driver_deg"],
                "angles_deg": state["angles_deg"],
                "overlaps_prior_geometry_witness": state["overlaps_prior_geometry_witness"],
                "cross_branch_intersection_pair_count_total": state_cross_total,
                "pair_rows": pair_rows,
            }
        )

    observer_result = (
        "PASS_FIVE_SHARED_DRIVER_STATIC_WITNESSES_NO_CROSS_BRANCH_NONADJACENT_TRIANGLE_INTERSECTION"
        if maximum_cross == 0
        else "HOLD_SHARED_DRIVER_STATIC_WITNESS_CROSS_BRANCH_INTERSECTION_OBSERVED"
    )

    controls = [
        expect_rejection("rigging-donor-head-drift", lambda: evaluate(source, requested_rigging_head="0" * 40)),
        expect_rejection("vfx-donor-head-drift", lambda: evaluate(source, requested_vfx_head="0" * 40)),
        expect_rejection("witness-set-narrowing", lambda: evaluate(source, requested_shared_driver_values=(-5.0, 0.0, 5.0))),
        expect_rejection("continuous-interval-promotion", lambda: evaluate(source, claim_continuous_interval=True)),
        expect_rejection("simultaneous-motion-promotion", lambda: evaluate(source, claim_simultaneous_motion=True)),
    ]

    payload = {
        **evidence,
        "contract": contract,
        "donors": {"rigging_contract": rigging_contract, "vfx_contract": vfx_contract},
        "uc_observer": {
            "repository": "mike-axiom-mir/axm-universal-creation",
            "commit": UC_HEAD,
            "path": "src/axm_uc/mesh_self_intersection.py",
            "method": "PAIRWISE_CHILD_COMBINED_COUNT_MINUS_EXACT_SOLO_COUNTS",
            "solo_triangle_count": SOLO_TRIANGLES,
            "solo_pair_checks": SOLO_PAIR_CHECKS,
            "combined_pair_triangle_count": PAIR_TRIANGLES,
            "combined_pair_checks": PAIR_PAIR_CHECKS,
            "pair_budget": PAIR_BUDGET,
            "budget_hold_control": budget_hold,
            "state_count": len(observed_states),
            "branch_pair_count": len(pair_ids),
            "branch_pair_state_observations": len(observed_states) * len(pair_ids),
            "maximum_cross_branch_intersection_pair_count_in_any_pair_state": maximum_cross,
            "pair_state_cross_hits": pair_state_hits,
            "observed_states": observed_states,
            "result": observer_result,
            "continuous_interval_checked": False,
            "adjacent_foldover_or_contact_checked": False,
            "child_fixed_receiver_clearance_checked": False,
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
        "observer_result": observer_result,
        "shared_driver_values_deg": payload["shared_driver"]["values_deg"],
        "prior_overlap_states": payload["shared_driver"]["prior_geometry_overlap_state_count"],
        "new_interior_states": payload["shared_driver"]["new_interior_state_count"],
        "branch_pair_state_observations": payload["uc_observer"]["branch_pair_state_observations"],
        "maximum_cross_branch_intersection_pair_count_in_any_pair_state": maximum_cross,
        "pair_state_cross_hits": pair_state_hits,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

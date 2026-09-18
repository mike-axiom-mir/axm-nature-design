#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from axm_nature_design import rear_tree_geometry_north_low_transition_open_ring as subject


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="examples/east_rear_tree_neutral_001.json")
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def load_source(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def must_reject(source, **kwargs):
    try:
        subject.evaluate(source, **kwargs)
    except ValueError:
        return True
    raise AssertionError(f"failure control unexpectedly passed: {kwargs}")


def main():
    args = parse_args()
    source = load_source(args.source)
    report = subject.evaluate(source)
    failure_controls = {
        "reject_geometry_predecessor_drift": must_reject(source, requested_geometry_predecessor_head="0" * 40),
        "reject_current_rigging_owner_drift": must_reject(source, requested_rigging_owner_head="0" * 40),
        "reject_organic_transition_owner_drift": must_reject(source, requested_organic_owner_head="0" * 40),
        "reject_procedural_transition_owner_drift": must_reject(source, requested_procedural_owner_head="0" * 40),
        "reject_transition_parameter_drift": must_reject(source, requested_transition_u=subject.TRANSITION_U + 1e-4),
        "reject_transition_length_drift": must_reject(source, requested_transition_length_m=subject.TRANSITION_LENGTH_M + 1e-4),
        "reject_trunk_opening_promotion": must_reject(source, claim_trunk_opening_proven=True),
        "reject_connected_junction_promotion": must_reject(source, claim_connected_branch_trunk_junction=True),
        "reject_source_adoption_promotion": must_reject(source, claim_source_adoption=True),
        "reject_rigging_rebind_promotion": must_reject(source, claim_rigging_rebind=True),
        "reject_target_host_runtime_promotion": must_reject(source, claim_target_host_or_runtime=True),
    }
    report["failure_controls"] = failure_controls
    report["all_failure_controls_rejected"] = all(failure_controls.values())

    if report["result"] != subject.RESULT:
        raise AssertionError(report["result"])
    if not report["all_failure_controls_rejected"]:
        raise AssertionError("one or more failure controls did not reject")
    topology = report["candidate_topology"]
    if topology["boundary_cycles"] != 1 or topology["boundary_cycle_lengths"] != [8]:
        raise AssertionError("candidate does not expose exactly one simple eight-edge boundary loop")
    if topology["nonmanifold_edges"] != 0 or topology["winding_conflicts"] != 0:
        raise AssertionError("candidate topology is not structurally clean")
    if report["truth_boundary"]["connected_branch_trunk_topology_proven"]:
        raise AssertionError("open ring was inflated into connected-junction evidence")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["result"])
    print(
        f"V={topology['vertices']} F={topology['triangles']} E={topology['edges']} "
        f"boundary={topology['boundary_edges']} cycles={topology['boundary_cycles']} "
        f"u={report['owner_transition']['parameter_u']:.15f}"
    )


if __name__ == "__main__":
    main()

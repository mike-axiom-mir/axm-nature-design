#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from axm_nature_design import rear_tree_geometry_north_low_trunk_bridge_candidate as subject


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
        "reject_organic_exit_frame_owner_drift": must_reject(source, requested_organic_exit_frame_owner_head="0" * 40),
        "reject_organic_exit_frame_blob_drift": must_reject(source, requested_organic_exit_frame_blob="0" * 40),
        "reject_rigging_owner_drift": must_reject(source, requested_rigging_owner_head="0" * 40),
        "reject_indexed_trunk_cut_promotion": must_reject(source, claim_indexed_trunk_cut_integrated=True),
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
    combined = report["combined_candidate_topology"]
    bridge = report["bridge_patch_topology"]
    if (combined["vertices"], combined["triangles"], combined["edges"]) != (25, 40, 64):
        raise AssertionError("combined bridge candidate topology drift")
    if combined["boundary_cycles"] != 1 or combined["boundary_cycle_lengths"] != [8]:
        raise AssertionError("combined candidate must expose exactly one eight-edge trunk-side boundary")
    if bridge["boundary_cycles"] != 2 or bridge["boundary_cycle_lengths"] != [8, 8]:
        raise AssertionError("bridge patch must remain a two-boundary annulus")
    if combined["nonmanifold_edges"] or combined["winding_conflicts"]:
        raise AssertionError("combined candidate is not structurally clean")
    truth = report["truth_boundary"]
    if truth["indexed_trunk_mesh_cut_or_mutated"] or truth["connected_branch_trunk_indexed_topology_proven"]:
        raise AssertionError("analytic bridge evidence was inflated into an indexed connected-junction claim")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["result"])
    print(
        f"combined V={combined['vertices']} F={combined['triangles']} E={combined['edges']} "
        f"boundary={combined['boundary_edges']} min_bridge={report['analytic_trunk_loop']['minimum_bridge_span_m']:.9f}m"
    )


if __name__ == "__main__":
    main()

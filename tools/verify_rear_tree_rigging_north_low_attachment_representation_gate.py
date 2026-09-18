#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from axm_nature_design import rear_tree_rigging_north_low_attachment_representation_gate as subject


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="examples/east_rear_tree_neutral_001.json")
    parser.add_argument("--geometry-contract", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def must_reject(source, geometry_contract, **kwargs):
    try:
        subject.evaluate(source, geometry_contract, **kwargs)
    except ValueError:
        return True
    raise AssertionError(f"failure control unexpectedly passed: {kwargs}")


def main():
    args = parse_args()
    source = load_json(args.source)
    geometry_contract = load_json(args.geometry_contract)
    report = subject.evaluate(source, geometry_contract)

    shared_vertex_mutation = copy.deepcopy(geometry_contract)
    shared_vertex_mutation["expected"]["shared_indexed_vertices_with_trunk"] = 1
    component_mutation = copy.deepcopy(geometry_contract)
    component_mutation["expected"]["edge_connected_components"] = 1

    failure_controls = {
        "reject_rigging_predecessor_drift": must_reject(source, geometry_contract, requested_rigging_predecessor_head="0" * 40),
        "reject_geometry_donor_drift": must_reject(source, geometry_contract, requested_geometry_donor_head="0" * 40),
        "reject_geometry_shared_vertex_mutation": must_reject(source, shared_vertex_mutation),
        "reject_geometry_component_mutation": must_reject(source, component_mutation),
        "reject_connected_attachment_promotion": must_reject(source, geometry_contract, claim_connected_branch_trunk_attachment=True),
        "reject_production_skinning_promotion": must_reject(source, geometry_contract, claim_production_skinning=True),
        "reject_production_parent_weight_promotion": must_reject(source, geometry_contract, claim_production_parent_weight=True),
        "reject_animation_acceptance_promotion": must_reject(source, geometry_contract, claim_animation_acceptance=True),
        "reject_technical_art_acceptance_promotion": must_reject(source, geometry_contract, claim_technical_art_acceptance=True),
        "reject_runtime_acceptance_promotion": must_reject(source, geometry_contract, claim_runtime_acceptance=True),
    }
    report["failure_controls"] = failure_controls
    report["all_failure_controls_rejected"] = all(failure_controls.values())
    if report["result"] != subject.RESULT:
        raise AssertionError(report["result"])
    if not report["all_failure_controls_rejected"]:
        raise AssertionError("one or more failure controls did not reject")
    if report["geometry_attachment_class"]["shared_indexed_vertices_with_trunk"] != 0:
        raise AssertionError("north-low attachment is no longer detached by indexed identity")
    if report["attachment_representation_constraint"]["production_connected_skinning_allowed"]:
        raise AssertionError("detached diagnostic child was promoted to production skinning")
    if report["preserved_rigging_motion_evidence"]["representative_parent_child_pose_count"] != 9:
        raise AssertionError("representative pose schedule drift")
    if report["truth_boundary"]["animation_timing_interpolation_or_playback_claimed"]:
        raise AssertionError("Animation authority promotion")
    if report["truth_boundary"]["runtime_controller_or_device_claimed"]:
        raise AssertionError("Runtime authority promotion")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["result"])
    print(
        f"components={report['geometry_attachment_class']['edge_connected_components']} "
        f"shared_with_trunk={report['geometry_attachment_class']['shared_indexed_vertices_with_trunk']} "
        f"poses={report['preserved_rigging_motion_evidence']['representative_parent_child_pose_count']}"
    )


if __name__ == "__main__":
    main()

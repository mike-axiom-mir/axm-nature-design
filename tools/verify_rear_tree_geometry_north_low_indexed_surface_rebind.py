#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from axm_nature_design import rear_tree_geometry_north_low_indexed_surface_rebind as subject


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
        "reject_analytic_geometry_head_drift": must_reject(source, requested_analytic_geometry_donor_head="0" * 40),
        "reject_analytic_geometry_blob_drift": must_reject(source, requested_analytic_geometry_module_blob="0" * 40),
        "reject_rigging_owner_drift": must_reject(source, requested_rigging_owner_head="0" * 40),
        "reject_indexed_cut_promotion": must_reject(source, claim_indexed_trunk_cut_integrated=True),
        "reject_connected_junction_promotion": must_reject(source, claim_connected_branch_trunk_junction=True),
        "reject_continuous_clearance_promotion": must_reject(source, claim_continuous_deformation_clearance=True),
        "reject_rigging_transfer_promotion": must_reject(source, claim_rigging_transfer=True),
        "reject_target_host_runtime_promotion": must_reject(source, claim_target_host_or_runtime=True),
    }
    report["failure_controls"] = failure_controls
    report["all_failure_controls_rejected"] = all(failure_controls.values())

    if report["result"] != subject.RESULT:
        raise AssertionError(report["result"])
    if not report["all_failure_controls_rejected"]:
        raise AssertionError("one or more failure controls did not reject")
    binding = report["indexed_surface_binding"]
    if binding["touched_side_cells"] != [0, 1, 2, 9] or binding["parameter_space_self_intersections"] != 0:
        raise AssertionError("indexed opening footprint drift")
    if len(binding["memberships"]) != 8:
        raise AssertionError("expected eight exact source-triangle memberships")
    if binding["maximum_triangle_plane_residual_m"] > 1e-10:
        raise AssertionError("indexed-surface point left source triangle plane")
    if binding["minimum_barycentric_coordinate"] < -1e-10:
        raise AssertionError("indexed-surface point left source triangle bounds")
    delta = report["analytic_to_indexed_surface_rebind"]
    if delta["maximum_surface_delta_m"] <= 0.004:
        raise AssertionError("analytic/indexed mismatch unexpectedly disappeared")
    if not 0.010 < delta["indexed_surface_minimum_bridge_span_m"] < delta["analytic_minimum_bridge_span_m"]:
        raise AssertionError("indexed bridge span relation drift")
    truth = report["truth_boundary"]
    if truth["source_or_default_mesh_mutated"] or truth["indexed_trunk_cut_integrated"]:
        raise AssertionError("diagnostic rebind was inflated into source mutation")
    if truth["analytic_rigging_pass_transferred"]:
        raise AssertionError("analytic Rigging PASS transferred without revalidation")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["result"])
    print(
        "indexed-loop cells={} max-analytic-delta={:.9f}m min-indexed-span={:.9f}m min-area={:.9f}m2".format(
            binding["touched_side_cells"],
            delta["maximum_surface_delta_m"],
            delta["indexed_surface_minimum_bridge_span_m"],
            delta["minimum_neutral_bridge_triangle_area_m2"],
        )
    )


if __name__ == "__main__":
    main()

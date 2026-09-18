#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from axm_nature_design import rear_tree_rigging_north_low_parent_influence_gate as subject


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        default="examples/east_rear_tree_neutral_001.json",
        help="Exact east/rear Nature source JSON.",
    )
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
        "reject_rigging_predecessor_drift": must_reject(
            source, requested_rigging_predecessor_head="0" * 40
        ),
        "reject_organic_interaction_donor_drift": must_reject(
            source, requested_organic_interaction_head="0" * 40
        ),
        "reject_parent_interval_widening": must_reject(
            source, parent_diagnostic_max_deg=3.0
        ),
        "reject_forced_parent_influence": must_reject(source, force_parent_influence=True),
        "reject_source_rom_promotion": must_reject(source, claim_source_rom=True),
        "reject_production_weighting_promotion": must_reject(
            source, claim_production_weighting=True
        ),
        "reject_surface_attachment_promotion": must_reject(
            source, claim_surface_attachment=True
        ),
        "reject_animation_acceptance_promotion": must_reject(
            source, claim_animation_acceptance=True
        ),
        "reject_runtime_acceptance_promotion": must_reject(
            source, claim_runtime_acceptance=True
        ),
    }
    report["failure_controls"] = failure_controls
    report["all_failure_controls_rejected"] = all(failure_controls.values())

    if report["result"] != subject.RESULT:
        raise AssertionError(report["result"])
    if not report["all_failure_controls_rejected"]:
        raise AssertionError("one or more failure controls did not reject")
    if report["rigging_constraint"]["upper_trunk_parent_influence_enabled_for_north_low"]:
        raise AssertionError("north-low parent influence unexpectedly enabled")
    if report["measurements"]["maximum_gated_parent_command_leak_m"] > subject.TOL:
        raise AssertionError("parent command leaked through exclusion gate")
    if report["measurements"]["maximum_counterfactual_inherited_parent_socket_travel_m"] <= 0.01:
        raise AssertionError("counterfactual parent inheritance is not discriminating")
    if report["truth_boundary"]["animation_timing_interpolation_or_playback_claimed"]:
        raise AssertionError("Animation authority promotion")
    if report["truth_boundary"]["runtime_controller_or_device_claimed"]:
        raise AssertionError("Runtime authority promotion")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    relation = report["organic_interaction_consumed"]
    measures = report["measurements"]
    print(report["result"])
    print(
        "attachment_gap_m="
        f"{relation['neutral_attachment_cross_section_to_trunk_flex_boundary_signed_m']:.17g} "
        "counterfactual_socket_travel_m="
        f"{measures['maximum_counterfactual_inherited_parent_socket_travel_m']:.17g} "
        "parent_leak_m="
        f"{measures['maximum_gated_parent_command_leak_m']:.17g}"
    )


if __name__ == "__main__":
    main()

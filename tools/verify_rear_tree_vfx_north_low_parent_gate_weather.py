#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from axm_nature_design import rear_tree_vfx_north_low_parent_gate_weather as subject


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="examples/east_rear_tree_neutral_001.json")
    parser.add_argument("--output", required=True)
    parser.add_argument("--svg", required=True)
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
    controls = {
        "reject_weather_direction_drift": must_reject(source, wind_xy=(0.9, 0.35)),
        "reject_parent_widening": must_reject(source, parent_angles_deg=(-3.0, 0.0, 3.0)),
        "reject_child_widening": must_reject(source, child_angles_deg=(-6.0, 0.0, 6.0)),
        "reject_physical_wind_promotion": must_reject(source, claim_physical_wind=True),
        "reject_animation_promotion": must_reject(source, claim_animation_adoption=True),
        "reject_runtime_promotion": must_reject(source, claim_runtime_acceptance=True),
        "reject_gameplay_physics_promotion": must_reject(source, claim_gameplay_or_physics=True),
        "reject_biological_motion_promotion": must_reject(source, claim_biological_motion=True),
        "reject_art_qa_promotion": must_reject(source, claim_art_or_qa_acceptance=True),
    }
    report["failure_controls"] = controls
    report["all_failure_controls_rejected"] = all(controls.values())
    if report["result"] != subject.RESULT or not report["all_failure_controls_rejected"]:
        raise AssertionError("VFX parent-gate Weather verification failed")
    if report["measurements"]["review_only_downwind_alignment_angle_deg"] != -5.0:
        raise AssertionError("north-low review polarity changed")
    if report["measurements"]["maximum_weather_parallel_response_drift_across_parent_commands_m"] > subject.TOL:
        raise AssertionError("parent command changed Weather-parallel response")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    svg = Path(args.svg)
    svg.parent.mkdir(parents=True, exist_ok=True)
    svg.write_text(subject.build_review_svg(source), encoding="utf-8")
    print(subject.RESULT)
    print(
        f"preferred={report['measurements']['review_only_downwind_alignment_angle_deg']:+.1f}deg "
        f"parallel_drift={report['measurements']['maximum_weather_parallel_response_drift_across_parent_commands_m']:.17g}m "
        f"counterfactual_delta={report['measurements']['rigging_counterfactual_parent_inheritance_max_output_delta_m']:.17g}m"
    )


if __name__ == "__main__":
    main()

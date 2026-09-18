#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from axm_nature_design import rear_tree_animation_north_low_parent_exclusion_temporal_rebind as subject


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

    controls = {
        "reject_duration_drift": must_reject(source, geometry_contract, duration_s=0.9),
        "reject_sample_rate_drift": must_reject(source, geometry_contract, sample_rate_hz=30),
        "reject_child_amplitude_drift": must_reject(source, geometry_contract, child_amplitude_deg=5.1),
        "reject_parent_stress_widening": must_reject(source, geometry_contract, parent_stress_amplitude_deg=2.6),
        "reject_inherited_parent_frame": must_reject(source, geometry_contract, inherit_parent_frame=True),
        "reject_wind_promotion": must_reject(source, geometry_contract, claim_wind_motion=True),
        "reject_biological_rom_promotion": must_reject(source, geometry_contract, claim_biological_rom=True),
        "reject_connected_attachment_promotion": must_reject(source, geometry_contract, claim_connected_attachment=True),
        "reject_production_skinning_promotion": must_reject(source, geometry_contract, claim_production_skinning=True),
        "reject_target_engine_promotion": must_reject(source, geometry_contract, claim_target_engine_playback=True),
        "reject_runtime_controller_promotion": must_reject(source, geometry_contract, claim_runtime_controller=True),
        "reject_gameplay_promotion": must_reject(source, geometry_contract, claim_gameplay_acceptance=True),
    }
    report["failure_controls"] = controls
    report["all_failure_controls_rejected"] = all(controls.values())

    if report["result"] != subject.RESULT:
        raise AssertionError(report["result"])
    if not report["all_failure_controls_rejected"]:
        raise AssertionError("one or more fail-closed controls did not reject")
    if report["measurements"]["maximum_parent_command_leak_m"] > subject.TOL:
        raise AssertionError("parent command leaked through current Rigging exclusion gate")
    if report["measurements"]["maximum_counterfactual_inherited_parent_output_delta_m"] <= 1e-6:
        raise AssertionError("wrong-parent counterfactual is not discriminating")
    if report["truth_boundary"]["target_engine_playback_claimed"]:
        raise AssertionError("target-host authority promotion")
    if report["truth_boundary"]["runtime_controller_state_machine_input_or_device_claimed"]:
        raise AssertionError("Runtime authority promotion")
    if report["truth_boundary"]["physics_or_gameplay_claimed"]:
        raise AssertionError("gameplay authority promotion")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report["result"])
    measurements = report["measurements"]
    print(
        f"samples={measurements['sample_count']} "
        f"parent_leak={measurements['maximum_parent_command_leak_m']} "
        f"counterfactual_delta={measurements['maximum_counterfactual_inherited_parent_output_delta_m']} "
        f"endpoint={measurements['endpoint_closure_m']}"
    )


if __name__ == "__main__":
    main()

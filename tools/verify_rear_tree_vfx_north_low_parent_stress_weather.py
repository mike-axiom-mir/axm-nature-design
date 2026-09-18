#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from axm_nature_design import rear_tree_vfx_north_low_parent_stress_weather as subject


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="examples/east_rear_tree_neutral_001.json")
    parser.add_argument("--geometry-contract", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--svg", required=True)
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
        "reject_weather_direction_drift": must_reject(source, geometry_contract, wind_xy=(1.0, 0.36)),
        "reject_physical_wind_promotion": must_reject(source, geometry_contract, claim_physical_wind=True),
        "reject_botanical_motion_promotion": must_reject(source, geometry_contract, claim_botanical_motion=True),
        "reject_animation_authorship_promotion": must_reject(source, geometry_contract, claim_animation_authorship=True),
        "reject_target_engine_promotion": must_reject(source, geometry_contract, claim_target_engine_playback=True),
        "reject_runtime_promotion": must_reject(source, geometry_contract, claim_runtime_acceptance=True),
        "reject_gameplay_or_physics_promotion": must_reject(source, geometry_contract, claim_gameplay_or_physics=True),
        "reject_art_or_qa_promotion": must_reject(source, geometry_contract, claim_art_or_qa_acceptance=True),
    }
    report["failure_controls"] = controls
    report["all_failure_controls_rejected"] = all(controls.values())
    if report["result"] != subject.RESULT:
        raise AssertionError(report["result"])
    if not report["all_failure_controls_rejected"]:
        raise AssertionError("one or more authority controls did not fail closed")
    measurements = report["measurements"]
    if measurements["owner_pose_digest_mismatches"] != 0:
        raise AssertionError("VFX reconstruction drifted from Animation owner poses")
    if measurements["weather_polarity_sign_violations"] != 0:
        raise AssertionError("accepted Animation samples violate retained Weather polarity")
    if measurements["maximum_accepted_vs_wrong_parent_weather_parallel_delta_m"] <= 1e-6:
        raise AssertionError("wrong-parent counterfactual is not visually discriminating")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    svg = Path(args.svg)
    svg.parent.mkdir(parents=True, exist_ok=True)
    svg.write_text(subject.build_review_svg(source, geometry_contract), encoding="utf-8")
    print(report["result"])
    print(
        "samples={sample_count} peak_downwind_mm={down:.6f} peak_upwind_mm={up:.6f} "
        "wrong_parent_parallel_delta_mm={wrong:.6f} wrong_parent_vertex_delta_mm={vertex:.6f}".format(
            sample_count=measurements["sample_count"],
            down=measurements["minus5_peak_downwind_parallel_m"] * 1000.0,
            up=measurements["plus5_peak_upwind_parallel_m"] * 1000.0,
            wrong=measurements["maximum_accepted_vs_wrong_parent_weather_parallel_delta_m"] * 1000.0,
            vertex=measurements["maximum_accepted_vs_wrong_parent_vertex_delta_m"] * 1000.0,
        )
    )


if __name__ == "__main__":
    main()

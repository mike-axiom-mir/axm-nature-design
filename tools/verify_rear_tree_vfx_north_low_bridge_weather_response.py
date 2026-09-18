#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from axm_nature_design import rear_tree_vfx_north_low_bridge_weather_response as subject

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--svg", type=Path, required=True)
    parser.add_argument("--weather-y", type=float, default=0.35)
    parser.add_argument("--claim-physical-wind", action="store_true")
    parser.add_argument("--claim-production-skinning", action="store_true")
    parser.add_argument("--claim-continuous-surface-safety", action="store_true")
    parser.add_argument("--claim-target-host", action="store_true")
    parser.add_argument("--claim-runtime", action="store_true")
    parser.add_argument("--claim-gameplay-or-physics", action="store_true")
    parser.add_argument("--claim-art-or-qa", action="store_true")
    args = parser.parse_args()

    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    report = subject.evaluate(
        source,
        wind_xy=(1.0, args.weather_y),
        claim_physical_wind=args.claim_physical_wind,
        claim_production_skinning=args.claim_production_skinning,
        claim_continuous_foldover_or_collision=args.claim_continuous_surface_safety,
        claim_target_host_acceptance=args.claim_target_host,
        claim_runtime_acceptance=args.claim_runtime,
        claim_gameplay_or_physics=args.claim_gameplay_or_physics,
        claim_art_or_qa_acceptance=args.claim_art_or_qa,
    )
    if report["result"] != subject.RESULT or not all(report["checks"].values()):
        raise SystemExit("bounded VFX Weather-response gate failed")

    truth = report["truth_boundary"]
    forbidden = [
        "physical_wind_speed_force_drag_or_turbulence_claimed",
        "production_skinning_or_blending_claimed",
        "indexed_connected_junction_claimed",
        "continuous_bridge_foldover_collision_or_self_intersection_claimed",
        "botanical_mechanics_or_biological_rom_claimed",
        "animation_timing_interpolation_or_playback_claimed",
        "technical_art_target_host_claimed",
        "runtime_controller_device_or_performance_claimed",
        "gameplay_damage_collision_or_physics_claimed",
        "art_direction_or_independent_visual_qa_acceptance_claimed",
        "canon_or_production_readiness_claimed",
    ]
    if any(truth[name] for name in forbidden):
        raise SystemExit("VFX truth boundary widened")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.svg.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.svg.write_text(subject.build_review_svg(source), encoding="utf-8")

    m = report["measurements"]
    print(
        "PASS",
        report["result"],
        f"minus5_branch_mm={m['minus5_branch_downwind_parallel_m']*1000:.9f}",
        f"minus5_bridge_mm={m['minus5_bridge_downwind_parallel_m']*1000:.9f}",
        f"plus5_branch_mm={m['plus5_branch_upwind_parallel_m']*1000:.9f}",
        f"plus5_bridge_mm={m['plus5_bridge_upwind_parallel_m']*1000:.9f}",
        f"trunk_drift_m={m['maximum_trunk_centroid_drift_m']:.15g}",
        f"half_gradient_residual_m={m['maximum_bridge_vs_half_branch_centroid_residual_m']:.15g}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

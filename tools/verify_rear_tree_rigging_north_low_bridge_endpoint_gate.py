#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from axm_nature_design import rear_tree_rigging_north_low_bridge_endpoint_gate as subject

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    report = subject.evaluate(source)

    if report["result"] != subject.RESULT:
        raise SystemExit("unexpected bounded Rigging result")
    if not all(report["checks"].values()):
        raise SystemExit("one or more endpoint constraint checks failed")
    truth = report["truth_boundary"]
    forbidden = [
        "source_geometry_mutated",
        "geometry_bridge_topology_mutated",
        "indexed_trunk_cut_or_connected_junction_claimed",
        "production_skinning_or_blending_claimed",
        "botanical_mechanics_or_strength_claimed",
        "continuous_bridge_foldover_collision_or_self_intersection_claimed",
        "source_or_biological_rom_claimed",
        "animation_timing_interpolation_or_playback_claimed",
        "technical_art_target_host_claimed",
        "runtime_controller_device_or_performance_claimed",
        "art_or_visual_qa_claimed",
        "canon_or_production_readiness_claimed",
    ]
    if any(truth[name] for name in forbidden):
        raise SystemExit("truth boundary widened")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    evidence = report["representative_pose_evidence"]
    print(
        "PASS",
        report["result"],
        f"poses={evidence['witness_count']}",
        f"min_area_m2={evidence['minimum_bridge_triangle_area_m2']:.15g}",
        f"min_span_m={evidence['minimum_paired_bridge_span_m']:.15g}",
        f"branch_fixed_negative_m={evidence['branch_fixed_counterfactual_m']:.15g}",
        f"trunk_follow_negative_m={evidence['trunk_follows_child_counterfactual_m']:.15g}",
    )


if __name__ == "__main__":
    main()

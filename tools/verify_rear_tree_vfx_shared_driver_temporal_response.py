#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from axm_nature_design.rear_tree_vfx_shared_driver_temporal_response import evaluate

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "examples" / "east_rear_tree_neutral_001.json"


def _svg(payload: dict) -> str:
    width = 1120
    height = 720
    left = 90
    right = 40
    top = 60
    plot_w = width - left - right
    family_top = 95
    family_h = 230
    branch_top = 390
    branch_h = 210
    samples = payload["review"]["samples"]
    branches = payload["review"]["branch_ids"]

    values_mm = [abs(row["family"]["parallel_m"] * 1000.0) for row in samples]
    for row in samples:
        values_mm.extend(abs(row["branches"][branch]["parallel_m"] * 1000.0) for branch in branches)
    peak = max(max(values_mm), 1.0)
    scale = max(5.0, peak * 1.12)

    def x_for(index: int) -> float:
        return left + plot_w * (float(index) / 40.0)

    def y_for(value_mm: float, mid_y: float, plot_h: float) -> float:
        return mid_y - (float(value_mm) / scale) * (plot_h / 2.0)

    rows = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="90" y="30" font-family="monospace" font-size="17">AXM Nature VFX — exact Animation loop measured in Weather visual-direction frame</text>',
        '<text x="90" y="52" font-family="monospace" font-size="12">review-only: source-space temporal response; not physical wind, natural motion, target-host playback, Runtime or Art/QA acceptance</text>',
    ]

    family_mid = family_top + family_h / 2.0
    rows += [
        f'<rect x="{left}" y="{family_top}" width="{plot_w}" height="{family_h}" fill="none" stroke="black" stroke-width="1"/>',
        f'<line x1="{left}" y1="{family_mid:.2f}" x2="{left + plot_w}" y2="{family_mid:.2f}" stroke="black" stroke-width="1"/>',
        f'<text x="{left}" y="{family_top - 12}" font-family="monospace" font-size="14">family centroid parallel response (mm) — sign must follow shared diagnostic driver</text>',
    ]
    family_points = " ".join(
        f"{x_for(row['index']):.2f},{y_for(row['family']['parallel_m'] * 1000.0, family_mid, family_h):.2f}"
        for row in samples
    )
    rows.append(f'<polyline fill="none" stroke="black" stroke-width="3" points="{family_points}"/>')

    branch_mid = branch_top + branch_h / 2.0
    rows += [
        f'<rect x="{left}" y="{branch_top}" width="{plot_w}" height="{branch_h}" fill="none" stroke="black" stroke-width="1"/>',
        f'<line x1="{left}" y1="{branch_mid:.2f}" x2="{left + plot_w}" y2="{branch_mid:.2f}" stroke="black" stroke-width="1"/>',
        f'<text x="{left}" y="{branch_top - 12}" font-family="monospace" font-size="14">five branch-centroid parallel responses (mm)</text>',
    ]
    dash_patterns = ["", "7 3", "2 3", "9 3 2 3", "4 4"]
    for branch, dash in zip(branches, dash_patterns):
        points = " ".join(
            f"{x_for(row['index']):.2f},{y_for(row['branches'][branch]['parallel_m'] * 1000.0, branch_mid, branch_h):.2f}"
            for row in samples
        )
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        rows.append(f'<polyline fill="none" stroke="black" stroke-width="1.5"{dash_attr} points="{points}"/>')

    landmark_y = 636
    rows.append(f'<text x="90" y="{landmark_y}" font-family="monospace" font-size="12">landmarks: 0.00s neutral | 0.25s +5° | 0.50s neutral | 0.75s -5° | 1.00s neutral</text>')
    rows.append(f'<text x="90" y="{landmark_y + 20}" font-family="monospace" font-size="12">Weather donor: wind_xy=[1.0,0.35], semantics=VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED</text>')
    rows.append(f'<text x="90" y="{landmark_y + 40}" font-family="monospace" font-size="12">cross-direction + vertical components are retained in JSON as descriptive measurements, not forced to zero.</text>')
    rows.append('</svg>')
    return "\n".join(rows) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--svg-output", type=Path)
    parser.add_argument("--animation-head", default="bfb66da82bc358b14e52711bbdef7b58e4c943af")
    parser.add_argument("--weather-head", default="ca2eaba519e8449835b0ea6ef944b7080c3caa6a")
    parser.add_argument("--weather-y", type=float, default=0.35)
    parser.add_argument("--claim-vfx-motion-adoption", action="store_true")
    parser.add_argument("--claim-physical-wind", action="store_true")
    parser.add_argument("--claim-natural-vegetation-motion", action="store_true")
    parser.add_argument("--claim-continuous-collision-clearance", action="store_true")
    parser.add_argument("--claim-target-engine-playback", action="store_true")
    parser.add_argument("--claim-runtime-acceptance", action="store_true")
    parser.add_argument("--claim-gameplay-acceptance", action="store_true")
    parser.add_argument("--claim-art-or-visual-qa-acceptance", action="store_true")
    args = parser.parse_args()

    source = json.loads(args.source.read_text(encoding="utf-8"))
    payload = evaluate(
        source,
        requested_animation_head=args.animation_head,
        requested_weather_owner_head=args.weather_head,
        requested_weather_direction_xy=(1.0, args.weather_y),
        claim_vfx_motion_adoption=args.claim_vfx_motion_adoption,
        claim_physical_wind=args.claim_physical_wind,
        claim_natural_vegetation_motion=args.claim_natural_vegetation_motion,
        claim_continuous_collision_clearance=args.claim_continuous_collision_clearance,
        claim_target_engine_playback=args.claim_target_engine_playback,
        claim_runtime_acceptance=args.claim_runtime_acceptance,
        claim_gameplay_acceptance=args.claim_gameplay_acceptance,
        claim_art_or_visual_qa_acceptance=args.claim_art_or_visual_qa_acceptance,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.svg_output:
        args.svg_output.parent.mkdir(parents=True, exist_ok=True)
        args.svg_output.write_text(_svg(payload), encoding="utf-8")
    print(payload["result"])
    return 0 if payload["result"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())

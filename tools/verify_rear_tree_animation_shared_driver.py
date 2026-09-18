#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from axm_nature_design.rear_tree_animation_shared_driver import evaluate

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "examples" / "east_rear_tree_neutral_001.json"


def _svg(payload: dict) -> str:
    width = 920
    height = 430
    left = 70
    top = 40
    plot_w = 790
    plot_h = 250
    mid_y = top + plot_h / 2.0
    scale_y = plot_h / 12.0
    samples = payload["samples"]

    def x_for(index: int) -> float:
        return left + plot_w * (index / 40.0)

    def y_for(angle: float) -> float:
        return mid_y - float(angle) * scale_y

    rows = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="70" y="24" font-family="monospace" font-size="16">AXM Nature Animation — five-socket shared-driver diagnostic loop</text>',
        f'<line x1="{left}" y1="{mid_y:.2f}" x2="{left + plot_w}" y2="{mid_y:.2f}" stroke="black" stroke-width="1"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="black" stroke-width="1"/>',
    ]
    shared_points = " ".join(
        f"{x_for(row['index']):.2f},{y_for(row['shared_driver_deg']):.2f}" for row in samples
    )
    rows.append(f'<polyline fill="none" stroke="black" stroke-width="2" points="{shared_points}"/>')
    rows.append('<text x="70" y="322" font-family="monospace" font-size="13">shared u(t): 0 -> +5 -> 0 -> -5 -> 0 deg, 1.0 s, 40 Hz sampled review</text>')
    rows.append('<text x="70" y="344" font-family="monospace" font-size="13">local polarity: south + | north-low - | east + | west-high - | north-top +</text>')
    rows.append('<text x="70" y="366" font-family="monospace" font-size="13">all five Rigging children move simultaneously in sampled source-mesh evidence</text>')
    rows.append('<text x="70" y="388" font-family="monospace" font-size="13">NOT wind, biological ROM, continuous collision, target-engine playback, Runtime or gameplay acceptance</text>')
    rows.append('</svg>')
    return "\n".join(rows) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--svg-output", type=Path)
    parser.add_argument("--duration-s", type=float, default=1.0)
    parser.add_argument("--sample-rate-hz", type=int, default=40)
    parser.add_argument("--amplitude-deg", type=float, default=5.0)
    parser.add_argument("--claim-wind-motion", action="store_true")
    parser.add_argument("--claim-physical-wind", action="store_true")
    parser.add_argument("--claim-biological-rom", action="store_true")
    parser.add_argument("--claim-continuous-collision-clearance", action="store_true")
    parser.add_argument("--claim-target-engine-playback", action="store_true")
    parser.add_argument("--claim-runtime-controller", action="store_true")
    parser.add_argument("--claim-gameplay-acceptance", action="store_true")
    args = parser.parse_args()

    source = json.loads(args.source.read_text(encoding="utf-8"))
    payload = evaluate(
        source,
        duration_s=args.duration_s,
        sample_rate_hz=args.sample_rate_hz,
        amplitude_deg=args.amplitude_deg,
        claim_wind_motion=args.claim_wind_motion,
        claim_physical_wind=args.claim_physical_wind,
        claim_biological_rom=args.claim_biological_rom,
        claim_continuous_collision_clearance=args.claim_continuous_collision_clearance,
        claim_target_engine_playback=args.claim_target_engine_playback,
        claim_runtime_controller=args.claim_runtime_controller,
        claim_gameplay_acceptance=args.claim_gameplay_acceptance,
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

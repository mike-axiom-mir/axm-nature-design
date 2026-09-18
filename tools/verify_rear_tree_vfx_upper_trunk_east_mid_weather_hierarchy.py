#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from axm_nature_design.rear_tree_vfx_upper_trunk_east_mid_weather_hierarchy import (
    PASS_RESULT,
    evaluate,
)


def _svg(report: dict) -> str:
    rows = report["measurements"]["parent_rows"]
    width, height = 900, 470
    origin_x, origin_y = 450, 205
    scale = 5200.0
    wind = report["weather_visual_direction_donor"]["normalized_wind_xy"]
    chunks = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:monospace;font-size:14px}.axis{stroke:#bbb;stroke-width:1}.wind{stroke:#111;stroke-width:3}.neg{stroke:#666;stroke-width:3}.pos{stroke:#111;stroke-width:4}.base{fill:#111}</style>',
        f'<text x="24" y="28">east-mid child response relative to same-parent neutral · Weather visual direction only</text>',
        f'<line class="wind" x1="{origin_x}" y1="55" x2="{origin_x + wind[0]*100}" y2="{55 - wind[1]*100}"/>',
        f'<text x="{origin_x+115}" y="60">Weather [1.0, 0.35]</text>',
    ]
    row_y = [150, 260, 370]
    for y, row in zip(row_y, rows):
        chunks.append(f'<line class="axis" x1="140" y1="{y}" x2="780" y2="{y}"/>')
        chunks.append(f'<circle class="base" cx="{origin_x}" cy="{y}" r="4"/>')
        chunks.append(f'<text x="24" y="{y+5}">parent {row["parent_angle_deg"]:+.1f}°</text>')
        for witness in row["child_witnesses"]:
            angle = witness["child_angle_deg"]
            if angle == 0.0:
                continue
            d = witness["incremental_centroid_delta_m"]
            x2 = origin_x + d[0] * scale
            y2 = y - d[1] * scale
            cls = "pos" if angle > 0 else "neg"
            chunks.append(f'<line class="{cls}" x1="{origin_x}" y1="{y}" x2="{x2:.2f}" y2="{y2:.2f}"/>')
            chunks.append(f'<circle cx="{x2:.2f}" cy="{y2:.2f}" r="4" fill="#111"/>')
            chunks.append(f'<text x="{x2+7:.2f}" y="{y2-7:.2f}">{angle:+.0f}° · {witness["incremental_downwind_projection_m"]*1000:+.2f} mm downwind</text>')
        chunks.append(f'<text x="570" y="{y+45}">preferred {row["preferred_child_angle_deg"]:+.0f}° · separation {row["signed_child_projection_separation_m"]*1000:.2f} mm</text>')
    chunks.append('<text x="24" y="448">Diagnostic centroid vectors from exact generated geometry; not wind physics, Animation, Runtime, or Art/QA acceptance.</text>')
    chunks.append('</svg>')
    return "\n".join(chunks) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="examples/east_rear_tree_neutral_001.json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    source = json.loads(Path(args.source).read_text())
    report = evaluate(source)
    if report["result"] != PASS_RESULT:
        raise SystemExit(f"VFX hierarchy review did not pass: {report['result']}")
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "evidence.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    (out / "review.svg").write_text(_svg(report))
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

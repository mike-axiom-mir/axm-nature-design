from __future__ import annotations

import argparse
import json
from pathlib import Path

from axm_nature_design.rear_tree_vfx_weather_sign import build_review_svg, evaluate

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--svg-output", required=True)
    args = parser.parse_args()

    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    evidence = evaluate(source)
    Path(args.output).write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(args.svg_output).write_text(build_review_svg(source) + "\n", encoding="utf-8")
    print(evidence["result"])
    print(evidence["decision"]["state"])
    print(
        "review_only_downwind_alignment_angle_deg=",
        evidence["decision"]["review_only_downwind_alignment_angle_deg"],
    )
    print(
        "signed_centroid_projection_separation_m=",
        evidence["measurements"]["signed_centroid_projection_separation_m"],
    )
    return 0 if evidence["result"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())

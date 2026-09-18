#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from axm_nature_design.rear_tree_animation import RESULT, build_review_svg, evaluate

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build exact east-rear root-socket Animation evidence")
    parser.add_argument("--output", required=True)
    parser.add_argument("--svg-output", required=True)
    args = parser.parse_args()

    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    evidence = evaluate(source)
    if evidence["result"] != RESULT:
        raise SystemExit(f"unexpected Animation result: {evidence['result']}")
    if not all(evidence["checks"].values()):
        raise SystemExit("Animation evidence has a failed check")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    svg = build_review_svg(source)
    ET.fromstring(svg)
    svg_output = Path(args.svg_output)
    svg_output.parent.mkdir(parents=True, exist_ok=True)
    svg_output.write_text(svg + "\n", encoding="utf-8")

    print(RESULT)
    print(json.dumps(evidence["measurements"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

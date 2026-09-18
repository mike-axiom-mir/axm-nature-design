#!/usr/bin/env python3
"""Build retained evidence for the east/rear Nature root-socket Rigging probe."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from axm_nature_design.organic_form import load_source
from axm_nature_design.rear_tree_rigging import RESULT, evaluate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        default="examples/east_rear_tree_neutral_001.json",
        help="Exact Organic source JSON.",
    )
    parser.add_argument("--output", help="Optional evidence JSON path.")
    args = parser.parse_args()

    evidence = evaluate(load_source(args.source))
    if evidence["result"] != RESULT:
        raise SystemExit(f"Rigging evidence failed: {evidence['result']}")

    payload = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

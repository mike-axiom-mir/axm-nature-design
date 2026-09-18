#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from axm_nature_design import rear_tree_rigging_north_low_bridge_continuous_span as subject

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=ROOT / "examples/east_rear_tree_neutral_001.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source = json.loads(args.source.read_text(encoding="utf-8"))
    report = subject.evaluate(source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    cert = report["continuous_paired_span_certificate"]
    print(report["result"])
    print(f"paired_spans={cert['paired_span_count']}")
    print(f"continuous_domain_deg={cert['child_domain_deg']}")
    print(f"global_minimum_span_m={cert['global_minimum_span_m']:.17g}")
    print(f"global_minimum_pair_index={cert['global_minimum_pair_index']}")
    print(f"global_minimum_angle_deg={cert['global_minimum_angle_deg']:.17g}")
    print(f"representative_minimum_span_m={cert['representative_minimum_span_m']:.17g}")
    print(f"maximum_closed_form_vs_direct_residual_m={cert['maximum_closed_form_vs_direct_residual_m']:.17g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

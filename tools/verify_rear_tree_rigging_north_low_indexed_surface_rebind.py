#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

from axm_nature_design import rear_tree_rigging_north_low_indexed_surface_rebind as subject

ROOT = Path(__file__).resolve().parents[1]


def load_geometry_donor(path: Path):
    name = "axm_nature_design._exact_north_low_indexed_surface_geometry_donor"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load exact Geometry donor module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=ROOT / "examples/east_rear_tree_neutral_001.json")
    parser.add_argument("--geometry-module", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source = json.loads(args.source.read_text(encoding="utf-8"))
    donor = load_geometry_donor(args.geometry_module)
    if donor.RESULT != subject.GEOMETRY_DONOR_RESULT:
        raise RuntimeError("loaded Geometry donor result constant drift")
    if donor.RIGGING_OWNER_HEAD != subject.RIGGING_PREDECESSOR_HEAD:
        raise RuntimeError("loaded Geometry donor Rigging owner drift")

    geometry_report = donor.evaluate(source)
    geometry_candidate = donor.build_candidate(source)
    report = subject.evaluate(source, geometry_report, geometry_candidate)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rebind = report["receiver_rebind"]
    poses = report["representative_pose_evidence"]
    cert = report["continuous_paired_span_certificate"]
    print(report["result"])
    print(f"receiver_delta_min_m={rebind['minimum_fixed_receiver_delta_from_analytic_m']:.17g}")
    print(f"receiver_delta_max_m={rebind['maximum_fixed_receiver_delta_from_analytic_m']:.17g}")
    print(f"representative_min_triangle_area_m2={poses['minimum_bridge_triangle_area_m2']:.17g}")
    print(f"representative_min_span_m={poses['minimum_paired_bridge_span_m']:.17g}")
    print(f"continuous_min_span_m={cert['global_minimum_span_m']:.17g}")
    print(f"continuous_min_pair_index={cert['global_minimum_pair_index']}")
    print(f"continuous_min_angle_deg={cert['global_minimum_angle_deg']:.17g}")
    print(f"closed_form_residual_m={cert['maximum_closed_form_vs_direct_residual_m']:.17g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

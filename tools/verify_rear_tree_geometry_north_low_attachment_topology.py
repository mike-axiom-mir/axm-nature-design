#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from axm_nature_design import rear_tree_geometry_north_low_attachment_topology as subject

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"


def _rejects(source: dict, **kwargs) -> bool:
    try:
        subject.evaluate(source, **kwargs)
    except ValueError:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    report = subject.evaluate(source)
    controls = {
        "rigging_owner_drift_rejected": _rejects(source, requested_rigging_owner_head="0" * 40),
        "geometry_predecessor_drift_rejected": _rejects(source, requested_geometry_predecessor_head="0" * 40),
        "connected_attachment_promotion_rejected": _rejects(source, claim_connected_branch_trunk_attachment=True),
        "production_topology_promotion_rejected": _rejects(source, claim_production_topology=True),
        "skinning_acceptance_promotion_rejected": _rejects(source, claim_skinning_acceptance=True),
        "runtime_acceptance_promotion_rejected": _rejects(source, claim_runtime_acceptance=True),
    }
    if not all(controls.values()):
        raise SystemExit(f"failure control unexpectedly passed: {controls}")
    report["failure_controls"] = controls
    report["all_failure_controls_rejected"] = True

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "result": report["result"],
        "components": report["indexed_topology"]["edge_connected_components"],
        "closed_components": report["indexed_topology"]["closed_edge_manifold_components"],
        "open_components": report["indexed_topology"]["open_components"],
        "shared_indexed_vertices_with_trunk": len(report["indexed_topology"]["shared_indexed_vertices_with_trunk"]),
        "all_failure_controls_rejected": True,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

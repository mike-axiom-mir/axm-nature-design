#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from axm_nature_design.rear_tree_geometry_upper_trunk_east_mid_hierarchy import (
    RESULT,
    RIGGING_OWNER_HEAD,
    evaluate,
)

SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"
CONTRACT_PATH = ROOT / "contracts" / "east-rear-upper-trunk-east-mid-geometry-rebind-004.json"


def expect_rejection(label: str, action) -> dict:
    try:
        action()
    except Exception as exc:
        return {"label": label, "rejected": True, "error": f"{type(exc).__name__}: {exc}"}
    raise AssertionError(f"negative control unexpectedly passed: {label}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    before = copy.deepcopy(source)
    evidence = evaluate(source)
    if source != before:
        raise RuntimeError("Geometry evaluator mutated Organic source")
    if evidence["result"] != RESULT:
        raise RuntimeError(f"Geometry hierarchy rebind did not pass: {evidence['result']}")
    if evidence["lineage"]["rigging_hierarchy_owner_head"] != RIGGING_OWNER_HEAD:
        raise RuntimeError("exact Rigging hierarchy owner identity drift")
    if evidence["receiver"]["selected_vertices"] != 52 or evidence["receiver"]["owned_triangles"] != 72:
        raise RuntimeError("exact east-mid child structural cardinality drift")
    if evidence["receiver"]["partial_selected_triangles"] != 0:
        raise RuntimeError("east-mid child partition is no longer triangle-closed")
    if evidence["continuous_structural_certificate"]["continuous_child_topology_isometry"] is not True:
        raise RuntimeError("continuous child topology isometry certificate missing")
    if evidence["continuous_structural_certificate"]["predecessor_five_child_continuous_clearance_transferred"] is not False:
        raise RuntimeError("historical five-child clearance was incorrectly transferred")

    controls = [
        expect_rejection(
            "rigging-owner-head-drift",
            lambda: evaluate(source, requested_rigging_owner_head="0" * 40),
        ),
        expect_rejection(
            "historical-clearance-transfer",
            lambda: evaluate(source, claim_predecessor_five_child_clearance_transfer=True),
        ),
        expect_rejection(
            "trunk-mesh-deformation-promotion",
            lambda: evaluate(source, claim_trunk_mesh_deformation=True),
        ),
        expect_rejection(
            "surface-attachment-promotion",
            lambda: evaluate(source, claim_surface_attachment=True),
        ),
        expect_rejection(
            "collision-gameplay-promotion",
            lambda: evaluate(source, claim_collision_or_gameplay=True),
        ),
    ]
    payload = {
        **evidence,
        "contract": json.loads(CONTRACT_PATH.read_text(encoding="utf-8")),
        "failure_controls": controls,
        "all_failure_controls_rejected": all(row["rejected"] for row in controls),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "result": payload["result"],
        "selected_vertices": payload["receiver"]["selected_vertices"],
        "owned_triangles": payload["receiver"]["owned_triangles"],
        "witness_count": payload["representative_recheck"]["witness_count"],
        "max_triangle_area_drift_m2": payload["representative_recheck"]["maximum_owned_triangle_area_drift_m2"],
        "max_pairwise_distance_drift_m": payload["representative_recheck"]["maximum_selected_pairwise_distance_drift_m"],
        "historical_clearance_transferred": payload["continuous_structural_certificate"]["predecessor_five_child_continuous_clearance_transferred"],
        "all_failure_controls_rejected": payload["all_failure_controls_rejected"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

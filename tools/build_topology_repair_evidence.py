#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axm_nature_design.organic_form import build_mesh, load_source
from axm_nature_design.topology_repair import evaluate, repair_tapered_segment_cap_winding

SOURCES = [
    ROOT / "examples" / "sapling_neutral_001.json",
    ROOT / "examples" / "compact_east_tree_neutral_001.json",
]


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "evidence" / "tapered-cap-winding-001"
    out.mkdir(parents=True, exist_ok=True)
    summary = []
    for source_path in SOURCES:
        source = load_source(source_path)
        baseline = build_mesh(source)
        candidate, _ = repair_tapered_segment_cap_winding(baseline)
        report = evaluate(source)
        if report["status"] != "PASS_TAPERED_CAP_WINDING_REPAIR":
            raise SystemExit(f"topology repair failed for {source['study_id']}")
        stem = source["study_id"]
        (out / f"{stem}-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (out / f"{stem}-candidate-mesh.json").write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summary.append({
            "study_id": stem,
            "source_digest": report["source_digest"],
            "baseline_mesh_digest": report["baseline_mesh_digest"],
            "candidate_mesh_digest": report["candidate_mesh_digest"],
            "flipped_triangle_count": report["flipped_triangle_count"],
            "before": report["before"],
            "after": report["after"],
            "status": report["status"],
        })
    (out / "summary.json").write_text(json.dumps({
        "schema": "axm.nature-tapered-cap-winding-evidence-set/v0.1",
        "state": "PASS_TWO_REAL_OUTPUTS" if all(item["status"].startswith("PASS_") for item in summary) else "FAIL",
        "items": summary,
        "non_claims": [
            "source geometry authority unchanged",
            "no vertex positions changed",
            "no connected vegetation topology claim",
            "no self-intersection or deformation claim",
            "no visual, runtime, collision or gameplay acceptance claim",
        ],
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

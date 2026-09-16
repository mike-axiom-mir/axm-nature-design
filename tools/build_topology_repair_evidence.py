#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axm_nature_design.organic_form import build_mesh, load_source
from axm_nature_design.topology_repair import evaluate, repair_tapered_segment_cap_winding

LOCAL_SOURCES = [
    ROOT / "examples" / "sapling_neutral_001.json",
    ROOT / "examples" / "compact_east_tree_neutral_001.json",
]


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "evidence" / "tapered-cap-winding-001"
    external_source = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None
    external_ref = sys.argv[3] if len(sys.argv) > 3 else None
    out.mkdir(parents=True, exist_ok=True)

    sources = [(path, "LOCAL_BRANCH", None) for path in LOCAL_SOURCES]
    if external_source is not None:
        if not external_source.is_file():
            raise SystemExit(f"external source not found: {external_source}")
        if not external_ref:
            raise SystemExit("external source requires an exact donor ref")
        sources.append((external_source, "EXACT_EXTERNAL_DONOR", external_ref))

    summary = []
    for source_path, provenance_kind, provenance_ref in sources:
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
            "source_path": str(source_path),
            "provenance_kind": provenance_kind,
            "provenance_ref": provenance_ref,
            "source_digest": report["source_digest"],
            "baseline_mesh_digest": report["baseline_mesh_digest"],
            "candidate_mesh_digest": report["candidate_mesh_digest"],
            "flipped_triangle_count": report["flipped_triangle_count"],
            "before": report["before"],
            "after": report["after"],
            "status": report["status"],
        })

    expected_count = 3 if external_source is not None else 2
    passed = len(summary) == expected_count and all(item["status"].startswith("PASS_") for item in summary)
    state = f"PASS_{expected_count}_REAL_OUTPUTS" if passed else "FAIL"
    (out / "summary.json").write_text(json.dumps({
        "schema": "axm.nature-tapered-cap-winding-evidence-set/v0.2",
        "state": state,
        "source_count": len(summary),
        "items": summary,
        "non_claims": [
            "source geometry authority unchanged",
            "external donor remains source-owned at its exact ref",
            "no vertex positions changed",
            "no connected vegetation topology claim",
            "no self-intersection or deformation claim",
            "no visual, runtime, collision or gameplay acceptance claim",
            "no source-generator migration claim",
        ],
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not passed:
        raise SystemExit("evidence set did not satisfy exact expected source count/status")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

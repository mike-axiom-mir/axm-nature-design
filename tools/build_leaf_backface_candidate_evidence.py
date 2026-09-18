from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axm_nature_design.leaf_backface_candidate import add_explicit_leaf_backfaces, evaluate
from axm_nature_design.organic_form import build_mesh, load_source

SOURCES = [
    ROOT / "examples" / "sapling_neutral_001.json",
    ROOT / "examples" / "compact_east_tree_neutral_001.json",
    ROOT / "examples" / "east_rear_tree_neutral_001.json",
]


def main(output_dir: str) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    reports = []
    for path in SOURCES:
        source = load_source(path)
        baseline = build_mesh(source)
        candidate = add_explicit_leaf_backfaces(baseline)
        report = evaluate(source)
        reports.append(report)
        stem = source["study_id"]
        (out / f"{stem}-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (out / f"{stem}-candidate-mesh.json").write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    state = "PASS_EXPLICIT_LEAF_BACKFACE_CANDIDATE_3_REAL_OUTPUTS" if all(
        item["status"] == "PASS_EXPLICIT_DISJOINT_LEAF_BACKFACE_CANDIDATE" for item in reports
    ) else "FAIL"
    summary = {
        "schema": "axm.nature-leaf-backface-candidate-summary/v0.1",
        "state": state,
        "source_count": len(reports),
        "base_source_migration_ref": reports[0]["base_source_migration_ref"] if reports else None,
        "items": reports,
        "truth_boundary": {
            "source_generator_changed": False,
            "candidate_only": True,
            "target_renderer_evidence": False,
            "visual_acceptance": False,
            "runtime_acceptance": False,
            "deformation_acceptance": False,
            "game_readiness": False,
            "geometry_mastery": False,
        },
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if state != "PASS_EXPLICIT_LEAF_BACKFACE_CANDIDATE_3_REAL_OUTPUTS":
        raise SystemExit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: build_leaf_backface_candidate_evidence.py OUTPUT_DIR")
    main(sys.argv[1])

#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axm_nature_design.organic_form import build_mesh, load_source
from axm_nature_design.source_topology_migration import GEOMETRY_ORACLE_REF, evaluate

SOURCES = [
    ROOT / "examples" / "sapling_neutral_001.json",
    ROOT / "examples" / "compact_east_tree_neutral_001.json",
    ROOT / "examples" / "east_rear_tree_neutral_001.json",
]


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "evidence" / "source-topology-migration-001"
    out.mkdir(parents=True, exist_ok=True)

    items = []
    for source_path in SOURCES:
        source = load_source(source_path)
        report = evaluate(source)
        if report["status"] != "PASS_SOURCE_GENERATOR_WINDING_MIGRATION":
            raise SystemExit(f"source topology migration failed for {source['study_id']}")
        mesh = build_mesh(source)
        stem = source["study_id"]
        (out / f"{stem}-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (out / f"{stem}-migrated-mesh.json").write_text(json.dumps(mesh, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        items.append({
            "study_id": stem,
            "source_ref": report["source_ref"],
            "source_digest": report["source_digest"],
            "historical_mesh_digest": report["historical_mesh_digest"],
            "proven_reindex_digest": report["proven_reindex_digest"],
            "migrated_mesh_digest": report["migrated_mesh_digest"],
            "topology": report["topology"],
            "status": report["status"],
        })

    passed = len(items) == 3 and all(item["status"] == "PASS_SOURCE_GENERATOR_WINDING_MIGRATION" for item in items)
    summary = {
        "schema": "axm.nature-source-topology-migration-evidence-set/v0.1",
        "state": "PASS_SOURCE_GENERATOR_MIGRATION_3_REAL_OUTPUTS" if passed else "FAIL",
        "source_count": len(items),
        "geometry_oracle_ref": GEOMETRY_ORACLE_REF,
        "items": items,
        "non_claims": [
            "historical source and mesh receipts remain valid for their exact old identities",
            "source JSON and authored form semantics are unchanged",
            "only tapered-cap index emission is migrated",
            "no connected production vegetation topology claim",
            "no self-intersection, normals, tangents, UV, deformation or wind acceptance claim",
            "no receiving-scene visual acceptance claim",
            "no target-device runtime, collision, navigation or gameplay acceptance claim",
            "no CANON, production readiness, game readiness or Geometry mastery claim",
        ],
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not passed:
        raise SystemExit("source topology migration evidence did not pass all three exact sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

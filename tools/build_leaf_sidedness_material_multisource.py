#!/usr/bin/env python3
"""Build a bounded three-source Materials A/B packet for Nature leaf sidedness.

This extends the existing one-sapling renderer comparison without replacing it.
For each exact current Nature source from Geometry PR #10 it compares:

A. migrated single-sided source geometry + foliage culling disabled at material level;
B. Geometry PR #10's explicit disjoint opposite-wound leaf backfaces + ordinary culling.

The scalar review materials are held identical between strategies. Reusing the
existing sapling lookdev values on the two additional studies is observation-only
and does not widen that profile's source ownership or claim material adoption.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

SCHEMA = "axm.nature-leaf-sidedness-material-multisource/v0.2"
GEOMETRY_HEAD = "da3adbef4de8cddb8f3ebe841d39bb31a8936f5f"
PROFILE_FILE = "lookdev/sapling_material_profile_001.json"
STUDIES = (
    ("sapling-neutral-001", "examples/sapling_neutral_001.json"),
    ("compact-east-tree-neutral-001", "examples/compact_east_tree_neutral_001.json"),
    ("east-rear-tree-neutral-001", "examples/east_rear_tree_neutral_001.json"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--geometry-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    geometry_root = args.geometry_root.resolve()
    sys.path.insert(0, str(geometry_root / "src"))

    from axm_nature_design.organic_form import build_mesh, digest
    from axm_nature_design.leaf_backface_candidate import add_explicit_leaf_backfaces, evaluate

    profile = json.loads(Path(PROFILE_FILE).read_text())
    if profile.get("schema") != "axm.nature-sapling-material-profile/v0.1":
        raise SystemExit("unexpected Materials profile schema")
    if profile.get("source_scope") != "sapling-neutral-001":
        raise SystemExit("reference Materials profile source scope drifted")

    studies: dict[str, dict] = {}
    source_digests: set[str] = set()
    baseline_digests: set[str] = set()
    explicit_digests: set[str] = set()

    for expected_study_id, source_file in STUDIES:
        source = json.loads((geometry_root / source_file).read_text())
        if source.get("study_id") != expected_study_id:
            raise SystemExit(
                f"unexpected source study for {source_file}: {source.get('study_id')!r}"
            )

        geometry_evidence = evaluate(source)
        if geometry_evidence.get("status") != "PASS_EXPLICIT_DISJOINT_LEAF_BACKFACE_CANDIDATE":
            raise SystemExit(
                f"exact Geometry donor is not structurally passing for {expected_study_id}: "
                f"{geometry_evidence}"
            )

        baseline = build_mesh(source)
        explicit = add_explicit_leaf_backfaces(baseline)
        baseline_digest = digest(baseline)
        explicit_digest = digest(explicit)

        checks = {
            "geometry_candidate_structurally_passes": geometry_evidence["status"]
            == "PASS_EXPLICIT_DISJOINT_LEAF_BACKFACE_CANDIDATE",
            "baseline_digest_matches_geometry_evidence": baseline_digest
            == geometry_evidence["baseline_mesh_digest"],
            "explicit_digest_matches_geometry_evidence": explicit_digest
            == geometry_evidence["candidate_mesh_digest"],
            "baseline_is_390_vertices_570_triangles": len(baseline["vertices"]) == 390
            and len(baseline["triangles"]) == 570,
            "explicit_is_490_vertices_620_triangles": len(explicit["vertices"]) == 490
            and len(explicit["triangles"]) == 620,
            "baseline_vertices_are_exact_prefix": explicit["vertices"][: len(baseline["vertices"])]
            == baseline["vertices"],
            "baseline_triangles_are_exact_prefix": explicit["triangles"][: len(baseline["triangles"])]
            == baseline["triangles"],
            "material_values_identical_between_strategies": True,
        }
        if not all(checks.values()):
            raise SystemExit(f"leaf sidedness packet checks failed for {expected_study_id}: {checks}")

        source_digests.add(geometry_evidence["source_digest"])
        baseline_digests.add(baseline_digest)
        explicit_digests.add(explicit_digest)
        studies[expected_study_id] = {
            "study_id": expected_study_id,
            "source_file": source_file,
            "source_digest": geometry_evidence["source_digest"],
            "baseline_mesh_digest": baseline_digest,
            "explicit_mesh_digest": explicit_digest,
            "geometry_status": geometry_evidence["status"],
            "comparison_contract": {
                "baseline_strategy": "MIGRATED_SINGLE_SIDED_SOURCE_MESH_PLUS_FOLIAGE_CULL_DISABLED",
                "explicit_strategy": "GEOMETRY_PR10_DISJOINT_OPPOSITE_WOUND_BACKFACES_PLUS_CULL_BACK",
                "woody_cull_mode_both": "CULL_BACK",
                "material_color_metallic_roughness": "IDENTICAL_BOTH_STRATEGIES",
                "lighting_and_cameras": "IDENTICAL_WITHIN_EACH_STUDY_CONTEXT",
                "source_form_changes": "NONE",
                "baseline_vertices": len(baseline["vertices"]),
                "explicit_vertices": len(explicit["vertices"]),
                "baseline_triangles": len(baseline["triangles"]),
                "explicit_triangles": len(explicit["triangles"]),
                "triangle_delta": len(explicit["triangles"]) - len(baseline["triangles"]),
                "triangle_delta_percent_of_baseline": round(
                    (len(explicit["triangles"]) - len(baseline["triangles"]))
                    * 100.0
                    / len(baseline["triangles"]),
                    9,
                ),
            },
            "baseline_mesh": baseline,
            "explicit_mesh": explicit,
            "geometry_evidence": geometry_evidence,
            "checks": checks,
        }

    global_checks = {
        "geometry_donor_head_is_exact": GEOMETRY_HEAD
        == "da3adbef4de8cddb8f3ebe841d39bb31a8936f5f",
        "exactly_three_materially_different_sources": len(studies) == 3
        and len(source_digests) == 3,
        "three_distinct_baseline_meshes": len(baseline_digests) == 3,
        "three_distinct_explicit_meshes": len(explicit_digests) == 3,
        "reference_material_profile_remains_sapling_scoped": profile["source_scope"]
        == "sapling-neutral-001",
    }
    if not all(global_checks.values()):
        raise SystemExit(f"multi-source leaf sidedness checks failed: {global_checks}")

    payload = {
        "schema": SCHEMA,
        "state": "PASS_EXACT_MULTI_SOURCE_LEAF_SIDEDNESS_MATERIAL_AB_PACKET",
        "materials_head": os.environ.get("AXM_MATERIALS_HEAD", "LOCAL_OR_UNBOUND"),
        "geometry_donor": {
            "repository": "mike-axiom-mir/axm-nature-design",
            "head": GEOMETRY_HEAD,
            "pr": 10,
            "status": "THREE_EXACT_CURRENT_SOURCE_OUTPUTS_REBUILT_FROM_PINNED_DONOR",
        },
        "review_material_profile": profile,
        "review_material_policy": (
            "The existing sapling lookdev scalar values are reused unchanged only as a fixed renderer "
            "reference so sidedness strategies can be compared across three source forms. This does not "
            "widen sapling_material_profile_001 source ownership to compact-east or east-rear trees."
        ),
        "studies": studies,
        "global_checks": global_checks,
        "truth_boundary": {
            "cross_source_material_profile_adoption": False,
            "two_sided_material_visual_equivalence_proven": False,
            "explicit_geometry_preferred": False,
            "material_cull_disabled_preferred": False,
            "runtime_cost_accepted": False,
            "final_leaf_shader_or_normals_accepted": False,
            "source_migration_requested": False,
            "map_or_vfx_acceptance": False,
            "canon_or_production_readiness": False,
        },
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "comparison.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    )
    (args.output / "exact-head.txt").write_text(payload["materials_head"] + "\n")
    print(
        json.dumps(
            {
                "state": payload["state"],
                "global_checks": global_checks,
                "studies": {
                    key: value["comparison_contract"] for key, value in studies.items()
                },
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build a bounded three-source Materials A/B packet for Nature leaf sidedness.

For each exact current Nature source from Geometry PR #10 this compares:

A. migrated single-sided source geometry + foliage culling disabled at material level;
B. Geometry PR #10's explicit disjoint opposite-wound leaf backfaces + ordinary culling.

The scalar/color material payload is held identical between strategies. By default
this preserves the historical sapling-profile reference proof. A caller may instead
supply the already-evidenced three-source woody/foliage family profile to test the
composition of that family candidate with the sidedness strategies without changing
geometry, source ownership, or runtime acceptance.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

SCHEMA = "axm.nature-leaf-sidedness-material-multisource/v0.2"
GEOMETRY_HEAD = "da3adbef4de8cddb8f3ebe841d39bb31a8936f5f"
DEFAULT_PROFILE_FILE = Path("lookdev/sapling_material_profile_001.json")
FAMILY_PROFILE_FILE = Path("lookdev/nature_woody_foliage_family_001.json")
EXPECTED_STUDIES = (
    "sapling-neutral-001",
    "compact-east-tree-neutral-001",
    "east-rear-tree-neutral-001",
)
STUDIES = (
    ("sapling-neutral-001", "examples/sapling_neutral_001.json"),
    ("compact-east-tree-neutral-001", "examples/compact_east_tree_neutral_001.json"),
    ("east-rear-tree-neutral-001", "examples/east_rear_tree_neutral_001.json"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--geometry-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--profile",
        type=Path,
        default=DEFAULT_PROFILE_FILE,
        help=(
            "Material profile to hold identical across sidedness strategies. "
            "Supported inputs are the historical sapling profile and the bounded "
            "three-source woody/foliage family profile."
        ),
    )
    return parser.parse_args()


def load_profile(path: Path) -> tuple[dict, str, str]:
    profile = json.loads(path.read_text())
    schema = profile.get("schema")
    if schema == "axm.nature-sapling-material-profile/v0.1":
        if profile.get("source_scope") != "sapling-neutral-001":
            raise SystemExit("reference Materials profile source scope drifted")
        return (
            profile,
            "SAPLING_REVIEW_REFERENCE_ONLY",
            (
                "The existing sapling lookdev scalar values are reused unchanged only as a fixed "
                "renderer reference so sidedness strategies can be compared across three source "
                "forms. This does not widen sapling_material_profile_001 source ownership to "
                "compact-east or east-rear trees."
            ),
        )
    if schema == "axm.nature-woody-foliage-material-family/v0.1":
        if profile.get("family_id") != "nature-woody-foliage-family-001":
            raise SystemExit("unexpected woody/foliage family identity")
        if profile.get("supported_source_scope") != list(EXPECTED_STUDIES):
            raise SystemExit("bounded woody/foliage family source scope drifted")
        return (
            profile,
            "BOUNDED_THREE_SOURCE_FAMILY_CANDIDATE",
            (
                "The separately evidenced bounded three-source woody/foliage family candidate is "
                "held identical across both sidedness strategies. This composes two existing "
                "Materials candidates for direct rendering without promoting either strategy into "
                "Environment, Runtime, CANON, or final Art Direction."
            ),
        )
    raise SystemExit(f"unsupported Materials profile schema: {schema!r}")


def main() -> int:
    args = parse_args()
    geometry_root = args.geometry_root.resolve()
    sys.path.insert(0, str(geometry_root / "src"))

    from axm_nature_design.organic_form import build_mesh, digest
    from axm_nature_design.leaf_backface_candidate import add_explicit_leaf_backfaces, evaluate

    profile, profile_mode, review_policy = load_profile(args.profile)

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
        "material_profile_mode_is_supported": profile_mode
        in {"SAPLING_REVIEW_REFERENCE_ONLY", "BOUNDED_THREE_SOURCE_FAMILY_CANDIDATE"},
        "family_scope_exact_when_family_mode": (
            profile_mode != "BOUNDED_THREE_SOURCE_FAMILY_CANDIDATE"
            or profile.get("supported_source_scope") == list(EXPECTED_STUDIES)
        ),
        "sapling_scope_exact_when_reference_mode": (
            profile_mode != "SAPLING_REVIEW_REFERENCE_ONLY"
            or profile.get("source_scope") == "sapling-neutral-001"
        ),
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
        "material_profile_path": str(args.profile),
        "profile_mode": profile_mode,
        "review_material_profile": profile,
        "review_material_policy": review_policy,
        "renderer_truth_boundary": (
            "Pinned Godot 4.7.2 GL Compatibility observation of three exact Nature source forms "
            "comparing material-level disabled foliage culling against explicit opposite-wound "
            "leaf backface geometry while the selected material profile, lighting and camera "
            "derivation are held fixed within each source/context. This does not prove final leaf "
            "shader/normals, botanical correctness, target-device runtime cost, Environment/VFX "
            "acceptance, CANON, production readiness, or Materials mastery."
        ),
        "studies": studies,
        "global_checks": global_checks,
        "truth_boundary": {
            "cross_source_material_profile_adoption": False,
            "family_candidate_composition_observed": profile_mode
            == "BOUNDED_THREE_SOURCE_FAMILY_CANDIDATE",
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
                "profile_mode": profile_mode,
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

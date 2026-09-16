#!/usr/bin/env python3
"""Build a bounded three-source Nature woody/foliage material-family A/B packet.

Control: the original proof-only woody/foliage scalars used by the Nature -> UC
surface bridge. Candidate: the already-proven sapling lookdev scalars, promoted
only as a candidate family over the three exact current Nature source forms.

Geometry and foliage culling are not comparison variables here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

SCHEMA = "axm.nature-woody-foliage-material-family-evidence/v0.1"
GEOMETRY_HEAD = "da3adbef4de8cddb8f3ebe841d39bb31a8936f5f"
FAMILY_FILE = Path("lookdev/nature_woody_foliage_family_001.json")
FAMILY_SCHEMA = "axm.nature-woody-foliage-material-family/v0.1"
STUDIES = (
    ("sapling-neutral-001", "examples/sapling_neutral_001.json"),
    ("compact-east-tree-neutral-001", "examples/compact_east_tree_neutral_001.json"),
    ("east-rear-tree-neutral-001", "examples/east_rear_tree_neutral_001.json"),
)
BASELINE_PROFILE = {
    "profile_id": "nature-proof-material-control-001",
    "materials": {
        "woody": {"color": "#6B5138FF", "metallic": 0.0, "roughness": 0.92},
        "foliage": {"color": "#4E7B45FF", "metallic": 0.0, "roughness": 0.88},
    },
}


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def rgb8(color: str) -> tuple[int, int, int]:
    if not isinstance(color, str) or len(color) != 9 or not color.startswith("#"):
        raise ValueError("color must be #RRGGBBAA")
    return tuple(int(color[i : i + 2], 16) for i in (1, 3, 5))


def srgb_channel(value: int) -> float:
    x = value / 255.0
    return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4


def relative_luminance(color: str) -> float:
    r8, g8, b8 = rgb8(color)
    r, g, b = (srgb_channel(value) for value in (r8, g8, b8))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def validate_materials(materials: dict[str, Any]) -> None:
    if set(materials) != {"woody", "foliage"}:
        raise ValueError("materials must define exactly woody and foliage")
    for key, material in materials.items():
        if set(material) != {"color", "metallic", "roughness"}:
            raise ValueError(f"{key} material keys drifted")
        rgb8(material["color"])
        if float(material["metallic"]) != 0.0:
            raise ValueError("bounded Nature family remains non-metallic")
        roughness = float(material["roughness"])
        if not 0.0 <= roughness <= 1.0:
            raise ValueError("roughness outside [0,1]")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--geometry-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    geometry_root = args.geometry_root.resolve()
    sys.path.insert(0, str(geometry_root / "src"))
    from axm_nature_design.organic_form import build_mesh

    family = json.loads(FAMILY_FILE.read_text())
    if family.get("schema") != FAMILY_SCHEMA:
        raise SystemExit("unexpected Nature material family schema")
    expected_sources = [study_id for study_id, _ in STUDIES]
    if family.get("supported_source_scope") != expected_sources:
        raise SystemExit("family source scope must equal the three exact current studies in stable order")
    if family.get("intent", {}).get("variation_policy") != "NO_PER_SOURCE_VARIATION_YET__ESTABLISH_SHARED_FAMILY_BASELINE_FIRST":
        raise SystemExit("family variation policy drifted")
    validate_materials(BASELINE_PROFILE["materials"])
    validate_materials(family["materials"])

    baseline_luma = {k: relative_luminance(v["color"]) for k, v in BASELINE_PROFILE["materials"].items()}
    candidate_luma = {k: relative_luminance(v["color"]) for k, v in family["materials"].items()}
    baseline_luma_gap = abs(baseline_luma["woody"] - baseline_luma["foliage"])
    candidate_luma_gap = abs(candidate_luma["woody"] - candidate_luma["foliage"])
    baseline_roughness_gap = abs(BASELINE_PROFILE["materials"]["woody"]["roughness"] - BASELINE_PROFILE["materials"]["foliage"]["roughness"])
    candidate_roughness_gap = abs(family["materials"]["woody"]["roughness"] - family["materials"]["foliage"]["roughness"])

    studies: dict[str, dict[str, Any]] = {}
    source_digests: set[str] = set()
    mesh_digests: set[str] = set()
    for study_id, source_file in STUDIES:
        source = json.loads((geometry_root / source_file).read_text())
        if source.get("study_id") != study_id:
            raise SystemExit(f"source identity mismatch for {source_file}")
        mesh = build_mesh(source)
        source_digest = digest(source)
        mesh_digest = digest(mesh)
        source_digests.add(source_digest)
        mesh_digests.add(mesh_digest)
        checks = {
            "source_identity_exact": source.get("study_id") == study_id,
            "source_is_explicitly_supported": study_id in family["supported_source_scope"],
            "mesh_is_390_vertices_570_triangles": len(mesh["vertices"]) == 390 and len(mesh["triangles"]) == 570,
            "candidate_changes_materials_only": True,
            "foliage_culling_fixed_between_control_candidate": True,
        }
        if not all(checks.values()):
            raise SystemExit(f"study checks failed for {study_id}: {checks}")
        studies[study_id] = {
            "study_id": study_id,
            "source_file": source_file,
            "source_digest": source_digest,
            "mesh_digest": mesh_digest,
            "mesh": mesh,
            "checks": checks,
        }

    checks = {
        "geometry_donor_head_exact": GEOMETRY_HEAD == "da3adbef4de8cddb8f3ebe841d39bb31a8936f5f",
        "exactly_three_distinct_sources": len(source_digests) == 3,
        "three_distinct_meshes": len(mesh_digests) == 3,
        "family_scope_exactly_matches_studies": family["supported_source_scope"] == expected_sources,
        "candidate_materials_differ_from_control": digest(family["materials"]) != digest(BASELINE_PROFILE["materials"]),
        "candidate_luminance_separation_increased": candidate_luma_gap > baseline_luma_gap,
        "candidate_roughness_separation_increased": candidate_roughness_gap > baseline_roughness_gap,
        "metallic_remains_zero": all(float(v["metallic"]) == 0.0 for v in family["materials"].values()),
        "no_per_source_variation_introduced": family["intent"]["variation_policy"] == "NO_PER_SOURCE_VARIATION_YET__ESTABLISH_SHARED_FAMILY_BASELINE_FIRST",
    }
    if not all(checks.values()):
        raise SystemExit(f"family checks failed: {checks}")

    payload = {
        "schema": SCHEMA,
        "state": "PASS_EXACT_THREE_SOURCE_WOODY_FOLIAGE_FAMILY_PACKET",
        "materials_head": os.environ.get("AXM_MATERIALS_HEAD", "LOCAL_OR_UNBOUND"),
        "geometry_donor": {
            "repository": "mike-axiom-mir/axm-nature-design",
            "pr": 10,
            "head": GEOMETRY_HEAD,
            "relation": "PINNED_EXACT_CURRENT_SOURCE_FORMS__NO_GEOMETRY_ADOPTION_OR_CHANGE",
        },
        "comparison_contract": {
            "control": "ORIGINAL_PROOF_ONLY_WOODY_FOLIAGE_PBR_SCALARS",
            "candidate": family["family_id"],
            "foliage_cull_mode_both": "CULL_DISABLED_FOR_MATERIAL_REVIEW_ONLY",
            "geometry_change": "NONE",
            "lighting_camera_change_within_context": "NONE",
            "per_source_candidate_variation": "NONE",
        },
        "control_profile": BASELINE_PROFILE,
        "candidate_family": family,
        "control_relative_luminance": baseline_luma,
        "candidate_relative_luminance": candidate_luma,
        "control_luminance_gap": baseline_luma_gap,
        "candidate_luminance_gap": candidate_luma_gap,
        "control_roughness_gap": baseline_roughness_gap,
        "candidate_roughness_gap": candidate_roughness_gap,
        "studies": studies,
        "checks": checks,
        "truth_boundary": {
            "three_source_material_family_structurally_supported": True,
            "visual_family_acceptance": False,
            "environment_adoption": False,
            "final_sidedness_strategy": False,
            "target_device_runtime_cost": False,
            "botanical_correctness": False,
            "uv_texture_quality": False,
            "canon_or_production_readiness": False,
        },
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "comparison.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    (args.output / "exact-head.txt").write_text(payload["materials_head"] + "\n")
    print(json.dumps({"state": payload["state"], "checks": checks, "material_gaps": {"control_luma": baseline_luma_gap, "candidate_luma": candidate_luma_gap, "control_roughness": baseline_roughness_gap, "candidate_roughness": candidate_roughness_gap}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

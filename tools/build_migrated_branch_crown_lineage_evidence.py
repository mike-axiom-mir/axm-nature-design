#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axm_nature_design.organic_form import build_mesh, digest, load_source
from axm_nature_design.procedural_family import generate_accepted_variant, load_family
from axm_nature_design.source_topology_migration import inspect_shared_edge_orientation

SCHEMA = "axm.nature-branch-crown-migrated-lineage-evidence/v0.1"
MIGRATION_REF = "4ddbe66e5c02d22407ef773d5346a2fe6f349a2d"
HISTORICAL_PROCEDURAL_HEAD = "d535484d4c3623a32fc9f5dc44b0856619b9b1ec"
HISTORICAL_ARTIFACT_ID = 10434505038
HISTORICAL_ARTIFACT_SHA256 = "7098f308b63bd4b6d8e121255f67378979045d6849abd9c22370bd4d087b9102"
HISTORICAL_MUTATOR_BLOB = "2e405aa3a7a85228d61cc1f1d3dd76e06aaa2341"
HISTORICAL_FAMILY_BLOBS = {
    "examples/sapling_variation_family_001.json": "ce06ab419e8866a28448618af69b35d8cea60311",
    "examples/compact_tree_variation_family_001.json": "72ed799e2e7b35aad7cec1a35b09c3d7134fbd4e",
    "examples/east_rear_tree_variation_family_001.json": "51ad3dd368b7a73fc5cf50c6ade63ceddc85ce53",
}

# Exact prior retained identities from artifact 10434505038.  Source digests must
# remain byte-identical under the same parameters; mesh digests must change because
# the Nature source generator now emits the proven cap winding migration.
CASES = [
    {
        "case_id": "sapling-west-a",
        "source_path": "examples/sapling_neutral_001.json",
        "family_path": "examples/sapling_variation_family_001.json",
        "source_origin_ref": "fbc202449981f2bac153951c561ed0ed6120c936",
        "historical": {
            11: ("e4b4a27b7455c5960fb7a55d24581d9255a9ca9efbc9296a107b0205b6a96d29", "8615b98886005e248dbec22b23cb4ec1e7e71632d65bd4baaab9252b8e897009"),
            47: ("887fac85fe624125cb9b2ac3298ad4a4e575292b97ce58a971c1cc3ab45578d5", "b5cd1ac0ee272f2427386be6b5d164838624b456a340d1c811dc61a1b8349a3d"),
            101: ("257c2445ad01a358e78cd0ab181566074968877a6e5932fedf2582f3671c513b", "a07152d4a72d0ad709d98d7b5667af4891daf8f98b1728c90b1b1d0492bf35b2"),
        },
    },
    {
        "case_id": "compact-east-b",
        "source_path": "examples/compact_east_tree_neutral_001.json",
        "family_path": "examples/compact_tree_variation_family_001.json",
        "source_origin_ref": "64116d63fc76daa1623b5fd5046a4e6074100bda",
        "historical": {
            17: ("7e6aadbc74265d73a1485aa79e7fee8ad770a7097de21b042a47d58625253fee", "6f51d2feea576d7ae814e5538effd113888297f3f07403be14a1aa80948f4623"),
            59: ("1f62b250782729851d3fd64fb99c96a0846bfa463039e38995cbc404401ae8ac", "db7a7b8dd25db99daf0a0d685ea23323f15088d1b87412a307e196e069de9db3"),
            131: ("06b8766fce1c7e774f272e4f838b5eae7a5dcef64ff145eab5294e13e08a6d69", "f561e821b337f07656fec08a5fcb6c5d8c3ff9600dec77a505f74c91ccb07e5d"),
        },
    },
    {
        "case_id": "east-rear-a",
        "source_path": "examples/east_rear_tree_neutral_001.json",
        "family_path": "examples/east_rear_tree_variation_family_001.json",
        "source_origin_ref": "a4e5ee011e1d87f47866a7e6c6f4e66f57b6af12",
        "historical": {
            23: ("e0be3708658d5eafaf16a03685365d2a66a557d8f996f6a5b9f439bd9b8d5c52", "7fef08f5760bf3c2967a260a63562fb1f8271c4e2b3c1c2d226f9d6db3cbc091"),
            71: ("d85370d7b3a3b02f50064676d8ab8d8a0659b31e84be48bee412b99c3cc23c26", "4acaee105250b92e4b7da7803ff68a6a394008cd392841718243bf2b912f78ac"),
            149: ("befb571ad4a425491054805306506c245b262156924d283c1fe119a56e2dc91d", "33108363590b83295a97040e2163cbfa9fd2f0f0f1ebeb8b8cff28254e686102"),
        },
    },
]


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head(root: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def git_blob(root: Path, relative_path: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "hash-object", relative_path],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def validate_code_and_profile_identity(migrated_root: Path) -> dict:
    observed_migration = git_head(migrated_root)
    if observed_migration != MIGRATION_REF:
        raise RuntimeError(f"migration donor drift: {observed_migration} != {MIGRATION_REF}")

    local_generator = ROOT / "src" / "axm_nature_design" / "organic_form.py"
    donor_generator = migrated_root / "src" / "axm_nature_design" / "organic_form.py"
    local_generator_sha = sha256_file(local_generator)
    donor_generator_sha = sha256_file(donor_generator)
    if local_generator_sha != donor_generator_sha:
        raise RuntimeError("local Nature generator differs from the exact migrated donor")

    mutator_blob = git_blob(ROOT, "src/axm_nature_design/procedural_family.py")
    if mutator_blob != HISTORICAL_MUTATOR_BLOB:
        raise RuntimeError(f"procedural mutator drifted: {mutator_blob} != {HISTORICAL_MUTATOR_BLOB}")

    family_blobs = {}
    for path, expected in HISTORICAL_FAMILY_BLOBS.items():
        observed = git_blob(ROOT, path)
        if observed != expected:
            raise RuntimeError(f"procedural family profile drifted: {path}: {observed} != {expected}")
        family_blobs[path] = observed

    return {
        "migration_ref": observed_migration,
        "local_generator_sha256": local_generator_sha,
        "migration_generator_sha256": donor_generator_sha,
        "historical_mutator_blob": mutator_blob,
        "historical_family_blobs": family_blobs,
    }


def build_case(case: dict, migrated_root: Path) -> dict:
    source = load_source(migrated_root / case["source_path"])
    family = load_family(ROOT / case["family_path"])
    base = family["base_source"]

    if source["study_id"] != base["study_id"] or digest(source) != base["expected_digest"]:
        raise RuntimeError(f"{case['case_id']}: source identity drift under migrated donor")
    if family["schema"].endswith("/v0.2"):
        if base["repository"] != "mike-axiom-mir/axm-nature-design":
            raise RuntimeError(f"{case['case_id']}: unexpected source repository")
        if base["ref"] != case["source_origin_ref"] or base["path"] != case["source_path"]:
            raise RuntimeError(f"{case['case_id']}: source-origin provenance drift")

    variants = []
    migrated_mesh_digests = set()
    migrated_source_digests = set()
    for seed in family["evidence_seeds"]:
        seed = int(seed)
        if seed not in case["historical"]:
            raise RuntimeError(f"{case['case_id']}: seed {seed} lacks historical retained identity")
        historical_source_digest, historical_mesh_digest = case["historical"][seed]
        result = generate_accepted_variant(source, family, seed)
        receipt = result["receipt"]
        candidate = result["candidate"]
        if receipt["state"] != "PASS_BOUNDED_VARIANT" or candidate is None:
            raise RuntimeError(f"{case['case_id']}: seed {seed} did not regenerate as PASS")

        candidate_source_digest = digest(candidate)
        mesh = build_mesh(candidate)
        candidate_mesh_digest = digest(mesh)
        topology = inspect_shared_edge_orientation(mesh)

        source_identity_preserved = candidate_source_digest == historical_source_digest
        mesh_identity_migrated = candidate_mesh_digest != historical_mesh_digest
        topology_migrated = topology["shared_edge_orientation_conflicts"] == 0
        if not source_identity_preserved:
            raise RuntimeError(f"{case['case_id']}: seed {seed} source parameters drifted across migration")
        if not mesh_identity_migrated:
            raise RuntimeError(f"{case['case_id']}: seed {seed} still emits historical mesh identity")
        if not topology_migrated:
            raise RuntimeError(f"{case['case_id']}: seed {seed} retains shared-edge winding conflicts")
        if len(mesh["vertices"]) != 390 or len(mesh["triangles"]) != 570:
            raise RuntimeError(f"{case['case_id']}: seed {seed} changed expected bounded mesh counts")

        metrics = receipt["metrics"]
        if not all((metrics["organic_checks_pass"], metrics["envelope_ok"],
                    metrics["attachments_preserved"], metrics["immutable_fields_preserved"])):
            raise RuntimeError(f"{case['case_id']}: seed {seed} failed inherited procedural/source gates")

        migrated_source_digests.add(candidate_source_digest)
        migrated_mesh_digests.add(candidate_mesh_digest)
        variants.append({
            "seed": seed,
            "study_id": candidate["study_id"],
            "accepted_attempt": int(receipt["accepted_attempt"]),
            "historical_source_digest": historical_source_digest,
            "migrated_source_digest": candidate_source_digest,
            "source_identity_preserved": source_identity_preserved,
            "historical_mesh_digest": historical_mesh_digest,
            "migrated_mesh_digest": candidate_mesh_digest,
            "mesh_identity_migrated": mesh_identity_migrated,
            "vertices": len(mesh["vertices"]),
            "triangles": len(mesh["triangles"]),
            "shared_edge_orientation_conflicts": topology["shared_edge_orientation_conflicts"],
            "boundary_edges": topology["boundary_edges"],
            "nonmanifold_edges": topology["nonmanifold_edges"],
            "moved_branch_tips": metrics["moved_branch_tips"],
            "changed_leaf_blades": metrics["changed_leaf_blades"],
            "envelope_ok": metrics["envelope_ok"],
            "attachments_preserved": metrics["attachments_preserved"],
            "immutable_fields_preserved": metrics["immutable_fields_preserved"],
        })

    if len(migrated_source_digests) != len(variants) or len(migrated_mesh_digests) != len(variants):
        raise RuntimeError(f"{case['case_id']}: migrated outputs collapsed to duplicate identity")

    impossible = copy.deepcopy(family)
    impossible["family_id"] = f"{family['family_id']}-migrated-impossible-envelope-control"
    impossible["attempt_limit"] = 3
    impossible["acceptance"]["max_envelope_m"] = [
        float(value) * 0.5 for value in family["acceptance"]["max_envelope_m"]
    ]
    hold = generate_accepted_variant(source, impossible, int(family["evidence_seeds"][0]))["receipt"]
    if hold["state"] != "HOLD_NO_VALID_VARIANT" or len(hold["rejected_attempts"]) != 3:
        raise RuntimeError(f"{case['case_id']}: migrated failure-bound control did not HOLD after 3 attempts")

    return {
        "case_id": case["case_id"],
        "source_study_id": source["study_id"],
        "source_path": case["source_path"],
        "source_origin_ref": case["source_origin_ref"],
        "source_digest": digest(source),
        "family_path": case["family_path"],
        "family_schema": family["schema"],
        "family_id": family["family_id"],
        "variants": variants,
        "distinct_migrated_source_digests": len(migrated_source_digests),
        "distinct_migrated_mesh_digests": len(migrated_mesh_digests),
        "negative_control": {
            "state": hold["state"],
            "attempt_limit": hold["attempt_limit"],
            "rejected_attempts": len(hold["rejected_attempts"]),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--migrated-root", required=True, type=Path)
    args = parser.parse_args()

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    identity = validate_code_and_profile_identity(args.migrated_root)
    cases = [build_case(case, args.migrated_root) for case in CASES]
    variants = [variant for case in cases for variant in case["variants"]]

    migrated_source_digests = [row["migrated_source_digest"] for row in variants]
    migrated_mesh_digests = [row["migrated_mesh_digest"] for row in variants]
    if len(set(migrated_source_digests)) != 9 or len(set(migrated_mesh_digests)) != 9:
        raise RuntimeError("migrated cross-source outputs are not globally distinct")

    summary = {
        "schema": SCHEMA,
        "state": "PASS_BRANCH_CROWN_VARIANTS_REBOUND_TO_MIGRATED_SOURCE_LINEAGE",
        "procedural_head": git_head(ROOT),
        "migration": identity,
        "historical_procedural_head": HISTORICAL_PROCEDURAL_HEAD,
        "historical_artifact_id": HISTORICAL_ARTIFACT_ID,
        "historical_artifact_sha256": HISTORICAL_ARTIFACT_SHA256,
        "source_case_count": len(cases),
        "retained_output_count": len(variants),
        "globally_distinct_source_outputs": len(set(migrated_source_digests)),
        "globally_distinct_migrated_mesh_outputs": len(set(migrated_mesh_digests)),
        "all_variant_source_identities_preserved": all(row["source_identity_preserved"] for row in variants),
        "all_mesh_identities_migrated": all(row["mesh_identity_migrated"] for row in variants),
        "all_shared_edge_orientation_conflicts_zero": all(row["shared_edge_orientation_conflicts"] == 0 for row in variants),
        "all_failure_bounds_hold": all(case["negative_control"]["state"] == "HOLD_NO_VALID_VARIANT" for case in cases),
        "cases": cases,
        "placement": "NATURE_LOCAL_MUTATOR_REBOUND_TO_EXACT_NATURE_SOURCE_GENERATOR_MIGRATION__NO_UC_OR_PROFESSION_FABRIC_EXTRACTION",
        "truth_boundary": "This evidence proves only that the byte-identical prior Nature-local branch/crown mutator and byte-identical family profiles regenerate the same nine derived source identities from the exact migrated Nature source lineage, while producing new mesh identities with zero indexed shared-edge orientation conflicts and retaining bounded HOLD behavior. Historical artifacts remain valid for their old mesh identities. It does not prove universal vegetation generation, botanical correctness, visual acceptance, deformation/wind quality, global outward-normal correctness, runtime fitness, gameplay, CANON, production readiness, or Procedural Design mastery.",
    }
    write_json(out / "summary.json", summary)
    (out / "exact-head.txt").write_text(summary["procedural_head"] + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

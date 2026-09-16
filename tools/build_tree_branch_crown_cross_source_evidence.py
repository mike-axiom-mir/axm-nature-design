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

from axm_nature_design.organic_form import build_mesh, digest, load_source, write_svg
from axm_nature_design.procedural_family import generate_accepted_variant, load_family

SCHEMA = "axm.nature-branch-crown-cross-source-evidence/v0.1"


def write_json(path: Path, value: object) -> None:
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


def write_variant_svg(mesh: dict, path: Path, view: str, study_id: str) -> None:
    write_svg(mesh, path, view)
    text = path.read_text(encoding="utf-8")
    baseline_label = f"sapling-neutral-001 / {view}"
    if baseline_label not in text:
        raise RuntimeError("Organic Form SVG label contract changed; refusing to retain mislabelled evidence")
    path.write_text(text.replace(baseline_label, f"{study_id} / {view}", 1), encoding="utf-8")


def build_case(*, case_id: str, source_root: Path, source_path: str, source_ref: str,
               family_path: Path, out: Path, require_exact_checkout: bool) -> dict:
    if require_exact_checkout:
        observed_head = git_head(source_root)
        if observed_head != source_ref:
            raise RuntimeError(f"{case_id}: source checkout drift: {observed_head} != {source_ref}")
    else:
        observed_head = None

    local_evaluator = ROOT / "src" / "axm_nature_design" / "organic_form.py"
    source_evaluator = source_root / "src" / "axm_nature_design" / "organic_form.py"
    if require_exact_checkout and sha256_file(local_evaluator) != sha256_file(source_evaluator):
        raise RuntimeError(f"{case_id}: source Organic Form evaluator differs from receiving evaluator")

    source = load_source(source_root / source_path)
    family = load_family(family_path)
    base = family["base_source"]
    if source["study_id"] != base["study_id"] or digest(source) != base["expected_digest"]:
        raise RuntimeError(f"{case_id}: exact source identity does not match family profile")
    if family["schema"].endswith("/v0.2"):
        if base["repository"] != "mike-axiom-mir/axm-nature-design":
            raise RuntimeError(f"{case_id}: unexpected source repository")
        if base["ref"] != source_ref or base["path"] != source_path:
            raise RuntimeError(f"{case_id}: family source provenance does not match probe manifest")

    case_out = out / case_id
    case_out.mkdir(parents=True, exist_ok=True)
    source_digests: set[str] = set()
    mesh_digests: set[str] = set()
    variants = []
    for seed in family["evidence_seeds"]:
        result = generate_accepted_variant(source, family, int(seed))
        receipt = result["receipt"]
        candidate = result["candidate"]
        if receipt["state"] != "PASS_BOUNDED_VARIANT" or candidate is None:
            raise RuntimeError(f"{case_id}: evidence seed {seed} failed: {receipt['state']}")
        metrics = receipt["metrics"]
        if not all((metrics["organic_checks_pass"], metrics["envelope_ok"],
                    metrics["attachments_preserved"], metrics["immutable_fields_preserved"])):
            raise RuntimeError(f"{case_id}: evidence seed {seed} violated a source-bound gate")

        mesh = build_mesh(candidate)
        seed_out = case_out / f"seed-{int(seed)}"
        seed_out.mkdir(parents=True, exist_ok=True)
        write_json(seed_out / "source.json", candidate)
        write_json(seed_out / "receipt.json", receipt)
        write_json(seed_out / "mesh.json", mesh)
        for view in ("front", "side", "top"):
            write_variant_svg(mesh, seed_out / f"{view}.svg", view, candidate["study_id"])

        source_digests.add(receipt["candidate_source_digest"])
        mesh_digests.add(receipt["candidate_mesh_digest"])
        variants.append({
            "seed": int(seed),
            "accepted_attempt": int(receipt["accepted_attempt"]),
            "study_id": candidate["study_id"],
            "source_digest": receipt["candidate_source_digest"],
            "mesh_digest": receipt["candidate_mesh_digest"],
            "moved_branch_tips": metrics["moved_branch_tips"],
            "changed_leaf_blades": metrics["changed_leaf_blades"],
            "bounds_m": metrics["bounds_m"],
        })

    if len(source_digests) != len(variants) or len(mesh_digests) != len(variants):
        raise RuntimeError(f"{case_id}: retained outputs collapsed to duplicate identity")

    impossible = copy.deepcopy(family)
    impossible["family_id"] = f"{family['family_id']}-impossible-envelope-control"
    impossible["attempt_limit"] = 3
    impossible["acceptance"]["max_envelope_m"] = [
        float(value) * 0.5 for value in family["acceptance"]["max_envelope_m"]
    ]
    hold = generate_accepted_variant(source, impossible, int(family["evidence_seeds"][0]))["receipt"]
    if hold["state"] != "HOLD_NO_VALID_VARIANT" or len(hold["rejected_attempts"]) != 3:
        raise RuntimeError(f"{case_id}: impossible-envelope control did not exhaust and HOLD")

    row = {
        "case_id": case_id,
        "source_study_id": source["study_id"],
        "source_origin_ref": source_ref,
        "observed_checkout_head": observed_head,
        "source_path": source_path,
        "source_digest": digest(source),
        "family_schema": family["schema"],
        "family_id": family["family_id"],
        "family_path": str(family_path.relative_to(ROOT)),
        "variants": variants,
        "distinct_source_digests": len(source_digests),
        "distinct_mesh_digests": len(mesh_digests),
        "negative_control": {
            "state": hold["state"],
            "attempt_limit": hold["attempt_limit"],
            "rejected_attempts": len(hold["rejected_attempts"]),
        },
    }
    write_json(case_out / "case-summary.json", row)
    return row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--compact-root", required=True, type=Path)
    parser.add_argument("--rear-root", required=True, type=Path)
    args = parser.parse_args()

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    procedural_head = git_head(ROOT)

    cases = [
        build_case(
            case_id="sapling-west-a",
            source_root=ROOT,
            source_path="examples/sapling_neutral_001.json",
            source_ref="fbc202449981f2bac153951c561ed0ed6120c936",
            family_path=ROOT / "examples" / "sapling_variation_family_001.json",
            out=out,
            require_exact_checkout=False,
        ),
        build_case(
            case_id="compact-east-b",
            source_root=args.compact_root,
            source_path="examples/compact_east_tree_neutral_001.json",
            source_ref="64116d63fc76daa1623b5fd5046a4e6074100bda",
            family_path=ROOT / "examples" / "compact_tree_variation_family_001.json",
            out=out,
            require_exact_checkout=True,
        ),
        build_case(
            case_id="east-rear-a",
            source_root=args.rear_root,
            source_path="examples/east_rear_tree_neutral_001.json",
            source_ref="a4e5ee011e1d87f47866a7e6c6f4e66f57b6af12",
            family_path=ROOT / "examples" / "east_rear_tree_variation_family_001.json",
            out=out,
            require_exact_checkout=True,
        ),
    ]

    all_source_digests = [variant["source_digest"] for case in cases for variant in case["variants"]]
    all_mesh_digests = [variant["mesh_digest"] for case in cases for variant in case["variants"]]
    if len(set(all_source_digests)) != len(all_source_digests):
        raise RuntimeError("cross-source candidate source identities are not globally distinct")
    if len(set(all_mesh_digests)) != len(all_mesh_digests):
        raise RuntimeError("cross-source candidate mesh identities are not globally distinct")

    summary = {
        "schema": SCHEMA,
        "state": "PASS_BRANCH_CROWN_MUTATOR_THREE_SOURCE_PROBE",
        "procedural_head": procedural_head,
        "required_material_sources": 3,
        "observed_material_sources": len(cases),
        "retained_outputs": len(all_source_digests),
        "globally_distinct_source_outputs": len(set(all_source_digests)),
        "globally_distinct_mesh_outputs": len(set(all_mesh_digests)),
        "all_cases_retain_bounded_hold": all(case["negative_control"]["state"] == "HOLD_NO_VALID_VARIANT" for case in cases),
        "cases": cases,
        "placement": "NATURE_LOCAL_REUSABLE_MUTATOR__SOURCE_PROFILES_REMAIN_SOURCE_BOUND__NO_UC_EXTRACTION",
        "truth_boundary": "This probe proves one Nature-local branch/crown mutator can operate unchanged across three exact source-owned tree studies with source-specific bounds, multiple distinct retained outputs and bounded HOLD behavior. It does not prove species generation, biological growth, Art Direction or Environment acceptance, deformation, topology migration, runtime fitness, CANON, production readiness, a universal vegetation generator, or Procedural Design mastery.",
    }
    write_json(out / "summary.json", summary)
    (out / "exact-head.txt").write_text(procedural_head + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

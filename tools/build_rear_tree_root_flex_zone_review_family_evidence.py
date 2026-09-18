#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from axm_nature_design.flex_zone_candidate_family import (
    REVIEW_RELATION,
    assemble_family,
    derive_review_candidate,
    digest,
    validate_contract,
    validate_review_candidate,
)

CONTRACT_PATH = ROOT / "examples" / "rear_tree_root_flex_zone_review_family_001.json"
PASS_STATE = "PASS_BOUNDED_ROOT_FLEX_ZONE_REVIEW_FAMILY"
DECISION = "PASS_ROOT_CENTERED_FLEX_METADATA_REVIEW_ONLY__NO_SOURCE_DEFORMATION_OR_DOWNSTREAM_ADOPTION"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_head(root: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


def git_blob(root: Path, relpath: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", f"HEAD:{relpath}"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


def load_observer(organic_root: Path, relpath: str):
    path = organic_root / relpath
    spec = importlib.util.spec_from_file_location("axm_exact_organic_rear_tree_readiness", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load exact Organic deformation-readiness observer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_provider(organic_root: Path, contract: dict) -> dict:
    validate_contract(contract)
    provider = contract["organic_provider"]
    observed_head = git_head(organic_root)
    if observed_head != provider["ref"]:
        raise ValueError(f"Organic provider head drift: {observed_head} != {provider['ref']}")
    source_blob = git_blob(organic_root, provider["source_path"])
    observer_blob = git_blob(organic_root, provider["observer_path"])
    if source_blob != provider["source_blob"]:
        raise ValueError("Organic source blob drift")
    if observer_blob != provider["observer_blob"]:
        raise ValueError("Organic observer blob drift")
    source = load_json(organic_root / provider["source_path"])
    if digest(source) != provider["source_digest"]:
        raise ValueError("Organic source canonical digest drift")
    return source


def expect_rejection(label: str, action) -> dict:
    try:
        action()
    except Exception as exc:
        return {"label": label, "rejected": True, "error": f"{type(exc).__name__}: {exc}"}
    raise AssertionError(f"negative control unexpectedly passed: {label}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--organic-root", type=Path, required=True)
    args = parser.parse_args()

    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    organic_root = args.organic_root.resolve()
    contract = load_json(CONTRACT_PATH)
    source = validate_provider(organic_root, contract)
    observer = load_observer(organic_root, contract["organic_provider"]["observer_path"])

    baseline = observer.evaluate(source)
    if baseline["state"] != contract["expected_baseline_state"]:
        raise RuntimeError("exact Organic baseline state drift")
    if baseline["branch_roots_missing_exact_flex_zone"] != contract["expected_baseline_missing_branch_ids"]:
        raise RuntimeError("exact Organic missing-root identity drift")

    family = assemble_family(source, contract)
    reverse_contract = copy.deepcopy(contract)
    reverse_contract["allowed_review_radius_classes_m"] = list(reversed(reverse_contract["allowed_review_radius_classes_m"]))
    reverse_family = assemble_family(source, reverse_contract)
    if family["family_digest"] != reverse_family["family_digest"]:
        raise RuntimeError("family digest depends on allowed-radius declaration order")

    candidate_results = []
    for radius in sorted(float(value) for value in contract["allowed_review_radius_classes_m"]):
        candidate = derive_review_candidate(source, contract, radius)
        result = observer.evaluate(candidate["source_candidate"])
        if result["state"] != contract["expected_review_candidate_state"]:
            raise RuntimeError(f"review candidate {radius} did not close metadata-coverage HOLD")
        if result["branch_roots_with_exact_flex_zone"] != result["branch_count"]:
            raise RuntimeError("review candidate did not produce exact-root metadata coverage")
        row = {
            "radius_m": radius,
            "relation": candidate["relation"],
            "zone": candidate["zone"],
            "source_candidate_digest": candidate["source_candidate_digest"],
            "organic_observer_state": result["state"],
            "branch_roots_with_exact_flex_zone": result["branch_roots_with_exact_flex_zone"],
            "branch_count": result["branch_count"],
            "deformation_tested": False,
            "source_authorized": False,
        }
        candidate_results.append(row)
        write_json(out / f"review-candidate-radius-{radius:.2f}".replace(".", "p") / "candidate.json", {
            "schema": "axm.nature-root-flex-zone-review-candidate-evidence/v0.1",
            "relation": REVIEW_RELATION,
            "candidate": row,
            "source_candidate": candidate["source_candidate"],
            "truth_boundary": contract["truth_boundary"],
        })

    controls = []
    drift_head = copy.deepcopy(contract)
    drift_head["organic_provider"]["ref"] = "0" * 40
    controls.append(expect_rejection("organic-provider-head-drift", lambda: validate_provider(organic_root, drift_head)))

    drift_blob = copy.deepcopy(contract)
    drift_blob["organic_provider"]["source_blob"] = "0" * 40
    controls.append(expect_rejection("organic-source-blob-drift", lambda: validate_provider(organic_root, drift_blob)))

    controls.append(expect_rejection(
        "non-owner-radius-class",
        lambda: derive_review_candidate(source, contract, 0.13),
    ))

    adoption = copy.deepcopy(contract)
    adoption["automatic_source_adoption"] = True
    controls.append(expect_rejection("automatic-source-adoption", lambda: validate_contract(adoption)))

    candidate = derive_review_candidate(source, contract, float(contract["allowed_review_radius_classes_m"][0]))
    promoted = copy.deepcopy(candidate["source_candidate"])
    promoted["flex_zones"][-1]["status"] = "DEFORMATION_READY"
    controls.append(expect_rejection(
        "deformation-status-promotion",
        lambda: validate_review_candidate(source, promoted, contract, float(contract["allowed_review_radius_classes_m"][0])),
    ))

    off_root = copy.deepcopy(candidate["source_candidate"])
    off_root["flex_zones"][-1]["center"][0] += 0.001
    controls.append(expect_rejection(
        "off-root-center-drift",
        lambda: validate_review_candidate(source, off_root, contract, float(contract["allowed_review_radius_classes_m"][0])),
    ))

    already_covered = copy.deepcopy(contract)
    already_covered["target_branch_id"] = "west-high"
    controls.append(expect_rejection(
        "duplicate-covered-root-declaration",
        lambda: derive_review_candidate(source, already_covered, float(contract["allowed_review_radius_classes_m"][0])),
    ))

    if family["owner_example_count"] != int(contract["expected_owner_example_count"]):
        raise RuntimeError("owner-backed root-centered example count drift")
    if family["variant_count"] != 3 or family["distinct_variant_source_digest_count"] != 3:
        raise RuntimeError("three materially distinct source-state outputs were not preserved")

    summary = {
        "schema": "axm.nature-root-flex-zone-review-family-evidence/v0.1",
        "state": PASS_STATE,
        "decision": DECISION,
        "procedural_head": git_head(ROOT),
        "organic_provider_head": contract["organic_provider"]["ref"],
        "organic_source_blob": contract["organic_provider"]["source_blob"],
        "organic_observer_blob": contract["organic_provider"]["observer_blob"],
        "source_study": source["study_id"],
        "source_digest": digest(source),
        "baseline_state": baseline["state"],
        "baseline_branch_roots_with_exact_flex_zone": baseline["branch_roots_with_exact_flex_zone"],
        "baseline_branch_count": baseline["branch_count"],
        "baseline_missing_branch_ids": baseline["branch_roots_missing_exact_flex_zone"],
        "owner_example_count": family["owner_example_count"],
        "owner_examples": family["owner_examples"],
        "allowed_review_radius_classes_m": sorted(contract["allowed_review_radius_classes_m"]),
        "variant_count": family["variant_count"],
        "distinct_variant_source_digest_count": family["distinct_variant_source_digest_count"],
        "family_digest": family["family_digest"],
        "reverse_order_family_digest": reverse_family["family_digest"],
        "candidate_results": candidate_results,
        "failure_controls": controls,
        "all_failure_controls_rejected": all(row["rejected"] for row in controls),
        "truth_boundary": contract["truth_boundary"],
    }
    write_json(out / "summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
    derive_review_candidate,
    digest,
)
from axm_nature_design.flex_zone_owner_adoption_rebind import (
    HISTORICAL_RELATION,
    OWNER_ADOPTED_RELATION,
    assemble_rebound_family,
    resolve_review_base,
)

CANDIDATE_CONTRACT_PATH = ROOT / "examples" / "rear_tree_root_flex_zone_review_family_001.json"
REBIND_CONTRACT_PATH = ROOT / "examples" / "rear_tree_root_flex_zone_owner_adoption_rebind_002.json"
PASS_STATE = "PASS_NATURE_ROOT_FLEX_OWNER_ADOPTION_REBIND"
DECISION = "PASS_EXACT_OWNER_ADOPTED_REVIEW_VARIANT_REBIND__HISTORICAL_FAMILY_PRESERVED__NO_PROCEDURAL_SOURCE_AUTHORITY"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_head(root: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def git_blob(root: Path, relpath: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", f"HEAD:{relpath}"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def load_observer(root: Path, relpath: str, module_name: str):
    path = root / relpath
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load exact Organic deformation-readiness observer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_rebind_contract(contract: dict) -> None:
    if contract.get("schema") != "axm.nature-root-flex-zone-owner-adoption-rebind/v0.1":
        raise ValueError("unsupported owner-adoption rebind schema")
    if contract.get("automatic_source_adoption") is not False:
        raise ValueError("automatic source adoption remains forbidden")
    if contract.get("deformation_semantics_authorized") is not False:
        raise ValueError("deformation semantics remain outside Procedural authority")
    if contract.get("downstream_adoption_authorized") is not False:
        raise ValueError("downstream adoption remains outside Procedural authority")
    if float(contract.get("expected_owner_adopted_radius_m")) == float(contract.get("historical_alternative_radius_m")):
        raise ValueError("adopted and alternative radius classes must remain distinct")


def validate_provider(root: Path, provider: dict, label: str) -> dict:
    head = git_head(root)
    if head != provider["ref"]:
        raise ValueError(f"{label} owner head drift: {head} != {provider['ref']}")
    if git_blob(root, provider["source_path"]) != provider["source_blob"]:
        raise ValueError(f"{label} source blob drift")
    if git_blob(root, provider["observer_path"]) != provider["observer_blob"]:
        raise ValueError(f"{label} observer blob drift")
    source = load_json(root / provider["source_path"])
    if digest(source) != provider["source_digest"]:
        raise ValueError(f"{label} source canonical digest drift")
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
    parser.add_argument("--historical-organic-root", type=Path, required=True)
    parser.add_argument("--current-organic-root", type=Path, required=True)
    args = parser.parse_args()

    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    historical_root = args.historical_organic_root.resolve()
    current_root = args.current_organic_root.resolve()

    candidate_contract = load_json(CANDIDATE_CONTRACT_PATH)
    rebind_contract = load_json(REBIND_CONTRACT_PATH)
    validate_rebind_contract(rebind_contract)

    candidate_binding = rebind_contract["candidate_family_contract"]
    if git_blob(ROOT, candidate_binding["path"]) != candidate_binding["blob"]:
        raise ValueError("historical Procedural candidate contract blob drift")

    historical_source = validate_provider(historical_root, rebind_contract["historical_owner"], "historical")
    current_source = validate_provider(current_root, rebind_contract["current_owner"], "current")

    historical = assemble_rebound_family(historical_source, candidate_contract)
    current = assemble_rebound_family(current_source, candidate_contract)
    if historical["input_relation"] != HISTORICAL_RELATION:
        raise RuntimeError("historical owner no longer resolves as the review base")
    if current["input_relation"] != OWNER_ADOPTED_RELATION:
        raise RuntimeError("current owner does not resolve as one exact historical review variant")
    if historical["family_digest"] != candidate_binding["family_digest"]:
        raise RuntimeError("historical family digest drift")
    if current["family_digest"] != historical["family_digest"]:
        raise RuntimeError("owner adoption changed historical family identity")
    if current["review_base_source_digest"] != rebind_contract["historical_owner"]["source_digest"]:
        raise RuntimeError("current owner did not reconstruct the exact historical review base")

    adopted_radius = float(rebind_contract["expected_owner_adopted_radius_m"])
    alternative_radius = float(rebind_contract["historical_alternative_radius_m"])
    if float(current["adopted_radius_m"]) != adopted_radius:
        raise RuntimeError("current owner adopted a different historical review radius")

    adopted_candidate = derive_review_candidate(historical_source, candidate_contract, adopted_radius)
    alternative_candidate = derive_review_candidate(historical_source, candidate_contract, alternative_radius)
    if adopted_candidate["source_candidate"] != current_source:
        raise RuntimeError("current owner source is not byte-semantically equal to the historical adopted candidate")
    if alternative_candidate["source_candidate"] == current_source:
        raise RuntimeError("historical alternative collapsed onto current owner source")

    output_source_digests = {
        digest(historical_source),
        adopted_candidate["source_candidate_digest"],
        alternative_candidate["source_candidate_digest"],
    }
    if len(output_source_digests) != 3:
        raise RuntimeError("historical/adopted/alternative source states are not materially distinct")

    historical_observer = load_observer(
        historical_root,
        rebind_contract["historical_owner"]["observer_path"],
        "axm_historical_rear_tree_readiness",
    )
    current_observer = load_observer(
        current_root,
        rebind_contract["current_owner"]["observer_path"],
        "axm_current_rear_tree_readiness",
    )
    historical_readiness = historical_observer.evaluate(historical_source)
    current_readiness = current_observer.evaluate(current_source)
    alternative_readiness = historical_observer.evaluate(alternative_candidate["source_candidate"])

    if historical_readiness["state"] != "HOLD_BRANCH_ROOT_FLEX_ZONE_COVERAGE":
        raise RuntimeError("historical owner baseline state drift")
    if current_readiness["state"] != "PASS_NEUTRAL_BRANCH_ROOT_SUPPORT__DEFORMATION_UNTESTED":
        raise RuntimeError("current owner metadata readiness state drift")
    if alternative_readiness["state"] != "PASS_NEUTRAL_BRANCH_ROOT_SUPPORT__DEFORMATION_UNTESTED":
        raise RuntimeError("historical alternative no longer closes metadata coverage")

    controls = []
    drift_head = copy.deepcopy(rebind_contract)
    drift_head["current_owner"]["ref"] = "0" * 40
    controls.append(expect_rejection(
        "current-owner-head-drift",
        lambda: validate_provider(current_root, drift_head["current_owner"], "current"),
    ))

    drift_blob = copy.deepcopy(rebind_contract)
    drift_blob["current_owner"]["source_blob"] = "0" * 40
    controls.append(expect_rejection(
        "current-owner-source-blob-drift",
        lambda: validate_provider(current_root, drift_blob["current_owner"], "current"),
    ))

    automatic = copy.deepcopy(rebind_contract)
    automatic["automatic_source_adoption"] = True
    controls.append(expect_rejection("automatic-source-adoption", lambda: validate_rebind_contract(automatic)))

    downstream = copy.deepcopy(rebind_contract)
    downstream["downstream_adoption_authorized"] = True
    controls.append(expect_rejection("downstream-authority-expansion", lambda: validate_rebind_contract(downstream)))

    non_owner_radius = copy.deepcopy(current_source)
    target = [z for z in non_owner_radius["flex_zones"] if z.get("id") == "north-top-branch-flex"][0]
    target["radius"] = 0.13
    controls.append(expect_rejection(
        "non-owner-radius-013",
        lambda: resolve_review_base(non_owner_radius, candidate_contract),
    ))

    off_root = copy.deepcopy(current_source)
    target = [z for z in off_root["flex_zones"] if z.get("id") == "north-top-branch-flex"][0]
    target["center"][0] += 0.001
    controls.append(expect_rejection("off-root-owner-adoption", lambda: resolve_review_base(off_root, candidate_contract)))

    promoted = copy.deepcopy(current_source)
    target = [z for z in promoted["flex_zones"] if z.get("id") == "north-top-branch-flex"][0]
    target["status"] = "DEFORMATION_READY"
    controls.append(expect_rejection("deformation-status-promotion", lambda: resolve_review_base(promoted, candidate_contract)))

    duplicate = copy.deepcopy(current_source)
    extra = copy.deepcopy([z for z in duplicate["flex_zones"] if z.get("id") == "north-top-branch-flex"][0])
    extra["id"] = "north-top-branch-flex-duplicate"
    duplicate["flex_zones"].append(extra)
    controls.append(expect_rejection("duplicate-target-root-zone", lambda: resolve_review_base(duplicate, candidate_contract)))

    summary = {
        "schema": "axm.nature-root-flex-zone-owner-adoption-rebind-evidence/v0.1",
        "state": PASS_STATE,
        "decision": DECISION,
        "procedural_head": git_head(ROOT),
        "historical_owner_head": rebind_contract["historical_owner"]["ref"],
        "current_owner_head": rebind_contract["current_owner"]["ref"],
        "historical_source_blob": rebind_contract["historical_owner"]["source_blob"],
        "current_source_blob": rebind_contract["current_owner"]["source_blob"],
        "historical_source_digest": digest(historical_source),
        "current_source_digest": digest(current_source),
        "historical_family_digest": historical["family_digest"],
        "current_rebound_family_digest": current["family_digest"],
        "review_base_source_digest": current["review_base_source_digest"],
        "input_relation": current["input_relation"],
        "adopted_radius_m": current["adopted_radius_m"],
        "alternative_radius_m": alternative_radius,
        "historical_owner_example_count": historical["current_owner_example_count"],
        "current_owner_example_count": current["current_owner_example_count"],
        "variant_count": current["variant_count"],
        "distinct_variant_source_digest_count": current["distinct_variant_source_digest_count"],
        "three_materially_distinct_source_state_digests": sorted(output_source_digests),
        "historical_readiness_state": historical_readiness["state"],
        "historical_coverage": [
            historical_readiness["branch_roots_with_exact_flex_zone"],
            historical_readiness["branch_count"],
        ],
        "current_readiness_state": current_readiness["state"],
        "current_coverage": [
            current_readiness["branch_roots_with_exact_flex_zone"],
            current_readiness["branch_count"],
        ],
        "alternative_readiness_state": alternative_readiness["state"],
        "failure_controls": controls,
        "all_failure_controls_rejected": all(row["rejected"] for row in controls),
        "truth_boundary": rebind_contract["truth_boundary"],
    }
    write_json(out / "summary.json", summary)
    write_json(out / "current-owner-rebind.json", {
        "relation": current["input_relation"],
        "owner_source_digest": current["input_owner_source_digest"],
        "review_base_source_digest": current["review_base_source_digest"],
        "adopted_radius_m": current["adopted_radius_m"],
        "family_digest": current["family_digest"],
        "source_authorized_by_procedural": False,
        "deformation_tested_by_procedural": False,
    })
    write_json(out / "historical-alternative-014.json", {
        "relation": "HISTORICAL_REVIEW_VARIANT_NOT_CURRENT_OWNER_SOURCE",
        "radius_m": alternative_radius,
        "source_candidate_digest": alternative_candidate["source_candidate_digest"],
        "equals_current_owner_source": False,
        "source_authorized": False,
    })
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

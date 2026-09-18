"""Bounded review-only root-centered flex-zone declaration family for Nature.

This module automates only the repeated metadata construction already present in the
east-rear source: a branch flex-zone declaration is centered exactly on an authored
branch root and remains explicitly deformation-untested. It never chooses a new
production radius, edits the owner source in place, or grants deformation authority.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from typing import Iterable

SCHEMA = "axm.nature-root-flex-zone-review-candidate-family/v0.1"
FLEX_STATUS = "DECLARED_NOT_DEFORMATION_TESTED"
REVIEW_RELATION = "REVIEW_ONLY_CANDIDATE_NOT_SOURCE_AUTHORIZATION"
TOLERANCE = 1e-12


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def validate_contract(contract: dict) -> None:
    if contract.get("schema") != SCHEMA:
        raise ValueError("unsupported root-flex review family schema")
    provider = contract.get("organic_provider", {})
    required_provider = ("repository", "ref", "source_path", "source_blob", "source_digest", "observer_path", "observer_blob")
    missing = [key for key in required_provider if not provider.get(key)]
    if missing:
        raise ValueError(f"incomplete Organic provider provenance: {missing}")
    if not contract.get("target_branch_id"):
        raise ValueError("target_branch_id required")
    radii = contract.get("allowed_review_radius_classes_m")
    if not isinstance(radii, list) or len(radii) < 2:
        raise ValueError("at least two owner-backed review radius classes required")
    parsed = [float(value) for value in radii]
    if any(not math.isfinite(value) or value <= 0.0 for value in parsed):
        raise ValueError("review radius classes must be finite and positive")
    if len(set(parsed)) != len(parsed):
        raise ValueError("review radius classes must be distinct")
    if contract.get("required_status") != FLEX_STATUS:
        raise ValueError("flex status must remain explicitly deformation-untested")
    if contract.get("review_relation") != REVIEW_RELATION:
        raise ValueError("review relation drift")
    if contract.get("automatic_source_adoption") is not False:
        raise ValueError("automatic source adoption is forbidden")
    if contract.get("deformation_semantics_authorized") is not False:
        raise ValueError("Procedural may not grant deformation semantics")
    if contract.get("source_geometry_mutation_authorized") is not False:
        raise ValueError("Procedural may not mutate source geometry")


def _branch(source: dict, branch_id: str) -> dict:
    matches = [branch for branch in source.get("branches", []) if branch.get("id") == branch_id]
    if len(matches) != 1:
        raise ValueError(f"branch identity must resolve exactly once: {branch_id}")
    branch = matches[0]
    if not branch.get("points") or not branch.get("radii"):
        raise ValueError(f"branch missing authored root geometry: {branch_id}")
    return branch


def branch_root(source: dict, branch_id: str) -> list[float]:
    return [float(value) for value in _branch(source, branch_id)["points"][0]]


def _same_vec3(a, b) -> bool:
    return (
        isinstance(a, list)
        and isinstance(b, list)
        and len(a) == len(b) == 3
        and all(abs(float(a[i]) - float(b[i])) <= TOLERANCE for i in range(3))
    )


def exact_root_zones(source: dict, branch_id: str) -> list[dict]:
    root = branch_root(source, branch_id)
    return [zone for zone in source.get("flex_zones", []) if _same_vec3(zone.get("center"), root)]


def make_root_centered_declaration(
    source: dict,
    branch_id: str,
    radius_m: float,
    *,
    zone_id: str | None = None,
) -> dict:
    radius = float(radius_m)
    if not math.isfinite(radius) or radius <= 0.0:
        raise ValueError("flex-zone radius must be finite and positive")
    root = branch_root(source, branch_id)
    return {
        "id": zone_id or f"{branch_id}-branch-flex",
        "center": root,
        "radius": radius,
        "status": FLEX_STATUS,
    }


def owner_backed_root_examples(source: dict) -> list[dict]:
    """Reconstruct every exact root-centered branch flex zone from owner-authored values."""
    out = []
    for branch in source.get("branches", []):
        branch_id = branch.get("id")
        zones = exact_root_zones(source, branch_id)
        if len(zones) > 1:
            raise ValueError(f"multiple exact root flex zones for {branch_id}")
        if not zones:
            continue
        zone = zones[0]
        if zone.get("status") != FLEX_STATUS:
            raise ValueError(f"owner flex status promoted for {branch_id}")
        rebuilt = make_root_centered_declaration(
            source,
            branch_id,
            float(zone["radius"]),
            zone_id=str(zone["id"]),
        )
        if rebuilt != zone:
            raise ValueError(f"root-centered declaration does not exactly reproduce owner zone: {branch_id}")
        out.append(
            {
                "branch_id": branch_id,
                "zone_id": zone["id"],
                "root_point_m": rebuilt["center"],
                "radius_m": float(rebuilt["radius"]),
                "declaration_digest": digest(rebuilt),
            }
        )
    return out


def _radius_is_allowed(radius: float, allowed: Iterable[float]) -> bool:
    return any(abs(radius - float(value)) <= TOLERANCE for value in allowed)


def derive_review_candidate(source: dict, contract: dict, radius_m: float) -> dict:
    """Derive one review-only candidate without changing the owner source in place."""
    validate_contract(contract)
    branch_id = str(contract["target_branch_id"])
    if exact_root_zones(source, branch_id):
        raise ValueError("target branch already has an exact-root flex declaration")
    radius = float(radius_m)
    if not _radius_is_allowed(radius, contract["allowed_review_radius_classes_m"]):
        raise ValueError("radius is not one of the exact owner-authored review classes")

    candidate = copy.deepcopy(source)
    zone = make_root_centered_declaration(candidate, branch_id, radius)
    candidate.setdefault("flex_zones", []).append(zone)
    validate_review_candidate(source, candidate, contract, radius)
    return {
        "relation": REVIEW_RELATION,
        "target_branch_id": branch_id,
        "radius_m": radius,
        "zone": zone,
        "source_candidate": candidate,
        "source_candidate_digest": digest(candidate),
    }


def validate_review_candidate(base_source: dict, candidate: dict, contract: dict, radius_m: float) -> None:
    validate_contract(contract)
    branch_id = str(contract["target_branch_id"])
    radius = float(radius_m)
    if not _radius_is_allowed(radius, contract["allowed_review_radius_classes_m"]):
        raise ValueError("radius is not owner-backed")

    if set(candidate) != set(base_source):
        raise ValueError("review candidate may not add or remove source top-level fields")
    for key in base_source:
        if key != "flex_zones" and candidate[key] != base_source[key]:
            raise ValueError(f"review candidate changed source-owned field: {key}")

    if len(candidate.get("flex_zones", [])) != len(base_source.get("flex_zones", [])) + 1:
        raise ValueError("review candidate must add exactly one flex declaration")
    if candidate.get("flex_zones", [])[: len(base_source.get("flex_zones", []))] != base_source.get("flex_zones", []):
        raise ValueError("existing source flex-zone declarations changed or reordered")

    zones = exact_root_zones(candidate, branch_id)
    if len(zones) != 1:
        raise ValueError("review candidate must have exactly one target-root flex declaration")
    expected = make_root_centered_declaration(base_source, branch_id, radius)
    if zones[0] != expected:
        raise ValueError("review candidate declaration drifted from exact root/status/radius contract")


def assemble_family(base_source: dict, contract: dict) -> dict:
    validate_contract(contract)
    examples = owner_backed_root_examples(base_source)
    owner_classes = sorted(set(float(example["radius_m"]) for example in examples))
    contract_classes = sorted(float(value) for value in contract["allowed_review_radius_classes_m"])
    if owner_classes != contract_classes:
        raise ValueError("review radius classes are not exactly the owner-authored branch-flex radius classes")

    variants = [
        {
            "variant_id": "baseline-hold",
            "relation": "EXACT_OWNER_SOURCE_BASELINE",
            "source_digest": digest(base_source),
            "radius_m": None,
        }
    ]
    for radius in contract_classes:
        candidate = derive_review_candidate(base_source, contract, radius)
        variants.append(
            {
                "variant_id": f"north-top-owner-radius-class-{radius:.2f}".replace(".", "p"),
                "relation": candidate["relation"],
                "source_digest": candidate["source_candidate_digest"],
                "radius_m": radius,
                "zone_digest": digest(candidate["zone"]),
            }
        )

    if len({variant["source_digest"] for variant in variants}) != len(variants):
        raise ValueError("materially different source-state outputs collapsed")

    canonical = {
        "schema": SCHEMA,
        "family_id": contract["family_id"],
        "owner_examples": sorted(examples, key=lambda row: row["branch_id"]),
        "variants": sorted(variants, key=lambda row: row["variant_id"]),
    }
    return {
        **canonical,
        "owner_example_count": len(examples),
        "variant_count": len(variants),
        "distinct_variant_source_digest_count": len({row["source_digest"] for row in variants}),
        "family_digest": digest(canonical),
    }

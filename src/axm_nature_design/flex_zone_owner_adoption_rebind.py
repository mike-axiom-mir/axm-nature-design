"""Bounded continuity guard for a Procedural flex-zone review family after owner adoption.

The historical review family remains review-only. This module does not authorize a
source edit. It only proves whether a later owner-authored source is exactly one of
the previously generated review variants, and reconstructs the historical review
base so the original family can still be re-executed without duplicating a root zone.
"""
from __future__ import annotations

import copy

from .flex_zone_candidate_family import (
    FLEX_STATUS,
    assemble_family,
    derive_review_candidate,
    digest,
    exact_root_zones,
    owner_backed_root_examples,
    validate_contract,
)

SCHEMA = "axm.nature-root-flex-zone-owner-adoption-rebind/v0.1"
HISTORICAL_RELATION = "HISTORICAL_REVIEW_BASE__NO_OWNER_TARGET_DECLARATION"
OWNER_ADOPTED_RELATION = "OWNER_SOURCE_EXACTLY_MATCHES_ONE_HISTORICAL_REVIEW_VARIANT"
TOLERANCE = 1e-12


def _radius_is_allowed(radius: float, allowed: list[float]) -> bool:
    return any(abs(float(radius) - float(value)) <= TOLERANCE for value in allowed)


def resolve_review_base(owner_source: dict, candidate_contract: dict) -> dict:
    """Return the historical review base without silently rewriting owner authority.

    If the owner source still has no target-root declaration, it already is the review
    base. If it has one, that declaration must reproduce exactly one historical review
    candidate; only then is an in-memory predecessor reconstructed for re-execution.
    """
    validate_contract(candidate_contract)
    branch_id = str(candidate_contract["target_branch_id"])
    expected_zone_id = f"{branch_id}-branch-flex"
    exact = exact_root_zones(owner_source, branch_id)
    named = [zone for zone in owner_source.get("flex_zones", []) if zone.get("id") == expected_zone_id]

    if not exact:
        if named:
            raise ValueError("target-named flex declaration is not centered at the exact authored root")
        return {
            "relation": HISTORICAL_RELATION,
            "review_base_source": copy.deepcopy(owner_source),
            "review_base_source_digest": digest(owner_source),
            "owner_source_digest": digest(owner_source),
            "adopted_radius_m": None,
            "adopted_zone_digest": None,
        }

    if len(exact) != 1:
        raise ValueError("owner source must contain at most one exact target-root flex declaration")
    zone = exact[0]
    if zone.get("id") != expected_zone_id:
        raise ValueError("owner target-root flex declaration identity drift")
    if zone.get("status") != FLEX_STATUS:
        raise ValueError("owner target-root flex declaration promoted beyond deformation-untested")
    radius = float(zone.get("radius"))
    if not _radius_is_allowed(radius, candidate_contract["allowed_review_radius_classes_m"]):
        raise ValueError("owner target-root radius is not one of the historical owner-backed review classes")

    review_base = copy.deepcopy(owner_source)
    removed = False
    kept = []
    for item in review_base.get("flex_zones", []):
        if not removed and item == zone:
            removed = True
            continue
        kept.append(item)
    if not removed:
        raise ValueError("could not reconstruct historical review base")
    review_base["flex_zones"] = kept
    if exact_root_zones(review_base, branch_id):
        raise ValueError("reconstructed review base still contains a target-root declaration")

    reproduced = derive_review_candidate(review_base, candidate_contract, radius)
    if reproduced["source_candidate"] != owner_source:
        raise ValueError("owner source is not exactly one historical review candidate")

    return {
        "relation": OWNER_ADOPTED_RELATION,
        "review_base_source": review_base,
        "review_base_source_digest": digest(review_base),
        "owner_source_digest": digest(owner_source),
        "adopted_radius_m": radius,
        "adopted_zone_digest": digest(zone),
    }


def assemble_rebound_family(owner_source: dict, candidate_contract: dict) -> dict:
    """Re-execute the historical family while making current owner state explicit."""
    resolved = resolve_review_base(owner_source, candidate_contract)
    family = assemble_family(resolved["review_base_source"], candidate_contract)
    current_examples = owner_backed_root_examples(owner_source)
    return {
        **family,
        "rebind_schema": SCHEMA,
        "input_relation": resolved["relation"],
        "input_owner_source_digest": resolved["owner_source_digest"],
        "review_base_source_digest": resolved["review_base_source_digest"],
        "adopted_radius_m": resolved["adopted_radius_m"],
        "adopted_zone_digest": resolved["adopted_zone_digest"],
        "current_owner_example_count": len(current_examples),
    }

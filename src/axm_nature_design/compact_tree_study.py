"""Bounded source-form evidence for the compact east-foreground tree candidate.

This module stays Nature/Organic owned. It does not compose the map, scale the
source to fit, approve the form aesthetically, or claim deformation/runtime
acceptance. It only proves the authored source body fits its declared receiving
envelope without hidden source mutation.
"""
from __future__ import annotations

import copy

from .organic_form import build_evidence as build_organic_evidence

SCHEMA = "axm.nature-compact-tree-envelope-evidence/v0.1"
EXPECTED_TARGET = "proxy:nature-tree-east-b"
EXPECTED_POLICY = "PRESERVE_TARGET_CENTER_XY__GROUND_SOURCE_MIN_Z__NO_FORM_SCALE__NO_EXTRA_ROTATION"


def evaluate(source: dict) -> dict:
    organic = build_organic_evidence(source)
    handoff = source.get("environment_handoff", {})
    intent = source.get("form_intent", {})
    proxy_size = handoff.get("proxy_size_m")
    if not isinstance(proxy_size, list) or len(proxy_size) != 3:
        raise ValueError("environment_handoff.proxy_size_m must be a 3-value list")
    proxy_size = [float(value) for value in proxy_size]
    if any(value <= 0.0 for value in proxy_size):
        raise ValueError("proxy_size_m values must be positive")

    form_size = [float(value) for value in organic["design"]["bounds_m"]["size"]]
    margin = [proxy_size[i] - form_size[i] for i in range(3)]
    branch_root_heights = [float(branch["points"][0][2]) for branch in source.get("branches", [])]
    if not branch_root_heights:
        raise ValueError("compact tree candidate requires authored branches")
    lowest_branch_root = min(branch_root_heights)
    minimum_clear_trunk = float(intent.get("minimum_clear_trunk_before_primary_branch_m", 0.0))

    checks = {
        "organic_source_pass": organic.get("state") == "PASS_AUTHORED_ORGANIC_FORM_INTENT",
        "exact_receiving_target_declared": handoff.get("replacement_target") == EXPECTED_TARGET,
        "receiving_head_declared": isinstance(handoff.get("head"), str) and len(handoff["head"]) == 40,
        "no_receiver_scale_or_rotation_policy": handoff.get("placement_policy") == EXPECTED_POLICY,
        "form_intent_rejects_receiver_scaling": intent.get("fit_without_receiver_scale_or_rotation") is True,
        "source_bounds_fit_reserved_envelope": all(value >= -1e-9 for value in margin),
        "clear_lower_trunk_intent_met": lowest_branch_root + 1e-9 >= minimum_clear_trunk,
        "flex_zones_still_unproven": all(
            zone.get("status") == "DECLARED_NOT_DEFORMATION_TESTED"
            for zone in source.get("flex_zones", [])
        ),
        "environment_still_not_composed": handoff.get("status") == "CANDIDATE_REPLACEMENT_NOT_COMPOSED",
    }
    return {
        "schema": SCHEMA,
        "study_id": source.get("study_id"),
        "status": "PASS_COMPACT_SOURCE_ENVELOPE" if all(checks.values()) else "FAIL",
        "checks": checks,
        "source_digest": organic["source_digest"],
        "mesh_digest": organic["mesh_digest"],
        "vertices": organic["vertices"],
        "triangles": organic["triangles"],
        "source_bounds_m": copy.deepcopy(organic["design"]["bounds_m"]),
        "source_size_m": form_size,
        "reserved_proxy_size_m": proxy_size,
        "reserved_margin_m": margin,
        "lowest_primary_branch_root_z_m": lowest_branch_root,
        "minimum_clear_trunk_intent_m": minimum_clear_trunk,
        "receiving_context": {
            "repository": handoff.get("repository"),
            "pr": handoff.get("pr"),
            "head": handoff.get("head"),
            "replacement_target": handoff.get("replacement_target"),
            "placement_policy": handoff.get("placement_policy"),
        },
        "organic_evidence": organic,
        "truth_boundary": {
            "source_form_fit_checked": True,
            "hidden_receiving_scale_used": False,
            "map_composition_tested": False,
            "visual_hierarchy_accepted": False,
            "botanical_correctness_claimed": False,
            "deformation_tested": False,
            "runtime_tested": False,
        },
    }

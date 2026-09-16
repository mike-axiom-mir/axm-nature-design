"""Bounded source-form evidence for the retained seed-29 east/rear Nature slot.

Organic Form owns only the authored source body and its explicit receiving envelope.
This module does not compose the Map, apply target rotation, scale the source to fit,
approve the form aesthetically, or claim deformation/runtime acceptance.
"""
from __future__ import annotations

import copy

from .organic_form import build_evidence as build_organic_evidence

SCHEMA = "axm.nature-rear-tree-envelope-evidence/v0.1"
EXPECTED_TARGET = "proxy:nature-tree-east-a"
EXPECTED_MAP_HEAD = "cdac7d1316631b3b130d5e558de2aee462a21d40"
EXPECTED_SEED = 29
EXPECTED_POSITION_M = [6.089407, 2.004654, 2.098546]
EXPECTED_SIZE_M = [1.678837, 1.678837, 4.197092]
EXPECTED_ROTATION_DEG = -5.415604
EXPECTED_POLICY = "PRESERVE_TARGET_CENTER_XY__GROUND_SOURCE_MIN_Z__NO_FORM_SCALE__NO_EXTRA_ROTATION"


def _vector_matches(actual, expected, tolerance=1e-9):
    return (
        isinstance(actual, list)
        and len(actual) == len(expected)
        and all(abs(float(actual[i]) - float(expected[i])) <= tolerance for i in range(len(expected)))
    )


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
        raise ValueError("rear tree candidate requires authored branches")
    lowest_branch_root = min(branch_root_heights)
    minimum_clear_trunk = float(intent.get("minimum_clear_trunk_before_primary_branch_m", 0.0))

    checks = {
        "organic_source_pass": organic.get("state") == "PASS_AUTHORED_ORGANIC_FORM_INTENT",
        "exact_receiving_target_declared": handoff.get("replacement_target") == EXPECTED_TARGET,
        "exact_receiving_head_declared": handoff.get("head") == EXPECTED_MAP_HEAD,
        "exact_retained_seed_declared": handoff.get("seed") == EXPECTED_SEED,
        "exact_retained_position_declared": _vector_matches(handoff.get("proxy_position_m"), EXPECTED_POSITION_M),
        "exact_retained_size_declared": _vector_matches(handoff.get("proxy_size_m"), EXPECTED_SIZE_M),
        "exact_retained_rotation_declared": abs(float(handoff.get("proxy_rotation_deg", 999.0)) - EXPECTED_ROTATION_DEG) <= 1e-9,
        "no_receiver_scale_or_extra_rotation_policy": handoff.get("placement_policy") == EXPECTED_POLICY,
        "form_intent_rejects_receiver_scaling": intent.get("fit_without_receiver_scale_or_rotation") is True,
        "source_declares_distinct_form": intent.get("distinct_from_compact_east_tree") is True,
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
        "status": "PASS_REAR_SOURCE_ENVELOPE" if all(checks.values()) else "FAIL",
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
            "seed": handoff.get("seed"),
            "replacement_target": handoff.get("replacement_target"),
            "proxy_position_m": copy.deepcopy(handoff.get("proxy_position_m")),
            "proxy_size_m": copy.deepcopy(handoff.get("proxy_size_m")),
            "proxy_rotation_deg": handoff.get("proxy_rotation_deg"),
            "placement_policy": handoff.get("placement_policy"),
        },
        "organic_evidence": organic,
        "truth_boundary": {
            "source_form_fit_checked": True,
            "hidden_receiving_scale_used": False,
            "target_rotation_applied_to_source": False,
            "map_composition_tested": False,
            "visual_hierarchy_accepted": False,
            "botanical_correctness_claimed": False,
            "production_topology_claimed": False,
            "deformation_tested": False,
            "runtime_tested": False,
        },
    }

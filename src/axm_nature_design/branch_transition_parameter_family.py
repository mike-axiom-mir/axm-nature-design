"""Deterministic source-transition parameter windows for the east/rear Nature tree.

Organic Form owns the authored centerline/radius measurement. Procedural Design only
canonicalizes that exact owner report into reusable normalized parameter windows. The
family does not choose a junction topology, assign weights, simulate deformation, or
authorize downstream adoption.
"""
from __future__ import annotations

import hashlib
import json
import math

SCHEMA = "axm.nature-branch-transition-parameter-family/v0.1"
OWNER_REPORT_SCHEMA = "axm.nature-neutral-branch-transition-envelope/v0.1"
OWNER_PASS_STATE = "PASS_EXACT_NEUTRAL_BRANCH_TRANSITION_ENVELOPES__CONNECTED_TOPOLOGY_HELD"
RELATION = "DERIVED_OWNER_TRANSITION_PARAMETER_WINDOWS_ONLY_NOT_JUNCTION_RIGGING_WEIGHT_OR_DOWNSTREAM_AUTHORITY"
TOLERANCE = 1e-12


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _finite_positive(value: object, label: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number <= 0.0:
        raise ValueError(f"{label} must be finite and positive")
    return number


def validate_contract(contract: dict) -> None:
    if contract.get("schema") != SCHEMA:
        raise ValueError("unsupported branch transition parameter family schema")
    if contract.get("owner_report_schema") != OWNER_REPORT_SCHEMA:
        raise ValueError("owner transition report schema drift")
    if contract.get("relation") != RELATION:
        raise ValueError("branch transition parameter relation drift")

    branch_ids = contract.get("authorized_branch_ids")
    if not isinstance(branch_ids, list) or len(branch_ids) < 3:
        raise ValueError("at least three authorized branch identities required")
    if any(not isinstance(branch_id, str) or not branch_id for branch_id in branch_ids):
        raise ValueError("authorized branch identities must be non-empty strings")
    if len(set(branch_ids)) != len(branch_ids):
        raise ValueError("authorized branch identities must be unique")

    expected = contract.get("expected_transitions")
    if not isinstance(expected, dict) or set(expected) != set(branch_ids):
        raise ValueError("expected transition identities must exactly match authorized branches")
    for branch_id, row in expected.items():
        if not isinstance(row, dict):
            raise ValueError(f"expected transition for {branch_id} must be an object")
        fraction = float(row.get("embedded_fraction_of_first_segment"))
        length = _finite_positive(row.get("embedded_length_along_first_segment_m"), f"{branch_id} embedded length")
        if not math.isfinite(fraction) or not 0.0 < fraction < 1.0:
            raise ValueError(f"{branch_id} embedded fraction must be inside the first segment")
        if length <= 0.0:
            raise ValueError(f"{branch_id} embedded length must be positive")

    forbidden_true = (
        "source_mutation_authorized",
        "junction_strategy_authorized",
        "connected_topology_claim_authorized",
        "automatic_geometry_adoption",
        "automatic_rigging_adoption",
        "automatic_animation_adoption",
        "automatic_vfx_adoption",
        "automatic_runtime_adoption",
        "production_weight_authorized",
    )
    for key in forbidden_true:
        if contract.get(key) is not False:
            raise ValueError(f"authority expansion forbidden: {key}")


def _validate_owner_report(owner_report: dict, contract: dict) -> list[dict]:
    if owner_report.get("schema") != OWNER_REPORT_SCHEMA:
        raise ValueError("unexpected Organic transition-report schema")
    if owner_report.get("state") != OWNER_PASS_STATE:
        raise ValueError("Organic transition report is not in the exact bounded PASS state")

    rows = owner_report.get("branches")
    if not isinstance(rows, list):
        raise ValueError("Organic transition rows missing")
    if owner_report.get("branch_count") != len(contract["authorized_branch_ids"]) or len(rows) != len(contract["authorized_branch_ids"]):
        raise ValueError("Organic transition branch-count drift")
    observed_ids = [row.get("branch_id") for row in rows if isinstance(row, dict)]
    if len(observed_ids) != len(rows) or len(set(observed_ids)) != len(observed_ids):
        raise ValueError("Organic transition branch identities must be unique")
    if set(observed_ids) != set(contract["authorized_branch_ids"]):
        raise ValueError("Organic transition branch identity set drift")

    checks = owner_report.get("checks")
    if not isinstance(checks, dict):
        raise ValueError("Organic transition checks missing")
    required_true = (
        "all_branch_roots_have_full_radius_neutral_support",
        "all_primary_branches_have_exact_unproven_root_flex_declaration",
        "all_primary_branches_have_measured_first_segment_transition",
    )
    if any(checks.get(key) is not True for key in required_true):
        raise ValueError("Organic transition readiness check drift")

    handoff = owner_report.get("handoff")
    if not isinstance(handoff, dict):
        raise ValueError("Organic transition handoff missing")
    if handoff.get("organic_claim") != "AUTHORED_NEUTRAL_RADIAL_TRANSITION_GEOMETRY_ONLY":
        raise ValueError("Organic transition claim widened")
    if handoff.get("connected_topology_state") != "HELD_FOR_GEOMETRY":
        raise ValueError("connected topology is no longer held for Geometry")
    if handoff.get("junction_strategy_selected") is not False or handoff.get("source_compensation_authorized") is not False:
        raise ValueError("Organic handoff authority widened")

    truth = owner_report.get("truth_boundary")
    if not isinstance(truth, dict):
        raise ValueError("Organic transition truth boundary missing")
    required_false = (
        "source_geometry_changed",
        "flex_zone_metadata_changed",
        "generated_mesh_connectivity_inspected",
        "connected_branch_trunk_topology_proven",
        "weld_boolean_or_remesh_strategy_selected",
        "deformation_simulated",
        "rigging_hierarchy_or_weights_inferred",
        "biological_attachment_claimed",
        "runtime_readiness_claimed",
    )
    if any(truth.get(key) is not False for key in required_false):
        raise ValueError("Organic transition truth boundary widened")

    expected = contract["expected_transitions"]
    for row in rows:
        branch_id = row["branch_id"]
        if row.get("transition_state") != "FULL_BRANCH_RADIUS_EXITS_TRUNK_RADIAL_ENVELOPE_WITHIN_FIRST_SEGMENT":
            raise ValueError(f"{branch_id} transition state drift")
        boundary = row.get("first_full_radius_exit_boundary")
        if not isinstance(boundary, dict):
            raise ValueError(f"{branch_id} exact transition boundary missing")
        fraction = float(row.get("embedded_fraction_of_first_segment"))
        length = float(row.get("embedded_length_along_first_segment_m"))
        first_segment_length = _finite_positive(row.get("first_segment_length_m"), f"{branch_id} first segment")
        if not 0.0 < fraction < 1.0 or not 0.0 < length < first_segment_length:
            raise ValueError(f"{branch_id} transition window left first-segment bounds")
        expected_row = expected[branch_id]
        if abs(fraction - float(expected_row["embedded_fraction_of_first_segment"])) > TOLERANCE:
            raise ValueError(f"{branch_id} owner transition fraction drift")
        if abs(length - float(expected_row["embedded_length_along_first_segment_m"])) > TOLERANCE:
            raise ValueError(f"{branch_id} owner transition length drift")
    return rows


def assemble_transition_parameter_family(owner_report: dict, contract: dict) -> dict:
    validate_contract(contract)
    rows = _validate_owner_report(owner_report, contract)

    outputs = []
    for row in rows:
        branch_id = row["branch_id"]
        end_u = float(row["embedded_fraction_of_first_segment"])
        length_m = float(row["embedded_length_along_first_segment_m"])
        first_segment_length_m = float(row["first_segment_length_m"])
        core = {
            "output_id": f"{branch_id}-neutral-transition-window",
            "branch_id": branch_id,
            "parameter_space": "FIRST_SEGMENT_NORMALIZED_U_AND_METRES",
            "transition_u_min": 0.0,
            "transition_u_max": end_u,
            "transition_length_m": length_m,
            "first_segment_length_m": first_segment_length_m,
            "sample_u": [0.0, end_u * 0.5, end_u],
            "sample_distance_m": [0.0, length_m * 0.5, length_m],
            "root_radius_m": float(row["root_radius_m"]),
            "first_segment_end_radius_m": float(row["first_segment_end_radius_m"]),
            "owner_transition_state": row["transition_state"],
            "owner_root_flex_zone_id": row["exact_root_flex_zone_id"],
            "owner_root_flex_zone_status": row["exact_root_flex_zone_status"],
            "source_authorized": False,
            "junction_strategy_authorized": False,
            "connected_topology_claim_authorized": False,
            "rigging_authorized": False,
            "production_weight_authorized": False,
            "downstream_adoption_authorized": False,
        }
        outputs.append({**core, "parameter_digest": digest(core)})

    outputs.sort(key=lambda row: row["branch_id"])
    if len({row["parameter_digest"] for row in outputs}) < 3:
        raise ValueError("transition family does not contain at least three materially different outputs")
    if len({row["transition_length_m"] for row in outputs}) < 3:
        raise ValueError("transition family collapsed to fewer than three material lengths")
    if len({row["transition_u_max"] for row in outputs}) < 3:
        raise ValueError("transition family collapsed to fewer than three normalized windows")

    family_core = {
        "schema": SCHEMA,
        "family_id": contract["family_id"],
        "relation": RELATION,
        "owner_report_schema": owner_report["schema"],
        "owner_report_state": owner_report["state"],
        "output_count": len(outputs),
        "outputs": outputs,
        "source_authority": False,
        "geometry_junction_authority": False,
        "rigging_authority": False,
        "production_weight_authority": False,
        "animation_authority": False,
        "vfx_authority": False,
        "runtime_authority": False,
    }
    return {**family_core, "family_digest": digest(family_core)}

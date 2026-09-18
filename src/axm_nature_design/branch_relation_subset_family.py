"""Deterministic branch-child subsets derived from exact Organic relation evidence.

Procedural owns only repeatable selection/composition over the existing branch partition
family. Organic Form owns the source-space interaction classification. Rigging and every
downstream lane retain hierarchy, weight, motion, target-host and adoption authority.
"""
from __future__ import annotations

import hashlib
import json

from axm_nature_design.branch_subset_family import (
    PARTITION_SCHEMA,
    RELATION as SUBSET_RELATION,
    SCHEMA as SUBSET_SCHEMA,
    compose_subset,
)

SCHEMA = "axm.nature-branch-child-owner-relation-subset-family/v0.1"
OWNER_REPORT_SCHEMA = "axm.nature-trunk-branch-flex-interaction-classification/v0.2"
OWNER_PASS_STATE = "PASS_EXACT_TRUNK_BRANCH_FLEX_INTERACTION_CLASSES__DEFORMATION_UNTESTED"
FLEX_ENVELOPE_OVERLAP_ONLY = "FLEX_ENVELOPE_OVERLAP_ONLY"
RELATION = "DERIVED_OWNER_RELATION_SELECTION_ONLY_NOT_SOURCE_RIGGING_ANIMATION_VFX_OR_RUNTIME_AUTHORITY"

MODE_ATTACHMENT_INTERSECTING = "NEUTRAL_ATTACHMENT_INTERSECTING"
MODE_DECLARED_OVERLAP_ATTACHMENT_DISJOINT = "DECLARED_OVERLAP_ATTACHMENT_DISJOINT"
MODE_ATTACHMENT_DISJOINT = "NEUTRAL_ATTACHMENT_DISJOINT"
SUPPORTED_MODES = (
    MODE_ATTACHMENT_INTERSECTING,
    MODE_DECLARED_OVERLAP_ATTACHMENT_DISJOINT,
    MODE_ATTACHMENT_DISJOINT,
)


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def validate_contract(contract: dict) -> None:
    if contract.get("schema") != SCHEMA:
        raise ValueError("unsupported owner-relation subset schema")
    if contract.get("partition_family_schema") != PARTITION_SCHEMA:
        raise ValueError("partition-family schema drift")
    if contract.get("owner_report_schema") != OWNER_REPORT_SCHEMA:
        raise ValueError("Organic owner-report schema drift")
    if contract.get("relation") != RELATION:
        raise ValueError("owner-relation subset relation drift")
    expected_digest = contract.get("expected_partition_family_digest")
    if not isinstance(expected_digest, str) or len(expected_digest) != 64:
        raise ValueError("exact partition-family digest required")
    total_vertices = contract.get("total_vertices")
    if not isinstance(total_vertices, int) or total_vertices <= 0:
        raise ValueError("positive total vertex count required")

    branch_ids = contract.get("authorized_branch_ids")
    if not isinstance(branch_ids, list) or len(branch_ids) < 2:
        raise ValueError("at least two authorized branch identities required")
    if any(not isinstance(value, str) or not value for value in branch_ids):
        raise ValueError("authorized branch identities must be non-empty strings")
    if len(set(branch_ids)) != len(branch_ids):
        raise ValueError("authorized branch identities must be unique")

    specs = contract.get("output_specs")
    if not isinstance(specs, list) or len(specs) < 3:
        raise ValueError("at least three materially different relation outputs required")
    output_ids: set[str] = set()
    modes: set[str] = set()
    for spec in specs:
        if not isinstance(spec, dict):
            raise ValueError("relation output spec must be an object")
        output_id = spec.get("output_id")
        mode = spec.get("mode")
        expected = spec.get("expected_branch_ids")
        if not isinstance(output_id, str) or not output_id:
            raise ValueError("relation output identity required")
        if output_id in output_ids:
            raise ValueError("relation output identities must be unique")
        output_ids.add(output_id)
        if mode not in SUPPORTED_MODES:
            raise ValueError(f"unsupported relation selection mode: {mode}")
        if mode in modes:
            raise ValueError("relation selection modes must be unique")
        modes.add(mode)
        if not isinstance(expected, list) or not expected:
            raise ValueError(f"output {output_id} requires an exact expected branch set")
        if any(branch_id not in branch_ids for branch_id in expected):
            raise ValueError(f"output {output_id} expected branch set contains unknown identity")
        if len(set(expected)) != len(expected):
            raise ValueError(f"output {output_id} expected branch set contains duplicates")

    forbidden_true = (
        "source_mutation_authorized",
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
        raise ValueError("unexpected Organic owner-report schema")
    if owner_report.get("state") != OWNER_PASS_STATE:
        raise ValueError("Organic owner report is not in the exact bounded PASS state")
    rows = owner_report.get("pairs")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Organic owner report pairs missing")
    expected_pair_count = int(contract.get("expected_owner_pair_count", -1))
    if len(rows) != expected_pair_count or owner_report.get("pair_count") != expected_pair_count:
        raise ValueError("Organic owner pair-count drift")

    authorized = set(contract["authorized_branch_ids"])
    observed = {row.get("branch_id") for row in rows if isinstance(row, dict)}
    if observed != authorized:
        raise ValueError("Organic owner report branch identity set drift")
    per_branch = {branch_id: 0 for branch_id in authorized}
    for row in rows:
        branch_id = row.get("branch_id")
        if branch_id not in authorized:
            raise ValueError("Organic owner report contains unauthorized branch identity")
        per_branch[branch_id] += 1
        if not isinstance(row.get("trunk_flex_intersects_neutral_attachment_cross_section"), bool):
            raise ValueError("Organic owner report attachment-intersection truth missing")
        if not isinstance(row.get("interaction_class"), str) or not row["interaction_class"]:
            raise ValueError("Organic owner report interaction class missing")
    expected_pairs_per_branch = int(contract.get("expected_pairs_per_branch", -1))
    if any(count != expected_pairs_per_branch for count in per_branch.values()):
        raise ValueError("Organic owner report per-branch pair multiplicity drift")

    truth = owner_report.get("truth_boundary")
    if not isinstance(truth, dict):
        raise ValueError("Organic owner report truth boundary missing")
    required_false = (
        "interaction_class_assigns_rig_policy",
        "attachment_cross_section_intersection_assigns_rig_policy",
        "neutral_attachment_support_is_deformation_proof",
        "neutral_attachment_cross_section_intersection_is_deformation_proof",
        "deformation_simulated",
        "hierarchy_or_weighting_inferred",
        "runtime_readiness_claimed",
    )
    if any(truth.get(key) is not False for key in required_false):
        raise ValueError("Organic owner report truth boundary widened")
    return rows


def derive_branch_ids(owner_report: dict, contract: dict, mode: str) -> list[str]:
    validate_contract(contract)
    rows = _validate_owner_report(owner_report, contract)
    if mode not in SUPPORTED_MODES:
        raise ValueError(f"unsupported relation selection mode: {mode}")
    order = {branch_id: index for index, branch_id in enumerate(contract["authorized_branch_ids"])}

    by_branch: dict[str, list[dict]] = {branch_id: [] for branch_id in contract["authorized_branch_ids"]}
    for row in rows:
        by_branch[row["branch_id"]].append(row)

    selected: list[str] = []
    for branch_id, branch_rows in by_branch.items():
        intersects = any(row["trunk_flex_intersects_neutral_attachment_cross_section"] for row in branch_rows)
        overlap_only = any(row["interaction_class"] == FLEX_ENVELOPE_OVERLAP_ONLY for row in branch_rows)
        if mode == MODE_ATTACHMENT_INTERSECTING and intersects:
            selected.append(branch_id)
        elif mode == MODE_DECLARED_OVERLAP_ATTACHMENT_DISJOINT and overlap_only and not intersects:
            selected.append(branch_id)
        elif mode == MODE_ATTACHMENT_DISJOINT and not intersects:
            selected.append(branch_id)
    selected.sort(key=order.__getitem__)
    if not selected:
        raise ValueError(f"relation selection produced an empty branch set: {mode}")
    return selected


def _subset_contract(contract: dict, specs: list[dict]) -> dict:
    return {
        "schema": SUBSET_SCHEMA,
        "family_id": f"{contract['family_id']}-composition-bridge",
        "partition_family_schema": PARTITION_SCHEMA,
        "expected_partition_family_digest": contract["expected_partition_family_digest"],
        "authorized_branch_ids": list(contract["authorized_branch_ids"]),
        "total_vertices": int(contract["total_vertices"]),
        "subset_specs": specs,
        "relation": SUBSET_RELATION,
        "source_mutation_authorized": False,
        "automatic_rigging_adoption": False,
        "automatic_animation_adoption": False,
        "automatic_vfx_adoption": False,
        "automatic_runtime_adoption": False,
    }


def assemble_relation_family(partition_family: dict, owner_report: dict, contract: dict) -> dict:
    validate_contract(contract)
    rows = _validate_owner_report(owner_report, contract)
    del rows

    derived_specs: list[dict] = []
    for spec in contract["output_specs"]:
        branch_ids = derive_branch_ids(owner_report, contract, spec["mode"])
        if branch_ids != spec["expected_branch_ids"]:
            raise ValueError(
                f"Organic owner relation changed for {spec['output_id']}: "
                f"{branch_ids} != {spec['expected_branch_ids']}"
            )
        derived_specs.append({"subset_id": spec["output_id"], "branch_ids": branch_ids})

    subset_contract = _subset_contract(contract, derived_specs)
    outputs = []
    for spec, derived in zip(contract["output_specs"], derived_specs):
        row = compose_subset(partition_family, subset_contract, derived)
        row = {
            **row,
            "mode": spec["mode"],
            "owner_relation_only": True,
            "production_weight_authorized": False,
        }
        row["relation_output_digest"] = digest(row)
        outputs.append(row)
    outputs.sort(key=lambda row: row["subset_id"])

    if len({row["selection_digest"] for row in outputs}) != len(outputs):
        raise ValueError("materially different owner-relation outputs collapsed to duplicate selections")
    if len({row["vertex_index_digest"] for row in outputs}) != len(outputs):
        raise ValueError("materially different owner-relation outputs collapsed to duplicate vertex identities")

    family_core = {
        "schema": SCHEMA,
        "family_id": contract["family_id"],
        "relation": RELATION,
        "partition_family_digest": partition_family.get("family_digest"),
        "owner_report_schema": owner_report.get("schema"),
        "owner_report_state": owner_report.get("state"),
        "output_count": len(outputs),
        "outputs": outputs,
        "source_authority": False,
        "rigging_authority": False,
        "animation_authority": False,
        "vfx_authority": False,
        "runtime_authority": False,
    }
    return {**family_core, "family_digest": digest(family_core)}

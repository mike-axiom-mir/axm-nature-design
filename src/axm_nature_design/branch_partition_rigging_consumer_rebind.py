"""Exact current-Rigging consumer rebind for the Nature branch child-partition family.

Procedural owns deterministic generated-region selection only. This module proves that
an exact downstream Rigging consumer still consumes the same five selections after
Rigging evolves. It does not copy Rigging transforms, sign logic, deformation, or
motion semantics back into Procedural.
"""
from __future__ import annotations

from .branch_partition_family import SCHEMA as PARTITION_SCHEMA, digest

SCHEMA = "axm.nature-branch-child-partition-rigging-consumer-rebind/v0.1"
RELATION = "EXACT_RIGGING_CONSUMER_REBIND_SELECTION_IDENTITY_ONLY"


def validate_contract(contract: dict) -> None:
    if contract.get("schema") != SCHEMA:
        raise ValueError("unsupported Rigging consumer rebind schema")
    if contract.get("relation") != RELATION:
        raise ValueError("Rigging consumer rebind relation drift")
    required = ("family_id", "branch_ids", "procedural_provider", "rigging_consumer")
    missing = [key for key in required if not contract.get(key)]
    if missing:
        raise ValueError(f"incomplete Rigging consumer rebind contract: {missing}")
    branch_ids = contract["branch_ids"]
    if not isinstance(branch_ids, list) or len(branch_ids) < 2 or len(set(branch_ids)) != len(branch_ids):
        raise ValueError("branch identity set must contain distinct identities")
    provider = contract["procedural_provider"]
    for key in ("family_digest", "geometry_rebind_contract_path", "geometry_rebind_contract_blob"):
        if not provider.get(key):
            raise ValueError(f"Procedural provider provenance missing: {key}")
    consumer = contract["rigging_consumer"]
    for key in (
        "repository", "pr", "ref", "family_result", "family_module_path", "family_module_blob",
        "shared_driver_result", "shared_driver_module_path", "shared_driver_module_blob",
    ):
        if not consumer.get(key):
            raise ValueError(f"Rigging consumer provenance missing: {key}")
    if contract.get("automatic_rigging_adoption") is not False:
        raise ValueError("automatic Rigging adoption is forbidden")
    if contract.get("rigging_authority_transferred") is not False:
        raise ValueError("Rigging authority transfer is forbidden")
    if contract.get("deformation_semantics_authorized") is not False:
        raise ValueError("Procedural may not grant deformation semantics")
    if contract.get("animation_or_vfx_motion_adopted") is not False:
        raise ValueError("Animation/VFX motion adoption is forbidden")
    if contract.get("automatic_downstream_adoption") is not False:
        raise ValueError("automatic downstream adoption is forbidden")


def _by_branch(rows: list[dict], *, label: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for row in rows:
        branch_id = row.get("branch_id")
        if not isinstance(branch_id, str) or not branch_id:
            raise ValueError(f"{label} row missing branch identity")
        if branch_id in out:
            raise ValueError(f"duplicate {label} branch identity: {branch_id}")
        out[branch_id] = row
    return out


def assemble_rigging_consumer_rebind(
    procedural_family: dict,
    rigging_family_evidence: dict,
    shared_driver_evidence: dict,
    contract: dict,
    *,
    observed_rigging_head: str,
    observed_family_module_blob: str,
    observed_shared_driver_module_blob: str,
) -> dict:
    """Bind the existing Procedural family to one exact downstream Rigging consumer."""
    validate_contract(contract)
    consumer = contract["rigging_consumer"]
    provider = contract["procedural_provider"]
    expected_branches = list(contract["branch_ids"])

    if observed_rigging_head != consumer["ref"]:
        raise ValueError("exact current Rigging consumer head drift")
    if observed_family_module_blob != consumer["family_module_blob"]:
        raise ValueError("exact Rigging family module blob drift")
    if observed_shared_driver_module_blob != consumer["shared_driver_module_blob"]:
        raise ValueError("exact Rigging shared-driver module blob drift")

    if procedural_family.get("schema") != PARTITION_SCHEMA:
        raise ValueError("unexpected Procedural partition family schema")
    if procedural_family.get("family_digest") != provider["family_digest"]:
        raise ValueError("Procedural partition family digest drift")
    procedural_rows = _by_branch(procedural_family.get("partitions", []), label="Procedural")
    if set(procedural_rows) != set(expected_branches):
        raise ValueError("Procedural branch identity set drift")
    if not procedural_family.get("pairwise_vertex_disjoint"):
        raise ValueError("Procedural family is no longer pairwise vertex-disjoint")

    if rigging_family_evidence.get("result") != consumer["family_result"]:
        raise ValueError("current Rigging family result drift")
    rig_lineage = rigging_family_evidence.get("lineage", {})
    if rig_lineage.get("procedural_rebind_contract_blob") != provider["geometry_rebind_contract_blob"]:
        raise ValueError("Rigging no longer consumes the exact Procedural Geometry-rebind contract")
    rigging_rows = _by_branch(
        rigging_family_evidence.get("rigging_family", {}).get("probes", []),
        label="Rigging",
    )
    if set(rigging_rows) != set(expected_branches):
        raise ValueError("Rigging branch identity set drift")

    if shared_driver_evidence.get("result") != consumer["shared_driver_result"]:
        raise ValueError("current Rigging shared-driver result drift")
    binding = shared_driver_evidence.get("binding", {})
    if binding.get("branch_ids") != expected_branches:
        raise ValueError("shared-driver branch order or identity drift")
    shared_rows = _by_branch(binding.get("sockets", []), label="shared-driver")
    if set(shared_rows) != set(expected_branches):
        raise ValueError("shared-driver socket identity set drift")
    continuous = shared_driver_evidence.get("continuous_mapping", {})
    if continuous.get("rigging_child_partition_changed") is not False:
        raise ValueError("shared-driver successor reports a Rigging child-partition change")
    if continuous.get("source_or_geometry_changed") is not False:
        raise ValueError("shared-driver successor reports source or Geometry change")

    comparisons = []
    for branch_id in expected_branches:
        procedural = procedural_rows[branch_id]
        rigging = rigging_rows[branch_id]
        shared = shared_rows[branch_id]
        selection_match = (
            list(procedural["region_ids"]) == list(rigging["selected_regions"])
            and list(procedural["vertex_indices"]) == list(rigging["selected_vertex_indices"])
            and procedural["vertex_count"] == rigging["selected_vertices"] == shared["selected_vertices"]
            and procedural["triangle_count"] == rigging["selected_triangles"] == shared["selected_triangles"]
            and procedural["fixed_vertex_count"] == rigging["fixed_vertices"] == shared["fixed_vertices"]
        )
        if not selection_match:
            raise ValueError(f"current Rigging consumer selection drift: {branch_id}")
        comparisons.append(
            {
                "branch_id": branch_id,
                "selection_match": True,
                "partition_digest": procedural["partition_digest"],
                "vertex_index_digest": procedural["vertex_index_digest"],
                "vertex_count": procedural["vertex_count"],
                "triangle_count": procedural["triangle_count"],
                "fixed_vertex_count": procedural["fixed_vertex_count"],
                "command_sign_multiplier": shared["command_sign_multiplier"],
            }
        )

    if len({row["partition_digest"] for row in comparisons}) != len(comparisons):
        raise ValueError("materially different Procedural outputs lost distinct partition identity")
    if len({row["vertex_index_digest"] for row in comparisons}) != len(comparisons):
        raise ValueError("materially different Procedural outputs lost distinct vertex identity")

    core = {
        "schema": SCHEMA,
        "family_id": contract["family_id"],
        "relation": RELATION,
        "procedural_family_digest": procedural_family["family_digest"],
        "rigging_consumer_head": observed_rigging_head,
        "branch_count": len(comparisons),
        "comparisons": comparisons,
        "all_exact_selection_identities_match": True,
        "pairwise_vertex_disjoint": True,
        "rigging_shared_driver_observed_not_adopted": True,
        "source_authorized": False,
        "rigging_authority_transferred": False,
        "deformation_tested_by_procedural": False,
        "animation_or_vfx_motion_adopted": False,
        "automatic_downstream_adoption": False,
    }
    return {**core, "consumer_rebind_digest": digest(core)}

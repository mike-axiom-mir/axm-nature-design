"""Current Rigging-composition continuity guard for the Nature branch partition family.

Procedural owns only deterministic generated-region selection. This successor proves
that the existing materially different selections remain the exact child supports
consumed after Rigging advanced from the polarity adapter to one simultaneous shared
kinematic parameter. It deliberately does not copy pivots, axes, sign logic, timing,
deformation, collision, wind, Animation, Runtime, or target-host semantics into
Procedural.
"""
from __future__ import annotations

from .branch_partition_family import SCHEMA as PARTITION_SCHEMA, digest

SCHEMA = "axm.nature-branch-child-partition-rigging-composition-rebind/v0.1"
RELATION = "EXACT_CURRENT_RIGGING_COMPOSITION_REBIND_SELECTION_IDENTITY_ONLY"


def validate_contract(contract: dict) -> None:
    if contract.get("schema") != SCHEMA:
        raise ValueError("unsupported Rigging composition rebind schema")
    if contract.get("relation") != RELATION:
        raise ValueError("Rigging composition rebind relation drift")
    required = ("family_id", "branch_ids", "procedural_provider", "rigging_consumer")
    missing = [key for key in required if not contract.get(key)]
    if missing:
        raise ValueError(f"incomplete Rigging composition rebind contract: {missing}")

    branch_ids = contract["branch_ids"]
    if not isinstance(branch_ids, list) or len(branch_ids) < 2 or len(set(branch_ids)) != len(branch_ids):
        raise ValueError("branch identity set must contain distinct identities")

    provider = contract["procedural_provider"]
    for key in (
        "family_digest",
        "predecessor_consumer_rebind_head",
        "predecessor_consumer_rebind_digest",
        "geometry_rebind_contract_blob",
    ):
        if not provider.get(key):
            raise ValueError(f"Procedural provider provenance missing: {key}")

    consumer = contract["rigging_consumer"]
    for key in (
        "repository",
        "pr",
        "ref",
        "family_result",
        "family_module_path",
        "family_module_blob",
        "polarity_result",
        "polarity_module_path",
        "polarity_module_blob",
        "composition_result",
        "composition_module_path",
        "composition_module_blob",
        "composition_contract_path",
        "composition_contract_blob",
        "expected_selected_vertex_union",
        "expected_globally_fixed_vertices",
        "expected_per_branch_selected_vertices",
    ):
        if key not in consumer:
            raise ValueError(f"Rigging consumer provenance missing: {key}")
    per_branch = consumer["expected_per_branch_selected_vertices"]
    if not isinstance(per_branch, dict) or set(per_branch) != set(branch_ids):
        raise ValueError("expected per-branch support identity drift")
    if any(not isinstance(per_branch[branch_id], int) or per_branch[branch_id] <= 0 for branch_id in branch_ids):
        raise ValueError("expected per-branch support counts must be positive integers")

    forbidden = (
        "automatic_rigging_adoption",
        "rigging_authority_transferred",
        "deformation_semantics_authorized",
        "shared_driver_semantics_adopted",
        "animation_or_vfx_motion_adopted",
        "continuous_collision_claimed",
        "automatic_downstream_adoption",
    )
    for field in forbidden:
        if contract.get(field) is not False:
            raise ValueError(f"forbidden Procedural authority expansion: {field}")


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


def assemble_rigging_composition_rebind(
    procedural_family: dict,
    rigging_family_evidence: dict,
    polarity_evidence: dict,
    composition_evidence: dict,
    contract: dict,
    *,
    observed_rigging_head: str,
    observed_family_module_blob: str,
    observed_polarity_module_blob: str,
    observed_composition_module_blob: str,
    observed_composition_contract_blob: str,
) -> dict:
    """Rebind exact Procedural selections to the current Rigging composition owner."""
    validate_contract(contract)
    provider = contract["procedural_provider"]
    consumer = contract["rigging_consumer"]
    expected_branches = list(contract["branch_ids"])

    exact_observed = {
        "ref": observed_rigging_head,
        "family_module_blob": observed_family_module_blob,
        "polarity_module_blob": observed_polarity_module_blob,
        "composition_module_blob": observed_composition_module_blob,
        "composition_contract_blob": observed_composition_contract_blob,
    }
    exact_expected = {
        "ref": consumer["ref"],
        "family_module_blob": consumer["family_module_blob"],
        "polarity_module_blob": consumer["polarity_module_blob"],
        "composition_module_blob": consumer["composition_module_blob"],
        "composition_contract_blob": consumer["composition_contract_blob"],
    }
    if exact_observed != exact_expected:
        raise ValueError("exact current Rigging composition provenance drift")

    if procedural_family.get("schema") != PARTITION_SCHEMA:
        raise ValueError("unexpected Procedural partition family schema")
    if procedural_family.get("family_digest") != provider["family_digest"]:
        raise ValueError("Procedural partition family digest drift")
    if not procedural_family.get("pairwise_vertex_disjoint"):
        raise ValueError("Procedural family is no longer pairwise vertex-disjoint")
    procedural_rows = _by_branch(procedural_family.get("partitions", []), label="Procedural")
    if list(procedural_rows) != expected_branches:
        raise ValueError("Procedural canonical branch order or identity drift")

    if rigging_family_evidence.get("result") != consumer["family_result"]:
        raise ValueError("current Rigging family result drift")
    rig_lineage = rigging_family_evidence.get("lineage", {})
    if rig_lineage.get("procedural_rebind_contract_blob") != provider["geometry_rebind_contract_blob"]:
        raise ValueError("Rigging no longer consumes the exact Procedural Geometry-rebind contract")
    rigging_rows = _by_branch(
        rigging_family_evidence.get("rigging_family", {}).get("probes", []),
        label="Rigging",
    )
    if list(rigging_rows) != expected_branches:
        raise ValueError("Rigging canonical branch order or identity drift")

    if polarity_evidence.get("result") != consumer["polarity_result"]:
        raise ValueError("current Rigging polarity result drift")
    binding = polarity_evidence.get("binding", {})
    if binding.get("branch_ids") != expected_branches:
        raise ValueError("Rigging polarity branch order or identity drift")
    polarity_rows = _by_branch(binding.get("sockets", []), label="Rigging polarity")
    if list(polarity_rows) != expected_branches:
        raise ValueError("Rigging polarity socket identity drift")

    if composition_evidence.get("result") != consumer["composition_result"]:
        raise ValueError("current Rigging composition result drift")
    composition = composition_evidence.get("composition", {})
    if composition.get("branch_ids") != expected_branches:
        raise ValueError("Rigging composition branch order or identity drift")
    if composition.get("selected_vertex_union") != consumer["expected_selected_vertex_union"]:
        raise ValueError("Rigging composition selected-vertex union drift")
    if composition.get("globally_fixed_vertices") != consumer["expected_globally_fixed_vertices"]:
        raise ValueError("Rigging composition fixed-receiver identity drift")
    per_branch = composition.get("per_branch_selected_vertices", {})
    expected_per_branch = consumer["expected_per_branch_selected_vertices"]
    if set(per_branch) != set(expected_branches) or per_branch != expected_per_branch:
        raise ValueError("Rigging composition per-branch support drift")

    certificate = composition_evidence.get("continuous_parameter_certificate", {})
    if certificate.get("timing_or_playback_defined") is not False:
        raise ValueError("Rigging composition unexpectedly claims timing/playback")
    if certificate.get("continuous_collision_clearance_proven") is not False:
        raise ValueError("Rigging composition unexpectedly claims continuous collision clearance")

    comparisons = []
    for branch_id in expected_branches:
        procedural = procedural_rows[branch_id]
        rigging = rigging_rows[branch_id]
        polarity = polarity_rows[branch_id]
        selection_match = (
            list(procedural["region_ids"]) == list(rigging["selected_regions"])
            and list(procedural["vertex_indices"]) == list(rigging["selected_vertex_indices"])
            and procedural["vertex_count"] == rigging["selected_vertices"] == polarity["selected_vertices"] == per_branch[branch_id]
            and procedural["triangle_count"] == rigging["selected_triangles"] == polarity["selected_triangles"]
            and procedural["fixed_vertex_count"] == rigging["fixed_vertices"] == polarity["fixed_vertices"]
        )
        if not selection_match:
            raise ValueError(f"current Rigging composition consumer selection drift: {branch_id}")
        comparisons.append(
            {
                "branch_id": branch_id,
                "selection_match": True,
                "partition_digest": procedural["partition_digest"],
                "vertex_index_digest": procedural["vertex_index_digest"],
                "vertex_count": procedural["vertex_count"],
                "triangle_count": procedural["triangle_count"],
                "fixed_vertex_count": procedural["fixed_vertex_count"],
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
        "predecessor_consumer_rebind_head": provider["predecessor_consumer_rebind_head"],
        "predecessor_consumer_rebind_digest": provider["predecessor_consumer_rebind_digest"],
        "rigging_consumer_head": observed_rigging_head,
        "branch_count": len(comparisons),
        "comparisons": comparisons,
        "all_exact_selection_identities_match": True,
        "pairwise_vertex_disjoint": True,
        "rigging_composition_observed_not_adopted": True,
        "source_authorized": False,
        "rigging_authority_transferred": False,
        "deformation_tested_by_procedural": False,
        "shared_driver_semantics_adopted": False,
        "animation_or_vfx_motion_adopted": False,
        "continuous_collision_claimed": False,
        "automatic_downstream_adoption": False,
    }
    return {**core, "composition_rebind_digest": digest(core)}

"""Exact Geometry-receiver rebind for the Nature primary-branch child partition family.

This module does not own Organic source form, Geometry topology, or Rigging semantics.
It re-executes the existing Procedural selection family across a distinct receiver mesh
identity and proves whether the derived selection identities survive unchanged.
"""
from __future__ import annotations

from .branch_partition_family import assemble_family, digest, validate_contract

SCHEMA = "axm.nature-branch-child-partition-geometry-rebind/v0.1"
RELATION = "EXACT_GEOMETRY_RECEIVER_REBIND_SELECTION_ONLY"
TOLERANCE = 1e-12


def validate_rebind_contract(contract: dict, predecessor_contract: dict) -> None:
    if contract.get("schema") != SCHEMA:
        raise ValueError("unsupported branch partition Geometry rebind schema")
    if contract.get("relation") != RELATION:
        raise ValueError("Geometry receiver rebind relation drift")
    required = (
        "family_id",
        "predecessor_family_contract",
        "organic_provider",
        "geometry_receiver",
        "branch_ids",
        "rigging_receiver_witness",
    )
    missing = [key for key in required if not contract.get(key)]
    if missing:
        raise ValueError(f"incomplete Geometry rebind contract: {missing}")

    validate_contract(predecessor_contract)
    if contract["branch_ids"] != predecessor_contract["branch_ids"]:
        raise ValueError("authorized branch identity set drift")
    if contract.get("automatic_rigging_adoption") is not False:
        raise ValueError("automatic Rigging adoption is forbidden")
    if contract.get("source_mutation_authorized") is not False:
        raise ValueError("Procedural may not mutate Organic source")
    if contract.get("deformation_semantics_authorized") is not False:
        raise ValueError("Procedural may not grant deformation semantics")
    if contract.get("geometry_authority_transferred") is not False:
        raise ValueError("Geometry authority transfer is forbidden")
    if contract.get("automatic_downstream_adoption") is not False:
        raise ValueError("automatic downstream adoption is forbidden")

    predecessor = contract["predecessor_family_contract"]
    for key in ("path", "blob", "family_digest"):
        if not predecessor.get(key):
            raise ValueError(f"predecessor family provenance missing: {key}")
    for label in ("organic_provider", "geometry_receiver"):
        provider = contract[label]
        for key in ("repository", "ref", "source_path", "source_blob", "builder_path", "builder_blob", "mesh_digest"):
            if not provider.get(key):
                raise ValueError(f"{label} provenance missing: {key}")


def _triangle_membership(mesh: dict) -> list[tuple[int, int, int]]:
    rows: list[tuple[int, int, int]] = []
    for triangle in mesh.get("triangles", []):
        if not isinstance(triangle, list) or len(triangle) != 3:
            raise ValueError("receiver triangle must contain three indices")
        rows.append(tuple(sorted(int(index) for index in triangle)))
    return sorted(rows)


def _vertices_equal(a: list, b: list) -> bool:
    if len(a) != len(b):
        return False
    for va, vb in zip(a, b):
        if len(va) != len(vb):
            return False
        if any(abs(float(va[i]) - float(vb[i])) > TOLERANCE for i in range(len(va))):
            return False
    return True


def assemble_geometry_rebind(
    source: dict,
    historical_mesh: dict,
    migrated_mesh: dict,
    predecessor_contract: dict,
    rebind_contract: dict,
) -> dict:
    validate_rebind_contract(rebind_contract, predecessor_contract)

    historical_digest = digest(historical_mesh)
    migrated_digest = digest(migrated_mesh)
    organic = rebind_contract["organic_provider"]
    geometry = rebind_contract["geometry_receiver"]
    if historical_digest != organic["mesh_digest"]:
        raise ValueError("historical Organic receiver mesh digest drift")
    if migrated_digest != geometry["mesh_digest"]:
        raise ValueError("Geometry migrated receiver mesh digest drift")
    if historical_digest == migrated_digest:
        raise ValueError("Geometry rebind requires a distinct receiver mesh identity")

    if not _vertices_equal(historical_mesh.get("vertices", []), migrated_mesh.get("vertices", [])):
        raise ValueError("Geometry receiver changed generated vertex positions")
    if _triangle_membership(historical_mesh) != _triangle_membership(migrated_mesh):
        raise ValueError("Geometry receiver changed triangle membership")
    if historical_mesh.get("regions") != migrated_mesh.get("regions"):
        raise ValueError("Geometry receiver changed generated region identity or ranges")

    historical_family = assemble_family(source, historical_mesh, predecessor_contract)
    migrated_family = assemble_family(source, migrated_mesh, predecessor_contract)

    historical_rows = {row["branch_id"]: row for row in historical_family["partitions"]}
    migrated_rows = {row["branch_id"]: row for row in migrated_family["partitions"]}
    branch_ids = sorted(rebind_contract["branch_ids"])
    if sorted(historical_rows) != branch_ids or sorted(migrated_rows) != branch_ids:
        raise ValueError("receiver family branch identity drift")

    comparisons = []
    for branch_id in branch_ids:
        before = historical_rows[branch_id]
        after = migrated_rows[branch_id]
        selection_preserved = (
            before["region_ids"] == after["region_ids"]
            and before["vertex_indices"] == after["vertex_indices"]
            and before["triangle_indices"] == after["triangle_indices"]
            and before["partition_digest"] == after["partition_digest"]
            and before["vertex_index_digest"] == after["vertex_index_digest"]
        )
        if not selection_preserved:
            raise ValueError(f"derived partition selection changed across Geometry receiver: {branch_id}")
        comparisons.append(
            {
                "branch_id": branch_id,
                "selection_preserved": True,
                "partition_digest": after["partition_digest"],
                "vertex_index_digest": after["vertex_index_digest"],
                "vertex_count": after["vertex_count"],
                "triangle_count": after["triangle_count"],
                "fixed_vertex_count": after["fixed_vertex_count"],
            }
        )

    expected_family_digest = rebind_contract["predecessor_family_contract"]["family_digest"]
    if historical_family["family_digest"] != expected_family_digest:
        raise ValueError("predecessor partition family digest drift")
    if historical_family["family_digest"] != migrated_family["family_digest"]:
        raise ValueError("canonical partition family identity changed across Geometry receiver")

    ordered_triangle_changes = sum(
        1
        for before, after in zip(historical_mesh["triangles"], migrated_mesh["triangles"])
        if before != after
    )
    if ordered_triangle_changes <= 0:
        raise ValueError("receiver identity changed without an observed ordered-triangle change")

    result_core = {
        "schema": SCHEMA,
        "family_id": rebind_contract["family_id"],
        "relation": RELATION,
        "historical_receiver_mesh_digest": historical_digest,
        "geometry_receiver_mesh_digest": migrated_digest,
        "receiver_mesh_identity_changed": True,
        "vertex_positions_preserved": True,
        "triangle_membership_preserved": True,
        "generated_regions_preserved": True,
        "ordered_triangle_changes": ordered_triangle_changes,
        "branch_count": len(comparisons),
        "comparisons": comparisons,
        "historical_family_digest": historical_family["family_digest"],
        "geometry_receiver_family_digest": migrated_family["family_digest"],
        "selection_family_identity_preserved": True,
        "source_authorized": False,
        "geometry_authority_transferred": False,
        "rigging_authorized": False,
        "deformation_tested": False,
        "automatic_downstream_adoption": False,
    }
    return {**result_core, "rebind_digest": digest(result_core)}

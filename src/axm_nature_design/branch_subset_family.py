"""Deterministic subset composition over the existing east-rear branch partitions.

Procedural owns only repeatable composition of already-derived child selections. Organic
keeps source authority; Geometry keeps topology authority; Rigging/Animation/VFX/Runtime
keep their downstream semantics and adoption authority.
"""
from __future__ import annotations

import hashlib
import json
from typing import Iterable

SCHEMA = "axm.nature-branch-child-subset-family/v0.1"
PARTITION_SCHEMA = "axm.nature-branch-child-partition-family/v0.1"
RELATION = "DERIVED_PARTITION_UNION_ONLY_NOT_SOURCE_RIGGING_ANIMATION_VFX_OR_RUNTIME_AUTHORITY"


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def validate_contract(contract: dict) -> None:
    if contract.get("schema") != SCHEMA:
        raise ValueError("unsupported branch child-subset schema")
    if contract.get("partition_family_schema") != PARTITION_SCHEMA:
        raise ValueError("partition-family schema drift")
    if contract.get("relation") != RELATION:
        raise ValueError("subset relation drift")
    if not isinstance(contract.get("family_id"), str) or not contract["family_id"]:
        raise ValueError("subset family identity required")
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

    specs = contract.get("subset_specs")
    if not isinstance(specs, list) or len(specs) < 3:
        raise ValueError("at least three retained subset outputs required")
    subset_ids: set[str] = set()
    selections: set[tuple[str, ...]] = set()
    order = {branch_id: index for index, branch_id in enumerate(branch_ids)}
    for spec in specs:
        subset_id = spec.get("subset_id") if isinstance(spec, dict) else None
        selected = spec.get("branch_ids") if isinstance(spec, dict) else None
        if not isinstance(subset_id, str) or not subset_id:
            raise ValueError("subset identity required")
        if subset_id in subset_ids:
            raise ValueError("subset identities must be unique")
        subset_ids.add(subset_id)
        if not isinstance(selected, list) or not selected:
            raise ValueError(f"subset {subset_id} must select at least one branch")
        if any(branch_id not in order for branch_id in selected):
            raise ValueError(f"subset {subset_id} uses unknown branch selector")
        if len(set(selected)) != len(selected):
            raise ValueError(f"subset {subset_id} repeats a branch selector")
        canonical = tuple(sorted(selected, key=order.__getitem__))
        if canonical in selections:
            raise ValueError("duplicate material branch selection under different subset identity")
        selections.add(canonical)

    forbidden_true = (
        "source_mutation_authorized",
        "automatic_rigging_adoption",
        "automatic_animation_adoption",
        "automatic_vfx_adoption",
        "automatic_runtime_adoption",
    )
    for key in forbidden_true:
        if contract.get(key) is not False:
            raise ValueError(f"authority expansion forbidden: {key}")


def _partition_map(partition_family: dict, contract: dict) -> dict[str, dict]:
    if partition_family.get("schema") != PARTITION_SCHEMA:
        raise ValueError("unexpected partition-family schema")
    if partition_family.get("family_digest") != contract["expected_partition_family_digest"]:
        raise ValueError("partition-family digest drift")
    rows = partition_family.get("partitions")
    if not isinstance(rows, list):
        raise ValueError("partition family rows missing")
    mapping: dict[str, dict] = {}
    for row in rows:
        branch_id = row.get("branch_id") if isinstance(row, dict) else None
        if not isinstance(branch_id, str) or not branch_id:
            raise ValueError("partition branch identity missing")
        if branch_id in mapping:
            raise ValueError("duplicate partition branch identity")
        mapping[branch_id] = row
    if set(mapping) != set(contract["authorized_branch_ids"]):
        raise ValueError("partition family branch identity set drift")
    if partition_family.get("pairwise_vertex_disjoint") is not True:
        raise ValueError("partition family no longer proves pairwise vertex disjointness")
    return mapping


def compose_subset(partition_family: dict, contract: dict, spec: dict) -> dict:
    validate_contract(contract)
    mapping = _partition_map(partition_family, contract)
    order = {branch_id: index for index, branch_id in enumerate(contract["authorized_branch_ids"])}

    subset_id = spec.get("subset_id") if isinstance(spec, dict) else None
    requested = spec.get("branch_ids") if isinstance(spec, dict) else None
    if not isinstance(subset_id, str) or not subset_id:
        raise ValueError("subset identity required")
    if not isinstance(requested, list) or not requested:
        raise ValueError("subset must select at least one branch")
    if any(branch_id not in mapping for branch_id in requested):
        raise ValueError("unknown branch selector in subset")
    if len(set(requested)) != len(requested):
        raise ValueError("duplicate branch selector in subset")
    branch_ids = sorted(requested, key=order.__getitem__)

    selected_rows = [mapping[branch_id] for branch_id in branch_ids]
    vertex_sets = [set(int(value) for value in row.get("vertex_indices", [])) for row in selected_rows]
    triangle_sets = [set(int(value) for value in row.get("triangle_indices", [])) for row in selected_rows]
    for index in range(len(selected_rows)):
        row = selected_rows[index]
        if len(vertex_sets[index]) != int(row.get("vertex_count", -1)):
            raise ValueError(f"partition vertex identity/count drift: {row.get('branch_id')}")
        if len(triangle_sets[index]) != int(row.get("triangle_count", -1)):
            raise ValueError(f"partition triangle identity/count drift: {row.get('branch_id')}")
    if any(vertex_sets[i] & vertex_sets[j] for i in range(len(vertex_sets)) for j in range(i + 1, len(vertex_sets))):
        raise ValueError("selected branch partitions overlap in vertex identity")
    if any(triangle_sets[i] & triangle_sets[j] for i in range(len(triangle_sets)) for j in range(i + 1, len(triangle_sets))):
        raise ValueError("selected branch partitions overlap in triangle identity")

    vertex_indices = sorted(set().union(*vertex_sets)) if vertex_sets else []
    triangle_indices = sorted(set().union(*triangle_sets)) if triangle_sets else []
    region_ids: list[str] = []
    for row in selected_rows:
        region_ids.extend(str(value) for value in row.get("region_ids", []))
    if len(set(region_ids)) != len(region_ids):
        raise ValueError("selected branch partitions overlap in generated region identity")

    total_vertices = int(contract["total_vertices"])
    if any(index < 0 or index >= total_vertices for index in vertex_indices):
        raise ValueError("subset vertex index out of range")
    fixed_vertex_count = total_vertices - len(vertex_indices)
    if fixed_vertex_count < 0:
        raise ValueError("subset selected more vertices than the bound receiver")

    selection_core = {
        "branch_ids": branch_ids,
        "region_ids": sorted(region_ids),
        "vertex_indices": vertex_indices,
        "triangle_indices": triangle_indices,
        "vertex_count": len(vertex_indices),
        "triangle_count": len(triangle_indices),
        "fixed_vertex_count": fixed_vertex_count,
    }
    row = {
        "subset_id": subset_id,
        "relation": RELATION,
        **selection_core,
        "source_authorized": False,
        "rigging_authorized": False,
        "animation_authorized": False,
        "vfx_authorized": False,
        "runtime_authorized": False,
        "selection_digest": digest(selection_core),
        "vertex_index_digest": digest(vertex_indices),
        "triangle_index_digest": digest(triangle_indices),
    }
    row["subset_digest"] = digest({key: value for key, value in row.items() if key != "subset_digest"})
    return row


def assemble_subset_family(
    partition_family: dict,
    contract: dict,
    specs: Iterable[dict] | None = None,
) -> dict:
    validate_contract(contract)
    requested = [dict(spec) for spec in (contract["subset_specs"] if specs is None else specs)]
    if len(requested) != len(contract["subset_specs"]):
        raise ValueError("subset family must retain the exact declared output count")
    declared_ids = {spec["subset_id"] for spec in contract["subset_specs"]}
    if {spec.get("subset_id") for spec in requested} != declared_ids:
        raise ValueError("subset family must retain the exact declared subset identity set")

    outputs = [compose_subset(partition_family, contract, spec) for spec in requested]
    outputs.sort(key=lambda row: row["subset_id"])
    if len({row["selection_digest"] for row in outputs}) != len(outputs):
        raise ValueError("materially distinct subset outputs collapsed to duplicate selections")
    if len({row["vertex_index_digest"] for row in outputs}) != len(outputs):
        raise ValueError("materially distinct subset outputs collapsed to duplicate vertex identities")

    family_core = {
        "schema": SCHEMA,
        "family_id": contract["family_id"],
        "relation": RELATION,
        "partition_family_digest": partition_family["family_digest"],
        "output_count": len(outputs),
        "outputs": outputs,
    }
    return {**family_core, "family_digest": digest(family_core)}

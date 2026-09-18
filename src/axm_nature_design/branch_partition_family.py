"""Deterministic branch child-region partition family for the east-rear Nature source.

Procedural owns only repeatable selection of already-authored generated regions. Organic
Form keeps source authority and Rigging keeps articulation/deformation authority.
"""
from __future__ import annotations

import hashlib
import json
from typing import Iterable

SCHEMA = "axm.nature-branch-child-partition-family/v0.1"
RELATION = "DERIVED_REGION_PARTITION_REVIEW_ONLY_NOT_RIGGING_AUTHORITY"
FLEX_STATUS = "DECLARED_NOT_DEFORMATION_TESTED"
TOLERANCE = 1e-12


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def validate_contract(contract: dict) -> None:
    if contract.get("schema") != SCHEMA:
        raise ValueError("unsupported branch child-partition schema")
    provider = contract.get("organic_provider", {})
    required = (
        "repository", "ref", "source_path", "source_blob", "source_digest",
        "builder_path", "builder_blob", "generated_mesh_digest",
    )
    missing = [key for key in required if not provider.get(key)]
    if missing:
        raise ValueError(f"incomplete Organic provider provenance: {missing}")
    branch_ids = contract.get("branch_ids")
    if not isinstance(branch_ids, list) or len(branch_ids) < 2:
        raise ValueError("at least two branch identities required")
    if any(not isinstance(value, str) or not value for value in branch_ids):
        raise ValueError("branch identities must be non-empty strings")
    if len(set(branch_ids)) != len(branch_ids):
        raise ValueError("branch identities must be unique")
    if contract.get("relation") != RELATION:
        raise ValueError("partition relation drift")
    if contract.get("automatic_rigging_adoption") is not False:
        raise ValueError("automatic Rigging adoption is forbidden")
    if contract.get("source_mutation_authorized") is not False:
        raise ValueError("Procedural may not mutate Organic source")
    if contract.get("deformation_semantics_authorized") is not False:
        raise ValueError("Procedural may not grant deformation semantics")


def _single(items: Iterable[dict], *, label: str) -> dict:
    values = list(items)
    if len(values) != 1:
        raise ValueError(f"{label} must resolve exactly once")
    return values[0]


def _branch(source: dict, branch_id: str) -> dict:
    return _single((row for row in source.get("branches", []) if row.get("id") == branch_id), label=f"branch {branch_id}")


def _leaf_cluster(source: dict, branch_id: str) -> dict:
    expected = f"{branch_id}-leaves"
    return _single((row for row in source.get("leaf_clusters", []) if row.get("id") == expected), label=f"leaf cluster {expected}")


def _flex_zone(source: dict, branch_id: str) -> dict:
    expected = f"{branch_id}-branch-flex"
    return _single((row for row in source.get("flex_zones", []) if row.get("id") == expected), label=f"flex zone {expected}")


def _same_vec3(a: object, b: object) -> bool:
    return (
        isinstance(a, list) and isinstance(b, list) and len(a) == len(b) == 3
        and all(abs(float(a[i]) - float(b[i])) <= TOLERANCE for i in range(3))
    )


def _region_map(mesh: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for region in mesh.get("regions", []):
        region_id = region.get("id")
        if not isinstance(region_id, str) or not region_id:
            raise ValueError("generated region missing identity")
        if region_id in out:
            raise ValueError(f"duplicate generated region identity: {region_id}")
        out[region_id] = region
    return out


def _region_triangle_indices(mesh: dict, region: dict) -> list[int]:
    start = int(region["triangle_start"])
    count = int(region["triangle_count"])
    total = len(mesh.get("triangles", []))
    if start < 0 or count <= 0 or start + count > total:
        raise ValueError(f"invalid generated region triangle range: {region.get('id')}")
    return list(range(start, start + count))


def derive_partition(source: dict, mesh: dict, contract: dict, branch_id: str) -> dict:
    validate_contract(contract)
    if branch_id not in contract["branch_ids"]:
        raise ValueError(f"unknown or unauthorized branch selector: {branch_id}")

    branch = _branch(source, branch_id)
    cluster = _leaf_cluster(source, branch_id)
    zone = _flex_zone(source, branch_id)
    points = branch.get("points", [])
    radii = branch.get("radii", [])
    blades = cluster.get("blades", [])
    if len(points) < 2 or len(points) != len(radii):
        raise ValueError(f"branch geometry malformed: {branch_id}")
    if not blades:
        raise ValueError(f"branch leaf cluster empty: {branch_id}")
    if zone.get("status") != FLEX_STATUS:
        raise ValueError(f"branch flex status promoted: {branch_id}")
    if not _same_vec3(zone.get("center"), points[0]):
        raise ValueError(f"branch flex center drift: {branch_id}")

    regions = _region_map(mesh)
    expected_branch_regions = [f"branch:{branch_id}:{i}" for i in range(len(points) - 1)]
    expected_leaf_regions = [f"leaf:{branch_id}-leaves:{i}" for i in range(len(blades))]
    expected_regions = expected_branch_regions + expected_leaf_regions
    if any(region_id not in regions for region_id in expected_regions):
        missing = [region_id for region_id in expected_regions if region_id not in regions]
        raise ValueError(f"generated child region missing for {branch_id}: {missing}")

    triangle_indices: list[int] = []
    for region_id in expected_regions:
        triangle_indices.extend(_region_triangle_indices(mesh, regions[region_id]))
    if len(set(triangle_indices)) != len(triangle_indices):
        raise ValueError(f"overlapping generated region triangle ranges: {branch_id}")

    triangles = mesh.get("triangles", [])
    vertex_indices = sorted({int(index) for tri_index in triangle_indices for index in triangles[tri_index]})
    if any(index < 0 or index >= len(mesh.get("vertices", [])) for index in vertex_indices):
        raise ValueError(f"generated child vertex index out of range: {branch_id}")

    row = {
        "branch_id": branch_id,
        "root_center_m": [float(value) for value in points[0]],
        "flex_zone_id": zone["id"],
        "flex_radius_m": float(zone["radius"]),
        "flex_status": zone["status"],
        "branch_region_ids": expected_branch_regions,
        "leaf_region_ids": expected_leaf_regions,
        "region_ids": expected_regions,
        "vertex_indices": vertex_indices,
        "triangle_indices": sorted(triangle_indices),
        "vertex_count": len(vertex_indices),
        "triangle_count": len(triangle_indices),
        "fixed_vertex_count": len(mesh.get("vertices", [])) - len(vertex_indices),
        "source_authorized": False,
        "rigging_authorized": False,
        "deformation_tested": False,
        "relation": RELATION,
    }
    row["vertex_index_digest"] = digest(vertex_indices)
    row["partition_digest"] = digest({key: value for key, value in row.items() if key != "partition_digest"})
    return row


def assemble_family(source: dict, mesh: dict, contract: dict, branch_ids: Iterable[str] | None = None) -> dict:
    validate_contract(contract)
    requested = list(contract["branch_ids"] if branch_ids is None else branch_ids)
    if len(set(requested)) != len(requested):
        raise ValueError("duplicate branch selector")
    if set(requested) != set(contract["branch_ids"]):
        raise ValueError("family must contain the exact authorized branch identity set")

    partitions = [derive_partition(source, mesh, contract, branch_id) for branch_id in requested]
    partitions.sort(key=lambda row: row["branch_id"])
    vertex_sets = [set(row["vertex_indices"]) for row in partitions]
    pairwise_disjoint = all(not (vertex_sets[i] & vertex_sets[j]) for i in range(len(vertex_sets)) for j in range(i + 1, len(vertex_sets)))
    if not pairwise_disjoint:
        raise ValueError("primary branch child partitions overlap in generated vertex identity")

    if len({row["partition_digest"] for row in partitions}) != len(partitions):
        raise ValueError("materially distinct branch partitions did not produce distinct identities")
    if len({row["vertex_index_digest"] for row in partitions}) != len(partitions):
        raise ValueError("branch partitions did not produce distinct vertex-index identities")

    family_core = {
        "schema": SCHEMA,
        "family_id": contract["family_id"],
        "relation": RELATION,
        "branch_count": len(partitions),
        "partitions": partitions,
        "pairwise_vertex_disjoint": pairwise_disjoint,
    }
    return {**family_core, "family_digest": digest(family_core)}

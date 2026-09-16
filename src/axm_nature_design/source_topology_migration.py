"""Evidence contract for the Nature tapered-cap source-generator migration.

This module does not own Organic source form. It verifies that the current shared
Nature generator emits exactly the already-proven Geometry reindex candidates for
three established source studies, while retaining the historical baseline digests
as lineage evidence.
"""
from __future__ import annotations

from collections import defaultdict

from .organic_form import build_mesh, digest, structural_checks

SCHEMA = "axm.nature-source-topology-migration-evidence/v0.1"
GEOMETRY_ORACLE_REF = "e2224d4bf88f7e68503072c884e5a726b8d0c53d"

LINEAGE = {
    "sapling-neutral-001": {
        "source_ref": "fbc202449981f2bac153951c561ed0ed6120c936",
        "source_digest": "a61207b23c441b2cc0becd165fa62289bb7e51065ae0d6fa56bf9f3cab036cc1",
        "historical_mesh_digest": "89b835bd8f3e728206543d210787f1bbd1cc1bacb6d01f6695caf3ea1a63fa4c",
        "proven_reindex_digest": "47dd4d82651138299d05071df3e8a410f21f673ab8d42b936d7222eb5351b862",
    },
    "compact-east-tree-neutral-001": {
        "source_ref": "64116d63fc76daa1623b5fd5046a4e6074100bda",
        "source_digest": "9c87cf26f02f7adee832908652942218ec779c9029a0611aae1fb66eb0f62f54",
        "historical_mesh_digest": "c7367ed5dcea6ebe39869c48fd653845b25c9a8725a2e637a1d6f2fbee1fa32f",
        "proven_reindex_digest": "420135f6effbadb1b344675948b9ddc471dcb83177702888f0b32327c5121c18",
    },
    "east-rear-tree-neutral-001": {
        "source_ref": "a4e5ee011e1d87f47866a7e6c6f4e66f57b6af12",
        "source_digest": "0adf2cde8cfc355ec21b6fb06c6759b753300164b5f72ba029dc1b8c6d2ef307",
        "historical_mesh_digest": "d7fc5deaa1c12d1d8c7d7b6dc95bf1e8544ce26140ee2e4a7d2c67a2c4133e48",
        "proven_reindex_digest": "aa9d450a78fef722672ea9af0f9aca98b4c1a0ca3705661784f5f61f3e9b6a31",
    },
}


def inspect_shared_edge_orientation(mesh: dict) -> dict:
    """Count exact indexed shared-edge orientation conflicts without welding seams."""
    vertices = mesh.get("vertices", [])
    triangles = mesh.get("triangles", [])
    edge_faces: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
    for face_index, triangle in enumerate(triangles):
        if not isinstance(triangle, list) or len(triangle) != 3:
            raise ValueError(f"triangle {face_index} must contain three indices")
        if any(type(index) is not int or index < 0 or index >= len(vertices) for index in triangle):
            raise ValueError(f"triangle {face_index} contains an out-of-range index")
        a, b, c = triangle
        for start, end in ((a, b), (b, c), (c, a)):
            key = (start, end) if start < end else (end, start)
            edge_faces[key].append((start, end))

    boundary = 0
    nonmanifold = 0
    conflicts = 0
    for incidents in edge_faces.values():
        if len(incidents) == 1:
            boundary += 1
        elif len(incidents) > 2:
            nonmanifold += 1
        elif incidents[0] == incidents[1]:
            conflicts += 1
    return {
        "unique_edges": len(edge_faces),
        "boundary_edges": boundary,
        "nonmanifold_edges": nonmanifold,
        "shared_edge_orientation_conflicts": conflicts,
    }


def evaluate(source: dict) -> dict:
    study_id = source.get("study_id")
    if study_id not in LINEAGE:
        raise ValueError(f"unrecognized migration source study: {study_id}")
    expected = LINEAGE[study_id]
    source_digest = digest(source)
    mesh = build_mesh(source)
    mesh_digest = digest(mesh)
    topology = inspect_shared_edge_orientation(mesh)
    structural = structural_checks(mesh)

    checks = {
        "exact_source_identity_preserved": source_digest == expected["source_digest"],
        "source_generator_matches_proven_reindex_candidate": mesh_digest == expected["proven_reindex_digest"],
        "historical_and_migrated_mesh_identities_are_distinct": mesh_digest != expected["historical_mesh_digest"],
        "expected_vertex_count_preserved": len(mesh["vertices"]) == 390,
        "expected_triangle_count_preserved": len(mesh["triangles"]) == 570,
        "shared_edge_orientation_conflicts_zero": topology["shared_edge_orientation_conflicts"] == 0,
        "boundary_edges_preserved": topology["boundary_edges"] == 100,
        "nonmanifold_edges_zero": topology["nonmanifold_edges"] == 0,
        "organic_structural_checks_pass": structural["pass"],
    }
    passed = all(checks.values())
    return {
        "schema": SCHEMA,
        "study_id": study_id,
        "status": "PASS_SOURCE_GENERATOR_WINDING_MIGRATION" if passed else "FAIL",
        "source_ref": expected["source_ref"],
        "source_digest": source_digest,
        "historical_mesh_digest": expected["historical_mesh_digest"],
        "geometry_oracle_ref": GEOMETRY_ORACLE_REF,
        "proven_reindex_digest": expected["proven_reindex_digest"],
        "migrated_mesh_digest": mesh_digest,
        "vertices": len(mesh["vertices"]),
        "triangles": len(mesh["triangles"]),
        "topology": topology,
        "structural": structural,
        "checks": checks,
        "truth_boundary": {
            "source_json_rewritten": False,
            "source_generator_index_emission_changed": True,
            "vertex_positions_changed_from_proven_candidate": False,
            "triangle_membership_changed_from_proven_candidate": False,
            "historical_mesh_receipts_rewritten": False,
            "connected_production_topology_proven": False,
            "self_intersection_checked": False,
            "normals_tangents_uvs_accepted": False,
            "deformation_accepted": False,
            "visual_receiving_scene_accepted": False,
            "runtime_or_gameplay_accepted": False,
        },
    }

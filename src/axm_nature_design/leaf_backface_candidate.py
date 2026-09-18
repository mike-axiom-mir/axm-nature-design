"""Derived Geometry candidate for explicit two-sided Nature leaf blades.

This module does not rewrite Nature source form or the migrated source generator.
It derives a review-only mesh candidate from the exact current generated mesh by
adding a disjoint, opposite-wound copy of each planar leaf blade. The purpose is
to make the existing thin-plane backface hold structurally testable before any
source migration or receiving-scene adoption.
"""
from __future__ import annotations

import copy

from .organic_form import build_mesh, digest, structural_checks, _cross, _sub, _length
from .source_topology_migration import LINEAGE, inspect_shared_edge_orientation

SCHEMA = "axm.nature-leaf-backface-candidate-evidence/v0.1"
BASE_SOURCE_MIGRATION_REF = "4ddbe66e5c02d22407ef773d5346a2fe6f349a2d"


def _triangle_normal(mesh: dict, triangle: list[int]) -> list[float]:
    a, b, c = (mesh["vertices"][index] for index in triangle)
    return _cross(_sub(b, a), _sub(c, a))


def _bounds(vertices: list[list[float]]) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    return (
        tuple(min(vertex[axis] for vertex in vertices) for axis in range(3)),
        tuple(max(vertex[axis] for vertex in vertices) for axis in range(3)),
    )


def add_explicit_leaf_backfaces(mesh: dict) -> dict:
    """Return a derived mesh with one disjoint opposite-wound copy per leaf blade.

    Original vertices, triangles and regions remain an exact prefix. Duplicate
    vertices are intentional so opposite coplanar faces do not create indexed
    non-manifold edges or corrupt the already-proven branch/trunk topology.
    """
    candidate = copy.deepcopy(mesh)
    original_regions = list(mesh.get("regions", []))
    for region in original_regions:
        if region.get("kind") != "leaf-blade":
            continue
        triangle_start = int(region["triangle_start"])
        triangle_count = int(region["triangle_count"])
        if triangle_count != 2:
            raise ValueError(f"leaf region {region.get('id')} must contain exactly two triangles")
        source_triangles = mesh["triangles"][triangle_start:triangle_start + triangle_count]
        source_indices = sorted({index for triangle in source_triangles for index in triangle})
        if len(source_indices) != 4:
            raise ValueError(f"leaf region {region.get('id')} must contain exactly four indexed vertices")
        mapping: dict[int, int] = {}
        for source_index in source_indices:
            mapping[source_index] = len(candidate["vertices"])
            candidate["vertices"].append(list(mesh["vertices"][source_index]))
        backface_start = len(candidate["triangles"])
        for triangle in source_triangles:
            a, b, c = triangle
            candidate["triangles"].append([mapping[a], mapping[c], mapping[b]])
        candidate["regions"].append(
            {
                "id": f"{region['id']}:backface",
                "triangle_start": backface_start,
                "triangle_count": triangle_count,
                "kind": "leaf-blade-backface",
                "source_region": region["id"],
            }
        )
    return candidate


def inspect_leaf_pairs(baseline: dict, candidate: dict) -> dict:
    leaf_regions = [region for region in baseline["regions"] if region.get("kind") == "leaf-blade"]
    back_regions = [region for region in candidate["regions"] if region.get("kind") == "leaf-blade-backface"]
    back_by_source = {region["source_region"]: region for region in back_regions}
    exact_position_pairs = 0
    opposite_winding_pairs = 0
    minimum_normal_cosine = 1.0
    for front in leaf_regions:
        back = back_by_source.get(front["id"])
        if back is None:
            continue
        front_triangles = baseline["triangles"][front["triangle_start"]:front["triangle_start"] + front["triangle_count"]]
        back_triangles = candidate["triangles"][back["triangle_start"]:back["triangle_start"] + back["triangle_count"]]
        if len(front_triangles) != len(back_triangles):
            continue
        pair_exact = True
        pair_opposite = True
        for front_triangle, back_triangle in zip(front_triangles, back_triangles):
            front_positions = [baseline["vertices"][index] for index in front_triangle]
            back_positions = [candidate["vertices"][index] for index in back_triangle]
            if back_positions != [front_positions[0], front_positions[2], front_positions[1]]:
                pair_exact = False
            front_normal = _triangle_normal(baseline, front_triangle)
            back_normal = _triangle_normal(candidate, back_triangle)
            front_len = _length(front_normal)
            back_len = _length(back_normal)
            if front_len <= 1e-12 or back_len <= 1e-12:
                pair_opposite = False
                cosine = 1.0
            else:
                cosine = sum(a*b for a, b in zip(front_normal, back_normal)) / (front_len * back_len)
                if cosine > -0.999999999:
                    pair_opposite = False
            minimum_normal_cosine = min(minimum_normal_cosine, cosine)
        if pair_exact:
            exact_position_pairs += 1
        if pair_opposite:
            opposite_winding_pairs += 1
    return {
        "leaf_blades": len(leaf_regions),
        "backface_regions": len(back_regions),
        "exact_position_pairs": exact_position_pairs,
        "opposite_winding_pairs": opposite_winding_pairs,
        "minimum_front_back_normal_cosine": minimum_normal_cosine,
    }


def evaluate(source: dict) -> dict:
    study_id = source.get("study_id")
    if study_id not in LINEAGE:
        raise ValueError(f"unrecognized Nature source study: {study_id}")
    expected = LINEAGE[study_id]
    source_digest = digest(source)
    baseline = build_mesh(source)
    baseline_digest = digest(baseline)
    candidate = add_explicit_leaf_backfaces(baseline)
    candidate_digest = digest(candidate)
    pairs = inspect_leaf_pairs(baseline, candidate)
    structural = structural_checks(candidate)
    topology = inspect_shared_edge_orientation(candidate)
    leaf_count = pairs["leaf_blades"]
    checks = {
        "exact_source_identity_preserved": source_digest == expected["source_digest"],
        "exact_migrated_baseline_identity_preserved": baseline_digest == expected["proven_reindex_digest"],
        "baseline_vertices_are_exact_prefix": candidate["vertices"][:len(baseline["vertices"])] == baseline["vertices"],
        "baseline_triangles_are_exact_prefix": candidate["triangles"][:len(baseline["triangles"])] == baseline["triangles"],
        "baseline_regions_are_exact_prefix": candidate["regions"][:len(baseline["regions"])] == baseline["regions"],
        "one_backface_region_per_leaf": pairs["backface_regions"] == leaf_count,
        "all_leaf_positions_paired_exactly": pairs["exact_position_pairs"] == leaf_count,
        "all_leaf_winding_opposed": pairs["opposite_winding_pairs"] == leaf_count,
        "vertex_delta_is_four_per_leaf": len(candidate["vertices"]) - len(baseline["vertices"]) == 4 * leaf_count,
        "triangle_delta_is_two_per_leaf": len(candidate["triangles"]) - len(baseline["triangles"]) == 2 * leaf_count,
        "bounds_unchanged": _bounds(candidate["vertices"]) == _bounds(baseline["vertices"]),
        "candidate_structural_checks_pass": structural["pass"],
        "candidate_nonmanifold_edges_zero": topology["nonmanifold_edges"] == 0,
        "candidate_shared_edge_orientation_conflicts_zero": topology["shared_edge_orientation_conflicts"] == 0,
        "candidate_identity_is_distinct": candidate_digest != baseline_digest,
    }
    passed = all(checks.values())
    return {
        "schema": SCHEMA,
        "study_id": study_id,
        "status": "PASS_EXPLICIT_DISJOINT_LEAF_BACKFACE_CANDIDATE" if passed else "FAIL",
        "base_source_migration_ref": BASE_SOURCE_MIGRATION_REF,
        "source_digest": source_digest,
        "baseline_mesh_digest": baseline_digest,
        "candidate_mesh_digest": candidate_digest,
        "baseline_vertices": len(baseline["vertices"]),
        "candidate_vertices": len(candidate["vertices"]),
        "baseline_triangles": len(baseline["triangles"]),
        "candidate_triangles": len(candidate["triangles"]),
        "pairs": pairs,
        "topology": topology,
        "structural": structural,
        "checks": checks,
        "truth_boundary": {
            "source_json_rewritten": False,
            "source_generator_rewritten": False,
            "baseline_mesh_rewritten": False,
            "candidate_is_derived_review_only": True,
            "leaf_vertex_positions_changed": False,
            "leaf_front_faces_changed": False,
            "explicit_disjoint_opposite_wound_faces_added": True,
            "renderer_backface_behavior_proven": False,
            "final_leaf_thickness_or_surface_quality_proven": False,
            "normals_tangents_uvs_materials_accepted": False,
            "deformation_or_wind_accepted": False,
            "runtime_cost_accepted": False,
            "receiving_scene_visual_acceptance": False,
            "gameplay_or_production_readiness": False,
        },
    }

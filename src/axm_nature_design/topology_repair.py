"""Nature-local topology repair evidence for tapered-segment cap winding.

The Organic generator remains source authority. This module does not reshape the
source or silently replace it. It derives a candidate by reversing only the two
cap-triangle windings emitted per side by the existing tapered-segment layout.
Vertex positions, triangle vertex membership, region identity and component
structure remain unchanged so visual/deformation/runtime acceptance can stay
separate.
"""
from __future__ import annotations

import copy
from collections import defaultdict

from .organic_form import build_mesh, digest, structural_checks

EVIDENCE_SCHEMA = "axm.nature-tapered-cap-winding-evidence/v0.1"


def inspect_index_topology(mesh: dict) -> dict:
    vertices = mesh.get("vertices", [])
    triangles = mesh.get("triangles", [])
    edge_faces: dict[tuple[int, int], list[tuple[int, tuple[int, int]]]] = defaultdict(list)
    face_adjacency = [set() for _ in triangles]

    for face_index, triangle in enumerate(triangles):
        if not isinstance(triangle, list) or len(triangle) != 3:
            raise ValueError(f"triangle {face_index} must contain three indices")
        if any(type(index) is not int or index < 0 or index >= len(vertices) for index in triangle):
            raise ValueError(f"triangle {face_index} contains an out-of-range index")
        if len(set(triangle)) != 3:
            raise ValueError(f"triangle {face_index} is collapsed by index")
        a, b, c = triangle
        for start, end in ((a, b), (b, c), (c, a)):
            key = (start, end) if start < end else (end, start)
            edge_faces[key].append((face_index, (start, end)))

    boundary_edges = 0
    nonmanifold_edges = 0
    orientation_conflicts = 0
    for incidents in edge_faces.values():
        if len(incidents) == 1:
            boundary_edges += 1
        elif len(incidents) > 2:
            nonmanifold_edges += 1
        if len(incidents) == 2:
            (left_face, left_direction), (right_face, right_direction) = incidents
            face_adjacency[left_face].add(right_face)
            face_adjacency[right_face].add(left_face)
            if left_direction == right_direction:
                orientation_conflicts += 1

    remaining = set(range(len(triangles)))
    components = 0
    while remaining:
        components += 1
        stack = [remaining.pop()]
        while stack:
            current = stack.pop()
            for neighbor in face_adjacency[current]:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    stack.append(neighbor)

    return {
        "vertices": len(vertices),
        "triangles": len(triangles),
        "unique_edges": len(edge_faces),
        "boundary_edges": boundary_edges,
        "nonmanifold_edges": nonmanifold_edges,
        "shared_edge_orientation_conflicts": orientation_conflicts,
        "edge_connected_components": components,
    }


def repair_tapered_segment_cap_winding(mesh: dict) -> tuple[dict, list[int]]:
    """Return a reindexed candidate with tapered-segment cap faces reversed only.

    `_add_tapered_segment()` emits four triangles per radial side in this order:
    side, side, start-cap, end-cap. The current cap faces traverse their shared
    perimeter edges in the same direction as the adjacent side face. Reversing
    only those cap triangles restores opposite traversal across shared manifold
    edges without moving vertices or changing triangle membership.
    """
    candidate = copy.deepcopy(mesh)
    triangles = candidate.get("triangles")
    regions = candidate.get("regions")
    if not isinstance(triangles, list) or not isinstance(regions, list):
        raise ValueError("mesh must provide triangles and regions lists")

    flipped: list[int] = []
    for region in regions:
        if region.get("kind") != "tapered-segment":
            continue
        start = region.get("triangle_start")
        count = region.get("triangle_count")
        if type(start) is not int or type(count) is not int or start < 0 or count <= 0:
            raise ValueError(f"invalid tapered region range for {region.get('id')}")
        if count % 4:
            raise ValueError(f"tapered region {region.get('id')} does not match four-triangles-per-side layout")
        if start + count > len(triangles):
            raise ValueError(f"tapered region {region.get('id')} exceeds triangle array")
        for offset in range(0, count, 4):
            for local in (2, 3):
                index = start + offset + local
                a, b, c = triangles[index]
                triangles[index] = [a, c, b]
                flipped.append(index)
    if not flipped:
        raise ValueError("mesh contains no tapered-segment regions to repair")
    return candidate, flipped


def evaluate(source: dict) -> dict:
    baseline = build_mesh(source)
    candidate, flipped = repair_tapered_segment_cap_winding(baseline)
    before = inspect_index_topology(baseline)
    after = inspect_index_topology(candidate)

    same_membership = all(
        sorted(left) == sorted(right)
        for left, right in zip(baseline["triangles"], candidate["triangles"])
    ) and len(baseline["triangles"]) == len(candidate["triangles"])
    checks = {
        "vertices_exactly_unchanged": baseline["vertices"] == candidate["vertices"],
        "regions_exactly_unchanged": baseline["regions"] == candidate["regions"],
        "triangle_count_unchanged": len(baseline["triangles"]) == len(candidate["triangles"]),
        "triangle_vertex_membership_unchanged": same_membership,
        "baseline_conflict_is_reproduced": before["shared_edge_orientation_conflicts"] > 0,
        "candidate_shared_edge_orientation_conflicts_zero": after["shared_edge_orientation_conflicts"] == 0,
        "boundary_edge_count_unchanged": before["boundary_edges"] == after["boundary_edges"],
        "nonmanifold_edge_count_unchanged": before["nonmanifold_edges"] == after["nonmanifold_edges"],
        "edge_connected_components_unchanged": before["edge_connected_components"] == after["edge_connected_components"],
        "candidate_structural_checks_pass": structural_checks(candidate)["pass"],
    }
    passed = all(checks.values())
    return {
        "schema": EVIDENCE_SCHEMA,
        "study_id": source.get("study_id"),
        "status": "PASS_TAPERED_CAP_WINDING_REPAIR" if passed else "FAIL",
        "source_digest": digest(source),
        "baseline_mesh_digest": digest(baseline),
        "candidate_mesh_digest": digest(candidate),
        "flipped_triangle_count": len(flipped),
        "flipped_triangle_indices": flipped,
        "before": before,
        "after": after,
        "checks": checks,
        "truth_boundary": {
            "source_rewritten": False,
            "vertex_positions_changed": False,
            "triangle_vertex_membership_changed": False,
            "region_identity_changed": False,
            "production_connected_vegetation_topology_proven": False,
            "self_intersection_checked": False,
            "deformation_tested": False,
            "normals_or_tangents_authored": False,
            "uvs_or_materials_tested": False,
            "visual_acceptance_claimed": False,
            "runtime_or_gameplay_acceptance_claimed": False,
        },
    }

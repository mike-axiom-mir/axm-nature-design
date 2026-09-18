"""Geometry-owned topology classification for the north-low diagnostic child.

Rigging's parent-influence exclusion gate is a transform-policy result.  It must not be
silently promoted into a claim that the generated branch is a connected production
junction with the trunk.  This observer re-executes the exact Rigging owner, inspects
only indexed triangle topology, and records the actual attachment class of the current
Geometry receiver.

No source form, Rigging transform, material, animation, target-host, runtime, collision,
or aesthetic acceptance is changed here.
"""
from __future__ import annotations

from collections import Counter, defaultdict, deque

from .organic_form import build_mesh, digest, validate_source
from . import rear_tree_rigging_north_low_parent_influence_gate as rig_gate

SCHEMA = "axm.nature-north-low-attachment-topology-geometry-evidence/v0.1"
RESULT = "PASS_NORTH_LOW_DIAGNOSTIC_CHILD_TOPOLOGY_CLASSIFIED__HOLD_CONNECTED_BRANCH_TRUNK_ATTACHMENT"
STUDY_ID = rig_gate.STUDY_ID
SOURCE_OWNER_HEAD = rig_gate.SOURCE_OWNER_HEAD
EXPECTED_SOURCE_DIGEST = rig_gate.EXPECTED_SOURCE_DIGEST
EXPECTED_MESH_DIGEST = rig_gate.EXPECTED_MIGRATED_MESH_DIGEST
GEOMETRY_PREDECESSOR_HEAD = "200ab4b60b8a54460f1265b0ee52eb111f1b280a"
RIGGING_OWNER_HEAD = "975931b11555d156e04e2ab12e9756fc6c9598a3"
BRANCH_ID = "north-low"
EXPECTED_SELECTED_VERTICES = 52
EXPECTED_SELECTED_TRIANGLES = 72
EXPECTED_COMPONENT_COUNT = 6


def _region_triangle_indices(mesh: dict, region_ids) -> list[int]:
    wanted = set(region_ids)
    found = set()
    indices: list[int] = []
    for region in mesh["regions"]:
        if region["id"] not in wanted:
            continue
        found.add(region["id"])
        start = int(region["triangle_start"])
        count = int(region["triangle_count"])
        indices.extend(range(start, start + count))
    if found != wanted:
        missing = sorted(wanted - found)
        extra = sorted(found - wanted)
        raise ValueError(f"region identity mismatch; missing={missing} extra={extra}")
    return sorted(indices)


def _vertices_for_triangles(mesh: dict, triangle_indices) -> set[int]:
    vertices: set[int] = set()
    for triangle_index in triangle_indices:
        vertices.update(int(i) for i in mesh["triangles"][triangle_index])
    return vertices


def _edges_for_triangles(mesh: dict, triangle_indices) -> Counter:
    edges: Counter = Counter()
    for triangle_index in triangle_indices:
        a, b, c = (int(i) for i in mesh["triangles"][triangle_index])
        for left, right in ((a, b), (b, c), (c, a)):
            edges[tuple(sorted((left, right)))] += 1
    return edges


def _edge_connected_components(mesh: dict, triangle_indices) -> list[list[int]]:
    triangle_indices = list(triangle_indices)
    edge_to_triangles: dict[tuple[int, int], list[int]] = defaultdict(list)
    for triangle_index in triangle_indices:
        a, b, c = (int(i) for i in mesh["triangles"][triangle_index])
        for left, right in ((a, b), (b, c), (c, a)):
            edge_to_triangles[tuple(sorted((left, right)))].append(triangle_index)

    adjacency: dict[int, set[int]] = {index: set() for index in triangle_indices}
    for owners in edge_to_triangles.values():
        for left in owners:
            adjacency[left].update(right for right in owners if right != left)

    unseen = set(triangle_indices)
    components: list[list[int]] = []
    while unseen:
        seed = min(unseen)
        queue = deque([seed])
        unseen.remove(seed)
        component: list[int] = []
        while queue:
            current = queue.popleft()
            component.append(current)
            for neighbor in sorted(adjacency[current]):
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    queue.append(neighbor)
        components.append(sorted(component))
    return sorted(components, key=lambda row: (len(row), row[0]))


def _component_summary(mesh: dict, triangle_indices) -> dict:
    triangle_indices = list(triangle_indices)
    vertices = _vertices_for_triangles(mesh, triangle_indices)
    edges = _edges_for_triangles(mesh, triangle_indices)
    boundary_edges = sum(1 for count in edges.values() if count == 1)
    nonmanifold_edges = sum(1 for count in edges.values() if count > 2)
    euler_characteristic = len(vertices) - len(edges) + len(triangle_indices)
    return {
        "vertices": len(vertices),
        "triangles": len(triangle_indices),
        "edges": len(edges),
        "boundary_edges": boundary_edges,
        "nonmanifold_edges": nonmanifold_edges,
        "euler_characteristic": euler_characteristic,
        "closed_edge_manifold": boundary_edges == 0 and nonmanifold_edges == 0,
    }


def evaluate(
    source: dict,
    *,
    requested_rigging_owner_head: str = RIGGING_OWNER_HEAD,
    requested_geometry_predecessor_head: str = GEOMETRY_PREDECESSOR_HEAD,
    claim_connected_branch_trunk_attachment: bool = False,
    claim_production_topology: bool = False,
    claim_skinning_acceptance: bool = False,
    claim_runtime_acceptance: bool = False,
) -> dict:
    """Classify the exact north-low receiver topology without mutating it."""
    validate_source(source)
    if source.get("study_id") != STUDY_ID:
        raise ValueError("unexpected Nature study identity")
    if digest(source) != EXPECTED_SOURCE_DIGEST:
        raise ValueError("exact Organic source identity drift")
    if requested_rigging_owner_head != RIGGING_OWNER_HEAD:
        raise ValueError("exact Rigging owner head drift")
    if requested_geometry_predecessor_head != GEOMETRY_PREDECESSOR_HEAD:
        raise ValueError("exact Geometry predecessor head drift")
    if claim_connected_branch_trunk_attachment:
        raise ValueError("current generated receiver does not prove indexed branch/trunk attachment")
    if claim_production_topology:
        raise ValueError("diagnostic generated topology may not be promoted to production topology")
    if claim_skinning_acceptance:
        raise ValueError("Geometry topology evidence cannot claim production skinning acceptance")
    if claim_runtime_acceptance:
        raise ValueError("Geometry topology evidence cannot claim Runtime acceptance")

    rigging = rig_gate.evaluate(source)
    if rigging["result"] != rig_gate.RESULT:
        raise ValueError("exact Rigging north-low exclusion owner no longer passes")
    if rigging["rigging_constraint"]["upper_trunk_parent_influence_enabled_for_north_low"] is not False:
        raise ValueError("north-low exclusion gate state drift")

    mesh = build_mesh(source)
    mesh_digest = digest(mesh)
    if mesh_digest != EXPECTED_MESH_DIGEST:
        raise ValueError("exact Geometry migrated receiver identity drift")

    child = rigging["child_socket"]
    selected_indices = [int(i) for i in child["selected_vertex_indices"]]
    selected_set = set(selected_indices)
    selected_regions = list(child["selected_regions"])
    child_triangle_indices = _region_triangle_indices(mesh, selected_regions)
    child_vertices_from_faces = _vertices_for_triangles(mesh, child_triangle_indices)

    if len(selected_indices) != EXPECTED_SELECTED_VERTICES:
        raise ValueError("north-low selected vertex count drift")
    if len(child_triangle_indices) != EXPECTED_SELECTED_TRIANGLES:
        raise ValueError("north-low selected triangle count drift")
    if child_vertices_from_faces != selected_set:
        raise ValueError("north-low selected vertices no longer equal the exact owned triangle support")

    trunk_regions = [row["id"] for row in mesh["regions"] if row["id"].startswith("trunk:")]
    trunk_triangle_indices = _region_triangle_indices(mesh, trunk_regions)
    trunk_vertices = _vertices_for_triangles(mesh, trunk_triangle_indices)
    shared_indexed_vertices = sorted(selected_set & trunk_vertices)

    components = _edge_connected_components(mesh, child_triangle_indices)
    component_summaries = [_component_summary(mesh, component) for component in components]
    closed_components = [row for row in component_summaries if row["closed_edge_manifold"]]
    open_components = [row for row in component_summaries if not row["closed_edge_manifold"]]

    root_region_id = f"branch:{BRANCH_ID}:0"
    root_triangle_indices = _region_triangle_indices(mesh, [root_region_id])
    root_summary = _component_summary(mesh, root_triangle_indices)

    expected_component_signature = sorted(
        [(18, 32, 48, 0, 2), (18, 32, 48, 0, 2)]
        + [(4, 2, 5, 4, 1)] * 4
    )
    actual_component_signature = sorted(
        (
            row["vertices"],
            row["triangles"],
            row["edges"],
            row["boundary_edges"],
            row["euler_characteristic"],
        )
        for row in component_summaries
    )

    checks = {
        "exact_rigging_owner_reexecuted": rigging["result"] == rig_gate.RESULT,
        "exact_receiver_identity": mesh_digest == EXPECTED_MESH_DIGEST,
        "north_low_partition_is_triangle_closed": child_vertices_from_faces == selected_set,
        "north_low_component_count_is_six": len(components) == EXPECTED_COMPONENT_COUNT,
        "north_low_component_signature_matches_generator": actual_component_signature == expected_component_signature,
        "north_low_has_two_closed_tapered_segment_components": len(closed_components) == 2,
        "north_low_has_four_open_leaf_components": len(open_components) == 4,
        "root_branch_segment_is_closed_capped_shell": root_summary == {
            "vertices": 18,
            "triangles": 32,
            "edges": 48,
            "boundary_edges": 0,
            "nonmanifold_edges": 0,
            "euler_characteristic": 2,
            "closed_edge_manifold": True,
        },
        "north_low_and_trunk_share_no_indexed_vertices": len(shared_indexed_vertices) == 0,
    }
    if not all(checks.values()):
        raise ValueError(f"north-low attachment topology invariant failed: {checks}")

    return {
        "schema": SCHEMA,
        "result": RESULT,
        "study_id": STUDY_ID,
        "source_owner_head": SOURCE_OWNER_HEAD,
        "source_digest": EXPECTED_SOURCE_DIGEST,
        "geometry_predecessor_head": GEOMETRY_PREDECESSOR_HEAD,
        "rigging_owner_head": RIGGING_OWNER_HEAD,
        "geometry_receiver_mesh_digest": mesh_digest,
        "branch_id": BRANCH_ID,
        "indexed_topology": {
            "selected_vertices": len(selected_indices),
            "selected_triangles": len(child_triangle_indices),
            "edge_connected_components": len(components),
            "closed_edge_manifold_components": len(closed_components),
            "open_components": len(open_components),
            "component_summaries": component_summaries,
            "root_branch_segment": root_summary,
            "trunk_regions": len(trunk_regions),
            "shared_indexed_vertices_with_trunk": shared_indexed_vertices,
            "indexed_branch_trunk_attachment_proven": False,
        },
        "interpretation": {
            "rigging_parent_influence_gate_is_transform_policy_not_topology_attachment": True,
            "current_child_is_one_connected_manifold": False,
            "current_root_segment_is_open_for_welded_attachment": False,
            "production_welded_branch_trunk_junction_proven": False,
            "reusable_rule": "SPATIAL_OR_RIGGING_ATTACHMENT_EVIDENCE_MUST_DECLARE_INDEXED_CONNECTIVITY_CLASS_BEFORE_CONNECTED_TOPOLOGY_PASS_TRANSFER",
        },
        "checks": checks,
        "truth_boundary": {
            "source_mutated": False,
            "rigging_mutated": False,
            "connected_branch_trunk_attachment_claimed": False,
            "production_topology_claimed": False,
            "skinning_acceptance_claimed": False,
            "animation_or_vfx_acceptance_claimed": False,
            "target_host_acceptance_claimed": False,
            "runtime_or_device_acceptance_claimed": False,
            "collision_or_gameplay_suitability_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }

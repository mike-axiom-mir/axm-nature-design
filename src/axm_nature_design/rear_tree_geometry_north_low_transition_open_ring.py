"""Geometry-owned open transition-ring candidate for the north-low branch.

Organic Form owns the neutral radial-support exit measurement and Procedural Design
canonicalizes that owner measurement. Geometry consumes that exact bounded handoff to
construct one *diagnostic* branch-side open boundary ring: the first branch segment is
trimmed at the owner transition parameter, leaving a single simple 8-edge boundary loop
that a future Geometry pass could bridge to an independently proven trunk opening.

The authored source, current generated receiver, Rigging socket, trunk topology and
downstream receivers are not mutated by this candidate.
"""
from __future__ import annotations

from collections import Counter, defaultdict, deque
import math

from .organic_form import digest, validate_source
from . import rear_tree_geometry_north_low_attachment_topology as attachment
from . import rear_tree_rigging_north_low_attachment_representation_gate as rigging

SCHEMA = "axm.nature-north-low-owner-transition-open-ring-geometry-evidence/v0.1"
RESULT = "PASS_NORTH_LOW_OWNER_TRANSITION_OPEN_RING_CANDIDATE__HOLD_TRUNK_OPENING_BRIDGE_CONNECTED_JUNCTION"
STUDY_ID = attachment.STUDY_ID
SOURCE_DIGEST = attachment.EXPECTED_SOURCE_DIGEST
GEOMETRY_PREDECESSOR_HEAD = "d5ebbf26afd466faad259621b60fa33f1126ef3c"
RIGGING_OWNER_HEAD = "69640e558f0c1ac59d4d0e3155676e0967a03d04"
ORGANIC_TRANSITION_OWNER_HEAD = "4b5c291d6b044dafeadd6eeaf4849a6f3d4f4148"
ORGANIC_TRANSITION_OBSERVER_BLOB = "1e8323b9bf6495a9f19704c217808300f3b46757"
PROCEDURAL_TRANSITION_OWNER_HEAD = "b3283e255bfffb2979889fd542a93e35be2a4b03"
PROCEDURAL_TRANSITION_CONTRACT_BLOB = "08df5c1eb79a596a05b37a3187b5fa010e8d658d"
PROCEDURAL_FAMILY_DIGEST = "d742e72e2a5f8be868465d91c286ca8fd6509789936c14a595b4cc18a57fb096"
BRANCH_ID = "north-low"
TRANSITION_U = 0.14801958337760968
TRANSITION_LENGTH_M = 0.0645372173379806
SIDES = 8
TOL = 1e-12
GEOMETRY_TOL = 1e-10


def _sub(a, b):
    return [float(a[i]) - float(b[i]) for i in range(3)]


def _add(a, b):
    return [float(a[i]) + float(b[i]) for i in range(3)]


def _mul(a, scalar):
    return [float(a[i]) * float(scalar) for i in range(3)]


def _dot(a, b):
    return sum(float(a[i]) * float(b[i]) for i in range(3))


def _cross(a, b):
    return [
        float(a[1]) * float(b[2]) - float(a[2]) * float(b[1]),
        float(a[2]) * float(b[0]) - float(a[0]) * float(b[2]),
        float(a[0]) * float(b[1]) - float(a[1]) * float(b[0]),
    ]


def _length(v):
    return math.sqrt(_dot(v, v))


def _norm(v):
    length = _length(v)
    if length <= 1e-18:
        raise ValueError("zero-length vector")
    return [float(value) / length for value in v]


def _lerp(a, b, u):
    return [float(a[i]) + float(u) * (float(b[i]) - float(a[i])) for i in range(3)]


def _frame(a, b):
    axis = _norm(_sub(b, a))
    ref = [0.0, 0.0, 1.0]
    if abs(_dot(axis, ref)) > 0.94:
        ref = [1.0, 0.0, 0.0]
    u = _norm(_cross(axis, ref))
    v = _norm(_cross(axis, u))
    return axis, u, v


def _ring(center, radius, u_axis, v_axis, sides=SIDES):
    vertices = []
    for index in range(sides):
        angle = math.tau * index / sides
        radial = _add(
            _mul(u_axis, math.cos(angle) * radius),
            _mul(v_axis, math.sin(angle) * radius),
        )
        vertices.append(_add(center, radial))
    return vertices


def _branch(source):
    matches = [row for row in source["branches"] if row.get("id") == BRANCH_ID]
    if len(matches) != 1:
        raise ValueError("exact north-low branch identity missing or duplicated")
    return matches[0]


def build_open_transition_stub(source: dict, transition_u: float = TRANSITION_U) -> dict:
    """Build a diagnostic branch-side stub with one open transition boundary.

    This does not mutate ``source`` or the production/diagnostic receiver. The branch
    first segment is sampled at the exact owner transition parameter and only the
    outside portion ``transition_u -> 1`` is represented. The far end remains capped;
    the owner-transition end remains open.
    """
    branch = _branch(source)
    p0 = [float(value) for value in branch["points"][0]]
    p1 = [float(value) for value in branch["points"][1]]
    r0 = float(branch["radii"][0])
    r1 = float(branch["radii"][1])
    if not 0.0 < float(transition_u) < 1.0:
        raise ValueError("transition parameter must lie strictly inside first segment")

    _, u_axis, v_axis = _frame(p0, p1)
    cut_center = _lerp(p0, p1, transition_u)
    cut_radius = r0 + float(transition_u) * (r1 - r0)
    cut_ring = _ring(cut_center, cut_radius, u_axis, v_axis)
    end_ring = _ring(p1, r1, u_axis, v_axis)

    vertices = cut_ring + end_ring + [list(p1)]
    end_center = 2 * SIDES
    triangles = []
    for index in range(SIDES):
        nxt = (index + 1) % SIDES
        a0, a1 = index, nxt
        b0, b1 = SIDES + index, SIDES + nxt
        triangles.extend(
            [
                [a0, b0, b1],
                [a0, b1, a1],
                [end_center, b1, b0],
            ]
        )

    return {
        "schema": "axm.nature-open-transition-stub/v0.1",
        "branch_id": BRANCH_ID,
        "transition_u": float(transition_u),
        "transition_center_m": cut_center,
        "transition_radius_m": cut_radius,
        "vertices": vertices,
        "triangles": triangles,
        "transition_ring_vertex_indices": list(range(SIDES)),
        "far_ring_vertex_indices": list(range(SIDES, 2 * SIDES)),
        "far_cap_center_vertex_index": end_center,
    }


def _edges(triangles):
    counts = Counter()
    directed = defaultdict(list)
    for triangle_index, triangle in enumerate(triangles):
        if len(triangle) != 3:
            raise ValueError("non-triangle face")
        a, b, c = (int(value) for value in triangle)
        for left, right in ((a, b), (b, c), (c, a)):
            key = tuple(sorted((left, right)))
            counts[key] += 1
            directed[key].append((left, right, triangle_index))
    return counts, directed


def _triangle_components(triangles):
    counts, directed = _edges(triangles)
    edge_owners = defaultdict(list)
    for key, owners in directed.items():
        edge_owners[key].extend(row[2] for row in owners)
    adjacency = {index: set() for index in range(len(triangles))}
    for owners in edge_owners.values():
        for left in owners:
            adjacency[left].update(right for right in owners if right != left)
    unseen = set(adjacency)
    components = []
    while unseen:
        seed = min(unseen)
        unseen.remove(seed)
        queue = deque([seed])
        component = []
        while queue:
            current = queue.popleft()
            component.append(current)
            for neighbor in sorted(adjacency[current]):
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    queue.append(neighbor)
        components.append(sorted(component))
    return components, counts, directed


def _boundary_cycles(boundary_edges):
    adjacency = defaultdict(set)
    for left, right in boundary_edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    if not adjacency:
        return []
    if any(len(neighbors) != 2 for neighbors in adjacency.values()):
        raise ValueError("boundary graph is not a union of simple cycles")
    unseen = set(adjacency)
    cycles = []
    while unseen:
        seed = min(unseen)
        current = seed
        previous = None
        cycle = []
        while True:
            cycle.append(current)
            unseen.discard(current)
            options = sorted(adjacency[current] - ({previous} if previous is not None else set()))
            if not options:
                raise ValueError("boundary cycle terminated")
            nxt = options[0]
            previous, current = current, nxt
            if current == seed:
                break
            if current in cycle:
                raise ValueError("boundary cycle self-revisits before closure")
        cycles.append(cycle)
    return cycles


def _triangle_area(a, b, c):
    return 0.5 * _length(_cross(_sub(b, a), _sub(c, a)))


def _topology(mesh):
    vertices = mesh["vertices"]
    triangles = mesh["triangles"]
    components, edge_counts, directed = _triangle_components(triangles)
    boundary_edges = sorted(edge for edge, count in edge_counts.items() if count == 1)
    nonmanifold_edges = sorted(edge for edge, count in edge_counts.items() if count > 2)
    winding_conflicts = []
    for edge, owners in directed.items():
        if len(owners) != 2:
            continue
        left = owners[0][:2]
        right = owners[1][:2]
        if left != (right[1], right[0]):
            winding_conflicts.append(edge)
    degenerate = sum(
        1
        for a, b, c in triangles
        if _triangle_area(vertices[a], vertices[b], vertices[c]) <= 1e-12
    )
    isolated = sorted(set(range(len(vertices))) - {i for tri in triangles for i in tri})
    cycles = _boundary_cycles(boundary_edges)
    return {
        "vertices": len(vertices),
        "triangles": len(triangles),
        "edges": len(edge_counts),
        "triangle_components": len(components),
        "boundary_edges": len(boundary_edges),
        "nonmanifold_edges": len(nonmanifold_edges),
        "winding_conflicts": len(winding_conflicts),
        "degenerate_triangles": degenerate,
        "isolated_vertices": len(isolated),
        "euler_characteristic": len(vertices) - len(edge_counts) + len(triangles),
        "boundary_cycles": len(cycles),
        "boundary_cycle_lengths": sorted(len(cycle) for cycle in cycles),
        "boundary_edge_list": boundary_edges,
        "boundary_cycles_vertices": cycles,
    }


def evaluate(
    source: dict,
    *,
    requested_geometry_predecessor_head: str = GEOMETRY_PREDECESSOR_HEAD,
    requested_rigging_owner_head: str = RIGGING_OWNER_HEAD,
    requested_organic_owner_head: str = ORGANIC_TRANSITION_OWNER_HEAD,
    requested_procedural_owner_head: str = PROCEDURAL_TRANSITION_OWNER_HEAD,
    requested_transition_u: float = TRANSITION_U,
    requested_transition_length_m: float = TRANSITION_LENGTH_M,
    claim_trunk_opening_proven: bool = False,
    claim_connected_branch_trunk_junction: bool = False,
    claim_source_adoption: bool = False,
    claim_rigging_rebind: bool = False,
    claim_target_host_or_runtime: bool = False,
) -> dict:
    validate_source(source)
    if source.get("study_id") != STUDY_ID or digest(source) != SOURCE_DIGEST:
        raise ValueError("exact Nature source identity drift")
    if requested_geometry_predecessor_head != GEOMETRY_PREDECESSOR_HEAD:
        raise ValueError("exact Geometry predecessor drift")
    if requested_rigging_owner_head != RIGGING_OWNER_HEAD:
        raise ValueError("exact current Rigging owner drift")
    if requested_organic_owner_head != ORGANIC_TRANSITION_OWNER_HEAD:
        raise ValueError("exact Organic transition owner drift")
    if requested_procedural_owner_head != PROCEDURAL_TRANSITION_OWNER_HEAD:
        raise ValueError("exact Procedural transition owner drift")
    if abs(float(requested_transition_u) - TRANSITION_U) > TOL:
        raise ValueError("north-low owner transition parameter drift")
    if abs(float(requested_transition_length_m) - TRANSITION_LENGTH_M) > TOL:
        raise ValueError("north-low owner transition length drift")
    if claim_trunk_opening_proven:
        raise ValueError("branch-side open ring does not prove a trunk opening")
    if claim_connected_branch_trunk_junction:
        raise ValueError("branch-side open ring does not prove a connected junction")
    if claim_source_adoption:
        raise ValueError("diagnostic topology candidate cannot adopt source geometry")
    if claim_rigging_rebind:
        raise ValueError("Geometry candidate cannot claim Rigging rebind")
    if claim_target_host_or_runtime:
        raise ValueError("Geometry candidate cannot claim target-host or Runtime acceptance")

    old_attachment = attachment.evaluate(source)
    if old_attachment["result"] != attachment.RESULT:
        raise ValueError("historical Geometry attachment classification no longer passes")
    rig_report = rigging.evaluate(source, rigging.expected_geometry_contract())
    if rig_report["result"] != rigging.RESULT:
        raise ValueError("current detached Rigging owner no longer passes")
    if rig_report["attachment_representation_constraint"]["mode"] != "DETACHED_DIAGNOSTIC_CHILD_SOCKET_ONLY":
        raise ValueError("current Rigging attachment mode drift")

    branch = _branch(source)
    p0 = [float(value) for value in branch["points"][0]]
    p1 = [float(value) for value in branch["points"][1]]
    r0 = float(branch["radii"][0])
    r1 = float(branch["radii"][1])
    segment_length = _length(_sub(p1, p0))
    if abs(segment_length * TRANSITION_U - TRANSITION_LENGTH_M) > TOL:
        raise ValueError("owner normalized and metric transition handoffs disagree")

    _, u_axis, v_axis = _frame(p0, p1)
    baseline_start = _ring(p0, r0, u_axis, v_axis)
    baseline_end = _ring(p1, r1, u_axis, v_axis)
    expected_cut_vertices = [
        _lerp(baseline_start[index], baseline_end[index], TRANSITION_U)
        for index in range(SIDES)
    ]

    candidate = build_open_transition_stub(source)
    topology = _topology(candidate)
    cut_indices = set(candidate["transition_ring_vertex_indices"])
    expected_boundary_edges = {
        tuple(sorted((index, (index + 1) % SIDES)))
        for index in range(SIDES)
    }
    actual_boundary_edges = set(topology["boundary_edge_list"])

    max_edge_split_residual = max(
        _length(_sub(candidate["vertices"][index], expected_cut_vertices[index]))
        for index in range(SIDES)
    )
    cut_center = candidate["transition_center_m"]
    max_radius_residual = max(
        abs(_length(_sub(candidate["vertices"][index], cut_center)) - candidate["transition_radius_m"])
        for index in range(SIDES)
    )
    mean_center = [
        sum(float(candidate["vertices"][index][axis]) for index in range(SIDES)) / SIDES
        for axis in range(3)
    ]
    center_residual = _length(_sub(mean_center, cut_center))
    min_boundary_edge_length = min(
        _length(_sub(candidate["vertices"][left], candidate["vertices"][right]))
        for left, right in topology["boundary_edge_list"]
    )

    checks = {
        "historical_detached_topology_reexecuted": old_attachment["result"] == attachment.RESULT,
        "current_rigging_detached_attachment_reexecuted": rig_report["result"] == rigging.RESULT,
        "owner_transition_normalized_and_metric_values_agree": abs(segment_length * TRANSITION_U - TRANSITION_LENGTH_M) <= TOL,
        "candidate_is_one_connected_triangle_component": topology["triangle_components"] == 1,
        "candidate_has_expected_17_vertices": topology["vertices"] == 17,
        "candidate_has_expected_24_triangles": topology["triangles"] == 24,
        "candidate_has_no_nonmanifold_edges": topology["nonmanifold_edges"] == 0,
        "candidate_has_no_winding_conflicts": topology["winding_conflicts"] == 0,
        "candidate_has_no_degenerate_triangles": topology["degenerate_triangles"] == 0,
        "candidate_has_no_isolated_vertices": topology["isolated_vertices"] == 0,
        "candidate_is_disk_like_chi_one": topology["euler_characteristic"] == 1,
        "candidate_has_exactly_one_boundary_cycle": topology["boundary_cycles"] == 1,
        "candidate_boundary_cycle_has_eight_edges": topology["boundary_cycle_lengths"] == [SIDES],
        "candidate_boundary_is_exact_transition_ring": actual_boundary_edges == expected_boundary_edges,
        "candidate_boundary_only_uses_transition_vertices": all(left in cut_indices and right in cut_indices for left, right in actual_boundary_edges),
        "transition_ring_is_exact_longitudinal_edge_split": max_edge_split_residual <= GEOMETRY_TOL,
        "transition_ring_center_is_preserved": center_residual <= GEOMETRY_TOL,
        "transition_ring_radius_is_preserved": max_radius_residual <= GEOMETRY_TOL,
        "transition_boundary_has_positive_edge_lengths": min_boundary_edge_length > GEOMETRY_TOL,
    }
    if not all(checks.values()):
        raise ValueError(f"north-low owner-transition open-ring invariant failed: {checks}")

    return {
        "schema": SCHEMA,
        "result": RESULT,
        "study_id": STUDY_ID,
        "branch_id": BRANCH_ID,
        "lineage": {
            "geometry_predecessor_head": GEOMETRY_PREDECESSOR_HEAD,
            "rigging_owner_head": RIGGING_OWNER_HEAD,
            "organic_transition_owner_head": ORGANIC_TRANSITION_OWNER_HEAD,
            "organic_transition_observer_blob": ORGANIC_TRANSITION_OBSERVER_BLOB,
            "procedural_transition_owner_head": PROCEDURAL_TRANSITION_OWNER_HEAD,
            "procedural_transition_contract_blob": PROCEDURAL_TRANSITION_CONTRACT_BLOB,
            "procedural_family_digest": PROCEDURAL_FAMILY_DIGEST,
            "source_digest": SOURCE_DIGEST,
        },
        "owner_transition": {
            "parameter_u": TRANSITION_U,
            "length_along_first_segment_m": TRANSITION_LENGTH_M,
            "first_segment_length_m": segment_length,
            "transition_center_m": candidate["transition_center_m"],
            "transition_radius_m": candidate["transition_radius_m"],
        },
        "candidate_topology": topology,
        "candidate_geometry": {
            "maximum_transition_ring_edge_split_residual_m": max_edge_split_residual,
            "transition_ring_center_residual_m": center_residual,
            "maximum_transition_ring_radius_residual_m": max_radius_residual,
            "minimum_transition_boundary_edge_length_m": min_boundary_edge_length,
            "vertices": candidate["vertices"],
            "triangles": candidate["triangles"],
        },
        "reusable_pattern": {
            "name": "OWNER_TRANSITION_OPEN_BOUNDARY_RING",
            "rule": "OWNER_TRANSITION_EXIT_MAY_SEED_A_BRANCH_SIDE_OPEN_BOUNDARY_RING_ONLY_AFTER_TOPOLOGY_PRESERVING_LONGITUDINAL_EDGE_SPLIT__TRUNK_OPENING_BRIDGE_AND_CONNECTED_JUNCTION_REMAIN_SEPARATE_GEOMETRY_GATES",
            "future_consumer_boundary": "one simple branch-side boundary loop only; no matching trunk loop or bridge exists yet",
        },
        "checks": checks,
        "truth_boundary": {
            "source_geometry_mutated": False,
            "current_generated_receiver_mutated": False,
            "rigging_mutated_or_rebound": False,
            "organic_transition_recomputed_or_reauthored": False,
            "procedural_family_reauthored": False,
            "trunk_opening_generated_or_proven": False,
            "branch_trunk_bridge_generated_or_proven": False,
            "connected_branch_trunk_topology_proven": False,
            "production_topology_adopted": False,
            "skinning_or_deformation_acceptance_claimed": False,
            "target_host_or_runtime_acceptance_claimed": False,
            "collision_or_gameplay_suitability_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }

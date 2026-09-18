"""Rebind the north-low analytic trunk loop to the exact indexed trunk surface.

The predecessor Geometry lane proved an eight-vertex branch-side open ring and an
analytic tapered-trunk loop/bridge.  This bounded successor answers a narrower but
necessary question before any real cut: where do those eight intended opening
vertices land on the *actual generated ten-sided indexed trunk shell*?

No source/default mesh is mutated.  The result is a diagnostic indexed-surface loop
and bridge candidate plus exact source-triangle membership.  Cutting, welding,
continuous deformation clearance and downstream acceptance remain separate gates.
"""
from __future__ import annotations

import math

from .organic_form import build_mesh, digest, validate_source
from . import rear_tree_geometry_north_low_transition_open_ring as open_ring
from . import rear_tree_geometry_north_low_trunk_bridge_candidate as analytic_bridge

SCHEMA = "axm.nature-north-low-indexed-surface-rebind-geometry-evidence/v0.1"
RESULT = "PASS_NORTH_LOW_EXACT_INDEXED_TRUNK_SURFACE_REBIND__HOLD_INDEXED_CUT_CONNECTED_JUNCTION"
RULE = "ANALYTIC_ENVELOPE_HANDOFF_REQUIRES_EXACT_INDEXED_SURFACE_REPROJECTION_BEFORE_CUT_CONNECTIVITY"
STUDY_ID = analytic_bridge.STUDY_ID
SOURCE_DIGEST = analytic_bridge.SOURCE_DIGEST
BRANCH_ID = analytic_bridge.BRANCH_ID
SIDES = analytic_bridge.SIDES
TRUNK_SIDES = 10
ANALYTIC_GEOMETRY_DONOR_HEAD = "14d05fdabc943376c231308001d00eb87dc23430"
ANALYTIC_GEOMETRY_MODULE_BLOB = "47ba57110f43b0f3f1f29582b46a90505fa4515c"
RIGGING_OWNER_HEAD = "efe99261459858636dbe65b16cbe1d5ad2b93a56"
TOL = 1e-10


def _add(a, b):
    return [float(a[i]) + float(b[i]) for i in range(3)]


def _sub(a, b):
    return [float(a[i]) - float(b[i]) for i in range(3)]


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
    size = _length(v)
    if size <= 1e-18:
        raise ValueError("zero-length vector")
    return [float(value) / size for value in v]


def _distance(a, b):
    return _length(_sub(a, b))


def _frame(a, b):
    axis = _norm(_sub(b, a))
    ref = [0.0, 0.0, 1.0]
    if abs(_dot(axis, ref)) > 0.94:
        ref = [1.0, 0.0, 0.0]
    u = _norm(_cross(axis, ref))
    v = _norm(_cross(axis, u))
    return axis, u, v


def _cross2(a, b):
    return float(a[0]) * float(b[1]) - float(a[1]) * float(b[0])


def _triangle_area(a, b, c):
    return 0.5 * _length(_cross(_sub(b, a), _sub(c, a)))


def _trunk_segment(source: dict, segment_id: str):
    trunk = source["trunk"]
    matches = []
    for index in range(len(trunk) - 1):
        start = trunk[index]
        end = trunk[index + 1]
        if f"{start['id']}->{end['id']}" == segment_id:
            matches.append((start, end))
    if len(matches) != 1:
        raise ValueError("exact trunk segment missing or duplicated")
    return matches[0]


def _region(mesh: dict, region_id: str):
    matches = [row for row in mesh["regions"] if row.get("id") == region_id]
    if len(matches) != 1:
        raise ValueError("exact indexed trunk region missing or duplicated")
    return matches[0]


def _barycentric(point, a, b, c):
    v0 = _sub(b, a)
    v1 = _sub(c, a)
    v2 = _sub(point, a)
    d00 = _dot(v0, v0)
    d01 = _dot(v0, v1)
    d11 = _dot(v1, v1)
    d20 = _dot(v2, v0)
    d21 = _dot(v2, v1)
    denom = d00 * d11 - d01 * d01
    if abs(denom) <= 1e-20:
        raise ValueError("degenerate indexed receiver triangle")
    vb = (d11 * d20 - d01 * d21) / denom
    vc = (d00 * d21 - d01 * d20) / denom
    va = 1.0 - vb - vc
    normal = _cross(v0, v1)
    plane_residual = abs(_dot(v2, _norm(normal)))
    return [va, vb, vc], plane_residual


def _indexed_surface_projection(vertex, start: dict, end: dict) -> dict:
    start_pos = [float(value) for value in start["position"]]
    end_pos = [float(value) for value in end["position"]]
    axis, u_axis, v_axis = _frame(start_pos, end_pos)
    delta = _sub(end_pos, start_pos)
    length = _length(delta)
    axial = _dot(_sub(vertex, start_pos), axis)
    segment_t = axial / length
    if segment_t < -TOL or segment_t > 1.0 + TOL:
        raise ValueError("branch-ring vertex leaves exact trunk segment")
    segment_t = min(1.0, max(0.0, segment_t))
    center = _add(start_pos, _mul(axis, segment_t * length))
    radius = float(start["radius"]) + segment_t * (float(end["radius"]) - float(start["radius"]))
    radial = _sub(vertex, center)
    x = _dot(radial, u_axis)
    y = _dot(radial, v_axis)
    theta = math.atan2(y, x)
    theta_tau = theta % math.tau
    step = math.tau / TRUNK_SIDES
    cell = int(math.floor(theta_tau / step)) % TRUNK_SIDES
    a_angle = cell * step
    b_angle = (cell + 1) * step
    ray = [math.cos(theta_tau), math.sin(theta_tau)]
    edge_a = [radius * math.cos(a_angle), radius * math.sin(a_angle)]
    edge_b = [radius * math.cos(b_angle), radius * math.sin(b_angle)]
    edge = [edge_b[0] - edge_a[0], edge_b[1] - edge_a[1]]
    denom = _cross2(ray, edge)
    if abs(denom) <= 1e-14:
        raise ValueError("radial ray parallel to indexed trunk side")
    radial_distance = _cross2(edge_a, edge) / denom
    edge_lambda = _cross2(edge_a, ray) / denom
    if radial_distance <= 0.0 or edge_lambda < -TOL or edge_lambda > 1.0 + TOL:
        raise ValueError("indexed trunk side intersection lies outside exact face")
    point = _add(
        center,
        _add(
            _mul(u_axis, radial_distance * math.cos(theta_tau)),
            _mul(v_axis, radial_distance * math.sin(theta_tau)),
        ),
    )
    return {
        "segment_t": segment_t,
        "theta_rad": theta,
        "side_cell": cell,
        "side_edge_lambda": edge_lambda,
        "local_radius_m": radius,
        "indexed_radial_distance_m": radial_distance,
        "surface_point_m": point,
    }


def _proper_segments_intersect(a, b, c, d):
    def orient(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    o1 = orient(a, b, c)
    o2 = orient(a, b, d)
    o3 = orient(c, d, a)
    o4 = orient(c, d, b)
    return o1 * o2 < -1e-14 and o3 * o4 < -1e-14


def _loop_self_intersections(parameter_points):
    count = 0
    size = len(parameter_points)
    for left in range(size):
        a = parameter_points[left]
        b = parameter_points[(left + 1) % size]
        for right in range(left + 1, size):
            if right == left or (right + 1) % size == left or (left + 1) % size == right:
                continue
            c = parameter_points[right]
            d = parameter_points[(right + 1) % size]
            if _proper_segments_intersect(a, b, c, d):
                count += 1
    return count


def build_candidate(source: dict) -> dict:
    predecessor = analytic_bridge.build_candidate(source)
    stub = predecessor["branch_stub"]
    frame = predecessor["organic_exit_frame"]
    start, end = _trunk_segment(source, frame["nearest_trunk_segment"])
    branch_ring_indices = list(stub["transition_ring_vertex_indices"])
    branch_ring = [list(stub["vertices"][index]) for index in branch_ring_indices]
    indexed_samples = [_indexed_surface_projection(vertex, start, end) for vertex in branch_ring]
    indexed_ring = [row["surface_point_m"] for row in indexed_samples]

    vertices = [list(value) for value in stub["vertices"]] + [list(value) for value in indexed_ring]
    triangles = [list(face) for face in stub["triangles"]]
    trunk_base = len(stub["vertices"])
    for index in range(SIDES):
        nxt = (index + 1) % SIDES
        triangles.extend([
            [branch_ring_indices[index], branch_ring_indices[nxt], trunk_base + nxt],
            [branch_ring_indices[index], trunk_base + nxt, trunk_base + index],
        ])

    bridge_vertices = branch_ring + indexed_ring
    bridge_triangles = []
    for index in range(SIDES):
        nxt = (index + 1) % SIDES
        bridge_triangles.extend([
            [index, nxt, SIDES + nxt],
            [index, SIDES + nxt, SIDES + index],
        ])
    return {
        "branch_stub": stub,
        "analytic_predecessor": predecessor,
        "indexed_samples": indexed_samples,
        "indexed_ring": indexed_ring,
        "vertices": vertices,
        "triangles": triangles,
        "bridge_only": {"vertices": bridge_vertices, "triangles": bridge_triangles},
    }


def evaluate(
    source: dict,
    *,
    requested_analytic_geometry_donor_head: str = ANALYTIC_GEOMETRY_DONOR_HEAD,
    requested_analytic_geometry_module_blob: str = ANALYTIC_GEOMETRY_MODULE_BLOB,
    requested_rigging_owner_head: str = RIGGING_OWNER_HEAD,
    claim_indexed_trunk_cut_integrated: bool = False,
    claim_connected_branch_trunk_junction: bool = False,
    claim_continuous_deformation_clearance: bool = False,
    claim_rigging_transfer: bool = False,
    claim_target_host_or_runtime: bool = False,
) -> dict:
    validate_source(source)
    if source.get("study_id") != STUDY_ID or digest(source) != SOURCE_DIGEST:
        raise ValueError("exact Nature source identity drift")
    if requested_analytic_geometry_donor_head != ANALYTIC_GEOMETRY_DONOR_HEAD:
        raise ValueError("analytic Geometry donor drift")
    if requested_analytic_geometry_module_blob != ANALYTIC_GEOMETRY_MODULE_BLOB:
        raise ValueError("analytic Geometry module blob drift")
    if requested_rigging_owner_head != RIGGING_OWNER_HEAD:
        raise ValueError("current Rigging owner drift")
    if claim_indexed_trunk_cut_integrated:
        raise ValueError("indexed-surface rebind does not cut the trunk")
    if claim_connected_branch_trunk_junction:
        raise ValueError("indexed-surface rebind does not prove connected topology")
    if claim_continuous_deformation_clearance:
        raise ValueError("static indexed-surface rebind does not prove continuous clearance")
    if claim_rigging_transfer:
        raise ValueError("analytic Rigging evidence does not transfer automatically")
    if claim_target_host_or_runtime:
        raise ValueError("Geometry cannot claim target-host or Runtime acceptance")

    predecessor_report = analytic_bridge.evaluate(source)
    if predecessor_report.get("result") != analytic_bridge.RESULT:
        raise ValueError("analytic Geometry predecessor no longer passes")

    candidate = build_candidate(source)
    predecessor = candidate["analytic_predecessor"]
    stub = candidate["branch_stub"]
    indexed_samples = candidate["indexed_samples"]
    indexed_ring = candidate["indexed_ring"]
    analytic_ring = [
        predecessor["vertices"][index]
        for index in predecessor["trunk_ring_vertex_indices"]
    ]

    mesh = build_mesh(source)
    region_id = f"trunk:{predecessor['trunk_segment_id']}"
    region = _region(mesh, region_id)
    memberships = []
    max_plane_residual = 0.0
    minimum_barycentric = 1.0
    for sample, point in zip(indexed_samples, indexed_ring):
        cell = int(sample["side_cell"])
        candidates = [int(region["triangle_start"]) + 4 * cell, int(region["triangle_start"]) + 4 * cell + 1]
        accepted = []
        for triangle_index in candidates:
            triangle = mesh["triangles"][triangle_index]
            bary, residual = _barycentric(
                point,
                mesh["vertices"][triangle[0]],
                mesh["vertices"][triangle[1]],
                mesh["vertices"][triangle[2]],
            )
            if residual <= TOL and min(bary) >= -TOL and max(bary) <= 1.0 + TOL:
                accepted.append((triangle_index, bary, residual))
        if len(accepted) != 1:
            raise ValueError("indexed loop point does not resolve to exactly one source triangle")
        triangle_index, bary, residual = accepted[0]
        max_plane_residual = max(max_plane_residual, residual)
        minimum_barycentric = min(minimum_barycentric, min(bary))
        memberships.append({
            "side_cell": cell,
            "triangle_index": triangle_index,
            "barycentric": bary,
            "plane_residual_m": residual,
        })

    parameter_points = [(float(row["theta_rad"]), float(row["segment_t"])) for row in indexed_samples]
    if _loop_self_intersections(parameter_points) != 0:
        raise ValueError("indexed-surface opening loop self-intersects in trunk parameter space")

    combined_topology = open_ring._topology({"vertices": candidate["vertices"], "triangles": candidate["triangles"]})
    bridge_topology = open_ring._topology(candidate["bridge_only"])
    expected_combined = {
        "vertices": 25,
        "triangles": 40,
        "edges": 64,
        "triangle_components": 1,
        "boundary_edges": 8,
        "nonmanifold_edges": 0,
        "winding_conflicts": 0,
        "degenerate_triangles": 0,
        "isolated_vertices": 0,
        "euler_characteristic": 1,
        "boundary_cycles": 1,
        "boundary_cycle_lengths": [8],
    }
    expected_bridge = {
        "vertices": 16,
        "triangles": 16,
        "edges": 32,
        "triangle_components": 1,
        "boundary_edges": 16,
        "nonmanifold_edges": 0,
        "winding_conflicts": 0,
        "degenerate_triangles": 0,
        "isolated_vertices": 0,
        "euler_characteristic": 0,
        "boundary_cycles": 2,
        "boundary_cycle_lengths": [8, 8],
    }
    for key, expected in expected_combined.items():
        if combined_topology[key] != expected:
            raise ValueError(f"combined indexed-surface bridge topology drift for {key}")
    for key, expected in expected_bridge.items():
        if bridge_topology[key] != expected:
            raise ValueError(f"indexed-surface bridge annulus topology drift for {key}")

    analytic_deltas = [_distance(a, b) for a, b in zip(analytic_ring, indexed_ring)]
    bridge_spans = [
        _distance(stub["vertices"][index], indexed_ring[index])
        for index in stub["transition_ring_vertex_indices"]
    ]
    bridge_areas = [
        _triangle_area(candidate["vertices"][a], candidate["vertices"][b], candidate["vertices"][c])
        for a, b, c in candidate["triangles"][-2 * SIDES:]
    ]
    if min(bridge_spans) <= TOL or min(bridge_areas) <= TOL:
        raise ValueError("indexed-surface bridge candidate collapses at neutral pose")
    touched_cells = sorted({int(row["side_cell"]) for row in indexed_samples})
    if touched_cells != [0, 1, 2, 9]:
        raise ValueError(f"unexpected indexed trunk face-cell footprint: {touched_cells!r}")

    return {
        "schema": SCHEMA,
        "result": RESULT,
        "reusable_geometry_rule": RULE,
        "study_id": STUDY_ID,
        "source_digest": SOURCE_DIGEST,
        "provenance": {
            "analytic_geometry_donor_head": ANALYTIC_GEOMETRY_DONOR_HEAD,
            "analytic_geometry_module_blob": ANALYTIC_GEOMETRY_MODULE_BLOB,
            "rigging_owner_head": RIGGING_OWNER_HEAD,
            "analytic_predecessor_result": analytic_bridge.RESULT,
        },
        "indexed_surface_binding": {
            "trunk_region_id": region_id,
            "generated_region_triangle_start": region["triangle_start"],
            "generated_region_triangle_count": region["triangle_count"],
            "loop_vertices": SIDES,
            "touched_side_cells": touched_cells,
            "touched_source_triangle_indices": sorted({row["triangle_index"] for row in memberships}),
            "memberships": memberships,
            "maximum_triangle_plane_residual_m": max_plane_residual,
            "minimum_barycentric_coordinate": minimum_barycentric,
            "parameter_space_self_intersections": 0,
        },
        "analytic_to_indexed_surface_rebind": {
            "maximum_surface_delta_m": max(analytic_deltas),
            "minimum_surface_delta_m": min(analytic_deltas),
            "analytic_minimum_bridge_span_m": predecessor_report["analytic_trunk_loop"]["minimum_bridge_span_m"],
            "indexed_surface_minimum_bridge_span_m": min(bridge_spans),
            "indexed_surface_maximum_bridge_span_m": max(bridge_spans),
            "minimum_neutral_bridge_triangle_area_m2": min(bridge_areas),
        },
        "bridge_patch_topology": bridge_topology,
        "combined_candidate_topology": combined_topology,
        "truth_boundary": {
            "source_or_default_mesh_mutated": False,
            "indexed_trunk_cut_integrated": False,
            "connected_branch_trunk_indexed_topology_proven": False,
            "neutral_indexed_surface_membership_proven": True,
            "continuous_deformation_clearance_proven": False,
            "analytic_rigging_pass_transferred": False,
            "target_host_or_runtime_accepted": False,
            "game_ready_or_mastery_claimed": False,
        },
    }

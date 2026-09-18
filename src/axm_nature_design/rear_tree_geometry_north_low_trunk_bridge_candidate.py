"""Geometry-owned analytic trunk-surface loop and bridge candidate for north-low.

This bounded successor consumes the exact Organic transition exit frame and the prior
Geometry branch-side open ring.  It projects that existing eight-vertex branch ring
outward onto the authored tapered trunk *analytic envelope* at matching local axial
coordinates, then builds a one-to-one annular bridge patch between the two loops.

It deliberately does not cut or mutate the indexed trunk mesh.  Therefore this module
can prove loop/bridge compatibility without claiming a welded branch/trunk junction,
production skinning, target-host transport, or source adoption.
"""
from __future__ import annotations

import math

from .organic_form import digest, validate_source
from . import rear_tree_geometry_north_low_transition_open_ring as open_ring
from . import rear_tree_transition_exit_frames as exit_frames

SCHEMA = "axm.nature-north-low-analytic-trunk-bridge-geometry-evidence/v0.1"
RESULT = "PASS_NORTH_LOW_ANALYTIC_TRUNK_SURFACE_LOOP_AND_BRIDGE_PATCH__HOLD_INDEXED_TRUNK_CUT_CONNECTED_JUNCTION"
RULE = "ANALYTIC_TRUNK_ENVELOPE_PROJECTION_CAN_DEFINE_MATCHED_BOUNDARY_LOOP_AND_BRIDGE_PATCH__INDEXED_TRUNK_CUT_AND_CONNECTED_JUNCTION_REMAIN_SEPARATE_GATES"
STUDY_ID = open_ring.STUDY_ID
SOURCE_DIGEST = open_ring.SOURCE_DIGEST
BRANCH_ID = open_ring.BRANCH_ID
SIDES = open_ring.SIDES
GEOMETRY_PREDECESSOR_HEAD = "a7164ce18e309c3cd548c89380639bdfa2b46ebf"
ORGANIC_EXIT_FRAME_OWNER_HEAD = "7f3b937b440e9870d07f7c356c5a3cbb779d0cd7"
ORGANIC_EXIT_FRAME_BLOB = "406c169963c34aed394e269f0dff2c91bb035cb8"
RIGGING_OWNER_HEAD = open_ring.RIGGING_OWNER_HEAD
TOL = 1e-10


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
    size = _length(v)
    if size <= 1e-18:
        raise ValueError("zero-length vector")
    return [float(value) / size for value in v]


def _triangle_area(a, b, c):
    return 0.5 * _length(_cross(_sub(b, a), _sub(c, a)))


def _distance(a, b):
    return _length(_sub(a, b))


def _north_low_exit_frame(source: dict) -> tuple[dict, dict]:
    report = exit_frames.evaluate(source)
    if report.get("state") != "PASS_EXACT_NEUTRAL_BRANCH_TRANSITION_EXIT_FRAMES__CONNECTED_TOPOLOGY_HELD":
        raise ValueError("exact Organic exit-frame handoff no longer passes")
    matches = [row for row in report["frames"] if row.get("branch_id") == BRANCH_ID]
    if len(matches) != 1:
        raise ValueError("north-low exit frame missing or duplicated")
    return report, matches[0]


def _trunk_segment(source: dict, segment_id: str) -> tuple[dict, dict]:
    trunk = source.get("trunk", [])
    matches = []
    for index in range(len(trunk) - 1):
        start = trunk[index]
        end = trunk[index + 1]
        if f"{start.get('id')}->{end.get('id')}" == segment_id:
            matches.append((start, end))
    if len(matches) != 1:
        raise ValueError(f"expected exactly one trunk segment {segment_id}")
    return matches[0]


def _project_ring_vertex_to_tapered_trunk(vertex, start: dict, end: dict) -> dict:
    start_pos = [float(v) for v in start["position"]]
    end_pos = [float(v) for v in end["position"]]
    axis_delta = _sub(end_pos, start_pos)
    segment_length = _length(axis_delta)
    if segment_length <= 1e-18:
        raise ValueError("zero-length trunk segment")
    axis = _norm(axis_delta)
    axial_distance = _dot(_sub(vertex, start_pos), axis)
    segment_t = axial_distance / segment_length
    if segment_t < -TOL or segment_t > 1.0 + TOL:
        raise ValueError("branch-ring vertex projects outside exact local trunk segment")
    segment_t = max(0.0, min(1.0, segment_t))
    center = _add(start_pos, _mul(axis, segment_t * segment_length))
    local_radius = float(start["radius"]) + segment_t * (float(end["radius"]) - float(start["radius"]))
    radial = _sub(vertex, center)
    radial_length = _length(radial)
    if radial_length <= 1e-18:
        raise ValueError("branch-ring vertex lies on trunk centerline")
    surface = _add(center, _mul(_norm(radial), local_radius))
    surface_residual = abs(_distance(surface, center) - local_radius)
    return {
        "segment_t": segment_t,
        "centerline_point_m": center,
        "local_radius_m": local_radius,
        "input_radial_distance_m": radial_length,
        "surface_point_m": surface,
        "surface_residual_m": surface_residual,
        "bridge_span_m": _distance(vertex, surface),
    }


def build_candidate(source: dict) -> dict:
    """Return diagnostic branch stub + analytic trunk loop + annular bridge patch."""
    stub = open_ring.build_open_transition_stub(source)
    _, frame = _north_low_exit_frame(source)
    start, end = _trunk_segment(source, frame["nearest_trunk_segment"])

    branch_ring_indices = list(stub["transition_ring_vertex_indices"])
    branch_ring = [list(stub["vertices"][index]) for index in branch_ring_indices]
    projections = [_project_ring_vertex_to_tapered_trunk(vertex, start, end) for vertex in branch_ring]
    trunk_ring = [row["surface_point_m"] for row in projections]

    vertices = [list(v) for v in stub["vertices"]] + [list(v) for v in trunk_ring]
    triangles = [list(face) for face in stub["triangles"]]
    trunk_base = len(stub["vertices"])
    for index in range(SIDES):
        nxt = (index + 1) % SIDES
        branch_a = branch_ring_indices[index]
        branch_b = branch_ring_indices[nxt]
        trunk_a = trunk_base + index
        trunk_b = trunk_base + nxt
        # The predecessor stub uses the branch boundary edge in the opposite direction.
        # This orientation therefore closes that edge manifoldly while leaving the
        # analytic trunk loop as the one remaining open boundary.
        triangles.extend(
            [
                [branch_a, branch_b, trunk_b],
                [branch_a, trunk_b, trunk_a],
            ]
        )

    bridge_only_vertices = branch_ring + trunk_ring
    bridge_only_triangles = []
    for index in range(SIDES):
        nxt = (index + 1) % SIDES
        bridge_only_triangles.extend(
            [
                [index, nxt, SIDES + nxt],
                [index, SIDES + nxt, SIDES + index],
            ]
        )

    return {
        "schema": "axm.nature-north-low-analytic-trunk-bridge-candidate/v0.1",
        "branch_id": BRANCH_ID,
        "branch_stub": stub,
        "organic_exit_frame": frame,
        "trunk_segment_id": frame["nearest_trunk_segment"],
        "trunk_projection_samples": projections,
        "trunk_ring_vertex_indices": list(range(trunk_base, trunk_base + SIDES)),
        "vertices": vertices,
        "triangles": triangles,
        "bridge_only": {
            "vertices": bridge_only_vertices,
            "triangles": bridge_only_triangles,
        },
    }


def evaluate(
    source: dict,
    *,
    requested_geometry_predecessor_head: str = GEOMETRY_PREDECESSOR_HEAD,
    requested_organic_exit_frame_owner_head: str = ORGANIC_EXIT_FRAME_OWNER_HEAD,
    requested_organic_exit_frame_blob: str = ORGANIC_EXIT_FRAME_BLOB,
    requested_rigging_owner_head: str = RIGGING_OWNER_HEAD,
    claim_indexed_trunk_cut_integrated: bool = False,
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
    if requested_organic_exit_frame_owner_head != ORGANIC_EXIT_FRAME_OWNER_HEAD:
        raise ValueError("exact Organic exit-frame owner drift")
    if requested_organic_exit_frame_blob != ORGANIC_EXIT_FRAME_BLOB:
        raise ValueError("exact Organic exit-frame observer blob drift")
    if requested_rigging_owner_head != RIGGING_OWNER_HEAD:
        raise ValueError("exact detached Rigging owner drift")
    if claim_indexed_trunk_cut_integrated:
        raise ValueError("analytic trunk loop is not an indexed trunk cut")
    if claim_connected_branch_trunk_junction:
        raise ValueError("analytic bridge patch does not prove connected branch/trunk topology")
    if claim_source_adoption:
        raise ValueError("diagnostic bridge candidate cannot adopt source geometry")
    if claim_rigging_rebind:
        raise ValueError("Geometry cannot claim Rigging rebind")
    if claim_target_host_or_runtime:
        raise ValueError("Geometry cannot claim target-host or Runtime acceptance")

    predecessor = open_ring.evaluate(source)
    if predecessor.get("result") != open_ring.RESULT:
        raise ValueError("predecessor open-ring evidence no longer passes")

    candidate = build_candidate(source)
    frame = candidate["organic_exit_frame"]
    stub = candidate["branch_stub"]

    center_delta = _distance(stub["transition_center_m"], frame["exit_center_m"])
    radius_delta = abs(float(stub["transition_radius_m"]) - float(frame["exit_branch_radius_m"]))
    branch = [row for row in source["branches"] if row.get("id") == BRANCH_ID][0]
    branch_axis = _norm(_sub(branch["points"][1], branch["points"][0]))
    frame_axis_delta = _distance(branch_axis, frame["branch_first_segment_tangent_unit"])
    support_residual = abs(
        float(frame["exit_local_trunk_radius_m"])
        - float(frame["exit_centerline_distance_m"])
        - float(frame["exit_branch_radius_m"])
    )
    if max(center_delta, radius_delta, frame_axis_delta, support_residual) > TOL:
        raise ValueError("branch-side open ring and exact Organic exit frame disagree")

    combined_topology = open_ring._topology(
        {"vertices": candidate["vertices"], "triangles": candidate["triangles"]}
    )
    bridge_topology = open_ring._topology(candidate["bridge_only"])

    surface_residuals = [row["surface_residual_m"] for row in candidate["trunk_projection_samples"]]
    bridge_spans = [row["bridge_span_m"] for row in candidate["trunk_projection_samples"]]
    projection_parameters = [row["segment_t"] for row in candidate["trunk_projection_samples"]]
    if min(bridge_spans) <= TOL:
        raise ValueError("analytic trunk projection collapses at least one bridge edge")
    if max(surface_residuals) > TOL:
        raise ValueError("projected trunk loop leaves authored tapered trunk envelope")

    areas = [
        _triangle_area(candidate["vertices"][a], candidate["vertices"][b], candidate["vertices"][c])
        for a, b, c in candidate["triangles"]
    ]
    min_area = min(areas)
    if min_area <= TOL:
        raise ValueError("combined bridge candidate contains degenerate triangle")

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
    for key, expected in expected_combined.items():
        if combined_topology[key] != expected:
            raise ValueError(f"combined bridge topology drift for {key}: {combined_topology[key]!r}")

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
    for key, expected in expected_bridge.items():
        if bridge_topology[key] != expected:
            raise ValueError(f"bridge annulus topology drift for {key}: {bridge_topology[key]!r}")

    return {
        "schema": SCHEMA,
        "result": RESULT,
        "reusable_geometry_rule": RULE,
        "study_id": STUDY_ID,
        "source_digest": SOURCE_DIGEST,
        "provenance": {
            "geometry_predecessor_head": GEOMETRY_PREDECESSOR_HEAD,
            "organic_exit_frame_owner_head": ORGANIC_EXIT_FRAME_OWNER_HEAD,
            "organic_exit_frame_blob": ORGANIC_EXIT_FRAME_BLOB,
            "rigging_owner_head": RIGGING_OWNER_HEAD,
            "predecessor_result": open_ring.RESULT,
        },
        "organic_exit_frame_binding": {
            "branch_id": BRANCH_ID,
            "nearest_trunk_segment": frame["nearest_trunk_segment"],
            "transition_u": frame["transition_u"],
            "exit_center_m": frame["exit_center_m"],
            "exit_branch_radius_m": frame["exit_branch_radius_m"],
            "exit_local_trunk_radius_m": frame["exit_local_trunk_radius_m"],
            "exit_centerline_distance_m": frame["exit_centerline_distance_m"],
            "branch_vs_local_trunk_departure_angle_deg": frame["branch_vs_local_trunk_departure_angle_deg"],
            "open_ring_center_residual_m": center_delta,
            "open_ring_radius_residual_m": radius_delta,
            "branch_axis_residual": frame_axis_delta,
            "neutral_full_radius_support_residual_m": support_residual,
        },
        "analytic_trunk_loop": {
            "vertices": SIDES,
            "minimum_segment_t": min(projection_parameters),
            "maximum_segment_t": max(projection_parameters),
            "maximum_surface_residual_m": max(surface_residuals),
            "minimum_bridge_span_m": min(bridge_spans),
            "maximum_bridge_span_m": max(bridge_spans),
            "indexed_trunk_vertices_or_faces_mutated": False,
            "analytic_envelope_only": True,
        },
        "bridge_patch_topology": bridge_topology,
        "combined_candidate_topology": combined_topology,
        "minimum_combined_triangle_area_m2": min_area,
        "truth_boundary": {
            "predecessor_branch_open_ring_reused": True,
            "exact_organic_exit_frame_consumed": True,
            "analytic_tapered_trunk_envelope_sampled": True,
            "matching_eight_vertex_trunk_surface_loop_constructed": True,
            "one_to_one_annular_bridge_patch_constructed": True,
            "indexed_trunk_mesh_cut_or_mutated": False,
            "connected_branch_trunk_indexed_topology_proven": False,
            "bridge_self_intersection_freedom_proven": False,
            "deformation_or_skinning_proven": False,
            "target_host_or_runtime_proven": False,
            "source_or_default_adopted": False,
            "game_or_production_readiness_claimed": False,
        },
    }

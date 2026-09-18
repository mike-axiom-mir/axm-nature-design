"""Geometry-owned topology/isometry rebind for the Nature upper-trunk -> east-mid hierarchy.

Rigging owns the parent/child frame relation. Geometry only asks whether the exact
existing east-mid child remains the same triangle-closed structural partition under
that new hierarchy. The proof deliberately does not invent trunk deformation,
surface attachment, whole-tree simultaneous motion, or collision acceptance.
"""
from __future__ import annotations

import copy

from . import rear_tree_rigging as rig_math
from . import rear_tree_rigging_primary_branch_family as rig_family
from . import rear_tree_rigging_upper_trunk_east_mid_hierarchy as hierarchy
from .organic_form import build_mesh, digest, validate_source

SCHEMA = "axm.nature-geometry-upper-trunk-east-mid-hierarchy-rebind/v0.1"
RESULT = "PASS_EAST_MID_HIERARCHICAL_REBASE_CHILD_TOPOLOGY_ISOMETRY__HOLD_WHOLE_TREE_CLEARANCE"
RIGGING_OWNER_HEAD = "6cf64925f0ea00737e4d3f2d4f15979c773f309d"
GEOMETRY_PREDECESSOR_HEAD = "f4e8d408480ccb81f559fc56d915e5b4a935851d"
CHILD_BRANCH_ID = hierarchy.CHILD_BRANCH_ID
TOL = rig_family.TOL


def _triangle_area(vertices: list[list[float]], triangle: list[int]) -> float:
    a, b, c = (vertices[int(index)] for index in triangle)
    ab = rig_math._sub(b, a)
    ac = rig_math._sub(c, a)
    return 0.5 * rig_math._length(rig_math._cross(ab, ac))


def _parent_frame(source: dict) -> tuple[list[float], list[float]]:
    trunk = source["trunk"]
    upper_index = next(
        (index for index, row in enumerate(trunk) if row.get("id") == hierarchy.TRUNK_POINT_ID),
        None,
    )
    if upper_index is None or upper_index <= 0 or upper_index >= len(trunk) - 1:
        raise ValueError("upper trunk point no longer has exact incoming/outgoing source segments")
    previous = trunk[upper_index - 1]
    upper = trunk[upper_index]
    following = trunk[upper_index + 1]
    pivot = [float(value) for value in upper["position"]]
    incoming = rig_math._norm(rig_math._sub(pivot, previous["position"]))
    outgoing = rig_math._norm(rig_math._sub(following["position"], pivot))
    axis_raw = rig_math._cross(incoming, outgoing)
    if rig_math._length(axis_raw) <= 1e-9:
        raise ValueError("source-derived parent axis became degenerate")
    return pivot, rig_math._norm(axis_raw)


def _rotate_vector(vector: list[float], axis: list[float], angle_deg: float) -> list[float]:
    return rig_math._rotate_about_axis(vector, [0.0, 0.0, 0.0], axis, angle_deg)


def _pose_selected(
    neutral_vertices: list[list[float]],
    selected_indices: list[int],
    parent_pivot: list[float],
    parent_axis: list[float],
    child_pivot: list[float],
    child_axis: list[float],
    parent_angle_deg: float,
    child_angle_deg: float,
) -> list[list[float]]:
    posed = copy.deepcopy(neutral_vertices)
    transported_pivot = rig_math._rotate_about_axis(
        child_pivot, parent_pivot, parent_axis, parent_angle_deg
    )
    transported_axis = rig_math._norm(_rotate_vector(child_axis, parent_axis, parent_angle_deg))
    for index in selected_indices:
        parented = rig_math._rotate_about_axis(
            neutral_vertices[index], parent_pivot, parent_axis, parent_angle_deg
        )
        posed[index] = rig_math._rotate_about_axis(
            parented, transported_pivot, transported_axis, child_angle_deg
        )
    return posed


def evaluate(
    source: dict,
    *,
    requested_rigging_owner_head: str = RIGGING_OWNER_HEAD,
    claim_predecessor_five_child_clearance_transfer: bool = False,
    claim_trunk_mesh_deformation: bool = False,
    claim_surface_attachment: bool = False,
    claim_collision_or_gameplay: bool = False,
) -> dict:
    validate_source(source)
    if requested_rigging_owner_head != RIGGING_OWNER_HEAD:
        raise ValueError("exact Rigging hierarchy owner head drift")
    if claim_predecessor_five_child_clearance_transfer:
        raise ValueError("predecessor five-child clearance cannot transfer across hierarchy owner change")
    if claim_trunk_mesh_deformation:
        raise ValueError("Rigging hierarchy does not define trunk mesh deformation")
    if claim_surface_attachment:
        raise ValueError("Rigging hierarchy does not prove branch/trunk surface attachment")
    if claim_collision_or_gameplay:
        raise ValueError("Geometry hierarchy rebind cannot claim collision/gameplay acceptance")

    rigging_evidence = hierarchy.evaluate(source)
    if rigging_evidence.get("result") != hierarchy.RESULT:
        raise ValueError("exact Rigging hierarchy prerequisite did not pass")
    certificate = rigging_evidence["continuous_product_domain_certificate"]
    if certificate.get("child_rigidity_preserved_for_every_parent_child_pair") is not True:
        raise ValueError("Rigging hierarchy no longer certifies continuous child rigidity")
    if certificate.get("simultaneous_whole_tree_motion_proven") is not False:
        raise ValueError("Rigging hierarchy authority boundary unexpectedly widened")

    mesh = build_mesh(source)
    mesh_digest = digest(mesh)
    if mesh_digest != rig_family.EXPECTED_MIGRATED_MESH_DIGEST:
        raise ValueError("exact Geometry migrated receiver identity drift")
    neutral_vertices = [[float(value) for value in row] for row in mesh["vertices"]]
    probe = rig_family._probe_branch(source, mesh, CHILD_BRANCH_ID)
    selected_indices = [int(index) for index in probe["selected_vertex_indices"]]
    selected_set = set(selected_indices)

    owned_triangles: list[int] = []
    partial_triangles: list[int] = []
    for triangle_index, triangle in enumerate(mesh["triangles"]):
        face = {int(index) for index in triangle}
        if not (face & selected_set):
            continue
        if face.issubset(selected_set):
            owned_triangles.append(triangle_index)
        else:
            partial_triangles.append(triangle_index)

    if len(selected_indices) != 52:
        raise ValueError("east-mid selected-vertex cardinality drift")
    if len(owned_triangles) != 72 or partial_triangles:
        raise ValueError("east-mid triangle-closed child partition drift")

    neutral_areas = [
        _triangle_area(neutral_vertices, mesh["triangles"][triangle_index])
        for triangle_index in owned_triangles
    ]
    minimum_neutral_area = min(neutral_areas)
    if minimum_neutral_area <= TOL:
        raise ValueError("east-mid neutral child contains a degenerate owned triangle")

    parent_pivot, parent_axis = _parent_frame(source)
    child_pivot = [float(value) for value in probe["joint_pivot_m"]]
    child_axis = [float(value) for value in probe["source_derived_axis"]]
    index_topology_digest = digest(mesh["triangles"])

    witness_rows: list[dict] = []
    maximum_triangle_area_drift = 0.0
    maximum_selected_pairwise_drift = 0.0
    neutral_pairwise = rig_math._pairwise_distances(
        [neutral_vertices[index] for index in selected_indices]
    )
    for parent_angle in hierarchy.PARENT_REPRESENTATIVE_ANGLES_DEG:
        for child_angle in hierarchy.CHILD_REPRESENTATIVE_ANGLES_DEG:
            posed = _pose_selected(
                neutral_vertices,
                selected_indices,
                parent_pivot,
                parent_axis,
                child_pivot,
                child_axis,
                float(parent_angle),
                float(child_angle),
            )
            posed_areas = [
                _triangle_area(posed, mesh["triangles"][triangle_index])
                for triangle_index in owned_triangles
            ]
            area_drift = max(
                (abs(left - right) for left, right in zip(neutral_areas, posed_areas)),
                default=0.0,
            )
            pairwise_drift = rig_math._max_abs_delta(
                neutral_pairwise,
                rig_math._pairwise_distances([posed[index] for index in selected_indices]),
            )
            maximum_triangle_area_drift = max(maximum_triangle_area_drift, area_drift)
            maximum_selected_pairwise_drift = max(maximum_selected_pairwise_drift, pairwise_drift)
            witness_rows.append(
                {
                    "parent_angle_deg": float(parent_angle),
                    "child_angle_deg": float(child_angle),
                    "selected_vertex_count": len(selected_indices),
                    "owned_triangle_count": len(owned_triangles),
                    "index_topology_digest": index_topology_digest,
                    "minimum_owned_triangle_area_m2": min(posed_areas),
                    "maximum_owned_triangle_area_drift_m2": area_drift,
                    "maximum_selected_pairwise_distance_drift_m": pairwise_drift,
                }
            )

    representative_pass = (
        maximum_triangle_area_drift <= TOL
        and maximum_selected_pairwise_drift <= TOL
        and all(row["index_topology_digest"] == index_topology_digest for row in witness_rows)
    )
    continuous_isometry = (
        certificate["continuous_for_every_real_parent_child_pair_in_closed_product_domain"] is True
        and certificate["child_rigidity_preserved_for_every_parent_child_pair"] is True
        and len(partial_triangles) == 0
        and minimum_neutral_area > TOL
    )
    if not representative_pass or not continuous_isometry:
        result = "HOLD_EAST_MID_HIERARCHICAL_REBASE_CHILD_TOPOLOGY_ISOMETRY"
    else:
        result = RESULT

    return {
        "schema": SCHEMA,
        "result": result,
        "reusable_rule": (
            "RIGID_HIERARCHICAL_FRAME_REBASE_PRESERVES_CHILD_TOPOLOGY_ONLY_AFTER_EXACT_OWNER_REBIND"
            "__NO_PARENT_MESH_DEFORMATION_OR_CLEARANCE_TRANSFER"
        ),
        "lineage": {
            "repository": "mike-axiom-mir/axm-nature-design",
            "geometry_pr": 18,
            "geometry_predecessor_head": GEOMETRY_PREDECESSOR_HEAD,
            "rigging_pr": 14,
            "rigging_hierarchy_owner_head": RIGGING_OWNER_HEAD,
            "organic_source_owner_head": rig_family.SOURCE_OWNER_HEAD,
            "geometry_receiver_head": rig_family.GEOMETRY_RECEIVER_HEAD,
            "migrated_mesh_digest": mesh_digest,
        },
        "receiver": {
            "vertices": len(mesh["vertices"]),
            "triangles": len(mesh["triangles"]),
            "index_topology_digest": index_topology_digest,
            "child_branch_id": CHILD_BRANCH_ID,
            "selected_vertices": len(selected_indices),
            "owned_triangles": len(owned_triangles),
            "partial_selected_triangles": len(partial_triangles),
            "triangle_closed_child_partition": len(partial_triangles) == 0,
            "minimum_neutral_owned_triangle_area_m2": minimum_neutral_area,
        },
        "representative_recheck": {
            "witness_count": len(witness_rows),
            "maximum_owned_triangle_area_drift_m2": maximum_triangle_area_drift,
            "maximum_selected_pairwise_distance_drift_m": maximum_selected_pairwise_drift,
            "witnesses": witness_rows,
        },
        "continuous_structural_certificate": {
            "parent_interval_deg": list(certificate["parent_interval_deg"]),
            "child_interval_deg": list(certificate["child_interval_deg"]),
            "continuous_child_topology_isometry": continuous_isometry,
            "reason": (
                "The exact child index partition is constant, all neutral owned triangles are nondegenerate, "
                "and the re-executed Rigging owner certifies the child transform as a rigid isometry for every "
                "real parent/child pair in the closed product domain. Rigid isometries preserve distances, "
                "triangle areas and incidence; therefore the child structural topology is invariant over that domain."
            ),
            "predecessor_five_child_continuous_clearance_transferred": False,
            "simultaneous_parent_plus_five_branch_motion_proven": False,
            "trunk_mesh_deformation_proven": False,
            "branch_trunk_surface_attachment_proven": False,
            "collision_or_self_intersection_proven": False,
        },
        "rigging_measurements_reexecuted": rigging_evidence["measurements"],
        "truth_boundary": {
            "source_geometry_rewritten": False,
            "geometry_receiver_rewritten": False,
            "rigging_policy_rewritten": False,
            "predecessor_clearance_pass_transferred": False,
            "trunk_mesh_deformation_claimed": False,
            "surface_attachment_claimed": False,
            "north_low_overlap_policy_claimed_resolved": False,
            "simultaneous_whole_tree_motion_claimed": False,
            "collision_or_gameplay_claimed": False,
            "animation_vfx_target_host_runtime_claimed": False,
            "canon_production_game_readiness_claimed": False,
            "geometry_mastery_claimed": False,
        },
    }

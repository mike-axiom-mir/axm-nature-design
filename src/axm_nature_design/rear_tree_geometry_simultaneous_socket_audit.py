"""Geometry-owned simultaneous composition audit for the east/rear Nature tree.

The Rigging owner independently proves five source-declared rigid child sockets on
one exact Geometry-migrated receiver.  Pairwise-disjoint vertex ownership is useful,
but it is not by itself evidence that the five children can be composed together
without ambiguous triangle ownership or order-dependent vertex results.

This module performs only that bounded Geometry composition check.  It never widens
the Rigging diagnostic interval, never authors motion, and never claims collision or
continuous self-intersection freedom.  A separate verifier may pass the resulting
exact witness meshes to the merged UC read-only self-intersection observer.
"""
from __future__ import annotations

import copy
import itertools
from typing import Iterable

from . import rear_tree_rigging as rig_math
from . import rear_tree_rigging_primary_branch_family as rig_family
from .organic_form import build_mesh, digest, validate_source

SCHEMA = "axm.nature-geometry-simultaneous-primary-branch-composition/v0.1"
RIGGING_PARENT_HEAD = "898529f602893c8f6be179bd3e9b6821fc099904"
BRANCH_IDS = tuple(rig_family.BRANCH_IDS)
CORNER_ANGLES_DEG = (-5.0, 5.0)
EXPECTED_MIGRATED_MESH_DIGEST = rig_family.EXPECTED_MIGRATED_MESH_DIGEST
TOL = rig_family.TOL


def _distance(left: Iterable[float], right: Iterable[float]) -> float:
    return rig_math._distance(list(left), list(right))


def _compose(
    neutral_vertices: list[list[float]],
    probes_by_branch: dict[str, dict],
    angles_by_branch: dict[str, float],
    order: Iterable[str],
) -> list[list[float]]:
    """Compose disjoint rigid children from the same neutral receiver."""
    result = copy.deepcopy(neutral_vertices)
    for branch_id in order:
        probe = probes_by_branch[branch_id]
        angle = float(angles_by_branch[branch_id])
        pivot = probe["joint_pivot_m"]
        axis = probe["source_derived_axis"]
        for index in probe["selected_vertex_indices"]:
            # Deliberately rotate from the neutral source, not a previously-mutated
            # value.  Disjoint ownership should make composition order irrelevant.
            result[index] = rig_math._rotate_about_axis(
                neutral_vertices[index], pivot, axis, angle
            )
    return result


def _triangle_partition_audit(mesh: dict, selected_sets: dict[str, set[int]]) -> dict:
    partial_selected_triangles: list[int] = []
    cross_branch_triangles: list[int] = []
    owned_triangle_counts = {branch_id: 0 for branch_id in BRANCH_IDS}
    globally_fixed_triangles = 0

    for triangle_index, triangle in enumerate(mesh["triangles"]):
        face = set(int(index) for index in triangle)
        touched = [branch_id for branch_id in BRANCH_IDS if face & selected_sets[branch_id]]
        if not touched:
            globally_fixed_triangles += 1
            continue
        if len(touched) > 1:
            cross_branch_triangles.append(triangle_index)
            continue
        owner = touched[0]
        if not face.issubset(selected_sets[owner]):
            partial_selected_triangles.append(triangle_index)
            continue
        owned_triangle_counts[owner] += 1

    return {
        "owned_triangle_counts": owned_triangle_counts,
        "globally_fixed_triangles": globally_fixed_triangles,
        "partial_selected_triangle_count": len(partial_selected_triangles),
        "partial_selected_triangle_examples": partial_selected_triangles[:16],
        "cross_branch_triangle_count": len(cross_branch_triangles),
        "cross_branch_triangle_examples": cross_branch_triangles[:16],
        "triangle_closed_child_partitions": not partial_selected_triangles
        and not cross_branch_triangles,
    }


def evaluate(
    source: dict,
    *,
    requested_rigging_parent_head: str = RIGGING_PARENT_HEAD,
    claim_continuous_deformation_clearance: bool = False,
    claim_collision_or_gameplay: bool = False,
    include_positions: bool = False,
) -> dict:
    """Build neutral + all 32 simultaneous +/-5 degree corner witnesses."""
    validate_source(source)
    if requested_rigging_parent_head != RIGGING_PARENT_HEAD:
        raise ValueError("exact Rigging parent head drift")
    if claim_continuous_deformation_clearance:
        raise ValueError("discrete Geometry witnesses cannot claim continuous clearance")
    if claim_collision_or_gameplay:
        raise ValueError("Geometry evidence cannot claim collision/gameplay acceptance")

    # Re-run the exact owner prerequisite rather than inheriting its PASS.
    rigging_evidence = rig_family.evaluate(source)
    if rigging_evidence.get("result") != rig_family.RESULT:
        raise ValueError("exact five-socket Rigging prerequisite did not pass")

    mesh = build_mesh(source)
    mesh_digest = digest(mesh)
    if mesh_digest != EXPECTED_MIGRATED_MESH_DIGEST:
        raise ValueError("exact Geometry-migrated receiver identity drift")

    neutral_vertices = [[float(value) for value in vertex] for vertex in mesh["vertices"]]
    probes = [rig_family._probe_branch(source, mesh, branch_id) for branch_id in BRANCH_IDS]
    probes_by_branch = {probe["branch_id"]: probe for probe in probes}
    selected_sets = {
        branch_id: set(probes_by_branch[branch_id]["selected_vertex_indices"])
        for branch_id in BRANCH_IDS
    }

    pairwise_disjoint = all(
        not (selected_sets[left] & selected_sets[right])
        for left_index, left in enumerate(BRANCH_IDS)
        for right in BRANCH_IDS[left_index + 1 :]
    )
    if not pairwise_disjoint:
        raise ValueError("Rigging child selections are no longer pairwise vertex-disjoint")

    selected_union = set().union(*(selected_sets[branch_id] for branch_id in BRANCH_IDS))
    globally_fixed_indices = [
        index for index in range(len(neutral_vertices)) if index not in selected_union
    ]
    partition = _triangle_partition_audit(mesh, selected_sets)

    requested_states: list[tuple[str, dict[str, float]]] = [
        ("neutral", {branch_id: 0.0 for branch_id in BRANCH_IDS})
    ]
    for corner_index, values in enumerate(
        itertools.product(CORNER_ANGLES_DEG, repeat=len(BRANCH_IDS))
    ):
        requested_states.append(
            (
                f"corner-{corner_index:02d}",
                {branch_id: float(angle) for branch_id, angle in zip(BRANCH_IDS, values)},
            )
        )

    states: list[dict] = []
    maximum_order_delta = 0.0
    maximum_globally_fixed_drift = 0.0
    maximum_pivot_drift = 0.0
    for state_id, angles in requested_states:
        canonical = _compose(neutral_vertices, probes_by_branch, angles, BRANCH_IDS)
        reverse = _compose(neutral_vertices, probes_by_branch, angles, reversed(BRANCH_IDS))
        order_delta = max(
            (_distance(canonical[index], reverse[index]) for index in range(len(canonical))),
            default=0.0,
        )
        fixed_drift = max(
            (_distance(canonical[index], neutral_vertices[index]) for index in globally_fixed_indices),
            default=0.0,
        )
        pivot_drift = max(
            (
                _distance(canonical[index], neutral_vertices[index])
                for probe in probes
                for index in probe["generated_pivot_vertex_indices"]
            ),
            default=0.0,
        )
        maximum_order_delta = max(maximum_order_delta, order_delta)
        maximum_globally_fixed_drift = max(maximum_globally_fixed_drift, fixed_drift)
        maximum_pivot_drift = max(maximum_pivot_drift, pivot_drift)
        state = {
            "state_id": state_id,
            "angles_deg": angles,
            "vertex_count": len(canonical),
            "triangle_count": len(mesh["triangles"]),
            "index_topology_digest": digest(mesh["triangles"]),
            "posed_mesh_digest": digest({"vertices": canonical, "triangles": mesh["triangles"]}),
            "composition_order_max_vertex_delta_m": order_delta,
            "globally_fixed_vertex_max_drift_m": fixed_drift,
            "pivot_vertex_max_drift_m": pivot_drift,
        }
        if include_positions:
            state["positions"] = canonical
        states.append(state)

    structural_pass = (
        partition["triangle_closed_child_partitions"]
        and maximum_order_delta <= TOL
        and maximum_globally_fixed_drift <= TOL
        and maximum_pivot_drift <= TOL
    )
    result = (
        "PASS_SIMULTANEOUS_FIVE_CHILD_COMPOSITION_STRUCTURE_32_EXTREME_CORNERS"
        if structural_pass
        else "HOLD_SIMULTANEOUS_FIVE_CHILD_COMPOSITION_PARTITION_STRUCTURE"
    )

    return {
        "schema": SCHEMA,
        "result": result,
        "lineage": {
            "rigging_parent_head": RIGGING_PARENT_HEAD,
            "organic_source_owner_head": rig_family.SOURCE_OWNER_HEAD,
            "geometry_receiver_head": rig_family.GEOMETRY_RECEIVER_HEAD,
            "migrated_mesh_digest": mesh_digest,
        },
        "receiver": {
            "vertices": len(mesh["vertices"]),
            "triangles": len(mesh["triangles"]),
            "branch_ids": list(BRANCH_IDS),
            "per_branch_selected_vertices": {
                branch_id: len(selected_sets[branch_id]) for branch_id in BRANCH_IDS
            },
            "selected_vertex_union": len(selected_union),
            "globally_fixed_vertices": len(globally_fixed_indices),
            "pairwise_child_vertex_disjoint": pairwise_disjoint,
            "triangle_partition": partition,
        },
        "witness_family": {
            "neutral_state_count": 1,
            "extreme_corner_state_count": 32,
            "total_state_count": len(states),
            "per_branch_corner_angles_deg": list(CORNER_ANGLES_DEG),
            "maximum_composition_order_vertex_delta_m": maximum_order_delta,
            "maximum_globally_fixed_vertex_drift_m": maximum_globally_fixed_drift,
            "maximum_pivot_vertex_drift_m": maximum_pivot_drift,
            "states": states,
        },
        "truth_boundary": {
            "rigging_interval_widened": False,
            "source_or_biological_rom_claimed": False,
            "continuous_deformation_clearance_claimed": False,
            "self_intersection_freedom_claimed_by_this_module": False,
            "collision_or_gameplay_claimed": False,
            "animation_or_vfx_motion_adopted": False,
            "runtime_or_target_device_claimed": False,
            "automatic_source_or_receiver_adoption": False,
            "canon_or_production_readiness_claimed": False,
        },
    }

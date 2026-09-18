"""Geometry rebind for exact downstream shared-driver static witness poses.

Nature Geometry PR #18 already proves neutral plus all 32 independent +/-5 degree
corner poses for five triangle-closed rigid children. Later Rigging and VFX owners
introduced one exact sign-normalized shared diagnostic command and retained five
STATIC simultaneous review poses: -5, -2.5, 0, +2.5, +5 degrees.

Those downstream poses are not motion authority and their PASS cannot inherit the
older Geometry result merely because three endpoints overlap. This module replays
the exact command mapping on the unchanged Geometry receiver and keeps the two
interior +/-2.5 degree witnesses explicit for a fresh Geometry observer.
"""
from __future__ import annotations

from typing import Iterable

from . import rear_tree_rigging_primary_branch_family as rig_family
from .organic_form import build_mesh, digest, validate_source
from .rear_tree_geometry_simultaneous_socket_audit import (
    BRANCH_IDS,
    TOL,
    _compose,
    _distance,
    evaluate as evaluate_prior_geometry,
)

SCHEMA = "axm.nature-geometry-shared-driver-static-rebind/v0.1"
PRIOR_GEOMETRY_HEAD = "76c89348d63fd3523f81287767fc37527d6a8fcb"
RIGGING_SHARED_DRIVER_HEAD = "754797a815266a643c6b08f1606eb76ba95dd8c6"
VFX_STATIC_RESPONSE_HEAD = "ba1c12dd527f1ecc6a0eb4bc0b4322f15ccad475"
SHARED_DRIVER_VALUES_DEG = (-5.0, -2.5, 0.0, 2.5, 5.0)
COMMAND_SIGN_MULTIPLIER_BY_BRANCH = {
    "south-low": 1.0,
    "north-low": -1.0,
    "east-mid": 1.0,
    "west-high": -1.0,
    "north-top": 1.0,
}
EXPECTED_MIGRATED_MESH_DIGEST = rig_family.EXPECTED_MIGRATED_MESH_DIGEST


def _state_id(shared_driver_deg: float) -> str:
    if shared_driver_deg == 0.0:
        return "shared-zero"
    prefix = "pos" if shared_driver_deg > 0 else "neg"
    magnitude = str(abs(shared_driver_deg)).replace(".", "p")
    return f"shared-{prefix}-{magnitude}"


def _angles_for_shared_driver(shared_driver_deg: float) -> dict[str, float]:
    return {
        branch_id: float(COMMAND_SIGN_MULTIPLIER_BY_BRANCH[branch_id] * shared_driver_deg)
        for branch_id in BRANCH_IDS
    }


def evaluate(
    source: dict,
    *,
    requested_rigging_head: str = RIGGING_SHARED_DRIVER_HEAD,
    requested_vfx_head: str = VFX_STATIC_RESPONSE_HEAD,
    requested_shared_driver_values: Iterable[float] = SHARED_DRIVER_VALUES_DEG,
    claim_continuous_interval: bool = False,
    claim_simultaneous_motion: bool = False,
    include_positions: bool = False,
) -> dict:
    """Replay exactly five static shared-driver poses on the unchanged receiver."""
    validate_source(source)
    if requested_rigging_head != RIGGING_SHARED_DRIVER_HEAD:
        raise ValueError("exact shared-driver Rigging head drift")
    if requested_vfx_head != VFX_STATIC_RESPONSE_HEAD:
        raise ValueError("exact VFX static-response head drift")

    requested_values = tuple(float(value) for value in requested_shared_driver_values)
    if requested_values != SHARED_DRIVER_VALUES_DEG:
        raise ValueError("exact downstream shared-driver witness set drift")
    if claim_continuous_interval:
        raise ValueError("five static witnesses cannot claim a continuous interval")
    if claim_simultaneous_motion:
        raise ValueError("static Geometry witnesses cannot claim simultaneous motion")

    # Re-run the exact prior Geometry prerequisite rather than transferring its PASS.
    prior = evaluate_prior_geometry(source)
    if prior.get("result") != "PASS_SIMULTANEOUS_FIVE_CHILD_COMPOSITION_STRUCTURE_32_EXTREME_CORNERS":
        raise ValueError("prior Geometry simultaneous-composition prerequisite did not pass")
    if prior["receiver"]["triangle_partition"]["triangle_closed_child_partitions"] is not True:
        raise ValueError("prior Geometry child partition closure drift")

    mesh = build_mesh(source)
    mesh_digest = digest(mesh)
    if mesh_digest != EXPECTED_MIGRATED_MESH_DIGEST:
        raise ValueError("exact Geometry-migrated receiver identity drift")

    neutral_vertices = [[float(value) for value in vertex] for vertex in mesh["vertices"]]
    probes = [rig_family._probe_branch(source, mesh, branch_id) for branch_id in BRANCH_IDS]
    probes_by_branch = {probe["branch_id"]: probe for probe in probes}
    selected_sets = {
        branch_id: set(int(index) for index in probes_by_branch[branch_id]["selected_vertex_indices"])
        for branch_id in BRANCH_IDS
    }
    selected_union = set().union(*(selected_sets[branch_id] for branch_id in BRANCH_IDS))
    globally_fixed_indices = [
        index for index in range(len(neutral_vertices)) if index not in selected_union
    ]

    prior_pose_digests = {
        state["posed_mesh_digest"] for state in prior["witness_family"]["states"]
    }
    states: list[dict] = []
    maximum_order_delta = 0.0
    maximum_fixed_drift = 0.0
    maximum_pivot_drift = 0.0
    prior_overlap_count = 0

    for shared_driver_deg in SHARED_DRIVER_VALUES_DEG:
        angles = _angles_for_shared_driver(shared_driver_deg)
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
        posed_digest = digest({"vertices": canonical, "triangles": mesh["triangles"]})
        overlaps_prior = posed_digest in prior_pose_digests
        if overlaps_prior:
            prior_overlap_count += 1

        maximum_order_delta = max(maximum_order_delta, order_delta)
        maximum_fixed_drift = max(maximum_fixed_drift, fixed_drift)
        maximum_pivot_drift = max(maximum_pivot_drift, pivot_drift)

        state = {
            "state_id": _state_id(shared_driver_deg),
            "shared_driver_deg": shared_driver_deg,
            "angles_deg": angles,
            "vertex_count": len(canonical),
            "triangle_count": len(mesh["triangles"]),
            "index_topology_digest": digest(mesh["triangles"]),
            "posed_mesh_digest": posed_digest,
            "overlaps_prior_geometry_witness": overlaps_prior,
            "composition_order_max_vertex_delta_m": order_delta,
            "globally_fixed_vertex_max_drift_m": fixed_drift,
            "pivot_vertex_max_drift_m": pivot_drift,
        }
        if include_positions:
            state["positions"] = canonical
        states.append(state)

    # Exactly neutral and the two +/-5 shared-command endpoints should coincide with
    # witnesses in the old 33-state family; +/-2.5 are genuinely new interior poses.
    if prior_overlap_count != 3:
        raise ValueError("unexpected overlap cardinality with prior Geometry witnesses")

    structure_pass = (
        maximum_order_delta <= TOL
        and maximum_fixed_drift <= TOL
        and maximum_pivot_drift <= TOL
    )
    result = (
        "PASS_SHARED_DRIVER_STATIC_WITNESS_STRUCTURE_REBOUND"
        if structure_pass
        else "HOLD_SHARED_DRIVER_STATIC_WITNESS_STRUCTURE"
    )

    return {
        "schema": SCHEMA,
        "result": result,
        "lineage": {
            "prior_geometry_head": PRIOR_GEOMETRY_HEAD,
            "rigging_shared_driver_head": RIGGING_SHARED_DRIVER_HEAD,
            "vfx_static_response_head": VFX_STATIC_RESPONSE_HEAD,
            "organic_source_owner_head": rig_family.SOURCE_OWNER_HEAD,
            "geometry_receiver_head": rig_family.GEOMETRY_RECEIVER_HEAD,
            "migrated_mesh_digest": mesh_digest,
        },
        "receiver": {
            "vertices": len(mesh["vertices"]),
            "triangles": len(mesh["triangles"]),
            "branch_ids": list(BRANCH_IDS),
            "selected_vertex_union": len(selected_union),
            "globally_fixed_vertices": len(globally_fixed_indices),
            "per_branch_selected_vertices": {
                branch_id: len(selected_sets[branch_id]) for branch_id in BRANCH_IDS
            },
            "triangle_partition": prior["receiver"]["triangle_partition"],
        },
        "shared_driver": {
            "mapping": "local_angle_deg = command_sign_multiplier * shared_driver_deg",
            "values_deg": list(SHARED_DRIVER_VALUES_DEG),
            "command_sign_multiplier_by_branch": dict(COMMAND_SIGN_MULTIPLIER_BY_BRANCH),
            "state_count": len(states),
            "prior_geometry_overlap_state_count": prior_overlap_count,
            "new_interior_state_count": len(states) - prior_overlap_count,
            "maximum_composition_order_vertex_delta_m": maximum_order_delta,
            "maximum_globally_fixed_vertex_drift_m": maximum_fixed_drift,
            "maximum_pivot_vertex_drift_m": maximum_pivot_drift,
            "states": states,
        },
        "truth_boundary": {
            "static_simultaneous_review_only": True,
            "continuous_interval_checked": False,
            "simultaneous_motion_claimed": False,
            "child_fixed_receiver_clearance_checked": False,
            "adjacent_foldover_or_contact_checked": False,
            "physical_collision_checked": False,
            "source_or_biological_rom_claimed": False,
            "animation_timing_or_playback_claimed": False,
            "target_host_or_runtime_claimed": False,
            "automatic_adoption_authorized": False,
            "canon_or_production_readiness_claimed": False,
        },
    }

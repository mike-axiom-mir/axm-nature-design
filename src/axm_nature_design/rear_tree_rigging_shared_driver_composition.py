"""Rigging-owned simultaneous shared-driver kinematic composition proof.

This bounded successor keeps the exact five source-derived branch sockets, pivots,
axes, child partitions, diagnostic interval and mixed command-sign map unchanged.
It answers one Rigging question only: whether one scalar shared diagnostic parameter
can be applied to all five sockets at once as a deterministic, continuous kinematic
composition without changing receiver identity or taking Animation/Runtime authority.

Geometry's current shared-driver static rebind is consumed as an exact read-only
structural donor. Its finite intersection observations are *not* promoted into a
continuous collision claim here.
"""
from __future__ import annotations

import copy
import math
from typing import Iterable

from . import rear_tree_rigging as historical
from . import rear_tree_rigging_primary_branch_family as rig_family
from . import rear_tree_rigging_shared_driver_polarity as polarity
from .organic_form import build_mesh, digest, validate_source

SCHEMA = "axm.nature-five-socket-shared-driver-rig-composition/v0.1"
RESULT = "PASS_FIVE_SOCKET_SHARED_DRIVER_RIG_COMPOSITION_CONTINUOUS_PARAMETER_MINUS5_TO_PLUS5"
RIGGING_PREDECESSOR_HEAD = "754797a815266a643c6b08f1606eb76ba95dd8c6"
GEOMETRY_DONOR_HEAD = "75b7556b4dae7137411f4948e2e673a39de5467c"
GEOMETRY_CONTRACT_PATH = "contracts/east-rear-shared-driver-static-geometry-rebind-002.json"
GEOMETRY_CONTRACT_BLOB = "7056bb9b2160f536b88bf4827a81dec27af3f137"
GEOMETRY_MODULE_PATH = "src/axm_nature_design/rear_tree_geometry_shared_driver_static_rebind.py"
GEOMETRY_MODULE_BLOB = "33934c6352f56baa3690f8fdaffde775d85f8f4c"
VFX_STATIC_RESPONSE_HEAD = "ba1c12dd527f1ecc6a0eb4bc0b4322f15ccad475"
BRANCH_IDS = rig_family.BRANCH_IDS
REPRESENTATIVE_SHARED_DRIVER_DEG = polarity.REPRESENTATIVE_SHARED_DRIVER_DEG
SHARED_DRIVER_MIN_DEG = polarity.SHARED_DRIVER_MIN_DEG
SHARED_DRIVER_MAX_DEG = polarity.SHARED_DRIVER_MAX_DEG
COMMAND_SIGN_MULTIPLIER = polarity.COMMAND_SIGN_MULTIPLIER
TOL = rig_family.TOL


def _distance(a: Iterable[float], b: Iterable[float]) -> float:
    return math.sqrt(sum((float(x) - float(y)) ** 2 for x, y in zip(a, b)))


def _compose(neutral_vertices: list[list[float]], probes_by_branch: dict[str, dict], shared_driver_deg: float, order: Iterable[str]) -> list[list[float]]:
    """Compose disjoint Rigging children from the same exact neutral receiver."""
    posed = copy.deepcopy(neutral_vertices)
    for branch_id in order:
        probe = probes_by_branch[branch_id]
        local_angle = polarity.local_angle_for_shared_driver(branch_id, shared_driver_deg)
        pivot = probe["joint_pivot_m"]
        axis = probe["source_derived_axis"]
        for index in probe["selected_vertex_indices"]:
            # Always transform the exact neutral vertex. Because selected sets are
            # pairwise disjoint, composition order cannot accumulate transforms.
            posed[index] = historical._rotate_about_axis(
                neutral_vertices[index], pivot, axis, local_angle
            )
    return posed


def evaluate(
    source: dict,
    *,
    requested_geometry_donor_head: str = GEOMETRY_DONOR_HEAD,
    requested_vfx_static_response_head: str = VFX_STATIC_RESPONSE_HEAD,
    representative_shared_driver_deg=REPRESENTATIVE_SHARED_DRIVER_DEG,
    claim_animation_acceptance: bool = False,
    claim_runtime_acceptance: bool = False,
    claim_physical_wind: bool = False,
    claim_continuous_collision_clearance: bool = False,
    claim_source_or_biological_rom: bool = False,
) -> dict:
    """Prove a continuous Rigging parameter field, not timed motion or collision."""
    validate_source(source)
    if requested_geometry_donor_head != GEOMETRY_DONOR_HEAD:
        raise ValueError("exact Geometry shared-driver donor head drift")
    if requested_vfx_static_response_head != VFX_STATIC_RESPONSE_HEAD:
        raise ValueError("exact VFX static-response donor head drift")

    drivers = tuple(float(value) for value in representative_shared_driver_deg)
    if drivers != REPRESENTATIVE_SHARED_DRIVER_DEG:
        raise ValueError("representative shared-driver witness field drift")
    if claim_animation_acceptance:
        raise ValueError("Rigging kinematic composition cannot claim Animation acceptance")
    if claim_runtime_acceptance:
        raise ValueError("Rigging kinematic composition cannot claim Runtime acceptance")
    if claim_physical_wind:
        raise ValueError("shared diagnostic parameter is not physical wind")
    if claim_continuous_collision_clearance:
        raise ValueError("finite Geometry collision witnesses do not prove continuous collision clearance")
    if claim_source_or_biological_rom:
        raise ValueError("Rigging diagnostic interval is not source or biological ROM")

    polarity_evidence = polarity.evaluate(source)
    if polarity_evidence["result"] != polarity.RESULT:
        raise ValueError("exact shared-driver polarity predecessor is not green")

    family = rig_family.evaluate(source)
    if family["result"] != rig_family.RESULT:
        raise ValueError("exact five-socket Rigging family predecessor is not green")

    mesh = build_mesh(source)
    if digest(mesh) != rig_family.EXPECTED_MIGRATED_MESH_DIGEST:
        raise ValueError("exact Geometry-migrated receiver identity drift")

    neutral = [[float(value) for value in vertex] for vertex in mesh["vertices"]]
    probes = [rig_family._probe_branch(source, mesh, branch_id) for branch_id in BRANCH_IDS]
    probes_by_branch = {probe["branch_id"]: probe for probe in probes}
    selected_sets = {
        branch_id: set(int(index) for index in probes_by_branch[branch_id]["selected_vertex_indices"])
        for branch_id in BRANCH_IDS
    }
    pairwise_disjoint = all(
        not (selected_sets[BRANCH_IDS[left]] & selected_sets[BRANCH_IDS[right]])
        for left in range(len(BRANCH_IDS))
        for right in range(left + 1, len(BRANCH_IDS))
    )
    if not pairwise_disjoint:
        raise ValueError("five Rigging child partitions are not pairwise disjoint")

    selected_union = set().union(*(selected_sets[branch_id] for branch_id in BRANCH_IDS))
    fixed_indices = [index for index in range(len(neutral)) if index not in selected_union]
    if len(selected_union) != 260 or len(fixed_indices) != 130:
        raise ValueError("five-child receiver partition identity drift")

    neutral_pairwise = {
        branch_id: historical._pairwise_distances(
            [neutral[index] for index in probes_by_branch[branch_id]["selected_vertex_indices"]]
        )
        for branch_id in BRANCH_IDS
    }

    states = []
    max_order_delta = 0.0
    max_fixed_drift = 0.0
    max_pivot_drift = 0.0
    max_pairwise_drift = 0.0
    max_axis_projection_drift = 0.0
    max_selected_displacement = 0.0

    for shared_driver_deg in drivers:
        canonical = _compose(neutral, probes_by_branch, shared_driver_deg, BRANCH_IDS)
        reverse = _compose(neutral, probes_by_branch, shared_driver_deg, reversed(BRANCH_IDS))
        order_delta = max((_distance(a, b) for a, b in zip(canonical, reverse)), default=0.0)
        fixed_drift = max((_distance(canonical[index], neutral[index]) for index in fixed_indices), default=0.0)

        pivot_drift = 0.0
        pairwise_drift = 0.0
        axis_projection_drift = 0.0
        selected_displacement = 0.0
        local_angles = {}
        for branch_id in BRANCH_IDS:
            probe = probes_by_branch[branch_id]
            local_angles[branch_id] = polarity.local_angle_for_shared_driver(branch_id, shared_driver_deg)
            for index in probe["generated_pivot_vertex_indices"]:
                pivot_drift = max(pivot_drift, _distance(canonical[index], neutral[index]))

            selected_indices = probe["selected_vertex_indices"]
            selected = [canonical[index] for index in selected_indices]
            pairwise_drift = max(
                pairwise_drift,
                historical._max_abs_delta(
                    historical._pairwise_distances(selected), neutral_pairwise[branch_id]
                ),
            )
            pivot = probe["joint_pivot_m"]
            axis = probe["source_derived_axis"]
            axis_projection_drift = max(
                axis_projection_drift,
                max(
                    (
                        abs(
                            historical._dot(historical._sub(canonical[index], pivot), axis)
                            - historical._dot(historical._sub(neutral[index], pivot), axis)
                        )
                        for index in selected_indices
                    ),
                    default=0.0,
                ),
            )
            selected_displacement = max(
                selected_displacement,
                max((_distance(canonical[index], neutral[index]) for index in selected_indices), default=0.0),
            )

        max_order_delta = max(max_order_delta, order_delta)
        max_fixed_drift = max(max_fixed_drift, fixed_drift)
        max_pivot_drift = max(max_pivot_drift, pivot_drift)
        max_pairwise_drift = max(max_pairwise_drift, pairwise_drift)
        max_axis_projection_drift = max(max_axis_projection_drift, axis_projection_drift)
        max_selected_displacement = max(max_selected_displacement, selected_displacement)
        states.append(
            {
                "shared_driver_deg": shared_driver_deg,
                "local_angles_deg": local_angles,
                "composition_order_max_vertex_delta_m": order_delta,
                "globally_fixed_vertex_max_drift_m": fixed_drift,
                "pivot_vertex_max_drift_m": pivot_drift,
                "rigid_child_pairwise_distance_max_drift_m": pairwise_drift,
                "child_axis_projection_max_drift_m": axis_projection_drift,
                "maximum_selected_vertex_displacement_m": selected_displacement,
            }
        )

    checks = {
        "exact_shared_driver_predecessor_green": polarity_evidence["result"] == polarity.RESULT,
        "exact_five_socket_family_green": family["result"] == rig_family.RESULT,
        "exact_branch_order_preserved": tuple(probes_by_branch) == BRANCH_IDS,
        "mixed_sign_map_preserved": tuple(COMMAND_SIGN_MULTIPLIER[b] for b in BRANCH_IDS) == (1.0, -1.0, 1.0, -1.0, 1.0),
        "five_child_vertex_sets_pairwise_disjoint": pairwise_disjoint,
        "five_child_receiver_partition_exact": len(selected_union) == 260 and len(fixed_indices) == 130,
        "representative_composition_order_invariant": max_order_delta <= TOL,
        "representative_globally_fixed_receiver_exact": max_fixed_drift <= TOL,
        "representative_pivots_exact": max_pivot_drift <= TOL,
        "representative_children_rigid": max_pairwise_drift <= TOL,
        "representative_axis_projection_preserved": max_axis_projection_drift <= TOL,
    }
    if not all(checks.values()):
        raise ValueError("shared-driver simultaneous Rigging composition checks failed")

    # Analytic boundary: for each child, p(u)=pivot+R(axis,m*u)(p0-pivot).
    # R is continuous for every real u; fixed vertices are identity; disjoint support
    # makes the five transforms commute; rotations preserve pairwise distance and
    # projection onto their own axis. This proves kinematic parameter continuity,
    # not collision clearance or timed Animation motion.
    continuous_parameter_certificate = {
        "shared_driver_interval_deg": [SHARED_DRIVER_MIN_DEG, SHARED_DRIVER_MAX_DEG],
        "local_angle_formula": "local_angle_i(u) = command_sign_multiplier_i * u",
        "vertex_formula": "p_i(u) = pivot_i + R(axis_i, local_angle_i(u)) * (p_i0 - pivot_i)",
        "continuous_for_every_real_parameter_in_closed_interval": True,
        "pairwise_disjoint_transform_support": True,
        "composition_order_independent_for_every_real_parameter": True,
        "fixed_receiver_identity_for_every_real_parameter": True,
        "pivot_invariant_for_every_real_parameter": True,
        "rigid_child_pairwise_distances_invariant_for_every_real_parameter": True,
        "child_axis_projection_invariant_for_every_real_parameter": True,
        "local_angle_never_exceeds_existing_rigging_interval": True,
        "timing_or_playback_defined": False,
        "continuous_collision_clearance_proven": False,
    }

    return {
        "schema": SCHEMA,
        "result": RESULT,
        "lineage": {
            "rigging_predecessor_head": RIGGING_PREDECESSOR_HEAD,
            "geometry_donor_head": GEOMETRY_DONOR_HEAD,
            "geometry_contract_path": GEOMETRY_CONTRACT_PATH,
            "geometry_contract_blob": GEOMETRY_CONTRACT_BLOB,
            "geometry_module_path": GEOMETRY_MODULE_PATH,
            "geometry_module_blob": GEOMETRY_MODULE_BLOB,
            "vfx_static_response_head": VFX_STATIC_RESPONSE_HEAD,
            "organic_source_owner_head": rig_family.SOURCE_OWNER_HEAD,
            "geometry_receiver_head": rig_family.GEOMETRY_RECEIVER_HEAD,
            "source_digest": rig_family.EXPECTED_SOURCE_DIGEST,
            "migrated_mesh_digest": rig_family.EXPECTED_MIGRATED_MESH_DIGEST,
        },
        "composition": {
            "branch_ids": list(BRANCH_IDS),
            "command_sign_multiplier_by_branch": dict(COMMAND_SIGN_MULTIPLIER),
            "representative_shared_driver_deg": list(drivers),
            "selected_vertex_union": len(selected_union),
            "globally_fixed_vertices": len(fixed_indices),
            "per_branch_selected_vertices": {branch_id: len(selected_sets[branch_id]) for branch_id in BRANCH_IDS},
            "states": states,
        },
        "measurements": {
            "maximum_composition_order_vertex_delta_m": max_order_delta,
            "maximum_globally_fixed_vertex_drift_m": max_fixed_drift,
            "maximum_pivot_vertex_drift_m": max_pivot_drift,
            "maximum_rigid_child_pairwise_distance_drift_m": max_pairwise_drift,
            "maximum_child_axis_projection_drift_m": max_axis_projection_drift,
            "maximum_selected_vertex_displacement_m": max_selected_displacement,
        },
        "continuous_parameter_certificate": continuous_parameter_certificate,
        "checks": checks,
        "truth_boundary": {
            "static_kinematic_parameter_only_not_timed_motion": True,
            "source_or_biological_rom_claimed": False,
            "physical_wind_claimed": False,
            "continuous_collision_or_self_intersection_claimed": False,
            "finite_geometry_collision_witnesses_promoted_to_continuous": False,
            "animation_timing_interpolation_or_playback_claimed": False,
            "technical_art_target_host_acceptance_claimed": False,
            "runtime_controller_or_device_claimed": False,
            "physics_or_gameplay_claimed": False,
            "art_direction_or_visual_qa_acceptance_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }

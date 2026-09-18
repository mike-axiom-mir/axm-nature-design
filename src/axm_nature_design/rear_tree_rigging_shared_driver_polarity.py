"""Rigging-owned shared-driver polarity adapter for five Nature branch sockets.

This successor consumes the exact VFX review-only sign-map handoff without changing
any Rigging-owned pivot, axis, child partition, diagnostic interval, or source data.
It normalizes only command sign: one positive shared diagnostic command maps to the
per-socket local angle sign already shown by VFX to align with the same external
visual direction.

The adapter is a Rigging constraint/interface proof only. It does not author wind,
motion timing, cadence, amplitude, physics, Animation, Runtime, Art, or gameplay.
"""
from __future__ import annotations

from . import rear_tree_rigging_primary_branch_family as rigging_family

SCHEMA = "axm.nature-five-socket-shared-driver-polarity-binding/v0.1"
RESULT = "PASS_FIVE_SOCKET_SHARED_DRIVER_POLARITY_BINDING_DIAGNOSTIC_MINUS5_TO_PLUS5"
RIGGING_PREDECESSOR_HEAD = "898529f602893c8f6be179bd3e9b6821fc099904"
VFX_DONOR_HEAD = "ef7b35af27d5ca98a6447c1e33be07863e387305"
VFX_CONTRACT_PATH = "contracts/east-rear-primary-branch-weather-direction-vfx-sign-family-002.json"
VFX_CONTRACT_BLOB = "b06b5f6862c6c88ec5642e3bdbccfe0d3e65655f"
VFX_MODULE_PATH = "src/axm_nature_design/rear_tree_vfx_weather_sign_family.py"
VFX_MODULE_BLOB = "ae674ee8f6109d478446fbcd5348bcbee04b01e7"
BRANCH_IDS = rigging_family.BRANCH_IDS
SHARED_DRIVER_MIN_DEG = -5.0
SHARED_DRIVER_MAX_DEG = 5.0
REPRESENTATIVE_SHARED_DRIVER_DEG = (-5.0, -2.5, 0.0, 2.5, 5.0)
VFX_REVIEW_ONLY_PREFERRED_LOCAL_ANGLE_DEG = {
    "south-low": 5.0,
    "north-low": -5.0,
    "east-mid": 5.0,
    "west-high": -5.0,
    "north-top": 5.0,
}
COMMAND_SIGN_MULTIPLIER = {
    branch_id: (1.0 if angle > 0.0 else -1.0)
    for branch_id, angle in VFX_REVIEW_ONLY_PREFERRED_LOCAL_ANGLE_DEG.items()
}
TOL = rigging_family.TOL


def local_angle_for_shared_driver(branch_id: str, shared_driver_deg: float) -> float:
    """Map one bounded shared diagnostic command into an unchanged local Rigging angle."""
    if branch_id not in BRANCH_IDS:
        raise ValueError(f"unknown Rigging socket branch: {branch_id}")
    value = float(shared_driver_deg)
    if value < SHARED_DRIVER_MIN_DEG - TOL or value > SHARED_DRIVER_MAX_DEG + TOL:
        raise ValueError("shared driver command exceeds exact Rigging diagnostic interval")
    return COMMAND_SIGN_MULTIPLIER[branch_id] * value


def evaluate(
    source: dict,
    *,
    requested_vfx_donor_head: str = VFX_DONOR_HEAD,
    requested_preferred_local_angles: dict | None = None,
    representative_shared_driver_deg=REPRESENTATIVE_SHARED_DRIVER_DEG,
    claim_wind_motion: bool = False,
    claim_physical_wind: bool = False,
    claim_animation_acceptance: bool = False,
    claim_runtime_acceptance: bool = False,
    claim_simultaneous_motion: bool = False,
) -> dict:
    """Prove sign-normalized command binding while preserving exact Rigging identity."""
    if requested_vfx_donor_head != VFX_DONOR_HEAD:
        raise ValueError("exact VFX sign-map donor head drift")

    requested_map = (
        VFX_REVIEW_ONLY_PREFERRED_LOCAL_ANGLE_DEG
        if requested_preferred_local_angles is None
        else requested_preferred_local_angles
    )
    if dict(requested_map) != VFX_REVIEW_ONLY_PREFERRED_LOCAL_ANGLE_DEG:
        raise ValueError("exact VFX per-socket preferred local-angle map drift")

    drivers = tuple(float(value) for value in representative_shared_driver_deg)
    if drivers != REPRESENTATIVE_SHARED_DRIVER_DEG:
        raise ValueError("shared driver representative field may not be widened, reduced, or retimed")

    if claim_wind_motion:
        raise ValueError("Rigging sign binding does not adopt VFX or Weather motion")
    if claim_physical_wind:
        raise ValueError("visual-direction sign compatibility is not physical wind")
    if claim_animation_acceptance:
        raise ValueError("Rigging constraint evidence cannot claim Animation acceptance")
    if claim_runtime_acceptance:
        raise ValueError("Rigging constraint evidence cannot claim Runtime acceptance")
    if claim_simultaneous_motion:
        raise ValueError("sign-normalized independent sockets do not prove simultaneous motion")

    predecessor = rigging_family.evaluate(source)
    if predecessor["result"] != rigging_family.RESULT:
        raise ValueError("exact five-socket Rigging predecessor is not green")
    if tuple(predecessor["rigging_family"]["branch_ids"]) != BRANCH_IDS:
        raise ValueError("five-socket Rigging branch identity drift")

    probe_by_branch = {
        row["branch_id"]: row for row in predecessor["rigging_family"]["probes"]
    }
    rows = []
    for branch_id in BRANCH_IDS:
        probe = probe_by_branch[branch_id]
        multiplier = COMMAND_SIGN_MULTIPLIER[branch_id]
        preferred = VFX_REVIEW_ONLY_PREFERRED_LOCAL_ANGLE_DEG[branch_id]
        pose_by_angle = {float(row["angle_deg"]): row for row in probe["poses"]}

        mappings = []
        for shared in drivers:
            local = local_angle_for_shared_driver(branch_id, shared)
            if local not in pose_by_angle:
                raise ValueError(f"mapped local witness missing from exact Rigging predecessor: {branch_id}")
            mappings.append(
                {
                    "shared_driver_deg": shared,
                    "mapped_local_angle_deg": local,
                    "absolute_angle_preserved_deg": abs(local),
                    "predecessor_pose_reused": True,
                    "predecessor_pose_metrics": pose_by_angle[local],
                }
            )

        if abs(local_angle_for_shared_driver(branch_id, 5.0) - preferred) > TOL:
            raise ValueError(f"positive shared command does not select VFX preferred local sign: {branch_id}")
        if abs(local_angle_for_shared_driver(branch_id, -5.0) + preferred) > TOL:
            raise ValueError(f"negative shared command is not exact inverse local sign: {branch_id}")
        if abs(local_angle_for_shared_driver(branch_id, 0.0)) > TOL:
            raise ValueError(f"neutral shared command drift: {branch_id}")

        rows.append(
            {
                "branch_id": branch_id,
                "joint_pivot_m": probe["joint_pivot_m"],
                "source_derived_axis": probe["source_derived_axis"],
                "selected_vertices": probe["selected_vertices"],
                "selected_triangles": probe["selected_triangles"],
                "fixed_vertices": probe["fixed_vertices"],
                "diagnostic_interval_deg": probe["diagnostic_interval_deg"],
                "diagnostic_interval_semantics": probe["diagnostic_interval_semantics"],
                "vfx_review_only_preferred_local_angle_deg": preferred,
                "command_sign_multiplier": multiplier,
                "representative_driver_mapping": mappings,
            }
        )

    continuous_mapping = {
        "shared_driver_interval_deg": [SHARED_DRIVER_MIN_DEG, SHARED_DRIVER_MAX_DEG],
        "local_angle_formula": "local_angle_deg = command_sign_multiplier * shared_driver_deg",
        "absolute_angle_isometry": True,
        "bijective_per_socket_on_closed_interval": True,
        "neutral_maps_to_neutral": True,
        "boundary_maps_to_exact_existing_rigging_witnesses": True,
        "rigging_axis_or_pivot_changed": False,
        "rigging_child_partition_changed": False,
        "source_or_geometry_changed": False,
        "simultaneous_multi_branch_motion_proven": False,
    }

    checks = {
        "exact_predecessor_green": predecessor["result"] == rigging_family.RESULT,
        "exact_five_socket_identity": tuple(row["branch_id"] for row in rows) == BRANCH_IDS,
        "mixed_sign_map_preserved": tuple(COMMAND_SIGN_MULTIPLIER[b] for b in BRANCH_IDS)
        == (1.0, -1.0, 1.0, -1.0, 1.0),
        "positive_shared_boundary_selects_vfx_preferred_sign": all(
            abs(local_angle_for_shared_driver(branch_id, 5.0) - VFX_REVIEW_ONLY_PREFERRED_LOCAL_ANGLE_DEG[branch_id]) <= TOL
            for branch_id in BRANCH_IDS
        ),
        "negative_shared_boundary_is_exact_inverse": all(
            abs(local_angle_for_shared_driver(branch_id, -5.0) + VFX_REVIEW_ONLY_PREFERRED_LOCAL_ANGLE_DEG[branch_id]) <= TOL
            for branch_id in BRANCH_IDS
        ),
        "neutral_shared_command_is_exact": all(
            abs(local_angle_for_shared_driver(branch_id, 0.0)) <= TOL for branch_id in BRANCH_IDS
        ),
        "all_mapped_representatives_reuse_existing_rigging_poses": all(
            item["predecessor_pose_reused"]
            for row in rows
            for item in row["representative_driver_mapping"]
        ),
        "all_socket_identity_counts_preserved": all(
            row["selected_vertices"] == 52
            and row["selected_triangles"] == 72
            and row["fixed_vertices"] == 338
            for row in rows
        ),
        "no_wind_motion_claim": not claim_wind_motion,
        "no_physical_wind_claim": not claim_physical_wind,
        "no_animation_acceptance_claim": not claim_animation_acceptance,
        "no_runtime_acceptance_claim": not claim_runtime_acceptance,
        "no_simultaneous_motion_claim": not claim_simultaneous_motion,
    }
    if not all(checks.values()):
        raise ValueError("shared driver polarity binding checks failed")

    return {
        "schema": SCHEMA,
        "result": RESULT,
        "lineage": {
            "rigging_predecessor_head": RIGGING_PREDECESSOR_HEAD,
            "rigging_predecessor_result": rigging_family.RESULT,
            "vfx_donor_head": VFX_DONOR_HEAD,
            "vfx_contract_path": VFX_CONTRACT_PATH,
            "vfx_contract_blob": VFX_CONTRACT_BLOB,
            "vfx_module_path": VFX_MODULE_PATH,
            "vfx_module_blob": VFX_MODULE_BLOB,
            "organic_source_owner_head": rigging_family.SOURCE_OWNER_HEAD,
            "geometry_receiver_head": rigging_family.GEOMETRY_RECEIVER_HEAD,
            "source_digest": rigging_family.EXPECTED_SOURCE_DIGEST,
            "migrated_mesh_digest": rigging_family.EXPECTED_MIGRATED_MESH_DIGEST,
        },
        "binding": {
            "branch_ids": list(BRANCH_IDS),
            "command_sign_multiplier_by_branch": dict(COMMAND_SIGN_MULTIPLIER),
            "vfx_review_only_preferred_local_angle_deg_by_branch": dict(
                VFX_REVIEW_ONLY_PREFERRED_LOCAL_ANGLE_DEG
            ),
            "representative_shared_driver_deg": list(drivers),
            "sockets": rows,
        },
        "continuous_mapping": continuous_mapping,
        "checks": checks,
        "truth_boundary": {
            "vfx_or_weather_motion_adopted": False,
            "physical_wind_claimed": False,
            "source_or_biological_rom_claimed": False,
            "animation_timing_interpolation_or_playback_claimed": False,
            "technical_art_target_host_acceptance_claimed": False,
            "runtime_controller_or_device_claimed": False,
            "simultaneous_multi_branch_motion_claimed": False,
            "collision_or_self_intersection_claimed": False,
            "art_direction_or_visual_qa_acceptance_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }

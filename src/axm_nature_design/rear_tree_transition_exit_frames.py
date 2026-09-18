"""Source-owned neutral transition exit frames for the east/rear Nature tree.

This observer extends the existing neutral radial-transition measurement with a local
source-space frame at each first-segment exit boundary.  It measures only authored
centerlines/radii plus the already-derived neutral exit point.  The frame is intended
as a precise Geometry handoff; it is not a weld ring, skinning frame, joint frame,
biological attachment axis, deformation policy, or runtime representation.
"""
from __future__ import annotations

import math

from axm_nature_design.rear_tree_root_transition_readiness import evaluate as evaluate_transitions

SCHEMA = "axm.nature-neutral-branch-transition-exit-frame/v0.1"
EXPECTED_TRANSITION_STATE = "PASS_EXACT_NEUTRAL_BRANCH_TRANSITION_ENVELOPES__CONNECTED_TOPOLOGY_HELD"
TOLERANCE = 1e-9


def _sub(a, b):
    return [float(a[i]) - float(b[i]) for i in range(3)]


def _add_scaled(*terms):
    out = [0.0, 0.0, 0.0]
    for scalar, vector in terms:
        for i in range(3):
            out[i] += float(scalar) * float(vector[i])
    return out


def _dot(a, b):
    return sum(float(a[i]) * float(b[i]) for i in range(3))


def _cross(a, b):
    return [
        float(a[1]) * float(b[2]) - float(a[2]) * float(b[1]),
        float(a[2]) * float(b[0]) - float(a[0]) * float(b[2]),
        float(a[0]) * float(b[1]) - float(a[1]) * float(b[0]),
    ]


def _length(vector):
    return math.sqrt(_dot(vector, vector))


def _normalize(vector, label):
    size = _length(vector)
    if size <= 1e-12:
        raise ValueError(f"{label} must have nonzero length")
    return [float(value) / size for value in vector]


def _finite_vector(vector):
    return isinstance(vector, list) and len(vector) == 3 and all(math.isfinite(float(v)) for v in vector)


def _trunk_segment(source: dict, segment_id: str):
    trunk = source.get("trunk", [])
    matches = []
    for index in range(len(trunk) - 1):
        start = trunk[index]
        end = trunk[index + 1]
        if f"{start.get('id')}->{end.get('id')}" == segment_id:
            matches.append((start, end))
    if len(matches) != 1:
        raise ValueError(f"transition frame requires exactly one trunk segment {segment_id}")
    return matches[0]


def _branch(source: dict, branch_id: str):
    matches = [branch for branch in source.get("branches", []) if branch.get("id") == branch_id]
    if len(matches) != 1:
        raise ValueError(f"transition frame requires exactly one branch {branch_id}")
    return matches[0]


def evaluate(source: dict) -> dict:
    transitions = evaluate_transitions(source)
    if transitions.get("state") != EXPECTED_TRANSITION_STATE:
        raise ValueError("transition exit frames require exact neutral first-segment exit boundaries")

    frames = []
    for transition in transitions["branches"]:
        branch_id = transition["branch_id"]
        branch = _branch(source, branch_id)
        boundary = transition.get("first_full_radius_exit_boundary")
        if boundary is None:
            raise ValueError(f"branch {branch_id} has no neutral transition exit boundary")

        start, end = _trunk_segment(source, boundary["nearest_trunk_segment"])
        branch_tangent = _normalize(
            _sub(branch["points"][1], branch["points"][0]),
            f"branch {branch_id} first-segment tangent",
        )
        trunk_tangent = _normalize(
            _sub(end["position"], start["position"]),
            f"trunk segment {boundary['nearest_trunk_segment']} tangent",
        )
        radial_delta = _sub(boundary["point_m"], boundary["nearest_trunk_centerline_point_m"])
        radial_distance = _length(radial_delta)
        if abs(radial_distance - float(boundary["centerline_distance_m"])) > TOLERANCE:
            raise ValueError(f"branch {branch_id} exit radial distance disagrees with transition owner")
        radial = _normalize(radial_delta, f"branch {branch_id} exit radial vector")
        azimuth = _normalize(_cross(trunk_tangent, radial), f"branch {branch_id} exit azimuth")

        radial_orthogonality = abs(_dot(trunk_tangent, radial))
        if radial_orthogonality > TOLERANCE:
            raise ValueError(f"branch {branch_id} exit radial vector is not orthogonal to local trunk segment")

        axial_component = _dot(branch_tangent, trunk_tangent)
        radial_component = _dot(branch_tangent, radial)
        azimuthal_component = _dot(branch_tangent, azimuth)
        reconstructed = _add_scaled(
            (axial_component, trunk_tangent),
            (radial_component, radial),
            (azimuthal_component, azimuth),
        )
        reconstruction_error = _length(_sub(branch_tangent, reconstructed))
        if reconstruction_error > TOLERANCE:
            raise ValueError(f"branch {branch_id} tangent decomposition does not close")

        frame_orthogonality_error = max(
            abs(_dot(trunk_tangent, radial)),
            abs(_dot(trunk_tangent, azimuth)),
            abs(_dot(radial, azimuth)),
        )
        frame_unit_length_error = max(
            abs(_length(trunk_tangent) - 1.0),
            abs(_length(radial) - 1.0),
            abs(_length(azimuth) - 1.0),
        )
        departure_angle_deg = math.degrees(
            math.acos(max(-1.0, min(1.0, axial_component)))
        )

        frame = {
            "branch_id": branch_id,
            "exact_root_flex_zone_id": transition["exact_root_flex_zone_id"],
            "exact_root_flex_zone_status": transition["exact_root_flex_zone_status"],
            "transition_u": float(boundary["u"]),
            "transition_length_along_first_segment_m": float(
                transition["embedded_length_along_first_segment_m"]
            ),
            "exit_center_m": [float(v) for v in boundary["point_m"]],
            "exit_branch_radius_m": float(boundary["branch_radius_m"]),
            "nearest_trunk_segment": boundary["nearest_trunk_segment"],
            "nearest_trunk_segment_t": float(boundary["nearest_trunk_segment_t"]),
            "nearest_trunk_centerline_point_m": [
                float(v) for v in boundary["nearest_trunk_centerline_point_m"]
            ],
            "exit_centerline_distance_m": float(boundary["centerline_distance_m"]),
            "exit_local_trunk_radius_m": float(boundary["local_trunk_radius_m"]),
            "boundary_residual_m": float(boundary["boundary_residual_m"]),
            "branch_first_segment_tangent_unit": branch_tangent,
            "local_trunk_tangent_unit": trunk_tangent,
            "trunk_centerline_to_exit_radial_unit": radial,
            "exit_azimuth_unit": azimuth,
            "branch_tangent_components_in_exit_frame": {
                "axial_along_trunk": axial_component,
                "radial_away_from_trunk_centerline": radial_component,
                "azimuthal_around_trunk": azimuthal_component,
            },
            "branch_vs_local_trunk_departure_angle_deg": departure_angle_deg,
            "frame_orthogonality_max_abs_dot": frame_orthogonality_error,
            "frame_unit_length_max_error": frame_unit_length_error,
            "branch_tangent_reconstruction_error": reconstruction_error,
        }
        vectors = [
            frame["exit_center_m"],
            frame["nearest_trunk_centerline_point_m"],
            branch_tangent,
            trunk_tangent,
            radial,
            azimuth,
        ]
        if not all(_finite_vector(vector) for vector in vectors):
            raise ValueError(f"branch {branch_id} transition frame contains non-finite vector data")
        frames.append(frame)

    departure_angles = [row["branch_vs_local_trunk_departure_angle_deg"] for row in frames]
    max_orthogonality_error = max(row["frame_orthogonality_max_abs_dot"] for row in frames)
    max_reconstruction_error = max(row["branch_tangent_reconstruction_error"] for row in frames)

    return {
        "schema": SCHEMA,
        "study_id": source.get("study_id"),
        "state": "PASS_EXACT_NEUTRAL_BRANCH_TRANSITION_EXIT_FRAMES__CONNECTED_TOPOLOGY_HELD",
        "transition_owner_schema": transitions["schema"],
        "branch_count": len(frames),
        "frames": frames,
        "minimum_departure_angle_deg": min(departure_angles),
        "maximum_departure_angle_deg": max(departure_angles),
        "maximum_frame_orthogonality_error": max_orthogonality_error,
        "maximum_branch_tangent_reconstruction_error": max_reconstruction_error,
        "checks": {
            "all_five_primary_branch_exit_frames_measured": len(frames) == 5,
            "all_frames_use_exact_transition_owner_boundaries": all(
                row["transition_u"] > 0.0 and row["transition_u"] < 1.0 for row in frames
            ),
            "all_exit_frames_orthonormal_within_tolerance": max_orthogonality_error <= TOLERANCE,
            "all_branch_tangent_decompositions_close": max_reconstruction_error <= TOLERANCE,
            "all_root_flex_declarations_remain_unproven": all(
                row["exact_root_flex_zone_status"] == "DECLARED_NOT_DEFORMATION_TESTED"
                for row in frames
            ),
        },
        "handoff": {
            "organic_claim": "AUTHORED_NEUTRAL_TRANSITION_EXIT_FRAME_ONLY",
            "connected_topology_state": "HELD_FOR_GEOMETRY",
            "frame_is_weld_ring": False,
            "frame_is_skinning_or_joint_frame": False,
            "source_compensation_authorized": False,
        },
        "truth_boundary": {
            "authored_centerlines_and_radii_measured": True,
            "existing_transition_owner_reused": True,
            "source_geometry_changed": False,
            "generated_mesh_connectivity_inspected": False,
            "connected_branch_trunk_topology_proven": False,
            "junction_strategy_selected": False,
            "deformation_simulated": False,
            "rigging_hierarchy_or_weights_inferred": False,
            "biological_attachment_or_rom_claimed": False,
            "runtime_readiness_claimed": False,
        },
    }

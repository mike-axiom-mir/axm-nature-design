"""Deterministic owner-backed transition-frame parameters for the east/rear Nature tree.

Organic Form owns the authored neutral source-form exit frames. Procedural Design only
canonicalizes those exact owner frames into a stable right-handed parameter convention
that repeated Geometry / Geometry-Nodes experiments can consume without re-copying
origins or basis vectors. This family does not choose a junction topology, weld ring,
surface normal, rigging frame, weights, deformation policy, or downstream adoption.
"""
from __future__ import annotations

import hashlib
import json
import math

SCHEMA = "axm.nature-branch-transition-frame-parameter-family/v0.1"
OWNER_REPORT_SCHEMA = "axm.nature-neutral-branch-transition-exit-frame/v0.1"
OWNER_PASS_STATE = "PASS_EXACT_NEUTRAL_BRANCH_TRANSITION_EXIT_FRAMES__CONNECTED_TOPOLOGY_HELD"
OWNER_TRANSITION_SCHEMA = "axm.nature-neutral-branch-transition-envelope/v0.1"
PREDECESSOR_PARAMETER_SCHEMA = "axm.nature-branch-transition-parameter-family/v0.1"
RELATION = (
    "DERIVED_OWNER_EXIT_FRAMES_AS_RIGHT_HANDED_PARAMETER_TRANSFORMS_ONLY_"
    "NOT_WELD_SURFACE_NORMAL_RIGGING_WEIGHT_OR_DOWNSTREAM_AUTHORITY"
)
FRAME_CONVENTION = (
    "RIGHT_HANDED_X_RADIAL_AWAY_FROM_TRUNK__Y_AZIMUTH_CROSS_TRUNK_RADIAL__"
    "Z_LOCAL_TRUNK_TANGENT__ORIGIN_AT_OWNER_EXIT_CENTER"
)
TOLERANCE = 1e-9
SCALAR_TOLERANCE = 1e-12


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _finite(value: object, label: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite")
    return number


def _vec3(value: object, label: str) -> list[float]:
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError(f"{label} must be a three-component list")
    return [_finite(component, label) for component in value]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(a[index] * b[index] for index in range(3))


def _cross(a: list[float], b: list[float]) -> list[float]:
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def _length(value: list[float]) -> float:
    return math.sqrt(_dot(value, value))


def _sub(a: list[float], b: list[float]) -> list[float]:
    return [a[index] - b[index] for index in range(3)]


def _add_scaled(*terms: tuple[float, list[float]]) -> list[float]:
    result = [0.0, 0.0, 0.0]
    for scalar, vector in terms:
        for index in range(3):
            result[index] += scalar * vector[index]
    return result


def _require_unit(value: list[float], label: str) -> None:
    if abs(_length(value) - 1.0) > TOLERANCE:
        raise ValueError(f"{label} must be unit length")


def _require_hex_digest(value: object, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{label} must be a sha256 hex digest")
    if any(character not in "0123456789abcdef" for character in value):
        raise ValueError(f"{label} must be lowercase hexadecimal")
    return value


def validate_contract(contract: dict) -> None:
    if contract.get("schema") != SCHEMA:
        raise ValueError("unsupported branch transition frame family schema")
    if contract.get("owner_report_schema") != OWNER_REPORT_SCHEMA:
        raise ValueError("owner exit-frame report schema drift")
    if contract.get("predecessor_transition_family_schema") != PREDECESSOR_PARAMETER_SCHEMA:
        raise ValueError("predecessor transition family schema drift")
    _require_hex_digest(
        contract.get("predecessor_transition_family_digest"),
        "predecessor transition family digest",
    )
    if contract.get("relation") != RELATION:
        raise ValueError("branch transition frame family relation drift")
    if contract.get("frame_convention") != FRAME_CONVENTION:
        raise ValueError("branch transition frame convention drift")

    branch_ids = contract.get("authorized_branch_ids")
    if not isinstance(branch_ids, list) or len(branch_ids) < 3:
        raise ValueError("at least three authorized branch identities required")
    if any(not isinstance(branch_id, str) or not branch_id for branch_id in branch_ids):
        raise ValueError("authorized branch identities must be non-empty strings")
    if len(set(branch_ids)) != len(branch_ids):
        raise ValueError("authorized branch identities must be unique")

    expected = contract.get("expected_transitions")
    if not isinstance(expected, dict) or set(expected) != set(branch_ids):
        raise ValueError("expected transition identities must exactly match authorized branches")
    for branch_id, row in expected.items():
        if not isinstance(row, dict):
            raise ValueError(f"expected transition for {branch_id} must be an object")
        fraction = _finite(row.get("transition_u"), f"{branch_id} transition u")
        length = _finite(row.get("transition_length_m"), f"{branch_id} transition length")
        if not 0.0 < fraction < 1.0 or length <= 0.0:
            raise ValueError(f"{branch_id} expected transition must be inside the first segment")

    forbidden_true = (
        "source_mutation_authorized",
        "junction_strategy_authorized",
        "connected_topology_claim_authorized",
        "weld_ring_authorized",
        "surface_normal_authorized",
        "automatic_geometry_adoption",
        "automatic_rigging_adoption",
        "automatic_animation_adoption",
        "automatic_vfx_adoption",
        "automatic_technical_art_adoption",
        "automatic_runtime_adoption",
        "production_weight_authorized",
    )
    for key in forbidden_true:
        if contract.get(key) is not False:
            raise ValueError(f"authority expansion forbidden: {key}")


def _validate_owner_report(owner_report: dict, contract: dict) -> list[dict]:
    if owner_report.get("schema") != OWNER_REPORT_SCHEMA:
        raise ValueError("unexpected Organic transition exit-frame schema")
    if owner_report.get("state") != OWNER_PASS_STATE:
        raise ValueError("Organic transition exit-frame report is not in the exact bounded PASS state")
    if owner_report.get("transition_owner_schema") != OWNER_TRANSITION_SCHEMA:
        raise ValueError("Organic transition owner schema drift")

    frames = owner_report.get("frames")
    if not isinstance(frames, list):
        raise ValueError("Organic transition exit frames missing")
    if owner_report.get("branch_count") != len(contract["authorized_branch_ids"]) or len(frames) != len(contract["authorized_branch_ids"]):
        raise ValueError("Organic transition frame branch-count drift")
    observed_ids = [row.get("branch_id") for row in frames if isinstance(row, dict)]
    if len(observed_ids) != len(frames) or len(set(observed_ids)) != len(observed_ids):
        raise ValueError("Organic transition frame branch identities must be unique")
    if set(observed_ids) != set(contract["authorized_branch_ids"]):
        raise ValueError("Organic transition frame branch identity set drift")

    checks = owner_report.get("checks")
    required_checks = (
        "all_five_primary_branch_exit_frames_measured",
        "all_frames_use_exact_transition_owner_boundaries",
        "all_exit_frames_orthonormal_within_tolerance",
        "all_branch_tangent_decompositions_close",
        "all_root_flex_declarations_remain_unproven",
    )
    if not isinstance(checks, dict) or any(checks.get(key) is not True for key in required_checks):
        raise ValueError("Organic transition exit-frame checks drift")

    handoff = owner_report.get("handoff")
    if not isinstance(handoff, dict):
        raise ValueError("Organic transition exit-frame handoff missing")
    if handoff.get("organic_claim") != "AUTHORED_NEUTRAL_TRANSITION_EXIT_FRAME_ONLY":
        raise ValueError("Organic transition exit-frame claim widened")
    if handoff.get("connected_topology_state") != "HELD_FOR_GEOMETRY":
        raise ValueError("connected topology is no longer held for Geometry")
    if handoff.get("frame_is_weld_ring") is not False:
        raise ValueError("Organic exit frame promoted to a weld ring")
    if handoff.get("frame_is_skinning_or_joint_frame") is not False:
        raise ValueError("Organic exit frame promoted to a skinning or joint frame")
    if handoff.get("source_compensation_authorized") is not False:
        raise ValueError("Organic exit frame authorized source compensation")

    truth = owner_report.get("truth_boundary")
    if not isinstance(truth, dict):
        raise ValueError("Organic transition exit-frame truth boundary missing")
    if truth.get("authored_centerlines_and_radii_measured") is not True:
        raise ValueError("Organic exit-frame measurement basis missing")
    if truth.get("existing_transition_owner_reused") is not True:
        raise ValueError("Organic transition owner continuity missing")
    required_false = (
        "source_geometry_changed",
        "generated_mesh_connectivity_inspected",
        "connected_branch_trunk_topology_proven",
        "junction_strategy_selected",
        "deformation_simulated",
        "rigging_hierarchy_or_weights_inferred",
        "biological_attachment_or_rom_claimed",
        "runtime_readiness_claimed",
    )
    if any(truth.get(key) is not False for key in required_false):
        raise ValueError("Organic transition exit-frame truth boundary widened")

    expected = contract["expected_transitions"]
    for frame in frames:
        branch_id = frame["branch_id"]
        expected_row = expected[branch_id]
        transition_u = _finite(frame.get("transition_u"), f"{branch_id} transition u")
        transition_length = _finite(
            frame.get("transition_length_along_first_segment_m"),
            f"{branch_id} transition length",
        )
        if abs(transition_u - float(expected_row["transition_u"])) > SCALAR_TOLERANCE:
            raise ValueError(f"{branch_id} transition u drift from predecessor parameter family")
        if abs(transition_length - float(expected_row["transition_length_m"])) > SCALAR_TOLERANCE:
            raise ValueError(f"{branch_id} transition length drift from predecessor parameter family")
        if frame.get("exact_root_flex_zone_status") != "DECLARED_NOT_DEFORMATION_TESTED":
            raise ValueError(f"{branch_id} flex status promotion forbidden")
        if abs(_finite(frame.get("boundary_residual_m"), f"{branch_id} boundary residual")) > SCALAR_TOLERANCE:
            raise ValueError(f"{branch_id} transition boundary residual drift")

        branch_tangent = _vec3(frame.get("branch_first_segment_tangent_unit"), f"{branch_id} branch tangent")
        z_trunk = _vec3(frame.get("local_trunk_tangent_unit"), f"{branch_id} trunk tangent")
        x_radial = _vec3(frame.get("trunk_centerline_to_exit_radial_unit"), f"{branch_id} radial")
        y_azimuth = _vec3(frame.get("exit_azimuth_unit"), f"{branch_id} azimuth")
        _vec3(frame.get("exit_center_m"), f"{branch_id} exit center")
        _require_unit(branch_tangent, f"{branch_id} branch tangent")
        _require_unit(x_radial, f"{branch_id} radial")
        _require_unit(y_azimuth, f"{branch_id} azimuth")
        _require_unit(z_trunk, f"{branch_id} trunk tangent")

        if max(abs(_dot(x_radial, y_azimuth)), abs(_dot(x_radial, z_trunk)), abs(_dot(y_azimuth, z_trunk))) > TOLERANCE:
            raise ValueError(f"{branch_id} owner exit frame lost orthogonality")
        handedness = _dot(_cross(x_radial, y_azimuth), z_trunk)
        if abs(handedness - 1.0) > TOLERANCE:
            raise ValueError(f"{branch_id} owner exit frame is not right handed under the procedural convention")

        components = frame.get("branch_tangent_components_in_exit_frame")
        if not isinstance(components, dict):
            raise ValueError(f"{branch_id} branch tangent decomposition missing")
        axial = _finite(components.get("axial_along_trunk"), f"{branch_id} axial component")
        radial = _finite(
            components.get("radial_away_from_trunk_centerline"),
            f"{branch_id} radial component",
        )
        azimuthal = _finite(components.get("azimuthal_around_trunk"), f"{branch_id} azimuthal component")
        reconstructed = _add_scaled((radial, x_radial), (azimuthal, y_azimuth), (axial, z_trunk))
        if _length(_sub(branch_tangent, reconstructed)) > TOLERANCE:
            raise ValueError(f"{branch_id} branch tangent does not reconstruct in procedural XYZ convention")

        owner_departure = _finite(
            frame.get("branch_vs_local_trunk_departure_angle_deg"),
            f"{branch_id} departure angle",
        )
        reconstructed_departure = math.degrees(math.acos(max(-1.0, min(1.0, axial))))
        if abs(owner_departure - reconstructed_departure) > TOLERANCE:
            raise ValueError(f"{branch_id} departure angle disagrees with the owner tangent decomposition")

    return frames


def _matrix_from_frame(origin: list[float], x_axis: list[float], y_axis: list[float], z_axis: list[float]) -> list[list[float]]:
    return [
        [x_axis[0], y_axis[0], z_axis[0], origin[0]],
        [x_axis[1], y_axis[1], z_axis[1], origin[1]],
        [x_axis[2], y_axis[2], z_axis[2], origin[2]],
        [0.0, 0.0, 0.0, 1.0],
    ]


def assemble_transition_frame_family(owner_report: dict, contract: dict) -> dict:
    validate_contract(contract)
    frames = _validate_owner_report(owner_report, contract)

    outputs = []
    for frame in frames:
        branch_id = frame["branch_id"]
        origin = [float(value) for value in frame["exit_center_m"]]
        x_radial = [float(value) for value in frame["trunk_centerline_to_exit_radial_unit"]]
        y_azimuth = [float(value) for value in frame["exit_azimuth_unit"]]
        z_trunk = [float(value) for value in frame["local_trunk_tangent_unit"]]
        components = frame["branch_tangent_components_in_exit_frame"]
        basis_core = {
            "x_radial_away_from_trunk_unit": x_radial,
            "y_azimuth_around_trunk_unit": y_azimuth,
            "z_local_trunk_tangent_unit": z_trunk,
        }
        core = {
            "output_id": f"{branch_id}-neutral-transition-frame-parameters",
            "branch_id": branch_id,
            "frame_convention": FRAME_CONVENTION,
            "origin_exit_center_m": origin,
            "basis": basis_core,
            "local_to_source_matrix_4x4_column_basis": _matrix_from_frame(
                origin, x_radial, y_azimuth, z_trunk
            ),
            "branch_first_segment_tangent_local_xyz": [
                float(components["radial_away_from_trunk_centerline"]),
                float(components["azimuthal_around_trunk"]),
                float(components["axial_along_trunk"]),
            ],
            "transition_u": float(frame["transition_u"]),
            "transition_length_m": float(frame["transition_length_along_first_segment_m"]),
            "exit_branch_radius_m": float(frame["exit_branch_radius_m"]),
            "exit_local_trunk_radius_m": float(frame["exit_local_trunk_radius_m"]),
            "branch_vs_local_trunk_departure_angle_deg": float(
                frame["branch_vs_local_trunk_departure_angle_deg"]
            ),
            "owner_root_flex_zone_id": frame["exact_root_flex_zone_id"],
            "owner_root_flex_zone_status": frame["exact_root_flex_zone_status"],
            "origin_digest": digest(origin),
            "basis_digest": digest(basis_core),
            "source_authorized": False,
            "junction_strategy_authorized": False,
            "weld_ring_authorized": False,
            "surface_normal_authorized": False,
            "connected_topology_claim_authorized": False,
            "rigging_authorized": False,
            "production_weight_authorized": False,
            "downstream_adoption_authorized": False,
        }
        outputs.append({**core, "parameter_digest": digest(core)})

    outputs.sort(key=lambda row: row["branch_id"])
    if len({row["parameter_digest"] for row in outputs}) < 3:
        raise ValueError("transition frame family collapsed to fewer than three material outputs")
    if len({row["origin_digest"] for row in outputs}) < 3:
        raise ValueError("transition frame family collapsed to fewer than three material origins")
    if len({row["basis_digest"] for row in outputs}) < 3:
        raise ValueError("transition frame family collapsed to fewer than three material bases")

    family_core = {
        "schema": SCHEMA,
        "family_id": contract["family_id"],
        "relation": RELATION,
        "frame_convention": FRAME_CONVENTION,
        "owner_report_schema": owner_report["schema"],
        "owner_report_state": owner_report["state"],
        "predecessor_transition_family_schema": contract["predecessor_transition_family_schema"],
        "predecessor_transition_family_digest": contract["predecessor_transition_family_digest"],
        "output_count": len(outputs),
        "outputs": outputs,
        "source_authority": False,
        "geometry_junction_authority": False,
        "weld_ring_authority": False,
        "surface_normal_authority": False,
        "rigging_authority": False,
        "production_weight_authority": False,
        "animation_authority": False,
        "vfx_authority": False,
        "technical_art_authority": False,
        "runtime_authority": False,
    }
    return {**family_core, "family_digest": digest(family_core)}

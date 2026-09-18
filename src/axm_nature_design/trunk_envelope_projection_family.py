"""Topology-free tapered-trunk envelope projection family for Nature branch transitions.

Geometry owns boundary-loop topology, bridge faces, indexed trunk cuts, weld/remesh strategy,
and connected junction adoption. Procedural Design owns only the repeated deterministic math
that projects source-space samples radially onto one exact authored tapered trunk segment while
preserving each sample's axial coordinate.
"""
from __future__ import annotations

import hashlib
import json
import math

SCHEMA = "axm.nature-branch-transition-trunk-envelope-projection-family/v0.1"
PREDECESSOR_FRAME_SCHEMA = "axm.nature-branch-transition-frame-parameter-family/v0.1"
OWNER_FRAME_SCHEMA = "axm.nature-neutral-branch-transition-exit-frame/v0.1"
OWNER_FRAME_STATE = "PASS_EXACT_NEUTRAL_BRANCH_TRANSITION_EXIT_FRAMES__CONNECTED_TOPOLOGY_HELD"
RELATION = (
    "DERIVED_TOPOLOGY_FREE_TAPERED_TRUNK_ENVELOPE_PROJECTION_ONLY__"
    "NO_RING_TOPOLOGY_TRUNK_CUT_WELD_RIGGING_OR_DOWNSTREAM_AUTHORITY"
)
TOLERANCE = 1e-10


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


def _sub(a: list[float], b: list[float]) -> list[float]:
    return [a[index] - b[index] for index in range(3)]


def _add(a: list[float], b: list[float]) -> list[float]:
    return [a[index] + b[index] for index in range(3)]


def _mul(a: list[float], scalar: float) -> list[float]:
    return [value * scalar for value in a]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(a[index] * b[index] for index in range(3))


def _length(value: list[float]) -> float:
    return math.sqrt(_dot(value, value))


def _norm(value: list[float], label: str) -> list[float]:
    size = _length(value)
    if size <= 1e-18:
        raise ValueError(f"{label} must have nonzero length")
    return [component / size for component in value]


def _distance(a: list[float], b: list[float]) -> float:
    return _length(_sub(a, b))


def _require_hex(value: object, length: int, label: str) -> str:
    if not isinstance(value, str) or len(value) != length:
        raise ValueError(f"{label} must be {length}-character lowercase hexadecimal")
    if any(ch not in "0123456789abcdef" for ch in value):
        raise ValueError(f"{label} must be lowercase hexadecimal")
    return value


def validate_contract(contract: dict) -> None:
    if contract.get("schema") != SCHEMA:
        raise ValueError("unsupported trunk-envelope projection family schema")
    if contract.get("predecessor_frame_family_schema") != PREDECESSOR_FRAME_SCHEMA:
        raise ValueError("predecessor frame family schema drift")
    _require_hex(contract.get("predecessor_frame_family_digest"), 64, "predecessor frame family digest")
    _require_hex(contract.get("organic_source_digest"), 64, "Organic source digest")
    if contract.get("relation") != RELATION:
        raise ValueError("trunk-envelope projection relation drift")
    branch_ids = contract.get("authorized_branch_ids")
    if not isinstance(branch_ids, list) or len(branch_ids) < 3:
        raise ValueError("at least three authorized branch identities required")
    if any(not isinstance(branch_id, str) or not branch_id for branch_id in branch_ids):
        raise ValueError("authorized branch identities must be non-empty strings")
    if len(set(branch_ids)) != len(branch_ids):
        raise ValueError("authorized branch identities must be unique")
    donor = contract.get("geometry_reference")
    if not isinstance(donor, dict):
        raise ValueError("Geometry reference provenance missing")
    _require_hex(donor.get("head"), 40, "Geometry reference head")
    _require_hex(donor.get("module_blob"), 40, "Geometry reference module blob")
    if donor.get("branch_id") not in branch_ids:
        raise ValueError("Geometry reference branch must be one authorized branch")
    if not isinstance(donor.get("module_path"), str) or not donor["module_path"]:
        raise ValueError("Geometry reference module path missing")
    forbidden = (
        "source_mutation_authorized",
        "ring_topology_authorized",
        "bridge_topology_authorized",
        "indexed_trunk_cut_authorized",
        "connected_junction_authorized",
        "weld_or_remesh_authorized",
        "surface_normal_authorized",
        "automatic_geometry_adoption",
        "automatic_rigging_adoption",
        "automatic_animation_adoption",
        "automatic_vfx_adoption",
        "automatic_technical_art_adoption",
        "automatic_runtime_adoption",
        "production_weight_authorized",
    )
    for key in forbidden:
        if contract.get(key) is not False:
            raise ValueError(f"authority expansion forbidden: {key}")


def _trunk_segment(source: dict, segment_id: str) -> tuple[dict, dict]:
    trunk = source.get("trunk")
    if not isinstance(trunk, list):
        raise ValueError("source trunk missing")
    matches = []
    for index in range(len(trunk) - 1):
        start = trunk[index]
        end = trunk[index + 1]
        if f"{start.get('id')}->{end.get('id')}" == segment_id:
            matches.append((start, end))
    if len(matches) != 1:
        raise ValueError(f"expected exactly one trunk segment {segment_id}")
    return matches[0]


def project_point_to_tapered_trunk(source: dict, segment_id: str, point_m: object) -> dict:
    """Project one source-space point radially to a tapered trunk segment envelope.

    The point keeps its axial coordinate along the exact segment. No topology or adoption
    semantics are inferred by this math primitive.
    """
    point = _vec3(point_m, "projection point")
    start, end = _trunk_segment(source, segment_id)
    start_pos = _vec3(start.get("position"), "trunk segment start")
    end_pos = _vec3(end.get("position"), "trunk segment end")
    start_radius = _finite(start.get("radius"), "trunk start radius")
    end_radius = _finite(end.get("radius"), "trunk end radius")
    if start_radius <= 0.0 or end_radius <= 0.0:
        raise ValueError("trunk radii must be positive")

    axis_delta = _sub(end_pos, start_pos)
    segment_length = _length(axis_delta)
    if segment_length <= 1e-18:
        raise ValueError("zero-length trunk segment")
    axis = _norm(axis_delta, "trunk segment axis")
    axial_distance = _dot(_sub(point, start_pos), axis)
    segment_t = axial_distance / segment_length
    if segment_t < -TOLERANCE or segment_t > 1.0 + TOLERANCE:
        raise ValueError("projection point falls outside exact local trunk segment")
    segment_t = max(0.0, min(1.0, segment_t))
    center = _add(start_pos, _mul(axis, segment_t * segment_length))
    local_radius = start_radius + segment_t * (end_radius - start_radius)
    radial = _sub(point, center)
    input_radial_distance = _length(radial)
    if input_radial_distance <= 1e-18:
        raise ValueError("projection point lies on trunk centerline")
    surface = _add(center, _mul(_norm(radial, "projection radial"), local_radius))

    projected_axial_distance = _dot(_sub(surface, start_pos), axis)
    axial_residual = abs(projected_axial_distance - axial_distance)
    surface_residual = abs(_distance(surface, center) - local_radius)
    return {
        "segment_id": segment_id,
        "segment_t": segment_t,
        "centerline_point_m": center,
        "local_radius_m": local_radius,
        "input_point_m": point,
        "input_radial_distance_m": input_radial_distance,
        "surface_point_m": surface,
        "surface_residual_m": surface_residual,
        "axial_coordinate_residual_m": axial_residual,
        "projection_span_m": _distance(point, surface),
    }


def project_points_to_tapered_trunk(source: dict, segment_id: str, points_m: list[object]) -> list[dict]:
    if not isinstance(points_m, list) or not points_m:
        raise ValueError("at least one projection point required")
    return [project_point_to_tapered_trunk(source, segment_id, point) for point in points_m]


def _validate_inputs(source: dict, owner_report: dict, predecessor_family: dict, contract: dict) -> tuple[dict, dict]:
    validate_contract(contract)
    if digest(source) != contract["organic_source_digest"]:
        raise ValueError("exact Organic source digest drift")
    if owner_report.get("schema") != OWNER_FRAME_SCHEMA or owner_report.get("state") != OWNER_FRAME_STATE:
        raise ValueError("exact Organic transition-frame owner state drift")
    frames = owner_report.get("frames")
    if not isinstance(frames, list):
        raise ValueError("Organic transition frames missing")
    frame_map = {row.get("branch_id"): row for row in frames if isinstance(row, dict)}
    if len(frame_map) != len(frames) or set(frame_map) != set(contract["authorized_branch_ids"]):
        raise ValueError("Organic transition-frame branch identity drift")

    if predecessor_family.get("schema") != PREDECESSOR_FRAME_SCHEMA:
        raise ValueError("predecessor frame family schema mismatch")
    if predecessor_family.get("family_digest") != contract["predecessor_frame_family_digest"]:
        raise ValueError("predecessor frame family digest drift")
    outputs = predecessor_family.get("outputs")
    if not isinstance(outputs, list):
        raise ValueError("predecessor frame family outputs missing")
    output_map = {row.get("branch_id"): row for row in outputs if isinstance(row, dict)}
    if len(output_map) != len(outputs) or set(output_map) != set(contract["authorized_branch_ids"]):
        raise ValueError("predecessor frame-family branch identity drift")

    for branch_id in contract["authorized_branch_ids"]:
        owner = frame_map[branch_id]
        predecessor = output_map[branch_id]
        if _distance(
            _vec3(owner.get("exit_center_m"), f"{branch_id} owner exit center"),
            _vec3(predecessor.get("origin_exit_center_m"), f"{branch_id} predecessor origin"),
        ) > TOLERANCE:
            raise ValueError(f"{branch_id} predecessor origin no longer matches Organic owner")
        if abs(_finite(owner.get("exit_branch_radius_m"), "owner branch radius") - _finite(predecessor.get("exit_branch_radius_m"), "predecessor branch radius")) > TOLERANCE:
            raise ValueError(f"{branch_id} predecessor branch radius drift")
        if predecessor.get("downstream_adoption_authorized") is not False:
            raise ValueError(f"{branch_id} predecessor frame family widened downstream authority")
    return frame_map, output_map


def assemble_trunk_envelope_projection_family(
    source: dict,
    owner_report: dict,
    predecessor_frame_family: dict,
    contract: dict,
) -> dict:
    frame_map, predecessor_map = _validate_inputs(source, owner_report, predecessor_frame_family, contract)
    outputs = []
    for branch_id in contract["authorized_branch_ids"]:
        owner = frame_map[branch_id]
        predecessor = predecessor_map[branch_id]
        center = _vec3(owner["exit_center_m"], f"{branch_id} exit center")
        azimuth = _vec3(predecessor["basis"]["y_azimuth_around_trunk_unit"], f"{branch_id} azimuth")
        branch_radius = _finite(owner["exit_branch_radius_m"], f"{branch_id} exit branch radius")
        segment_id = owner.get("nearest_trunk_segment")
        if not isinstance(segment_id, str) or not segment_id:
            raise ValueError(f"{branch_id} nearest trunk segment missing")
        sample_points = [
            center,
            _add(center, _mul(azimuth, branch_radius)),
            _add(center, _mul(azimuth, -branch_radius)),
        ]
        samples = project_points_to_tapered_trunk(source, segment_id, sample_points)
        center_sample = samples[0]
        owner_t = _finite(owner.get("nearest_trunk_segment_t"), f"{branch_id} owner trunk segment t")
        owner_trunk_radius = _finite(owner.get("exit_local_trunk_radius_m"), f"{branch_id} owner trunk radius")
        if abs(center_sample["segment_t"] - owner_t) > TOLERANCE:
            raise ValueError(f"{branch_id} projected center axial coordinate drift")
        if abs(center_sample["local_radius_m"] - owner_trunk_radius) > TOLERANCE:
            raise ValueError(f"{branch_id} projected center trunk radius drift")
        if abs(center_sample["projection_span_m"] - branch_radius) > TOLERANCE:
            raise ValueError(f"{branch_id} neutral center projection span no longer equals branch radius")
        if max(row["surface_residual_m"] for row in samples) > TOLERANCE:
            raise ValueError(f"{branch_id} projection leaves tapered trunk envelope")
        if max(row["axial_coordinate_residual_m"] for row in samples) > TOLERANCE:
            raise ValueError(f"{branch_id} projection changes axial coordinate")

        core = {
            "output_id": f"{branch_id}-transition-trunk-envelope-projection",
            "branch_id": branch_id,
            "trunk_segment_id": segment_id,
            "owner_segment_t": owner_t,
            "owner_exit_branch_radius_m": branch_radius,
            "owner_exit_local_trunk_radius_m": owner_trunk_radius,
            "sample_semantics": ["exit-center", "exit-center-plus-azimuth-radius", "exit-center-minus-azimuth-radius"],
            "samples": samples,
            "topology_authored": False,
            "ring_identity_authored": False,
            "bridge_faces_authored": False,
            "indexed_trunk_cut_authorized": False,
            "connected_junction_authorized": False,
            "weld_or_remesh_authorized": False,
            "rigging_authorized": False,
            "production_weight_authorized": False,
            "downstream_adoption_authorized": False,
        }
        outputs.append({**core, "projection_digest": digest(core)})

    outputs.sort(key=lambda row: row["branch_id"])
    if len({row["projection_digest"] for row in outputs}) < 3:
        raise ValueError("projection family collapsed to fewer than three materially different outputs")
    surface_identities = {digest([sample["surface_point_m"] for sample in row["samples"]]) for row in outputs}
    if len(surface_identities) < 3:
        raise ValueError("projection family collapsed to fewer than three materially different surface outputs")

    family_core = {
        "schema": SCHEMA,
        "family_id": contract["family_id"],
        "relation": RELATION,
        "predecessor_frame_family_schema": PREDECESSOR_FRAME_SCHEMA,
        "predecessor_frame_family_digest": predecessor_frame_family["family_digest"],
        "geometry_reference": contract["geometry_reference"],
        "output_count": len(outputs),
        "outputs": outputs,
        "source_authority": False,
        "geometry_ring_topology_authority": False,
        "geometry_bridge_topology_authority": False,
        "indexed_trunk_cut_authority": False,
        "connected_junction_authority": False,
        "weld_or_remesh_authority": False,
        "surface_normal_authority": False,
        "rigging_authority": False,
        "animation_authority": False,
        "vfx_authority": False,
        "technical_art_authority": False,
        "runtime_authority": False,
    }
    return {**family_core, "family_digest": digest(family_core)}

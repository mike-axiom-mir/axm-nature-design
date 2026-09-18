"""Topology-free regular indexed tapered-shell projection family for Nature branch transitions.

Geometry owns indexed receiver triangle membership, opening-loop topology, bridge faces, trunk cuts,
weld/remesh strategy, and connected junction adoption. Procedural Design owns only the repeated
deterministic math that preserves axial position and intersects a radial ray with an exact regular
N-sided tapered shell cross-section.
"""
from __future__ import annotations

import hashlib
import json
import math

SCHEMA = "axm.nature-branch-transition-indexed-trunk-envelope-projection-family/v0.1"
PREDECESSOR_SCHEMA = "axm.nature-branch-transition-trunk-envelope-projection-family/v0.1"
RELATION = (
    "DERIVED_TOPOLOGY_FREE_REGULAR_INDEXED_TRUNK_ENVELOPE_PROJECTION_ONLY__"
    "NO_TRIANGLE_MEMBERSHIP_RING_TOPOLOGY_TRUNK_CUT_WELD_RIGGING_OR_DOWNSTREAM_AUTHORITY"
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


def _add(a: list[float], b: list[float]) -> list[float]:
    return [a[index] + b[index] for index in range(3)]


def _sub(a: list[float], b: list[float]) -> list[float]:
    return [a[index] - b[index] for index in range(3)]


def _mul(a: list[float], scalar: float) -> list[float]:
    return [value * scalar for value in a]


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


def _norm(value: list[float], label: str) -> list[float]:
    size = _length(value)
    if size <= 1e-18:
        raise ValueError(f"{label} must have nonzero length")
    return [component / size for component in value]


def _distance(a: list[float], b: list[float]) -> float:
    return _length(_sub(a, b))


def _cross2(a: list[float], b: list[float]) -> float:
    return a[0] * b[1] - a[1] * b[0]


def _require_hex(value: object, length: int, label: str) -> str:
    if not isinstance(value, str) or len(value) != length:
        raise ValueError(f"{label} must be {length}-character lowercase hexadecimal")
    if any(ch not in "0123456789abcdef" for ch in value):
        raise ValueError(f"{label} must be lowercase hexadecimal")
    return value


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


def _frame(start_pos: list[float], end_pos: list[float]) -> tuple[list[float], list[float], list[float]]:
    axis = _norm(_sub(end_pos, start_pos), "trunk segment axis")
    reference = [0.0, 0.0, 1.0]
    if abs(_dot(axis, reference)) > 0.94:
        reference = [1.0, 0.0, 0.0]
    u_axis = _norm(_cross(axis, reference), "trunk cross-section u axis")
    v_axis = _norm(_cross(axis, u_axis), "trunk cross-section v axis")
    return axis, u_axis, v_axis


def project_point_to_regular_tapered_shell(
    source: dict,
    segment_id: str,
    point_m: object,
    *,
    side_count: int,
    phase_rad: float = 0.0,
) -> dict:
    """Project one point radially to a regular N-sided tapered shell without authoring topology."""
    if isinstance(side_count, bool) or not isinstance(side_count, int) or side_count < 3:
        raise ValueError("regular indexed shell side_count must be an integer >= 3")
    phase = _finite(phase_rad, "regular indexed shell phase")
    point = _vec3(point_m, "projection point")
    start, end = _trunk_segment(source, segment_id)
    start_pos = _vec3(start.get("position"), "trunk segment start")
    end_pos = _vec3(end.get("position"), "trunk segment end")
    start_radius = _finite(start.get("radius"), "trunk start radius")
    end_radius = _finite(end.get("radius"), "trunk end radius")
    if start_radius <= 0.0 or end_radius <= 0.0:
        raise ValueError("trunk radii must be positive")

    axis, u_axis, v_axis = _frame(start_pos, end_pos)
    axis_delta = _sub(end_pos, start_pos)
    segment_length = _length(axis_delta)
    if segment_length <= 1e-18:
        raise ValueError("zero-length trunk segment")
    axial_distance = _dot(_sub(point, start_pos), axis)
    segment_t = axial_distance / segment_length
    if segment_t < -TOLERANCE or segment_t > 1.0 + TOLERANCE:
        raise ValueError("projection point falls outside exact local trunk segment")
    segment_t = max(0.0, min(1.0, segment_t))
    center = _add(start_pos, _mul(axis, segment_t * segment_length))
    radius = start_radius + segment_t * (end_radius - start_radius)

    radial = _sub(point, center)
    input_radial_distance = _length(radial)
    if input_radial_distance <= 1e-18:
        raise ValueError("projection point lies on trunk centerline")
    x = _dot(radial, u_axis)
    y = _dot(radial, v_axis)
    theta = math.atan2(y, x)
    theta_tau = theta % math.tau
    step = math.tau / side_count
    relative_theta = (theta_tau - phase) % math.tau
    cell = int(math.floor(relative_theta / step)) % side_count
    angle_a = phase + cell * step
    angle_b = phase + (cell + 1) * step

    ray = [math.cos(theta_tau), math.sin(theta_tau)]
    edge_a = [radius * math.cos(angle_a), radius * math.sin(angle_a)]
    edge_b = [radius * math.cos(angle_b), radius * math.sin(angle_b)]
    edge = [edge_b[0] - edge_a[0], edge_b[1] - edge_a[1]]
    denominator = _cross2(ray, edge)
    if abs(denominator) <= 1e-14:
        raise ValueError("radial ray parallel to indexed shell side")
    radial_distance = _cross2(edge_a, edge) / denominator
    edge_lambda = _cross2(edge_a, ray) / denominator
    if radial_distance <= 0.0 or edge_lambda < -TOLERANCE or edge_lambda > 1.0 + TOLERANCE:
        raise ValueError("indexed shell side intersection lies outside exact side")

    surface = _add(
        center,
        _add(
            _mul(u_axis, radial_distance * math.cos(theta_tau)),
            _mul(v_axis, radial_distance * math.sin(theta_tau)),
        ),
    )
    projected_axial_distance = _dot(_sub(surface, start_pos), axis)
    axial_residual = abs(projected_axial_distance - axial_distance)
    side_point_2d = [radial_distance * math.cos(theta_tau), radial_distance * math.sin(theta_tau)]
    edge_residual = abs(
        _cross2(
            [side_point_2d[0] - edge_a[0], side_point_2d[1] - edge_a[1]],
            edge,
        )
    ) / max(math.hypot(edge[0], edge[1]), 1e-18)

    return {
        "segment_id": segment_id,
        "side_count": side_count,
        "phase_rad": phase,
        "segment_t": segment_t,
        "centerline_point_m": center,
        "theta_rad": theta,
        "theta_tau_rad": theta_tau,
        "side_cell": cell,
        "side_edge_lambda": edge_lambda,
        "local_radius_m": radius,
        "input_point_m": point,
        "input_radial_distance_m": input_radial_distance,
        "indexed_radial_distance_m": radial_distance,
        "surface_point_m": surface,
        "surface_edge_residual_m": edge_residual,
        "axial_coordinate_residual_m": axial_residual,
        "projection_span_m": _distance(point, surface),
        "analytic_to_indexed_radial_delta_m": abs(radius - radial_distance),
    }


def project_points_to_regular_tapered_shell(
    source: dict,
    segment_id: str,
    points_m: list[object],
    *,
    side_count: int,
    phase_rad: float = 0.0,
) -> list[dict]:
    if not isinstance(points_m, list) or not points_m:
        raise ValueError("at least one projection point required")
    return [
        project_point_to_regular_tapered_shell(
            source,
            segment_id,
            point,
            side_count=side_count,
            phase_rad=phase_rad,
        )
        for point in points_m
    ]


def validate_contract(contract: dict) -> None:
    if contract.get("schema") != SCHEMA:
        raise ValueError("unsupported indexed trunk-envelope projection family schema")
    if contract.get("predecessor_projection_family_schema") != PREDECESSOR_SCHEMA:
        raise ValueError("predecessor projection family schema drift")
    _require_hex(
        contract.get("predecessor_projection_family_digest"),
        64,
        "predecessor projection family digest",
    )
    _require_hex(contract.get("organic_source_digest"), 64, "Organic source digest")
    if contract.get("relation") != RELATION:
        raise ValueError("indexed trunk-envelope projection relation drift")
    branch_ids = contract.get("authorized_branch_ids")
    if not isinstance(branch_ids, list) or len(branch_ids) < 3:
        raise ValueError("at least three authorized branch identities required")
    if any(not isinstance(branch_id, str) or not branch_id for branch_id in branch_ids):
        raise ValueError("authorized branch identities must be non-empty strings")
    if len(set(branch_ids)) != len(branch_ids):
        raise ValueError("authorized branch identities must be unique")
    side_count = contract.get("receiver_side_count")
    if isinstance(side_count, bool) or not isinstance(side_count, int) or side_count < 3:
        raise ValueError("receiver_side_count must be an integer >= 3")
    phase = _finite(contract.get("receiver_phase_rad"), "receiver phase")

    reference = contract.get("geometry_reference")
    if not isinstance(reference, dict):
        raise ValueError("Geometry indexed-surface reference provenance missing")
    _require_hex(reference.get("head"), 40, "Geometry reference head")
    _require_hex(reference.get("module_blob"), 40, "Geometry reference module blob")
    if reference.get("branch_id") not in branch_ids:
        raise ValueError("Geometry reference branch must be one authorized branch")
    if reference.get("side_count") != side_count:
        raise ValueError("Geometry reference side-count pin drift")
    if abs(_finite(reference.get("phase_rad"), "Geometry reference phase") - phase) > TOLERANCE:
        raise ValueError("Geometry reference phase pin drift")
    for key in ("module_path", "repository"):
        if not isinstance(reference.get(key), str) or not reference[key]:
            raise ValueError(f"Geometry reference {key} missing")

    predecessor = contract.get("predecessor_projection")
    if not isinstance(predecessor, dict):
        raise ValueError("predecessor projection provenance missing")
    _require_hex(predecessor.get("module_blob"), 40, "predecessor projection module blob")
    _require_hex(predecessor.get("contract_blob"), 40, "predecessor projection contract blob")
    _require_hex(predecessor.get("frame_contract_blob"), 40, "predecessor frame contract blob")
    for key in ("module_path", "contract_path", "frame_contract_path"):
        if not isinstance(predecessor.get(key), str) or not predecessor[key]:
            raise ValueError(f"predecessor projection {key} missing")

    forbidden = (
        "source_mutation_authorized",
        "triangle_membership_authorized",
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


def assemble_indexed_trunk_envelope_projection_family(
    source: dict,
    predecessor_projection_family: dict,
    contract: dict,
) -> dict:
    validate_contract(contract)
    if digest(source) != contract["organic_source_digest"]:
        raise ValueError("exact Organic source digest drift")
    if predecessor_projection_family.get("schema") != PREDECESSOR_SCHEMA:
        raise ValueError("predecessor projection family schema mismatch")
    if predecessor_projection_family.get("family_digest") != contract["predecessor_projection_family_digest"]:
        raise ValueError("predecessor projection family digest drift")
    predecessor_outputs = predecessor_projection_family.get("outputs")
    if not isinstance(predecessor_outputs, list):
        raise ValueError("predecessor projection outputs missing")
    predecessor_map = {
        row.get("branch_id"): row for row in predecessor_outputs if isinstance(row, dict)
    }
    if len(predecessor_map) != len(predecessor_outputs):
        raise ValueError("predecessor projection branch identity duplicated")
    if set(predecessor_map) != set(contract["authorized_branch_ids"]):
        raise ValueError("predecessor projection branch identity drift")

    outputs = []
    all_deltas = []
    for branch_id in contract["authorized_branch_ids"]:
        predecessor = predecessor_map[branch_id]
        segment_id = predecessor.get("trunk_segment_id")
        samples = predecessor.get("samples")
        if not isinstance(segment_id, str) or not segment_id:
            raise ValueError(f"{branch_id} predecessor trunk segment missing")
        if not isinstance(samples, list) or len(samples) < 3:
            raise ValueError(f"{branch_id} predecessor must retain at least three projection samples")
        points = [sample.get("input_point_m") for sample in samples]
        indexed = project_points_to_regular_tapered_shell(
            source,
            segment_id,
            points,
            side_count=contract["receiver_side_count"],
            phase_rad=contract["receiver_phase_rad"],
        )
        rows = []
        semantics = predecessor.get("sample_semantics", [None] * len(samples))
        if not isinstance(semantics, list) or len(semantics) != len(samples):
            raise ValueError(f"{branch_id} predecessor sample semantics drift")
        for sample_index, (smooth, shell) in enumerate(zip(samples, indexed)):
            if abs(float(smooth["segment_t"]) - shell["segment_t"]) > TOLERANCE:
                raise ValueError(f"{branch_id} sample {sample_index} axial parameter drift")
            if abs(float(smooth["local_radius_m"]) - shell["local_radius_m"]) > TOLERANCE:
                raise ValueError(f"{branch_id} sample {sample_index} taper radius drift")
            if shell["axial_coordinate_residual_m"] > TOLERANCE:
                raise ValueError(f"{branch_id} sample {sample_index} indexed projection changes axial coordinate")
            if shell["surface_edge_residual_m"] > TOLERANCE:
                raise ValueError(f"{branch_id} sample {sample_index} leaves indexed shell side")
            surface_delta = _distance(
                _vec3(smooth["surface_point_m"], "predecessor smooth surface"),
                shell["surface_point_m"],
            )
            if abs(surface_delta - shell["analytic_to_indexed_radial_delta_m"]) > TOLERANCE:
                raise ValueError(f"{branch_id} sample {sample_index} smooth/indexed delta inconsistency")
            all_deltas.append(surface_delta)
            rows.append(
                {
                    "sample_index": sample_index,
                    "sample_semantic": semantics[sample_index],
                    "smooth_surface_point_m": smooth["surface_point_m"],
                    "indexed_projection": shell,
                    "analytic_to_indexed_surface_delta_m": surface_delta,
                }
            )

        core = {
            "output_id": f"{branch_id}-transition-indexed-trunk-envelope-projection",
            "branch_id": branch_id,
            "trunk_segment_id": segment_id,
            "receiver_side_count": contract["receiver_side_count"],
            "receiver_phase_rad": contract["receiver_phase_rad"],
            "samples": rows,
            "triangle_membership_authored": False,
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
        raise ValueError("indexed projection family collapsed to fewer than three materially different outputs")
    surface_identities = {
        digest([sample["indexed_projection"]["surface_point_m"] for sample in row["samples"]])
        for row in outputs
    }
    if len(surface_identities) < 3:
        raise ValueError("indexed projection family collapsed to fewer than three materially different surfaces")
    if not all_deltas or max(all_deltas) <= TOLERANCE:
        raise ValueError("indexed projection family does not materially differ from smooth predecessor")

    family_core = {
        "schema": SCHEMA,
        "family_id": contract["family_id"],
        "relation": RELATION,
        "predecessor_projection_family_schema": PREDECESSOR_SCHEMA,
        "predecessor_projection_family_digest": predecessor_projection_family["family_digest"],
        "geometry_reference": contract["geometry_reference"],
        "receiver_side_count": contract["receiver_side_count"],
        "receiver_phase_rad": contract["receiver_phase_rad"],
        "output_count": len(outputs),
        "maximum_analytic_to_indexed_surface_delta_m": max(all_deltas),
        "minimum_analytic_to_indexed_surface_delta_m": min(all_deltas),
        "outputs": outputs,
        "source_authority": False,
        "geometry_triangle_membership_authority": False,
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

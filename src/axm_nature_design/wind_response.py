"""Bounded visual wind response for the source-owned sapling study.

This module produces deterministic *visual* deformation evidence. It does not
model physical wind, forces, plant biomechanics, rigging, gameplay or runtime
particles.
"""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

from .organic_form import build_mesh, digest, structural_checks

SCHEMA = "axm.nature-visual-wind-response-study/v0.2"
EVIDENCE_SCHEMA = "axm.nature-visual-wind-response-evidence/v0.2"
EXPECTED_SOURCE_REPOSITORY = "mike-axiom-mir/axm-nature-design"
EXPECTED_SOURCE_PR = 1
EXPECTED_SOURCE_HEAD = "fbc202449981f2bac153951c561ed0ed6120c936"
EXPECTED_SOURCE_DIGEST = "a61207b23c441b2cc0becd165fa62289bb7e51065ae0d6fa56bf9f3cab036cc1"
EXPECTED_NEUTRAL_MESH_DIGEST = "89b835bd8f3e728206543d210787f1bbd1cc1bacb6d01f6695caf3ea1a63fa4c"
EXPECTED_WEATHER_REPOSITORY = "mike-axiom-mir/axm-weather-design"
EXPECTED_WEATHER_PR = 2
EXPECTED_WEATHER_HEAD = "ca2eaba519e8449835b0ea6ef944b7080c3caa6a"
WEATHER_SEMANTICS = "VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED"
EXPECTED_PRIOR_VFX_HEAD = "4ef316157844fc2236a7671ce9e90a5435cba2c5"
EXPECTED_PRIOR_ARTIFACT_ID = 10427854091
PROFILE = "HIERARCHICAL_TRUNK_BRANCH_LEAF_HALF_SINE_VISUAL_SWAY"


def _norm2(v):
    length = math.hypot(float(v[0]), float(v[1]))
    if length <= 1e-12:
        raise ValueError("visual wind direction must be non-zero")
    return [float(v[0]) / length, float(v[1]) / length]


def _smoothstep01(value: float) -> float:
    x = min(1.0, max(0.0, float(value)))
    return x * x * (3.0 - 2.0 * x)


def _phase(time_s: float, duration_s: float) -> float:
    t = float(time_s)
    duration = float(duration_s)
    if duration <= 0.0:
        raise ValueError("duration_s must be positive")
    if t < -1e-12 or t > duration + 1e-12:
        raise ValueError("sample time outside bounded response window")
    if abs(t) <= 1e-12 or abs(t - duration) <= 1e-12:
        return 0.0
    return math.sin(math.pi * t / duration)


def _sub3(a, b):
    return [float(a[0]) - float(b[0]), float(a[1]) - float(b[1]), float(a[2]) - float(b[2])]


def _dot3(a, b):
    return float(a[0]) * float(b[0]) + float(a[1]) * float(b[1]) + float(a[2]) * float(b[2])


def _segment_progress(point, a, b) -> float:
    axis = _sub3(b, a)
    denom = _dot3(axis, axis)
    if denom <= 1e-18:
        raise ValueError("response support segment must have non-zero length")
    u = _dot3(_sub3(point, a), axis) / denom
    return min(1.0, max(0.0, u))


def _leaf_direction(yaw_deg: float, pitch_deg: float):
    yaw = math.radians(float(yaw_deg))
    pitch = math.radians(float(pitch_deg))
    horizontal = math.cos(pitch)
    return [horizontal * math.cos(yaw), horizontal * math.sin(yaw), math.sin(pitch)]


def _region_vertices(mesh: dict) -> dict[str, list[int]]:
    result: dict[str, list[int]] = {}
    triangles = mesh["triangles"]
    for region in mesh["regions"]:
        start = int(region["triangle_start"])
        end = start + int(region["triangle_count"])
        indices = sorted({int(i) for tri in triangles[start:end] for i in tri})
        result[str(region["id"])] = indices
    return result


def _hierarchy_weights(source: dict, mesh: dict, anchor_z_m: float) -> dict:
    """Return deterministic visual response weights without mutating source/mesh.

    `primary` is the original height field at reduced amplitude.
    `branch` adds source-owned branch/crown-tip give while preserving support
    attachment positions.
    `leaf` adds only local blade-base -> blade-tip give.
    """
    vertices = mesh["vertices"]
    max_z = max(float(v[2]) for v in vertices)
    span = max(max_z - float(anchor_z_m), 1e-12)
    primary = [_smoothstep01((float(v[2]) - float(anchor_z_m)) / span) for v in vertices]
    branch = [0.0] * len(vertices)
    leaf = [0.0] * len(vertices)
    region_vertices = _region_vertices(mesh)

    branches = {str(item["id"]): item for item in source["branches"]}
    for branch_id, branch_source in branches.items():
        points = branch_source["points"]
        segment_count = len(points) - 1
        for segment_index in range(segment_count):
            region_id = f"branch:{branch_id}:{segment_index}"
            if region_id not in region_vertices:
                raise ValueError(f"missing branch response region: {region_id}")
            a = points[segment_index]
            b = points[segment_index + 1]
            for vertex_index in region_vertices[region_id]:
                local_u = _segment_progress(vertices[vertex_index], a, b)
                branch_u = (segment_index + local_u) / segment_count
                branch[vertex_index] = max(branch[vertex_index], _smoothstep01(branch_u))

    trunk = source["trunk"]
    crown_a = trunk[-2]["position"]
    crown_b = trunk[-1]["position"]
    crown_region_id = f"trunk:{trunk[-2]['id']}->{trunk[-1]['id']}"
    if crown_region_id not in region_vertices:
        raise ValueError("missing crown response region")
    for vertex_index in region_vertices[crown_region_id]:
        branch[vertex_index] = max(
            branch[vertex_index],
            _smoothstep01(_segment_progress(vertices[vertex_index], crown_a, crown_b)),
        )

    branch_tip_by_center = {
        tuple(float(x) for x in item["points"][-1]): str(item["id"])
        for item in source["branches"]
    }
    crown_tip = tuple(float(x) for x in trunk[-1]["position"])

    for cluster in source["leaf_clusters"]:
        center = tuple(float(x) for x in cluster["center"])
        if center not in branch_tip_by_center and center != crown_tip:
            raise ValueError(f"leaf cluster {cluster.get('id')} is not attached to a known response support tip")
        length = float(cluster["length"])
        if length <= 0.0:
            raise ValueError("leaf response requires positive blade length")
        for blade_index, (yaw_deg, pitch_deg) in enumerate(cluster["blades"]):
            region_id = f"leaf:{cluster['id']}:{blade_index}"
            if region_id not in region_vertices:
                raise ValueError(f"missing leaf response region: {region_id}")
            direction = _leaf_direction(yaw_deg, pitch_deg)
            for vertex_index in region_vertices[region_id]:
                point = vertices[vertex_index]
                along = _dot3(_sub3(point, cluster["center"]), direction) / length
                branch[vertex_index] = 1.0
                leaf[vertex_index] = max(leaf[vertex_index], _smoothstep01(along))

    return {"primary": primary, "branch": branch, "leaf": leaf}


def _response_components(spec: dict) -> tuple[float, float, float, float]:
    response = spec["response"]
    primary = float(response["primary_height_offset_m"])
    branch = float(response["branch_tip_secondary_offset_m"])
    leaf = float(response["leaf_tip_secondary_offset_m"])
    ceiling = float(response["max_displacement_ceiling_m"])
    return primary, branch, leaf, ceiling


def validate_spec(spec: dict, source: dict) -> None:
    if spec.get("schema") != SCHEMA:
        raise ValueError("unsupported visual wind response schema")
    provenance = spec.get("source_provenance", {})
    expected_source = {
        "repository": EXPECTED_SOURCE_REPOSITORY,
        "pr": EXPECTED_SOURCE_PR,
        "head": EXPECTED_SOURCE_HEAD,
        "source_digest": EXPECTED_SOURCE_DIGEST,
        "mesh_digest": EXPECTED_NEUTRAL_MESH_DIGEST,
    }
    for key, expected in expected_source.items():
        if provenance.get(key) != expected:
            raise ValueError(f"source provenance mismatch: {key}")
    if digest(source) != EXPECTED_SOURCE_DIGEST:
        raise ValueError("receiving source digest does not match pinned Nature source")
    neutral = build_mesh(source)
    if digest(neutral) != EXPECTED_NEUTRAL_MESH_DIGEST:
        raise ValueError("receiving neutral mesh digest does not match pinned Nature mesh")

    weather = spec.get("weather_provenance", {})
    if weather.get("repository") != EXPECTED_WEATHER_REPOSITORY:
        raise ValueError("weather repository mismatch")
    if weather.get("pr") != EXPECTED_WEATHER_PR:
        raise ValueError("weather PR mismatch")
    if weather.get("head") != EXPECTED_WEATHER_HEAD:
        raise ValueError("weather head mismatch")
    if weather.get("semantics") != WEATHER_SEMANTICS:
        raise ValueError("weather semantics must remain visual-only")
    wind = weather.get("visual_wind_xy")
    if not isinstance(wind, list) or len(wind) != 2:
        raise ValueError("visual_wind_xy must contain two values")
    _norm2(wind)
    if source.get("weather_handoff", {}).get("head") != EXPECTED_WEATHER_HEAD:
        raise ValueError("Nature source weather handoff no longer matches pinned Weather head")
    if source.get("weather_handoff", {}).get("visual_wind_xy") != wind:
        raise ValueError("visual wind direction differs from Nature handoff")

    prior = spec.get("prior_visual_baseline", {})
    if prior.get("head") != EXPECTED_PRIOR_VFX_HEAD:
        raise ValueError("prior visual baseline head mismatch")
    if int(prior.get("artifact_id", -1)) != EXPECTED_PRIOR_ARTIFACT_ID:
        raise ValueError("prior visual baseline artifact mismatch")

    response = spec.get("response", {})
    duration = float(response.get("duration_s", 0.0))
    anchor_z = float(response.get("anchor_z_m", -1.0))
    samples = [float(v) for v in response.get("sample_times_s", [])]
    if duration <= 0.0:
        raise ValueError("response duration must be positive")
    if anchor_z < 0.0:
        raise ValueError("anchor_z_m must be non-negative")
    if samples != sorted(set(samples)) or not samples:
        raise ValueError("sample times must be non-empty, unique and sorted")
    if samples[0] != 0.0 or samples[-1] != duration:
        raise ValueError("sample window must include exact neutral endpoints")
    if len(samples) < 5 or duration * 0.5 not in samples:
        raise ValueError("hierarchical comparison requires at least five samples including the exact midpoint")
    for t in samples:
        _phase(t, duration)
    if response.get("profile") != PROFILE:
        raise ValueError("unknown response profile")

    primary, branch, leaf, ceiling = _response_components(spec)
    if min(primary, branch, leaf, ceiling) <= 0.0:
        raise ValueError("visual response component bounds must be positive")
    if primary + branch + leaf > ceiling + 1e-12:
        raise ValueError("hierarchical visual response components exceed declared ceiling")
    if abs((primary + branch + leaf) - ceiling) > 1e-12:
        raise ValueError("component budget must account exactly for the retained displacement ceiling")

    _hierarchy_weights(source, neutral, anchor_z)


def deform_mesh(source: dict, spec: dict, time_s: float) -> dict:
    validate_spec(spec, source)
    neutral = build_mesh(source)
    result = copy.deepcopy(neutral)
    response = spec["response"]
    wind = _norm2(spec["weather_provenance"]["visual_wind_xy"])
    phase = _phase(time_s, float(response["duration_s"]))
    primary_cap, branch_cap, leaf_cap, _ = _response_components(spec)
    weights = _hierarchy_weights(source, neutral, float(response["anchor_z_m"]))

    for index, vertex in enumerate(result["vertices"]):
        offset = phase * (
            primary_cap * weights["primary"][index]
            + branch_cap * weights["branch"][index]
            + leaf_cap * weights["leaf"][index]
        )
        vertex[0] = float(vertex[0]) + wind[0] * offset
        vertex[1] = float(vertex[1]) + wind[1] * offset
    return result


def _vertex_delta(a, b):
    return [float(b[0]) - float(a[0]), float(b[1]) - float(a[1]), float(b[2]) - float(a[2])]


def measure_sample(neutral: dict, deformed: dict, wind_xy, anchor_z_m: float) -> dict:
    if neutral["triangles"] != deformed["triangles"] or neutral["regions"] != deformed["regions"]:
        raise ValueError("visual response may not alter topology or region identity")
    wind = _norm2(wind_xy)
    cross = [-wind[1], wind[0]]
    projected = []
    crosswind = []
    anchor_displacements = []
    magnitudes = []
    for before, after in zip(neutral["vertices"], deformed["vertices"]):
        d = _vertex_delta(before, after)
        projected.append(d[0] * wind[0] + d[1] * wind[1])
        crosswind.append(d[0] * cross[0] + d[1] * cross[1])
        magnitudes.append(math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2))
        if float(before[2]) <= float(anchor_z_m) + 1e-12:
            anchor_displacements.append(magnitudes[-1])
    structure = structural_checks(deformed)
    return {
        "max_displacement_m": max(magnitudes, default=0.0),
        "max_downwind_projection_m": max(projected, default=0.0),
        "min_downwind_projection_m": min(projected, default=0.0),
        "max_abs_crosswind_drift_m": max((abs(v) for v in crosswind), default=0.0),
        "max_anchor_displacement_m": max(anchor_displacements, default=0.0),
        "structural": structure,
        "mesh_digest": digest(deformed),
    }


def _find_vertex_at_point(mesh: dict, candidate_indices: list[int], point, tolerance: float = 1e-12) -> int:
    best = None
    best_distance = None
    for index in candidate_indices:
        delta = _sub3(mesh["vertices"][index], point)
        distance = math.sqrt(_dot3(delta, delta))
        if best_distance is None or distance < best_distance:
            best = index
            best_distance = distance
    if best is None or best_distance is None or best_distance > tolerance:
        raise ValueError("could not locate exact support vertex for visual hierarchy evidence")
    return best


def _leaf_support_gap(source: dict, neutral: dict, deformed: dict) -> float:
    region_vertices = _region_vertices(neutral)
    trunk = source["trunk"]
    crown_tip = tuple(float(x) for x in trunk[-1]["position"])
    branch_by_tip = {
        tuple(float(x) for x in item["points"][-1]): item
        for item in source["branches"]
    }
    gaps = []
    for cluster in source["leaf_clusters"]:
        center = tuple(float(x) for x in cluster["center"])
        leaf_region_id = f"leaf:{cluster['id']}:0"
        leaf_indices = region_vertices[leaf_region_id]
        leaf_base = _find_vertex_at_point(neutral, leaf_indices, center)
        if center == crown_tip:
            support_region_id = f"trunk:{trunk[-2]['id']}->{trunk[-1]['id']}"
        elif center in branch_by_tip:
            branch_source = branch_by_tip[center]
            support_region_id = f"branch:{branch_source['id']}:{len(branch_source['points']) - 2}"
        else:
            raise ValueError("leaf cluster has no known support for continuity evidence")
        support_index = _find_vertex_at_point(neutral, region_vertices[support_region_id], center)
        leaf_delta = _vertex_delta(neutral["vertices"][leaf_base], deformed["vertices"][leaf_base])
        support_delta = _vertex_delta(neutral["vertices"][support_index], deformed["vertices"][support_index])
        gap = math.sqrt(sum((leaf_delta[i] - support_delta[i]) ** 2 for i in range(3)))
        gaps.append(gap)
    return max(gaps, default=0.0)


def _hierarchy_metrics(source: dict, neutral: dict, spec: dict, peak_deformed: dict) -> dict:
    response = spec["response"]
    weights = _hierarchy_weights(source, neutral, float(response["anchor_z_m"]))
    primary_cap, branch_cap, leaf_cap, ceiling = _response_components(spec)
    return {
        "primary_height_component_cap_m": primary_cap,
        "branch_tip_secondary_component_cap_m": branch_cap,
        "leaf_tip_secondary_component_cap_m": leaf_cap,
        "declared_displacement_ceiling_m": ceiling,
        "max_primary_weight": max(weights["primary"], default=0.0),
        "max_branch_secondary_weight": max(weights["branch"], default=0.0),
        "max_leaf_secondary_weight": max(weights["leaf"], default=0.0),
        "max_leaf_base_support_gap_m": _leaf_support_gap(source, neutral, peak_deformed),
    }


def build_evidence(source: dict, spec: dict) -> dict:
    validate_spec(spec, source)
    neutral = build_mesh(source)
    response = spec["response"]
    samples = []
    deformed_by_time = {}
    for time_s in response["sample_times_s"]:
        deformed = deform_mesh(source, spec, float(time_s))
        deformed_by_time[float(time_s)] = deformed
        samples.append({
            "time_s": float(time_s),
            "phase": _phase(float(time_s), float(response["duration_s"])),
            **measure_sample(neutral, deformed, spec["weather_provenance"]["visual_wind_xy"], float(response["anchor_z_m"])),
        })

    endpoint_exact = (
        samples[0]["mesh_digest"] == EXPECTED_NEUTRAL_MESH_DIGEST
        and samples[-1]["mesh_digest"] == EXPECTED_NEUTRAL_MESH_DIGEST
    )
    peak = max(samples, key=lambda item: item["phase"])
    peak_mesh = deformed_by_time[float(peak["time_s"])]
    hierarchy = _hierarchy_metrics(source, neutral, spec, peak_mesh)
    _, _, _, ceiling = _response_components(spec)
    checks = {
        "neutral_endpoints_exact": endpoint_exact,
        "topology_preserved_all_samples": all(s["structural"]["pass"] for s in samples),
        "anchor_preserved_all_samples": all(s["max_anchor_displacement_m"] <= 1e-12 for s in samples),
        "peak_is_downwind": peak["max_downwind_projection_m"] > 0.0 and peak["min_downwind_projection_m"] >= -1e-12,
        "crosswind_residual_bounded": peak["max_abs_crosswind_drift_m"] <= 1e-12,
        "peak_respects_authored_ceiling": peak["max_displacement_m"] <= ceiling + 1e-12,
        "peak_response_remains_materially_visible": peak["max_displacement_m"] >= ceiling * 0.85,
        "branch_secondary_response_present": hierarchy["max_branch_secondary_weight"] >= 1.0 - 1e-12,
        "leaf_secondary_response_present": hierarchy["max_leaf_secondary_weight"] >= 1.0 - 1e-12,
        "leaf_bases_follow_support_without_gap": hierarchy["max_leaf_base_support_gap_m"] <= 1e-12,
        "source_flex_claims_unchanged": all(zone.get("status") == "DECLARED_NOT_DEFORMATION_TESTED" for zone in source.get("flex_zones", [])),
        "prior_held_profile_preserved_as_before_evidence": spec["prior_visual_baseline"]["head"] == EXPECTED_PRIOR_VFX_HEAD,
    }
    state = "PASS_BOUNDED_VISUAL_WIND_RESPONSE" if all(checks.values()) else "FAIL"
    return {
        "schema": EVIDENCE_SCHEMA,
        "study_id": spec["study_id"],
        "state": state,
        "source_provenance": spec["source_provenance"],
        "weather_provenance": spec["weather_provenance"],
        "prior_visual_baseline": spec["prior_visual_baseline"],
        "response": spec["response"],
        "neutral_vertices": len(neutral["vertices"]),
        "neutral_triangles": len(neutral["triangles"]),
        "hierarchy": hierarchy,
        "checks": checks,
        "samples": samples,
        "truth_boundary": spec["truth_boundary"],
    }


def _unique_edges(triangles):
    edges = set()
    for a, b, c in triangles:
        for x, y in ((a, b), (b, c), (c, a)):
            edges.add(tuple(sorted((x, y))))
    return sorted(edges)


def write_comparison_svg(meshes: list[tuple[float, dict]], path: str | Path, view: str) -> None:
    axes = {"front": (0, 2), "side": (1, 2), "top": (0, 1)}
    if view not in axes:
        raise ValueError("unknown view")
    ax0, ax1 = axes[view]
    all_points = [(float(v[ax0]), float(v[ax1])) for _, mesh in meshes for v in mesh["vertices"]]
    min0, max0 = min(p[0] for p in all_points), max(p[0] for p in all_points)
    min1, max1 = min(p[1] for p in all_points), max(p[1] for p in all_points)
    span0 = max(max0 - min0, 1e-9)
    span1 = max(max1 - min1, 1e-9)
    panel_w = 420.0
    scale = min(340.0 / span0, 410.0 / span1)
    width = int(panel_w * len(meshes))
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="560" viewBox="0 0 {width} 560">',
        f'<rect width="{width}" height="560" fill="white"/>',
        f'<text x="20" y="28" font-family="monospace" font-size="17">sapling-wind-response-001 / {view} / hierarchical visual-only</text>',
    ]
    for panel_index, (time_s, mesh) in enumerate(meshes):
        cx = panel_index * panel_w + panel_w * 0.5
        cy = 300.0
        center0 = (min0 + max0) * 0.5
        center1 = (min1 + max1) * 0.5
        points = [(float(v[ax0]), float(v[ax1])) for v in mesh["vertices"]]

        def p2(p):
            return (cx + (p[0] - center0) * scale, cy - (p[1] - center1) * scale)

        lines.append(f'<rect x="{panel_index*panel_w+8:.1f}" y="42" width="{panel_w-16:.1f}" height="488" fill="none" stroke="#bbb"/>')
        lines.append(f'<text x="{panel_index*panel_w+20:.1f}" y="64" font-family="monospace" font-size="15">t={time_s:.3f}s</text>')
        for a, b in _unique_edges(mesh["triangles"]):
            x1, y1 = p2(points[a])
            x2, y2 = p2(points[b])
            lines.append(f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="#111" stroke-width="0.65" stroke-opacity="0.58"/>')
    lines.append("</svg>")
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_spec(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))

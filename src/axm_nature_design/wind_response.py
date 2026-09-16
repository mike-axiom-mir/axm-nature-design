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

SCHEMA = "axm.nature-visual-wind-response-study/v0.1"
EVIDENCE_SCHEMA = "axm.nature-visual-wind-response-evidence/v0.1"
EXPECTED_SOURCE_REPOSITORY = "mike-axiom-mir/axm-nature-design"
EXPECTED_SOURCE_PR = 1
EXPECTED_SOURCE_HEAD = "fbc202449981f2bac153951c561ed0ed6120c936"
EXPECTED_SOURCE_DIGEST = "a61207b23c441b2cc0becd165fa62289bb7e51065ae0d6fa56bf9f3cab036cc1"
EXPECTED_NEUTRAL_MESH_DIGEST = "89b835bd8f3e728206543d210787f1bbd1cc1bacb6d01f6695caf3ea1a63fa4c"
EXPECTED_WEATHER_REPOSITORY = "mike-axiom-mir/axm-weather-design"
EXPECTED_WEATHER_PR = 2
EXPECTED_WEATHER_HEAD = "ca2eaba519e8449835b0ea6ef944b7080c3caa6a"
WEATHER_SEMANTICS = "VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED"


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

    response = spec.get("response", {})
    duration = float(response.get("duration_s", 0.0))
    anchor_z = float(response.get("anchor_z_m", -1.0))
    max_tip_offset = float(response.get("max_tip_offset_m", 0.0))
    samples = [float(v) for v in response.get("sample_times_s", [])]
    if duration <= 0.0 or max_tip_offset <= 0.0:
        raise ValueError("response duration and max tip offset must be positive")
    if anchor_z < 0.0:
        raise ValueError("anchor_z_m must be non-negative")
    if samples != sorted(set(samples)) or not samples:
        raise ValueError("sample times must be non-empty, unique and sorted")
    if samples[0] != 0.0 or samples[-1] != duration:
        raise ValueError("sample window must include exact neutral endpoints")
    for t in samples:
        _phase(t, duration)
    if response.get("profile") != "HEIGHT_WEIGHTED_HALF_SINE_DOWNWIND_VISUAL_SWAY":
        raise ValueError("unknown response profile")


def deform_mesh(source: dict, spec: dict, time_s: float) -> dict:
    validate_spec(spec, source)
    neutral = build_mesh(source)
    result = copy.deepcopy(neutral)
    response = spec["response"]
    anchor_z = float(response["anchor_z_m"])
    max_tip_offset = float(response["max_tip_offset_m"])
    duration = float(response["duration_s"])
    wind = _norm2(spec["weather_provenance"]["visual_wind_xy"])
    phase = _phase(time_s, duration)
    max_z = max(float(v[2]) for v in neutral["vertices"])
    span = max(max_z - anchor_z, 1e-12)

    for vertex in result["vertices"]:
        z = float(vertex[2])
        height_u = (z - anchor_z) / span
        weight = _smoothstep01(height_u)
        offset = max_tip_offset * phase * weight
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


def build_evidence(source: dict, spec: dict) -> dict:
    validate_spec(spec, source)
    neutral = build_mesh(source)
    response = spec["response"]
    samples = []
    for time_s in response["sample_times_s"]:
        deformed = deform_mesh(source, spec, float(time_s))
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
    checks = {
        "neutral_endpoints_exact": endpoint_exact,
        "topology_preserved_all_samples": all(s["structural"]["pass"] for s in samples),
        "anchor_preserved_all_samples": all(s["max_anchor_displacement_m"] <= 1e-12 for s in samples),
        "peak_is_downwind": peak["max_downwind_projection_m"] > 0.0 and peak["min_downwind_projection_m"] >= -1e-12,
        "crosswind_residual_bounded": peak["max_abs_crosswind_drift_m"] <= 1e-12,
        "peak_offset_matches_authored_bound": abs(peak["max_displacement_m"] - float(response["max_tip_offset_m"])) <= 1e-12,
        "source_flex_claims_unchanged": all(zone.get("status") == "DECLARED_NOT_DEFORMATION_TESTED" for zone in source.get("flex_zones", [])),
    }
    state = "PASS_BOUNDED_VISUAL_WIND_RESPONSE" if all(checks.values()) else "FAIL"
    return {
        "schema": EVIDENCE_SCHEMA,
        "study_id": spec["study_id"],
        "state": state,
        "source_provenance": spec["source_provenance"],
        "weather_provenance": spec["weather_provenance"],
        "response": spec["response"],
        "neutral_vertices": len(neutral["vertices"]),
        "neutral_triangles": len(neutral["triangles"]),
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
        f'<text x="20" y="28" font-family="monospace" font-size="17">sapling-wind-response-001 / {view} / visual-only</text>',
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
        lines.append(f'<text x="{panel_index*panel_w+20:.1f}" y="64" font-family="monospace" font-size="15">t={time_s:.2f}s</text>')
        for a, b in _unique_edges(mesh["triangles"]):
            x1, y1 = p2(points[a]); x2, y2 = p2(points[b])
            lines.append(f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="#111" stroke-width="0.65" stroke-opacity="0.58"/>')
    lines.append('</svg>')
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_spec(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))

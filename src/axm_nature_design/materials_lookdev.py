"""Bounded material/look-development overlay for the first Nature sapling.

This module is deliberately source-preserving. It consumes the exact Nature -> UC
surface bridge and changes only material scalar/color fields for known primitive
IDs. Geometry, normals, indices, source provenance and explicit leaf-backface
strategy remain owned by the upstream bridge.
"""
from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

PROFILE_SCHEMA = "axm.nature-sapling-material-profile/v0.1"
EVIDENCE_SCHEMA = "axm.nature-sapling-material-lookdev-evidence/v0.1"
_ALLOWED_MATERIAL_KEYS = {"color", "metallic", "roughness"}
_EXPECTED_PRIMITIVES = {"woody", "foliage"}


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _hex_rgb(color: str) -> tuple[int, int, int]:
    if not isinstance(color, str) or len(color) != 9 or not color.startswith("#"):
        raise ValueError("material color must be #RRGGBBAA")
    try:
        values = tuple(int(color[i : i + 2], 16) for i in (1, 3, 5))
        int(color[7:9], 16)
    except ValueError as exc:
        raise ValueError("material color must be #RRGGBBAA") from exc
    return values


def _srgb_channel(value: int) -> float:
    x = value / 255.0
    return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4


def relative_luminance(color: str) -> float:
    r8, g8, b8 = _hex_rgb(color)
    r, g, b = (_srgb_channel(value) for value in (r8, g8, b8))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def validate_profile(profile: dict[str, Any]) -> None:
    if profile.get("schema") != PROFILE_SCHEMA:
        raise ValueError("unsupported Nature material profile schema")
    materials = profile.get("materials")
    if not isinstance(materials, dict) or set(materials) != _EXPECTED_PRIMITIVES:
        raise ValueError("profile must define exactly woody and foliage materials")
    for identifier, material in materials.items():
        if not isinstance(material, dict) or set(material) != _ALLOWED_MATERIAL_KEYS:
            raise ValueError(f"{identifier} material must contain only color/metallic/roughness")
        _hex_rgb(material["color"])
        metallic = float(material["metallic"])
        roughness = float(material["roughness"])
        if metallic != 0.0:
            raise ValueError("first sapling lookdev profile is intentionally non-metallic")
        if not 0.0 <= roughness <= 1.0:
            raise ValueError("roughness must be inside [0,1]")


def _geometry_payload(surface: dict[str, Any]) -> dict[str, Any]:
    payload = {"schema": surface.get("schema"), "name": surface.get("name"), "primitives": []}
    for primitive in surface.get("primitives", []):
        payload["primitives"].append(
            {
                "id": primitive.get("id"),
                "positions": primitive.get("positions"),
                "normals": primitive.get("normals"),
                "indices": primitive.get("indices"),
            }
        )
    return payload


def apply_profile(surface: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    """Return a derived UC-compatible surface with material fields replaced only."""
    validate_profile(profile)
    primitives = surface.get("primitives")
    if not isinstance(primitives, list) or {row.get("id") for row in primitives if isinstance(row, dict)} != _EXPECTED_PRIMITIVES:
        raise ValueError("surface must expose exactly woody and foliage primitives")
    candidate = copy.deepcopy(surface)
    for primitive in candidate["primitives"]:
        identifier = primitive["id"]
        primitive["material"] = copy.deepcopy(profile["materials"][identifier])
    return candidate


def build_material_evidence(surface: dict[str, Any], candidate: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    validate_profile(profile)
    baseline_geometry = _geometry_payload(surface)
    candidate_geometry = _geometry_payload(candidate)
    baseline_materials = {row["id"]: row["material"] for row in surface["primitives"]}
    candidate_materials = {row["id"]: row["material"] for row in candidate["primitives"]}
    baseline_luma = {key: relative_luminance(value["color"]) for key, value in baseline_materials.items()}
    candidate_luma = {key: relative_luminance(value["color"]) for key, value in candidate_materials.items()}
    baseline_roughness_gap = abs(float(baseline_materials["woody"]["roughness"]) - float(baseline_materials["foliage"]["roughness"]))
    candidate_roughness_gap = abs(float(candidate_materials["woody"]["roughness"]) - float(candidate_materials["foliage"]["roughness"]))
    baseline_luma_gap = abs(baseline_luma["woody"] - baseline_luma["foliage"])
    candidate_luma_gap = abs(candidate_luma["woody"] - candidate_luma["foliage"])
    geometry_unchanged = digest(baseline_geometry) == digest(candidate_geometry)
    materials_changed = digest(baseline_materials) != digest(candidate_materials)
    checks = {
        "geometry_unchanged": geometry_unchanged,
        "materials_changed": materials_changed,
        "candidate_roughness_separation_increased": candidate_roughness_gap > baseline_roughness_gap,
        "candidate_luminance_separation_not_reduced": candidate_luma_gap >= baseline_luma_gap,
        "metallic_remains_zero": all(float(row["metallic"]) == 0.0 for row in candidate_materials.values()),
    }
    return {
        "schema": EVIDENCE_SCHEMA,
        "state": "PASS_BOUNDED_MATERIAL_PROFILE_STRUCTURE" if all(checks.values()) else "FAIL",
        "profile_id": profile.get("profile_id"),
        "profile_digest": digest(profile),
        "baseline_surface_digest": digest(surface),
        "candidate_surface_digest": digest(candidate),
        "geometry_digest": digest(baseline_geometry),
        "baseline_materials": baseline_materials,
        "candidate_materials": candidate_materials,
        "baseline_relative_luminance": baseline_luma,
        "candidate_relative_luminance": candidate_luma,
        "baseline_luminance_gap": baseline_luma_gap,
        "candidate_luminance_gap": candidate_luma_gap,
        "baseline_roughness_gap": baseline_roughness_gap,
        "candidate_roughness_gap": candidate_roughness_gap,
        "checks": checks,
        "truth_boundary": profile.get("truth_boundary"),
    }

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from typing import Any

from axm_nature_design.materials_lookdev import apply_profile, build_material_evidence, digest as material_digest
from axm_nature_design.organic_form import build_mesh, digest as nature_digest, load_source
from axm_nature_design.uc_surface_bridge import adapt_source_for_uc

SCHEMA = "axm.nature-material-environment-context/v0.1"
EVIDENCE_SCHEMA = "axm.nature-material-environment-context-evidence/v0.1"
EXPECTED_MAP_HEAD = "d52cb54a2aeb3eb4f5668e3d6ba4b05ddcc02899"
EXPECTED_MAP_SCENE_DIGEST = "f63ddbb0fcdacd5109b45df1d0338701fb138014d3b98dc697d6279fd370447d"
EXPECTED_NATURE_SOURCE_HEAD = "fbc202449981f2bac153951c561ed0ed6120c936"
EXPECTED_NATURE_SOURCE_DIGEST = "a61207b23c441b2cc0becd165fa62289bb7e51065ae0d6fa56bf9f3cab036cc1"
EXPECTED_WEATHER_HEAD = "ca2eaba519e8449835b0ea6ef944b7080c3caa6a"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _load_module(name: str, path: str | Path):
    spec = importlib.util.spec_from_file_location(name, Path(path))
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _bounds(vertices: list[list[float]]) -> dict[str, list[float]]:
    if not vertices:
        raise ValueError("source mesh has no vertices")
    mins = [min(float(v[i]) for v in vertices) for i in range(3)]
    maxs = [max(float(v[i]) for v in vertices) for i in range(3)]
    return {"min": mins, "max": maxs}


def placement_translation(source_vertices: list[list[float]], target_position: list[float]) -> list[float]:
    """Return the exact Map placement translation in Nature source XYZ coordinates."""
    if len(target_position) != 3:
        raise ValueError("target position must contain three coordinates")
    bounds = _bounds(source_vertices)
    center_x = (bounds["min"][0] + bounds["max"][0]) * 0.5
    center_y = (bounds["min"][1] + bounds["max"][1]) * 0.5
    return [
        float(target_position[0]) - center_x,
        float(target_position[1]) - center_y,
        -bounds["min"][2],
    ]


def _map_scene(map_root: Path, nature_source_root: Path, weather_root: Path) -> dict[str, Any]:
    eye = _load_module("axm_map_environment_eye_level_for_materials", map_root / "tools" / "environment_eye_level.py")
    previous = os.environ.get("AXM_RECEIVING_HEAD")
    os.environ["AXM_RECEIVING_HEAD"] = EXPECTED_MAP_HEAD
    try:
        scene = eye.build_scene_payload(
            map_root / "examples" / "environment_real_slice_001.json",
            nature_source_root,
            weather_root,
        )
    finally:
        if previous is None:
            os.environ.pop("AXM_RECEIVING_HEAD", None)
        else:
            os.environ["AXM_RECEIVING_HEAD"] = previous
    if scene.get("scene_digest") != EXPECTED_MAP_SCENE_DIGEST:
        raise ValueError("pinned Environment scene digest drifted; refusing an unbound material comparison")
    return scene


def build_context(map_root: str | Path, nature_source_root: str | Path, weather_root: str | Path) -> tuple[dict[str, Any], dict[str, Any]]:
    root = Path(__file__).resolve().parents[1]
    map_root = Path(map_root)
    nature_source_root = Path(nature_source_root)
    weather_root = Path(weather_root)

    source = load_source(root / "examples" / "sapling_neutral_001.json")
    source_digest = nature_digest(source)
    if source_digest != EXPECTED_NATURE_SOURCE_DIGEST:
        raise ValueError("Materials branch no longer matches the pinned Nature source digest")

    profile = json.loads((root / "lookdev" / "sapling_material_profile_001.json").read_text(encoding="utf-8"))
    bridge = adapt_source_for_uc(source)
    baseline_surface = bridge["surface"]
    candidate_surface = apply_profile(baseline_surface, profile)
    material_evidence = build_material_evidence(baseline_surface, candidate_surface, profile)
    if material_evidence["state"] != "PASS_BOUNDED_MATERIAL_PROFILE_STRUCTURE":
        raise ValueError("material candidate no longer passes its source-preserving structural gate")

    scene = _map_scene(map_root, nature_source_root, weather_root)
    mesh = build_mesh(source)
    replacement = scene["source_integration"]["replacement"]
    translation = placement_translation(mesh["vertices"], replacement["reserved_proxy_position_m"])

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "study_id": "sapling-material-environment-context-001",
        "materials_head": os.environ.get("AXM_MATERIALS_HEAD", "UNSET_LOCAL_HEAD"),
        "environment": {
            "repository": "mike-axiom-mir/axm-map-design",
            "head": EXPECTED_MAP_HEAD,
            "scene_digest": scene["scene_digest"],
            "relationship": "CONSUMES_EXACT_RECEIVING_CONTEXT_WITHOUT_MUTATING_PLACEMENT_OR_CAMERAS",
            "scene": scene,
        },
        "nature_source": {
            "repository": "mike-axiom-mir/axm-nature-design",
            "head": EXPECTED_NATURE_SOURCE_HEAD,
            "source_digest": source_digest,
            "source_mesh_digest": nature_digest(mesh),
        },
        "weather_source": {
            "repository": "mike-axiom-mir/axm-weather-design",
            "head": EXPECTED_WEATHER_HEAD,
            "source_digest": scene["source_integration"]["weather_overlay"]["source_digest"],
        },
        "portable_surface": {
            "bridge_surface_digest": bridge["surface_digest"],
            "leaf_sidedness_strategy": bridge["leaf_sidedness_strategy"],
            "baseline": baseline_surface,
            "candidate": candidate_surface,
            "baseline_digest": material_digest(baseline_surface),
            "candidate_digest": material_digest(candidate_surface),
            "placement_translation_source_xyz_m": translation,
            "representation_note": (
                "Both A/B renders use the already-proven Nature->UC portable surface with explicit leaf backfaces (620 triangles), "
                "not the Environment proof host's 570-triangle source mesh with observation-only culling disabled. This keeps the material "
                "comparison internally identical while preserving the Map placement/cameras/proxies/weather."
            ),
        },
        "material_evidence": material_evidence,
        "comparison_contract": {
            "variants": ["baseline", "candidate"],
            "contexts": ["path_eye", "elevated_oblique"],
            "only_allowed_A_B_difference": "woody_and_foliage_material_fields",
            "movement": "NONE_STATIC_NEUTRAL_ONLY",
            "environment_placement_changes": "NONE",
            "camera_changes": "NONE",
            "weather_changes": "NONE",
        },
        "provenance": {
            "map_observation_donor": {
                "repository": "mike-axiom-mir/axm-map-design",
                "head": EXPECTED_MAP_HEAD,
                "files": ["tools/environment_eye_level.py", "environment-proof/observe.gd"],
                "license_observation": "NO_EXPLICIT_LICENSE_FILE_FOUND_AT_PINNED_HEAD; SAME_OWNER_CAMPAIGN_REUSE_WITH_EXACT_PROVENANCE",
            }
        },
        "truth_boundary": (
            "This packet asks one bounded LookDev question: whether the existing source-preserving woody/foliage material delta remains visibly distinguishable "
            "inside the exact static Map receiving context from the existing path-eye and elevated-oblique cameras. It does not prove final vegetation lookdev, "
            "texture/UV quality, botanical reflectance, moving-sapling shading, final environment hierarchy, renderer equivalence, gameplay/runtime acceptance, CANON, or mastery."
        ),
    }
    payload["context_digest"] = digest(payload)

    checks = {
        "environment_scene_exact": payload["environment"]["scene_digest"] == EXPECTED_MAP_SCENE_DIGEST,
        "nature_source_exact": source_digest == EXPECTED_NATURE_SOURCE_DIGEST,
        "source_integration_pass": scene["source_integration"]["status"] == "PASS",
        "material_structure_pass": material_evidence["state"] == "PASS_BOUNDED_MATERIAL_PROFILE_STRUCTURE",
        "portable_geometry_unchanged": material_evidence["checks"]["geometry_unchanged"] is True,
        "materials_changed": material_evidence["checks"]["materials_changed"] is True,
        "two_fixed_environment_views": set(scene["cameras"]) == {"path_eye", "elevated_oblique"},
        "weather_count_preserved": len(scene["weather_lines"]) == 36,
        "static_only": payload["comparison_contract"]["movement"] == "NONE_STATIC_NEUTRAL_ONLY",
    }
    report = {
        "schema": EVIDENCE_SCHEMA,
        "study_id": payload["study_id"],
        "status": "PASS_CONTEXT_READY_FOR_TARGET_RENDER" if all(checks.values()) else "FAIL",
        "checks": checks,
        "context_digest": payload["context_digest"],
        "environment_scene_digest": scene["scene_digest"],
        "materials_head": payload["materials_head"],
        "baseline_surface_digest": payload["portable_surface"]["baseline_digest"],
        "candidate_surface_digest": payload["portable_surface"]["candidate_digest"],
        "placement_translation_source_xyz_m": translation,
        "truth_boundary": payload["truth_boundary"],
    }
    return payload, report


def build(map_root: str | Path, nature_source_root: str | Path, weather_root: str | Path, output_dir: str | Path) -> dict[str, Any]:
    payload, report = build_context(map_root, nature_source_root, weather_root)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "context.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "evidence.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--map-root", required=True)
    parser.add_argument("--nature-source-root", required=True)
    parser.add_argument("--weather-root", required=True)
    parser.add_argument("--output", default="evidence/sapling-material-environment-context-001")
    args = parser.parse_args()
    report = build(args.map_root, args.nature_source_root, args.weather_root, args.output)
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["status"] == "PASS_CONTEXT_READY_FOR_TARGET_RENDER" else 1)


if __name__ == "__main__":
    main()

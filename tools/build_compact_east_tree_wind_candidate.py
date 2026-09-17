from __future__ import annotations

import copy
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axm_nature_design import wind_response as response
from axm_nature_design.organic_form import build_mesh, digest, load_source, write_obj
from axm_nature_design.source_topology_migration import LINEAGE, evaluate as evaluate_migration

SOURCE = ROOT / "examples" / "compact_east_tree_neutral_001.json"
SPEC = ROOT / "examples" / "compact_east_tree_wind_candidate_001.json"
EXPECTED_SCHEMA = "axm.nature-visual-wind-response-transfer-study/v0.1"
EXPECTED_STUDY = "compact-east-tree-wind-candidate-001"
EXPECTED_SOURCE_STUDY = "compact-east-tree-neutral-001"
EXPECTED_SOURCE_HEAD = "64116d63fc76daa1623b5fd5046a4e6074100bda"
EXPECTED_MIGRATION_HEAD = "4ddbe66e5c02d22407ef773d5346a2fe6f349a2d"
EXPECTED_WEATHER_HEAD = "ca2eaba519e8449835b0ea6ef944b7080c3caa6a"
EXPECTED_WEATHER_SEMANTICS = "VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED"
EXPECTED_MECHANISM_HEAD = "cee14f5b3feea78b0adcd044bad2ea3c97657fc6"
EXPECTED_PROFILE = "HIERARCHICAL_TRUNK_BRANCH_LEAF_HALF_SINE_VISUAL_SWAY"
EXPECTED_LINEAGE = LINEAGE[EXPECTED_SOURCE_STUDY]


def load_spec(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("compact-tree response contract must be a JSON object")
    return data


def _max_vertex_distance(a: dict, b: dict) -> float:
    if a["triangles"] != b["triangles"] or a["regions"] != b["regions"]:
        raise ValueError("phase comparison requires identical topology and region identity")
    if len(a["vertices"]) != len(b["vertices"]):
        raise ValueError("phase comparison requires identical vertex counts")
    maximum = 0.0
    for av, bv in zip(a["vertices"], b["vertices"]):
        maximum = max(
            maximum,
            math.sqrt(sum((float(av[axis]) - float(bv[axis])) ** 2 for axis in range(3))),
        )
    return maximum


def _validate(source: dict, spec: dict) -> tuple[dict, dict]:
    if spec.get("schema") != EXPECTED_SCHEMA:
        raise ValueError("unsupported compact-tree visual response schema")
    if spec.get("study_id") != EXPECTED_STUDY:
        raise ValueError("compact-tree response study identity drifted")
    if source.get("study_id") != EXPECTED_SOURCE_STUDY:
        raise ValueError("compact-tree source study identity drifted")

    lineage = EXPECTED_LINEAGE
    source_digest = digest(source)
    neutral = build_mesh(source)
    neutral_digest = digest(neutral)
    provenance = spec.get("source_provenance", {})
    expected_source = {
        "repository": "mike-axiom-mir/axm-nature-design",
        "source_study": EXPECTED_SOURCE_STUDY,
        "source_head": EXPECTED_SOURCE_HEAD,
        "source_digest": lineage["source_digest"],
        "migrated_mesh_digest": lineage["proven_reindex_digest"],
        "migration_head": EXPECTED_MIGRATION_HEAD,
    }
    for key, expected in expected_source.items():
        if provenance.get(key) != expected:
            raise ValueError(f"compact-tree source provenance mismatch: {key}")
    if source_digest != lineage["source_digest"]:
        raise ValueError("compact-tree source digest drifted")
    if neutral_digest != lineage["proven_reindex_digest"]:
        raise ValueError("compact-tree migrated neutral mesh digest drifted")

    migration = evaluate_migration(source)
    if migration.get("status") != "PASS_SOURCE_GENERATOR_WINDING_MIGRATION":
        raise ValueError("compact-tree source no longer passes the exact topology migration gate")
    if migration.get("migrated_mesh_digest") != lineage["proven_reindex_digest"]:
        raise ValueError("compact-tree migration result no longer matches pinned migrated mesh")
    if migration.get("topology", {}).get("shared_edge_orientation_conflicts") != 0:
        raise ValueError("compact-tree migrated topology reintroduced shared-edge orientation conflicts")

    mechanism = spec.get("mechanism_provenance", {})
    if mechanism.get("donor_head") != EXPECTED_MECHANISM_HEAD:
        raise ValueError("visual-response mechanism donor head drifted")
    if mechanism.get("donor_profile") != EXPECTED_PROFILE:
        raise ValueError("visual-response mechanism profile drifted")
    if mechanism.get("relationship") != "TRANSFER_MECHANISM_ONLY_WITH_SOURCE_LOCAL_BOUNDED_AMPLITUDE":
        raise ValueError("visual-response mechanism relationship must remain explicit")

    weather = spec.get("weather_provenance", {})
    if weather.get("repository") != "mike-axiom-mir/axm-weather-design":
        raise ValueError("Weather repository provenance drifted")
    if int(weather.get("pr", -1)) != 2 or weather.get("head") != EXPECTED_WEATHER_HEAD:
        raise ValueError("Weather visual-direction provenance drifted")
    if weather.get("semantics") != EXPECTED_WEATHER_SEMANTICS:
        raise ValueError("Weather semantics must remain visual-only")
    wind = weather.get("visual_wind_xy")
    if wind != source.get("weather_handoff", {}).get("visual_wind_xy"):
        raise ValueError("compact-tree candidate visual direction differs from the source handoff")
    if source.get("weather_handoff", {}).get("head") != EXPECTED_WEATHER_HEAD:
        raise ValueError("compact-tree source Weather handoff drifted")
    response._norm2(wind)

    cfg = spec.get("response", {})
    if cfg.get("profile") != EXPECTED_PROFILE:
        raise ValueError("compact-tree response profile drifted")
    duration = float(cfg.get("duration_s", 0.0))
    phase_count = int(cfg.get("phase_count", 0))
    anchor = float(cfg.get("anchor_z_m", -1.0))
    primary = float(cfg.get("primary_height_offset_m", 0.0))
    branch = float(cfg.get("branch_tip_secondary_offset_m", 0.0))
    leaf = float(cfg.get("leaf_tip_secondary_offset_m", 0.0))
    ceiling = float(cfg.get("max_displacement_ceiling_m", 0.0))
    if duration != 0.5 or phase_count != 16:
        raise ValueError("compact-tree bounded response timing contract drifted")
    if abs(anchor - 1.42) > 1e-12:
        raise ValueError("compact-tree lower-anchor contract drifted")
    if min(primary, branch, leaf, ceiling) <= 0.0:
        raise ValueError("compact-tree response component bounds must be positive")
    if abs((primary + branch + leaf) - ceiling) > 1e-12:
        raise ValueError("compact-tree response component budget must equal its ceiling")
    if abs(ceiling - 0.135) > 1e-12:
        raise ValueError("compact-tree response ceiling drifted")
    response._hierarchy_weights(source, neutral, anchor)

    if not all(zone.get("status") == "DECLARED_NOT_DEFORMATION_TESTED" for zone in source.get("flex_zones", [])):
        raise ValueError("compact-tree source flex-zone truth state changed")
    return neutral, migration


def deform(source: dict, spec: dict, neutral: dict, time_s: float) -> dict:
    cfg = spec["response"]
    duration = float(cfg["duration_s"])
    if time_s < -1e-12 or time_s > duration + 1e-12:
        raise ValueError("compact-tree response time outside bounded window")
    phase = 0.0 if abs(time_s) <= 1e-12 or abs(time_s - duration) <= 1e-12 else math.sin(math.pi * time_s / duration)
    wind = response._norm2(spec["weather_provenance"]["visual_wind_xy"])
    weights = response._hierarchy_weights(source, neutral, float(cfg["anchor_z_m"]))
    primary = float(cfg["primary_height_offset_m"])
    branch = float(cfg["branch_tip_secondary_offset_m"])
    leaf = float(cfg["leaf_tip_secondary_offset_m"])
    result = copy.deepcopy(neutral)
    for index, vertex in enumerate(result["vertices"]):
        offset = phase * (
            primary * weights["primary"][index]
            + branch * weights["branch"][index]
            + leaf * weights["leaf"][index]
        )
        vertex[0] = float(vertex[0]) + wind[0] * offset
        vertex[1] = float(vertex[1]) + wind[1] * offset
    return result


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "evidence" / "compact-east-tree-wind-candidate-001"
    out.mkdir(parents=True, exist_ok=True)
    source = load_source(SOURCE)
    spec = load_spec(SPEC)
    neutral, migration = _validate(source, spec)

    cfg = spec["response"]
    duration = float(cfg["duration_s"])
    phase_count = int(cfg["phase_count"])
    anchor = float(cfg["anchor_z_m"])
    ceiling = float(cfg["max_displacement_ceiling_m"])
    wind = spec["weather_provenance"]["visual_wind_xy"]

    samples: list[dict] = []
    meshes: list[dict] = []
    for phase_index in range(phase_count + 1):
        time_s = duration * phase_index / phase_count
        mesh = deform(source, spec, neutral, time_s)
        measured = response.measure_sample(neutral, mesh, wind, anchor)
        phase_value = 0.0 if phase_index in (0, phase_count) else math.sin(math.pi * phase_index / phase_count)
        samples.append({
            "phase_index": phase_index,
            "time_s": time_s,
            "phase": phase_value,
            **measured,
        })
        meshes.append(mesh)
        (out / f"phase_{phase_index:02d}_mesh.json").write_text(
            json.dumps(mesh, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        write_obj(mesh, out / f"phase_{phase_index:02d}.obj")

    peak_index = phase_count // 2
    peak = samples[peak_index]
    peak_mesh = meshes[peak_index]
    neutral_digest = digest(neutral)
    symmetry_residuals = [
        _max_vertex_distance(meshes[index], meshes[phase_count - index])
        for index in range(phase_count + 1)
    ]
    source_height = max(float(v[2]) for v in neutral["vertices"]) - min(float(v[2]) for v in neutral["vertices"])
    leaf_support_gap = response._leaf_support_gap(source, neutral, peak_mesh)

    checks = {
        "exact_migrated_neutral_identity": neutral_digest == EXPECTED_LINEAGE["proven_reindex_digest"],
        "all_17_source_phases_present": len(samples) == 17,
        "neutral_endpoints_exact": digest(meshes[0]) == neutral_digest and digest(meshes[-1]) == neutral_digest,
        "phase_symmetry_bounded": max(symmetry_residuals) <= 1e-12,
        "topology_structurally_valid_all_phases": all(sample["structural"]["pass"] for sample in samples),
        "lower_anchor_preserved_all_phases": all(sample["max_anchor_displacement_m"] <= 1e-12 for sample in samples),
        "peak_response_visible_and_downwind": peak["max_displacement_m"] >= ceiling * 0.85 and peak["min_downwind_projection_m"] >= -1e-12,
        "peak_respects_source_local_ceiling": peak["max_displacement_m"] <= ceiling + 1e-12,
        "crosswind_residual_bounded": max(sample["max_abs_crosswind_drift_m"] for sample in samples) <= 1e-12,
        "leaf_bases_follow_support_without_gap": leaf_support_gap <= 1e-12,
        "source_flex_claims_remain_untested": all(zone.get("status") == "DECLARED_NOT_DEFORMATION_TESTED" for zone in source.get("flex_zones", [])),
        "migration_topology_conflicts_remain_zero": migration["topology"]["shared_edge_orientation_conflicts"] == 0,
    }

    drift_source = copy.deepcopy(source)
    drift_source["study_id"] = "wrong-source"
    negative_source_rejected = False
    try:
        _validate(drift_source, spec)
    except ValueError:
        negative_source_rejected = True
    if not negative_source_rejected:
        raise SystemExit("deliberate compact-tree source identity drift was not rejected")

    drift_spec = copy.deepcopy(spec)
    drift_spec["weather_provenance"]["semantics"] = "PHYSICAL_WIND_SPEED"
    negative_weather_rejected = False
    try:
        _validate(source, drift_spec)
    except ValueError:
        negative_weather_rejected = True
    if not negative_weather_rejected:
        raise SystemExit("deliberate Weather semantic promotion was not rejected")

    checks["negative_source_identity_drift_rejected"] = negative_source_rejected
    checks["negative_physical_weather_promotion_rejected"] = negative_weather_rejected
    state = "PASS_COMPACT_EAST_TREE_BOUNDED_VISUAL_RESPONSE_CANDIDATE" if all(checks.values()) else "FAIL"
    summary = {
        "schema": "axm.nature-compact-east-tree-wind-candidate-evidence/v0.1",
        "state": state,
        "source_study": EXPECTED_SOURCE_STUDY,
        "source_head": EXPECTED_SOURCE_HEAD,
        "source_digest": EXPECTED_LINEAGE["source_digest"],
        "migrated_neutral_mesh_digest": neutral_digest,
        "migration_head": EXPECTED_MIGRATION_HEAD,
        "mechanism_donor_head": EXPECTED_MECHANISM_HEAD,
        "weather_head": EXPECTED_WEATHER_HEAD,
        "weather_semantics": EXPECTED_WEATHER_SEMANTICS,
        "response": cfg,
        "sample_count": len(samples),
        "source_height_m": source_height,
        "ceiling_as_fraction_of_source_height": ceiling / source_height,
        "peak_max_displacement_m": peak["max_displacement_m"],
        "peak_max_downwind_projection_m": peak["max_downwind_projection_m"],
        "max_crosswind_residual_m": max(sample["max_abs_crosswind_drift_m"] for sample in samples),
        "max_anchor_displacement_m": max(sample["max_anchor_displacement_m"] for sample in samples),
        "max_phase_symmetry_residual_m": max(symmetry_residuals),
        "peak_leaf_base_support_gap_m": leaf_support_gap,
        "checks": checks,
        "samples": samples,
        "truth_boundary": {
            "source_json_changed": False,
            "migrated_topology_changed": False,
            "weather_semantics_changed": False,
            "hierarchical_visual_mechanism_transferred": True,
            "source_local_response_parameters_new_candidate": True,
            "declared_flex_zones_validated": False,
            "physical_wind_or_biomechanics": False,
            "continuous_playback_or_timing": False,
            "map_receiving_scene_acceptance": False,
            "final_materials_or_leaf_sidedness": False,
            "target_device_performance": False,
            "gameplay_or_collision": False,
            "art_direction_acceptance": False,
            "canon_or_production_readiness": False,
        },
    }
    (out / "candidate-contract.json").write_text(json.dumps(spec, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    if state != "PASS_COMPACT_EAST_TREE_BOUNDED_VISUAL_RESPONSE_CANDIDATE":
        raise SystemExit("compact-east-tree visual response candidate did not pass its structural evidence gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

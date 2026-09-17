from __future__ import annotations

import copy
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axm_nature_design.organic_form import build_mesh, digest, load_source
from axm_nature_design.wind_response_migrated import (
    MIGRATED_NEUTRAL_MESH_DIGEST,
    build_evidence,
    deform_mesh,
    load_spec,
)

SOURCE = ROOT / "examples" / "sapling_neutral_001.json"
SPEC = ROOT / "examples" / "sapling_wind_response_migrated_001.json"
GEOMETRY_LEAF_HEAD = "da3adbef4de8cddb8f3ebe841d39bb31a8936f5f"
GEOMETRY_LEAF_ARTIFACT_ID = 10441910340
EXPECTED_LEAF_CANDIDATE_DIGEST = "e0b423bd4ff20251a960655441f97e36277da2f5b88a832ecfc5ccfe404bbbea"
EXPECTED_SAMPLE_TIMES = [0.0, 0.125, 0.25, 0.375, 0.5]


def _leaf_regions(mesh: dict) -> dict[str, dict]:
    return {
        str(region["id"]): region
        for region in mesh.get("regions", [])
        if region.get("kind") == "leaf-blade"
    }


def _backface_regions(mesh: dict) -> dict[str, dict]:
    return {
        str(region["source_region"]): region
        for region in mesh.get("regions", [])
        if region.get("kind") == "leaf-blade-backface"
    }


def _derive_duplicate_mapping(neutral: dict, candidate: dict) -> dict[int, int]:
    baseline_vertices = len(neutral["vertices"])
    if candidate["vertices"][:baseline_vertices] != neutral["vertices"]:
        raise ValueError("Geometry leaf candidate no longer preserves the migrated baseline vertex prefix")
    if candidate["triangles"][:len(neutral["triangles"])] != neutral["triangles"]:
        raise ValueError("Geometry leaf candidate no longer preserves the migrated baseline triangle prefix")
    if candidate["regions"][:len(neutral["regions"])] != neutral["regions"]:
        raise ValueError("Geometry leaf candidate no longer preserves the migrated baseline region prefix")

    fronts = _leaf_regions(neutral)
    backs = _backface_regions(candidate)
    if len(fronts) != 25 or set(fronts) != set(backs):
        raise ValueError("Geometry leaf candidate no longer contains one exact backface region per authored leaf")

    mapping: dict[int, int] = {}
    for source_region, front in fronts.items():
        back = backs[source_region]
        front_start = int(front["triangle_start"])
        front_count = int(front["triangle_count"])
        back_start = int(back["triangle_start"])
        back_count = int(back["triangle_count"])
        if front_count != 2 or back_count != 2:
            raise ValueError("leaf front/back region must remain exactly two triangles")
        front_triangles = neutral["triangles"][front_start:front_start + front_count]
        back_triangles = candidate["triangles"][back_start:back_start + back_count]
        for front_triangle, back_triangle in zip(front_triangles, back_triangles):
            if len(front_triangle) != 3 or len(back_triangle) != 3:
                raise ValueError("leaf triangle is malformed")
            expected_source_order = [int(front_triangle[0]), int(front_triangle[2]), int(front_triangle[1])]
            for source_index, duplicate_index_value in zip(expected_source_order, back_triangle):
                duplicate_index = int(duplicate_index_value)
                if duplicate_index < baseline_vertices:
                    raise ValueError("leaf backface reused a baseline vertex instead of the disjoint duplicate domain")
                if candidate["vertices"][duplicate_index] != neutral["vertices"][source_index]:
                    raise ValueError("leaf duplicate vertex is not exactly position-bound to its source front vertex")
                previous = mapping.get(duplicate_index)
                if previous is not None and previous != source_index:
                    raise ValueError("leaf duplicate vertex maps inconsistently across its two triangles")
                mapping[duplicate_index] = source_index

    expected_duplicates = len(candidate["vertices"]) - baseline_vertices
    if expected_duplicates != 100 or len(mapping) != expected_duplicates:
        raise ValueError("leaf duplicate mapping does not cover the exact 100-vertex Geometry candidate domain")
    if set(mapping) != set(range(baseline_vertices, len(candidate["vertices"]))):
        raise ValueError("leaf duplicate mapping does not cover the exact appended vertex range")
    return mapping


def _apply_response_to_candidate(candidate_neutral: dict, deformed_front: dict, mapping: dict[int, int]) -> dict:
    baseline_vertices = len(deformed_front["vertices"])
    if candidate_neutral["triangles"][:len(deformed_front["triangles"])] != deformed_front["triangles"]:
        raise ValueError("deformed front topology drifted from the Geometry candidate baseline prefix")
    if candidate_neutral["regions"][:len(deformed_front["regions"])] != deformed_front["regions"]:
        raise ValueError("deformed front region identity drifted from the Geometry candidate baseline prefix")
    result = copy.deepcopy(candidate_neutral)
    result["vertices"][:baseline_vertices] = copy.deepcopy(deformed_front["vertices"])
    for duplicate_index, source_index in mapping.items():
        result["vertices"][duplicate_index] = list(deformed_front["vertices"][source_index])
    return result


def _max_duplicate_gap(mesh: dict, mapping: dict[int, int]) -> float:
    maximum = 0.0
    for duplicate_index, source_index in mapping.items():
        a = mesh["vertices"][duplicate_index]
        b = mesh["vertices"][source_index]
        distance = math.sqrt(sum((float(a[axis]) - float(b[axis])) ** 2 for axis in range(3)))
        maximum = max(maximum, distance)
    return maximum


def _assert_dynamic_candidate(mesh: dict, mapping: dict[int, int]) -> None:
    if len(mesh["vertices"]) != 490 or len(mesh["triangles"]) != 620:
        raise ValueError("dynamic leaf candidate counts drifted")
    if _max_duplicate_gap(mesh, mapping) > 1e-12:
        raise ValueError("dynamic leaf backfaces detached from their exact source front vertices")


def main() -> int:
    if len(sys.argv) not in (2, 3):
        raise SystemExit("usage: build_sapling_wind_leaf_backface_dynamic.py GEOMETRY_EVIDENCE_DIR [OUTPUT_DIR]")
    donor_dir = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) == 3 else ROOT / "evidence" / "sapling-wind-leaf-backface-dynamic-001"
    out.mkdir(parents=True, exist_ok=True)

    donor_head = (donor_dir / "exact-head.txt").read_text(encoding="utf-8").strip()
    if donor_head != GEOMETRY_LEAF_HEAD:
        raise SystemExit(f"Geometry leaf donor head drifted: {donor_head}")
    donor_summary = json.loads((donor_dir / "summary.json").read_text(encoding="utf-8"))
    donor_report = json.loads((donor_dir / "sapling-neutral-001-report.json").read_text(encoding="utf-8"))
    candidate_neutral = json.loads((donor_dir / "sapling-neutral-001-candidate-mesh.json").read_text(encoding="utf-8"))
    if donor_summary.get("state") != "PASS_EXPLICIT_LEAF_BACKFACE_CANDIDATE_3_REAL_OUTPUTS":
        raise SystemExit("Geometry leaf donor evidence is not green")
    if donor_report.get("status") != "PASS_EXPLICIT_DISJOINT_LEAF_BACKFACE_CANDIDATE":
        raise SystemExit("sapling Geometry leaf donor report is not green")
    if donor_report.get("baseline_mesh_digest") != MIGRATED_NEUTRAL_MESH_DIGEST:
        raise SystemExit("Geometry leaf donor baseline no longer matches migrated sapling")
    if donor_report.get("candidate_mesh_digest") != EXPECTED_LEAF_CANDIDATE_DIGEST:
        raise SystemExit("Geometry leaf candidate identity drifted")
    if digest(candidate_neutral) != EXPECTED_LEAF_CANDIDATE_DIGEST:
        raise SystemExit("Geometry leaf candidate payload bytes do not match its pinned digest")

    source = load_source(SOURCE)
    spec = load_spec(SPEC)
    retained = build_evidence(source, spec)
    if retained.get("state") != "PASS_BOUNDED_VISUAL_WIND_RESPONSE":
        raise SystemExit("migrated VFX response prerequisite is not green")
    sample_times = [float(value) for value in spec["response"]["sample_times_s"]]
    if sample_times != EXPECTED_SAMPLE_TIMES:
        raise SystemExit(f"VFX retained sample identity drifted: {sample_times!r}")

    neutral = build_mesh(source)
    if digest(neutral) != MIGRATED_NEUTRAL_MESH_DIGEST:
        raise SystemExit("current migrated neutral mesh identity drifted")
    mapping = _derive_duplicate_mapping(neutral, candidate_neutral)

    samples = []
    candidate_meshes = []
    for time_s in sample_times:
        millis = int(round(time_s * 1000.0))
        front = deform_mesh(source, spec, time_s)
        candidate = _apply_response_to_candidate(candidate_neutral, front, mapping)
        _assert_dynamic_candidate(candidate, mapping)
        front_name = f"frame_{millis:04d}ms_front_mesh.json"
        candidate_name = f"frame_{millis:04d}ms_leaf_backface_mesh.json"
        (out / front_name).write_text(json.dumps(front, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (out / candidate_name).write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        candidate_meshes.append(candidate)
        samples.append({
            "time_s": time_s,
            "front_mesh_digest": digest(front),
            "candidate_mesh_digest": digest(candidate),
            "max_duplicate_position_gap_m": _max_duplicate_gap(candidate, mapping),
            "front_payload": front_name,
            "candidate_payload": candidate_name,
        })

    if samples[0]["candidate_mesh_digest"] != EXPECTED_LEAF_CANDIDATE_DIGEST:
        raise SystemExit("dynamic candidate does not reproduce exact Geometry neutral identity at t=0")
    if samples[-1]["candidate_mesh_digest"] != EXPECTED_LEAF_CANDIDATE_DIGEST:
        raise SystemExit("dynamic candidate does not return exactly to Geometry neutral identity")
    if samples[1]["candidate_mesh_digest"] != samples[3]["candidate_mesh_digest"]:
        raise SystemExit("half-sine symmetric leaf candidate phases no longer match exactly")
    if samples[0]["candidate_mesh_digest"] == samples[2]["candidate_mesh_digest"]:
        raise SystemExit("peak dynamic leaf candidate is not distinct from neutral")

    mutated = copy.deepcopy(candidate_meshes[2])
    first_duplicate = min(mapping)
    mutated["vertices"][first_duplicate][0] = float(mutated["vertices"][first_duplicate][0]) + 0.001
    negative_control_rejected = False
    try:
        _assert_dynamic_candidate(mutated, mapping)
    except ValueError:
        negative_control_rejected = True
    if not negative_control_rejected:
        raise SystemExit("deliberate leaf duplicate deformation drift was not rejected")

    summary = {
        "schema": "axm.nature-leaf-backface-dynamic-vfx-rebind/v0.1",
        "state": "PASS_EXPLICIT_LEAF_BACKFACE_WIND_RESPONSE_REBIND",
        "geometry_leaf_head": GEOMETRY_LEAF_HEAD,
        "geometry_leaf_artifact_id": GEOMETRY_LEAF_ARTIFACT_ID,
        "geometry_leaf_candidate_digest": EXPECTED_LEAF_CANDIDATE_DIGEST,
        "migrated_neutral_mesh_digest": MIGRATED_NEUTRAL_MESH_DIGEST,
        "response_profile": spec["response"]["profile"],
        "sample_times_s": sample_times,
        "sample_count": len(samples),
        "front_vertices": len(neutral["vertices"]),
        "front_triangles": len(neutral["triangles"]),
        "candidate_vertices": len(candidate_neutral["vertices"]),
        "candidate_triangles": len(candidate_neutral["triangles"]),
        "leaf_backface_duplicate_vertices": len(mapping),
        "max_duplicate_position_gap_m": max(sample["max_duplicate_position_gap_m"] for sample in samples),
        "negative_control_duplicate_drift_rejected": negative_control_rejected,
        "samples": samples,
        "truth_boundary": {
            "geometry_leaf_candidate_reauthored": False,
            "vfx_response_profile_changed": False,
            "weather_semantics_changed": False,
            "explicit_leaf_backfaces_deformed_with_source_fronts": True,
            "target_renderer_evidence": False,
            "perceptual_or_final_visual_acceptance": False,
            "physical_wind_or_biomechanics": False,
            "gameplay_or_collision": False,
            "runtime_cost_or_target_performance": False,
            "canon_or_production_readiness": False,
        },
    }
    (out / "leaf-dynamic-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

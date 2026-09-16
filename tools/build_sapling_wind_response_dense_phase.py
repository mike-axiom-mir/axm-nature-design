from __future__ import annotations

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
    measure_sample,
)

SOURCE = ROOT / "examples" / "sapling_neutral_001.json"
SPEC = ROOT / "examples" / "sapling_wind_response_migrated_001.json"
SUBDIVISIONS_PER_RETAINED_INTERVAL = 4
EXPECTED_RETAINED_TIMES = [0.0, 0.125, 0.25, 0.375, 0.5]


def _max_vertex_distance(a: dict, b: dict) -> float:
    if a["triangles"] != b["triangles"] or len(a["vertices"]) != len(b["vertices"]):
        raise ValueError("dense phase comparison requires identical topology")
    maximum = 0.0
    for av, bv in zip(a["vertices"], b["vertices"]):
        distance = math.sqrt(sum((float(av[i]) - float(bv[i])) ** 2 for i in range(3)))
        maximum = max(maximum, distance)
    return maximum


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "evidence" / "sapling-wind-response-dense-phase-001"
    out.mkdir(parents=True, exist_ok=True)

    source = load_source(SOURCE)
    spec = load_spec(SPEC)
    retained = build_evidence(source, spec)
    if retained["state"] != "PASS_BOUNDED_VISUAL_WIND_RESPONSE":
        raise SystemExit("retained migrated visual response is not green")

    retained_times = [float(value) for value in spec["response"]["sample_times_s"]]
    if retained_times != EXPECTED_RETAINED_TIMES:
        raise SystemExit(f"retained response sample identity drifted: {retained_times!r}")

    duration = float(spec["response"]["duration_s"])
    dense_interval_count = (len(retained_times) - 1) * SUBDIVISIONS_PER_RETAINED_INTERVAL
    dense_times = [duration * index / dense_interval_count for index in range(dense_interval_count + 1)]
    expected_anchor_indices = [index * SUBDIVISIONS_PER_RETAINED_INTERVAL for index in range(len(retained_times))]

    neutral = build_mesh(source)
    if digest(neutral) != MIGRATED_NEUTRAL_MESH_DIGEST:
        raise SystemExit("migrated neutral mesh identity drifted before dense phase build")

    retained_by_time = {round(float(sample["time_s"]), 12): sample for sample in retained["samples"]}
    meshes: list[dict] = []
    samples: list[dict] = []
    for index, time_s in enumerate(dense_times):
        mesh = deform_mesh(source, spec, time_s)
        measured = measure_sample(
            neutral,
            mesh,
            spec["weather_provenance"]["visual_wind_xy"],
            float(spec["response"]["anchor_z_m"]),
        )
        if not measured["structural"]["pass"]:
            raise SystemExit(f"dense phase topology failed at index {index}")
        if measured["max_anchor_displacement_m"] > 1e-12:
            raise SystemExit(f"dense phase lower anchor drifted at index {index}")
        payload_name = f"phase_{index:02d}_mesh.json"
        (out / payload_name).write_text(json.dumps(mesh, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        meshes.append(mesh)
        samples.append(
            {
                "index": index,
                "time_s": time_s,
                "mesh_digest": measured["mesh_digest"],
                "max_displacement_m": measured["max_displacement_m"],
                "max_anchor_displacement_m": measured["max_anchor_displacement_m"],
                "max_abs_crosswind_drift_m": measured["max_abs_crosswind_drift_m"],
                "payload": payload_name,
            }
        )

    anchor_checks = []
    for retained_time, dense_index in zip(retained_times, expected_anchor_indices):
        dense_sample = samples[dense_index]
        retained_sample = retained_by_time[round(retained_time, 12)]
        exact = dense_sample["mesh_digest"] == retained_sample["mesh_digest"]
        anchor_checks.append(
            {
                "time_s": retained_time,
                "dense_index": dense_index,
                "dense_mesh_digest": dense_sample["mesh_digest"],
                "retained_mesh_digest": retained_sample["mesh_digest"],
                "exact_digest_match": exact,
            }
        )
        if not exact:
            raise SystemExit(f"dense phase anchor {retained_time} no longer matches retained source sample")

    adjacent_steps = [_max_vertex_distance(meshes[index], meshes[index + 1]) for index in range(len(meshes) - 1)]
    if any(step <= 0.0 for step in adjacent_steps):
        raise SystemExit("dense source sequence contains an unchanged adjacent mesh")

    symmetry_residuals = [_max_vertex_distance(meshes[index], meshes[-1 - index]) for index in range(len(meshes))]
    max_symmetry_residual = max(symmetry_residuals, default=0.0)
    if max_symmetry_residual > 1e-12:
        raise SystemExit(f"dense half-sine phase symmetry drifted: {max_symmetry_residual}")

    rising = [sample["max_displacement_m"] for sample in samples[: len(samples) // 2 + 1]]
    falling = [sample["max_displacement_m"] for sample in samples[len(samples) // 2 :]]
    if any(b + 1e-12 < a for a, b in zip(rising, rising[1:])):
        raise SystemExit("dense source displacement is not monotonic toward peak")
    if any(b > a + 1e-12 for a, b in zip(falling, falling[1:])):
        raise SystemExit("dense source displacement is not monotonic after peak")

    if samples[0]["mesh_digest"] != MIGRATED_NEUTRAL_MESH_DIGEST or samples[-1]["mesh_digest"] != MIGRATED_NEUTRAL_MESH_DIGEST:
        raise SystemExit("dense source sequence no longer returns exactly to migrated neutral")

    summary = {
        "schema": "axm.nature-migrated-wind-dense-phase-source-evidence/v0.1",
        "state": "PASS_MIGRATED_WOODY_WIND_RESPONSE_DENSE_SOURCE_PHASES",
        "migrated_neutral_mesh_digest": MIGRATED_NEUTRAL_MESH_DIGEST,
        "response_profile": spec["response"]["profile"],
        "duration_s": duration,
        "dense_phase_count": len(samples),
        "dense_interval_count": dense_interval_count,
        "phase_step_s": duration / dense_interval_count,
        "retained_anchor_indices": expected_anchor_indices,
        "retained_anchor_checks": anchor_checks,
        "samples": samples,
        "max_adjacent_vertex_step_m": max(adjacent_steps, default=0.0),
        "min_adjacent_vertex_step_m": min(adjacent_steps, default=0.0),
        "max_half_sine_symmetry_residual_m": max_symmetry_residual,
        "truth_boundary": {
            "source_response_reauthored": False,
            "weather_semantics_changed": False,
            "retained_five_sample_evidence_replaced": False,
            "dense_states_are_direct_source_evaluations": True,
            "wall_clock_pacing_tested": False,
            "perceptual_smoothness_claimed": False,
            "physical_wind_or_biomechanics": False,
            "gameplay_or_collision": False,
            "target_device_performance": False,
        },
    }
    (out / "dense-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

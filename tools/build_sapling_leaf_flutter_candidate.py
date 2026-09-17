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
    deform_mesh,
    load_spec,
)

SOURCE = ROOT / "examples" / "sapling_neutral_001.json"
SPEC = ROOT / "examples" / "sapling_wind_response_migrated_001.json"

GEOMETRY_LEAF_HEAD = "da3adbef4de8cddb8f3ebe841d39bb31a8936f5f"
EXPECTED_LEAF_CANDIDATE_DIGEST = "e0b423bd4ff20251a960655441f97e36277da2f5b88a832ecfc5ccfe404bbbea"

DENSE_INTERVALS = 16
FLUTTER_CYCLES_PER_WINDOW = 3.0
MAX_TWIST_DEG = 5.0
LEAF_PHASE_STEP_RAD = 0.73
MAX_ALLOWED_FLUTTER_VERTEX_DELTA_M = 0.0085


def _v_sub(a, b):
    return [float(a[i]) - float(b[i]) for i in range(3)]


def _v_add(a, b):
    return [float(a[i]) + float(b[i]) for i in range(3)]


def _v_mul(a, s):
    return [float(a[i]) * float(s) for i in range(3)]


def _dot(a, b):
    return sum(float(a[i]) * float(b[i]) for i in range(3))


def _cross(a, b):
    return [
        float(a[1]) * float(b[2]) - float(a[2]) * float(b[1]),
        float(a[2]) * float(b[0]) - float(a[0]) * float(b[2]),
        float(a[0]) * float(b[1]) - float(a[1]) * float(b[0]),
    ]


def _length(v):
    return math.sqrt(_dot(v, v))


def _norm(v):
    length = _length(v)
    if length <= 1e-12:
        raise ValueError("zero-length leaf axis")
    return [float(v[i]) / length for i in range(3)]


def _distance(a, b):
    return _length(_v_sub(a, b))


def _rotate_about_axis(point, origin, axis, angle_rad):
    # Rodrigues rotation. This is a visual-only leaf-plane twist around the
    # authored blade base->tip axis; it does not model force or biomechanics.
    relative = _v_sub(point, origin)
    cosine = math.cos(angle_rad)
    sine = math.sin(angle_rad)
    term_a = _v_mul(relative, cosine)
    term_b = _v_mul(_cross(axis, relative), sine)
    term_c = _v_mul(axis, _dot(axis, relative) * (1.0 - cosine))
    return _v_add(origin, _v_add(term_a, _v_add(term_b, term_c)))


def _leaf_regions(mesh: dict) -> list[dict]:
    return [region for region in mesh.get("regions", []) if region.get("kind") == "leaf-blade"]


def _backface_regions(mesh: dict) -> dict[str, dict]:
    return {
        str(region["source_region"]): region
        for region in mesh.get("regions", [])
        if region.get("kind") == "leaf-blade-backface"
    }


def _derive_duplicate_mapping(neutral: dict, candidate: dict) -> dict[int, int]:
    baseline_vertices = len(neutral["vertices"])
    if candidate["vertices"][:baseline_vertices] != neutral["vertices"]:
        raise ValueError("Geometry leaf candidate no longer preserves baseline vertices")
    if candidate["triangles"][:len(neutral["triangles"])] != neutral["triangles"]:
        raise ValueError("Geometry leaf candidate no longer preserves baseline triangles")
    if candidate["regions"][:len(neutral["regions"])] != neutral["regions"]:
        raise ValueError("Geometry leaf candidate no longer preserves baseline regions")

    backs = _backface_regions(candidate)
    fronts = {str(region["id"]): region for region in _leaf_regions(neutral)}
    if len(fronts) != 25 or set(fronts) != set(backs):
        raise ValueError("expected one explicit backface region for every authored leaf")

    mapping: dict[int, int] = {}
    for source_region, front in fronts.items():
        back = backs[source_region]
        front_triangles = neutral["triangles"][
            int(front["triangle_start"]):int(front["triangle_start"]) + int(front["triangle_count"])
        ]
        back_triangles = candidate["triangles"][
            int(back["triangle_start"]):int(back["triangle_start"]) + int(back["triangle_count"])
        ]
        if len(front_triangles) != 2 or len(back_triangles) != 2:
            raise ValueError("leaf front/back region triangle count drifted")
        for front_triangle, back_triangle in zip(front_triangles, back_triangles):
            expected_source_order = [
                int(front_triangle[0]),
                int(front_triangle[2]),
                int(front_triangle[1]),
            ]
            for source_index, duplicate_index_value in zip(expected_source_order, back_triangle):
                duplicate_index = int(duplicate_index_value)
                if duplicate_index < baseline_vertices:
                    raise ValueError("backface candidate reused front vertex domain")
                if candidate["vertices"][duplicate_index] != neutral["vertices"][source_index]:
                    raise ValueError("backface duplicate is not exactly co-located with source front vertex")
                previous = mapping.get(duplicate_index)
                if previous is not None and previous != source_index:
                    raise ValueError("backface duplicate maps to inconsistent source vertices")
                mapping[duplicate_index] = source_index

    if len(mapping) != 100:
        raise ValueError("expected exact 100-vertex explicit leaf backface domain")
    if set(mapping) != set(range(baseline_vertices, len(candidate["vertices"]))):
        raise ValueError("backface duplicate map does not cover exact appended vertex domain")
    return mapping


def _cluster_centers(source: dict) -> dict[str, list[float]]:
    return {str(cluster["id"]): [float(v) for v in cluster["center"]] for cluster in source["leaf_clusters"]}


def _leaf_topology(neutral: dict, source: dict) -> list[dict]:
    centers = _cluster_centers(source)
    leaves: list[dict] = []
    for order, region in enumerate(_leaf_regions(neutral)):
        region_id = str(region["id"])
        parts = region_id.split(":")
        if len(parts) != 3 or parts[0] != "leaf":
            raise ValueError(f"unexpected leaf region id: {region_id}")
        cluster_id = parts[1]
        if cluster_id not in centers:
            raise ValueError(f"leaf region references unknown source cluster: {cluster_id}")
        start = int(region["triangle_start"])
        count = int(region["triangle_count"])
        triangles = neutral["triangles"][start:start + count]
        if len(triangles) != 2:
            raise ValueError("leaf region must remain two triangles")
        shared = set(int(v) for v in triangles[0]).intersection(int(v) for v in triangles[1])
        unique = sorted(set(int(v) for tri in triangles for v in tri))
        if len(shared) != 2 or len(unique) != 4:
            raise ValueError("leaf blade topology no longer forms a four-vertex lozenge")
        center = centers[cluster_id]
        shared_sorted = sorted(shared, key=lambda idx: _distance(neutral["vertices"][idx], center))
        base_index, tip_index = shared_sorted[0], shared_sorted[1]
        if _distance(neutral["vertices"][base_index], center) > 1e-12:
            raise ValueError("could not recover exact authored leaf base from source cluster center")
        side_indices = [index for index in unique if index not in shared]
        if len(side_indices) != 2:
            raise ValueError("leaf blade side-vertex recovery failed")
        leaves.append(
            {
                "order": order,
                "region_id": region_id,
                "base_index": base_index,
                "tip_index": tip_index,
                "side_indices": side_indices,
            }
        )
    if len(leaves) != 25:
        raise ValueError(f"expected 25 authored leaf blades, got {len(leaves)}")
    return leaves


def _compose_explicit_backfaces(candidate_neutral: dict, front_mesh: dict, mapping: dict[int, int]) -> dict:
    front_vertices = len(front_mesh["vertices"])
    if candidate_neutral["triangles"][:len(front_mesh["triangles"])] != front_mesh["triangles"]:
        raise ValueError("front topology drifted from explicit backface candidate baseline")
    if candidate_neutral["regions"][:len(front_mesh["regions"])] != front_mesh["regions"]:
        raise ValueError("front regions drifted from explicit backface candidate baseline")
    result = copy.deepcopy(candidate_neutral)
    result["vertices"][:front_vertices] = copy.deepcopy(front_mesh["vertices"])
    for duplicate_index, source_index in mapping.items():
        result["vertices"][duplicate_index] = list(front_mesh["vertices"][source_index])
    return result


def _apply_flutter(front_mesh: dict, leaves: list[dict], time_s: float, duration_s: float) -> tuple[dict, list[dict]]:
    if duration_s <= 0.0:
        raise ValueError("duration must be positive")
    normalized = max(0.0, min(1.0, float(time_s) / duration_s))
    envelope = math.sin(math.pi * normalized)
    max_twist_rad = math.radians(MAX_TWIST_DEG)
    result = copy.deepcopy(front_mesh)
    leaf_records = []

    for leaf in leaves:
        order = int(leaf["order"])
        phase = math.tau * FLUTTER_CYCLES_PER_WINDOW * normalized + LEAF_PHASE_STEP_RAD * order
        angle = max_twist_rad * envelope * math.sin(phase)
        base_index = int(leaf["base_index"])
        tip_index = int(leaf["tip_index"])
        base = [float(v) for v in front_mesh["vertices"][base_index]]
        tip = [float(v) for v in front_mesh["vertices"][tip_index]]
        axis = _norm(_v_sub(tip, base))

        maximum = 0.0
        for side_index in leaf["side_indices"]:
            side_index = int(side_index)
            before = [float(v) for v in front_mesh["vertices"][side_index]]
            after = _rotate_about_axis(before, base, axis, angle)
            result["vertices"][side_index] = after
            maximum = max(maximum, _distance(before, after))

        leaf_records.append(
            {
                "region_id": leaf["region_id"],
                "order": order,
                "twist_deg": math.degrees(angle),
                "max_side_vertex_delta_m": maximum,
            }
        )
    return result, leaf_records


def _max_vertex_delta(a: dict, b: dict) -> float:
    if a["triangles"] != b["triangles"] or len(a["vertices"]) != len(b["vertices"]):
        raise ValueError("vertex delta comparison requires identical topology")
    return max((_distance(av, bv) for av, bv in zip(a["vertices"], b["vertices"])), default=0.0)


def _non_leaf_vertex_indices(neutral: dict) -> set[int]:
    leaf_indices: set[int] = set()
    for region in _leaf_regions(neutral):
        start = int(region["triangle_start"])
        count = int(region["triangle_count"])
        for triangle in neutral["triangles"][start:start + count]:
            leaf_indices.update(int(index) for index in triangle)
    return set(range(len(neutral["vertices"]))) - leaf_indices


def _max_selected_vertex_delta(a: dict, b: dict, indices: set[int]) -> float:
    return max((_distance(a["vertices"][i], b["vertices"][i]) for i in indices), default=0.0)


def _max_duplicate_gap(mesh: dict, mapping: dict[int, int]) -> float:
    return max(
        (_distance(mesh["vertices"][duplicate], mesh["vertices"][source]) for duplicate, source in mapping.items()),
        default=0.0,
    )


def main() -> int:
    if len(sys.argv) not in (2, 3):
        raise SystemExit(
            "usage: build_sapling_leaf_flutter_candidate.py GEOMETRY_EVIDENCE_DIR [OUTPUT_DIR]"
        )
    donor_dir = Path(sys.argv[1])
    out = (
        Path(sys.argv[2])
        if len(sys.argv) == 3
        else ROOT / "evidence" / "sapling-leaf-flutter-candidate-001"
    )
    out.mkdir(parents=True, exist_ok=True)

    donor_head = (donor_dir / "exact-head.txt").read_text(encoding="utf-8").strip()
    if donor_head != GEOMETRY_LEAF_HEAD:
        raise SystemExit(f"Geometry leaf donor head drifted: {donor_head}")
    donor_summary = json.loads((donor_dir / "summary.json").read_text(encoding="utf-8"))
    donor_report = json.loads((donor_dir / "sapling-neutral-001-report.json").read_text(encoding="utf-8"))
    candidate_neutral = json.loads(
        (donor_dir / "sapling-neutral-001-candidate-mesh.json").read_text(encoding="utf-8")
    )
    if donor_summary.get("state") != "PASS_EXPLICIT_LEAF_BACKFACE_CANDIDATE_3_REAL_OUTPUTS":
        raise SystemExit("Geometry leaf donor evidence is not green")
    if donor_report.get("candidate_mesh_digest") != EXPECTED_LEAF_CANDIDATE_DIGEST:
        raise SystemExit("Geometry leaf donor candidate identity drifted")
    if digest(candidate_neutral) != EXPECTED_LEAF_CANDIDATE_DIGEST:
        raise SystemExit("Geometry leaf candidate bytes do not match pinned digest")

    source = load_source(SOURCE)
    spec = load_spec(SPEC)
    neutral = build_mesh(source)
    if digest(neutral) != MIGRATED_NEUTRAL_MESH_DIGEST:
        raise SystemExit("migrated neutral mesh identity drifted")
    mapping = _derive_duplicate_mapping(neutral, candidate_neutral)
    leaves = _leaf_topology(neutral, source)
    non_leaf_indices = _non_leaf_vertex_indices(neutral)

    duration_s = float(spec["response"]["duration_s"])
    dense_times = [duration_s * index / DENSE_INTERVALS for index in range(DENSE_INTERVALS + 1)]
    samples = []
    max_flutter_delta = 0.0
    max_non_leaf_delta = 0.0
    max_duplicate_gap = 0.0
    max_abs_twist = 0.0

    for index, time_s in enumerate(dense_times):
        baseline_front = deform_mesh(source, spec, time_s)
        flutter_front, leaf_records = _apply_flutter(baseline_front, leaves, time_s, duration_s)
        baseline_candidate = _compose_explicit_backfaces(candidate_neutral, baseline_front, mapping)
        flutter_candidate = _compose_explicit_backfaces(candidate_neutral, flutter_front, mapping)

        flutter_delta = _max_vertex_delta(baseline_front, flutter_front)
        non_leaf_delta = _max_selected_vertex_delta(baseline_front, flutter_front, non_leaf_indices)
        duplicate_gap = _max_duplicate_gap(flutter_candidate, mapping)
        sample_abs_twist = max((abs(float(record["twist_deg"])) for record in leaf_records), default=0.0)

        if flutter_delta > MAX_ALLOWED_FLUTTER_VERTEX_DELTA_M + 1e-12:
            raise SystemExit(
                f"leaf flutter exceeded bounded visual displacement at phase {index}: {flutter_delta}"
            )
        if non_leaf_delta > 1e-12:
            raise SystemExit(f"leaf flutter moved non-leaf geometry at phase {index}: {non_leaf_delta}")
        if duplicate_gap > 1e-12:
            raise SystemExit(f"explicit leaf backfaces detached at phase {index}: {duplicate_gap}")

        baseline_name = f"phase_{index:02d}_baseline_candidate_mesh.json"
        flutter_name = f"phase_{index:02d}_flutter_candidate_mesh.json"
        (out / baseline_name).write_text(
            json.dumps(baseline_candidate, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (out / flutter_name).write_text(
            json.dumps(flutter_candidate, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        samples.append(
            {
                "index": index,
                "time_s": time_s,
                "baseline_candidate_digest": digest(baseline_candidate),
                "flutter_candidate_digest": digest(flutter_candidate),
                "max_flutter_vertex_delta_m": flutter_delta,
                "max_non_leaf_vertex_delta_m": non_leaf_delta,
                "max_duplicate_position_gap_m": duplicate_gap,
                "max_abs_twist_deg": sample_abs_twist,
                "leaf_records": leaf_records,
                "baseline_payload": baseline_name,
                "flutter_payload": flutter_name,
            }
        )
        max_flutter_delta = max(max_flutter_delta, flutter_delta)
        max_non_leaf_delta = max(max_non_leaf_delta, non_leaf_delta)
        max_duplicate_gap = max(max_duplicate_gap, duplicate_gap)
        max_abs_twist = max(max_abs_twist, sample_abs_twist)

    if samples[0]["baseline_candidate_digest"] != samples[0]["flutter_candidate_digest"]:
        raise SystemExit("flutter candidate must be exact baseline at neutral start")
    if samples[-1]["baseline_candidate_digest"] != samples[-1]["flutter_candidate_digest"]:
        raise SystemExit("flutter candidate must be exact baseline at neutral return")
    if not any(
        sample["baseline_candidate_digest"] != sample["flutter_candidate_digest"]
        for sample in samples[1:-1]
    ):
        raise SystemExit("leaf flutter candidate produced no distinct interior source state")
    if max_abs_twist > MAX_TWIST_DEG + 1e-12:
        raise SystemExit("leaf flutter twist exceeded declared cap")

    mutated = copy.deepcopy(json.loads((out / samples[8]["flutter_payload"]).read_text(encoding="utf-8")))
    first_duplicate = min(mapping)
    mutated["vertices"][first_duplicate][0] = float(mutated["vertices"][first_duplicate][0]) + 0.001
    negative_control_rejected = _max_duplicate_gap(mutated, mapping) > 1e-12
    if not negative_control_rejected:
        raise SystemExit("deliberate leaf backface detachment was not detected")

    summary = {
        "schema": "axm.nature-leaf-flutter-vfx-candidate/v0.1",
        "state": "PASS_BOUNDED_DETERMINISTIC_LEAF_FLUTTER_SOURCE_CANDIDATE",
        "geometry_leaf_head": GEOMETRY_LEAF_HEAD,
        "geometry_leaf_candidate_digest": EXPECTED_LEAF_CANDIDATE_DIGEST,
        "migrated_neutral_mesh_digest": MIGRATED_NEUTRAL_MESH_DIGEST,
        "effect": {
            "kind": "leaf_plane_twist",
            "scope": "leaf side vertices only; authored base and tip vertices remain on the inherited wind response",
            "duration_s": duration_s,
            "dense_phase_count": len(samples),
            "phase_step_s": duration_s / DENSE_INTERVALS,
            "flutter_cycles_per_window": FLUTTER_CYCLES_PER_WINDOW,
            "max_twist_deg": MAX_TWIST_DEG,
            "leaf_phase_step_rad": LEAF_PHASE_STEP_RAD,
            "envelope": "sin(pi * normalized_time), exact zero at both response endpoints",
            "max_allowed_flutter_vertex_delta_m": MAX_ALLOWED_FLUTTER_VERTEX_DELTA_M,
        },
        "leaf_count": len(leaves),
        "front_vertices": len(neutral["vertices"]),
        "front_triangles": len(neutral["triangles"]),
        "candidate_vertices": len(candidate_neutral["vertices"]),
        "candidate_triangles": len(candidate_neutral["triangles"]),
        "max_observed_flutter_vertex_delta_m": max_flutter_delta,
        "max_observed_non_leaf_vertex_delta_m": max_non_leaf_delta,
        "max_observed_duplicate_position_gap_m": max_duplicate_gap,
        "max_observed_abs_twist_deg": max_abs_twist,
        "negative_control_duplicate_detachment_rejected": negative_control_rejected,
        "samples": samples,
        "truth_boundary": {
            "existing_wind_response_reauthored": False,
            "geometry_leaf_candidate_reauthored": False,
            "weather_semantics_changed": False,
            "deterministic_visual_leaf_flutter_candidate_added": True,
            "leaf_base_or_tip_vertices_fluttered": False,
            "non_leaf_geometry_fluttered": False,
            "physical_wind_or_biomechanics": False,
            "gameplay_or_collision": False,
            "perceptual_naturalness_or_final_art_acceptance": False,
            "wall_clock_timing_or_target_performance": False,
            "canon_or_production_readiness": False,
        },
    }
    (out / "leaf-flutter-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

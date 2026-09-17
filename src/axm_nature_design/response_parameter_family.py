from __future__ import annotations

import copy
import hashlib
import json
import math
from typing import Iterable

EXPECTED_STATE_COUNT = 17
EXPECTED_INTERVAL_COUNT = 16


def canonical_digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def half_sine_weights(interval_count: int = EXPECTED_INTERVAL_COUNT) -> list[float]:
    if int(interval_count) != EXPECTED_INTERVAL_COUNT:
        raise ValueError("bounded response family requires exactly 16 intervals")
    values = []
    for index in range(interval_count + 1):
        if index in (0, interval_count):
            values.append(0.0)
        else:
            values.append(math.sin(math.pi * index / interval_count))
    return values


def _require_same_topology(neutral: dict, other: dict) -> None:
    if len(neutral.get("vertices", [])) != len(other.get("vertices", [])):
        raise ValueError("response state vertex-count drift")
    if neutral.get("triangles") != other.get("triangles"):
        raise ValueError("response state triangle topology drift")
    if neutral.get("regions") != other.get("regions"):
        raise ValueError("response state region identity drift")


def reconstruct_from_neutral_peak(neutral: dict, peak: dict, weight: float) -> dict:
    _require_same_topology(neutral, peak)
    value = float(weight)
    if value < -1e-12 or value > 1.0 + 1e-12:
        raise ValueError("response weight outside bounded 0..1 family")
    out = copy.deepcopy(neutral)
    vertices = []
    for neutral_vertex, peak_vertex in zip(neutral["vertices"], peak["vertices"]):
        if len(neutral_vertex) != 3 or len(peak_vertex) != 3:
            raise ValueError("response family requires 3D vertices")
        vertices.append([
            float(neutral_vertex[axis]) + value * (float(peak_vertex[axis]) - float(neutral_vertex[axis]))
            for axis in range(3)
        ])
    out["vertices"] = vertices
    return out


def max_vertex_residual(a: dict, b: dict) -> float:
    _require_same_topology(a, b)
    maximum = 0.0
    for av, bv in zip(a["vertices"], b["vertices"]):
        maximum = max(
            maximum,
            math.sqrt(sum((float(av[axis]) - float(bv[axis])) ** 2 for axis in range(3))),
        )
    return maximum


def analyze_exact_state_family(
    *,
    case_id: str,
    source_study: str,
    source_digest: str,
    response_ceiling_m: float,
    meshes: Iterable[dict],
    tolerance_m: float = 1e-12,
) -> dict:
    states = list(meshes)
    if len(states) != EXPECTED_STATE_COUNT:
        raise ValueError("bounded response family requires exactly 17 endpoint-inclusive states")
    if not case_id or not source_study or not source_digest:
        raise ValueError("response case identity is incomplete")
    if float(response_ceiling_m) <= 0.0:
        raise ValueError("response ceiling must be positive")
    if float(tolerance_m) <= 0.0:
        raise ValueError("residual tolerance must be positive")

    neutral = states[0]
    peak = states[EXPECTED_INTERVAL_COUNT // 2]
    _require_same_topology(neutral, peak)
    if canonical_digest(states[-1]) != canonical_digest(neutral):
        raise ValueError("response family does not return exactly to neutral")

    weights = half_sine_weights()
    residuals = []
    reconstructed_digests = []
    exact_state_digests = []
    for index, (state, weight) in enumerate(zip(states, weights)):
        _require_same_topology(neutral, state)
        reconstructed = reconstruct_from_neutral_peak(neutral, peak, weight)
        residual = max_vertex_residual(reconstructed, state)
        if residual > float(tolerance_m):
            raise ValueError(f"phase {index:02d} exceeds neutral-peak parameterization tolerance: {residual}")
        residuals.append(residual)
        reconstructed_digests.append(canonical_digest(reconstructed))
        exact_state_digests.append(canonical_digest(state))

    return {
        "case_id": case_id,
        "source_study": source_study,
        "source_digest": source_digest,
        "response_ceiling_m": float(response_ceiling_m),
        "state_count": len(states),
        "interval_count": EXPECTED_INTERVAL_COUNT,
        "vertex_count": len(neutral["vertices"]),
        "triangle_count": len(neutral["triangles"]),
        "neutral_mesh_digest": canonical_digest(neutral),
        "peak_mesh_digest": canonical_digest(peak),
        "exact_state_digests": exact_state_digests,
        "reconstructed_state_digests": reconstructed_digests,
        "phase_weights": weights,
        "max_reconstruction_residual_m": max(residuals, default=0.0),
        "all_states_within_tolerance": True,
        "parameterization_digest": canonical_digest({
            "source_study": source_study,
            "source_digest": source_digest,
            "response_ceiling_m": float(response_ceiling_m),
            "neutral_mesh_digest": canonical_digest(neutral),
            "peak_mesh_digest": canonical_digest(peak),
            "phase_weights": weights,
        }),
    }


def assemble_family(cases: Iterable[dict]) -> dict:
    ordered = sorted((copy.deepcopy(case) for case in cases), key=lambda row: row["case_id"])
    if len(ordered) < 2:
        raise ValueError("response parameterization family requires at least two materially different cases")
    case_ids = [row["case_id"] for row in ordered]
    source_ids = [row["source_study"] for row in ordered]
    source_digests = [row["source_digest"] for row in ordered]
    neutral_digests = [row["neutral_mesh_digest"] for row in ordered]
    peak_digests = [row["peak_mesh_digest"] for row in ordered]
    ceilings = [row["response_ceiling_m"] for row in ordered]
    if len(set(case_ids)) != len(case_ids):
        raise ValueError("duplicate response case identity")
    if len(set(source_ids)) != len(source_ids) or len(set(source_digests)) != len(source_digests):
        raise ValueError("duplicate source identity in response family")
    if len(set(neutral_digests)) != len(neutral_digests):
        raise ValueError("response family neutral meshes are not materially distinct")
    if len(set(peak_digests)) != len(peak_digests):
        raise ValueError("response family peak meshes are not materially distinct")
    if len(set(ceilings)) < 2:
        raise ValueError("response family needs materially different bounded response envelopes")
    payload = {
        "cases": ordered,
        "case_count": len(ordered),
        "distinct_source_count": len(set(source_digests)),
        "distinct_neutral_count": len(set(neutral_digests)),
        "distinct_peak_count": len(set(peak_digests)),
        "distinct_response_ceiling_count": len(set(ceilings)),
    }
    payload["family_digest"] = canonical_digest(payload)
    return payload

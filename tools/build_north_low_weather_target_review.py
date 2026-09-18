#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

RESULT = "PASS_NORTH_LOW_WEATHER_POLARITY_CURRENT_GODOT_TARGET_REVIEW"
SOURCE_RESULT = "PASS_NORTH_LOW_DETACHED_TEMPORAL_WEATHER_RESPONSE_PARENT_STRESS_DISCRIMINATION"
WEATHER = [1.0, 0.35]
WEATHER_SERIALIZATION_TOL = 1e-6


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--target-receipt", type=Path, required=True)
    p.add_argument("--source-vfx-evidence", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--svg", type=Path, required=True)
    p.add_argument("--weather-y", type=float, default=0.35)
    p.add_argument("--claim-physical-wind", action="store_true")
    p.add_argument("--claim-runtime-performance", action="store_true")
    p.add_argument("--claim-gameplay-or-physics", action="store_true")
    p.add_argument("--claim-art-or-qa-acceptance", action="store_true")
    return p.parse_args()


def sign(value: float, eps: float = 5e-7) -> int:
    if value > eps:
        return 1
    if value < -eps:
        return -1
    return 0


def build_svg(target_rows: list[dict], source_rows: list[dict]) -> str:
    width, height = 1000, 520
    left, right, top, bottom = 80, 30, 62, 78
    plot_w = width - left - right
    plot_h = height - top - bottom
    source_by_index = {int(r["index"]): r for r in source_rows}
    target_vals = [float(r["weather_parallel_m"]) for r in target_rows]
    source_vals = [float(source_by_index[int(r["index"])]["accepted_weather_parallel_m"]) for r in target_rows]
    y_abs = max(max(abs(v) for v in target_vals), max(abs(v) for v in source_vals), 1e-6)

    def xy(i: int, value: float) -> tuple[float, float]:
        x = left + (i / max(1, len(target_rows) - 1)) * plot_w
        y = top + (1.0 - ((value + y_abs) / (2.0 * y_abs))) * plot_h
        return x, y

    target_pts = " ".join(f"{xy(i,v)[0]:.2f},{xy(i,v)[1]:.2f}" for i, v in enumerate(target_vals))
    source_pts = " ".join(f"{xy(i,v)[0]:.2f},{xy(i,v)[1]:.2f}" for i, v in enumerate(source_vals))
    zero_y = xy(0, 0.0)[1]
    peak_mm = y_abs * 1000.0
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="#101419"/>
<text x="{left}" y="30" fill="#f2f5f7" font-family="monospace" font-size="18">North-low Weather-direction response: source centroid vs real Godot target witness</text>
<text x="{left}" y="49" fill="#9aa7b2" font-family="monospace" font-size="12">Different observables; sign/phase continuity is comparable, numeric magnitude identity is not claimed.</text>
<line x1="{left}" y1="{zero_y:.2f}" x2="{width-right}" y2="{zero_y:.2f}" stroke="#66717a" stroke-width="1"/>
<polyline points="{source_pts}" fill="none" stroke="#74b9ff" stroke-width="3"/>
<polyline points="{target_pts}" fill="none" stroke="#f8c471" stroke-width="3"/>
<text x="{left}" y="{height-45}" fill="#74b9ff" font-family="monospace" font-size="13">source-space 52-vertex centroid (VFX PR #27)</text>
<text x="{left+430}" y="{height-45}" fill="#f8c471" font-family="monospace" font-size="13">real-Godot imported witness (this review)</text>
<text x="{left}" y="{height-24}" fill="#9aa7b2" font-family="monospace" font-size="12">41 samples / 1.0 s owner loop; Weather visual direction [1.0, 0.35]; vertical range +/-{peak_mm:.2f} mm</text>
</svg>\n'''


def main() -> int:
    args = parse_args()
    if abs(args.weather_y - 0.35) > 1e-12:
        raise ValueError("Weather donor direction drift: expected [1.0, 0.35]")
    if args.claim_physical_wind:
        raise ValueError("VFX target review cannot promote visual direction into physical wind")
    if args.claim_runtime_performance:
        raise ValueError("VFX target review cannot claim Runtime/device performance")
    if args.claim_gameplay_or_physics:
        raise ValueError("VFX target review cannot claim gameplay/collision/physics semantics")
    if args.claim_art_or_qa_acceptance:
        raise ValueError("VFX target review cannot claim Art Direction or independent Visual QA acceptance")

    target = load(args.target_receipt)
    source = load(args.source_vfx_evidence)
    if target.get("state") != RESULT:
        raise ValueError("real Godot target receipt is not green")
    if source.get("result") != SOURCE_RESULT:
        raise ValueError("exact source-space VFX predecessor is not green")
    target_weather = [float(v) for v in target.get("weather_source_xy", [])]
    if len(target_weather) != 2 or any(abs(a - b) > WEATHER_SERIALIZATION_TOL for a, b in zip(target_weather, WEATHER)):
        raise ValueError("target receipt Weather vector drift")

    target_rows = target.get("rows") or []
    source_rows = (source.get("measurements") or {}).get("rows") or []
    if len(target_rows) != 41 or len(source_rows) != 41:
        raise ValueError("expected exact 41-sample owner loop in both evidence sets")
    source_by_index = {int(r["index"]): r for r in source_rows}

    agreement = 0
    mismatches: list[int] = []
    for row in target_rows:
        idx = int(row["index"])
        src = source_by_index[idx]
        child = float(row["north_low_child_angle_deg"])
        if abs(child - float(src["child_angle_deg"])) > 1e-12:
            raise ValueError(f"owner angle drift at sample {idx}")
        target_sign = sign(float(row["weather_parallel_m"]))
        source_sign = sign(float(src["accepted_weather_parallel_m"]))
        if target_sign == source_sign:
            agreement += 1
        else:
            mismatches.append(idx)

    report = {
        "schema": "axm.nature-north-low-weather-vfx-target-review/v0.1",
        "result": RESULT,
        "weather_source_xy": WEATHER,
        "comparison_semantics": "sign_and_phase_continuity_only__source_centroid_vs_target_witness_magnitudes_are_not_identity_comparable",
        "measurements": {
            "sample_count": 41,
            "target_weather_polarity_sign_violations": int(target.get("weather_polarity_sign_violations", -1)),
            "source_weather_polarity_sign_violations": int((source.get("measurements") or {}).get("weather_polarity_sign_violations", -1)),
            "source_target_sign_agreement_samples": agreement,
            "source_target_sign_mismatch_indices": mismatches,
            "target_witness_peak_downwind_parallel_m": float(target["target_witness_peak_downwind_parallel_m"]),
            "target_witness_peak_upwind_parallel_m": float(target["target_witness_peak_upwind_parallel_m"]),
            "source_centroid_peak_downwind_parallel_m": float(source["measurements"]["minus5_peak_downwind_parallel_m"]),
            "source_centroid_peak_upwind_parallel_m": float(source["measurements"]["plus5_peak_upwind_parallel_m"]),
            "maximum_target_sample_position_residual_m": float(target["maximum_target_sample_position_residual_m"]),
            "maximum_weather_parallel_target_vs_analytic_residual_m": float(target["maximum_weather_parallel_target_vs_analytic_residual_m"]),
            "endpoint_closure_m": float(target["endpoint_closure_m"]),
        },
        "truth_boundary": {
            "real_godot_target_host_visual_direction_observation": True,
            "source_centroid_and_target_witness_numeric_identity_claimed": False,
            "physical_wind_speed_force_drag_or_turbulence_claimed": False,
            "botanical_or_natural_motion_quality_claimed": False,
            "runtime_controller_or_target_device_performance_claimed": False,
            "collision_gameplay_damage_or_physics_claimed": False,
            "art_direction_or_independent_visual_qa_acceptance_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }
    m = report["measurements"]
    if m["target_weather_polarity_sign_violations"] != 0 or m["source_weather_polarity_sign_violations"] != 0:
        raise ValueError("Weather polarity violation present")
    if agreement != 41 or mismatches:
        raise ValueError(f"source/target sign continuity mismatch: {mismatches}")
    if m["maximum_target_sample_position_residual_m"] > 5e-6:
        raise ValueError("target transport residual exceeds Technical Art gate")
    if m["maximum_weather_parallel_target_vs_analytic_residual_m"] > 5e-6:
        raise ValueError("target Weather-parallel residual exceeds Technical Art gate")
    if abs(m["endpoint_closure_m"]) > 5e-6:
        raise ValueError("target endpoint failed to close")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.svg.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.svg.write_text(build_svg(target_rows, source_rows), encoding="utf-8")
    print(RESULT)
    print(json.dumps(m, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Animation evidence for the exact east-rear north-top Rigging socket.

This module adds one time-domain diagnostic pulse over the exact Rigging-owned
-5..+5 degree verification interval.  The interval remains a Rigging probe, not a
source or biological range of motion.  The pulse is not wind, controller logic,
gameplay, or final motion direction.
"""
from __future__ import annotations

import math
from typing import Iterable

from .organic_form import build_mesh, digest, validate_source
from .rear_tree_rigging import evaluate as evaluate_rigging

SCHEMA = "axm.nature-animation-root-socket-diagnostic-pulse/v0.1"
RESULT = "PASS_NORTH_TOP_ROOT_SOCKET_DIAGNOSTIC_PULSE_SAMPLED_MOTION"
RIGGING_HEAD = "87ce8b2ff10937abec4432e1c6d5a7114a076cdb"
RIGGING_RESULT = "PASS_NORTH_TOP_ROOT_SOCKET_RIGID_CHILD_ARTICULATION_DIAGNOSTIC_MINUS5_TO_PLUS5"
TRUTH_LABEL = "ANIMATION_DIAGNOSTIC_SOCKET_PULSE_NOT_WIND_NOT_BIOLOGICAL_ROM_NOT_CONTROLLER"
DURATION_S = 1.0
SAMPLE_RATE_HZ = 40
SAMPLE_COUNT = 41
AMPLITUDE_DEG = 5.0
TOL = 1e-12


def _sub(a, b):
    return [float(a[i]) - float(b[i]) for i in range(3)]


def _add(a, b):
    return [float(a[i]) + float(b[i]) for i in range(3)]


def _mul(a, s):
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


def _distance(a, b):
    return _length(_sub(a, b))


def _rotate_about_axis(point, pivot, axis, angle_deg):
    """Proof-local replay of the exact Rigging Rodrigues transform contract."""
    v = _sub(point, pivot)
    theta = math.radians(float(angle_deg))
    c = math.cos(theta)
    s = math.sin(theta)
    return _add(
        pivot,
        _add(
            _add(_mul(v, c), _mul(_cross(axis, v), s)),
            _mul(axis, _dot(axis, v) * (1.0 - c)),
        ),
    )


def _selected_indices(mesh: dict, region_ids: Iterable[str]):
    wanted = set(region_ids)
    found = set()
    indices = set()
    for region in mesh["regions"]:
        if region["id"] not in wanted:
            continue
        found.add(region["id"])
        start = int(region["triangle_start"])
        count = int(region["triangle_count"])
        for triangle in mesh["triangles"][start : start + count]:
            indices.update(int(i) for i in triangle)
    if found != wanted:
        raise ValueError(f"Rigging child-region identity drift: missing {sorted(wanted - found)}")
    return sorted(indices)


def _pairwise_distances(vertices):
    values = []
    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            values.append(_distance(vertices[i], vertices[j]))
    return values


def _max_abs_delta(a, b):
    if len(a) != len(b):
        raise ValueError("mismatched evidence vector lengths")
    return max((abs(float(x) - float(y)) for x, y in zip(a, b)), default=0.0)


def _angle_for_index(index: int) -> float:
    if index < 0 or index >= SAMPLE_COUNT:
        raise ValueError("sample index outside endpoint-inclusive clip")
    # Force exact semantic landmarks instead of retaining tiny trig residue.
    if index in (0, 20, 40):
        return 0.0
    if index == 10:
        return AMPLITUDE_DEG
    if index == 30:
        return -AMPLITUDE_DEG
    phase = float(index) / float(SAMPLE_RATE_HZ)
    return AMPLITUDE_DEG * (math.sin(2.0 * math.pi * phase) ** 3)


def _pose(neutral_vertices, selected_indices, pivot, axis, angle_deg):
    posed = [[float(x) for x in vertex] for vertex in neutral_vertices]
    for index in selected_indices:
        posed[index] = _rotate_about_axis(neutral_vertices[index], pivot, axis, angle_deg)
    return posed


def _pose_metrics(neutral_vertices, posed, selected_indices, fixed_indices, pivot_indices, pivot, axis):
    neutral_selected = [neutral_vertices[i] for i in selected_indices]
    posed_selected = [posed[i] for i in selected_indices]
    pairwise = _max_abs_delta(_pairwise_distances(posed_selected), _pairwise_distances(neutral_selected))
    fixed = max((_distance(posed[i], neutral_vertices[i]) for i in fixed_indices), default=0.0)
    pivot_drift = max((_distance(posed[i], neutral_vertices[i]) for i in pivot_indices), default=0.0)
    axis_projection = max(
        (
            abs(_dot(_sub(posed[i], pivot), axis) - _dot(_sub(neutral_vertices[i], pivot), axis))
            for i in selected_indices
        ),
        default=0.0,
    )
    displacement = max((_distance(posed[i], neutral_vertices[i]) for i in selected_indices), default=0.0)
    return {
        "fixed_vertex_drift_m": fixed,
        "pivot_vertex_drift_m": pivot_drift,
        "selected_pairwise_distance_drift_m": pairwise,
        "selected_axis_projection_drift_m": axis_projection,
        "maximum_selected_vertex_displacement_m": displacement,
    }


def evaluate(
    source: dict,
    *,
    duration_s: float = DURATION_S,
    sample_rate_hz: int = SAMPLE_RATE_HZ,
    amplitude_deg: float = AMPLITUDE_DEG,
    claim_wind_motion: bool = False,
    claim_biological_rom: bool = False,
    claim_runtime_controller: bool = False,
    claim_gameplay_acceptance: bool = False,
) -> dict:
    """Build one bounded sampled Animation diagnostic over the exact Rigging socket."""
    validate_source(source)
    if abs(float(duration_s) - DURATION_S) > TOL:
        raise ValueError("diagnostic Animation duration drift")
    if int(sample_rate_hz) != SAMPLE_RATE_HZ:
        raise ValueError("diagnostic Animation sample-rate drift")
    if abs(float(amplitude_deg) - AMPLITUDE_DEG) > TOL:
        raise ValueError("Animation may not widen or relabel the Rigging diagnostic interval")
    if claim_wind_motion:
        raise ValueError("diagnostic socket pulse is not a wind-motion claim")
    if claim_biological_rom:
        raise ValueError("Rigging diagnostic interval is not biological/source ROM")
    if claim_runtime_controller:
        raise ValueError("Animation evidence cannot claim Runtime controller acceptance")
    if claim_gameplay_acceptance:
        raise ValueError("Animation evidence cannot claim gameplay acceptance")

    rig = evaluate_rigging(source)
    if rig["result"] != RIGGING_RESULT:
        raise ValueError("exact Rigging prerequisite is not green")
    rig_probe = rig["rigging_probe"]
    if rig_probe["diagnostic_interval_semantics"] != "RIGGING_VERIFICATION_PROBE_ONLY_NOT_SOURCE_OR_BIOLOGICAL_ROM":
        raise ValueError("Rigging truth boundary drift")
    if [float(x) for x in rig_probe["diagnostic_interval_deg"]] != [-5.0, 5.0]:
        raise ValueError("Rigging diagnostic interval drift")

    mesh = build_mesh(source)
    neutral_vertices = [[float(x) for x in vertex] for vertex in mesh["vertices"]]
    selected_indices = _selected_indices(mesh, rig_probe["selected_regions"])
    if len(selected_indices) != 52:
        raise ValueError("exact Rigging child vertex partition drift")
    selected_set = set(selected_indices)
    fixed_indices = [i for i in range(len(neutral_vertices)) if i not in selected_set]
    if len(fixed_indices) != 338:
        raise ValueError("exact Rigging fixed vertex partition drift")

    pivot = [float(x) for x in rig_probe["joint_pivot_m"]]
    axis = [float(x) for x in rig_probe["source_derived_axis"]]
    pivot_indices = [int(i) for i in rig_probe["generated_pivot_vertex_indices"]]
    if len(pivot_indices) != 1:
        raise ValueError("expected one exact Rigging pivot vertex")

    samples = []
    posed_frames = []
    maximum_fixed_drift = 0.0
    maximum_pivot_drift = 0.0
    maximum_pairwise_drift = 0.0
    maximum_axis_projection_drift = 0.0
    maximum_selected_displacement = 0.0
    maximum_adjacent_selected_step = 0.0

    for index in range(SAMPLE_COUNT):
        angle = _angle_for_index(index)
        if angle < -AMPLITUDE_DEG - TOL or angle > AMPLITUDE_DEG + TOL:
            raise ValueError("sample escaped exact Rigging diagnostic interval")
        posed = _pose(neutral_vertices, selected_indices, pivot, axis, angle)
        metrics = _pose_metrics(
            neutral_vertices, posed, selected_indices, fixed_indices, pivot_indices, pivot, axis
        )
        if posed_frames:
            step = max(
                (_distance(posed[i], posed_frames[-1][i]) for i in selected_indices),
                default=0.0,
            )
        else:
            step = 0.0
        maximum_adjacent_selected_step = max(maximum_adjacent_selected_step, step)
        maximum_fixed_drift = max(maximum_fixed_drift, metrics["fixed_vertex_drift_m"])
        maximum_pivot_drift = max(maximum_pivot_drift, metrics["pivot_vertex_drift_m"])
        maximum_pairwise_drift = max(maximum_pairwise_drift, metrics["selected_pairwise_distance_drift_m"])
        maximum_axis_projection_drift = max(
            maximum_axis_projection_drift, metrics["selected_axis_projection_drift_m"]
        )
        maximum_selected_displacement = max(
            maximum_selected_displacement, metrics["maximum_selected_vertex_displacement_m"]
        )
        samples.append(
            {
                "index": index,
                "time_s": index / float(SAMPLE_RATE_HZ),
                "angle_deg": angle,
                "maximum_selected_step_from_previous_m": step,
                "pose_digest": digest({"vertices": posed, "triangles": mesh["triangles"]}),
                **metrics,
            }
        )
        posed_frames.append(posed)

    # The endpoint is deliberately retained as a duplicate-neutral seam witness but
    # omitted from the repeating visible sample set, matching the established AXM
    # sampled-animation evidence discipline.
    endpoint_closure = max(
        (_distance(posed_frames[0][i], posed_frames[-1][i]) for i in range(len(neutral_vertices))),
        default=0.0,
    )
    visible_wrap = max(
        (_distance(posed_frames[39][i], posed_frames[0][i]) for i in selected_indices),
        default=0.0,
    )
    authored_final_step = max(
        (_distance(posed_frames[39][i], posed_frames[40][i]) for i in selected_indices),
        default=0.0,
    )
    wrap_residual = abs(visible_wrap - authored_final_step)

    angular_symmetry_error = max(
        (abs(samples[i]["angle_deg"] + samples[40 - i]["angle_deg"]) for i in range(41)),
        default=0.0,
    )

    # Replay the exact five Rigging witness angles through the Animation-local
    # transform and require metric agreement. This prevents a second incompatible
    # motion transform from drifting behind the same names.
    rig_pose_by_angle = {float(row["angle_deg"]): row for row in rig["poses"]}
    representative_replay = []
    maximum_rig_metric_residual = 0.0
    metric_names = (
        "fixed_vertex_drift_m",
        "pivot_vertex_drift_m",
        "selected_pairwise_distance_drift_m",
        "selected_axis_projection_drift_m",
        "maximum_selected_vertex_displacement_m",
    )
    for angle in (-5.0, -2.5, 0.0, 2.5, 5.0):
        posed = _pose(neutral_vertices, selected_indices, pivot, axis, angle)
        metrics = _pose_metrics(
            neutral_vertices, posed, selected_indices, fixed_indices, pivot_indices, pivot, axis
        )
        owner = rig_pose_by_angle[angle]
        residuals = {name: abs(float(metrics[name]) - float(owner[name])) for name in metric_names}
        maximum_rig_metric_residual = max(maximum_rig_metric_residual, *residuals.values())
        representative_replay.append({"angle_deg": angle, "metric_residuals": residuals})

    checks = {
        "exact_rigging_prerequisite": rig["result"] == RIGGING_RESULT,
        "exact_sample_count": len(samples) == SAMPLE_COUNT,
        "exact_landmarks": samples[0]["angle_deg"] == 0.0
        and samples[10]["angle_deg"] == 5.0
        and samples[20]["angle_deg"] == 0.0
        and samples[30]["angle_deg"] == -5.0
        and samples[40]["angle_deg"] == 0.0,
        "all_samples_inside_rigging_probe": all(-5.0 - TOL <= row["angle_deg"] <= 5.0 + TOL for row in samples),
        "fixed_receiver_exact": maximum_fixed_drift <= TOL,
        "pivot_exact": maximum_pivot_drift <= TOL,
        "rigid_child_preserved": maximum_pairwise_drift <= TOL,
        "axis_projection_preserved": maximum_axis_projection_drift <= TOL,
        "endpoint_neutral_closure": endpoint_closure <= TOL,
        "repeat_wrap_matches_authored_final_step": wrap_residual <= TOL,
        "bidirectional_curve_is_antisymmetric": angular_symmetry_error <= TOL,
        "animation_replay_matches_rigging_witness_metrics": maximum_rig_metric_residual <= TOL,
        "wind_not_claimed": not claim_wind_motion,
        "biological_rom_not_claimed": not claim_biological_rom,
        "runtime_controller_not_claimed": not claim_runtime_controller,
        "gameplay_not_claimed": not claim_gameplay_acceptance,
    }

    return {
        "schema": SCHEMA,
        "result": RESULT if all(checks.values()) else "FAIL",
        "motion": {
            "clip_id": "north-top-root-socket-diagnostic-pulse-001",
            "truth_label": TRUTH_LABEL,
            "duration_s": DURATION_S,
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "endpoint_inclusive_samples": SAMPLE_COUNT,
            "visible_repeating_samples": 40,
            "curve": "angle_deg = 5 * sin(2*pi*t)^3; exact landmarks clamped at 0/0.25/0.5/0.75/1.0 s",
            "landmarks": [
                {"time_s": 0.0, "angle_deg": 0.0},
                {"time_s": 0.25, "angle_deg": 5.0},
                {"time_s": 0.5, "angle_deg": 0.0},
                {"time_s": 0.75, "angle_deg": -5.0},
                {"time_s": 1.0, "angle_deg": 0.0},
            ],
            "amplitude_semantics": "EXACT_RIGGING_DIAGNOSTIC_BOUND_ONLY_NOT_SOURCE_OR_BIOLOGICAL_ROM",
        },
        "rigging_owner": {
            "repository": "mike-axiom-mir/axm-nature-design",
            "pr": 14,
            "head": RIGGING_HEAD,
            "result": rig["result"],
            "joint_pivot_m": pivot,
            "source_derived_axis": axis,
            "selected_regions": rig_probe["selected_regions"],
            "selected_vertices": len(selected_indices),
            "fixed_vertices": len(fixed_indices),
            "diagnostic_interval_deg": rig_probe["diagnostic_interval_deg"],
            "diagnostic_interval_semantics": rig_probe["diagnostic_interval_semantics"],
        },
        "measurements": {
            "maximum_fixed_vertex_drift_m": maximum_fixed_drift,
            "maximum_pivot_vertex_drift_m": maximum_pivot_drift,
            "maximum_selected_pairwise_distance_drift_m": maximum_pairwise_drift,
            "maximum_selected_axis_projection_drift_m": maximum_axis_projection_drift,
            "maximum_selected_vertex_displacement_m": maximum_selected_displacement,
            "maximum_adjacent_selected_vertex_step_m": maximum_adjacent_selected_step,
            "maximum_adjacent_angular_step_deg": max(
                abs(samples[i + 1]["angle_deg"] - samples[i]["angle_deg"]) for i in range(40)
            ),
            "endpoint_closure_m": endpoint_closure,
            "visible_wrap_step_m": visible_wrap,
            "authored_final_adjacent_step_m": authored_final_step,
            "wrap_step_residual_m": wrap_residual,
            "angular_antisymmetry_error_deg": angular_symmetry_error,
            "maximum_rigging_witness_metric_residual": maximum_rig_metric_residual,
        },
        "samples": samples,
        "rigging_witness_replay": representative_replay,
        "checks": checks,
        "truth_boundary": {
            "source_or_biological_rom_claimed": False,
            "wind_or_vfx_motion_claimed": False,
            "physical_or_biomechanical_motion_claimed": False,
            "target_engine_playback_claimed": False,
            "wall_clock_or_display_delivery_claimed": False,
            "runtime_controller_or_state_machine_claimed": False,
            "gameplay_or_input_acceptance_claimed": False,
            "collision_or_clearance_claimed": False,
            "art_direction_or_visual_qa_acceptance_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }


def build_review_svg(source: dict) -> str:
    """Return a deterministic five-pose Y/Z projection of the actual generated child vertices."""
    rig = evaluate_rigging(source)
    mesh = build_mesh(source)
    neutral = [[float(x) for x in vertex] for vertex in mesh["vertices"]]
    selected = _selected_indices(mesh, rig["rigging_probe"]["selected_regions"])
    pivot = [float(x) for x in rig["rigging_probe"]["joint_pivot_m"]]
    axis = [float(x) for x in rig["rigging_probe"]["source_derived_axis"]]
    pose_indices = [0, 10, 20, 30, 40]
    posed = [_pose(neutral, selected, pivot, axis, _angle_for_index(i)) for i in pose_indices]
    ys = [frame[i][1] for frame in posed for i in selected]
    zs = [frame[i][2] for frame in posed for i in selected]
    ymin, ymax = min(ys), max(ys)
    zmin, zmax = min(zs), max(zs)
    yspan = max(ymax - ymin, 1e-9)
    zspan = max(zmax - zmin, 1e-9)
    panel_w, panel_h, margin = 220, 260, 24
    width = panel_w * len(posed)
    height = panel_h + 48
    chunks = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:monospace;font-size:13px}.p{fill:#111}.pivot{fill:none;stroke:#111;stroke-width:1.5}</style>',
    ]
    for panel, (sample_index, frame) in enumerate(zip(pose_indices, posed)):
        x0 = panel * panel_w
        chunks.append(f'<rect x="{x0 + 1}" y="1" width="{panel_w - 2}" height="{panel_h - 2}" fill="none" stroke="#bbb"/>')
        for i in selected:
            y, z = frame[i][1], frame[i][2]
            px = x0 + margin + ((y - ymin) / yspan) * (panel_w - 2 * margin)
            py = margin + (1.0 - (z - zmin) / zspan) * (panel_h - 2 * margin)
            chunks.append(f'<circle class="p" cx="{px:.3f}" cy="{py:.3f}" r="1.2"/>')
        ppx = x0 + margin + ((pivot[1] - ymin) / yspan) * (panel_w - 2 * margin)
        ppy = margin + (1.0 - (pivot[2] - zmin) / zspan) * (panel_h - 2 * margin)
        chunks.append(f'<circle class="pivot" cx="{ppx:.3f}" cy="{ppy:.3f}" r="4"/>')
        angle = _angle_for_index(sample_index)
        chunks.append(f'<text x="{x0 + 10}" y="{panel_h + 22}">t={sample_index / SAMPLE_RATE_HZ:.2f}s  {angle:+.1f} deg</text>')
    chunks.append('<text x="10" y="302">Y/Z projection — generated north-top child vertices; review evidence only</text>')
    chunks.append('</svg>')
    return "\n".join(chunks)

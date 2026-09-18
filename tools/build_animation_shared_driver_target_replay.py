#!/usr/bin/env python3
"""Build an Animation-owned oracle for replaying the exact current shared-driver loop
through the already-proven Nature Technical-Art dynamic-window receiver.

This tool deliberately does not grant Technical Art adoption of the current
Animation/Rigging owner pair. It proves only that the exact current Animation
samples address the same 260-vertex receiver window and emits target-coordinate
packets for a proof-local Godot AnimationPlayer observer. The older Technical-Art
pose oracle is retained as a predecessor comparison, not treated as semantic
pose authority for the newer Rigging/Animation pair.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from axm_nature_design.organic_form import build_mesh, digest, load_source
from axm_nature_design import rear_tree_animation_shared_driver as animation
from axm_nature_design import rear_tree_rigging_primary_branch_family as rig_family
from axm_nature_design import rear_tree_rigging_shared_driver_composition as rig_composition

SCHEMA = "axm.nature-animation-five-socket-ta-window-replay/v0.1"
RESULT = "PASS_CURRENT_ANIMATION_SHARED_DRIVER_PACKETS_MATCH_TA_DYNAMIC_WINDOW"
ANIMATION_PREDECESSOR_HEAD = "bfb66da82bc358b14e52711bbdef7b58e4c943af"
RIGGING_OWNER_HEAD = "b4b480b415047fea90b4740f7702ced0dba9142d"
TECHNICAL_ART_DONOR_HEAD = "da60cd491ac7f9ac04f918dd000f464a627b3316"
TECHNICAL_ART_RESULT = "PASS_NATURE_EAST_REAR_RUNTIME_WINDOW_CURRENT_UC_TARGET_RECEIVER_READY"
TECHNICAL_ART_ORACLE_SCHEMA = "axm.nature-east-rear-dynamic-window-godot-oracle/v0.1"
RUNTIME_DONOR_HEAD = "6d89e1fc0f8dc5e2ef6c57fc99c1dc6b1727780f"
UC_DONOR_HEAD = "5c5d2cfdc3aa4e9462fd4d5ec5bc7874f12674a4"
SOURCE_DIGEST = "178cd8cfb1a859bff411f60e13154109528062cf0ad2384b343d406cc0cc9d61"
MESH_DIGEST = "aa9d450a78fef722672ea9af0f9aca98b4c1a0ca3705661784f5f61f3e9b6a31"
WINDOW_START = 110
WINDOW_END = 370
EXPECTED_VERTICES = 390
POSITION_STRIDE_BYTES = 12


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _source_to_target(point: list[float]) -> list[float]:
    # Exact established Nature -> UC / Godot boundary: [x,y,z] -> [x,z,y].
    return [float(point[0]), float(point[2]), float(point[1])]


def _max_component_delta(left: list[list[float]], right: list[list[float]]) -> float:
    if len(left) != len(right):
        return float("inf")
    return max(
        (
            abs(float(left[i][axis]) - float(right[i][axis]))
            for i in range(len(left))
            for axis in range(3)
        ),
        default=0.0,
    )


def build(
    *,
    ta_receipt_path: Path,
    ta_oracle_path: Path,
    ta_glb_path: Path,
    output_path: Path,
    mutate_window_end: int | None = None,
    claim_technical_art_current_pair_adoption: bool = False,
    claim_runtime_controller: bool = False,
    claim_gameplay_acceptance: bool = False,
) -> dict[str, Any]:
    if claim_technical_art_current_pair_adoption:
        raise ValueError("Animation compatibility replay cannot grant Technical Art current-pair adoption")
    if claim_runtime_controller:
        raise ValueError("Animation target replay cannot claim Runtime controller/state-machine acceptance")
    if claim_gameplay_acceptance:
        raise ValueError("Animation target replay cannot claim gameplay acceptance")

    ta_receipt = _read_json(ta_receipt_path)
    ta_oracle = _read_json(ta_oracle_path)
    if ta_receipt.get("result") != TECHNICAL_ART_RESULT:
        raise ValueError("exact Technical Art receiver prerequisite is not green")
    if ta_oracle.get("schema") != TECHNICAL_ART_ORACLE_SCHEMA:
        raise ValueError("Technical Art target oracle schema drift")
    if ta_receipt.get("source_digest") != SOURCE_DIGEST or ta_receipt.get("mesh_digest") != MESH_DIGEST:
        raise ValueError("Technical Art source/mesh identity drift")
    expected_heads = {
        "runtime": RUNTIME_DONOR_HEAD,
        "vfx": "ba1c12dd527f1ecc6a0eb4bc0b4322f15ccad475",
        "rigging": "754797a815266a643c6b08f1606eb76ba95dd8c6",
        "uc": UC_DONOR_HEAD,
    }
    if ta_receipt.get("heads") != expected_heads:
        raise ValueError("Technical Art dynamic-window donor lineage drift")
    receiver = ta_receipt.get("receiver") or {}
    window = list(receiver.get("dynamic_window_target_vertex_indices") or [])
    if mutate_window_end is not None and len(window) == 2:
        window[1] = int(mutate_window_end)
    if window != [WINDOW_START, WINDOW_END]:
        raise ValueError("Technical Art dynamic-window identity drift")
    if int(receiver.get("target_vertex_stride_bytes", -1)) != POSITION_STRIDE_BYTES:
        raise ValueError("Technical Art mutable position stride drift")
    if int(receiver.get("target_dynamic_byte_offset", -1)) != WINDOW_START * POSITION_STRIDE_BYTES:
        raise ValueError("Technical Art target dynamic offset drift")
    if int(receiver.get("target_dynamic_byte_length", -1)) != (WINDOW_END - WINDOW_START) * POSITION_STRIDE_BYTES:
        raise ValueError("Technical Art target dynamic length drift")
    if _sha256_file(ta_glb_path) != str(ta_oracle.get("receiver_glb_sha256", "")):
        raise ValueError("Technical Art exact receiver GLB identity drift")

    source = load_source(Path("examples/east_rear_tree_neutral_001.json"))
    mesh = build_mesh(source)
    if digest(source) != SOURCE_DIGEST or digest(mesh) != MESH_DIGEST:
        raise ValueError("current Animation source/mesh identity drift")
    if len(mesh.get("vertices", [])) != EXPECTED_VERTICES:
        raise ValueError("current Animation receiver vertex count drift")

    animation_receipt = animation.evaluate(source)
    if animation_receipt.get("result") != animation.RESULT:
        raise ValueError("exact current Animation prerequisite is not green")
    if animation.RIGGING_OWNER_HEAD != RIGGING_OWNER_HEAD:
        raise ValueError("current Animation Rigging owner identity drift")

    neutral = [[float(value) for value in vertex] for vertex in mesh["vertices"]]
    probes = [rig_family._probe_branch(source, mesh, branch_id) for branch_id in rig_composition.BRANCH_IDS]
    probes_by_branch = {probe["branch_id"]: probe for probe in probes}
    selected_union = sorted(
        set().union(
            *(set(int(i) for i in probe["selected_vertex_indices"]) for probe in probes)
        )
    )
    expected_window_indices = list(range(WINDOW_START, WINDOW_END))
    if selected_union != expected_window_indices:
        raise ValueError("current five-socket selected union is not the exact TA/Runtime dynamic window")

    samples: list[dict[str, Any]] = []
    max_dynamic_motion = 0.0
    neutral_dynamic_target = [_source_to_target(point) for point in neutral[WINDOW_START:WINDOW_END]]
    for source_sample in animation_receipt.get("samples", []):
        index = int(source_sample["index"])
        shared_driver_deg = float(source_sample["shared_driver_deg"])
        posed = rig_composition._compose(
            neutral,
            probes_by_branch,
            shared_driver_deg,
            rig_composition.BRANCH_IDS,
        )
        dynamic_target = [_source_to_target(point) for point in posed[WINDOW_START:WINDOW_END]]
        max_dynamic_motion = max(max_dynamic_motion, _max_component_delta(dynamic_target, neutral_dynamic_target))
        samples.append(
            {
                "index": index,
                "time_s": float(source_sample["time_s"]),
                "shared_driver_deg": shared_driver_deg,
                "local_angles_deg": source_sample["local_angles_deg"],
                "dynamic_target_positions_m": dynamic_target,
            }
        )

    if len(samples) != 41:
        raise ValueError("current Animation endpoint-inclusive sample count drift")
    if samples[0]["dynamic_target_positions_m"] != samples[-1]["dynamic_target_positions_m"]:
        raise ValueError("current Animation endpoint packet is not exact neutral closure")
    if max_dynamic_motion <= 0.05:
        raise ValueError("current Animation packet family is not motion-discriminating")

    # The Technical-Art donor predates the current continuous Rigging owner. Its
    # five pose packets are retained only as an explicit semantic-divergence
    # witness. The transport boundary we reuse is source/mesh identity + exact
    # vertex-index window + float32 byte layout, not predecessor pose equality.
    ta_static_witness_by_driver = {
        float(row["shared_driver_deg"]): row for row in ta_oracle.get("poses", [])
    }
    predecessor_pose_residual = 0.0
    for witness_index in (0, 10, 20, 30, 40):
        row = samples[witness_index]
        driver = float(row["shared_driver_deg"])
        donor = ta_static_witness_by_driver.get(driver)
        if donor is None:
            raise ValueError(f"Technical Art static target oracle missing driver witness {driver}")
        predecessor_pose_residual = max(
            predecessor_pose_residual,
            _max_component_delta(
                row["dynamic_target_positions_m"],
                donor.get("candidate_dynamic_target_positions_m", []),
            ),
        )

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "result": RESULT,
        "lineage": {
            "animation_predecessor_head": ANIMATION_PREDECESSOR_HEAD,
            "rigging_owner_head": RIGGING_OWNER_HEAD,
            "technical_art_receiver_donor_head": TECHNICAL_ART_DONOR_HEAD,
            "technical_art_receiver_donor_is_current_pair_adoption": False,
            "technical_art_pose_semantics_inherited_by_current_pair": False,
            "runtime_receiver_donor_head": RUNTIME_DONOR_HEAD,
            "uc_receiver_donor_head": UC_DONOR_HEAD,
        },
        "receiver": {
            "source_digest": SOURCE_DIGEST,
            "mesh_digest": MESH_DIGEST,
            "vertex_count": EXPECTED_VERTICES,
            "dynamic_window_vertices": [WINDOW_START, WINDOW_END],
            "dynamic_vertex_count": WINDOW_END - WINDOW_START,
            "fixed_vertex_count": EXPECTED_VERTICES - (WINDOW_END - WINDOW_START),
            "position_stride_bytes": POSITION_STRIDE_BYTES,
            "dynamic_byte_offset": WINDOW_START * POSITION_STRIDE_BYTES,
            "dynamic_byte_length": (WINDOW_END - WINDOW_START) * POSITION_STRIDE_BYTES,
            "receiver_glb_sha256": _sha256_file(ta_glb_path),
            "selected_union_exactly_matches_ta_window": True,
        },
        "animation": {
            "source_schema": animation.SCHEMA,
            "source_result": animation.RESULT,
            "duration_s": animation.DURATION_S,
            "sample_rate_hz": animation.SAMPLE_RATE_HZ,
            "endpoint_inclusive_samples": animation.SAMPLE_COUNT,
            "visible_repeat_samples": animation.VISIBLE_REPEAT_SAMPLES,
            "amplitude_deg": animation.AMPLITUDE_DEG,
            "target_replay_policy": "ANIMATIONPLAYER_DISCRETE_EXACT_AUTHORED_SAMPLES_0_TO_39__ENDPOINT_40_EQUALS_SAMPLE_0",
        },
        "measurements": {
            "maximum_dynamic_target_component_motion_m": max_dynamic_motion,
            "maximum_representative_pose_residual_vs_ta_predecessor_oracle_m": predecessor_pose_residual,
        },
        "samples": samples,
        "truth_boundary": {
            "current_animation_sample_packets_proven_against_ta_window_identity": True,
            "predecessor_ta_pose_semantics_reused_as_current_authority": False,
            "technical_art_current_animation_rigging_pair_adoption_claimed": False,
            "runtime_controller_state_machine_or_input_claimed": False,
            "wall_clock_full_40hz_slot_delivery_claimed": False,
            "physical_wind_or_biological_motion_claimed": False,
            "collision_or_physics_claimed": False,
            "gameplay_acceptance_claimed": False,
            "art_or_visual_qa_acceptance_claimed": False,
            "canon_or_production_readiness_claimed": False,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(_canonical(payload) + b"\n")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ta-receipt", type=Path, required=True)
    parser.add_argument("--ta-oracle", type=Path, required=True)
    parser.add_argument("--ta-glb", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mutate-window-end", type=int)
    parser.add_argument("--claim-technical-art-current-pair-adoption", action="store_true")
    parser.add_argument("--claim-runtime-controller", action="store_true")
    parser.add_argument("--claim-gameplay-acceptance", action="store_true")
    args = parser.parse_args()
    payload = build(
        ta_receipt_path=args.ta_receipt,
        ta_oracle_path=args.ta_oracle,
        ta_glb_path=args.ta_glb,
        output_path=args.output,
        mutate_window_end=args.mutate_window_end,
        claim_technical_art_current_pair_adoption=args.claim_technical_art_current_pair_adoption,
        claim_runtime_controller=args.claim_runtime_controller,
        claim_gameplay_acceptance=args.claim_gameplay_acceptance,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

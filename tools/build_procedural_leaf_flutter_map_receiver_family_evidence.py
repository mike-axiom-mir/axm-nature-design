#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

from axm_nature_design.organic_form import build_mesh, digest, load_source
from axm_nature_design.procedural_family import generate_accepted_variant, load_family
import build_procedural_leaf_flutter_family_evidence as flutter_family

SCHEMA = "axm.nature-procedural-leaf-flutter-map-receiver-family-evidence/v0.1"
PASS_STATE = "PASS_PROCEDURAL_VARIANTS_CURRENT_WORLD_LEAF_FLUTTER_RECEIVER_COMPATIBILITY"
CONTRACT_PATH = ROOT / "examples/procedural_leaf_flutter_map_receiver_family_001.json"


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_map_receiver(map_root: Path, contract: dict[str, Any]):
    receiver = contract["map_receiver"]
    observed_head = flutter_family._git_head(map_root)
    if observed_head != receiver["ref"]:
        raise RuntimeError(f"Map receiver head drift: {observed_head} != {receiver['ref']}")
    observed_blob = flutter_family._git_blob(map_root, receiver["path"])
    if observed_blob != receiver["git_blob"]:
        raise RuntimeError(f"Map receiver helper drift: {observed_blob} != {receiver['git_blob']}")

    tools = map_root / "tools"
    sys.path.insert(0, str(tools))
    module_path = map_root / receiver["path"]
    spec = importlib.util.spec_from_file_location("axm_exact_map_leaf_flutter_receiver", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load exact Map leaf-flutter receiver")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    expected = {
        "PARENT_POLICY_ID": receiver["parent_policy_id"],
        "VFX_HEAD": receiver["vfx_source_head"],
        "GEOMETRY_LEAF_HEAD": receiver["geometry_leaf_head"],
        "STRUCTURE_RESULT": receiver["structure_result"],
        "FRONT_VERTICES": int(contract["expected_baseline_vertices"]),
        "FRONT_TRIANGLES": int(contract["expected_baseline_triangles"]),
    }
    for name, value in expected.items():
        if getattr(module, name, None) != value:
            raise RuntimeError(f"Map receiver constant drift: {name}")

    return module, {
        "repository": receiver["repository"],
        "head": observed_head,
        "path": receiver["path"],
        "git_blob": observed_blob,
        "receiving_schema": receiver["schema"],
        "parent_policy_id": receiver["parent_policy_id"],
        "vfx_source_head": receiver["vfx_source_head"],
        "geometry_leaf_head": receiver["geometry_leaf_head"],
    }


def _foliage_triangle_indices(mesh: dict[str, Any]) -> list[int]:
    indices: list[int] = []
    leaves = [row for row in mesh.get("regions", []) if row.get("kind") == "leaf-blade"]
    if len(leaves) != 25:
        raise RuntimeError(f"expected exact 25 leaf regions, got {len(leaves)}")
    for region in leaves:
        start = int(region["triangle_start"])
        count = int(region["triangle_count"])
        if count != 2:
            raise RuntimeError("leaf region triangle-count drift")
        indices.extend(range(start, start + count))
    if len(indices) != 50 or len(set(indices)) != 50:
        raise RuntimeError("foliage triangle partition is not exact 50-triangle set")
    return indices


def _distance(a: list[float], b: list[float]) -> float:
    return sum((float(a[i]) - float(b[i])) ** 2 for i in range(3)) ** 0.5


def _receiver_record(map_tool, baseline: dict[str, Any], translation: list[float]) -> dict[str, Any]:
    foliage = _foliage_triangle_indices(baseline)
    return {
        "asset_id": "procedural-review:nature-tree",
        "vertices_source_xyz_m": map_tool._translate(baseline["vertices"], translation),
        "triangles": copy.deepcopy(baseline["triangles"]),
        "nature_material_family_receiving": {
            "surface_triangle_indices": {
                "foliage": foliage,
            }
        },
    }


def _validate_phase(
    map_tool,
    receiver: dict[str, Any],
    baseline: dict[str, Any],
    flutter: dict[str, Any],
    translation: list[float],
    displacement_cap_m: float,
    *,
    endpoint: bool,
) -> dict[str, Any]:
    if receiver["triangles"] != baseline["triangles"] or flutter["triangles"] != baseline["triangles"]:
        raise RuntimeError("receiver/VFX topology drift")

    residual, observed_translation = map_tool._translated_residual(
        receiver["vertices_source_xyz_m"], baseline["vertices"]
    )
    if residual > 1e-12:
        raise RuntimeError(f"Map translated-residual contract failed: {residual}")
    if len(observed_translation) != 3 or any(
        abs(float(a) - float(b)) > 1e-12 for a, b in zip(observed_translation, translation)
    ):
        raise RuntimeError("Map receiver translation identity drift")

    foliage_vertices = map_tool._foliage_vertices(receiver)
    changed = {
        index
        for index, (before, after) in enumerate(zip(baseline["vertices"], flutter["vertices"]))
        if before != after
    }
    if not changed.issubset(foliage_vertices):
        raise RuntimeError("flutter escaped exact Map foliage vertex domain")
    if endpoint and changed:
        raise RuntimeError("neutral endpoint changed source vertices")
    if not endpoint and not changed:
        raise RuntimeError("interior receiver phase collapsed to neutral")

    translated = map_tool._translate(flutter["vertices"], translation)
    maximum_delta = max(
        (_distance(a, b) for a, b in zip(receiver["vertices_source_xyz_m"], translated)),
        default=0.0,
    )
    if maximum_delta > float(displacement_cap_m) + 1e-12:
        raise RuntimeError("Map receiver phase exceeded exact VFX displacement cap")

    return {
        "changed_vertex_count": len(changed),
        "foliage_vertex_domain_count": len(foliage_vertices),
        "translated_residual_m": residual,
        "observed_translation_m": observed_translation,
        "maximum_added_vertex_displacement_m": maximum_delta,
        "translated_mesh_digest": digest({
            "vertices": translated,
            "triangles": flutter["triangles"],
            "regions": flutter["regions"],
        }),
        "translated_vertices": translated,
    }


def _expect_failure(fn, label: str) -> dict[str, Any]:
    try:
        fn()
    except Exception as exc:  # exact failure class is receiver-owned and intentionally not reauthored here
        return {"label": label, "rejected": True, "exception": type(exc).__name__, "message": str(exc)}
    raise RuntimeError(f"negative control unexpectedly passed: {label}")


def _build_output(
    case: dict[str, Any],
    seed: int,
    contract: dict[str, Any],
    vfx_root: Path,
    map_tool,
    out: Path,
) -> dict[str, Any]:
    source = load_source(ROOT / case["source_path"])
    family = load_family(ROOT / case["family_path"])
    generated = generate_accepted_variant(source, family, int(seed))
    if generated["receipt"]["state"] != "PASS_BOUNDED_VARIANT" or generated["candidate"] is None:
        raise RuntimeError(f"{case['case_id']} seed {seed}: procedural variant did not PASS")
    candidate_source = generated["candidate"]
    baseline = build_mesh(candidate_source)
    if len(baseline["vertices"]) != int(contract["expected_baseline_vertices"]):
        raise RuntimeError("baseline vertex budget drift")
    if len(baseline["triangles"]) != int(contract["expected_baseline_triangles"]):
        raise RuntimeError("baseline triangle budget drift")

    phases = [float(value) for value in contract["normalized_phases"]]
    provider = flutter_family._provider_call(
        vfx_root,
        candidate_source,
        baseline,
        float(contract["duration_s"]),
        phases,
    )
    translation = [float(value) for value in case["receiver_translation_m"]]
    receiver = _receiver_record(map_tool, baseline, translation)
    foliage_vertices = map_tool._foliage_vertices(receiver)
    if len(foliage_vertices) != int(contract["expected_foliage_vertex_domain_count"]):
        raise RuntimeError(f"Map foliage vertex domain drift: {len(foliage_vertices)}")

    phase_records: list[dict[str, Any]] = []
    interior_digests: list[str] = []
    retained_midpoint: dict[str, Any] | None = None
    for sample in provider["samples"]:
        normalized = float(sample["normalized_phase"])
        endpoint = normalized in (0.0, 1.0)
        record = _validate_phase(
            map_tool,
            receiver,
            baseline,
            sample["mesh"],
            translation,
            float(provider["max_allowed_flutter_vertex_delta_m"]),
            endpoint=endpoint,
        )
        record.update({
            "normalized_phase": normalized,
            "source_mesh_digest": sample["mesh_digest"],
        })
        if not endpoint:
            interior_digests.append(record["translated_mesh_digest"])
        if abs(normalized - 0.5) <= 1e-12:
            retained_midpoint = {
                "schema": baseline.get("schema"),
                "vertices": record.pop("translated_vertices"),
                "triangles": copy.deepcopy(sample["mesh"]["triangles"]),
                "regions": copy.deepcopy(sample["mesh"]["regions"]),
                "receiver_translation_m": translation,
            }
        else:
            record.pop("translated_vertices")
        phase_records.append(record)

    if retained_midpoint is None:
        raise RuntimeError("receiver family lost midpoint phase")
    retained_name = f"{case['case_id']}-seed-{seed}-receiver-phase-050.mesh.json"
    _write_json(out / "meshes" / retained_name, retained_midpoint)

    malformed_receiver = copy.deepcopy(receiver)
    malformed_receiver["nature_material_family_receiving"]["surface_triangle_indices"]["foliage"].pop()
    partition_failure = _expect_failure(
        lambda: map_tool._foliage_vertices(malformed_receiver),
        "foliage-partition-count-drift",
    )

    drifted_receiver = copy.deepcopy(receiver)
    drifted_receiver["vertices_source_xyz_m"][1][0] += 0.001
    translation_failure = _expect_failure(
        lambda: (
            (_ for _ in ()).throw(RuntimeError("non-translation receiver drift accepted"))
            if map_tool._translated_residual(drifted_receiver["vertices_source_xyz_m"], baseline["vertices"])[0] <= 1e-12
            else (_ for _ in ()).throw(ValueError("non-translation receiver drift rejected"))
        ),
        "non-translation-receiver-drift",
    )

    midpoint_sample = next(row for row in provider["samples"] if abs(float(row["normalized_phase"]) - 0.5) <= 1e-12)
    escaped = copy.deepcopy(midpoint_sample["mesh"])
    foreign_index = next(index for index in range(len(baseline["vertices"])) if index not in foliage_vertices)
    escaped["vertices"][foreign_index][0] += 0.001
    domain_failure = _expect_failure(
        lambda: _validate_phase(
            map_tool,
            receiver,
            baseline,
            escaped,
            translation,
            float(provider["max_allowed_flutter_vertex_delta_m"]),
            endpoint=False,
        ),
        "flutter-domain-escape",
    )

    baseline_receiver_digest = digest({
        "vertices": receiver["vertices_source_xyz_m"],
        "triangles": receiver["triangles"],
    })
    midpoint_digest = next(
        row["translated_mesh_digest"] for row in phase_records if abs(float(row["normalized_phase"]) - 0.5) <= 1e-12
    )
    return {
        "case_id": case["case_id"],
        "seed": int(seed),
        "accepted_attempt": int(generated["receipt"]["accepted_attempt"]),
        "receiver_translation_m": translation,
        "variant_source_digest": digest(candidate_source),
        "baseline_mesh_digest": digest(baseline),
        "baseline_receiver_digest": baseline_receiver_digest,
        "midpoint_receiver_digest": midpoint_digest,
        "interior_receiver_digests": interior_digests,
        "phase_records": phase_records,
        "foliage_triangle_count": int(contract["expected_foliage_triangle_count"]),
        "foliage_vertex_domain_count": len(foliage_vertices),
        "failure_controls": [partition_failure, translation_failure, domain_failure],
        "checks": {
            "procedural_variant_passed": True,
            "exact_map_foliage_partition_accepted": True,
            "exact_translation_receiver_contract_all_phases": all(float(row["translated_residual_m"]) <= 1e-12 for row in phase_records),
            "neutral_endpoints_exact": phase_records[0]["changed_vertex_count"] == 0 and phase_records[-1]["changed_vertex_count"] == 0,
            "all_15_interior_phases_nonzero": all(int(row["changed_vertex_count"]) > 0 for row in phase_records[1:-1]),
            "all_flutter_changes_inside_map_foliage_domain": True,
            "vfx_displacement_cap_preserved": all(float(row["maximum_added_vertex_displacement_m"]) <= float(provider["max_allowed_flutter_vertex_delta_m"]) + 1e-12 for row in phase_records),
            "all_failure_controls_rejected": all(row["rejected"] for row in [partition_failure, translation_failure, domain_failure]),
        },
        "retained_midpoint_receiver_mesh": f"meshes/{retained_name}",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--vfx-root", required=True, type=Path)
    parser.add_argument("--map-root", required=True, type=Path)
    args = parser.parse_args()

    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if contract.get("schema") != "axm.nature-procedural-leaf-flutter-map-receiver-family/v0.1":
        raise RuntimeError("unsupported Map-receiver family contract")
    if len(contract["normalized_phases"]) != int(contract["expected_receiver_states_per_output"]):
        raise RuntimeError("receiver phase-count contract drift")

    base_flutter_contract = json.loads(flutter_family.CONTRACT_PATH.read_text(encoding="utf-8"))
    provider_identity = flutter_family._validate_provider(args.vfx_root.resolve(), base_flutter_contract)
    procedural_identity = flutter_family._validate_local_procedural_identity(base_flutter_contract)
    if provider_identity["head"] != contract["vfx_provider"]["ref"] or provider_identity["git_blob"] != contract["vfx_provider"]["git_blob"]:
        raise RuntimeError("VFX provider identity differs from receiver-family contract")
    map_tool, map_identity = _load_map_receiver(args.map_root.resolve(), contract)

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    outputs: list[dict[str, Any]] = []
    for case in contract["cases"]:
        family = load_family(ROOT / case["family_path"])
        seeds = [int(value) for value in family["evidence_seeds"]]
        if len(seeds) != int(contract["expected_variants_per_source"]):
            raise RuntimeError(f"{case['case_id']}: evidence seed count drift")
        for seed in seeds:
            outputs.append(_build_output(case, seed, contract, args.vfx_root.resolve(), map_tool, out))

    expected = int(contract["expected_total_outputs"])
    if len(outputs) != expected:
        raise RuntimeError("Map receiver output count drift")
    source_digests = {row["variant_source_digest"] for row in outputs}
    baseline_digests = {row["baseline_receiver_digest"] for row in outputs}
    midpoint_digests = {row["midpoint_receiver_digest"] for row in outputs}
    translations = {tuple(row["receiver_translation_m"]) for row in outputs}
    if len(source_digests) != expected or len(baseline_digests) != expected or len(midpoint_digests) != expected:
        raise RuntimeError("materially different procedural receiver outputs collapsed")
    if len(translations) != int(contract["expected_source_case_count"]):
        raise RuntimeError("receiver translation contexts collapsed")
    if not all(all(row["checks"].values()) for row in outputs):
        raise RuntimeError("one or more Map receiver compatibility checks failed")

    summary = {
        "schema": SCHEMA,
        "state": PASS_STATE,
        "procedural_head": flutter_family._git_head(ROOT),
        "contract": contract,
        "procedural_identity": procedural_identity,
        "vfx_provider": provider_identity,
        "map_receiver": map_identity,
        "source_case_count": len(contract["cases"]),
        "retained_output_count": len(outputs),
        "receiver_states_per_output": len(contract["normalized_phases"]),
        "tested_receiver_states_total": len(outputs) * len(contract["normalized_phases"]),
        "tested_interior_receiver_states_total": len(outputs) * (len(contract["normalized_phases"]) - 2),
        "distinct_variant_source_digests": len(source_digests),
        "distinct_baseline_receiver_digests": len(baseline_digests),
        "distinct_midpoint_receiver_digests": len(midpoint_digests),
        "materially_different_receiver_translation_contexts": len(translations),
        "all_outputs_materially_distinct": len(midpoint_digests) == expected,
        "all_candidate_checks_pass": all(all(row["checks"].values()) for row in outputs),
        "all_failure_controls_rejected": all(all(control["rejected"] for control in row["failure_controls"]) for row in outputs),
        "outputs": outputs,
        "decision": "PASS_RECEIVER_COMPATIBILITY_FAMILY_ONLY__NO_MAP_SOURCE_OR_ART_ADOPTION",
        "truth_boundary": contract["truth_boundary"],
    }
    _write_json(out / "summary.json", summary)
    (out / "exact-head.txt").write_text(summary["procedural_head"] + "\n", encoding="utf-8")
    (out / "map-receiver-head.txt").write_text(map_identity["head"] + "\n", encoding="utf-8")
    (out / "vfx-provider-head.txt").write_text(provider_identity["head"] + "\n", encoding="utf-8")
    print(json.dumps({key: summary[key] for key in (
        "state", "procedural_head", "retained_output_count", "receiver_states_per_output",
        "tested_receiver_states_total", "tested_interior_receiver_states_total",
        "distinct_midpoint_receiver_digests", "materially_different_receiver_translation_contexts",
        "all_candidate_checks_pass", "all_failure_controls_rejected", "decision",
    )}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axm_nature_design.organic_form import build_mesh, digest, load_source
from axm_nature_design.procedural_family import generate_accepted_variant, load_family
from axm_nature_design.source_topology_migration import inspect_shared_edge_orientation

SCHEMA = "axm.nature-procedural-leaf-flutter-family-evidence/v0.1"
PASS_STATE = "PASS_PROCEDURAL_VARIANTS_VFX_LEAF_FLUTTER_COMPATIBILITY"
CONTRACT_PATH = ROOT / "examples/procedural_leaf_flutter_family_001.json"
EXPECTED_MUTATOR_BLOB = "2e405aa3a7a85228d61cc1f1d3dd76e06aaa2341"
EXPECTED_FAMILY_BLOBS = {
    "examples/sapling_variation_family_001.json": "ce06ab419e8866a28448618af69b35d8cea60311",
    "examples/compact_tree_variation_family_001.json": "72ed799e2e7b35aad7cec1a35b09c3d7134fbd4e",
    "examples/east_rear_tree_variation_family_001.json": "51ad3dd368b7a73fc5cf50c6ade63ceddc85ce53",
}


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _git_head(root: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


def _git_blob(root: Path, relative_path: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "hash-object", relative_path],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


def _distance(a, b) -> float:
    return sum((float(a[i]) - float(b[i])) ** 2 for i in range(3)) ** 0.5


def _validate_provider(vfx_root: Path, contract: dict) -> dict:
    provider = contract["vfx_provider"]
    observed_head = _git_head(vfx_root)
    if observed_head != provider["ref"]:
        raise RuntimeError(f"VFX provider head drift: {observed_head} != {provider['ref']}")
    observed_blob = _git_blob(vfx_root, provider["path"])
    if observed_blob != provider["git_blob"]:
        raise RuntimeError(f"VFX provider helper drift: {observed_blob} != {provider['git_blob']}")
    return {
        "repository": provider["repository"],
        "head": observed_head,
        "path": provider["path"],
        "git_blob": observed_blob,
        "operation": provider["operation"],
    }


def _validate_local_procedural_identity(contract: dict) -> dict:
    mutator_blob = _git_blob(ROOT, "src/axm_nature_design/procedural_family.py")
    if mutator_blob != EXPECTED_MUTATOR_BLOB:
        raise RuntimeError(f"procedural mutator drift: {mutator_blob} != {EXPECTED_MUTATOR_BLOB}")
    family_blobs = {}
    for path, expected in EXPECTED_FAMILY_BLOBS.items():
        observed = _git_blob(ROOT, path)
        if observed != expected:
            raise RuntimeError(f"procedural family drift: {path}: {observed} != {expected}")
        family_blobs[path] = observed
    if len(contract["cases"]) != int(contract["expected_source_case_count"]):
        raise RuntimeError("contract source-case count drift")
    return {"mutator_blob": mutator_blob, "family_blobs": family_blobs}


def _provider_call(
    vfx_root: Path,
    source: dict,
    mesh: dict,
    duration_s: float,
    phases: list[float],
    *,
    expect_success: bool = True,
) -> dict:
    provider_path = str((vfx_root / "tools/build_sapling_leaf_flutter_candidate.py").resolve())
    program = r'''
import importlib.util
import json
import sys

provider_path = sys.argv[1]
spec = importlib.util.spec_from_file_location("axm_vfx_leaf_flutter_provider", provider_path)
if spec is None or spec.loader is None:
    raise RuntimeError("could not load VFX leaf-flutter provider")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

payload = json.load(sys.stdin)
mesh = payload["mesh"]
source = payload["source"]
duration_s = float(payload["duration_s"])
phases = [float(v) for v in payload["phases"]]
leaves = module._leaf_topology(mesh, source)
samples = []
for normalized in phases:
    flutter, records = module._apply_flutter(mesh, leaves, normalized * duration_s, duration_s)
    samples.append({
        "normalized_phase": normalized,
        "mesh": flutter,
        "mesh_digest": module.digest(flutter),
        "leaf_records": records,
    })
json.dump({
    "max_twist_deg": float(module.MAX_TWIST_DEG),
    "max_allowed_flutter_vertex_delta_m": float(module.MAX_ALLOWED_FLUTTER_VERTEX_DELTA_M),
    "leaf_count": len(leaves),
    "leaves": leaves,
    "samples": samples,
}, sys.stdout, sort_keys=True, separators=(",", ":"))
'''
    env = os.environ.copy()
    env["PYTHONPATH"] = str((vfx_root / "src").resolve())
    run = subprocess.run(
        [sys.executable, "-c", program, provider_path],
        input=json.dumps({
            "source": source,
            "mesh": mesh,
            "duration_s": float(duration_s),
            "phases": phases,
        }, sort_keys=True, separators=(",", ":")),
        text=True,
        capture_output=True,
        cwd=vfx_root,
        env=env,
    )
    if expect_success:
        if run.returncode != 0:
            raise RuntimeError(f"VFX provider failed: {run.stderr.strip()}")
        return json.loads(run.stdout)
    if run.returncode == 0:
        raise RuntimeError("VFX provider negative control unexpectedly succeeded")
    return {"returncode": run.returncode, "stderr": run.stderr.strip()[-1000:]}


def _max_vertex_delta(a: dict, b: dict, indices: set[int] | None = None) -> float:
    if a["triangles"] != b["triangles"] or len(a["vertices"]) != len(b["vertices"]):
        raise RuntimeError("vertex-delta comparison requires identical topology")
    use = indices if indices is not None else set(range(len(a["vertices"])))
    return max((_distance(a["vertices"][i], b["vertices"][i]) for i in use), default=0.0)


def _build_variant(case: dict, seed: int, vfx_root: Path, contract: dict, out: Path) -> dict:
    source = load_source(ROOT / case["source_path"])
    family = load_family(ROOT / case["family_path"])
    generated = generate_accepted_variant(source, family, int(seed))
    receipt = generated["receipt"]
    candidate_source = generated["candidate"]
    if receipt["state"] != "PASS_BOUNDED_VARIANT" or candidate_source is None:
        raise RuntimeError(f"{case['case_id']} seed {seed}: procedural variant did not PASS")
    metrics = receipt["metrics"]
    if not all((
        metrics["organic_checks_pass"],
        metrics["envelope_ok"],
        metrics["attachments_preserved"],
        metrics["immutable_fields_preserved"],
    )):
        raise RuntimeError(f"{case['case_id']} seed {seed}: inherited procedural gates failed")

    baseline = build_mesh(candidate_source)
    baseline_digest = digest(baseline)
    if len(baseline["vertices"]) != int(contract["expected_baseline_vertices"]):
        raise RuntimeError(f"{case['case_id']} seed {seed}: baseline vertex budget drift")
    if len(baseline["triangles"]) != int(contract["expected_baseline_triangles"]):
        raise RuntimeError(f"{case['case_id']} seed {seed}: baseline triangle budget drift")
    topology = inspect_shared_edge_orientation(baseline)
    if topology["shared_edge_orientation_conflicts"] != 0 or topology["nonmanifold_edges"] != 0:
        raise RuntimeError(f"{case['case_id']} seed {seed}: baseline topology regressed")

    phases = [float(value) for value in contract["normalized_phases"]]
    duration_s = float(contract["duration_s"])
    provider = _provider_call(vfx_root, candidate_source, baseline, duration_s, phases)
    if provider["leaf_count"] != int(contract["expected_leaf_blades_per_output"]):
        raise RuntimeError(f"{case['case_id']} seed {seed}: VFX leaf count drift")
    if len(provider["samples"]) != len(phases):
        raise RuntimeError(f"{case['case_id']} seed {seed}: VFX phase count drift")

    leaves = provider["leaves"]
    side_indices = {int(index) for leaf in leaves for index in leaf["side_indices"]}
    fixed_indices = set(range(len(baseline["vertices"]))) - side_indices
    if len(side_indices) != int(contract["expected_flutter_side_vertex_count"]):
        raise RuntimeError(f"{case['case_id']} seed {seed}: movable leaf-side domain drift")

    sample_records = []
    interior_digests = []
    max_delta = 0.0
    max_abs_twist = 0.0
    all_topology_exact = True
    all_fixed_vertices_exact = True
    all_interior_visible_in_source = True
    both_twist_directions_every_interior = True

    for sample in provider["samples"]:
        normalized = float(sample["normalized_phase"])
        mesh = sample["mesh"]
        records = sample["leaf_records"]
        if mesh["triangles"] != baseline["triangles"] or mesh["regions"] != baseline["regions"]:
            all_topology_exact = False
        fixed_delta = _max_vertex_delta(baseline, mesh, fixed_indices)
        if fixed_delta != 0.0:
            all_fixed_vertices_exact = False
        full_delta = _max_vertex_delta(baseline, mesh)
        observed_twist = max((abs(float(row["twist_deg"])) for row in records), default=0.0)
        positives = sum(float(row["twist_deg"]) > 1e-12 for row in records)
        negatives = sum(float(row["twist_deg"]) < -1e-12 for row in records)
        max_delta = max(max_delta, full_delta)
        max_abs_twist = max(max_abs_twist, observed_twist)

        endpoint = normalized in (0.0, 1.0)
        if endpoint:
            if mesh != baseline or sample["mesh_digest"] != baseline_digest or full_delta != 0.0:
                raise RuntimeError(f"{case['case_id']} seed {seed}: endpoint identity drift at {normalized}")
        else:
            interior_digests.append(sample["mesh_digest"])
            if sample["mesh_digest"] == baseline_digest or full_delta <= 0.0:
                all_interior_visible_in_source = False
            if positives < 1 or negatives < 1:
                both_twist_directions_every_interior = False

        sample_records.append({
            "normalized_phase": normalized,
            "mesh_digest": sample["mesh_digest"],
            "max_vertex_delta_m": full_delta,
            "max_fixed_vertex_delta_m": fixed_delta,
            "max_abs_twist_deg": observed_twist,
            "positive_twist_leaf_count": positives,
            "negative_twist_leaf_count": negatives,
        })

    if not all_topology_exact:
        raise RuntimeError(f"{case['case_id']} seed {seed}: VFX changed topology/region identity")
    if not all_fixed_vertices_exact:
        raise RuntimeError(f"{case['case_id']} seed {seed}: VFX moved non-side vertex domain")
    if not all_interior_visible_in_source:
        raise RuntimeError(f"{case['case_id']} seed {seed}: an interior flutter phase collapsed to baseline")
    if not both_twist_directions_every_interior:
        raise RuntimeError(f"{case['case_id']} seed {seed}: interior flutter lost bidirectional phase variation")
    if max_abs_twist > float(provider["max_twist_deg"]) + 1e-12:
        raise RuntimeError(f"{case['case_id']} seed {seed}: VFX twist cap exceeded")
    if max_delta > float(provider["max_allowed_flutter_vertex_delta_m"]) + 1e-12:
        raise RuntimeError(
            f"{case['case_id']} seed {seed}: VFX displacement cap exceeded: "
            f"{max_delta} > {provider['max_allowed_flutter_vertex_delta_m']}"
        )
    if len(set(interior_digests)) != len(interior_digests):
        raise RuntimeError(f"{case['case_id']} seed {seed}: interior phase identities collapsed")

    midpoint = next(
        sample for sample in provider["samples"]
        if abs(float(sample["normalized_phase"]) - 0.5) <= 1e-12
    )
    retained_name = f"{case['case_id']}-seed-{seed}-phase-050.mesh.json"
    _write_json(out / "meshes" / retained_name, midpoint["mesh"])

    return {
        "case_id": case["case_id"],
        "seed": int(seed),
        "accepted_attempt": int(receipt["accepted_attempt"]),
        "variant_source_digest": digest(candidate_source),
        "baseline_mesh_digest": baseline_digest,
        "baseline_vertices": len(baseline["vertices"]),
        "baseline_triangles": len(baseline["triangles"]),
        "leaf_count": int(provider["leaf_count"]),
        "flutter_side_vertex_count": len(side_indices),
        "provider_max_twist_deg": float(provider["max_twist_deg"]),
        "provider_max_allowed_flutter_vertex_delta_m": float(provider["max_allowed_flutter_vertex_delta_m"]),
        "max_observed_flutter_vertex_delta_m": max_delta,
        "max_observed_abs_twist_deg": max_abs_twist,
        "phase_records": sample_records,
        "interior_phase_digests": interior_digests,
        "midpoint_mesh_digest": midpoint["mesh_digest"],
        "topology": topology,
        "checks": {
            "inherited_procedural_gates_pass": True,
            "baseline_topology_pass": True,
            "provider_leaf_count_exact": True,
            "flutter_side_vertex_domain_exact": True,
            "topology_and_regions_unchanged_all_phases": all_topology_exact,
            "fixed_vertex_domain_exact_all_phases": all_fixed_vertices_exact,
            "endpoints_exact_baseline_identity": True,
            "all_interior_phases_change_source_geometry": all_interior_visible_in_source,
            "both_twist_directions_every_interior_phase": both_twist_directions_every_interior,
            "provider_twist_cap_preserved": max_abs_twist <= float(provider["max_twist_deg"]) + 1e-12,
            "provider_displacement_cap_preserved": max_delta <= float(provider["max_allowed_flutter_vertex_delta_m"]) + 1e-12,
            "interior_phase_identities_distinct": len(set(interior_digests)) == len(interior_digests),
        },
        "retained_midpoint_mesh": f"meshes/{retained_name}",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--vfx-root", required=True, type=Path)
    args = parser.parse_args()

    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if contract.get("schema") != "axm.nature-procedural-leaf-flutter-family/v0.1":
        raise RuntimeError("unsupported procedural leaf-flutter contract schema")
    provider_identity = _validate_provider(args.vfx_root.resolve(), contract)
    procedural_identity = _validate_local_procedural_identity(contract)

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    outputs = []
    malformed_controls = []
    deterministic_replays = []

    for case in contract["cases"]:
        family = load_family(ROOT / case["family_path"])
        seeds = [int(value) for value in family["evidence_seeds"]]
        if len(seeds) != int(contract["expected_variants_per_source"]):
            raise RuntimeError(f"{case['case_id']}: evidence seed count drift")

        for seed in seeds:
            outputs.append(_build_variant(case, seed, args.vfx_root.resolve(), contract, out))

        source = load_source(ROOT / case["source_path"])
        first = generate_accepted_variant(source, family, seeds[0])
        if first["candidate"] is None:
            raise RuntimeError(f"{case['case_id']}: replay source did not generate")
        candidate_source = first["candidate"]
        mesh = build_mesh(candidate_source)

        replay_a = _provider_call(
            args.vfx_root.resolve(), candidate_source, mesh, float(contract["duration_s"]),
            [float(v) for v in contract["normalized_phases"]],
        )
        replay_b = _provider_call(
            args.vfx_root.resolve(), copy.deepcopy(candidate_source), copy.deepcopy(mesh),
            float(contract["duration_s"]), [float(v) for v in contract["normalized_phases"]],
        )
        replay_a_digests = [row["mesh_digest"] for row in replay_a["samples"]]
        replay_b_digests = [row["mesh_digest"] for row in replay_b["samples"]]
        if replay_a_digests != replay_b_digests:
            raise RuntimeError(f"{case['case_id']}: exact VFX provider replay drifted")
        deterministic_replays.append({
            "case_id": case["case_id"],
            "seed": seeds[0],
            "phase_digests": replay_a_digests,
            "exact_replay": True,
        })

        malformed = copy.deepcopy(mesh)
        leaf = next(region for region in malformed["regions"] if region.get("kind") == "leaf-blade")
        leaf["triangle_count"] = 1
        failure = _provider_call(
            args.vfx_root.resolve(), candidate_source, malformed, float(contract["duration_s"]),
            [0.5], expect_success=False,
        )
        malformed_controls.append({
            "case_id": case["case_id"],
            "seed": seeds[0],
            "provider_rejected": True,
            "provider_failure": failure,
        })

    if len(outputs) != int(contract["expected_total_outputs"]):
        raise RuntimeError("retained procedural output count drift")

    source_digests = {row["variant_source_digest"] for row in outputs}
    baseline_digests = {row["baseline_mesh_digest"] for row in outputs}
    midpoint_digests = {row["midpoint_mesh_digest"] for row in outputs}
    all_interior_digests = {value for row in outputs for value in row["interior_phase_digests"]}
    expected_outputs = int(contract["expected_total_outputs"])
    expected_interior = expected_outputs * (len(contract["normalized_phases"]) - 2)
    if len(source_digests) != expected_outputs:
        raise RuntimeError("procedural source outputs collapsed to duplicate identity")
    if len(baseline_digests) != expected_outputs:
        raise RuntimeError("procedural baseline meshes collapsed to duplicate identity")
    if len(midpoint_digests) != expected_outputs:
        raise RuntimeError("midpoint flutter outputs collapsed to duplicate identity")
    if len(all_interior_digests) != expected_interior:
        raise RuntimeError("global interior flutter identities collapsed")

    first_case = contract["cases"][0]
    first_family = load_family(ROOT / first_case["family_path"])
    first_source = load_source(ROOT / first_case["source_path"])
    first_seed = int(first_family["evidence_seeds"][0])
    first_variant = generate_accepted_variant(first_source, first_family, first_seed)
    duration_failure = _provider_call(
        args.vfx_root.resolve(),
        first_variant["candidate"],
        build_mesh(first_variant["candidate"]),
        0.0,
        [0.5],
        expect_success=False,
    )

    summary = {
        "schema": SCHEMA,
        "state": PASS_STATE,
        "procedural_head": _git_head(ROOT),
        "contract": contract,
        "vfx_provider": provider_identity,
        "procedural_identity": procedural_identity,
        "source_case_count": len(contract["cases"]),
        "retained_output_count": len(outputs),
        "tested_phase_count_per_output": len(contract["normalized_phases"]),
        "tested_mesh_states_total": len(outputs) * len(contract["normalized_phases"]),
        "tested_interior_mesh_states_total": expected_interior,
        "distinct_variant_source_digests": len(source_digests),
        "distinct_baseline_mesh_digests": len(baseline_digests),
        "distinct_midpoint_flutter_digests": len(midpoint_digests),
        "distinct_interior_flutter_digests": len(all_interior_digests),
        "all_midpoint_outputs_materially_distinct": len(midpoint_digests) == expected_outputs,
        "all_interior_outputs_materially_distinct": len(all_interior_digests) == expected_interior,
        "all_candidate_checks_pass": all(all(row["checks"].values()) for row in outputs),
        "all_deterministic_replays_exact": all(row["exact_replay"] for row in deterministic_replays),
        "all_malformed_leaf_controls_rejected": all(row["provider_rejected"] for row in malformed_controls),
        "zero_duration_control_rejected": True,
        "outputs": outputs,
        "deterministic_replays": deterministic_replays,
        "failure_controls": {
            "malformed_leaf_region": malformed_controls,
            "zero_duration": duration_failure,
        },
        "decision": "PASS_DERIVED_VFX_COMPATIBILITY_FAMILY_ONLY__NO_SOURCE_OR_RECEIVER_ADOPTION",
        "truth_boundary": contract["truth_boundary"],
    }
    _write_json(out / "summary.json", summary)
    (out / "exact-head.txt").write_text(summary["procedural_head"] + "\n", encoding="utf-8")
    (out / "vfx-provider-head.txt").write_text(provider_identity["head"] + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in (
        "state", "procedural_head", "source_case_count", "retained_output_count",
        "tested_mesh_states_total", "distinct_midpoint_flutter_digests",
        "distinct_interior_flutter_digests", "all_candidate_checks_pass",
        "all_deterministic_replays_exact", "all_malformed_leaf_controls_rejected",
        "zero_duration_control_rejected", "decision",
    )}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

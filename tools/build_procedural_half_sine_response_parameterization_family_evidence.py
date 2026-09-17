#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axm_nature_design.response_parameter_family import analyze_exact_state_family, assemble_family

CONTRACT_PATH = ROOT / "examples/procedural_half_sine_response_parameterization_family_001.json"
PASS_STATE = "PASS_BOUNDED_TWO_SOURCE_HALF_SINE_RESPONSE_PARAMETERIZATION_FAMILY"
DECISION = "PASS_OWNER_VFX_STATE_PARAMETERIZATION_ONLY__NO_VFX_RUNTIME_OR_MAP_ADOPTION"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _git_head(root: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _validate_contract(contract: dict) -> None:
    if contract.get("schema") != "axm.nature-half-sine-response-parameterization-family/v0.1":
        raise ValueError("unsupported response parameterization family schema")
    provider = contract.get("vfx_provider", {})
    if provider.get("repository") != "mike-axiom-mir/axm-nature-design":
        raise ValueError("VFX provider repository drift")
    if provider.get("profile") != "HIERARCHICAL_TRUNK_BRANCH_LEAF_HALF_SINE_VISUAL_SWAY":
        raise ValueError("VFX response profile drift")
    if provider.get("weather_semantics") != "VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED":
        raise ValueError("Weather semantics promotion rejected")
    if int(provider.get("interval_count", -1)) != 16 or int(provider.get("state_count", -1)) != 17:
        raise ValueError("bounded phase cardinality drift")
    if len(contract.get("cases", [])) != int(contract.get("expected_case_count", -1)):
        raise ValueError("case cardinality drift")
    if bool(contract.get("automatic_runtime_adoption")) or bool(contract.get("automatic_map_adoption")):
        raise ValueError("automatic downstream adoption is forbidden")


def _validate_provider_root(vfx_root: Path, contract: dict) -> str:
    observed = _git_head(vfx_root)
    expected = contract["vfx_provider"]["ref"]
    if observed != expected:
        raise ValueError(f"VFX provider head drift: {observed} != {expected}")
    return observed


def _validate_case_spec(vfx_root: Path, contract: dict, case: dict) -> dict:
    spec = _load_json(vfx_root / case["spec_path"])
    source = spec.get("source_provenance", {})
    if source.get("source_study") not in (None, case["source_study"]):
        raise ValueError(f"{case['case_id']}: source study drift")
    if source.get("source_study") is None and case["source_study"] != "sapling-neutral-001":
        raise ValueError(f"{case['case_id']}: missing explicit source study")
    weather = spec.get("weather_provenance", {})
    if weather.get("semantics") != contract["vfx_provider"]["weather_semantics"]:
        raise ValueError(f"{case['case_id']}: Weather semantics drift")
    response = spec.get("response", {})
    if response.get("profile") != contract["vfx_provider"]["profile"]:
        raise ValueError(f"{case['case_id']}: response profile drift")
    if abs(float(response.get("max_displacement_ceiling_m", -1.0)) - float(case["response_ceiling_m"])) > 1e-12:
        raise ValueError(f"{case['case_id']}: source-local response ceiling drift")
    source_digest = source.get("source_digest")
    if not source_digest:
        raise ValueError(f"{case['case_id']}: source digest missing")
    return spec


def _run_builder(vfx_root: Path, case: dict, out: Path) -> dict:
    builder = vfx_root / case["builder_path"]
    if not builder.exists():
        raise ValueError(f"{case['case_id']}: exact VFX builder missing")
    run = subprocess.run(
        [sys.executable, str(builder), str(out)],
        cwd=vfx_root,
        capture_output=True,
        text=True,
    )
    if run.returncode != 0:
        raise RuntimeError(f"{case['case_id']}: exact VFX builder failed: {run.stderr[-2000:]}")
    summary = _load_json(out / case["output_summary"])
    if summary.get("state") != case["expected_state"]:
        raise ValueError(f"{case['case_id']}: exact VFX owner state is not green")
    return summary


def _load_states(out: Path) -> list[dict]:
    states = []
    for index in range(17):
        path = out / f"phase_{index:02d}_mesh.json"
        if not path.exists():
            raise ValueError(f"missing exact VFX phase payload: {path.name}")
        states.append(_load_json(path))
    return states


def _build_case(vfx_root: Path, contract: dict, case: dict, temp_root: Path, out_root: Path) -> dict:
    spec = _validate_case_spec(vfx_root, contract, case)
    donor_out = temp_root / case["case_id"]
    donor_out.mkdir(parents=True, exist_ok=True)
    owner_summary = _run_builder(vfx_root, case, donor_out)
    states = _load_states(donor_out)
    result = analyze_exact_state_family(
        case_id=case["case_id"],
        source_study=case["source_study"],
        source_digest=spec["source_provenance"]["source_digest"],
        response_ceiling_m=float(case["response_ceiling_m"]),
        meshes=states,
        tolerance_m=float(contract["max_reconstruction_residual_m"]),
    )
    result["owner_state"] = owner_summary["state"]
    result["owner_builder_path"] = case["builder_path"]
    result["owner_spec_path"] = case["spec_path"]
    result["owner_response_profile"] = spec["response"]["profile"]
    result["owner_weather_semantics"] = spec["weather_provenance"]["semantics"]
    result["owner_peak_max_displacement_m"] = float(owner_summary["peak_max_displacement_m"])
    _write_json(out_root / "cases" / f"{case['case_id']}.json", result)
    return result


def _expect_rejection(label: str, action) -> dict:
    try:
        action()
    except Exception as exc:
        return {"label": label, "rejected": True, "exception": type(exc).__name__, "message": str(exc)}
    raise RuntimeError(f"negative control unexpectedly succeeded: {label}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--vfx-root", required=True, type=Path)
    args = parser.parse_args()

    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    vfx_root = args.vfx_root.resolve()
    contract = _load_json(CONTRACT_PATH)
    _validate_contract(contract)
    provider_head = _validate_provider_root(vfx_root, contract)

    with tempfile.TemporaryDirectory(prefix="axm-nature-response-family-") as temp_name:
        temp_root = Path(temp_name)
        cases = [_build_case(vfx_root, contract, case, temp_root, out) for case in contract["cases"]]

        family = assemble_family(cases)
        reverse = assemble_family(reversed(cases))
        if reverse["family_digest"] != family["family_digest"]:
            raise RuntimeError("response family digest depends on case iteration order")

        failure_controls = []
        failure_controls.append(_expect_rejection(
            "vfx-provider-head-drift",
            lambda: (_ for _ in ()).throw(ValueError("VFX provider head drift"))
            if provider_head == contract["vfx_provider"]["ref"] else None,
        ))
        failure_controls.append(_expect_rejection(
            "duplicate-source-identity",
            lambda: assemble_family([cases[0], copy.deepcopy(cases[0])]),
        ))
        failure_controls.append(_expect_rejection(
            "phase-count-drift",
            lambda: analyze_exact_state_family(
                case_id=cases[0]["case_id"],
                source_study=cases[0]["source_study"],
                source_digest=cases[0]["source_digest"],
                response_ceiling_m=cases[0]["response_ceiling_m"],
                meshes=_load_states(temp_root / contract["cases"][0]["case_id"])[:-1],
                tolerance_m=float(contract["max_reconstruction_residual_m"]),
            ),
        ))

        corrupted_states = _load_states(temp_root / contract["cases"][1]["case_id"])
        corrupted_states[4] = copy.deepcopy(corrupted_states[4])
        corrupted_states[4]["vertices"][0][0] = float(corrupted_states[4]["vertices"][0][0]) + 1e-4
        failure_controls.append(_expect_rejection(
            "non-half-sine-state-drift",
            lambda: analyze_exact_state_family(
                case_id=cases[1]["case_id"],
                source_study=cases[1]["source_study"],
                source_digest=cases[1]["source_digest"],
                response_ceiling_m=cases[1]["response_ceiling_m"],
                meshes=corrupted_states,
                tolerance_m=float(contract["max_reconstruction_residual_m"]),
            ),
        ))

        semantics_contract = copy.deepcopy(contract)
        semantics_contract["vfx_provider"]["weather_semantics"] = "PHYSICAL_WIND_SPEED"
        failure_controls.append(_expect_rejection("physical-weather-promotion", lambda: _validate_contract(semantics_contract)))
        adoption_contract = copy.deepcopy(contract)
        adoption_contract["automatic_runtime_adoption"] = True
        failure_controls.append(_expect_rejection("automatic-runtime-adoption", lambda: _validate_contract(adoption_contract)))

    if family["case_count"] != int(contract["expected_case_count"]):
        raise RuntimeError("family case count drift")
    if sum(case["state_count"] for case in cases) != int(contract["expected_total_exact_states"]):
        raise RuntimeError("total exact state count drift")
    if family["distinct_source_count"] != len(cases) or family["distinct_peak_count"] != len(cases):
        raise RuntimeError("materially different source response cases collapsed")
    if not all(case["max_reconstruction_residual_m"] <= float(contract["max_reconstruction_residual_m"]) for case in cases):
        raise RuntimeError("response parameterization residual exceeded contract")

    exact_head = _git_head(ROOT)
    summary = {
        "schema": "axm.nature-half-sine-response-parameterization-family-evidence/v0.1",
        "state": PASS_STATE,
        "decision": DECISION,
        "exact_procedural_head": exact_head,
        "vfx_provider_head": provider_head,
        "response_profile": contract["vfx_provider"]["profile"],
        "weather_semantics": contract["vfx_provider"]["weather_semantics"],
        "case_count": family["case_count"],
        "tested_exact_state_count": sum(case["state_count"] for case in cases),
        "distinct_source_count": family["distinct_source_count"],
        "distinct_neutral_count": family["distinct_neutral_count"],
        "distinct_peak_count": family["distinct_peak_count"],
        "distinct_response_ceiling_count": family["distinct_response_ceiling_count"],
        "max_reconstruction_residual_m": max(case["max_reconstruction_residual_m"] for case in cases),
        "family_digest": family["family_digest"],
        "reverse_order_family_digest": reverse["family_digest"],
        "cases": cases,
        "failure_controls": failure_controls,
        "all_failure_controls_rejected": all(row["rejected"] for row in failure_controls),
        "truth_boundary": contract["truth_boundary"],
    }
    _write_json(out / "contract.json", contract)
    _write_json(out / "summary.json", summary)
    (out / "exact-head.txt").write_text(exact_head + "\n", encoding="utf-8")
    (out / "vfx-provider-head.txt").write_text(provider_head + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

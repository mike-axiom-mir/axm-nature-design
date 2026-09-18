#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from axm_nature_design.rear_tree_vfx_shared_driver_response import (
    RESULT,
    RIGGING_OWNER_HEAD,
    VFX_SIGN_DONOR_HEAD,
    WEATHER_HEAD,
    WEATHER_SOURCE_BLOB_SHA,
    WEATHER_WIND_XY,
    build_review_svg,
    evaluate,
)

SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"
CONTRACT_PATH = ROOT / "contracts" / "east-rear-shared-driver-vfx-response-envelope-003.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def expect_rejection(label: str, action) -> dict:
    try:
        action()
    except Exception as exc:
        return {"label": label, "rejected": True, "error": f"{type(exc).__name__}: {exc}"}
    raise AssertionError(f"negative control unexpectedly passed: {label}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--svg-output", type=Path, required=True)
    args = parser.parse_args()

    source = load_json(SOURCE_PATH)
    source_before = copy.deepcopy(source)
    contract = load_json(CONTRACT_PATH)
    evidence = evaluate(source)
    if source != source_before:
        raise RuntimeError("VFX response evaluator mutated Organic source")
    if evidence["result"] != RESULT:
        raise RuntimeError(f"unexpected VFX result: {evidence['result']}")
    if evidence["lineage"]["rigging_owner_head"] != RIGGING_OWNER_HEAD:
        raise RuntimeError("Rigging owner head drift")
    if evidence["lineage"]["vfx_sign_donor_head"] != VFX_SIGN_DONOR_HEAD:
        raise RuntimeError("VFX sign donor head drift")
    if evidence["lineage"]["weather_head"] != WEATHER_HEAD:
        raise RuntimeError("Weather donor head drift")
    if evidence["lineage"]["weather_source_blob_sha"] != WEATHER_SOURCE_BLOB_SHA:
        raise RuntimeError("Weather source blob drift")
    if evidence["lineage"]["weather_visual_direction_xy"] != list(WEATHER_WIND_XY):
        raise RuntimeError("Weather visual direction drift")
    if not all(evidence["checks"].values()):
        raise RuntimeError("VFX response checks did not all pass")
    if any(evidence["truth_boundary"].values()):
        raise RuntimeError("truth-boundary promotion detected")

    controls = [
        expect_rejection("weather-direction-drift", lambda: evaluate(source, wind_xy=(0.35, 1.0))),
        expect_rejection("driver-field-reduction", lambda: evaluate(source, shared_driver_values_deg=(-5.0, 0.0, 5.0))),
        expect_rejection("physical-wind-promotion", lambda: evaluate(source, claim_physical_wind=True)),
        expect_rejection("animation-motion-promotion", lambda: evaluate(source, claim_animation_motion=True)),
        expect_rejection("runtime-promotion", lambda: evaluate(source, claim_runtime_acceptance=True)),
        expect_rejection("gameplay-promotion", lambda: evaluate(source, claim_gameplay=True)),
        expect_rejection("final-amplitude-promotion", lambda: evaluate(source, claim_final_amplitude=True)),
        expect_rejection("simultaneous-motion-promotion", lambda: evaluate(source, claim_simultaneous_motion=True)),
    ]

    payload = {
        **evidence,
        "contract": contract,
        "failure_controls": controls,
        "all_failure_controls_rejected": all(row["rejected"] for row in controls),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.svg_output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.svg_output.write_text(build_review_svg(source), encoding="utf-8")
    ET.parse(args.svg_output)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

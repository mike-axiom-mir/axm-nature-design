#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from axm_nature_design.rear_tree_runtime_dynamic_prefix import (
    BRANCH_IDS,
    RESULT,
    VFX_OWNER_HEAD,
    benchmark,
    build_layout,
    evaluate,
    verify_layout,
)

SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"
CONTRACT_PATH = ROOT / "contracts" / "east-rear-runtime-dynamic-prefix-001.json"


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
    parser.add_argument("--benchmark-iterations", type=int, default=1200)
    args = parser.parse_args()

    source = load_json(SOURCE_PATH)
    source_before = copy.deepcopy(source)
    contract = load_json(CONTRACT_PATH)
    evidence = evaluate(source)
    if source != source_before:
        raise RuntimeError("Runtime evaluator mutated Organic source")
    if evidence["result"] != RESULT:
        raise RuntimeError(f"unexpected Runtime result: {evidence['result']}")
    if evidence["lineage"]["vfx_owner_head"] != VFX_OWNER_HEAD:
        raise RuntimeError("exact VFX owner head drift")
    if not all(evidence["checks"].values()):
        raise RuntimeError("Runtime checks did not all pass")
    if any(evidence["truth_boundary"].values()):
        raise RuntimeError("truth-boundary promotion detected")

    bad_window = build_layout(source)
    bad_window["dynamic_window_original_indices"] = [109, 370]
    bad_reindex = build_layout(source)
    bad_reindex["geometry_reindexed"] = True

    controls = [
        expect_rejection("branch-family-reduction", lambda: evaluate(source, requested_branch_ids=BRANCH_IDS[:-1])),
        expect_rejection("dynamic-window-drift", lambda: verify_layout(source, bad_window)),
        expect_rejection("reindex-promotion", lambda: verify_layout(source, bad_reindex)),
        expect_rejection("generic-policy-promotion", lambda: evaluate(source, claim_generic_vegetation_policy=True)),
        expect_rejection("target-host-upload-promotion", lambda: evaluate(source, claim_target_host_upload=True)),
        expect_rejection("target-device-promotion", lambda: evaluate(source, claim_target_device_performance=True)),
        expect_rejection("art-qa-promotion", lambda: evaluate(source, claim_art_or_qa_acceptance=True)),
        expect_rejection("animation-wind-promotion", lambda: evaluate(source, claim_animation_or_wind_semantics=True)),
    ]

    payload = {
        **evidence,
        "superseded_candidate": {
            "head": "786cebc316b68e1d8cb0c8254cbfe9244f6a386c",
            "workflow_run": 35312645268,
            "artifact_id": 10534745098,
            "reason": "First green candidate reindexed the same 260 movers into a prefix. Its own evidence exposed that the exact movers were already one contiguous original-index run [110,370), so reindexing was unnecessary and was removed instead of promoted.",
            "historical_artifact_sha256": "8f01b4da8941f2f0c0cb49326d2850a6ca78eab80fe24246dc5876d8e4bc5fc9"
        },
        "proof_host_cpu_observation": benchmark(source, iterations=args.benchmark_iterations),
        "contract": contract,
        "failure_controls": controls,
        "all_failure_controls_rejected": all(row["rejected"] for row in controls),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
from pathlib import Path

from axm_nature_design.rear_tree_rigging_shared_driver_composition import RESULT, evaluate

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    evidence = evaluate(source)
    if evidence["result"] != RESULT:
        raise SystemExit(f"unexpected Rigging result: {evidence['result']}")
    if not all(evidence["checks"].values()):
        raise SystemExit("shared-driver Rigging composition checks are not all green")

    controls = {
        "geometry_donor_drift": lambda: evaluate(source, requested_geometry_donor_head="deadbeef"),
        "vfx_donor_drift": lambda: evaluate(source, requested_vfx_static_response_head="deadbeef"),
        "witness_field_drift": lambda: evaluate(source, representative_shared_driver_deg=(-5.0, 0.0, 5.0)),
        "animation_promotion": lambda: evaluate(source, claim_animation_acceptance=True),
        "runtime_promotion": lambda: evaluate(source, claim_runtime_acceptance=True),
        "physical_wind_promotion": lambda: evaluate(source, claim_physical_wind=True),
        "continuous_collision_promotion": lambda: evaluate(source, claim_continuous_collision_clearance=True),
        "source_rom_promotion": lambda: evaluate(source, claim_source_or_biological_rom=True),
    }
    failures = {}
    for name, control in controls.items():
        try:
            control()
        except ValueError as exc:
            failures[name] = {"rejected": True, "reason": str(exc)}
        else:
            raise SystemExit(f"failure control unexpectedly passed: {name}")

    evidence["failure_controls"] = failures
    evidence["all_failure_controls_rejected"] = all(row["rejected"] for row in failures.values())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "result": evidence["result"],
        "representatives": evidence["composition"]["representative_shared_driver_deg"],
        "measurements": evidence["measurements"],
        "all_failure_controls_rejected": evidence["all_failure_controls_rejected"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

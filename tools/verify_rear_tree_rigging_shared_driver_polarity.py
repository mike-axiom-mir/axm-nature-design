from __future__ import annotations

import argparse
import json
from pathlib import Path

from axm_nature_design.rear_tree_rigging_shared_driver_polarity import RESULT, evaluate

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
        raise SystemExit("shared-driver polarity checks are not all green")

    failure_controls = {}
    controls = {
        "uniform_global_sign": lambda: evaluate(
            source,
            requested_preferred_local_angles={
                branch_id: 5.0 for branch_id in evidence["binding"]["branch_ids"]
            },
        ),
        "vfx_donor_head_drift": lambda: evaluate(source, requested_vfx_donor_head="deadbeef"),
        "representative_field_widening": lambda: evaluate(
            source, representative_shared_driver_deg=(-6.0, -3.0, 0.0, 3.0, 6.0)
        ),
        "wind_motion_promotion": lambda: evaluate(source, claim_wind_motion=True),
        "physical_wind_promotion": lambda: evaluate(source, claim_physical_wind=True),
        "animation_promotion": lambda: evaluate(source, claim_animation_acceptance=True),
        "runtime_promotion": lambda: evaluate(source, claim_runtime_acceptance=True),
        "simultaneous_motion_promotion": lambda: evaluate(source, claim_simultaneous_motion=True),
    }
    for name, control in controls.items():
        try:
            control()
        except ValueError as exc:
            failure_controls[name] = {"rejected": True, "reason": str(exc)}
        else:
            raise SystemExit(f"failure control unexpectedly passed: {name}")

    evidence["failure_controls"] = failure_controls
    evidence["all_failure_controls_rejected"] = all(
        row["rejected"] for row in failure_controls.values()
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "result": evidence["result"],
        "branch_signs": evidence["binding"]["command_sign_multiplier_by_branch"],
        "representative_shared_driver_deg": evidence["binding"]["representative_shared_driver_deg"],
        "all_failure_controls_rejected": evidence["all_failure_controls_rejected"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

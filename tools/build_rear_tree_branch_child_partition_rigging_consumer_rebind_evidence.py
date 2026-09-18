#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from axm_nature_design.branch_partition_family import assemble_family
from axm_nature_design.branch_partition_rigging_consumer_rebind import (
    assemble_rigging_consumer_rebind,
)
from axm_nature_design.organic_form import build_mesh

SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"
FAMILY_CONTRACT_PATH = ROOT / "examples" / "rear_tree_branch_child_partition_family_001.json"
REBIND_CONTRACT_PATH = ROOT / "examples" / "rear_tree_branch_child_partition_rigging_consumer_rebind_003.json"

STATE = "PASS_NATURE_BRANCH_PARTITION_CURRENT_RIGGING_CONSUMER_REBIND"
DECISION = "PASS_EXACT_CURRENT_RIGGING_CONSUMER_REBIND__FIVE_SELECTION_IDENTITIES_MATCH__NO_RIGGING_MOTION_OR_DOWNSTREAM_ADOPTION"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def blob_at(root: Path, path: str) -> str:
    row = git(root, "ls-tree", "HEAD", "--", path)
    if not row:
        raise RuntimeError(f"missing exact donor path: {path}")
    fields = row.split()
    if len(fields) < 3 or fields[1] != "blob":
        raise RuntimeError(f"unexpected git tree row for {path}: {row}")
    return fields[2]


def rejection(label: str, action) -> dict:
    try:
        action()
    except Exception as exc:
        return {"label": label, "rejected": True, "error": f"{type(exc).__name__}: {exc}"}
    raise AssertionError(f"negative control unexpectedly passed: {label}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--rigging-root", type=Path, required=True)
    parser.add_argument("--rigging-family-evidence", type=Path, required=True)
    parser.add_argument("--shared-driver-evidence", type=Path, required=True)
    args = parser.parse_args()

    source = load_json(SOURCE_PATH)
    family_contract = load_json(FAMILY_CONTRACT_PATH)
    contract = load_json(REBIND_CONTRACT_PATH)
    rigging_family = load_json(args.rigging_family_evidence)
    shared_driver = load_json(args.shared_driver_evidence)

    mesh = build_mesh(source)
    procedural_family = assemble_family(source, mesh, family_contract)

    rigging_root = args.rigging_root.resolve()
    observed_rigging_head = git(rigging_root, "rev-parse", "HEAD")
    family_module_path = contract["rigging_consumer"]["family_module_path"]
    shared_module_path = contract["rigging_consumer"]["shared_driver_module_path"]
    observed_family_blob = blob_at(rigging_root, family_module_path)
    observed_shared_blob = blob_at(rigging_root, shared_module_path)
    procedural_head = git(ROOT, "rev-parse", "HEAD")

    result = assemble_rigging_consumer_rebind(
        procedural_family,
        rigging_family,
        shared_driver,
        contract,
        observed_rigging_head=observed_rigging_head,
        observed_family_module_blob=observed_family_blob,
        observed_shared_driver_module_blob=observed_shared_blob,
    )

    reverse_family = assemble_family(
        source,
        mesh,
        family_contract,
        branch_ids=list(reversed(family_contract["branch_ids"])),
    )
    if reverse_family["family_digest"] != procedural_family["family_digest"]:
        raise RuntimeError("reversed branch request changed canonical Procedural family identity")

    controls = []
    drift_contract = copy.deepcopy(contract)
    drift_contract["rigging_consumer"]["ref"] = "0" * 40
    controls.append(rejection(
        "rigging-head-drift",
        lambda: assemble_rigging_consumer_rebind(
            procedural_family, rigging_family, shared_driver, drift_contract,
            observed_rigging_head=observed_rigging_head,
            observed_family_module_blob=observed_family_blob,
            observed_shared_driver_module_blob=observed_shared_blob,
        ),
    ))
    controls.append(rejection(
        "rigging-family-module-blob-drift",
        lambda: assemble_rigging_consumer_rebind(
            procedural_family, rigging_family, shared_driver, contract,
            observed_rigging_head=observed_rigging_head,
            observed_family_module_blob="0" * 40,
            observed_shared_driver_module_blob=observed_shared_blob,
        ),
    ))
    controls.append(rejection(
        "rigging-shared-driver-module-blob-drift",
        lambda: assemble_rigging_consumer_rebind(
            procedural_family, rigging_family, shared_driver, contract,
            observed_rigging_head=observed_rigging_head,
            observed_family_module_blob=observed_family_blob,
            observed_shared_driver_module_blob="0" * 40,
        ),
    ))

    bad_family = copy.deepcopy(procedural_family)
    bad_family["family_digest"] = "0" * 64
    controls.append(rejection(
        "procedural-family-digest-drift",
        lambda: assemble_rigging_consumer_rebind(
            bad_family, rigging_family, shared_driver, contract,
            observed_rigging_head=observed_rigging_head,
            observed_family_module_blob=observed_family_blob,
            observed_shared_driver_module_blob=observed_shared_blob,
        ),
    ))

    bad_rig_regions = copy.deepcopy(rigging_family)
    bad_rig_regions["rigging_family"]["probes"][0]["selected_regions"][0] = "branch:wrong:0"
    controls.append(rejection(
        "rigging-region-selection-drift",
        lambda: assemble_rigging_consumer_rebind(
            procedural_family, bad_rig_regions, shared_driver, contract,
            observed_rigging_head=observed_rigging_head,
            observed_family_module_blob=observed_family_blob,
            observed_shared_driver_module_blob=observed_shared_blob,
        ),
    ))

    bad_rig_vertices = copy.deepcopy(rigging_family)
    bad_rig_vertices["rigging_family"]["probes"][0]["selected_vertex_indices"][0] = 389
    controls.append(rejection(
        "rigging-vertex-selection-drift",
        lambda: assemble_rigging_consumer_rebind(
            procedural_family, bad_rig_vertices, shared_driver, contract,
            observed_rigging_head=observed_rigging_head,
            observed_family_module_blob=observed_family_blob,
            observed_shared_driver_module_blob=observed_shared_blob,
        ),
    ))

    bad_shared = copy.deepcopy(shared_driver)
    bad_shared["continuous_mapping"]["rigging_child_partition_changed"] = True
    controls.append(rejection(
        "shared-driver-partition-change",
        lambda: assemble_rigging_consumer_rebind(
            procedural_family, rigging_family, bad_shared, contract,
            observed_rigging_head=observed_rigging_head,
            observed_family_module_blob=observed_family_blob,
            observed_shared_driver_module_blob=observed_shared_blob,
        ),
    ))

    for label, field in (
        ("rigging-authority-expansion", "rigging_authority_transferred"),
        ("automatic-downstream-adoption", "automatic_downstream_adoption"),
        ("animation-vfx-motion-adoption", "animation_or_vfx_motion_adopted"),
    ):
        bad_contract = copy.deepcopy(contract)
        bad_contract[field] = True
        controls.append(rejection(
            label,
            lambda bad_contract=bad_contract: assemble_rigging_consumer_rebind(
                procedural_family, rigging_family, shared_driver, bad_contract,
                observed_rigging_head=observed_rigging_head,
                observed_family_module_blob=observed_family_blob,
                observed_shared_driver_module_blob=observed_shared_blob,
            ),
        ))

    summary = {
        "state": STATE,
        "decision": DECISION,
        "procedural_head": procedural_head,
        "rigging_consumer_head": observed_rigging_head,
        "procedural_family_digest": procedural_family["family_digest"],
        "reverse_order_family_digest": reverse_family["family_digest"],
        "consumer_rebind_digest": result["consumer_rebind_digest"],
        "branch_count": result["branch_count"],
        "distinct_partition_digest_count": len({row["partition_digest"] for row in result["comparisons"]}),
        "distinct_vertex_index_digest_count": len({row["vertex_index_digest"] for row in result["comparisons"]}),
        "comparisons": result["comparisons"],
        "all_exact_selection_identities_match": result["all_exact_selection_identities_match"],
        "pairwise_vertex_disjoint": result["pairwise_vertex_disjoint"],
        "rigging_shared_driver_observed_not_adopted": result["rigging_shared_driver_observed_not_adopted"],
        "failure_controls": controls,
        "all_failure_controls_rejected": all(row["rejected"] for row in controls),
        "truth_boundary": {
            "source_authorized": False,
            "rigging_authority_transferred": False,
            "deformation_tested_by_procedural": False,
            "animation_or_vfx_motion_adopted": False,
            "automatic_downstream_adoption": False,
            "continuous_simultaneous_motion_claimed": False,
            "art_or_qa_acceptance_claimed": False,
            "canon_or_production_readiness_claimed": False
        }
    }

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "contract.json").write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "rigging_family_evidence.json").write_text(json.dumps(rigging_family, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "shared_driver_evidence.json").write_text(json.dumps(shared_driver, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "procedural_head.txt").write_text(procedural_head + "\n", encoding="utf-8")
    (out / "rigging_head.txt").write_text(observed_rigging_head + "\n", encoding="utf-8")
    print(json.dumps({
        "state": STATE,
        "branch_count": result["branch_count"],
        "family_digest": procedural_family["family_digest"],
        "consumer_rebind_digest": result["consumer_rebind_digest"],
        "failure_controls": len(controls),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

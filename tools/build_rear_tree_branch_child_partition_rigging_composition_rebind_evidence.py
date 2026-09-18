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
from axm_nature_design.branch_partition_rigging_composition_rebind import (
    assemble_rigging_composition_rebind,
)
from axm_nature_design.organic_form import build_mesh

SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"
FAMILY_CONTRACT_PATH = ROOT / "examples" / "rear_tree_branch_child_partition_family_001.json"
REBIND_CONTRACT_PATH = ROOT / "examples" / "rear_tree_branch_child_partition_rigging_composition_rebind_004.json"

STATE = "PASS_NATURE_BRANCH_PARTITION_CURRENT_RIGGING_COMPOSITION_REBIND"
DECISION = "PASS_EXACT_CURRENT_RIGGING_COMPOSITION_REBIND__FIVE_SELECTION_IDENTITIES_PRESERVED__NO_KINEMATIC_OR_MOTION_ADOPTION"


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
    parser.add_argument("--polarity-evidence", type=Path, required=True)
    parser.add_argument("--composition-evidence", type=Path, required=True)
    args = parser.parse_args()

    source = load_json(SOURCE_PATH)
    family_contract = load_json(FAMILY_CONTRACT_PATH)
    contract = load_json(REBIND_CONTRACT_PATH)
    rigging_family = load_json(args.rigging_family_evidence)
    polarity = load_json(args.polarity_evidence)
    composition = load_json(args.composition_evidence)

    mesh = build_mesh(source)
    procedural_family = assemble_family(source, mesh, family_contract)
    reverse_family = assemble_family(
        source,
        mesh,
        family_contract,
        branch_ids=list(reversed(family_contract["branch_ids"])),
    )
    if reverse_family["family_digest"] != procedural_family["family_digest"]:
        raise RuntimeError("reversed branch request changed canonical Procedural family identity")

    rigging_root = args.rigging_root.resolve()
    observed_rigging_head = git(rigging_root, "rev-parse", "HEAD")
    consumer = contract["rigging_consumer"]
    observed_family_blob = blob_at(rigging_root, consumer["family_module_path"])
    observed_polarity_blob = blob_at(rigging_root, consumer["polarity_module_path"])
    observed_composition_blob = blob_at(rigging_root, consumer["composition_module_path"])
    observed_composition_contract_blob = blob_at(rigging_root, consumer["composition_contract_path"])
    procedural_head = git(ROOT, "rev-parse", "HEAD")

    def assemble(
        family=procedural_family,
        rig=rigging_family,
        pol=polarity,
        comp=composition,
        con=contract,
        head=observed_rigging_head,
        family_blob=observed_family_blob,
        polarity_blob=observed_polarity_blob,
        composition_blob=observed_composition_blob,
        composition_contract_blob=observed_composition_contract_blob,
    ):
        return assemble_rigging_composition_rebind(
            family,
            rig,
            pol,
            comp,
            con,
            observed_rigging_head=head,
            observed_family_module_blob=family_blob,
            observed_polarity_module_blob=polarity_blob,
            observed_composition_module_blob=composition_blob,
            observed_composition_contract_blob=composition_contract_blob,
        )

    result = assemble()

    controls = []
    controls.append(rejection("rigging-head-drift", lambda: assemble(head="0" * 40)))
    controls.append(rejection("rigging-family-module-blob-drift", lambda: assemble(family_blob="0" * 40)))
    controls.append(rejection("rigging-polarity-module-blob-drift", lambda: assemble(polarity_blob="0" * 40)))
    controls.append(rejection("rigging-composition-module-blob-drift", lambda: assemble(composition_blob="0" * 40)))
    controls.append(rejection("rigging-composition-contract-blob-drift", lambda: assemble(composition_contract_blob="0" * 40)))

    bad_family = copy.deepcopy(procedural_family)
    bad_family["family_digest"] = "0" * 64
    controls.append(rejection("procedural-family-digest-drift", lambda: assemble(family=bad_family)))

    bad_regions = copy.deepcopy(rigging_family)
    bad_regions["rigging_family"]["probes"][0]["selected_regions"][0] = "branch:wrong:0"
    controls.append(rejection("rigging-region-selection-drift", lambda: assemble(rig=bad_regions)))

    bad_vertices = copy.deepcopy(rigging_family)
    bad_vertices["rigging_family"]["probes"][0]["selected_vertex_indices"][0] = 389
    controls.append(rejection("rigging-vertex-selection-drift", lambda: assemble(rig=bad_vertices)))

    bad_support = copy.deepcopy(composition)
    branch_id = contract["branch_ids"][0]
    bad_support["composition"]["per_branch_selected_vertices"][branch_id] -= 1
    controls.append(rejection("rigging-composition-support-drift", lambda: assemble(comp=bad_support)))

    bad_union = copy.deepcopy(composition)
    bad_union["composition"]["selected_vertex_union"] -= 1
    controls.append(rejection("rigging-composition-union-drift", lambda: assemble(comp=bad_union)))

    bad_timing = copy.deepcopy(composition)
    bad_timing["continuous_parameter_certificate"]["timing_or_playback_defined"] = True
    controls.append(rejection("rigging-composition-timing-promotion", lambda: assemble(comp=bad_timing)))

    for label, field in (
        ("shared-driver-semantics-adoption", "shared_driver_semantics_adopted"),
        ("animation-vfx-motion-adoption", "animation_or_vfx_motion_adopted"),
        ("continuous-collision-promotion", "continuous_collision_claimed"),
        ("automatic-downstream-adoption", "automatic_downstream_adoption"),
    ):
        bad_contract = copy.deepcopy(contract)
        bad_contract[field] = True
        controls.append(rejection(label, lambda bad_contract=bad_contract: assemble(con=bad_contract)))

    summary = {
        "state": STATE,
        "decision": DECISION,
        "procedural_head": procedural_head,
        "rigging_consumer_head": observed_rigging_head,
        "predecessor_consumer_rebind_head": contract["procedural_provider"]["predecessor_consumer_rebind_head"],
        "predecessor_consumer_rebind_digest": contract["procedural_provider"]["predecessor_consumer_rebind_digest"],
        "procedural_family_digest": procedural_family["family_digest"],
        "reverse_order_family_digest": reverse_family["family_digest"],
        "composition_rebind_digest": result["composition_rebind_digest"],
        "branch_count": result["branch_count"],
        "distinct_partition_digest_count": len({row["partition_digest"] for row in result["comparisons"]}),
        "distinct_vertex_index_digest_count": len({row["vertex_index_digest"] for row in result["comparisons"]}),
        "comparisons": result["comparisons"],
        "all_exact_selection_identities_match": result["all_exact_selection_identities_match"],
        "pairwise_vertex_disjoint": result["pairwise_vertex_disjoint"],
        "rigging_composition_observed_not_adopted": result["rigging_composition_observed_not_adopted"],
        "rigging_composition_support": {
            "selected_vertex_union": composition["composition"]["selected_vertex_union"],
            "globally_fixed_vertices": composition["composition"]["globally_fixed_vertices"],
            "per_branch_selected_vertices": composition["composition"]["per_branch_selected_vertices"],
        },
        "failure_controls": controls,
        "all_failure_controls_rejected": all(row["rejected"] for row in controls),
        "truth_boundary": {
            "source_authorized": False,
            "rigging_authority_transferred": False,
            "deformation_tested_by_procedural": False,
            "shared_driver_semantics_adopted": False,
            "continuous_kinematic_parameter_claimed_by_procedural": False,
            "animation_or_vfx_motion_adopted": False,
            "continuous_collision_claimed": False,
            "technical_art_or_runtime_adoption": False,
            "art_or_qa_acceptance_claimed": False,
            "canon_or_production_readiness_claimed": False
        }
    }

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "contract.json").write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "rigging_family_evidence.json").write_text(json.dumps(rigging_family, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "polarity_evidence.json").write_text(json.dumps(polarity, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "composition_evidence.json").write_text(json.dumps(composition, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "procedural_head.txt").write_text(procedural_head + "\n", encoding="utf-8")
    (out / "rigging_head.txt").write_text(observed_rigging_head + "\n", encoding="utf-8")
    print(json.dumps({
        "state": STATE,
        "branch_count": result["branch_count"],
        "family_digest": procedural_family["family_digest"],
        "composition_rebind_digest": result["composition_rebind_digest"],
        "failure_controls": len(controls),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from axm_nature_design.branch_partition_family import assemble_family, digest
from axm_nature_design.branch_partition_geometry_rebind import (
    assemble_geometry_rebind,
    validate_rebind_contract,
)

PREDECESSOR_CONTRACT_PATH = ROOT / "examples" / "rear_tree_branch_child_partition_family_001.json"
REBIND_CONTRACT_PATH = ROOT / "examples" / "rear_tree_branch_child_partition_geometry_rebind_002.json"
PASS_STATE = "PASS_NATURE_PRIMARY_BRANCH_CHILD_PARTITION_GEOMETRY_RECEIVER_REBIND"
DECISION = "PASS_EXACT_GEOMETRY_RECEIVER_PARTITION_REBIND__SELECTION_IDENTITIES_PRESERVED__NO_RIGGING_OR_DOWNSTREAM_ADOPTION"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_head(root: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def git_blob(root: Path, relpath: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", f"HEAD:{relpath}"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def load_exact_builder(root: Path, relpath: str, module_name: str):
    path = root / relpath
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load exact builder: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_donor(root: Path, provider: dict, *, label: str):
    observed_head = git_head(root)
    if observed_head != provider["ref"]:
        raise ValueError(f"{label} head drift: {observed_head} != {provider['ref']}")
    if git_blob(root, provider["source_path"]) != provider["source_blob"]:
        raise ValueError(f"{label} source blob drift")
    if git_blob(root, provider["builder_path"]) != provider["builder_blob"]:
        raise ValueError(f"{label} builder blob drift")
    source = load_json(root / provider["source_path"])
    builder = load_exact_builder(root, provider["builder_path"], f"axm_exact_{label.replace('-', '_')}_builder")
    observed_source_digest = builder.digest(source)
    if observed_source_digest != provider["source_digest"]:
        raise ValueError(f"{label} source canonical digest drift")
    mesh = builder.build_mesh(source)
    observed_mesh_digest = builder.digest(mesh)
    if observed_mesh_digest != provider["mesh_digest"]:
        raise ValueError(f"{label} receiver mesh digest drift")
    return source, mesh, builder


def validate_predecessor_contract_blob(contract: dict) -> None:
    expected = contract["predecessor_family_contract"]
    observed = git_blob(ROOT, expected["path"])
    if observed != expected["blob"]:
        raise ValueError(f"predecessor family contract blob drift: {observed} != {expected['blob']}")


def check_rigging_witness(result: dict, contract: dict) -> None:
    witness = contract["rigging_receiver_witness"]
    row = next(item for item in result["comparisons"] if item["branch_id"] == witness["branch_id"])
    if row["vertex_count"] != int(witness["selected_vertices"]):
        raise ValueError("Rigging witness selected-vertex count drift")
    if row["triangle_count"] != int(witness["selected_triangles"]):
        raise ValueError("Rigging witness selected-triangle count drift")
    if row["fixed_vertex_count"] != int(witness["fixed_vertices"]):
        raise ValueError("Rigging witness fixed-vertex count drift")
    if witness["geometry_receiver_head"] != contract["geometry_receiver"]["ref"]:
        raise ValueError("Rigging witness Geometry receiver head drift")


def expect_rejection(label: str, action) -> dict:
    try:
        action()
    except Exception as exc:
        return {"label": label, "rejected": True, "error": f"{type(exc).__name__}: {exc}"}
    raise AssertionError(f"negative control unexpectedly passed: {label}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--organic-root", type=Path, required=True)
    parser.add_argument("--geometry-root", type=Path, required=True)
    args = parser.parse_args()

    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    organic_root = args.organic_root.resolve()
    geometry_root = args.geometry_root.resolve()

    predecessor_contract = load_json(PREDECESSOR_CONTRACT_PATH)
    contract = load_json(REBIND_CONTRACT_PATH)
    validate_rebind_contract(contract, predecessor_contract)
    validate_predecessor_contract_blob(contract)

    organic_source, historical_mesh, organic_builder = validate_donor(
        organic_root, contract["organic_provider"], label="organic"
    )
    geometry_source, migrated_mesh, geometry_builder = validate_donor(
        geometry_root, contract["geometry_receiver"], label="geometry"
    )
    if organic_source != geometry_source:
        raise RuntimeError("Organic and Geometry donor source payloads are not exact")
    if organic_builder.digest(organic_source) != geometry_builder.digest(geometry_source):
        raise RuntimeError("Organic and Geometry donor source digest implementations disagree")

    result = assemble_geometry_rebind(
        organic_source,
        historical_mesh,
        migrated_mesh,
        predecessor_contract,
        contract,
    )
    check_rigging_witness(result, contract)

    reverse_family = assemble_family(
        organic_source,
        migrated_mesh,
        predecessor_contract,
        list(reversed(contract["branch_ids"])),
    )
    if reverse_family["family_digest"] != result["geometry_receiver_family_digest"]:
        raise RuntimeError("Geometry-rebound family digest depends on branch declaration order")

    expected_mesh = contract["expected_generated_mesh"]
    if len(historical_mesh["vertices"]) != int(expected_mesh["vertices"]):
        raise RuntimeError("historical receiver vertex-count drift")
    if len(migrated_mesh["vertices"]) != int(expected_mesh["vertices"]):
        raise RuntimeError("Geometry receiver vertex-count drift")
    if len(historical_mesh["triangles"]) != int(expected_mesh["triangles"]):
        raise RuntimeError("historical receiver triangle-count drift")
    if len(migrated_mesh["triangles"]) != int(expected_mesh["triangles"]):
        raise RuntimeError("Geometry receiver triangle-count drift")

    expected_partition = contract["expected_partition"]
    for row in result["comparisons"]:
        if row["vertex_count"] != int(expected_partition["vertices"]):
            raise RuntimeError(f"partition vertex-count drift: {row['branch_id']}")
        if row["triangle_count"] != int(expected_partition["triangles"]):
            raise RuntimeError(f"partition triangle-count drift: {row['branch_id']}")
        if row["fixed_vertex_count"] != int(expected_partition["fixed_vertices"]):
            raise RuntimeError(f"partition fixed-vertex-count drift: {row['branch_id']}")

    controls = []

    predecessor_blob = copy.deepcopy(contract)
    predecessor_blob["predecessor_family_contract"]["blob"] = "0" * 40
    controls.append(
        expect_rejection(
            "predecessor-family-contract-blob-drift",
            lambda: validate_predecessor_contract_blob(predecessor_blob),
        )
    )

    organic_head = copy.deepcopy(contract)
    organic_head["organic_provider"]["ref"] = "0" * 40
    controls.append(
        expect_rejection(
            "organic-owner-head-drift",
            lambda: validate_donor(organic_root, organic_head["organic_provider"], label="organic"),
        )
    )

    geometry_head = copy.deepcopy(contract)
    geometry_head["geometry_receiver"]["ref"] = "0" * 40
    controls.append(
        expect_rejection(
            "geometry-receiver-head-drift",
            lambda: validate_donor(geometry_root, geometry_head["geometry_receiver"], label="geometry"),
        )
    )

    geometry_blob = copy.deepcopy(contract)
    geometry_blob["geometry_receiver"]["builder_blob"] = "0" * 40
    controls.append(
        expect_rejection(
            "geometry-builder-blob-drift",
            lambda: validate_donor(geometry_root, geometry_blob["geometry_receiver"], label="geometry"),
        )
    )

    historical_digest = copy.deepcopy(contract)
    historical_digest["organic_provider"]["mesh_digest"] = "0" * 64
    controls.append(
        expect_rejection(
            "historical-receiver-mesh-digest-drift",
            lambda: assemble_geometry_rebind(
                organic_source, historical_mesh, migrated_mesh, predecessor_contract, historical_digest
            ),
        )
    )

    migrated_digest = copy.deepcopy(contract)
    migrated_digest["geometry_receiver"]["mesh_digest"] = "0" * 64
    controls.append(
        expect_rejection(
            "geometry-receiver-mesh-digest-drift",
            lambda: assemble_geometry_rebind(
                organic_source, historical_mesh, migrated_mesh, predecessor_contract, migrated_digest
            ),
        )
    )

    adoption = copy.deepcopy(contract)
    adoption["automatic_rigging_adoption"] = True
    controls.append(
        expect_rejection(
            "automatic-rigging-adoption",
            lambda: validate_rebind_contract(adoption, predecessor_contract),
        )
    )

    authority = copy.deepcopy(contract)
    authority["geometry_authority_transferred"] = True
    controls.append(
        expect_rejection(
            "geometry-authority-transfer",
            lambda: validate_rebind_contract(authority, predecessor_contract),
        )
    )

    region_drift_mesh = copy.deepcopy(migrated_mesh)
    region_drift_mesh["regions"][0]["id"] = f"{region_drift_mesh['regions'][0]['id']}-drift"
    region_drift_contract = copy.deepcopy(contract)
    region_drift_contract["geometry_receiver"]["mesh_digest"] = digest(region_drift_mesh)
    controls.append(
        expect_rejection(
            "generated-region-identity-drift",
            lambda: assemble_geometry_rebind(
                organic_source,
                historical_mesh,
                region_drift_mesh,
                predecessor_contract,
                region_drift_contract,
            ),
        )
    )

    membership_drift_mesh = copy.deepcopy(migrated_mesh)
    first = membership_drift_mesh["triangles"][0]
    first[0] = int((first[0] + 1) % len(membership_drift_mesh["vertices"]))
    membership_drift_contract = copy.deepcopy(contract)
    membership_drift_contract["geometry_receiver"]["mesh_digest"] = digest(membership_drift_mesh)
    controls.append(
        expect_rejection(
            "triangle-membership-drift",
            lambda: assemble_geometry_rebind(
                organic_source,
                historical_mesh,
                membership_drift_mesh,
                predecessor_contract,
                membership_drift_contract,
            ),
        )
    )

    witness_drift = copy.deepcopy(contract)
    witness_drift["rigging_receiver_witness"]["selected_vertices"] = 51
    controls.append(
        expect_rejection(
            "rigging-witness-count-drift",
            lambda: check_rigging_witness(result, witness_drift),
        )
    )

    summary = {
        "schema": "axm.nature-branch-child-partition-geometry-rebind-evidence/v0.1",
        "state": PASS_STATE,
        "decision": DECISION,
        "procedural_head": git_head(ROOT),
        "predecessor_family_contract_blob": contract["predecessor_family_contract"]["blob"],
        "predecessor_family_digest": contract["predecessor_family_contract"]["family_digest"],
        "organic_owner_head": contract["organic_provider"]["ref"],
        "organic_source_blob": contract["organic_provider"]["source_blob"],
        "organic_builder_blob": contract["organic_provider"]["builder_blob"],
        "historical_receiver_mesh_digest": result["historical_receiver_mesh_digest"],
        "geometry_receiver_head": contract["geometry_receiver"]["ref"],
        "geometry_source_blob": contract["geometry_receiver"]["source_blob"],
        "geometry_builder_blob": contract["geometry_receiver"]["builder_blob"],
        "geometry_receiver_mesh_digest": result["geometry_receiver_mesh_digest"],
        "receiver_mesh_identity_changed": result["receiver_mesh_identity_changed"],
        "vertex_positions_preserved": result["vertex_positions_preserved"],
        "triangle_membership_preserved": result["triangle_membership_preserved"],
        "generated_regions_preserved": result["generated_regions_preserved"],
        "ordered_triangle_changes": result["ordered_triangle_changes"],
        "branch_count": result["branch_count"],
        "distinct_partition_digest_count": len({row["partition_digest"] for row in result["comparisons"]}),
        "distinct_vertex_index_digest_count": len({row["vertex_index_digest"] for row in result["comparisons"]}),
        "comparisons": result["comparisons"],
        "historical_family_digest": result["historical_family_digest"],
        "geometry_receiver_family_digest": result["geometry_receiver_family_digest"],
        "reverse_order_geometry_receiver_family_digest": reverse_family["family_digest"],
        "selection_family_identity_preserved": result["selection_family_identity_preserved"],
        "rebind_digest": result["rebind_digest"],
        "rigging_receiver_witness": contract["rigging_receiver_witness"],
        "failure_controls": controls,
        "all_failure_controls_rejected": all(row["rejected"] for row in controls),
        "truth_boundary": contract["truth_boundary"],
    }
    write_json(out / "summary.json", summary)
    write_json(out / "rebind.json", result)
    write_json(out / "contract.json", contract)
    write_json(out / "predecessor-family-contract.json", predecessor_contract)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

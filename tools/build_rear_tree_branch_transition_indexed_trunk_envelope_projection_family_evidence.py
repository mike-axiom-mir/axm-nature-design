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

from axm_nature_design.branch_transition_frame_family import assemble_transition_frame_family
from axm_nature_design.trunk_envelope_projection_family import assemble_trunk_envelope_projection_family
from axm_nature_design.indexed_trunk_envelope_projection_family import (
    assemble_indexed_trunk_envelope_projection_family,
    project_points_to_regular_tapered_shell,
    validate_contract,
)

CONTRACT_PATH = ROOT / "examples" / "rear_tree_branch_transition_indexed_trunk_envelope_projection_family_001.json"
PREDECESSOR_CONTRACT_PATH = ROOT / "examples" / "rear_tree_branch_transition_trunk_envelope_projection_family_001.json"
FRAME_CONTRACT_PATH = ROOT / "examples" / "rear_tree_branch_transition_frame_family_001.json"
STATE = "PASS_BOUNDED_INDEXED_TRUNK_ENVELOPE_PROJECTION_FAMILY"
DECISION = (
    "PASS_TOPOLOGY_FREE_REGULAR_INDEXED_TRUNK_ENVELOPE_PROJECTOR__"
    "FIVE_PREDECESSOR_BACKED_OUTPUTS__NORTH_LOW_GEOMETRY_INDEXED_REFERENCE_MATCHES__"
    "NO_TRIANGLE_MEMBERSHIP_RING_TOPOLOGY_TRUNK_CUT_WELD_RIGGING_OR_DOWNSTREAM_ADOPTION"
)


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


def validate_checkout(root: Path, head: str, blobs: dict[str, str]) -> None:
    actual_head = git_head(root)
    if actual_head != head:
        raise ValueError(f"checkout head drift: expected {head}, got {actual_head}")
    for path, expected_blob in blobs.items():
        if git_blob(root, path) != expected_blob:
            raise ValueError(f"checkout blob drift: {path}")


def build_owner_frame_report(owner_root: Path, predecessor_contract: dict) -> tuple[dict, dict]:
    owner = predecessor_contract["organic_owner"]
    validate_checkout(
        owner_root,
        owner["head"],
        {
            owner["frame_observer_path"]: owner["frame_observer_blob"],
            owner["transition_observer_path"]: owner["transition_observer_blob"],
            owner["source_path"]: owner["source_blob"],
        },
    )
    script = """
import json, sys
from pathlib import Path
root = Path(sys.argv[1]).resolve(); source_path = sys.argv[2]
sys.path.insert(0, str(root / 'src'))
from axm_nature_design.rear_tree_transition_exit_frames import evaluate
source = json.loads((root / source_path).read_text(encoding='utf-8'))
print(json.dumps({'source': source, 'frames': evaluate(source)}, sort_keys=True))
"""
    result = subprocess.run(
        [sys.executable, "-c", script, str(owner_root), owner["source_path"]],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    return payload["source"], payload["frames"]


def validate_predecessor_files(contract: dict) -> None:
    predecessor = contract["predecessor_projection"]
    expected = {
        predecessor["module_path"]: predecessor["module_blob"],
        predecessor["contract_path"]: predecessor["contract_blob"],
        predecessor["frame_contract_path"]: predecessor["frame_contract_blob"],
    }
    for path, blob in expected.items():
        if git_blob(ROOT, path) != blob:
            raise ValueError(f"predecessor Procedural file drift: {path}")


def build_geometry_reference(
    geometry_root: Path,
    contract: dict,
    source_path: str,
    source_blob: str,
) -> dict:
    donor = contract["geometry_reference"]
    validate_checkout(
        geometry_root,
        donor["head"],
        {donor["module_path"]: donor["module_blob"], source_path: source_blob},
    )
    script = """
import json, sys
from pathlib import Path
root = Path(sys.argv[1]).resolve(); source_path = sys.argv[2]
sys.path.insert(0, str(root / 'src'))
from axm_nature_design.rear_tree_geometry_north_low_indexed_surface_rebind import build_candidate
source = json.loads((root / source_path).read_text(encoding='utf-8'))
candidate = build_candidate(source)
stub = candidate['branch_stub']
indices = list(stub['transition_ring_vertex_indices'])
points = [list(stub['vertices'][index]) for index in indices]
print(json.dumps({
    'segment_id': candidate['analytic_predecessor']['trunk_segment_id'],
    'input_points': points,
    'indexed_samples': candidate['indexed_samples'],
}, sort_keys=True))
"""
    result = subprocess.run(
        [sys.executable, "-c", script, str(geometry_root), source_path],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def max_numeric_delta(a, b) -> float:
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            raise ValueError("vector length drift during Geometry compatibility comparison")
        return max((max_numeric_delta(x, y) for x, y in zip(a, b)), default=0.0)
    return abs(float(a) - float(b))


def compare_geometry_projection_rows(expected: list[dict], actual: list[dict]) -> dict:
    if len(expected) != len(actual):
        raise ValueError("Geometry indexed reference sample count drift")
    scalar_fields = (
        "segment_t",
        "theta_rad",
        "side_edge_lambda",
        "local_radius_m",
        "indexed_radial_distance_m",
    )
    maximum = 0.0
    for index, (geometry_row, procedural_row) in enumerate(zip(expected, actual)):
        if int(geometry_row["side_cell"]) != int(procedural_row["side_cell"]):
            raise ValueError(f"Geometry side-cell identity drift at sample {index}")
        for field in scalar_fields:
            maximum = max(
                maximum,
                abs(float(geometry_row[field]) - float(procedural_row[field])),
            )
        maximum = max(
            maximum,
            max_numeric_delta(
                geometry_row["surface_point_m"],
                procedural_row["surface_point_m"],
            ),
        )
        if procedural_row["surface_edge_residual_m"] > 1e-10:
            raise ValueError(f"Procedural indexed-side residual too large at Geometry sample {index}")
        if procedural_row["axial_coordinate_residual_m"] > 1e-10:
            raise ValueError(f"Procedural axial residual too large at Geometry sample {index}")
    if maximum > 1e-10:
        raise ValueError(f"Procedural indexed projector no longer matches Geometry reference: {maximum}")
    return {
        "sample_count": len(expected),
        "maximum_numeric_delta": maximum,
        "side_cells": sorted({int(row["side_cell"]) for row in actual}),
        "match_within_tolerance": True,
    }


def expect_rejection(label: str, action) -> dict:
    try:
        action()
    except Exception as exc:
        return {"label": label, "rejected": True, "error": f"{type(exc).__name__}: {exc}"}
    raise AssertionError(f"negative control unexpectedly passed: {label}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--owner-organic-root", type=Path, required=True)
    parser.add_argument("--geometry-reference-root", type=Path, required=True)
    args = parser.parse_args()

    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    contract = load_json(CONTRACT_PATH)
    validate_contract(contract)
    validate_predecessor_files(contract)

    predecessor_contract = load_json(PREDECESSOR_CONTRACT_PATH)
    frame_contract = load_json(FRAME_CONTRACT_PATH)
    source, owner_frame_report = build_owner_frame_report(
        args.owner_organic_root.resolve(), predecessor_contract
    )
    frame_family = assemble_transition_frame_family(owner_frame_report, frame_contract)
    smooth_family = assemble_trunk_envelope_projection_family(
        source, owner_frame_report, frame_family, predecessor_contract
    )
    if smooth_family["family_digest"] != contract["predecessor_projection_family_digest"]:
        raise RuntimeError("predecessor smooth trunk-envelope family digest drift")

    family = assemble_indexed_trunk_envelope_projection_family(source, smooth_family, contract)
    reverse_predecessor = copy.deepcopy(smooth_family)
    reverse_predecessor["outputs"] = list(reversed(reverse_predecessor["outputs"]))
    reverse_contract = copy.deepcopy(contract)
    reverse_contract["authorized_branch_ids"] = list(reversed(reverse_contract["authorized_branch_ids"]))
    reverse_family = assemble_indexed_trunk_envelope_projection_family(
        source, reverse_predecessor, reverse_contract
    )
    if family["family_digest"] != reverse_family["family_digest"]:
        raise RuntimeError("indexed projection family identity depends on branch ordering")

    source_path = predecessor_contract["organic_owner"]["source_path"]
    source_blob = predecessor_contract["organic_owner"]["source_blob"]
    geometry = build_geometry_reference(
        args.geometry_reference_root.resolve(), contract, source_path, source_blob
    )
    procedural_geometry_reference = project_points_to_regular_tapered_shell(
        source,
        geometry["segment_id"],
        geometry["input_points"],
        side_count=contract["receiver_side_count"],
        phase_rad=contract["receiver_phase_rad"],
    )
    compatibility = compare_geometry_projection_rows(
        geometry["indexed_samples"], procedural_geometry_reference
    )

    outputs = family["outputs"]
    if len({row["projection_digest"] for row in outputs}) != 5:
        raise RuntimeError("five indexed projection outputs are not materially distinct")
    if any(len(row["samples"]) != 3 for row in outputs):
        raise RuntimeError("each branch must retain three indexed projection diagnostic samples")
    if family["maximum_analytic_to_indexed_surface_delta_m"] <= 1e-10:
        raise RuntimeError("indexed shell unexpectedly collapses to the smooth analytic envelope")

    controls = []
    bad_source = copy.deepcopy(contract)
    bad_source["organic_source_digest"] = "0" * 64
    controls.append(
        expect_rejection(
            "organic-source-digest-drift",
            lambda: assemble_indexed_trunk_envelope_projection_family(source, smooth_family, bad_source),
        )
    )
    bad_predecessor = copy.deepcopy(smooth_family)
    bad_predecessor["family_digest"] = "0" * 64
    controls.append(
        expect_rejection(
            "predecessor-projection-family-digest-drift",
            lambda: assemble_indexed_trunk_envelope_projection_family(source, bad_predecessor, contract),
        )
    )
    duplicate = copy.deepcopy(contract)
    duplicate["authorized_branch_ids"][-1] = duplicate["authorized_branch_ids"][0]
    controls.append(expect_rejection("duplicate-branch-declaration", lambda: validate_contract(duplicate)))
    wrong_sides = copy.deepcopy(contract)
    wrong_sides["receiver_side_count"] = 12
    controls.append(expect_rejection("receiver-side-count-drift", lambda: validate_contract(wrong_sides)))
    wrong_phase = copy.deepcopy(contract)
    wrong_phase["receiver_phase_rad"] = 0.1
    controls.append(expect_rejection("receiver-phase-drift", lambda: validate_contract(wrong_phase)))
    bad_geometry_head = copy.deepcopy(contract)
    bad_geometry_head["geometry_reference"]["head"] = "0" * 40
    controls.append(
        expect_rejection(
            "geometry-reference-head-drift",
            lambda: build_geometry_reference(
                args.geometry_reference_root.resolve(), bad_geometry_head, source_path, source_blob
            ),
        )
    )
    bad_geometry_blob = copy.deepcopy(contract)
    bad_geometry_blob["geometry_reference"]["module_blob"] = "0" * 40
    controls.append(
        expect_rejection(
            "geometry-reference-module-blob-drift",
            lambda: build_geometry_reference(
                args.geometry_reference_root.resolve(), bad_geometry_blob, source_path, source_blob
            ),
        )
    )
    centerline_source = {
        "trunk": [
            {"id": "a", "position": [0, 0, 0], "radius": 1},
            {"id": "b", "position": [0, 0, 1], "radius": 0.8},
        ]
    }
    controls.append(
        expect_rejection(
            "centerline-projection-degeneracy",
            lambda: project_points_to_regular_tapered_shell(
                centerline_source, "a->b", [[0, 0, 0.5]], side_count=10
            ),
        )
    )
    controls.append(
        expect_rejection(
            "outside-segment-projection",
            lambda: project_points_to_regular_tapered_shell(
                centerline_source, "a->b", [[1, 0, 1.5]], side_count=10
            ),
        )
    )
    for key in (
        "triangle_membership_authorized",
        "ring_topology_authorized",
        "indexed_trunk_cut_authorized",
        "connected_junction_authorized",
        "weld_or_remesh_authorized",
        "automatic_rigging_adoption",
        "automatic_runtime_adoption",
    ):
        bad = copy.deepcopy(contract)
        bad[key] = True
        controls.append(
            expect_rejection(
                f"authority-promotion-{key}",
                lambda bad=bad: validate_contract(bad),
            )
        )

    summary = {
        "schema": "axm.nature-branch-transition-indexed-trunk-envelope-projection-family-evidence/v0.1",
        "state": STATE,
        "decision": DECISION,
        "procedural_head": git_head(ROOT),
        "organic_owner_head": git_head(args.owner_organic_root.resolve()),
        "geometry_reference_head": git_head(args.geometry_reference_root.resolve()),
        "predecessor_projection_family_digest": smooth_family["family_digest"],
        "output_count": family["output_count"],
        "distinct_projection_digest_count": len({row["projection_digest"] for row in outputs}),
        "family_digest": family["family_digest"],
        "reverse_order_family_digest": reverse_family["family_digest"],
        "maximum_analytic_to_indexed_surface_delta_m": family[
            "maximum_analytic_to_indexed_surface_delta_m"
        ],
        "minimum_analytic_to_indexed_surface_delta_m": family[
            "minimum_analytic_to_indexed_surface_delta_m"
        ],
        "geometry_reference_compatibility": compatibility,
        "geometry_reference_segment_id": geometry["segment_id"],
        "geometry_reference_sample_count": len(geometry["indexed_samples"]),
        "failure_controls": controls,
        "all_failure_controls_rejected": all(row["rejected"] for row in controls),
        "truth_boundary": contract["truth_boundary"],
    }
    write_json(out / "summary.json", summary)
    write_json(out / "family.json", family)
    write_json(out / "contract.json", contract)
    write_json(out / "predecessor_smooth_family.json", smooth_family)
    write_json(out / "geometry_reference.json", geometry)
    write_json(out / "procedural_geometry_reference_projection.json", procedural_geometry_reference)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
from axm_nature_design.trunk_envelope_projection_family import (
    assemble_trunk_envelope_projection_family,
    project_points_to_tapered_trunk,
    validate_contract,
)

CONTRACT_PATH = ROOT / "examples" / "rear_tree_branch_transition_trunk_envelope_projection_family_001.json"
FRAME_CONTRACT_PATH = ROOT / "examples" / "rear_tree_branch_transition_frame_family_001.json"
STATE = "PASS_BOUNDED_TRANSITION_TRUNK_ENVELOPE_PROJECTION_FAMILY"
DECISION = (
    "PASS_TOPOLOGY_FREE_TAPERED_TRUNK_ENVELOPE_PROJECTOR__FIVE_OWNER_BACKED_OUTPUTS__"
    "NORTH_LOW_GEOMETRY_REFERENCE_MATCHES__NO_RING_TOPOLOGY_TRUNK_CUT_WELD_RIGGING_OR_DOWNSTREAM_ADOPTION"
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_head(root: Path) -> str:
    return subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()


def git_blob(root: Path, relpath: str) -> str:
    return subprocess.run(["git", "-C", str(root), "rev-parse", f"HEAD:{relpath}"], check=True, capture_output=True, text=True).stdout.strip()


def validate_checkout(root: Path, head: str, blobs: dict[str, str]) -> None:
    if git_head(root) != head:
        raise ValueError(f"checkout head drift: expected {head}, got {git_head(root)}")
    for path, expected_blob in blobs.items():
        if git_blob(root, path) != expected_blob:
            raise ValueError(f"checkout blob drift: {path}")


def build_owner_frame_report(owner_root: Path, contract: dict) -> tuple[dict, dict]:
    owner = contract["organic_owner"]
    validate_checkout(owner_root, owner["head"], {
        owner["frame_observer_path"]: owner["frame_observer_blob"],
        owner["transition_observer_path"]: owner["transition_observer_blob"],
        owner["source_path"]: owner["source_blob"],
    })
    script = r'''
import json, sys
from pathlib import Path
root = Path(sys.argv[1]).resolve(); source_path = sys.argv[2]
sys.path.insert(0, str(root / "src"))
from axm_nature_design.rear_tree_transition_exit_frames import evaluate
source = json.loads((root / source_path).read_text(encoding="utf-8"))
print(json.dumps({"source": source, "frames": evaluate(source)}, sort_keys=True))
'''
    result = subprocess.run([sys.executable, "-c", script, str(owner_root), owner["source_path"]], check=True, capture_output=True, text=True)
    payload = json.loads(result.stdout)
    return payload["source"], payload["frames"]


def build_geometry_reference(geometry_root: Path, contract: dict) -> dict:
    donor = contract["geometry_reference"]
    validate_checkout(geometry_root, donor["head"], {donor["module_path"]: donor["module_blob"]})
    source_path = contract["organic_owner"]["source_path"]
    if git_blob(geometry_root, source_path) != contract["organic_owner"]["source_blob"]:
        raise ValueError("Geometry reference source blob drift")
    script = r'''
import json, sys
from pathlib import Path
root = Path(sys.argv[1]).resolve(); source_path = sys.argv[2]
sys.path.insert(0, str(root / "src"))
from axm_nature_design.rear_tree_geometry_north_low_trunk_bridge_candidate import build_candidate
source = json.loads((root / source_path).read_text(encoding="utf-8"))
candidate = build_candidate(source)
indices = candidate["branch_stub"]["transition_ring_vertex_indices"]
vertices = [candidate["branch_stub"]["vertices"][i] for i in indices]
print(json.dumps({"segment_id": candidate["trunk_segment_id"], "input_points": vertices, "projections": candidate["trunk_projection_samples"]}, sort_keys=True))
'''
    result = subprocess.run([sys.executable, "-c", script, str(geometry_root), source_path], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def max_numeric_delta(a, b) -> float:
    if isinstance(a, list) and isinstance(b, list):
        return max((max_numeric_delta(x, y) for x, y in zip(a, b)), default=0.0)
    return abs(float(a) - float(b))


def compare_projection_rows(expected: list[dict], actual: list[dict]) -> dict:
    if len(expected) != len(actual):
        raise ValueError("Geometry reference projection count drift")
    scalar_fields = ("segment_t", "local_radius_m", "input_radial_distance_m", "surface_residual_m", "projection_span_m")
    vector_fields = ("centerline_point_m", "surface_point_m")
    maximum = 0.0
    for index, (owner_row, procedural_row) in enumerate(zip(expected, actual)):
        for field in scalar_fields:
            pfield = "projection_span_m" if field == "projection_span_m" else field
            ofield = "bridge_span_m" if field == "projection_span_m" else field
            delta = abs(float(owner_row[ofield]) - float(procedural_row[pfield]))
            maximum = max(maximum, delta)
        for field in vector_fields:
            maximum = max(maximum, max_numeric_delta(owner_row[field], procedural_row[field]))
        if procedural_row["axial_coordinate_residual_m"] > 1e-10:
            raise ValueError(f"Procedural axial residual too large at Geometry sample {index}")
    if maximum > 1e-10:
        raise ValueError(f"Procedural projector no longer matches Geometry reference: {maximum}")
    return {"sample_count": len(expected), "maximum_numeric_delta": maximum, "match_within_tolerance": True}


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

    out = args.output_dir.resolve(); out.mkdir(parents=True, exist_ok=True)
    contract = load_json(CONTRACT_PATH); validate_contract(contract)
    frame_contract = load_json(FRAME_CONTRACT_PATH)
    source, frame_report = build_owner_frame_report(args.owner_organic_root.resolve(), contract)
    predecessor = assemble_transition_frame_family(frame_report, frame_contract)
    if predecessor["family_digest"] != contract["predecessor_frame_family_digest"]:
        raise RuntimeError("predecessor transition-frame family digest drift")

    family = assemble_trunk_envelope_projection_family(source, frame_report, predecessor, contract)
    reverse_report = copy.deepcopy(frame_report); reverse_report["frames"] = list(reversed(reverse_report["frames"]))
    reverse_predecessor = copy.deepcopy(predecessor); reverse_predecessor["outputs"] = list(reversed(reverse_predecessor["outputs"]))
    reverse_contract = copy.deepcopy(contract); reverse_contract["authorized_branch_ids"] = list(reversed(reverse_contract["authorized_branch_ids"]))
    reverse_family = assemble_trunk_envelope_projection_family(source, reverse_report, reverse_predecessor, reverse_contract)
    if family["family_digest"] != reverse_family["family_digest"]:
        raise RuntimeError("projection family identity depends on branch ordering")

    geometry = build_geometry_reference(args.geometry_reference_root.resolve(), contract)
    procedural_reference = project_points_to_tapered_trunk(source, geometry["segment_id"], geometry["input_points"])
    compatibility = compare_projection_rows(geometry["projections"], procedural_reference)

    outputs = family["outputs"]
    if len({row["projection_digest"] for row in outputs}) != 5:
        raise RuntimeError("five owner-backed projection outputs are not materially distinct")
    if any(len(row["samples"]) != 3 for row in outputs):
        raise RuntimeError("each branch must retain three topology-free diagnostic samples")

    controls = []
    bad_source_contract = copy.deepcopy(contract); bad_source_contract["organic_source_digest"] = "0" * 64
    controls.append(expect_rejection("organic-source-digest-drift", lambda: assemble_trunk_envelope_projection_family(source, frame_report, predecessor, bad_source_contract)))
    bad_predecessor = copy.deepcopy(predecessor); bad_predecessor["family_digest"] = "0" * 64
    controls.append(expect_rejection("predecessor-frame-family-digest-drift", lambda: assemble_trunk_envelope_projection_family(source, frame_report, bad_predecessor, contract)))
    bad_state = copy.deepcopy(frame_report); bad_state["state"] = "HOLD_FRAME_REVIEW"
    controls.append(expect_rejection("owner-frame-state-drift", lambda: assemble_trunk_envelope_projection_family(source, bad_state, predecessor, contract)))
    bad_center = copy.deepcopy(frame_report); bad_center["frames"][0]["exit_center_m"][0] += 0.01
    controls.append(expect_rejection("owner-vs-predecessor-frame-origin-drift", lambda: assemble_trunk_envelope_projection_family(source, bad_center, predecessor, contract)))
    duplicate = copy.deepcopy(contract); duplicate["authorized_branch_ids"][-1] = duplicate["authorized_branch_ids"][0]
    controls.append(expect_rejection("duplicate-branch-declaration", lambda: validate_contract(duplicate)))
    bad_geometry_head = copy.deepcopy(contract); bad_geometry_head["geometry_reference"]["head"] = "0" * 40
    controls.append(expect_rejection("geometry-reference-head-drift", lambda: build_geometry_reference(args.geometry_reference_root.resolve(), bad_geometry_head)))
    bad_geometry_blob = copy.deepcopy(contract); bad_geometry_blob["geometry_reference"]["module_blob"] = "0" * 40
    controls.append(expect_rejection("geometry-reference-module-blob-drift", lambda: build_geometry_reference(args.geometry_reference_root.resolve(), bad_geometry_blob)))
    centerline_source = {"trunk": [{"id":"a","position":[0,0,0],"radius":1},{"id":"b","position":[0,0,1],"radius":0.8}]}
    controls.append(expect_rejection("centerline-projection-degeneracy", lambda: project_points_to_tapered_trunk(centerline_source, "a->b", [[0,0,0.5]])))
    for key in ("ring_topology_authorized", "indexed_trunk_cut_authorized", "connected_junction_authorized", "weld_or_remesh_authorized", "automatic_rigging_adoption", "automatic_runtime_adoption"):
        bad = copy.deepcopy(contract); bad[key] = True
        controls.append(expect_rejection(f"authority-promotion-{key}", lambda bad=bad: validate_contract(bad)))

    summary = {
        "schema": "axm.nature-branch-transition-trunk-envelope-projection-family-evidence/v0.1",
        "state": STATE,
        "decision": DECISION,
        "procedural_head": git_head(ROOT),
        "organic_owner_head": git_head(args.owner_organic_root.resolve()),
        "geometry_reference_head": git_head(args.geometry_reference_root.resolve()),
        "predecessor_frame_family_digest": predecessor["family_digest"],
        "output_count": family["output_count"],
        "distinct_projection_digest_count": len({row["projection_digest"] for row in outputs}),
        "family_digest": family["family_digest"],
        "reverse_order_family_digest": reverse_family["family_digest"],
        "geometry_reference_compatibility": compatibility,
        "geometry_reference_segment_id": geometry["segment_id"],
        "geometry_reference_sample_count": len(geometry["projections"]),
        "failure_controls": controls,
        "all_failure_controls_rejected": all(row["rejected"] for row in controls),
        "truth_boundary": contract["truth_boundary"],
    }
    write_json(out / "summary.json", summary)
    write_json(out / "family.json", family)
    write_json(out / "contract.json", contract)
    write_json(out / "owner_frame_report.json", frame_report)
    write_json(out / "predecessor_frame_family.json", predecessor)
    write_json(out / "geometry_reference.json", geometry)
    write_json(out / "procedural_geometry_reference_projection.json", procedural_reference)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

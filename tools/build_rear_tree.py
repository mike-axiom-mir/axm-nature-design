from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axm_nature_design.organic_form import build_mesh, load_source
from axm_nature_design.rear_tree_deformation_readiness import evaluate as evaluate_deformation_readiness
from axm_nature_design.rear_tree_flex_interaction_classification import (
    evaluate as evaluate_flex_interaction_classification,
)
from axm_nature_design.rear_tree_root_transition_readiness import (
    evaluate as evaluate_root_transition_readiness,
)
from axm_nature_design.rear_tree_transition_exit_frames import (
    evaluate as evaluate_transition_exit_frames,
)
from axm_nature_design.rear_tree_study import evaluate

SOURCE = ROOT / "examples" / "east_rear_tree_neutral_001.json"


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_obj(mesh: dict, path: Path, study_id: str) -> None:
    lines = [f"# AXM Nature Organic evidence: {study_id}", f"o {study_id}"]
    lines.extend(f"v {v[0]:.9f} {v[1]:.9f} {v[2]:.9f}" for v in mesh["vertices"])
    lines.extend(f"f {t[0]+1} {t[1]+1} {t[2]+1}" for t in mesh["triangles"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _unique_edges(triangles):
    edges = set()
    for a, b, c in triangles:
        for x, y in ((a, b), (b, c), (c, a)):
            edges.add(tuple(sorted((x, y))))
    return sorted(edges)


def _write_svg(mesh: dict, path: Path, view: str, study_id: str) -> None:
    axes = {"front": (0, 2), "side": (1, 2), "top": (0, 1)}
    ax0, ax1 = axes[view]
    points = [(v[ax0], v[ax1]) for v in mesh["vertices"]]
    min0, max0 = min(p[0] for p in points), max(p[0] for p in points)
    min1, max1 = min(p[1] for p in points), max(p[1] for p in points)
    span0 = max(max0 - min0, 1e-9)
    span1 = max(max1 - min1, 1e-9)
    scale = min(520.0 / span0, 520.0 / span1)
    ox = 300.0 - (min0 + max0) * 0.5 * scale
    oy = 300.0 + (min1 + max1) * 0.5 * scale

    def p2(point):
        return ox + point[0] * scale, oy - point[1] * scale

    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">',
        '<rect width="600" height="600" fill="white"/>',
        f'<text x="20" y="30" font-family="monospace" font-size="18">{study_id} / {view}</text>',
    ]
    for a, b in _unique_edges(mesh["triangles"]):
        x1, y1 = p2(points[a])
        x2, y2 = p2(points[b])
        lines.append(
            f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" '
            'stroke="#111" stroke-width="0.7" stroke-opacity="0.58"/>'
        )
    lines.append("</svg>")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "evidence" / "east-rear-tree-neutral-001"
    out.mkdir(parents=True, exist_ok=True)
    source = load_source(SOURCE)
    mesh = build_mesh(source)
    report = evaluate(source)
    readiness = evaluate_deformation_readiness(source)
    flex_interactions = evaluate_flex_interaction_classification(source)
    root_transitions = evaluate_root_transition_readiness(source)
    transition_exit_frames = evaluate_transition_exit_frames(source)
    if report["status"] != "PASS_REAR_SOURCE_ENVELOPE":
        raise SystemExit("east rear tree evidence failed")
    if readiness["state"] not in {
        "HOLD_BRANCH_ROOT_FLEX_ZONE_COVERAGE",
        "PASS_NEUTRAL_BRANCH_ROOT_SUPPORT__DEFORMATION_UNTESTED",
    }:
        raise SystemExit("east rear tree deformation-readiness evidence failed")
    if (
        flex_interactions["state"]
        != "PASS_EXACT_TRUNK_BRANCH_FLEX_INTERACTION_CLASSES__DEFORMATION_UNTESTED"
    ):
        raise SystemExit("east rear tree flex-interaction classification evidence failed")
    if (
        root_transitions["state"]
        != "PASS_EXACT_NEUTRAL_BRANCH_TRANSITION_ENVELOPES__CONNECTED_TOPOLOGY_HELD"
    ):
        raise SystemExit("east rear tree root-transition readiness evidence failed")
    if (
        transition_exit_frames["state"]
        != "PASS_EXACT_NEUTRAL_BRANCH_TRANSITION_EXIT_FRAMES__CONNECTED_TOPOLOGY_HELD"
    ):
        raise SystemExit("east rear tree transition exit-frame evidence failed")

    _write_json(out / "source.json", source)
    _write_json(out / "mesh.json", mesh)
    _write_json(out / "evidence.json", report)
    _write_json(out / "deformation-readiness.json", readiness)
    _write_json(out / "flex-interaction-classification.json", flex_interactions)
    _write_json(out / "root-transition-readiness.json", root_transitions)
    _write_json(out / "root-transition-exit-frames.json", transition_exit_frames)
    _write_obj(mesh, out / "east-rear-tree-neutral-001.obj", source["study_id"])
    for view in ("front", "side", "top"):
        _write_svg(mesh, out / f"{view}.svg", view, source["study_id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

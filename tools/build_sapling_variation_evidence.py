#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axm_nature_design.organic_form import build_mesh, digest, load_source, write_svg
from axm_nature_design.procedural_family import family_digest, generate_accepted_variant, load_family

SOURCE = ROOT / "examples" / "sapling_neutral_001.json"
FAMILY = ROOT / "examples" / "sapling_variation_family_001.json"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_variant_svg(mesh: dict, path: Path, view: str, study_id: str) -> None:
    """Reuse the baseline wire writer while correcting its baseline-only title in derived evidence."""
    write_svg(mesh, path, view)
    text = path.read_text(encoding="utf-8")
    baseline_label = f"sapling-neutral-001 / {view}"
    variant_label = f"{study_id} / {view}"
    if baseline_label not in text:
        raise RuntimeError("baseline SVG label changed; refusing to mislabel procedural evidence")
    path.write_text(text.replace(baseline_label, variant_label, 1), encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: build_sapling_variation_evidence.py OUTPUT_DIR")
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)

    source = load_source(SOURCE)
    family = load_family(FAMILY)
    source_hash = digest(source)
    fam_hash = family_digest(family)

    rows = []
    source_digests = set()
    mesh_digests = set()
    for seed in family["evidence_seeds"]:
        result = generate_accepted_variant(source, family, int(seed))
        receipt = result["receipt"]
        if receipt["state"] != "PASS_BOUNDED_VARIANT" or result["candidate"] is None:
            raise RuntimeError(f"evidence seed {seed} did not produce an accepted bounded variant: {receipt['state']}")
        candidate = result["candidate"]
        mesh = build_mesh(candidate)
        seed_dir = out / f"seed-{int(seed)}"
        seed_dir.mkdir(parents=True, exist_ok=True)
        write_json(seed_dir / "source.json", candidate)
        write_json(seed_dir / "mesh.json", mesh)
        write_json(seed_dir / "receipt.json", receipt)
        for view in ("front", "side", "top"):
            write_variant_svg(mesh, seed_dir / f"{view}.svg", view, candidate["study_id"])

        source_digests.add(receipt["candidate_source_digest"])
        mesh_digests.add(receipt["candidate_mesh_digest"])
        rows.append({
            "seed": int(seed),
            "accepted_attempt": int(receipt["accepted_attempt"]),
            "candidate_study_id": candidate["study_id"],
            "candidate_source_digest": receipt["candidate_source_digest"],
            "candidate_mesh_digest": receipt["candidate_mesh_digest"],
            "moved_branch_tips": receipt["metrics"]["moved_branch_tips"],
            "changed_leaf_blades": receipt["metrics"]["changed_leaf_blades"],
            "bounds_m": receipt["metrics"]["bounds_m"],
            "organic_checks_pass": receipt["metrics"]["organic_checks_pass"],
            "envelope_ok": receipt["metrics"]["envelope_ok"],
            "attachments_preserved": receipt["metrics"]["attachments_preserved"],
            "immutable_fields_preserved": receipt["metrics"]["immutable_fields_preserved"],
        })

    if len(source_digests) != len(rows) or len(mesh_digests) != len(rows):
        raise RuntimeError("retained evidence seeds are not materially distinct by source and mesh digest")

    impossible = json.loads(json.dumps(family))
    impossible["family_id"] = "sapling-impossible-envelope-negative-control"
    impossible["attempt_limit"] = 3
    impossible["acceptance"]["max_envelope_m"] = [1.0, 1.0, 4.0]
    hold = generate_accepted_variant(source, impossible, int(family["evidence_seeds"][0]))["receipt"]
    if hold["state"] != "HOLD_NO_VALID_VARIANT":
        raise RuntimeError("negative-control family did not HOLD")

    summary = {
        "schema": "axm.nature-sapling-variation-evidence/v0.1",
        "state": "PASS_MULTI_SEED_BOUNDED_VARIATION",
        "base_source_digest": source_hash,
        "family_digest": fam_hash,
        "family_id": family["family_id"],
        "seeds": rows,
        "distinct_candidate_source_digests": len(source_digests),
        "distinct_candidate_mesh_digests": len(mesh_digests),
        "negative_control": {
            "state": hold["state"],
            "attempt_limit": hold["attempt_limit"],
            "rejected_attempts": len(hold["rejected_attempts"]),
        },
        "truth_boundary": family["truth_boundary"],
    }
    write_json(out / "family.json", family)
    write_json(out / "summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

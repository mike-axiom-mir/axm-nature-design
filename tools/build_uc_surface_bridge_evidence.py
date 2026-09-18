#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from axm_nature_design.organic_form import load_source
from axm_nature_design.uc_surface_bridge import adapt_source_for_uc
from axm_uc.procedural_3d import publish_glb, verify_glb

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "sapling_neutral_001.json"
OUT = ROOT / "evidence" / "sapling-uc-surface-bridge-001"
EXPECTED_SOURCE_DIGEST = "a61207b23c441b2cc0becd165fa62289bb7e51065ae0d6fa56bf9f3cab036cc1"
EXPECTED_MESH_DIGEST = "89b835bd8f3e728206543d210787f1bbd1cc1bacb6d01f6695caf3ea1a63fa4c"


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    source = load_source(SOURCE)
    bridge = adapt_source_for_uc(source)
    if bridge["source_digest"] != EXPECTED_SOURCE_DIGEST:
        raise SystemExit(f"source digest drifted: {bridge['source_digest']}")
    if bridge["source_mesh_digest"] != EXPECTED_MESH_DIGEST:
        raise SystemExit(f"mesh digest drifted: {bridge['source_mesh_digest']}")
    if bridge["source_triangles"] != 570 or bridge["source_leaf_triangles"] != 50:
        raise SystemExit("unexpected exact sapling triangle identity")
    if bridge["emitted_triangles"] != 620:
        raise SystemExit("leaf backface expansion did not produce the expected bounded triangle count")

    OUT.mkdir(parents=True, exist_ok=True)
    surface_path = OUT / "sapling_uc_surface.json"
    glb_path = OUT / "sapling_uc_bridge.glb"
    evidence_path = OUT / "evidence.json"
    surface_path.write_text(canonical(bridge["surface"]) + "\n", encoding="utf-8")

    publication = publish_glb(glb_path, bridge["surface"], replace=True)
    verification = verify_glb(
        glb_path.read_bytes(),
        expected_spec_digest=publication["specification_sha256"],
    )
    if verification["triangles"] != bridge["emitted_triangles"]:
        raise SystemExit("UC verified triangle count does not match the bridge surface")
    if verification["primitives"] != 2 or verification["materials"] != 2:
        raise SystemExit("UC output did not preserve the two bounded proof material groups")
    if not verification["geometry_validation"]["winding_matches_vertex_normals"]:
        raise SystemExit("UC winding/normal verification failed")

    receiving_head = os.environ.get("AXM_RECEIVING_HEAD", os.environ.get("GITHUB_SHA", "LOCAL_UNBOUND"))
    workflow_sha = os.environ.get("GITHUB_SHA", "LOCAL_UNBOUND")
    evidence = {
        "schema": "axm.nature-uc-surface-bridge-run/v0.1",
        "state": "PASS_EXACT_NATURE_SURFACE_TO_UC_GLB_WITH_EXPLICIT_LEAF_BACKFACES",
        "receiving_repository": "mike-axiom-mir/axm-nature-design",
        "receiving_head": receiving_head,
        "workflow_sha": workflow_sha,
        "uc_repository": "mike-axiom-mir/axm-universal-creation",
        "uc_commit": os.environ.get("AXM_UC_COMMIT", "UNBOUND"),
        "source_digest": bridge["source_digest"],
        "source_mesh_digest": bridge["source_mesh_digest"],
        "surface_digest": bridge["surface_digest"],
        "surface_file_sha256": sha256(surface_path),
        "glb_sha256": sha256(glb_path),
        "source_triangles": bridge["source_triangles"],
        "source_leaf_triangles": bridge["source_leaf_triangles"],
        "emitted_triangles": bridge["emitted_triangles"],
        "emitted_vertices": bridge["emitted_vertices"],
        "leaf_sidedness_strategy": bridge["leaf_sidedness_strategy"],
        "material_scope": bridge["material_scope"],
        "uc_specification_sha256": publication["specification_sha256"],
        "uc_verification": verification,
        "truth_boundary": bridge["truth_boundary"],
        "non_claims": [
            "No final bark/leaf look-development or shader acceptance.",
            "No target-engine culling/import proof; explicit backface geometry removes dependence on an unproven double-sided material flag but does not prove every host renderer.",
            "No wind/deformation/animation state is exported; VFX PR #2 remains separate.",
            "No environment placement, runtime cost, collision, gameplay, CANON, production readiness, or Nature/Technical-Art mastery claim.",
            "No claim that Universal Creation should absorb Nature-specific source semantics.",
        ],
    }
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "state": evidence["state"],
        "receiving_head": evidence["receiving_head"],
        "workflow_sha": evidence["workflow_sha"],
        "glb_sha256": evidence["glb_sha256"],
        "triangles": verification["triangles"],
        "primitives": verification["primitives"],
        "materials": verification["materials"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()

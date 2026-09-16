#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from axm_nature_design.materials_lookdev import apply_profile, build_material_evidence
from axm_nature_design.organic_form import load_source
from axm_nature_design.uc_surface_bridge import adapt_source_for_uc
from axm_uc.procedural_3d import publish_glb, verify_glb

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "sapling_neutral_001.json"
PROFILE = ROOT / "lookdev" / "sapling_material_profile_001.json"
OUT = ROOT / "evidence" / "sapling-material-lookdev-001"
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
    if bridge["leaf_sidedness_strategy"] != "EXPLICIT_OPPOSITE_WINDING_BACKFACE_GEOMETRY":
        raise SystemExit("upstream leaf-sidedness strategy drifted")

    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    baseline_surface = bridge["surface"]
    candidate_surface = apply_profile(baseline_surface, profile)
    lookdev = build_material_evidence(baseline_surface, candidate_surface, profile)
    if lookdev["state"] != "PASS_BOUNDED_MATERIAL_PROFILE_STRUCTURE":
        raise SystemExit(json.dumps(lookdev, indent=2))

    OUT.mkdir(parents=True, exist_ok=True)
    baseline_surface_path = OUT / "baseline_surface.json"
    candidate_surface_path = OUT / "candidate_surface.json"
    baseline_glb_path = OUT / "sapling_baseline_proof_materials.glb"
    candidate_glb_path = OUT / "sapling_candidate_lookdev.glb"
    evidence_path = OUT / "evidence.json"

    baseline_surface_path.write_text(canonical(baseline_surface) + "\n", encoding="utf-8")
    candidate_surface_path.write_text(canonical(candidate_surface) + "\n", encoding="utf-8")

    baseline_publication = publish_glb(baseline_glb_path, baseline_surface, replace=True)
    candidate_publication = publish_glb(candidate_glb_path, candidate_surface, replace=True)
    baseline_verification = verify_glb(
        baseline_glb_path.read_bytes(), expected_spec_digest=baseline_publication["specification_sha256"]
    )
    candidate_verification = verify_glb(
        candidate_glb_path.read_bytes(), expected_spec_digest=candidate_publication["specification_sha256"]
    )

    for name, verification in (("baseline", baseline_verification), ("candidate", candidate_verification)):
        if verification["triangles"] != 620 or verification["primitives"] != 2 or verification["materials"] != 2:
            raise SystemExit(f"{name} UC verification drifted: {verification}")
        if not verification["geometry_validation"]["winding_matches_vertex_normals"]:
            raise SystemExit(f"{name} winding/normal verification failed")

    receiving_head = os.environ.get("AXM_RECEIVING_HEAD", os.environ.get("GITHUB_SHA", "LOCAL_UNBOUND"))
    workflow_sha = os.environ.get("GITHUB_SHA", "LOCAL_UNBOUND")
    evidence = {
        "schema": "axm.nature-sapling-material-lookdev-run/v0.1",
        "state": "PASS_SOURCE_PRESERVING_LOOKDEV_COMPARISON_READY_FOR_TARGET_RENDER",
        "receiving_repository": "mike-axiom-mir/axm-nature-design",
        "receiving_head": receiving_head,
        "workflow_sha": workflow_sha,
        "upstream_bridge_head": "9cab2df43d33effcc4fef3173d233f5a7fb00790",
        "uc_repository": "mike-axiom-mir/axm-universal-creation",
        "uc_commit": os.environ.get("AXM_UC_COMMIT", "UNBOUND"),
        "source_digest": bridge["source_digest"],
        "source_mesh_digest": bridge["source_mesh_digest"],
        "leaf_sidedness_strategy": bridge["leaf_sidedness_strategy"],
        "material_evidence": lookdev,
        "baseline_surface_sha256": sha256(baseline_surface_path),
        "candidate_surface_sha256": sha256(candidate_surface_path),
        "baseline_glb_sha256": sha256(baseline_glb_path),
        "candidate_glb_sha256": sha256(candidate_glb_path),
        "baseline_uc_verification": baseline_verification,
        "candidate_uc_verification": candidate_verification,
        "comparison_contexts_requested": ["neutral_three_quarter", "grazing_side_key"],
        "truth_boundary": "Exact neutral sapling geometry and explicit leaf-backface bridge are unchanged. This run proves only a bounded woody/foliage PBR-scalar material overlay plus UC GLB publication/verification. Visual quality requires direct retained target-render inspection.",
        "non_claims": [
            "No UV or texture quality claim; this candidate intentionally uses no texture maps.",
            "No bark microdetail, leaf normal map, subsurface, transmission, translucency, alpha-cutout, or physically measured botanical reflectance claim.",
            "No claim that the chosen colors/roughness are final Art Direction or species truth.",
            "No renderer equivalence beyond the separately retained Godot proof context.",
            "No runtime cost, environment acceptance, wind/deformation acceptance, gameplay, CANON, production readiness, or materials mastery claim.",
        ],
    }
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "state": evidence["state"],
        "receiving_head": receiving_head,
        "baseline_glb_sha256": evidence["baseline_glb_sha256"],
        "candidate_glb_sha256": evidence["candidate_glb_sha256"],
        "baseline_luminance_gap": lookdev["baseline_luminance_gap"],
        "candidate_luminance_gap": lookdev["candidate_luminance_gap"],
        "baseline_roughness_gap": lookdev["baseline_roughness_gap"],
        "candidate_roughness_gap": lookdev["candidate_roughness_gap"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()

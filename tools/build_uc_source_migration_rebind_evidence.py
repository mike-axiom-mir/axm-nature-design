#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from axm_nature_design.uc_surface_bridge import adapt_mesh_for_uc
from axm_uc.mesh_topology import inspect_mesh_topology
from axm_uc.procedural_3d import publish_glb, verify_glb

SOURCE_MIGRATION_COMMIT = "4ddbe66e5c02d22407ef773d5346a2fe6f349a2d"
HISTORICAL_REAR_COMMIT = "a4e5ee011e1d87f47866a7e6c6f4e66f57b6af12"
UC_COMMIT = "21e206fad99d53f6f01a9d3093b49e590cff7032"
GEOMETRY_ORACLE_COMMIT = "e2224d4bf88f7e68503072c884e5a726b8d0c53d"

EXPECTED = {
    "sapling-neutral-001": {
        "path": "examples/sapling_neutral_001.json",
        "source": "a61207b23c441b2cc0becd165fa62289bb7e51065ae0d6fa56bf9f3cab036cc1",
        "historical": "89b835bd8f3e728206543d210787f1bbd1cc1bacb6d01f6695caf3ea1a63fa4c",
        "migrated": "47dd4d82651138299d05071df3e8a410f21f673ab8d42b936d7222eb5351b862",
    },
    "compact-east-tree-neutral-001": {
        "path": "examples/compact_east_tree_neutral_001.json",
        "source": "9c87cf26f02f7adee832908652942218ec779c9029a0611aae1fb66eb0f62f54",
        "historical": "c7367ed5dcea6ebe39869c48fd653845b25c9a8725a2e637a1d6f2fbee1fa32f",
        "migrated": "420135f6effbadb1b344675948b9ddc471dcb83177702888f0b32327c5121c18",
    },
    "east-rear-tree-neutral-001": {
        "path": "examples/east_rear_tree_neutral_001.json",
        "source": "0adf2cde8cfc355ec21b6fb06c6759b753300164b5f72ba029dc1b8c6d2ef307",
        "historical": "d7fc5deaa1c12d1d8c7d7b6dc95bf1e8544ce26140ee2e4a7d2c67a2c4133e48",
        "migrated": "aa9d450a78fef722672ea9af0f9aca98b4c1a0ca3705661784f5f61f3e9b6a31",
    },
}


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head(root: Path) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()


def donor_mesh(root: Path, relative_path: str) -> dict[str, Any]:
    code = r'''
import json
import os
from pathlib import Path
from axm_nature_design.organic_form import build_mesh, digest, load_source
path = Path(os.environ["AXM_SOURCE_PATH"])
source = load_source(path)
mesh = build_mesh(source)
print(json.dumps({
    "source": source,
    "mesh": mesh,
    "source_digest": digest(source),
    "mesh_digest": digest(mesh),
}, sort_keys=True, separators=(",", ":")))
'''
    env = dict(os.environ)
    env["PYTHONPATH"] = str(root / "src")
    env["AXM_SOURCE_PATH"] = str(root / relative_path)
    raw = subprocess.check_output([sys.executable, "-c", code], cwd=root, env=env, text=True)
    return json.loads(raw)


def topology(mesh: dict[str, Any]) -> dict[str, Any]:
    return inspect_mesh_topology(
        mesh["vertices"],
        [index for triangle in mesh["triangles"] for index in triangle],
    )


def primitive_topology(surface: dict[str, Any], primitive_id: str) -> dict[str, Any]:
    primitive = next(item for item in surface["primitives"] if item["id"] == primitive_id)
    return inspect_mesh_topology(primitive["positions"], primitive["indices"])


def publish(out: Path, stem: str, bridge: dict[str, Any]) -> dict[str, Any]:
    surface_path = out / f"{stem}.surface.json"
    glb_path = out / f"{stem}.glb"
    surface_path.write_text(canonical(bridge["surface"]) + "\n", encoding="utf-8")
    publication = publish_glb(glb_path, bridge["surface"], replace=True)
    verification = verify_glb(glb_path.read_bytes(), expected_spec_digest=publication["specification_sha256"])
    return {
        "surface_path": surface_path.name,
        "surface_sha256": sha256(surface_path),
        "glb_path": glb_path.name,
        "glb_sha256": sha256(glb_path),
        "publication": publication,
        "verification": verification,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-migration-root", type=Path, required=True)
    parser.add_argument("--historical-root", type=Path, required=True)
    parser.add_argument("--uc-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    migration_root = args.source_migration_root.resolve()
    historical_root = args.historical_root.resolve()
    uc_root = args.uc_root.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    observed_migration = git_head(migration_root)
    observed_historical = git_head(historical_root)
    observed_uc = git_head(uc_root)
    if observed_migration != SOURCE_MIGRATION_COMMIT:
        raise SystemExit(f"Nature source-migration donor drifted: {observed_migration}")
    if observed_historical != HISTORICAL_REAR_COMMIT:
        raise SystemExit(f"historical rear donor drifted: {observed_historical}")
    if observed_uc != UC_COMMIT:
        raise SystemExit(f"UC donor drifted: {observed_uc}")

    studies: dict[str, Any] = {}
    for study_id, expected in EXPECTED.items():
        donor = donor_mesh(migration_root, expected["path"])
        if donor["source"].get("study_id") != study_id:
            raise SystemExit(f"{study_id} donor identity drifted")
        if donor["source_digest"] != expected["source"]:
            raise SystemExit(f"{study_id} source digest drifted: {donor['source_digest']}")
        if donor["mesh_digest"] != expected["migrated"]:
            raise SystemExit(f"{study_id} migrated mesh digest drifted: {donor['mesh_digest']}")

        source_topology = topology(donor["mesh"])
        if source_topology["orientation_conflict_edge_count"] != 0:
            raise SystemExit(f"{study_id} migrated source mesh retained orientation conflicts")

        bridge = adapt_mesh_for_uc(
            donor["source"],
            donor["mesh"],
            mesh_relation=f"NATURE_SOURCE_GENERATOR_MIGRATION_PR9@{SOURCE_MIGRATION_COMMIT}",
        )
        if bridge["source_mesh_digest"] != expected["migrated"]:
            raise SystemExit(f"{study_id} bridge mesh digest mismatch")
        emitted_topology = primitive_topology(bridge["surface"], "woody")
        if emitted_topology["orientation_conflict_edge_count"] != 0:
            raise SystemExit(f"{study_id} UC emitted woody surface lost migrated orientation consistency")

        published = publish(out, f"{study_id}-source-migrated", bridge)
        verification = published["verification"]
        if verification["triangles"] != bridge["emitted_triangles"]:
            raise SystemExit(f"{study_id} UC triangle verification drifted")
        if not verification["geometry_validation"]["winding_matches_vertex_normals"]:
            raise SystemExit(f"{study_id} UC winding/normal verification failed")

        studies[study_id] = {
            "source_digest": donor["source_digest"],
            "historical_mesh_digest": expected["historical"],
            "source_generated_migrated_mesh_digest": donor["mesh_digest"],
            "geometry_oracle_candidate_digest": expected["migrated"],
            "geometry_oracle_digest_match": donor["mesh_digest"] == expected["migrated"],
            "uc_source_topology": source_topology,
            "uc_emitted_woody_topology": emitted_topology,
            "bridge": {
                "schema": bridge["schema"],
                "mesh_relation": bridge["mesh_relation"],
                "surface_digest": bridge["surface_digest"],
                "source_triangles": bridge["source_triangles"],
                "emitted_triangles": bridge["emitted_triangles"],
                "leaf_sidedness_strategy": bridge["leaf_sidedness_strategy"],
            },
            "uc_glb": published,
            "result": "PASS_SOURCE_GENERATED_MIGRATED_MESH_THROUGH_CURRENT_UC_GLB",
        }

    rear_expected = EXPECTED["east-rear-tree-neutral-001"]
    historical = donor_mesh(historical_root, rear_expected["path"])
    if historical["source_digest"] != rear_expected["source"]:
        raise SystemExit("historical rear source digest drifted")
    if historical["mesh_digest"] != rear_expected["historical"]:
        raise SystemExit("historical rear mesh digest drifted")
    historical_topology = topology(historical["mesh"])
    if historical_topology["orientation_conflict_edge_count"] != 260:
        raise SystemExit("historical rear baseline no longer reproduces 260 orientation conflicts")
    historical_bridge = adapt_mesh_for_uc(
        historical["source"],
        historical["mesh"],
        mesh_relation=f"HISTORICAL_ORGANIC_REAR_PR8@{HISTORICAL_REAR_COMMIT}",
    )
    historical_publish = publish(out, "east-rear-tree-neutral-001-historical", historical_bridge)
    if historical_publish["verification"]["triangles"] != historical_bridge["emitted_triangles"]:
        raise SystemExit("historical rear UC triangle verification drifted")

    receiving_head = git_head(Path.cwd())
    overall = {
        "schema": "axm.nature-uc-source-migration-rebind/v0.1",
        "state": "PASS_SOURCE_GENERATED_MIGRATED_NATURE_THROUGH_CURRENT_UC_GLB",
        "receiving_repository": "mike-axiom-mir/axm-nature-design",
        "receiving_head": receiving_head,
        "source_migration_repository": "mike-axiom-mir/axm-nature-design",
        "source_migration_pr": 9,
        "source_migration_commit": observed_migration,
        "historical_rear_pr": 8,
        "historical_rear_commit": observed_historical,
        "geometry_oracle_pr": 7,
        "geometry_oracle_commit": GEOMETRY_ORACLE_COMMIT,
        "uc_repository": "mike-axiom-mir/axm-universal-creation",
        "uc_commit": observed_uc,
        "studies": studies,
        "historical_rear": {
            "source_digest": historical["source_digest"],
            "mesh_digest": historical["mesh_digest"],
            "uc_source_topology": historical_topology,
            "uc_glb": historical_publish,
        },
        "pipeline_decision": {
            "uc_core_change_required": False,
            "nature_domain_semantics_moved_to_uc": False,
            "source_generator_bytes_consumed_directly": True,
            "derived_geometry_repair_reapplied_by_technical_art": False,
            "reason": "Nature PR #9 now owns the exact cap-index migration. Technical Art consumes those source-generated bytes directly, while current UC continues to provide only domain-neutral topology inspection and deterministic GLB publication.",
        },
        "truth_boundary": {
            "historical_lineage_preserved": True,
            "source_generated_migrated_meshes_exactly_match_prior_geometry_oracle": True,
            "uc_core_modified": False,
            "exact_uc_glb_bytes_published_and_verified": True,
            "target_host_observation_in_this_receipt": False,
            "map_receiving_scene_changed": False,
            "procedural_variants_rebound": False,
            "normals_tangents_uvs_finalized": False,
            "wind_or_deformation_tested": False,
            "runtime_or_gameplay_acceptance_claimed": False,
        },
        "non_claims": [
            "This receipt rebinds exact source-generated migrated Nature bytes through current UC; it does not merge Nature PR #9 or transfer its lineage into other consumers automatically.",
            "Target-host culling is validated by a separate retained observer in the same workflow, not inferred from topology or GLB verification alone.",
            "No final normals/tangents/UVs, lookdev, wind/deformation, Map acceptance, target-device performance, collision/gameplay, CANON, production-readiness, or Technical-Art mastery claim is made.",
        ],
    }
    (out / "uc-source-migration-rebind-overall.json").write_text(
        json.dumps(overall, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "state": overall["state"],
        "receiving_head": receiving_head,
        "source_migration_commit": observed_migration,
        "uc_commit": observed_uc,
        "studies": {
            key: {
                "mesh": value["source_generated_migrated_mesh_digest"],
                "conflicts": value["uc_source_topology"]["orientation_conflict_edge_count"],
                "glb": value["uc_glb"]["glb_sha256"],
            }
            for key, value in studies.items()
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

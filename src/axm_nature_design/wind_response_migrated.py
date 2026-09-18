"""Explicit compatibility binding for the sapling visual-wind response on the
migrated Nature topology lineage.

This module reuses the already-reviewed hierarchical VFX response without
rewriting its motion profile.  It changes only the neutral generated-mesh
identity expected by that response, and verifies the exact Geometry-backed
source-generator migration that produced it.

The result is visual deformation evidence only: no physical wind, force,
biomechanics, gameplay, rigging, runtime-performance or production claim.
"""
from __future__ import annotations

from pathlib import Path

from . import wind_response as _response
from .source_topology_migration import GEOMETRY_ORACLE_REF, evaluate as evaluate_migration

MIGRATION_PR = 9
MIGRATION_HEAD = "4ddbe66e5c02d22407ef773d5346a2fe6f349a2d"
HISTORICAL_NEUTRAL_MESH_DIGEST = "89b835bd8f3e728206543d210787f1bbd1cc1bacb6d01f6695caf3ea1a63fa4c"
MIGRATED_NEUTRAL_MESH_DIGEST = "47dd4d82651138299d05071df3e8a410f21f673ab8d42b936d7222eb5351b862"
PROFILE = _response.PROFILE
WEATHER_SEMANTICS = _response.WEATHER_SEMANTICS
EXPECTED_SOURCE_DIGEST = _response.EXPECTED_SOURCE_DIGEST
EXPECTED_PRIOR_VFX_HEAD = _response.EXPECTED_PRIOR_VFX_HEAD
EXPECTED_PRIOR_ARTIFACT_ID = _response.EXPECTED_PRIOR_ARTIFACT_ID


def _bind_migrated_mesh_identity() -> None:
    # The underlying response reads this module-global identity at validation
    # time. Binding it here preserves the historical response implementation
    # while making the successor lineage explicit and reviewable.
    _response.EXPECTED_NEUTRAL_MESH_DIGEST = MIGRATED_NEUTRAL_MESH_DIGEST


def _validate_migration_provenance(spec: dict, source: dict) -> None:
    migration = spec.get("generator_migration", {})
    expected = {
        "pr": MIGRATION_PR,
        "head": MIGRATION_HEAD,
        "geometry_oracle_ref": GEOMETRY_ORACLE_REF,
        "historical_mesh_digest": HISTORICAL_NEUTRAL_MESH_DIGEST,
        "migrated_mesh_digest": MIGRATED_NEUTRAL_MESH_DIGEST,
    }
    for key, value in expected.items():
        if migration.get(key) != value:
            raise ValueError(f"generator migration provenance mismatch: {key}")

    result = evaluate_migration(source)
    if result["status"] != "PASS_SOURCE_GENERATOR_WINDING_MIGRATION":
        raise ValueError("current source generator does not pass the pinned topology migration gate")
    if result["migrated_mesh_digest"] != MIGRATED_NEUTRAL_MESH_DIGEST:
        raise ValueError("current migrated mesh identity drifted")
    if result["historical_mesh_digest"] != HISTORICAL_NEUTRAL_MESH_DIGEST:
        raise ValueError("historical mesh identity drifted")
    if result["topology"]["shared_edge_orientation_conflicts"] != 0:
        raise ValueError("migrated source reintroduced shared-edge orientation conflicts")


def load_spec(path: str | Path) -> dict:
    _bind_migrated_mesh_identity()
    return _response.load_spec(path)


def validate_spec(spec: dict, source: dict) -> None:
    _bind_migrated_mesh_identity()
    _validate_migration_provenance(spec, source)
    _response.validate_spec(spec, source)


def deform_mesh(source: dict, spec: dict, time_s: float) -> dict:
    validate_spec(spec, source)
    return _response.deform_mesh(source, spec, time_s)


def measure_sample(neutral: dict, deformed: dict, wind_xy, anchor_z_m: float) -> dict:
    return _response.measure_sample(neutral, deformed, wind_xy, anchor_z_m)


def build_evidence(source: dict, spec: dict) -> dict:
    validate_spec(spec, source)
    evidence = _response.build_evidence(source, spec)
    evidence["migration_rebind"] = {
        "pr": MIGRATION_PR,
        "head": MIGRATION_HEAD,
        "geometry_oracle_ref": GEOMETRY_ORACLE_REF,
        "historical_neutral_mesh_digest": HISTORICAL_NEUTRAL_MESH_DIGEST,
        "migrated_neutral_mesh_digest": MIGRATED_NEUTRAL_MESH_DIGEST,
        "response_profile_changed": False,
        "source_json_changed": False,
        "generator_triangle_winding_changed": True,
    }
    return evidence


def write_comparison_svg(meshes, path: str | Path, view: str) -> None:
    _response.write_comparison_svg(meshes, path, view)

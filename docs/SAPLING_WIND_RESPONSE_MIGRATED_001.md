# Sapling Wind Response — Migrated Topology Rebind 001

Status: **bounded VFX / atmosphere rebind candidate — no new motion-profile preference claimed**.

## Why this lane exists

Nature source-generator migration PR #9 changed only tapered-segment cap index winding and established the current sapling generated-mesh identity `47dd4d82651138299d05071df3e8a410f21f673ab8d42b936d7222eb5351b862`. Its own truth boundary explicitly held VFX/deformation receipts for exact downstream rebinding.

The established hierarchical sapling response on VFX PR #2 still targeted historical neutral mesh `89b835bd8f3e728206543d210787f1bbd1cc1bacb6d01f6695caf3ea1a63fa4c` even though the source JSON and Weather visual-direction handoff were unchanged.

This branch closes only that lineage gap.

## Exact relationship

Parent source-generator migration: `4ddbe66e5c02d22407ef773d5346a2fe6f349a2d`.

Geometry oracle retained by that migration: `e2224d4bf88f7e68503072c884e5a726b8d0c53d`.

Historical VFX response implementation is reused unchanged as `src/axm_nature_design/wind_response.py`. A small explicit compatibility layer binds that implementation to the migrated neutral mesh identity and requires the current source generator to continue passing the pinned migration oracle.

The response profile is not redesigned:

- visual direction remains `[1.0, 0.35]` and visual-only;
- duration remains `0.50 s`;
- samples remain `0 / 0.125 / 0.25 / 0.375 / 0.50 s`;
- lower anchor remains `z <= 0.92 m`;
- peak displacement ceiling remains `0.18 m`;
- primary / branch / leaf component caps remain `0.120 / 0.045 / 0.015 m`;
- exact neutral return remains required;
- branch/leaf attachment continuity remains required.

## Evidence gate

The dedicated workflow must run the full receiving repository suite on Python 3.11 and 3.13 and build exact retained migrated-response evidence. The scoped PASS requires:

- exact PR #9 parent ancestry;
- exact source JSON digest unchanged;
- exact migrated neutral mesh digest;
- zero indexed shared-edge orientation conflicts through every retained deformed sample;
- unchanged triangles/regions through deformation;
- exact neutral return at both endpoints;
- `0.18 m` peak bound;
- zero lower-anchor drift within tolerance;
- downwind-only response within tolerance;
- explicit migration-provenance negative control failing closed.

## Visual tradeoff / review note

This rebind intentionally does **not** create a new silhouette or sway preference. Its visual value is continuity: the existing hierarchical response can be evaluated on the topology lineage that removed the historical culling-slit defect instead of forcing VFX to choose between a newer static mesh and an older dynamic mesh.

Because this repository-level proof is renderer-neutral, it does not prove the deformed migrated mesh has no engine-specific culling, shading or temporal defect. A later current-world Godot receiver may test that separately without rewriting this source-level result.

## Truth boundary

A PASS proves only that the exact current migrated sapling mesh can receive the retained deterministic hierarchical **visual-only** deformation while preserving the migrated topology, anchor, response ceiling, source/Weather identities and neutral return.

It does **not** prove physical wind, plant biomechanics, skeleton/skin behavior, engine playback smoothness, current-world visual acceptance, target-device CPU/GPU/FPS/VRAM cost, collision, navigation, gameplay, Art Direction acceptance, CANON, production readiness or VFX mastery.

The four AXM roots remain the merge gate.

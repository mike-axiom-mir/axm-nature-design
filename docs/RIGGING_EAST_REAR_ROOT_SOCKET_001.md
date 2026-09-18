# Rigging — east/rear root-socket diagnostic 001

Status target: **bounded Rigging experiment only**.

This lane consumes the exact Organic Form PR #8 east/rear source at
`fdc9d2b6ee729728551e22fd3eafa23ad60b6c7a` without changing the source JSON or
the Organic mesh generator.

## Why this seam

Organic completed exact root-centered flex metadata for all five primary branch
roots while keeping every declaration `DECLARED_NOT_DEFORMATION_TESTED`.  The
weakest neutral support witness is `north-top`, whose exact source root is
`[0.01, 0.0, 3.16] m`, source flex radius is `0.12 m`, and neutral support
margin is about `0.001012586854 m`.

Rigging therefore tests only the smallest receiver-owned question: can that
exact root be used as a deterministic articulation socket for the exact
`north-top` branch + its leaf cluster while leaving the rest of the generated
receiver unchanged?

## Exact identities

- source-owner PR: Nature #8;
- source-owner head: `fdc9d2b6ee729728551e22fd3eafa23ad60b6c7a`;
- source digest: `178cd8cfb1a859bff411f60e13154109528062cf0ad2384b343d406cc0cc9d61`;
- generated Organic mesh digest:
  `d7fc5deaa1c12d1d8c7d7b6dc95bf1e8544ce26140ee2e4a7d2c67a2c4133e48`;
- source flex declaration: `north-top-branch-flex`, center
  `[0.01, 0.0, 3.16] m`, radius `0.12 m`, still
  `DECLARED_NOT_DEFORMATION_TESTED`.

The Geometry PR #9 migrated-winding mesh is a distinct lineage and is not
silently adopted by this source-level Rigging experiment.

## Bounded articulation probe

Rigging uses the exact source flex center as the joint pivot.  It derives a
bend-plane axis from the normalized cross product of:

1. the nearest authored local trunk tangent at the root (`crown -> tip`); and
2. the first authored `north-top` branch tangent.

The exact generated child partition is only:

- `branch:north-top:0`;
- `branch:north-top:1`;
- the four `leaf:north-top-leaves:*` blades.

That partition contains 52 generated vertices / 72 triangles.  The other 338
vertices are identity-mapped.

The diagnostic probe interval is exactly **-5° through +5°**, with retained
representative poses **-5 / -2.5 / 0 / +2.5 / +5°**.  This interval is a
Rigging verification envelope only.  It is not a biological, authored or
production range of motion.

The selected child receives one rigid Rodrigues rotation around the exact
source-owned pivot/axis.  This deliberately proves socket/hierarchy behavior
before inventing production skin weights.

## What can be proven continuously

For every real angle in the declared diagnostic interval, the transform itself
analytically preserves:

- the exact pivot;
- all selected-child pairwise distances;
- each selected-child projection onto the rotation axis;
- every fixed receiver position.

Representative generated-mesh poses are retained to prove the implementation
matches those invariants and to quantify the actual bounded displacement.

This does **not** prove surface attachment, motion collision/clearance, branch
stress, plant biomechanics, wind behavior, deformation aesthetics, or an
allowable source ROM.

## Fail-closed gates

The evaluator rejects:

- source digest drift;
- generated-mesh identity drift;
- pivot drift from the exact Organic flex center;
- flex-radius drift;
- ownership drift to another branch;
- widening/retiming the diagnostic interval;
- promotion of the probe to a source/biological ROM;
- Animation acceptance;
- Runtime acceptance.

## Authority boundary

Organic Form retains source geometry/metadata authority. Geometry retains
topology authority. VFX owns wind/effect response. Animation owns timing and
playback. Technical Art owns transport/target-host binding. Runtime owns
controller/device/performance. Art/QA own visual acceptance.

A green result here is only a bounded Rigging socket/articulation proof for the
exact pinned source identity. It is not CANON or production readiness.

The four AXM roots remain the gate: **Truth; Agency / non-domination;
Continuity; Wisdom before speed**.

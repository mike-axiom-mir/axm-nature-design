# VFX east-rear Weather-direction five-socket sign family 002

Status: bounded review evidence only.

## Why this successor exists

Nature Rigging PR #14 has expanded from one `north-top` socket to five exact, pairwise-disjoint primary branch child sockets on the Geometry-migrated east/rear tree receiver. VFX PR #16 already resolved `north-top` against Weather PR #2's exact visual-only direction `[1.0, 0.35]`, but the other four sockets had no equivalent polarity evidence.

This successor does not invent wind motion. It asks only whether each exact Rigging diagnostic `-5° / 0° / +5°` witness has a resolvable signed relationship to the source-owned Weather visual direction.

## Exact lineage

- Nature Rigging PR #14 head: `898529f602893c8f6be179bd3e9b6821fc099904`.
- Prior VFX north-top sign PR #16 head: `1976c5a4ff0a51b5f3ee4bfd323dbb6f89c34787`.
- Weather PR #2 head: `ca2eaba519e8449835b0ea6ef944b7080c3caa6a`.
- Weather source blob: `11298d447f262da8a78e43e2df68bc0346c99a2c`.
- Weather `wind_xy`: `[1.0, 0.35]`.
- Weather semantics: `VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED`.

The exact socket family is:

` south-low / north-low / east-mid / west-high / north-top `

Each child is independently probed using Rigging's exact generated 52-vertex child partition, exact source-owned root/flex pivot, and exact source-derived bend-plane axis.

## Method

For every socket independently:

1. Re-run the exact five-socket Rigging prerequisite.
2. Rebuild the actual generated Nature mesh.
3. Re-run the Rigging child-selection/pivot/axis probe for that socket.
4. Rotate only that selected child to exact witnesses `-5° / 0° / +5°`.
5. Compute its XY centroid displacement.
6. Project that displacement onto normalized Weather visual direction.
7. Require the neutral witness to remain zero and the two signed witnesses to be measurably separable.
8. Retain whichever signed witness has the larger downwind centroid projection as a **review-only polarity**.
9. Require `north-top` to reproduce the earlier PR #16 result exactly before accepting the family successor.

The generated SVG shows actual selected generated vertices for all five sockets and all three exact witness poses. It is review geometry, not a game render.

## Truth boundary

A green result means only that five per-socket visual-direction signs can be determined for this exact source/Rigging/Weather lineage.

It does **not** establish or adopt:

- physical wind, force, drag, turbulence, pressure or precipitation physics;
- Weather speed as a physical magnitude;
- timing, cadence, phase or gust logic;
- a final vegetation amplitude;
- biological or botanical response;
- simultaneous multi-branch motion;
- an Animation clip or controller;
- Runtime/device behavior;
- collision, damage or gameplay;
- Art Direction or independent Visual-QA acceptance;
- target-device performance;
- CANON or production readiness.

Weather keeps source semantics. Rigging keeps articulation. Animation keeps motion authorship. Runtime keeps controller/performance authority. VFX owns only this bounded per-socket visual-direction compatibility evidence.

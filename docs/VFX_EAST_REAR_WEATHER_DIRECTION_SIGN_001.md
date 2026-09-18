# VFX east-rear Weather-direction socket sign 001

Status: bounded review evidence only.

This lane stacks exactly on Nature Animation PR #15 head `74354ff851538d4d8aba9332900ae40218415eaf` and consumes only the source-owned Weather visual direction from `mike-axiom-mir/axm-weather-design` PR #2 exact head `ca2eaba519e8449835b0ea6ef944b7080c3caa6a`.

## Question

Rigging PR #14 proves one exact east-rear `north-top` child can be rotated over a diagnostic `-5..+5 deg` interval. Animation PR #15 then exercises that interval with a diagnostic pulse and explicitly says that pulse is **not wind**.

VFX therefore does not retime or relabel the Animation pulse. The bounded receiving question is smaller:

> Which signed Rigging witness, `-5 deg` or `+5 deg`, moves the actual generated selected-child geometry farther along the exact Weather source's declared **visual** direction in the XY plane?

Resolving that sign removes one future Weather-to-Nature hookup ambiguity without inventing wind strength, timing, biological response or a production motion.

## Exact donors

Nature Animation owner:

- repository `mike-axiom-mir/axm-nature-design`;
- PR #15;
- head `74354ff851538d4d8aba9332900ae40218415eaf`;
- truth label `ANIMATION_DIAGNOSTIC_SOCKET_PULSE_NOT_WIND_NOT_BIOLOGICAL_ROM_NOT_CONTROLLER`.

Weather visual-direction donor:

- repository `mike-axiom-mir/axm-weather-design`;
- PR #2;
- head `ca2eaba519e8449835b0ea6ef944b7080c3caa6a`;
- source `examples/wind_atmosphere_baseline_001.json`;
- source blob `11298d447f262da8a78e43e2df68bc0346c99a2c`;
- source digest `b33feba47b0a0f9a99ec439e32a87ff6d4cb2dacffe33ba78f8b646c3a1be8d6`;
- exact `wind_xy = [1.0, 0.35]`;
- semantics `VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED`.

## Method

The verifier rebuilds the exact Nature generated mesh and exact Rigging receiver, re-runs the exact Animation prerequisite, then reuses the Animation-local exact Rodrigues pose transform at only three Rigging witnesses: `-5`, `0`, and `+5 deg`.

For the 52 selected child vertices it computes:

- neutral XY centroid;
- posed XY centroid for each witness;
- centroid displacement projected onto the normalized Weather visual direction;
- signed crosswind projection;
- mean/min/max per-vertex downwind projections.

The review-only sign is whichever of the exact `-5` / `+5 deg` witnesses produces the larger selected-child centroid projection along the Weather visual direction. The neutral witness must remain zero and the two signed witnesses must be measurably separable.

The retained SVG shows all three actual generated child poses in XY with the exact Weather visual-direction arrow. It is evidence for sign compatibility only, not final art.

## Explicit non-claims

A PASS does not establish or adopt:

- physical wind, force, drag or biomechanics;
- wind strength or gust magnitude;
- wind timing or cadence;
- a final vegetation amplitude;
- the Animation PR #15 diagnostic pulse as wind motion;
- Runtime controller/state-machine behavior;
- gameplay, collision, damage or interaction;
- Art Direction or independent Visual QA acceptance;
- target-device performance;
- CANON or production readiness.

Weather keeps source semantics. Rigging keeps articulation and the diagnostic interval. Animation keeps timing and motion authorship. VFX only resolves this one visual-direction sign relationship for a later explicit receiving decision.

The four AXM roots remain the merge gate: Truth, Agency / non-domination, Continuity, Wisdom before speed.

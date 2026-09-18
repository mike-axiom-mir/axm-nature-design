# Rigging — east/rear shared-driver composition 005

## Why this exists

Rigging PR #14 already owns five exact source-derived branch sockets and the mixed
shared-command sign adapter. That predecessor intentionally refused to call the five
independent sockets a simultaneous-motion result. Geometry PR #18 has since rebound
the exact shared-driver static receiver, including the two interior `±2.5°` states,
without changing the source, receiver, pivots, axes or partitions.

The remaining Rigging question is smaller than Animation: can one scalar diagnostic
parameter be applied to all five sockets at once as one deterministic kinematic
composition while preserving the exact Rigging identities and authority boundaries?

## Bounded answer

For branch `i` and shared diagnostic parameter `u`:

`local_angle_i(u) = command_sign_multiplier_i * u`

`p_i(u) = pivot_i + R(axis_i, local_angle_i(u)) * (p_i0 - pivot_i)`

The exact multiplier family remains `+ / - / + / - / +`. The five selected vertex
sets are pairwise disjoint, so each selected vertex receives exactly one rigid
rotation from the same neutral receiver. All other vertices remain identity-mapped.

Therefore, for every real `u` in the already-owned `[-5°, +5°]` diagnostic interval:

- each local angle stays inside the existing per-socket interval;
- the five child transforms commute because their vertex supports are disjoint;
- globally fixed vertices remain exact;
- each source-owned pivot remains exact;
- each child remains rigid, preserving pairwise distances;
- projection onto each child's own rotation axis remains invariant;
- the parameter-to-pose map is continuous.

Representative witnesses remain `-5 / -2.5 / 0 / +2.5 / +5°`. They are evidence
samples, not the basis of the analytic continuity statement.

## Geometry donor boundary

Current Geometry PR #18 head `75b7556b4dae7137411f4948e2e673a39de5467c`
retains exact static receiver structure and finite child-child intersection observations
for the same five shared-driver witnesses. Rigging consumes that exact identity only
as a structural handoff. Its finite collision observations are not promoted into a
continuous collision-clearance claim.

## Truth boundary

This proves a continuous **Rigging kinematic parameter field**, not timed motion.
It does not define cadence, interpolation, playback, wind physics, force, drag,
source/biological ROM, continuous collision/self-intersection clearance, target-host
transport, Runtime/controller/device behavior, gameplay/physics, visual acceptance,
CANON or production readiness. Animation, Technical Art, Runtime, VFX/Weather,
Geometry, Art Direction and Visual QA retain their own acceptance gates.

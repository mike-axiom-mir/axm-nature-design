# Animation east-rear shared-driver diagnostic loop 004

## Scope

This Animation successor consumes the exact green five-socket Rigging shared-driver composition from PR #14 head `b4b480b415047fea90b4740f7702ced0dba9142d` and gives that already-defined kinematic parameter one bounded time-domain diagnostic loop.

Animation does not modify the Organic source, Geometry receiver, Rigging pivots/axes/child partitions, mixed polarity map, VFX visual-direction semantics, Technical-Art receiver, Runtime behavior, or Universal Creation.

## Continuity

Previous Nature Animation PR #15 head `b0771b3319b783103c8e4677d062c00419df7559` proved five independent one-branch-at-a-time clips using the same `1.0 s / 40 Hz / 41 endpoint-inclusive samples / 0 -> +5 -> 0 -> -5 -> 0` timing identity. This successor preserves that timing identity while rebinding it to the newer Rigging-owned simultaneous shared-driver parameter.

A first successor draft was opened from an earlier Rigging source head before the owner added its dedicated verification files. That draft was closed without claiming a PASS; this lane restarts from the exact green owner head above.

## Motion candidate

Contract: `axm.nature-animation-five-socket-shared-driver-loop/v0.1`.

Clip: `east-rear-five-socket-shared-driver-diagnostic-loop-004`.

Shared parameter:

`u(t) = 5 * sin(2*pi*t)^3`

with exact landmarks clamped at:

- `0.00 s -> 0°`
- `0.25 s -> +5°`
- `0.50 s -> 0°`
- `0.75 s -> -5°`
- `1.00 s -> 0°`

The Rigging-owned local polarity map remains unchanged:

- `south-low +1`
- `north-low -1`
- `east-mid +1`
- `west-high -1`
- `north-top +1`

Therefore shared `+5°` produces local `+5/-5/+5/-5/+5°`; shared `-5°` produces the exact inverse.

The amplitude is still only the Rigging diagnostic interval. It is not source or biological range of motion and not wind strength.

## Evidence method

All 41 authored samples are executed against the exact generated source mesh using Rigging's own simultaneous composition function. At every sample Animation checks:

- all five branch child partitions move from one neutral receiver under the same shared parameter;
- composition remains order-independent across the five pairwise-disjoint children;
- all 130 globally fixed vertices remain fixed;
- all five generated pivot vertices remain fixed;
- each 52-vertex branch child remains rigid;
- each child preserves projection onto its source-derived Rigging axis;
- all local angles remain inside the exact Rigging diagnostic interval;
- endpoint closure returns the full receiver to neutral;
- the visible 40-sample repeat seam equals the authored final adjacent step;
- the bidirectional shared-driver curve remains antisymmetric;
- the five exact Rigging representative shared-driver witnesses replay with zero/within-tolerance metric drift.

The retained SVG is a deterministic timing review surface generated from the executed evidence, not Art Direction approval.

## Truth boundary

This evidence may claim sampled simultaneous five-branch kinematic motion because Rigging now owns one continuous simultaneous shared parameter over the same five sockets.

It does **not** claim:

- natural vegetation motion or final timing/style;
- source or biological range of motion;
- physical wind, plant biomechanics, or VFX motion adoption;
- continuous collision/self-intersection clearance (Geometry has finite static witnesses only);
- Godot/target-engine playback or interpolation equivalence;
- wall-clock/display delivery;
- Runtime controller/state-machine/input/device behavior;
- physics or gameplay acceptance;
- target-device performance;
- Art Direction or independent Visual QA acceptance;
- CANON or production readiness.

The next downstream handoff is Technical Art: if it chooses to adopt this exact Animation head, it must rebind its current Nature target receiver from the older Rigging/Animation pair to this newer shared-driver owner and re-test in the target host. Runtime remains downstream of that evidence.

# East-rear north-top root-socket Animation diagnostic 001

## Purpose

This lane gives the exact Rigging PR #14 `north-top` socket one bounded time-domain review surface without promoting Rigging's diagnostic interval into source motion, biological ROM, physical wind, VFX semantics, Runtime controller logic or gameplay.

Exact Rigging prerequisite: `mike-axiom-mir/axm-nature-design#14` at `87ce8b2ff10937abec4432e1c6d5a7114a076cdb`.

The source, generated mesh, pivot, source-derived axis, 52-vertex child partition, 338 fixed vertices and Rigging `-5..+5°` diagnostic interval are consumed unchanged.

## Bounded motion candidate

`north-top-root-socket-diagnostic-pulse-001`

Truth label:

`ANIMATION_DIAGNOSTIC_SOCKET_PULSE_NOT_WIND_NOT_BIOLOGICAL_ROM_NOT_CONTROLLER`

The candidate is exactly 1.0 s at 40 Hz with 41 endpoint-inclusive samples. Angle is:

`5 * sin(2*pi*t)^3 degrees`

Exact semantic landmarks are forced to:

- `0.00 s -> 0°`
- `0.25 s -> +5°`
- `0.50 s -> 0°`
- `0.75 s -> -5°`
- `1.00 s -> 0°`

The endpoint sample is retained only as a duplicate-neutral seam witness. A repeating sampled review uses samples `0..39`, so the visible wrap is tested against the authored final adjacent step instead of displaying neutral twice.

The 1.0 s / 40 Hz choice is an Animation diagnostic candidate only. It is not a claim of natural vegetation cadence or production timing.

## Evidence method

The Animation evaluator first reruns the exact Rigging prerequisite. It then replays the same source-owned pivot/axis rigid-child transform through all 41 authored times over the actual generated east-rear mesh.

It verifies:

- every sample remains inside the exact Rigging diagnostic bound;
- all 338 non-child vertices remain exact;
- the source-owned pivot remains exact;
- selected-child pairwise distances and axis projection remain invariant;
- the endpoint returns exactly to neutral;
- the visible repeat step equals the authored final adjacent step;
- the curve is bidirectionally antisymmetric;
- a separate replay of Rigging's exact `-5/-2.5/0/+2.5/+5°` witnesses reproduces its retained metrics within `1e-12`.

CI also retains a deterministic five-pose SVG made from the actual generated child vertices at `0/+5/0/-5/0°` for review. This is sampled proof evidence, not a target-engine playback claim.

## Fail-closed boundaries

Evidence generation rejects retiming, sample-rate drift, amplitude widening, wind-motion promotion, biological/source-ROM promotion, Runtime controller acceptance and gameplay acceptance.

## Ownership

- Organic Form owns the source body and flex metadata.
- Geometry owns topology migration separately; this lane intentionally remains on Rigging's exact historical generated-mesh lineage and does not silently adopt Geometry PR #9.
- Rigging owns the pivot, axis, child partition and diagnostic articulation interval.
- Animation owns only this bounded diagnostic timing/curve and sampled-motion evidence.
- VFX owns wind/effect response semantics.
- Technical Art owns target-host transport.
- Runtime owns controller/state-machine and device/performance acceptance.
- Art Direction and Visual QA own motion/aesthetic acceptance.

## Truth boundary

A PASS proves only that one deterministic 1.0 s / 40 Hz sampled Animation diagnostic can exercise the exact Rigging PR #14 north-top socket bidirectionally, preserve its rigid/fixed invariants and repeat without a larger hidden seam step.

It does **not** prove source/biological ROM, wind/biomechanics, collision/clearance, target-engine playback, wall-clock/display delivery, Runtime controller/state-machine behavior, gameplay/input, target-device performance, final naturalness/style, Art/QA acceptance, CANON, production readiness or Animation mastery.

The four AXM roots — **Truth, Agency / non-domination, Continuity, Wisdom before speed** — remain the merge gate.

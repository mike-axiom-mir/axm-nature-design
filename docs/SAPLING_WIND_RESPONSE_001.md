# Sapling Wind Response 001

Status: **bounded VFX / atmosphere candidate**.

This study stacks on the exact source-owned sapling from `axm-nature-design` PR #1 head `fbc202449981f2bac153951c561ed0ed6120c936` and consumes only the visual direction from `axm-weather-design` PR #2 head `ca2eaba519e8449835b0ea6ef944b7080c3caa6a`.

## What it tests

The exact 390-vertex / 570-triangle sapling receives one deterministic 0.5-second visual-only downwind sway pulse. Vertices at or below the authored lower flex height (`z <= 0.92 m`) remain fixed. Above that anchor, a smooth height weight reaches an authored maximum tip displacement of `0.18 m` at `t=0.25 s`, then returns exactly to the untouched source mesh at `t=0.50 s`.

Retained evidence includes exact 3D meshes/OBJs for `0.00 / 0.25 / 0.50 s`, structural measurements, and front/side/top three-panel SVG comparisons.

## Why this is VFX evidence, not physics or rigging

The response is a renderer-neutral deformation field chosen to make a real vegetation reaction observable. It does not model force, mass, stiffness, turbulence, plant biomechanics, skin weights, a skeleton, collision, gameplay, or a runtime particle system. The source flex-zone declarations remain unchanged and explicitly unproven by the Organic Form lane.

## Acceptance boundary

A structural PASS requires exact source/weather provenance, exact neutral return at both endpoints, unchanged topology and region identity, zero anchor drift, bounded crosswind residual, no structural triangle failure at retained samples, and peak displacement matching the authored `0.18 m` visual bound.

Art Direction / Visual Observer still owns perceptual judgment of whether the amount and shape of sway look good. Environment still owns whether this exact response remains readable once composed into the real map slice. Runtime still owns cost.

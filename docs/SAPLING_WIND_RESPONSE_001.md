# Sapling Wind Response 001

Status: **bounded VFX / atmosphere candidate — art-direction hierarchy repair under review**.

This study remains stacked on the exact source-owned sapling from `axm-nature-design` PR #1 head `fbc202449981f2bac153951c561ed0ed6120c936` and consumes only the visual direction from `axm-weather-design` PR #2 head `ca2eaba519e8449835b0ea6ef944b7080c3caa6a`.

## Retained before-evidence

The first exact VFX head `4ef316157844fc2236a7671ce9e90a5435cba2c5` produced a three-sample global height-weighted response and retained artifact `10427854091`.

Art Direction directly inspected that exact artifact and returned:

`PASS_BOUNDED_VISIBLE_RESPONSE_PROOF / HOLD_ART_DIRECTION_SWAY_PROFILE_001`

The visible issue was not attachment failure or insufficient amplitude. At the 0.25 s peak, trunk, branches and leaf fans read too much like one height-sheared body, with too little internal response hierarchy. That head/artifact stays explicit before-evidence and is not rewritten.

## v0.2 bounded repair

The response keeps the successful constraints:

- exact Nature source and Weather visual-direction identities;
- visual-only semantics;
- 0.50 s duration;
- fixed source vertices at/below `z = 0.92 m`;
- exact neutral mesh at 0.00 s and 0.50 s;
- unchanged topology and region identity;
- same **0.18 m maximum-displacement ceiling**.

Only the spatial response hierarchy changes.

At peak, the visual displacement budget is:

- primary height response: **0.120 m** maximum;
- branch/crown-tip secondary give: **0.045 m** maximum;
- leaf-base-to-tip secondary give: **0.015 m** maximum.

The components sum to the existing **0.180 m ceiling**. All components remain aligned to the exact Weather visual vector; this candidate deliberately adds no crosswind noise, gusts, turbulence, inertia or force semantics.

Branch secondary weight progresses from each exact source-owned branch attachment toward its tip. The final crown segment receives the same bounded tip progression. Each leaf cluster inherits its support-tip response so its base does not detach, then receives only a local blade-base-to-tip secondary increment.

The retained comparison window is expanded to five same-camera samples:

`0.000 / 0.125 / 0.250 / 0.375 / 0.500 s`

Front, side and top boards are generated from the exact deformed meshes.

## Why this is VFX evidence, not physics or rigging

The response remains a renderer-neutral visual deformation field. It does not model force, mass, stiffness, drag, turbulence, plant biomechanics, a skeleton, skin weights, collision, gameplay, or a runtime particle system.

The source flex-zone declarations remain unchanged as `DECLARED_NOT_DEFORMATION_TESTED`. Branch/crown/leaf response weights are candidate-local VFX evidence and do not promote those flex declarations into rigging truth.

## Acceptance boundary

A structural PASS requires:

- exact source/weather/before-evidence provenance;
- exact neutral return;
- unchanged topology/region identity;
- zero lower-anchor drift within tolerance;
- downwind-only bounded response;
- maximum displacement no greater than 0.18 m;
- non-zero branch and leaf secondary response;
- leaf-base displacement matching its source support-tip displacement within tolerance;
- structural validity at all five retained samples;
- source flex claims remaining unpromoted.

Those machine gates do **not** prove that the hierarchy looks better. Art Direction / Visual Observer still own the perceptual A/B decision. Environment still owns the later placed-scene comparison, and Runtime still owns cost once a real engine consumes a dynamic response.

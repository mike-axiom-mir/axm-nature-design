# Nature Design -> Universal Creation Surface Bridge 001

Status: **EXPERIMENTAL TECHNICAL-ART CROSS-REPO EVIDENCE**

This lane exists because the first Nature Design sapling is now consumed by Environment and VFX, but its exact triangle body still had no proven Universal Creation / GLB handoff. Organic Form also recorded a specific renderer-facing unknown: the 25 authored leaf blades are planar and had no accepted two-sided material/backface treatment.

## Exact source

The bridge stacks on `axm-nature-design` Organic Form PR #1 exact source head:

`fbc202449981f2bac153951c561ed0ed6120c936`

Pinned source identities:

- source digest: `a61207b23c441b2cc0becd165fa62289bb7e51065ae0d6fa56bf9f3cab036cc1`
- mesh digest: `89b835bd8f3e728206543d210787f1bbd1cc1bacb6d01f6695caf3ea1a63fa4c`
- source mesh: 390 vertices / 570 triangles
- leaf blades: 25, represented by 50 source triangles
- source coordinates: `+X east/right, +Y north/forward, +Z up; metres`

The Universal Creation consumer is pinned exactly to:

`49ef11ca42b2079dffbd595daa8ea8626b99d2ab`

UC is used through its real strict `axm.surface-3d/v0.1` generator and `publish_glb()` / `verify_glb()` path. This repository does not copy UC's GLB encoder or verifier.

## Bounded bridge

`axm_nature_design.uc_surface_bridge.adapt_source_for_uc()` keeps Nature semantics local and performs only the source-owned handoff needed by the current mesh:

1. requires the exact Nature source coordinate declaration rather than guessing axes;
2. maps source `[x_right, y_forward, z_up]` to UC `[x_right, y_up, z_forward]` as `[x, z, y]`;
3. reverses front-face winding because the Y/Z swap changes handedness;
4. computes explicit flat normals from the exact source triangles;
5. groups the output only into `woody` and `foliage` proof surfaces;
6. uses bounded proof-only colors to make those groups inspectable without claiming final LookDev;
7. emits a second opposite-winding face with opposite normal for every planar leaf triangle.

The last step is deliberate. Current UC `axm.surface-3d/v0.1` supports bounded color/metallic/roughness plus optional unlit/emissive fields, but no two-sided material field. Instead of silently assuming a target renderer will disable backface culling, this exact proof uses explicit geometry for both leaf sides. That costs 50 additional triangles on this sapling: 570 source triangles become 620 UC triangles.

This is a **source-owned compatibility strategy**, not a declaration that duplicated backfaces are the final or universal foliage representation. If another materially different domain needs sidedness and a shared UC material flag is proven across real consumers, that may justify a future horizontal contract. One sapling is not enough to centralize Nature policy into UC.

## Evidence path

`.github/workflows/uc-nature-surface-bridge.yml`:

- compiles the exact Nature bridge;
- runs bridge regressions;
- checks out pinned UC commit `49ef11ca42b2079dffbd595daa8ea8626b99d2ab`;
- rebuilds the exact source-owned sapling;
- verifies the pinned source and mesh digests before export;
- converts the source mesh into strict UC surface input;
- publishes the exact GLB with UC `publish_glb()`;
- reopens the emitted bytes through UC `verify_glb()`;
- requires 2 primitives/materials and exact 620-triangle retention;
- retains the strict UC surface JSON, exact GLB bytes and one evidence receipt together.

## Truth boundary

A PASS proves only that this exact static Nature sapling can cross an explicit axis/winding/normal/material-group boundary into the pinned UC GLB path, while the planar leaf proof no longer depends on an unproven renderer-side two-sided flag.

It does **not** prove:

- final bark/leaf materials or shader quality;
- texture/UV quality;
- target-engine import or renderer culling behavior;
- visual/art-direction acceptance;
- wind/deformation/animation export;
- physical vegetation behavior;
- environment placement acceptance;
- runtime cost or LOD suitability;
- collision/gameplay behavior;
- CANON, production readiness, or Nature / Technical Art mastery.

VFX PR #2 remains a separate dynamic visual-response lane; this bridge exports the neutral static source only. Environment PR #4 remains the owner of scene composition. Universal Creation remains domain-neutral and does not gain Nature landmarks, branches, leaf-cluster policy, flex zones, or weather semantics from this lane.

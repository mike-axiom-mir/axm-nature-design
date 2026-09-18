# Materials Environment Context 001

Status: bounded Materials / LookDev receiving-context evidence only.

This evidence layer keeps the existing `sapling_material_profile_001` unchanged and asks one narrower question: does the already-proven woody/foliage material delta remain visible when the sapling is placed into the exact static Environment receiving context from `mike-axiom-mir/axm-map-design` head `d52cb54a2aeb3eb4f5668e3d6ba4b05ddcc02899`?

The proof preserves the Map seed-29 placement, path, building/nature/object proxies, Weather field and the existing fixed `path_eye` / `elevated_oblique` cameras. It does not import the active sapling wind response; movement is deliberately held at static neutral so motion and material evidence do not collapse into one comparison.

Both A/B renders use the already-proven Nature -> UC portable surface representation with explicit leaf backfaces (620 triangles). This differs from the Environment observation host's 570-triangle source mesh plus observation-only disabled culling, but the representation is identical between baseline and candidate; the only A/B difference is the two material families' color/roughness fields.

Provenance used by the evidence builder:

- Map receiving context: `mike-axiom-mir/axm-map-design@d52cb54a2aeb3eb4f5668e3d6ba4b05ddcc02899`;
- exact Map scene digest: `f63ddbb0fcdacd5109b45df1d0338701fb138014d3b98dc697d6279fd370447d`;
- exact Nature source used by Map: `fbc202449981f2bac153951c561ed0ed6120c936`;
- exact Weather source used by Map: `ca2eaba519e8449835b0ea6ef944b7080c3caa6a`;
- Map observation donor files: `tools/environment_eye_level.py` and `environment-proof/observe.gd` at the pinned Map head.

No explicit `LICENSE` file was present at that pinned Map head when this lane was created, so this reuse is recorded as same-owner campaign reuse with exact source provenance rather than silently asserting a license.

A PASS from this evidence means only that the exact context packet remains source-bound, the material-only A/B can be rendered in pinned Godot 4.7.2 GL Compatibility from both fixed Environment cameras, and the baseline/candidate images are not byte-identical. It does not decide whether the candidate is aesthetically better.

Not claimed: final bark/leaf lookdev, UVs or textures, botanical reflectance, moving-sapling shading, alpha/transmission/subsurface behavior, final Environment hierarchy, renderer equivalence, target-device performance, gameplay/runtime acceptance, Art Director acceptance, CANON, production readiness or Materials mastery.

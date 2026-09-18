# Rigging east/rear north-low parent-influence gate 007

## Scope

This successor answers one exact Rigging question returned by Organic Form: `north-low-branch-flex` overlaps the declared `trunk-upper-flex` envelope, but the authored neutral trunk cross-section at north-low's nearest attachment locus is still outside that trunk flex sphere.

The receiving rule is intentionally fail-closed: **do not silently parent north-low to the upper-trunk frame while that exact source relation remains disjoint.** The existing north-low child socket and its `[-5,+5]°` Rigging verification probe remain unchanged.

This is a diagnostic hierarchy/influence guard, not a production skin weight, plant biomechanics model, source-authored ROM, Animation decision, VFX/wind law, Technical-Art target-host adoption, Runtime policy or aesthetic acceptance.

## Exact identities

- Organic source owner: `fdc9d2b6ee729728551e22fd3eafa23ad60b6c7a`
- source digest: `178cd8cfb1a859bff411f60e13154109528062cf0ad2384b343d406cc0cc9d61`
- Geometry receiver: `9b451ba1f65281f550a6754e18574f7ab2951e28`
- migrated mesh digest: `aa9d450a78fef722672ea9af0f9aca98b4c1a0ca3705661784f5f61f3e9b6a31`
- Rigging predecessor: `6cf64925f0ea00737e4d3f2d4f15979c773f309d`
- Organic interaction donor: `925715d2f0491e2bcbc493b93dc6d14ab3dcb2a6`
- Organic interaction module blob: `be31e22283d43dcb4e6e8bda870760fa67ab1628`

## Exact source relation consumed

For `trunk-upper-flex` -> `north-low`:

- declared flex-envelope overlap: `0.028488310914984383 m`;
- nearest neutral trunk segment: `mid->upper`;
- neutral support margin after the branch-root radius: `0.040773804595473605 m`;
- upper-trunk-flex center -> nearest neutral attachment centerline: `0.33144612713000876 m`;
- neutral attachment cross-section -> upper-trunk-flex boundary signed gap: **`+0.009079537802862594 m`**.

The positive final value means the neutral attachment cross-section is about **9.08 mm outside** the declared upper-trunk flex sphere. Therefore `DECLARED_FLEX_ENVELOPE_OVERLAP` is not treated as permission to apply upper-trunk parent influence.

## Bounded Rigging constraint

`INTERSECTION_GATED_DIAGNOSTIC_ONLY`

- if the exact neutral attachment cross-section intersects the exact parent flex sphere, this gate must stop and be re-reviewed;
- on the current exact source it does not intersect, so north-low receives diagnostic upper-trunk parent weight `0.0`;
- the existing north-low pivot, source-derived axis, 52-vertex / 72-triangle child partition and `[-5,+5]°` child diagnostic remain unchanged;
- the upper-trunk diagnostic frame remains the existing source-derived frame with `[-2.5,+2.5]°` representatives only.

The zero is a verification receiver constraint, **not a production skinning value**.

## Representative proof

The verifier evaluates the 3 × 3 product witnesses:

- parent: `-2.5 / 0 / +2.5°`;
- north-low child: `-5 / 0 / +5°`.

Under the gate, parent commands map to identity for north-low, so each child pose is exactly invariant across the three parent commands and the existing child rigid-transform invariants remain intact. For contrast, the verifier also computes the explicitly forbidden counterfactual where north-low inherits the upper-trunk frame. At `±2.5°`, that counterfactual moves the north-low socket by about **14.46 mm**, so the gate prevents a materially different transform rather than a bookkeeping-only difference.

Because the gate maps every real parent command in `[-2.5,+2.5]°` to identity on north-low while the existing child motion remains a rigid Rodrigues rotation, the diagnostic composition is continuous for every real parent/child pair inside `[-2.5,+2.5]° × [-5,+5]°`.

## Reopen condition

This gate is not permanent policy. Reopen it if:

1. source or receiver evidence changes the exact north-low attachment relation; or
2. a separate Rigging/weighting owner supplies grounded influence evidence that justifies parent coupling despite the current source-space gap.

Do not mutate Organic source radii merely to make the gate pass differently.

## Non-claims

This result does not establish production skin weighting, botanical mechanics, branch/trunk surface attachment, stress or strength, simultaneous whole-tree deformation, continuous collision/self-intersection freedom, biological ROM, physical wind, Animation timing/interpolation/playback, Technical-Art target-host adoption, Runtime/controller/device behavior, Art Direction or Visual-QA acceptance, CANON or production/game readiness.

The four AXM roots remain the gate: Truth, Agency / non-domination, Continuity, Wisdom before speed.

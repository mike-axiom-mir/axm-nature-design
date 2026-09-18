# Organic east-rear neutral attachment / trunk-flex boundary evidence 006

## Scope

This bounded Organic Form pass does **not** reshape the east-rear tree and does not assign Rigging hierarchy, weights, constraints, ROM, physical wind, plant mechanics, runtime behavior or visual acceptance.

It extends the existing source-owned trunk/branch flex interaction classifier with one deformation-readiness question that remained ambiguous after the previous `ROOT_CENTER_CONTAINED / FLEX_ENVELOPE_OVERLAP_ONLY / DISJOINT` classification:

> When a declared branch flex envelope overlaps a declared trunk flex envelope, does that trunk flex envelope actually reach the authored neutral trunk cross-section at the branch's nearest attachment locus?

That distinction matters because metadata-envelope overlap alone can otherwise be mistaken for evidence that the parent trunk flex region geometrically reaches the neutral attachment body.

## Exact source boundary

Source/form owner remains the existing Organic source commit:

`fdc9d2b6ee729728551e22fd3eafa23ad60b6c7a`

Source digest remains:

`178cd8cfb1a859bff411f60e13154109528062cf0ad2384b343d406cc0cc9d61`

No source JSON, trunk point, branch point, radius, flex-zone declaration, generated mesh, Geometry receiver, Rigging transform, Animation timing, VFX response, Technical-Art transport, Runtime representation or Map placement changes in this pass.

## New measured relation

For each exact trunk-flex / branch-root pair, the observer already finds the branch root's nearest neutral trunk support point and interpolated local trunk radius. It now also measures:

`distance(trunk_flex_center, nearest_neutral_attachment_centerline_point) - trunk_flex_radius - local_trunk_radius`

Interpretation is strictly geometric and source-local:

- `<= 0`: the declared trunk-flex sphere intersects the neutral trunk cross-section at that attachment locus;
- `> 0`: the two are spatially disjoint by that signed gap.

This is **not** a weight field, influence map, joint assignment, deformation quality result, collision result, tissue model or biological claim.

## Current exact result

Across the same exact `2 trunk flex × 5 branch roots = 10` pairs:

- neutral attachment cross-section intersections: **1**;
- neutral attachment cross-section disjoint pairs: **9**.

The only intersecting pair is:

`trunk-upper-flex ↔ east-mid`

This sharpens the previous source-space distinction between `east-mid` and `north-low`.

### North-low

Existing declaration relation:

- class: `FLEX_ENVELOPE_OVERLAP_ONLY`;
- upper-trunk flex radius: `0.22 m`;
- north-low branch-flex radius: `0.14 m`;
- declared flex-envelope overlap margin: `0.028488310914984383 m`.

Neutral attachment relation:

- nearest trunk segment: `mid->upper`;
- nearest segment parameter: `0.5877803557617942`;
- nearest attachment centerline point: approximately `[-0.01114462, 0.00351121, 2.02022428] m`;
- local authored trunk radius: `0.10236658932714617 m`;
- upper-trunk-flex center -> attachment centerline distance: `0.33144612713000876 m`;
- neutral attachment cross-section to upper-trunk-flex boundary signed gap: **`+0.009079537802862594 m`**.

Therefore the declared north-low branch-flex envelope overlaps the upper-trunk flex envelope, while the actual authored neutral trunk cross-section at north-low's nearest attachment remains about **9.08 mm outside** the upper-trunk flex sphere.

North-low still has positive neutral branch-root support margin `0.040773804595473605 m`. The new measurement does not turn that support into deformation evidence.

### East-mid

Existing declaration relation:

- class: `ROOT_CENTER_CONTAINED_IN_TRUNK_FLEX`;
- root-center containment margin: `0.11369854187265342 m`;
- declared flex-envelope overlap margin: `0.23369854187265338 m`.

Neutral attachment relation:

- nearest trunk segment: `upper->crown`;
- local authored trunk radius: `0.08616457461645745 m`;
- upper-trunk-flex center -> attachment centerline distance: `0.10270063195882467 m`;
- neutral attachment cross-section to upper-trunk-flex boundary signed gap: **`-0.2034639426576328 m`**.

So east-mid's neutral attachment trunk cross-section intersects the declared upper-trunk flex sphere by about **203.46 mm** under this source-space sphere/cross-section relation.

This remains source geometry only. It does not validate Rigging's hierarchy beyond Rigging's own exact evidence.

## Sensitivity control

The observer is not hardcoded to the current answer. A verifier-only mutation of `trunk-upper-flex` radius from `0.22 m` to `0.23 m` moves north-low's neutral attachment relation across the geometric boundary:

- current signed gap: `+0.009079537802862594 m` — disjoint;
- mutated signed gap: approximately `-0.0009204621971374144 m` — intersecting.

The count becomes `2` intersecting attachment pairs under that test mutation.

That controlled mutation is **not** a source recommendation and does not authorize changing the authored flex radius.

## Handoff rule

`DECLARED_FLEX_ENVELOPE_OVERLAP != NEUTRAL_ATTACHMENT_CROSS_SECTION_REACH`

Downstream Rigging may consume this exact source relation as evidence input, but Organic does not choose parent hierarchy or weights from it. In particular, the existing east-mid contained-root parent-frame result must not be transferred to north-low merely because their declared flex envelopes overlap.

A future north-low hierarchy/weighting experiment should bind its own exact Rigging policy to the exact source evidence and remain free to reject this geometric relation as insufficient for deformation semantics.

## Truth boundary

This pass establishes only exact neutral source-space geometry/provenance for the existing authored tree. It does **not** establish botanical correctness, biological attachment mechanics, tissue behavior, trunk/branch strength, physical flex radius, stiffness, valid ROM, skinning/weights, deformation quality, continuous collision/self-intersection freedom, physical wind, Animation quality, target-host/runtime/device readiness, Art/QA acceptance, CANON, production readiness, game readiness, or Organic mastery.

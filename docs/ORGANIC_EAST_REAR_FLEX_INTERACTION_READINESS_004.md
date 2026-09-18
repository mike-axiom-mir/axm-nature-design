# Organic east-rear flex interaction readiness 004

## Scope

This is an additive Organic Form source-readiness observation for the existing east/rear tree. It does not reshape the tree and does not change any authored flex declaration. Its purpose is to make one source-owned relationship explicit before any future trunk-plus-branch deformation hierarchy is authored.

Exact source/form owner remains `fdc9d2b6ee729728551e22fd3eafa23ad60b6c7a` with source digest `178cd8cfb1a859bff411f60e13154109528062cf0ad2384b343d406cc0cc9d61`. The historical generated mesh remains `390v / 570t` with digest `d7fc5deaa1c12d1d8c7d7b6dc95bf1e8544ce26140ee2e4a7d2c67a2c4133e48`.

No source JSON, trunk/branch/leaf position, radius, flex-zone center/radius/status, generated mesh, Geometry receiver, Rigging pivot/axis/partition, Animation curve, VFX response, Technical-Art transport, Runtime representation or world placement changes in this pass.

## Bounded question

The source already declares two trunk flex envelopes and five exact branch-root flex envelopes, all explicitly `DECLARED_NOT_DEFORMATION_TESTED`.

Before a future specialist composes trunk motion with the existing five branch sockets, Organic asks only:

> Which declared trunk-flex spheres and branch-root-flex spheres overlap in the authored neutral source, and does any exact branch-root center lie inside a declared trunk-flex sphere?

This is metadata geometry, not a deformation test.

## Exact neutral-space interaction map

The observer evaluates `2 trunk flex zones × 5 branch-root flex zones = 10` exact pairs.

`trunk-lower-flex` is separated from all five declared branch-root flex envelopes. It contains no primary branch-root center.

`trunk-upper-flex` has two declared envelope overlaps:

- `north-low`: trunk/branch center distance `0.3315116890850156 m`; the branch root center is outside the `0.22 m` trunk-flex radius, while the `0.22 + 0.14 m` declared flex envelopes overlap by `0.028488310914984383 m` (~28.49 mm).
- `east-mid`: trunk/branch center distance `0.10630145812734658 m`; the exact branch root center lies inside the `0.22 m` trunk-flex envelope by `0.11369854187265342 m`, and the `0.22 + 0.12 m` declared flex envelopes overlap by `0.23369854187265338 m`.

The other three upper-trunk pairs do not overlap under the declared neutral spheres.

Scoped result:

`PASS_DECLARED_TRUNK_BRANCH_FLEX_INTERACTION_MAP__DEFORMATION_UNTESTED`

## Why this matters

The existing five-branch Rigging/Animation/VFX work can remain exactly true for its own branch-only composition while trunk deformation remains untested. But a later trunk-plus-branch system must not silently assume that the source declarations are independent: the upper-trunk declaration spatially intersects two branch flex declarations and contains the exact `east-mid` branch root center.

This pass therefore hands downstream Rigging one explicit question rather than one prescription: choose and test an exact hierarchy/influence/composition policy before combining trunk and branch deformation. Organic does not decide parent order, weights, constraints, stiffness, physical wind, collision or valid motion range.

The measured overlaps are not labelled defects. Overlapping source envelopes may be intentional and may be handled cleanly by a future hierarchy. The observer records the relationship so that later work cannot unknowingly double-apply or reinterpret the same source region without evidence.

## Fail-closed / sensitivity evidence

The exact current-source pair identities and measurements are retained by unit tests and the Organic workflow. A verifier-only source copy can reduce `trunk-upper-flex` from `0.22 m` to `0.10 m` while still enclosing its authored `0.09 m` trunk cross-section; the interaction observer then changes from `1` contained root / `2` envelope overlaps to `0` contained roots / `1` envelope overlap. That proves this map is measuring the declared source relationship rather than returning a fixed label.

Existing fail-closed gates for missing branch flex coverage, missing trunk flex coverage, shifted trunk-flex centers, undersized trunk envelopes, detached branch roots and promoted deformation status remain intact.

## Handoff boundary

Organic retains source form and flex-metadata authority. Geometry retains topology and finite intersection evidence. Procedural retains exact child-selection identities. Rigging owns any future trunk pivot/axis/weights/hierarchy and trunk+branch composition. Animation owns timing/playback. VFX/Weather own visual response semantics. Technical Art owns target-host transport. Runtime owns representation/device behavior. Art Direction and Visual QA own perceptual acceptance.

A future trunk deformation lane should consume the exact interaction map rather than treating the two trunk zones and five branch zones as seven unrelated declarations. Existing branch-only PASSes remain truthful for their exact domains and do not become trunk-plus-branch evidence automatically.

## Truth boundary

This result does **not** establish botanical or biological correctness, tissue mechanics, branch/trunk strength, physical flex radius, stiffness, parent-child deformation hierarchy, skinning/weights, valid plant ROM, physical wind, continuous collision or self-intersection freedom, Animation quality, target-host/runtime/device readiness, Art/QA acceptance, CANON, production readiness, game readiness or Organic Form mastery.

The four AXM roots remain the merge gate: Truth, Agency / non-domination, Continuity, Wisdom before speed.

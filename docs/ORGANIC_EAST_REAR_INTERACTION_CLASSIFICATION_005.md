# Organic east-rear trunk/branch interaction classification 005

## Scope

This is an additive Organic Form deformation-readiness observation on the existing east/rear Nature tree. It does not reshape the tree, alter a flex declaration, choose a rig hierarchy, or claim deformation quality.

Exact source/form owner remains `fdc9d2b6ee729728551e22fd3eafa23ad60b6c7a` with source digest `178cd8cfb1a859bff411f60e13154109528062cf0ad2384b343d406cc0cc9d61`. The historical Organic mesh remains `390v / 570t` at digest `d7fc5deaa1c12d1d8c7d7b6dc95bf1e8544ce26140ee2e4a7d2c67a2c4133e48`.

The immediate source-readiness predecessor is Organic head `f8d103a9f0a1e457539919a45c605c1edb8b9a7f`, which proved the exact `2 trunk flex × 5 branch flex = 10` neutral interaction map.

## Fresh downstream trigger

Nature Rigging PR #14 has now consumed the contained `trunk-upper-flex ↔ east-mid` relation at exact head `6cf64925f0ea00737e4d3f2d4f15979c773f309d` and proved one bounded parent-frame rebase diagnostic for that exact child. Rigging explicitly leaves the separate `trunk-upper-flex ↔ north-low` overlap unresolved because north-low's root center is outside the trunk flex radius.

Organic therefore sharpens only the source-owned distinction that downstream work now needs. It does not copy the east-mid hierarchy rule onto north-low.

## New exact interaction classes

Schema:

`axm.nature-trunk-branch-flex-interaction-classification/v0.1`

Scoped result:

`PASS_EXACT_TRUNK_BRANCH_FLEX_INTERACTION_CLASSES__DEFORMATION_UNTESTED`

Every exact trunk-flex / branch-root-flex pair is assigned one neutral-source geometry class:

1. `ROOT_CENTER_CONTAINED_IN_TRUNK_FLEX`
2. `FLEX_ENVELOPE_OVERLAP_ONLY`
3. `DISJOINT`

Current exact counts across all ten pairs:

- root-center contained: `1`
- flex-envelope overlap only: `1`
- disjoint: `8`

The only root-center-contained pair is:

`trunk-upper-flex ↔ east-mid-branch-flex`

The only overlap-only pair is:

`trunk-upper-flex ↔ north-low-branch-flex`

No classification is a rig policy, weighting rule, collision verdict, tissue model, or biological claim.

## Why north-low is not east-mid

### North-low — envelope overlap only

Exact upper-trunk-flex to north-low-root center distance:

`0.3315116890850156 m`

The root center is **outside** the `0.22 m` upper-trunk flex radius by:

`0.1115116890850156 m`

The declared `0.22 m + 0.14 m` flex envelopes nevertheless overlap by:

`0.028488310914984383 m`

Independent neutral source attachment remains positive:

- nearest authored trunk segment: `mid->upper`
- nearest segment parameter: `0.5877803557617942`
- root-centerline distance: `0.006592784731672557 m`
- local authored trunk radius: `0.10236658932714617 m`
- branch root radius: `0.055 m`
- full-root neutral support margin: `0.040773804595473605 m`

This says the branch root is well supported by the authored neutral trunk while only the **declared flex envelopes** overlap. It does not say how that overlap should deform.

### East-mid — root center contained

For comparison, `east-mid` is materially different:

- upper-trunk-flex to root-center distance: `0.10630145812734658 m`
- root center lies inside the `0.22 m` upper-trunk flex radius by `0.11369854187265342 m`
- declared flex-envelope overlap: `0.23369854187265338 m`
- nearest authored trunk segment: `upper->crown`
- full-root neutral support margin: `0.009731379482495778 m`

That difference is exactly why an east-mid parent-frame diagnostic must not silently become a north-low policy.

## Sensitivity / fail-closed evidence

A verifier-only copy reducing `trunk-upper-flex` from `0.22 m` to `0.10 m` changes the class distribution to:

- contained: `0`
- overlap only: `1`
- disjoint: `9`

Under that controlled mutation north-low becomes `DISJOINT` while east-mid becomes `FLEX_ENVELOPE_OVERLAP_ONLY`. The observer therefore measures source relationships rather than emitting fixed labels.

The classifier also fails closed when exact branch-root flex coverage is missing or when any flex declaration is promoted beyond `DECLARED_NOT_DEFORMATION_TESTED`.

## Handoff rule

`FLEX_ENVELOPE_OVERLAP_ONLY != ROOT_CENTER_CONTAINMENT__DOWNSTREAM_HIERARCHY_POLICY_MUST_BIND_EXACT_INTERACTION_CLASS__NO_POLICY_TRANSFER_BY_OVERLAP_ALONE`

Rigging owns any future north-low hierarchy, weighting, constraints, parent-frame policy, or diagnostic interval. Organic supplies only the exact source relation and neutral attachment facts.

Existing east-mid Rigging evidence remains truthful for its exact domain. It does not transfer to north-low by similarity.

## Truth boundary

This result does **not** establish botanical or biological correctness, tissue mechanics, branch/trunk strength, physical flex radius, stiffness, hierarchy/weights, production skinning, valid plant ROM, wind physics, collision/self-intersection freedom, Animation quality, target-host/runtime/device readiness, Art/QA acceptance, CANON, production readiness, game readiness, or Organic Form mastery.

The four AXM roots remain the merge gate: Truth, Agency / non-domination, Continuity, Wisdom before speed.

# Rigging east/rear upper-trunk -> east-mid hierarchy 006

## Scope

This is one bounded Rigging / Deformation successor on the existing Nature Rigging PR #14 lane.

Organic Form now proves a source-owned neutral interaction that the earlier branch-only Rigging work did not consume: the exact `east-mid` branch-root flex center lies inside the exact `trunk-upper-flex` declaration. Organic explicitly leaves hierarchy, weights, constraints, pivots, axes and angle policy to Rigging. This pass answers only the smallest hierarchy question before anyone attempts trunk skinning or combined plant motion.

`axm-create-me` remains coordination-only. Product/evidence implementation remains in `mike-axiom-mir/axm-nature-design`.

## Exact lineage

Preserved owner identities:

- Organic source owner: `fdc9d2b6ee729728551e22fd3eafa23ad60b6c7a`
- source digest: `178cd8cfb1a859bff411f60e13154109528062cf0ad2384b343d406cc0cc9d61`
- current Organic readiness donor: `f8d103a9f0a1e457539919a45c605c1edb8b9a7f`
- exact source JSON blob: `fb12b759e1abfd0455bf46fd39a0eba27095796b`
- exact Organic readiness module blob: `0e787e5724c29878a86a425b43a39d5120bf1086`
- exact Organic interaction document blob: `d103856df817d1b3c3ea7938fe8ac4067d7de0c9`
- Geometry receiver: `9b451ba1f65281f550a6754e18574f7ab2951e28`
- migrated mesh digest: `aa9d450a78fef722672ea9af0f9aca98b4c1a0ca3705661784f5f61f3e9b6a31`
- Rigging predecessor: `b4b480b415047fea90b4740f7702ced0dba9142d`

No source geometry, source flex metadata, Geometry receiver, existing east-mid branch socket, five-socket shared-driver composition, Animation, VFX, Technical Art or Runtime implementation is rewritten.

## Fresh source-owned interaction consumed

Organic's exact current interaction map records:

- `trunk-upper-flex` center: `[-0.04, 0.02, 2.35] m`
- `trunk-upper-flex` radius: `0.22 m`
- `east-mid-branch-flex` center: `[-0.01, 0.0, 2.45] m`
- `east-mid-branch-flex` radius: `0.12 m`
- center distance: `0.10630145812734658 m`
- east-mid root-center containment margin inside upper-trunk flex: `0.11369854187265342 m`
- declared flex-envelope overlap margin: `0.23369854187265338 m`
- both source statuses remain `DECLARED_NOT_DEFORMATION_TESTED`

`north-low` also has a declared envelope overlap with `trunk-upper-flex`, but its root center is outside the trunk flex radius. This pass deliberately leaves that separate policy unresolved.

## Bounded Rigging constraint

The parent frame uses the exact source `upper` trunk point as pivot.

Its diagnostic bend-plane axis is derived only from source geometry:

`normalize(cross(normalize(upper - mid), normalize(crown - upper)))`

The parent diagnostic interval is exactly `[-2.5,+2.5] degrees`, with representatives `-2.5 / 0 / +2.5`. This interval is a Rigging verification probe only. It is not inferred from the `0.22 m` flex radius and is not source or biological ROM.

The child is the already-proven exact `east-mid` socket from the five-primary-branch Rigging family. Its pivot, axis, `52` selected vertices, `72` selected triangles and existing `[-5,+5] degree` diagnostic interval are not changed.

The only new Rigging rule is:

**transport the child pivot and child axis through the parent trunk frame before applying the existing child-local rotation.**

## Continuous proof

For every real parent angle in `[-2.5,+2.5]`:

1. parent motion is one rigid Rodrigues rotation around the exact upper-trunk pivot;
2. therefore the parent-pivot -> east-mid-socket distance is invariant;
3. therefore the exact source-owned east-mid containment margin and declared flex-envelope overlap margin are invariant;
4. the child pivot and child axis are transported by the same rigid parent transform.

For every real child angle in the existing `[-5,+5]` interval:

1. the child uses its unchanged rigid Rodrigues rotation around the transported socket frame;
2. pairwise child distances remain invariant;
3. child-axis projection remains invariant;
4. rigid-transform conjugation proves:
   `parent(child_local(neutral)) == child_about_transported_frame(parent(neutral))`.

The proof therefore covers the complete closed parent x child diagnostic product domain, while retained representative witnesses remain `3 x 3 = 9` poses.

A fail-closed negative deliberately applies the child rotation after parent motion around the **stale neutral child pivot/axis**. Nonzero parent + child witnesses must diverge by more than `1e-6 m`, proving that the hierarchy rebase is not a no-op bookkeeping label.

## Truth boundary

This proves a parent-frame -> child-socket kinematic rebase constraint only.

It does **not** prove:

- trunk mesh deformation or trunk skin weights;
- branch/trunk surface attachment, seam quality or blended weighting;
- the separate `north-low` overlap policy;
- simultaneous trunk plus five-branch motion;
- continuous collision or self-intersection freedom;
- plant biomechanics, stiffness, stress, strength or physical wind;
- source or biological range of motion;
- Animation timing, interpolation, looping or playback;
- Technical Art target-host transport;
- Runtime controller, device or performance acceptance;
- final Art Direction or independent Visual QA acceptance;
- CANON or production readiness.

The four AXM roots remain the merge gate: **Truth, Agency / non-domination, Continuity, Wisdom before speed**.

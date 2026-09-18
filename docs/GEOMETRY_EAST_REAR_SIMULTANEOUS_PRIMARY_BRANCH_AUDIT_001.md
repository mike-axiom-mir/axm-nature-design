# Geometry — east/rear simultaneous primary-branch audit 001

## Why this lane exists

Nature Rigging PR #14 proves five exact rigid-child root sockets independently on the current Geometry-migrated east/rear tree receiver. Each child owns 52 generated vertices / 72 triangles in its own single-branch probe, and the five selected vertex sets are pairwise disjoint. Rigging explicitly leaves simultaneous multi-branch motion and collision/self-intersection unproven.

Geometry therefore does not invent a new source, rig, motion clip or wind rule. This lane asks the smallest structural receiving question that must be answered before anyone treats five independent socket PASSes as one simultaneous deformation surface.

## Reusable rule

`PAIRWISE_VERTEX_DISJOINT_RIGID_CHILDREN_REQUIRE_TRIANGLE_CLOSURE_AND_ORDER_INVARIANT_COMPOSITION_BEFORE_SIMULTANEOUS_DEFORMATION_REVIEW`

Pairwise-disjoint vertex ownership is necessary but not sufficient. Geometry independently checks whether triangles cross child ownership boundaries, whether the five transforms commute on the exact receiver, and whether the globally fixed receiver and exact pivot vertices remain fixed when all five children are posed at once.

## Exact lineage

- Organic source owner PR #8: `fdc9d2b6ee729728551e22fd3eafa23ad60b6c7a`.
- Geometry migrated receiver PR #9: `9b451ba1f65281f550a6754e18574f7ab2951e28`.
- Migrated mesh digest: `aa9d450a78fef722672ea9af0f9aca98b4c1a0ca3705661784f5f61f3e9b6a31`.
- Rigging parent PR #14: `898529f602893c8f6be179bd3e9b6821fc099904`.
- Shared read-only UC observer: `mike-axiom-mir/axm-universal-creation@ce70d717e381df6ca8a27c0c9fabe9d48bb1b23c`, `src/axm_uc/mesh_self_intersection.py`.

No inherited source/Rigging file is edited by this Geometry branch.

## Bounded witness family

The Geometry evaluator re-runs the exact five-socket Rigging prerequisite, rebuilds the exact 390-vertex / 570-triangle migrated receiver, and then evaluates one exact neutral state plus all 32 simultaneous corner combinations formed by assigning each of the five branches either `-5°` or `+5°` from the existing Rigging diagnostic interval.

Every child transform is evaluated from the same neutral receiver. Canonical branch order and reverse branch order are compared directly. The evaluator also audits triangle ownership against the five selected vertex sets and records the globally fixed vertex set.

## Verified structural result

The exact receiver partitions cleanly into five child-owned triangle groups of 72 triangles each plus 210 globally fixed triangles. The five child selections contain 260 unique selected vertices total, leaving 130 globally fixed vertices. There are zero partial-selection triangles and zero triangles crossing two child owners. Across all 33 witnesses, canonical-vs-reverse composition delta is exactly `0.0 m`, globally fixed drift is `0.0 m`, and pivot drift is `0.0 m`.

That proves the five exact rigid-child transforms compose deterministically on this receiver without index-ownership ambiguity. It does not by itself prove geometric clearance.

## Self-intersection observer scope correction

An initial whole-receiver observer attempt produced roughly 1705–1707 nonadjacent-triangle intersections per witness. That result was not promoted into a simultaneous-motion verdict: the Nature receiver intentionally contains many disconnected authored components that meet spatially, so a whole-body count mixes pre-existing attachment contacts with any possible new child-child contact. The same early retained run also exposed an evidence-packaging bug where the copied contract reused the receipt filename; that run was kept as failed evidence and the packaging path was corrected rather than relabelled as PASS.

The accepted method therefore stays narrower and attribution-safe. For each witness and each of the 10 unordered branch pairs, UC observes the 72-triangle left child, the 72-triangle right child, and their 144-triangle combination. The exact cross-child count is `combined - left_solo - right_solo`. This yields 330 branch-pair/state observations across the 33-witness family without copying UC's triangle-intersection algorithm into Nature.

The accepted evidence reports **zero cross-branch nonadjacent-triangle intersections in all 330 pair/state observations**. The observer work identities are 2,556 unordered checks per 72-triangle solo child and 10,296 per 144-triangle two-child combination. A separate full-receiver one-pair-short budget control (`162,164` requested vs `162,165` required) returns HOLD before scanning and exposes no partial intersection verdict.

## Truth boundary

This is a finite structural witness family, not a continuous five-dimensional deformation proof. Zero child-child intersections at neutral plus all 32 extreme corners does not prove every interior angle combination clear. This lane also does not establish child-versus-fixed-receiver clearance, adjacent foldover/contact, physical collision, stress, branch attachment strength, biological motion, Animation/VFX timing, target-host playback, target-device fitness, final visual quality, CANON, production readiness, game readiness or Geometry mastery.

Organic keeps source/form authority. Rigging keeps pivots, axes and diagnostic articulation authority. Geometry owns only this bounded composition/topology evidence. UC remains a neutral read-only observer and gains no Nature-specific policy.

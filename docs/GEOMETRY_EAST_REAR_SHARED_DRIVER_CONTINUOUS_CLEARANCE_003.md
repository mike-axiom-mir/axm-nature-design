# Geometry — East/Rear Shared-Driver Continuous Cross-Branch Clearance 003

## Scope

This Geometry successor consumes the exact continuous one-parameter Rigging owner at `b4b480b415047fea90b4740f7702ced0dba9142d` without changing the Organic source, migrated Geometry receiver, five Rigging pivots/axes, child partitions, shared sign map, or diagnostic interval.

The prior Geometry lane at `3197eba862a6b7e6e93098a5b98d2c91bf48d32a` proves only five exact static shared-driver witnesses and explicitly refuses to promote those finite observations to a continuous clearance claim. This successor answers that exact held Geometry question with a separate interval certificate.

Reusable rule:

`CONTINUOUS_ONE_PARAMETER_RIGID_CHILD_COMPOSITION_REQUIRES_FULL_INTERVAL_SEPARATION_CERTIFICATES__FINITE_STATIC_WITNESSES_DO_NOT_TRANSFER`

## Exact structural family

The unchanged receiver remains:

- 390 vertices;
- 570 triangles;
- five primary branch children;
- 52 selected vertices / 72 owned triangles per child;
- 260 selected vertices total;
- 130 globally fixed vertices;
- 10 unordered child pairs;
- 51,840 exact cross-branch triangle-pair trajectories.

The exact shared Rigging parameter remains `u in [-5,+5] degrees`, with the existing mixed sign map owned by Rigging.

## Continuous proof method

The certificate does not sample the interval and does not infer continuity from the earlier `-5/-2.5/0/+2.5/+5` states.

For each exact cross-branch triangle pair:

1. evaluate the two triangles at neutral;
2. construct deterministic proof-safe separating-axis candidates from triangle normals, edge cross-products, and coplanar edge-normal candidates;
3. keep the largest positive neutral projection gap found on any candidate axis;
4. for each triangle, compute the maximum perpendicular radius of its vertices from that child's exact Rigging axis;
5. bound every point of that rigid triangle over the full owner interval by the rotation chord bound:

   `delta_triangle <= 2 * r_max * sin(5deg / 2)`;

6. require the neutral separating-axis margin to be greater than the sum of both triangles' full-interval motion bounds plus the Geometry epsilon.

Why this is sufficient: once a fixed world-space axis separates two neutral triangles by margin `m`, and every point of each triangle can move by at most `d_left` and `d_right`, the projection gap on that same fixed axis can shrink by at most `d_left + d_right`. If `m > d_left + d_right`, the pair cannot meet anywhere in the closed interval.

The distance-to-axis norm is convex across a triangle, so the maximum radial distance occurs at a vertex; using the maximum vertex radius therefore bounds the whole rigid triangle rather than just its corners.

No receiver rewriting, collision proxy, epsilon welding, temporal interpolation, or UC policy is introduced.

## Acceptance boundary

PASS requires all 51,840 cross-branch triangle-pair trajectories to receive a positive full-interval certificate. A work budget below the exact root family size fails closed before scanning and exposes no partial clearance verdict.

The certificate is deliberately narrower than physical collision. It proves source-space cross-branch triangle separation under the exact current rigid Rigging field only.

It does **not** prove:

- child-versus-fixed-receiver clearance;
- child internal self-intersection quality;
- intended contact at branch attachments;
- adjacent foldover/contact freedom at attachment seams;
- branch stress, stiffness, strength, or botanical plausibility;
- that the diagnostic interval is source or biological ROM;
- Animation timing/playback quality;
- physical wind;
- target-host transport or Godot playback;
- Runtime/device behavior;
- physics/gameplay collision suitability;
- Art Direction or Visual QA acceptance;
- automatic source/receiver adoption;
- CANON, production readiness, game readiness, or Geometry mastery.

## Ownership / provenance

- Organic source remains owned by its existing Nature Organic lane.
- Geometry owns only this structural interval certificate.
- Rigging owns pivots, axes, child partitions, sign mapping and the `[-5,+5]` diagnostic parameter field.
- Animation owns timing and playback semantics.
- VFX owns visual-response semantics.
- Technical Art owns target-host transport.
- Runtime owns controller/device behavior.
- `axm-create-me` remains coordination only.

Truth, Agency / non-domination, Continuity, and Wisdom before speed remain the merge gate.

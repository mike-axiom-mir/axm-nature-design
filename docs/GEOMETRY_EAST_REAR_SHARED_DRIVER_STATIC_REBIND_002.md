# Geometry — east/rear shared-driver static rebind 002

## Why this exists

Geometry PR #18 previously proved the neutral receiver plus all 32 independent
`±5°` five-branch corner combinations. That evidence deliberately stopped before
every interior angle combination.

Rigging PR #14 later introduced an exact shared diagnostic command with mixed
per-socket sign multipliers, and VFX PR #19 retained five *static* simultaneous
review poses at `-5 / -2.5 / 0 / +2.5 / +5°`. Three of those poses (both endpoints
and neutral) overlap the older Geometry witness family. The two `±2.5°` states do
not. Their VFX PASS therefore cannot inherit the old Geometry intersection result.

## Reusable rule

`DOWNSTREAM_STATIC_SHARED_DRIVER_INTERIOR_WITNESSES_REQUIRE_EXACT_GEOMETRY_REBIND_BEFORE_INTERSECTION_PASS_TRANSFER`

When a downstream owner turns an existing deformation range into a new exact set
of static simultaneous witness poses, Geometry replays that exact set rather than
assuming an endpoint/corner proof covers the interior.

## Exact bounded method

This lane:

1. preserves Geometry PR #18 as the owning lane;
2. consumes Rigging `754797a8...` and VFX `ba1c12dd...` as exact read-only donors;
3. rejects donor semantic drift, witness-set drift, motion promotion and continuous-
   interval promotion;
4. replays the unchanged five source-owned pivots, axes and 52-vertex partitions;
5. proves canonical/reverse composition, fixed vertices and pivots remain exact;
6. confirms exactly three poses overlap prior Geometry evidence and exactly two are
   new interior poses;
7. uses merged UC `mesh_self_intersection.py` read-only;
8. observes every unordered branch pair at each of the five exact static poses using
   the same attribution-safe `combined - left_solo - right_solo` method as PR #18;
9. keeps child-vs-fixed receiver clearance, adjacent contact/foldover, continuous
   motion and physical collision outside the claim.

No Organic source, Geometry receiver mesh, Rigging owner geometry, VFX response
semantics, Animation, Technical Art, Runtime or UC product code is changed.

## Truth boundary

A green result proves only the exact five static shared-driver witnesses and exact
child-child nonadjacent-triangle observations. It does not prove the continuous
`[-5,+5]°` shared-driver interval, simultaneous motion, child-vs-fixed receiver
clearance, adjacent foldover/contact, physical collision, biological ROM, target-host
playback, Runtime/device fitness, gameplay, final visual quality, CANON, production
readiness, game readiness or Geometry mastery.

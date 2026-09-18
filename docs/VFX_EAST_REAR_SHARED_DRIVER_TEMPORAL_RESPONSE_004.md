# VFX east-rear shared-driver temporal response 004

Status: bounded review candidate. No automatic adoption.

This VFX successor stacks directly on Nature Animation PR #22 exact head `bfb66da82bc358b14e52711bbdef7b58e4c943af`, which is green for the exact `1.0 s / 40 Hz / 41 endpoint-inclusive samples` simultaneous five-socket diagnostic loop over Rigging PR #14 head `b4b480b415047fea90b4740f7702ced0dba9142d`.

The exact Weather visual-direction donor remains `mike-axiom-mir/axm-weather-design` PR #2 head `ca2eaba519e8449835b0ea6ef944b7080c3caa6a`, source blob `11298d447f262da8a78e43e2df68bc0346c99a2c`, `wind_xy=[1.0,0.35]`, semantics `VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED`.

## Bounded improvement

The previous VFX static response envelope proved five representative simultaneous poses against the Weather visual direction. Animation has since authored and verified the full sampled loop. This pass does not invent another motion curve. Instead it measures the exact current Animation receiver at all 41 samples in a Weather-aligned visual frame and produces a retained temporal review surface.

For every sample it derives each branch centroid and the combined 260-vertex family centroid from the actual generated geometry, then records:

- displacement parallel to the exact Weather visual direction;
- displacement perpendicular to that visual direction in XY;
- vertical displacement;
- whether the parallel response sign agrees with the shared diagnostic driver.

The gate requires every branch and the selected family to reverse coherently with the existing shared driver, and requires exact neutral response at `0.00 / 0.50 / 1.00 s`. Cross-direction and vertical motion are measured but are deliberately **not** required to be zero: the five source-derived Rigging axes are different, and suppressing those components would silently redesign Rigging.

## Ownership boundary

This is VFX-side temporal visual-direction evidence only. Animation keeps timing/cadence/motion authorship. Rigging keeps pivots, axes, child partitions, polarity and diagnostic interval. Weather keeps the source visual-direction semantics. Technical Art owns target-host deformation/playback transport. Runtime owns controller/device behavior. Art Direction and independent Visual QA own appearance acceptance.

A green result does **not** establish natural vegetation motion, physical wind force/speed/turbulence, biological range of motion, continuous collision/self-intersection freedom, Godot/target-host playback, target-device performance, gameplay, final visual quality, CANON or production readiness.

`axm-create-me` remains coordination-only. Truth, Agency / non-domination, Continuity and Wisdom before speed remain the merge gate.

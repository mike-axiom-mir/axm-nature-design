# VFX east/rear upper-trunk -> east-mid Weather-direction hierarchy 005

## Scope

This is one bounded VFX / Atmosphere receiving review on the exact Nature Rigging upper-trunk -> `east-mid` hierarchy. It does not author a new motion curve or physical wind model.

The previous VFX sign map proved that, with the parent trunk neutral, local `east-mid +5°` moves the exact generated child farther along Weather's source-owned visual direction `[1.0, 0.35]` than `-5°`. Rigging has since added a source-derived parent trunk frame that transports the child pivot and axis through a diagnostic `[-2.5,+2.5]°` parent interval. The smallest VFX question is whether that prior world-space visual-direction polarity remains stable after the parent-frame transport.

## Exact donors

- Rigging PR #14 exact hierarchy head: `6cf64925f0ea00737e4d3f2d4f15979c773f309d`.
- Rigging result: `PASS_UPPER_TRUNK_EAST_MID_PARENT_CHILD_SOCKET_REBASE_CONTINUOUS_PRODUCT_DOMAIN_DIAGNOSTIC`.
- VFX sign predecessor PR #17 exact head: `ef7b35af27d5ca98a6447c1e33be07863e387305`.
- Weather PR #2 exact head: `ca2eaba519e8449835b0ea6ef944b7080c3caa6a`.
- Weather source blob: `11298d447f262da8a78e43e2df68bc0346c99a2c`.
- Weather semantics: `VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED`.

## Measurement

For each exact parent representative `-2.5 / 0 / +2.5°`, the verifier evaluates child `-5 / 0 / +5°` using Rigging's transported child pivot/axis. Child response is measured **incrementally from the same-parent neutral child centroid**. That separation prevents parent-only socket travel from being misreported as child downwind response.

The neutral-parent row must reproduce the exact PR #17 east-mid VFX evidence before the hierarchy successor can pass. The result is then allowed to PASS only if all three parent representatives retain the same positive child polarity and the signed witnesses remain separable.

The generated SVG is a review surface over centroid vectors derived from exact generated geometry. It is not a target-host render or aesthetic approval.

## Authority boundary

Rigging retains parent/child pivots, axes, intervals and hierarchy composition. Weather retains visual-direction semantics. Animation retains timing/playback. Technical Art retains target-host transport. Runtime retains controller/device/performance. Art Direction and independent Visual QA retain appearance acceptance.

A PASS does not establish physical wind, wind strength/force/drag/turbulence, plant biomechanics or biological ROM, whole-tree simultaneous motion, continuous collision/self-intersection, Animation adoption, Godot/target-host playback, Runtime/device behavior, gameplay/physics, Art/QA acceptance, CANON or production readiness.

`axm-create-me` remains coordination-only. Truth, Agency / non-domination, Continuity and Wisdom before speed remain the merge gate.

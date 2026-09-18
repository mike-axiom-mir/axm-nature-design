# VFX east-rear shared-driver response envelope 003

Status: bounded review candidate. No automatic adoption.

This VFX successor consumes Nature Rigging PR #14 head `754797a815266a643c6b08f1606eb76ba95dd8c6`, which in turn consumes VFX PR #17 head `ef7b35af27d5ca98a6447c1e33be07863e387305` as a sign-compatibility donor only.

The exact Weather visual-direction donor remains PR #2 head `ca2eaba519e8449835b0ea6ef944b7080c3caa6a`, source blob `11298d447f262da8a78e43e2df68bc0346c99a2c`, `wind_xy=[1.0,0.35]`, semantics `VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED`.

## Bounded question

Does the exact Rigging sign-normalized shared diagnostic driver produce a coherent signed **static visual-response envelope** across all five generated primary-branch receivers relative to the exact Weather visual direction?

The review evaluates only the inherited Rigging diagnostic values `-5 / -2.5 / 0 / +2.5 / +5°`. It applies the exact Rigging command-sign multiplier per socket, builds simultaneous static poses from the actual generated child partitions, measures branch and family centroid displacement along the Weather visual direction, and retains a deterministic top-down centroid-vector SVG.

A positive shared diagnostic command must move every branch centroid in the positive Weather visual direction; a negative command must move every branch centroid in the inverse direction; neutral must remain exact. This is a coordinate/readability compatibility test, not a wind or motion model.

## Truth boundary

This work does **not** establish or adopt physical wind, force, drag, turbulence, plant biomechanics, final vegetation amplitude, timing, cadence, Animation playback, simultaneous multi-branch motion, Technical-Art target-host acceptance, Runtime/controller behavior, collision, gameplay, target-device performance, Art Direction acceptance, independent Visual QA acceptance, CANON or production readiness.

The static pose review must not be promoted into motion. Animation retains timing/motion authority, Rigging retains articulation/constraint authority, Weather retains source semantics, Technical Art retains target-host transport authority, Runtime retains device/controller authority, and Art/QA retain perceptual acceptance.

# VFX — east/rear north-low parent-stress Weather response

## Scope

This is a bounded VFX / Atmosphere receiving review stacked on Animation PR #26 exact head `5cacd61e22433b0c33f29111827283b81cc0ba0d`.

The Animation owner already proves a 1.0 s / 40 Hz / 41-sample detached `north-low` diagnostic child loop with a same-phase upper-trunk parent-command stress track. Rigging explicitly disables upper-trunk inheritance for this detached diagnostic receiver. VFX does not change that motion.

The Weather donor remains PR #2 exact head `ca2eaba519e8449835b0ea6ef944b7080c3caa6a`, source blob `11298d447f262da8a78e43e2df68bc0346c99a2c`, with visual direction `[1.0, 0.35]` and semantics `VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED`.

## Bounded question

Does every exact accepted Animation sample preserve the previously established `north-low` Weather-direction polarity while the parent stress command runs, and would the forbidden inherited-parent transform materially change that visual-direction response?

The verifier:

- re-executes the exact current Animation owner;
- reconstructs all 41 accepted child poses from the current generated Nature mesh;
- requires every reconstructed pose digest to equal the Animation owner's retained pose digest;
- projects the selected child centroid into Weather-parallel, Weather-cross and vertical coordinates;
- preserves the static VFX predecessor polarity: local negative child angle points downwind, local positive child angle points upwind;
- separately reconstructs the forbidden inherited-parent counterfactual and measures its difference;
- generates a source-space SVG showing accepted versus forbidden Weather-parallel response over the exact one-second loop.

## Ownership boundary

VFX owns only this visual-coordinate response review. Animation keeps timing/cadence/motion authorship. Rigging keeps articulation and the detached-parent exclusion. Weather keeps source direction semantics. Technical Art keeps target-host transport. Runtime keeps controller/device/performance behavior. Art Direction and independent Visual QA keep appearance acceptance.

A green workflow does **not** establish physical wind speed/force/drag/turbulence, botanical or biological motion, connected branch/trunk topology, production skinning, continuous collision/surface continuity, Godot/target-engine playback, wall-clock 40 Hz delivery, Runtime behavior, gameplay/physics, target-device performance, Art/QA acceptance, CANON or production readiness.

`axm-create-me` remains coordination-only. Truth, Agency / non-domination, Continuity, and Wisdom before speed remain the merge gate.

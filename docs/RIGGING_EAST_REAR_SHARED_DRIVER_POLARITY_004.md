# Rigging — east/rear five-socket shared-driver polarity binding 004

## Scope

This bounded Rigging successor consumes the exact VFX PR #17 review-only five-socket sign-map handoff and resolves one Rigging interface ambiguity: a single shared signed diagnostic command cannot be sent to all five independently derived local axes with one global local-angle sign.

The repair is a command-space adapter only. It does not rewrite any source-owned flex declaration, Geometry receiver, Rigging pivot, local axis, child partition, or diagnostic interval.

## Exact lineage

- Rigging predecessor PR #14: `898529f602893c8f6be179bd3e9b6821fc099904`
- Organic source owner: `fdc9d2b6ee729728551e22fd3eafa23ad60b6c7a`
- Geometry receiver: `9b451ba1f65281f550a6754e18574f7ab2951e28`
- VFX sign-map donor PR #17: `ef7b35af27d5ca98a6447c1e33be07863e387305`
- VFX contract blob: `b06b5f6862c6c88ec5642e3bdbccfe0d3e65655f`
- VFX module blob: `ae674ee8f6109d478446fbcd5348bcbee04b01e7`

The VFX donor is consumed as a review-only coordinate/sign compatibility handoff. Its Weather visual-direction semantics are not moved into Rigging.

## Constraint improvement

The unchanged local socket axes use this exact command multiplier map:

- `south-low`: `+1`
- `north-low`: `-1`
- `east-mid`: `+1`
- `west-high`: `-1`
- `north-top`: `+1`

For each socket:

`local_angle_deg = command_sign_multiplier * shared_driver_deg`

The shared diagnostic driver remains bounded to `[-5,+5]°`. Therefore `|local_angle| = |shared_driver|` exactly, and every shared command in the closed interval maps bijectively into the already-proven local Rigging interval without widening it.

Representative shared commands are `-5 / -2.5 / 0 / +2.5 / +5°`. The resulting local witnesses are always one of the predecessor Rigging poses. In particular, shared `+5°` maps to the exact VFX-preferred review-only local endpoint for every socket, while shared `-5°` maps to its exact inverse and shared `0°` remains neutral.

## Preserved identity

The adapter changes no:

- joint pivot;
- source-derived local axis;
- selected child geometry;
- fixed receiver partition;
- source flex metadata;
- Geometry mesh identity;
- local diagnostic interval;
- deformation transform.

Each socket remains `52` selected vertices / `72` selected triangles / `338` fixed vertices. The predecessor's rigid-child deformation evidence remains the geometry/articulation basis; this successor adds only a deterministic signed command interface.

## Truth boundary

This PASS, if the dedicated verifier is green, proves only the bounded shared-driver sign adapter over five independent Rigging sockets.

It does not prove or adopt physical wind, VFX motion, cadence, timing, amplitude, simultaneous multi-branch movement, source/biological ROM, collision/self-intersection freedom, Animation timing/interpolation/playback, Technical-Art target-host acceptance, Runtime/controller/device behavior, gameplay, Art Direction or Visual QA acceptance, CANON, or production readiness.

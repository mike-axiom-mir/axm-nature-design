# Runtime east/rear target-host dynamic-window proof

Status: bounded Runtime / Optimization experiment.

This extends the existing east/rear Runtime lane only after Technical Art supplied an exact current-UC receiver that preserves the Runtime predecessor's source-vertex identity. It does not replace or rewrite the pass-52 source-space result.

## Exact owner chain

- Runtime predecessor: `6d89e1fc0f8dc5e2ef6c57fc99c1dc6b1727780f`
- Technical Art receiver donor: `b96f794325f825188b6fd9a920e3fb575e43e467`
- VFX owner: `ba1c12dd527f1ecc6a0eb4bc0b4322f15ccad475`
- Rigging owner: `754797a815266a643c6b08f1606eb76ba95dd8c6`
- Universal Creation donor: `5c5d2cfdc3aa4e9462fd4d5ec5bc7874f12674a4`

## Bounded question

Can Godot 4.7.2 exercise `ArrayMesh.surface_update_vertex_region()` against the exact current-UC receiver, updating only the already-proven contiguous moving source-index window `[110,370)` while reproducing a full-position update control?

The control and candidate both begin from fresh copies of the same neutral receiver for every retained witness:

- control: update all 390 float32 positions (`4,680 B`);
- candidate: update only vertices `[110,370)` (`260` positions / `3,120 B`) at byte offset `1,320`;
- retained driver witnesses: `-5 / -2.5 / 0 / +2.5 / +5 deg`.

## Measure-before target-host layout discovery

The first target-host attempt deliberately measured the imported receiver instead of assuming the source-side 12-byte position layout. Godot 4.7.2 imports this exact GLB with compressed positions:

- imported vertex-position stride: **8 B**;
- imported position buffer: **3,120 B** for 390 vertices;
- imported positions compressed: **true**.

That means the pass-52 float32 packet cannot be applied directly to the imported buffer using source-side offsets. The first target-host workflow is retained as a failed predecessor rather than hidden.

The bounded Runtime repair creates a dynamic-update `ArrayMesh` from the exact imported arrays. Godot then exposes the mutable float32 position path actually consumed by `surface_update_vertex_region()`:

- mutable vertex-position stride: **12 B**;
- mutable position-buffer size: **4,680 B**;
- dynamic-update flag: **true**;
- candidate byte offset: **1,320 B**;
- candidate byte length: **3,120 B**.

This conversion has a real storage tradeoff: mutable position storage is **1,560 B / 50% larger** than the imported compressed position buffer. Runtime records that cost explicitly; it is not described as a memory win.

Within that mutable receiver, the partial update still saves **1,560 B / 33.3333% per position update** versus the full float32 control.

## Exact target-host equivalence

Across all five retained driver witnesses, Godot readback reports:

- maximum control vs Runtime-expected component delta: **0.0 m**;
- maximum candidate vs Runtime-expected component delta: **0.0 m**;
- maximum control vs candidate component delta: **0.0 m**;
- maximum static control vs candidate component delta: **0.0 m**.

The exact offset matters. A negative control shifts the candidate update window by one Vector3 (`+12 B`) and must fail the readback gate.

## Visual comparison

For each witness the workflow captures one fixed-view shaded control frame and one fixed-view candidate frame from the same proof material, camera and light. The retained five pairs are byte-identical in the green v2 evidence (`0` changed pixels, `0` LSB maximum channel delta). A neutral-vs-`+5 deg` control comparison changes thousands of pixels, so the observer is not passing on a static image.

Normals/tangents are intentionally not updated in either path. Therefore the visual PASS compares the partial-position candidate to the full-position control under the same retained proof normals; it does not establish physically correct deformed normals/tangents, final Nature lookdev, final leaf sidedness or Art/Visual-QA acceptance.

## Workflow lineage

The original auto-running target-host workflow is preserved in Git history as the failed v1 predecessor. It assumed the source-side 12-byte float32 position layout could be applied directly to the imported receiver and was correctly falsified by the measured 8-byte compressed Godot import layout. The active automatic verifier is `runtime-east-rear-target-host-window-v2.yml`; the v1 workflow is now manual-only so a known-invalid assumption does not keep new Runtime heads red.

## Explicit non-claims

A green result does not establish direct updates of Godot's compressed imported position buffer, target-device CPU/GPU/FPS/VRAM/heap/thermal/battery improvement, continuous timed wind playback, physical wind semantics, arbitrary vegetation safety, generic importer policy, final visual acceptance, CANON or production/game readiness.

`axm-create-me` remains coordination-only. Truth, Agency / non-domination, Continuity and Wisdom before speed remain the merge gate.

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

The control and candidate both begin from fresh copies of the same neutral imported `ArrayMesh` for every retained witness:

- control: update all 390 positions (`4,680 B`);
- candidate: update only vertices `[110,370)` (`260` positions / `3,120 B`) at byte offset `1,320`;
- retained driver witnesses: `-5 / -2.5 / 0 / +2.5 / +5 deg`.

The target observer measures the actual imported position-buffer stride/offset before updating. The contract requires Godot to report a 12-byte Vector3 vertex-position stride and zero position-buffer base offset for this exact receiver rather than assuming that layout from source code.

## Visual comparison

For each witness the workflow captures one fixed-view shaded control frame and one fixed-view candidate frame from the same proof material, camera and light. A follow-up pixel comparison is allowed to pass only when no pixel differs by more than 1 LSB. This is representation-equivalence evidence only.

Normals/tangents are intentionally not updated in either path. Therefore a visual PASS compares the partial-position candidate to the full-position control under the same retained proof normals; it does not establish physically correct deformed normals/tangents, final Nature lookdev, final leaf sidedness or Art/Visual-QA acceptance.

## Negative control

The same Godot observer is rerun with the candidate byte offset shifted by exactly one Vector3 (`+12 B`). That run must fail the control/candidate readback gate. The negative control exists to prove the success path depends on the exact `[110,370)` target-buffer window rather than merely calling the partial-update API.

## Explicit non-claims

A green result does not establish target-device CPU/GPU/FPS/VRAM/heap/thermal/battery improvement, continuous timed wind playback, physical wind semantics, arbitrary vegetation safety, generic importer policy, final visual acceptance, CANON or production/game readiness.

`axm-create-me` remains coordination-only. Truth, Agency / non-domination, Continuity and Wisdom before speed remain the merge gate.

# Nature east-rear north-top root socket — Geometry receiver rebind

## Scope

This is a bounded Rigging / Deformation receiver rebind for the existing `north-top` root-socket diagnostic in `mike-axiom-mir/axm-nature-design` PR #14.

The historical Rigging predecessor at `87ce8b2ff10937abec4432e1c6d5a7114a076cdb` proved the socket on Organic's historical generated mesh digest `d7fc5deaa1c12d1d8c7d7b6dc95bf1e8544ce26140ee2e4a7d2c67a2c4133e48`. Geometry PR #9 later rebound the same exact Organic source to its migrated winding receiver at `9b451ba1f65281f550a6754e18574f7ab2951e28`, mesh digest `aa9d450a78fef722672ea9af0f9aca98b4c1a0ca3705661784f5f61f3e9b6a31`.

This pass explicitly consumes that Geometry receiver and reruns the Rigging proof. It does not transfer the predecessor PASS by analogy.

## Exact identities

Organic source owner:

- PR #8 head `fdc9d2b6ee729728551e22fd3eafa23ad60b6c7a`;
- source digest `178cd8cfb1a859bff411f60e13154109528062cf0ad2384b343d406cc0cc9d61`;
- `north-top-branch-flex` center `[0.01, 0.0, 3.16] m`;
- source flex radius `0.12 m`;
- source status remains `DECLARED_NOT_DEFORMATION_TESTED`.

Geometry receiver:

- PR #9 head `9b451ba1f65281f550a6754e18574f7ab2951e28`;
- migrated mesh digest `aa9d450a78fef722672ea9af0f9aca98b4c1a0ca3705661784f5f61f3e9b6a31`;
- 390 vertices / 570 triangles;
- shared-edge winding conflicts `0`;
- boundary edges `100`;
- non-manifold indexed edges `0`.

Historical Rigging predecessor:

- PR #14 head `87ce8b2ff10937abec4432e1c6d5a7114a076cdb`;
- historical Organic mesh digest `d7fc5deaa1c12d1d8c7d7b6dc95bf1e8544ce26140ee2e4a7d2c67a2c4133e48`;
- result `PASS_NORTH_TOP_ROOT_SOCKET_RIGID_CHILD_ARTICULATION_DIAGNOSTIC_MINUS5_TO_PLUS5`.

Historical and migrated mesh identities remain distinct and independently addressable.

## Preserved Rigging contract

No source-owned or Rigging-owned articulation semantics are widened:

- branch: `north-top` only;
- leaf cluster: `north-top-leaves` only;
- pivot: exact source branch root / flex center `[0.01, 0.0, 3.16] m`;
- axis: normalized cross product of the nearest local trunk tangent and first branch tangent;
- selected child: two branch segments + four leaf blades;
- selected receiver partition: 52 vertices / 72 triangles;
- fixed receiver: 338 vertices;
- diagnostic interval: `-5° .. +5°`;
- retained representative poses: `-5 / -2.5 / 0 / +2.5 / +5°`;
- transform: one rigid Rodrigues rotation around the exact pivot/axis.

The interval remains `RIGGING_VERIFICATION_PROBE_ONLY_NOT_SOURCE_OR_BIOLOGICAL_ROM`.

## Receiver rebind rule

`EXACT_SOURCE_CONTINUITY_DOES_NOT_TRANSFER_MESH_LEVEL_RIGGING_ACCEPTANCE_ACROSS_A_TOPOLOGY_RECEIVER_IDENTITY_CHANGE__REBIND_EXACT_GEOMETRY_HEAD_AND_RERUN_THE_ARTICULATION_PROOF`

The Geometry migration changes cap winding/index emission only. Rigging consumes Geometry's exact migration receipt and current receiver identity; it does not claim authorship of Geometry's topology decision.

## Proved motion boundary

For every real angle in the declared diagnostic interval, selected child vertices use one rigid rotation around the exact pivot and source-derived axis while every unselected vertex is identity-mapped. Therefore the following are structural continuous invariants for this implementation:

- pivot position;
- every fixed receiver position;
- pairwise distances within the selected child;
- selected-child projection onto the rotation axis.

Representative poses quantify the implementation and maximum bounded movement. The proof does not establish collision freedom or surface attachment.

## Fail-closed controls

The lane rejects:

- Organic source digest drift;
- Geometry receiver-head drift;
- migrated receiver digest drift;
- historical receiver identity drift;
- pivot drift;
- branch ownership drift;
- source flex radius/status drift;
- diagnostic interval widening;
- promotion to source/biological ROM;
- transfer of Geometry acceptance into Rigging;
- Animation acceptance claims;
- Runtime acceptance claims.

## Truth boundary

A PASS here means only that the exact existing Rigging socket/articulation contract has been explicitly re-executed on Geometry PR #9's exact migrated receiver.

It does not establish production skin weights, blended attachment, plant biomechanics, stress/strength, self-intersection or collision freedom, wind/VFX response, Animation timing/interpolation/playback, Technical-Art target-host transport, Runtime/controller/device/performance, visual acceptance, CANON or production/game readiness.

Organic retains source authority. Geometry retains topology. Rigging retains articulation/deformation evidence. Animation, VFX, Technical Art, Runtime and Art/QA retain their own downstream acceptance gates.

The four AXM roots remain the merge gate: **Truth, Agency / non-domination, Continuity, Wisdom before speed**.

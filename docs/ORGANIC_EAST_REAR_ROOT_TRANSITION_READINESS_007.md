# Organic Form — east-rear neutral branch transition readiness 007

## Why this exists

Geometry PR #18 now proves an important negative boundary for the exact `north-low` diagnostic receiver: the selected branch child and trunk share zero indexed vertices, and the root branch segment is a closed capped shell. That is a Geometry/topology fact. It does not erase Organic's existing neutral spatial-support evidence, but it means Organic must not let radial support, flex-envelope overlap, or Rigging socket evidence be read as a connected branch/trunk mesh junction.

The smallest useful Organic follow-on is therefore **not** a source reshaping, weld, boolean, remesh, skinning rule, or larger flex radius. It is an exact source-space measurement of how far each authored first branch segment remains fully supported by the authored trunk radial envelope before the full tapered branch radius first reaches that envelope boundary.

This preserves source form and gives a future Geometry-owned junction experiment an exact neutral-form transition interval without pretending that the current diagnostic mesh is welded.

## Exact source identity retained

- Organic source/form owner: `fdc9d2b6ee729728551e22fd3eafa23ad60b6c7a`;
- source path: `examples/east_rear_tree_neutral_001.json`;
- source Git blob before this evidence-only pass: `fb12b759e1abfd0455bf46fd39a0eba27095796b`;
- source digest: `178cd8cfb1a859bff411f60e13154109528062cf0ad2384b343d406cc0cc9d61`;
- historical Organic generated mesh: `390 vertices / 570 triangles`;
- historical Organic mesh digest: `d7fc5deaa1c12d1d8c7d7b6dc95bf1e8544ce26140ee2e4a7d2c67a2c4133e48`.

No trunk point, branch point, source radius, leaf, flex-zone declaration, generator, generated mesh, Rigging transform, Animation/VFX state, target-host representation, Runtime state, or world placement is changed by this pass.

All seven source flex declarations remain `DECLARED_NOT_DEFORMATION_TESTED`.

## Fresh Geometry return consumed without authority transfer

Current Geometry PR #18 carries the exact `north-low` topology classification on the unchanged migrated receiver:

- Organic source owner: `fdc9d2b6...`;
- source digest: `178cd8cf...`;
- Geometry receiver digest: `aa9d450a78fef722672ea9af0f9aca98b4c1a0ca3705661784f5f61f3e9b6a31`;
- Rigging owner bound by Geometry: `975931b11555d156e04e2ab12e9756fc6c9598a3`;
- `north-low` selected child: `52 vertices / 72 triangles`;
- edge-connected components: `6`;
- two closed tapered-segment shells, each `18 vertices / 32 triangles / 48 edges / 0 boundary edges / Euler characteristic 2`;
- four open leaf-blade components, each `4 vertices / 2 triangles / 5 edges / 4 boundary edges / Euler characteristic 1`;
- root branch segment is a closed capped shell;
- shared indexed vertices between selected `north-low` child and trunk: `0`.

Geometry result:

`PASS_NORTH_LOW_DIAGNOSTIC_CHILD_TOPOLOGY_CLASSIFIED__HOLD_CONNECTED_BRANCH_TRUNK_ATTACHMENT`

Organic accepts that as a topology boundary only. No source compensation is inferred from it automatically.

## Bounded Organic measurement

New observer:

`axm.nature-neutral-branch-transition-envelope/v0.1`

For each of the five primary branches, the observer evaluates only the first authored tapered segment. At any segment parameter `u`, it:

1. evaluates the authored branch centerline point and linearly tapered branch radius;
2. finds the nearest authored trunk centerline segment and its linearly interpolated trunk radius;
3. evaluates the neutral source-space support margin:

`local_trunk_radius - centerline_distance - branch_radius`;

4. starting from the already-supported root, finds the first point where that full branch radius reaches the authored trunk radial-envelope boundary.

That first boundary is a **neutral source-form radial relation**, not generated-mesh contact, not a weld location, not a deformation weight boundary, and not a biological insertion depth.

## Exact current result

Scoped state:

`PASS_EXACT_NEUTRAL_BRANCH_TRANSITION_ENVELOPES__CONNECTED_TOPOLOGY_HELD`

All five branch roots retain positive full-radius neutral support, and all five first segments transition out of the authored trunk radial envelope before their first authored segment endpoint.

Exact embedded lengths measured along each first branch segment:

- `south-low`: `0.060865238939307745 m`;
- `north-low`: `0.0645372173379806 m`;
- `east-mid`: `0.021620222932618765 m`;
- `west-high`: `0.036156960642309076 m`;
- `north-top`: `0.021221011737572286 m`.

The exact current range is therefore about **21.22 mm to 64.54 mm** of source-space first-segment length before the full tapered branch radius first reaches the authored trunk radial-envelope boundary.

### North-low exact witness

The fresh Geometry HOLD makes `north-low` the important handoff witness.

At the authored root:

- nearest trunk segment: `mid->upper`;
- trunk-segment parameter: `0.5877803557617942`;
- root-center distance to nearest trunk centerline: `0.006592784731672558 m`;
- local authored trunk radius: `0.10236658932714617 m`;
- authored branch-root radius: `0.055 m`;
- full-radius neutral support margin: `0.040773804595473605 m`.

Its first branch segment is `0.4360045871318327 m` long. The full tapered branch radius first reaches the authored trunk radial-envelope boundary at:

- first-segment fraction: `0.14801958337760968`;
- length from authored root: `0.0645372173379806 m`;
- branch radius there: `0.0518915887490702 m`;
- centerline distance there: `0.04875371484283564 m`;
- local trunk radius there: `0.10064530359190585 m`;
- numerical boundary residual: approximately zero.

This makes the source-space relationship more precise without contradicting Geometry: **the authored radial masses overlap for a bounded neutral transition interval, while the current generated receiver still has no indexed welded branch/trunk junction. Both facts are true and remain separately owned.**

## Reusable handoff rule

`NEUTRAL_RADIAL_SUPPORT_INTERVAL != INDEXED_CONNECTIVITY__ORGANIC_MAY_MEASURE_THE_SOURCE_TRANSITION_ENVELOPE__GEOMETRY_MUST_EXPLICITLY_CHOOSE_AND_VERIFY_ANY_CONNECTED_JUNCTION_STRATEGY`

Operationally:

- Organic owns the authored centerlines, radii, mass/proportion relation and this neutral radial-transition measurement.
- Geometry owns whether a production successor uses a weld, boolean, remesh, bridge, shared-ring construction, or another verified topology strategy.
- Rigging owns hierarchy, deformation, weights, constraints and motion-domain acceptance.
- Animation/VFX own timing and visual-response semantics.
- Technical Art owns target-host transport/representation.
- Runtime owns device/performance behavior.
- Art Direction / Visual QA own perceptual acceptance.

No owner is allowed to promote this radial interval into another evidence class silently.

## Fail-closed controls

The observer/tests reject:

- a missing exact branch-root flex declaration;
- any source flex declaration promoted beyond `DECLARED_NOT_DEFORMATION_TESTED`;
- a zero-length first branch segment;
- a branch root whose full authored radius is outside the trunk support envelope.

The receipt also keeps explicit false claims for generated-mesh connectivity inspection, connected topology, junction-strategy selection, deformation simulation, rigging hierarchy/weights, biological attachment, and Runtime readiness.

## Visual / structural evidence retention

Because source form and generated mesh bytes are unchanged, no new visual shape is invented for this pass. The existing front/side/top wire views, exact OBJ, source JSON, generated mesh JSON, source-envelope receipt, deformation-readiness receipt and flex-interaction receipt remain the correct visual/structural evidence. The build now adds `root-transition-readiness.json` beside them so the new source-form transition measurement is retained without pretending there was a visual delta.

## Truth boundary

This result proves only a deterministic source-space relationship between the exact authored trunk centerline/radii and each exact authored first branch segment/radii in neutral form.

It does **not** establish:

- a welded or connected branch/trunk production mesh;
- a preferred weld/boolean/remesh/junction topology;
- botanical species correctness or biological attachment mechanics;
- tissue continuity, strength, stiffness, stress or valid plant ROM;
- production skinning, weights or blended deformation;
- physical wind, collision or self-intersection freedom;
- target-host or target-device acceptance;
- final Art/QA acceptance;
- CANON;
- production/game readiness;
- Organic, Geometry, Rigging or any specialist mastery.

The four AXM roots remain the merge gate: **Truth, Agency / non-domination, Continuity, Wisdom before speed**.

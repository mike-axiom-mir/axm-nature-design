# Geometry — north-low owner-transition open boundary ring 006

## Scope

This is a **Geometry-owned diagnostic mesh candidate** on the existing Nature Geometry PR #18 lane. It consumes, without rewriting, the exact Organic neutral-support exit and the Procedural canonical transition parameter for `north-low`.

The candidate trims only the *diagnostic branch-side first-segment representation* at the exact owner transition:

- `u = 0.14801958337760968`;
- `64.5372173379806 mm` along the authored first branch segment;
- branch radius at the cut: `0.0518915887490702 m`.

No authored source point/radius, current generated receiver, Rigging socket, trunk mesh, Animation/VFX state, target host, Runtime representation or world placement is changed.

## Reusable pattern

`OWNER_TRANSITION_EXIT_MAY_SEED_A_BRANCH_SIDE_OPEN_BOUNDARY_RING_ONLY_AFTER_TOPOLOGY_PRESERVING_LONGITUDINAL_EDGE_SPLIT__TRUNK_OPENING_BRIDGE_AND_CONNECTED_JUNCTION_REMAIN_SEPARATE_GEOMETRY_GATES`

The owner transition is used as a deterministic cut parameter on the existing 8-sided tapered first segment. Each transition-ring vertex is an exact longitudinal-edge interpolation between the original start and end rings. Geometry then keeps only the outside branch-side stub and its far cap, leaving the transition ring open.

This creates a bridge-ready **branch-side boundary interface**, not a welded branch/trunk junction.

## Exact lineage

- previous Geometry head after current-Rigging reconciliation: `d5ebbf26afd466faad259621b60fa33f1126ef3c`;
- current Rigging owner: `69640e558f0c1ac59d4d0e3155676e0967a03d04`;
- Organic transition owner: `4b5c291d6b044dafeadd6eeaf4849a6f3d4f4148`;
- Organic observer blob: `1e8323b9bf6495a9f19704c217808300f3b46757`;
- Procedural transition owner: `b3283e255bfffb2979889fd542a93e35be2a4b03`;
- Procedural transition contract blob: `08df5c1eb79a596a05b37a3187b5fa010e8d658d`;
- source blob: `fb12b759e1abfd0455bf46fd39a0eba27095796b`;
- source digest: `178cd8cfb1a859bff411f60e13154109528062cf0ad2384b343d406cc0cc9d61`.

## Structural target

The diagnostic open stub must prove:

- `17` vertices;
- `24` triangles;
- `40` undirected edges;
- one triangle component;
- `8` boundary edges;
- exactly one simple boundary cycle of length `8`;
- zero non-manifold edges;
- zero winding conflicts;
- zero degenerate triangles;
- zero isolated vertices;
- Euler characteristic `1`;
- transition-ring vertices lie on the exact original longitudinal edges to the Geometry tolerance.

## Explicit HOLDs

This pass does **not** generate or prove:

- a matching trunk opening;
- a trunk-side boundary loop;
- a bridge, weld, boolean union or remesh;
- connected branch/trunk indexed topology;
- source/default adoption;
- production skinning or deformation;
- collision/self-intersection freedom of a future connected junction;
- target-host / Runtime acceptance;
- gameplay suitability;
- CANON or production/game readiness;
- Geometry mastery.

A later connected-junction experiment must independently create and verify the trunk opening and the bridge, then trigger an explicit Rigging rebind.

# East/rear Nature source study 001

Status: **Organic Form candidate / not composed**

This lane adds one distinct source-owned vegetation body for the retained seed-29
`proxy:nature-tree-east-a` slot after the east-foreground source replacement was
accepted for scene hierarchy. It does not modify the accepted compact east-foreground
tree or the Map receiving scene.

## Exact receiving context

- Map repository: `mike-axiom-mir/axm-map-design`
- Map PR: `#4`
- exact accepted receiving head: `cdac7d1316631b3b130d5e558de2aee462a21d40`
- retained seed: `29`
- target: `proxy:nature-tree-east-a`
- retained proxy position: `[6.089407, 2.004654, 2.098546] m`
- retained proxy size: `[1.678837, 1.678837, 4.197092] m`
- retained proxy rotation metadata: `-5.415604 deg`
- placement contract: source remains unscaled and receives no extra rotation; a later
  Environment comparison must preserve the target centre XY and ground source min-Z.

## Bounded source intent

`east-rear-tree-neutral-001` is deliberately taller and asymmetrical relative to the
already accepted compact east-foreground body. It uses the existing Nature Organic
source schema and generator, with six tapered trunk points, five branch chains, six
leaf clusters / twenty-five planar leaf blades, and seven flex zones that remain
`DECLARED_NOT_DEFORMATION_TESTED`.

The seventh declaration is a metadata-only deformation-readiness successor for the
previously uncovered `north-top` branch root. It is centered exactly at the authored
root `[0.01, 0.0, 3.16] m` and uses radius `0.12 m`, the smaller of the two exact
branch-flex radius classes already authored in this same source. The existing upper
branch roots `east-mid` and `west-high` already use `0.12 m`; the larger/lower
`south-low` and `north-low` roots use `0.14 m`. This choice completes exact-root
metadata coverage without inventing a third radius class or changing source geometry.
It does not imply that `0.12 m` is biologically, mechanically, or visually correct.

Expected exact source digest from the authored JSON:
`178cd8cfb1a859bff411f60e13154109528062cf0ad2384b343d406cc0cc9d61`

Expected exact baseline mesh digest from the current Organic generator remains:
`d7fc5deaa1c12d1d8c7d7b6dc95bf1e8544ce26140ee2e4a7d2c67a2c4133e48`

Expected generated body:
- `390` vertices;
- `570` triangles;
- size approximately `1.465958133 x 1.248181893 x 4.090100386 m`;
- positive retained proxy margins approximately
  `0.212878867 / 0.430655107 / 0.106991614 m`.

The source digest changes because source metadata changed; the generated mesh digest
remains byte-identical because flex-zone metadata is not consumed by the mesh builder.
Receivers that pin the source digest must therefore rebind explicitly, while no mesh
change is inferred merely from the new source identity.

CI is authoritative for the exact published branch; these values are expected gates,
not a substitute for exact-head workflow evidence.

## Geometry / topology boundary

The source intentionally continues to use the established Organic generator so it
does not silently rewrite existing Nature mesh lineage. Geometry PR #9 separately
retains the migrated/reindexed topology successor. This metadata-only Organic change
does not adopt or rewrite that Geometry lineage and does not imply a topology PASS.

## Truth boundary

A PASS proves only that this exact authored stylized body satisfies the existing
Organic structural/proportion checks, fits the exact retained seed-29 east-a receiving
envelope without hidden scale or extra source rotation, and now carries exact-root
unproven flex metadata for all five authored primary branches. It does not prove Map
composition or Art Direction acceptance, botanical or biological correctness, branch
strength, production connected topology, self-intersection freedom, deformation/wind
quality, rigging, Materials, target-engine/runtime behavior, gameplay, CANON,
production readiness, or Organic/Nature mastery.

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
leaf clusters / twenty-five planar leaf blades, and six flex zones that remain
`DECLARED_NOT_DEFORMATION_TESTED`.

Expected exact source digest from the authored JSON:
`0adf2cde8cfc355ec21b6fb06c6759b753300164b5f72ba029dc1b8c6d2ef307`

Expected exact baseline mesh digest from the current Organic generator:
`d1c1f6530f5e922bd0c77a973c6fabd439e283bd8752c94f5f7d30a13d24d637`

Expected generated body:
- `390` vertices;
- `570` triangles;
- size approximately `1.465958133 x 1.248181893 x 4.090100386 m`;
- positive retained proxy margins approximately
  `0.212878867 / 0.430655107 / 0.106991614 m`.

CI is authoritative for the exact published branch; these values are expected gates,
not a substitute for exact-head workflow evidence.

## Geometry / topology boundary

The source intentionally continues to use the established Organic generator so it
does not silently rewrite existing Nature mesh lineage. Geometry PR #7 has separately
identified a repeated tapered-cap winding issue and retains a reindex-only candidate.
That repair is not imported here until Technical Art proves the downstream
consequences and an explicit source migration is justified.

## Truth boundary

A PASS proves only that this exact authored stylized body satisfies the existing
Organic structural/proportion checks and fits the exact retained seed-29 east-a
receiving envelope without hidden scale or extra source rotation. It does not prove
Map composition or Art Direction acceptance, botanical or biological correctness,
production connected topology, self-intersection freedom, deformation/wind quality,
rigging, Materials, target-engine/runtime behavior, gameplay, CANON, production
readiness, or Organic/Nature mastery.

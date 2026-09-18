# East/rear Nature deformation-readiness evidence 001

Status: **PASS_NEUTRAL_BRANCH_ROOT_SUPPORT__DEFORMATION_UNTESTED**

This evidence is deliberately narrower than deformation acceptance. It measures
source-owned neutral-form attachment relationships in `east-rear-tree-neutral-001`
so later Rigging/VFX work does not have to guess whether branch roots are detached,
weakly attached, or covered by declared Organic flex metadata.

This successor changes **one source metadata declaration only**: `north-top` now has
an exact-root flex zone with radius `0.12 m` and status
`DECLARED_NOT_DEFORMATION_TESTED`. No source point, trunk/branch radius, branch/leaf
placement, generated mesh, receiving context, weather input, topology, rig, material,
animation or runtime representation changes.

## Exact source identity

- Organic PR #8 pre-readiness source/form head: `a4e5ee011e1d87f47866a7e6c6f4e66f57b6af12`
- previous evidence-only head: `b681b8beb0f91c6cedb6067aa8a79ae9feea6482`
- previous source digest: `0adf2cde8cfc355ec21b6fb06c6759b753300164b5f72ba029dc1b8c6d2ef307`
- current source digest: `178cd8cfb1a859bff411f60e13154109528062cf0ad2384b343d406cc0cc9d61`
- baseline/current generated mesh digest: `d7fc5deaa1c12d1d8c7d7b6dc95bf1e8544ce26140ee2e4a7d2c67a2c4133e48`
- source mesh: `390` vertices / `570` triangles
- primary branch chains: `5`
- currently declared flex zones: `7`
- exact primary-root flex coverage: `5 / 5`

The current source digest exactly matches Procedural's retained **0.12 m review-only
candidate digest**. Organic explicitly adopts only that metadata declaration into its
own source authority; the Procedural family did not authorize or force adoption.

Geometry PR #9 remains a separate migrated-topology lineage. This source-form check
uses authored trunk/branch points and radii, not triangle winding, so it does not
adopt or overwrite Geometry's mesh authority. Because flex metadata is not consumed
by the mesh builder, the generated baseline mesh digest remains byte-identical.

## Why 0.12 m was selected

Procedural PR #4 independently reconstructed the four existing exact-root branch flex
declarations and exposed only the two radius classes already authored in this source:
`0.12 m` and `0.14 m`. Both review-only north-top candidates closed metadata coverage
without claiming deformation quality.

Organic selects `0.12 m` because it is the smaller already-authored branch-flex class
and is already used by the two higher/smaller covered branch roots (`east-mid`, root
radius `0.049 m`; `west-high`, root radius `0.045 m`). The lower/larger roots
`south-low` (`0.058 m`) and `north-low` (`0.055 m`) use `0.14 m`; `north-top` is the
smallest/highest primary root at `0.039 m`. This is a bounded source-pattern decision,
not a claim that flex-zone radius scales biologically, mechanically, or linearly with
branch size.

No third radius class was invented, no interpolation rule was introduced, and the
metadata remains explicitly untested.

## Neutral branch-root support method

For each primary branch root, the observer finds the closest point on every authored
trunk centerline segment, selects the nearest segment, linearly interpolates the
source trunk radius at that exact segment parameter, then computes:

`neutral support margin = local trunk radius - centerline distance - branch root radius`

A non-negative margin means the complete authored branch-root radius still fits
inside the local neutral trunk radius under this bounded centerline/radius model.
That is only a source-form attachment check. It is not a contact, stress, tissue,
wind, bend or rigging proof.

Exact measurements remain:

| branch root | nearest trunk segment | centerline distance m | local trunk radius m | branch root radius m | support margin m | exact root flex zone |
|---|---|---:|---:|---:|---:|---|
| `south-low` | `mid->upper` | `0.005015058531` | `0.109893271462` | `0.058` | `0.046878212931` | `south-low-branch-flex` / `0.14 m` |
| `north-low` | `mid->upper` | `0.006592784732` | `0.102366589327` | `0.055` | `0.040773804595` | `north-low-branch-flex` / `0.14 m` |
| `east-mid` | `upper->crown` | `0.027433195134` | `0.086164574616` | `0.049` | `0.009731379482` | `east-mid-branch-flex` / `0.12 m` |
| `west-high` | `upper->crown` | `0.010569554445` | `0.074602510460` | `0.045` | `0.019032956015` | `west-high-branch-flex` / `0.12 m` |
| `north-top` | `crown->tip` | `0.019635236228` | `0.059647823082` | `0.039` | `0.001012586854` | `north-top-branch-flex` / `0.12 m` |

All five branch roots retain positive neutral attachment support in this bounded
model. The minimum retained margin remains `0.0010125868542811625 m` at `north-top`.

## Exact scoped PASS

The source now has exact root-centered flex metadata for all five primary branch
roots, and every declaration remains `DECLARED_NOT_DEFORMATION_TESTED`.

Scoped observer state:

**`PASS_NEUTRAL_BRANCH_ROOT_SUPPORT__DEFORMATION_UNTESTED`**

This closes only the previous metadata-coverage HOLD. It does not convert a flex-zone
declaration into tested deformation, establish an allowable bend range, or authorize
Rigging/VFX/Animation behavior.

## Handoff

- **Organic Form:** current neutral geometry remains frozen; the only successor delta
  is the exact north-top flex declaration at `0.12 m`.
- **Rigging / Deformation:** consume the completed root metadata only as source intent.
  It does not authorize a rig, weight field, bend range, skinning or deformation PASS.
- **VFX / Animation:** no wind response, timing, displacement amplitude or flex
  response is accepted here.
- **Geometry:** PR #9 topology migration remains distinct. The source digest changed
  while the generated mesh digest did not; consumers that pin source identity must
  rebind, while mesh-only evidence must not be relabelled automatically.
- **Procedural:** the review family remains evidence provenance; Organic adoption of
  one owner-backed candidate does not turn the family into automatic source authority.
- **Environment / Art / QA / Runtime:** no receiving, visual or device conclusion is
  transferred from this source-form report.

## Truth boundary

This evidence establishes only deterministic neutral-form branch-root support under
the stated source centerline/radius model and complete exact-root **unproven** flex
metadata coverage. It does **not** prove botanical or biological correctness, branch
strength, stress distribution, tissue behavior, self-intersection freedom, connected
production topology, rigging quality, wind/deformation quality, animation quality,
target-host or device readiness, visual acceptance, CANON, production readiness or
Organic mastery.

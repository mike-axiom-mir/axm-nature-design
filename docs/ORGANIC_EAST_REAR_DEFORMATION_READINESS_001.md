# East/rear Nature deformation-readiness evidence 001

Status: **HOLD_BRANCH_ROOT_FLEX_ZONE_COVERAGE**

This evidence is deliberately narrower than deformation acceptance. It measures
source-owned neutral-form attachment relationships in `east-rear-tree-neutral-001`
so later Rigging/VFX work does not have to guess whether branch roots are detached,
weakly attached, or already covered by declared Organic flex metadata.

No source point, radius, branch, leaf, mesh, flex-zone declaration, receiving context,
weather input, topology, rig, material, animation or runtime representation is changed
by this evidence pass.

## Exact source identity retained

- Organic PR #8 pre-evidence source/form head: `a4e5ee011e1d87f47866a7e6c6f4e66f57b6af12`
- source digest: `0adf2cde8cfc355ec21b6fb06c6759b753300164b5f72ba029dc1b8c6d2ef307`
- baseline mesh digest: `d7fc5deaa1c12d1d8c7d7b6dc95bf1e8544ce26140ee2e4a7d2c67a2c4133e48`
- source mesh: `390` vertices / `570` triangles
- primary branch chains: `5`
- currently declared flex zones: `6`

Geometry PR #9 remains a separate migrated-topology lineage. This source-form check
uses authored trunk/branch points and radii, not triangle winding, so it does not
adopt or overwrite Geometry's mesh authority.

## Neutral branch-root support method

For each primary branch root, the observer finds the closest point on every authored
trunk centerline segment, selects the nearest segment, linearly interpolates the
source trunk radius at that exact segment parameter, then computes:

`neutral support margin = local trunk radius - centerline distance - branch root radius`

A non-negative margin means the complete authored branch-root radius still fits
inside the local neutral trunk radius under this bounded centerline/radius model.
That is only a source-form attachment check. It is not a contact, stress, tissue,
wind, bend or rigging proof.

Exact current measurements:

| branch root | nearest trunk segment | centerline distance m | local trunk radius m | branch root radius m | support margin m | exact root flex zone |
|---|---|---:|---:|---:|---:|---|
| `south-low` | `mid->upper` | `0.005015058531` | `0.109893271462` | `0.058` | `0.046878212931` | `south-low-branch-flex` |
| `north-low` | `mid->upper` | `0.006592784732` | `0.102366589327` | `0.055` | `0.040773804595` | `north-low-branch-flex` |
| `east-mid` | `upper->crown` | `0.027433195134` | `0.086164574616` | `0.049` | `0.009731379482` | `east-mid-branch-flex` |
| `west-high` | `upper->crown` | `0.010569554445` | `0.074602510460` | `0.045` | `0.019032956015` | `west-high-branch-flex` |
| `north-top` | `crown->tip` | `0.019635236228` | `0.059647823082` | `0.039` | `0.001012586854` | **missing** |

All five current branch roots therefore have positive neutral attachment support in
this bounded model. The minimum retained margin is `0.0010125868542811625 m` at
`north-top`.

## Exact HOLD

The source has five primary branch roots but exact root-centered flex metadata for
only four of them. `north-top` at `[0.01, 0.0, 3.16] m` has no declared matching flex
zone. That is now an explicit Organic deformation-readiness HOLD instead of an
implicit omission.

The evidence includes a candidate-only negative/closure control showing that adding a
matching root-centered zone with status `DECLARED_NOT_DEFORMATION_TESTED` would close
**only** the flex-zone coverage hold. That control does not authorize a source edit and
does not select a production radius. Organic must choose any future metadata change
as a separate source decision with downstream source-digest rebinding.

## Handoff

- **Organic Form:** keep the current neutral geometry frozen. If flex metadata is
  extended later, change only the missing north-top declaration and rebind exact
  source identity; do not imply deformation quality from metadata coverage.
- **Rigging / Deformation:** consume this as neutral source attachment evidence only.
  It does not authorize a rig, bend range, skinning or deformation PASS.
- **VFX / Animation:** no wind response, timing, displacement amplitude or flex
  response is accepted here.
- **Geometry:** PR #9 topology migration remains distinct. A future source-metadata
  edit changes the source digest even if the generated mesh stays byte-identical, so
  lineage must be rebound explicitly rather than assumed.
- **Environment / Art / QA / Runtime:** no receiving, visual or device conclusion is
  transferred from this source-form report.

## Truth boundary

This evidence establishes only deterministic neutral-form branch-root support under
the stated source centerline/radius model and exposes one missing flex-zone coverage
entry. It does **not** prove botanical or biological correctness, branch strength,
stress distribution, tissue behavior, self-intersection freedom, connected production
topology, rigging quality, wind/deformation quality, animation quality, target-host or
device readiness, visual acceptance, CANON, production readiness or Organic mastery.

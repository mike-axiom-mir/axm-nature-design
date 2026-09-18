# Procedural rear-tree branch transition parameter family 001

## Scope

This is a bounded Procedural Design adapter over Organic Form's exact source-space neutral
branch-transition evidence for the east/rear tree. Organic owns the authored centerlines,
radii and measured first-segment radial-support exits. Procedural does not recompute that
geometry. It canonicalizes the five owner measurements into reusable normalized-`u` and
metre parameter windows that a later owner may explicitly consume.

Schema: `axm.nature-branch-transition-parameter-family/v0.1`

Relation:

`DERIVED_OWNER_TRANSITION_PARAMETER_WINDOWS_ONLY_NOT_JUNCTION_RIGGING_WEIGHT_OR_DOWNSTREAM_AUTHORITY`

## Why this deserves proceduralization

The exact source now exposes the same bounded relation on five primary branches: each
branch begins with full-radius neutral support inside the authored trunk radial envelope,
then exits that envelope somewhere within its first tapered segment. Re-encoding those
five intervals manually in later Geometry/Geometry-Nodes experiments would duplicate
source-derived numbers and invite drift.

The smallest reusable capability is therefore a deterministic parameter family:

- start parameter: `u=0`;
- end parameter: the exact Organic-owned first full-radius exit fraction;
- physical length: the exact Organic-owned embedded first-segment length;
- three neutral sampling anchors: start / midpoint / end;
- no junction topology, weight, deformation or downstream adoption semantics.

## Exact owner

Organic PR #8 exact transition owner:

`4b5c291d6b044dafeadd6eeaf4849a6f3d4f4148`

Observer blob:

`1e8323b9bf6495a9f19704c217808300f3b46757`

Unchanged source blob:

`fb12b759e1abfd0455bf46fd39a0eba27095796b`

Source digest:

`178cd8cfb1a859bff411f60e13154109528062cf0ad2384b343d406cc0cc9d61`

## Five materially different outputs

| branch | end `u` | transition length |
|---|---:|---:|
| south-low | 0.13755075785472692 | 0.060865238939307745 m |
| north-low | 0.14801958337760968 | 0.0645372173379806 m |
| east-mid | 0.04877293495372904 | 0.021620222932618765 m |
| west-high | 0.08456756400847554 | 0.036156960642309076 m |
| north-top | 0.05131780006304828 | 0.021221011737572286 m |

The family requires all five parameter identities, normalized windows and physical
lengths to remain materially distinct. Reversing owner row order or contract declaration
order must preserve the canonical family digest.

## Failure boundary

The family fails closed on exact Organic owner/observer/source drift, owner PASS-state
drift, branch-count or branch-identity drift, transition length/fraction drift, connected
topology promotion, junction-strategy promotion, automatic Rigging adoption and
production-weight authority promotion.

## Non-claims

This family does not:

- choose or generate a weld, boolean, remesh, bridge or shared-ring junction;
- prove indexed branch/trunk connectivity;
- mutate Organic source geometry or flex declarations;
- assign Rigging hierarchy or skin weights;
- simulate deformation or biological attachment;
- authorize Animation, VFX, Technical Art, Runtime, Map or Art/QA adoption;
- establish UC/PF promotion, CANON or production readiness.

The four AXM roots remain the merge gate: Truth, Agency / non-domination, Continuity,
Wisdom before speed.

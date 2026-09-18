# Procedural Design — east/rear transition frame parameter family 007

## Why this exists

Organic Form PR #8 now owns five exact neutral source-form frames at the already-measured first-segment radial-support exits of the east/rear tree. The preceding Procedural family already canonicalizes the five scalar `u` / metre transition windows. Geometry PR #18 has started consuming one of those windows for a branch-side open-ring experiment while explicitly holding the trunk opening, bridge and connected junction.

The repeated gap is therefore no longer another scalar window and not a junction generator: future Geometry / Geometry-Nodes studies would otherwise have to re-copy five owner origins and basis vectors and choose their own axis ordering. This family makes that conversion deterministic once.

## Bounded family

Schema:

`axm.nature-branch-transition-frame-parameter-family/v0.1`

The family consumes Organic owner schema:

`axm.nature-neutral-branch-transition-exit-frame/v0.1`

and retains the predecessor scalar family identity:

`d742e72e2a5f8be868465d91c286ca8fd6509789936c14a595b4cc18a57fb096`

The only new procedural convention is a right-handed parameter frame:

- origin = exact Organic exit center;
- `+X` = exact radial unit vector away from the local trunk centerline;
- `+Y` = exact owner azimuth `cross(local_trunk_tangent, radial)`;
- `+Z` = exact local trunk tangent;
- a 4x4 local-to-source matrix is emitted with those three basis vectors as columns and the exit center as translation;
- the exact owner branch tangent is reordered into local `XYZ = radial / azimuth / axial` components.

This is a parameter convention only. `+X` is not promoted to a production mesh normal, the matrix is not a bone/joint frame, and no consumer convention is silently imposed on a renderer or target host.

## Exact owner provenance

The contract pins:

- Organic PR #8 owner head `7f3b937b440e9870d07f7c356c5a3cbb779d0cd7`;
- transition-exit-frame observer blob `406c169963c34aed394e269f0dff2c91bb035cb8`;
- predecessor transition observer blob `1e8323b9bf6495a9f19704c217808300f3b46757`;
- unchanged source blob `fb12b759e1abfd0455bf46fd39a0eba27095796b`;
- unchanged source digest `178cd8cfb1a859bff411f60e13154109528062cf0ad2384b343d406cc0cc9d61`.

The five retained branch identities are `south-low`, `north-low`, `east-mid`, `west-high`, and `north-top`. The new family must preserve the existing scalar windows exactly while producing materially distinct owner-backed frame outputs.

## Failure bounds

The family fails closed on owner head/blob/source drift, owner frame state or branch-set drift, scalar-window drift from the retained predecessor family, non-finite or non-unit bases, lost orthogonality or right-handedness, branch-tangent reconstruction drift, promoted flex status, connected-topology promotion, weld-ring promotion, production-surface-normal promotion, Rigging/weight promotion, or automatic downstream adoption.

Order is not identity: reversing owner-frame order and authorized branch declaration order must reproduce the same canonical family digest.

## Authority boundary

Organic owns authored centerlines, radii and exact neutral exit frames. Procedural owns only deterministic conversion of those five owner frames into this stable reusable parameter convention. Geometry owns any trunk opening, bridge, weld, boolean, remesh, shared ring or connected indexed topology. Rigging owns hierarchy, joints, weights, constraints and deformation acceptance. Animation and VFX own timing/response semantics. Technical Art owns target-host transport/representation. Runtime owns controller/device/performance behavior. Art Direction and independent Visual QA own perceptual acceptance.

This family does not establish connected branch/trunk topology, a weld/shared-ring strategy, a production surface normal, biological attachment/ROM, deformation quality, physical wind, target-host acceptance, automatic adoption, UC/PF promotion, CANON, production readiness, game readiness or Procedural Design mastery.

`axm-create-me` remains coordination-only. The four AXM roots remain the merge gate: **Truth, Agency / non-domination, Continuity, Wisdom before speed**.

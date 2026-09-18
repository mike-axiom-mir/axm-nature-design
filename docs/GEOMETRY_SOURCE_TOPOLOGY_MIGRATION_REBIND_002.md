# Geometry source-topology migration rebind 002

Status: **CANDIDATE / exact-head CI required**

## Bounded question

Organic Form PR #8 advanced `east-rear-tree-neutral-001` from source digest
`0adf2cde8cfc355ec21b6fb06c6759b753300164b5f72ba029dc1b8c6d2ef307`
to `178cd8cfb1a859bff411f60e13154109528062cf0ad2384b343d406cc0cc9d61`
by adding the source-owned `north-top-branch-flex` declaration only. The
historical baseline mesh stayed byte-identical because flex metadata is not consumed
by the mesh builder.

Geometry PR #9 previously proved the cap-winding source migration against the older
Organic source identity. That PASS is preserved as historical evidence and is not
silently transferred to the newer source identity.

## Reusable rule

`SOURCE_METADATA_SUCCESSOR_STILL_REQUIRES_EXACT_TOPOLOGY_MIGRATION_REBIND_BEFORE_PASS_TRANSFER`

A source successor may be geometry-invariant and still be a distinct evidence identity.
Geometry must bind the exact new source, reconstruct the migrated mesh, and prove the
same structural result before reusing a prior topology conclusion.

## Exact identities

- current Organic owner head: `fdc9d2b6ee729728551e22fd3eafa23ad60b6c7a`;
- current source digest: `178cd8cfb1a859bff411f60e13154109528062cf0ad2384b343d406cc0cc9d61`;
- predecessor Organic head: `a4e5ee011e1d87f47866a7e6c6f4e66f57b6af12`;
- predecessor source digest: `0adf2cde8cfc355ec21b6fb06c6759b753300164b5f72ba029dc1b8c6d2ef307`;
- historical baseline mesh digest: `d7fc5deaa1c12d1d8c7d7b6dc95bf1e8544ce26140ee2e4a7d2c67a2c4133e48`;
- proven migrated mesh digest: `aa9d450a78fef722672ea9af0f9aca98b4c1a0ca3705661784f5f61f3e9b6a31`;
- Geometry oracle: `e2224d4bf88f7e68503072c884e5a726b8d0c53d`.

The rebind test reconstructs the predecessor source by removing only the newly adopted
`north-top-branch-flex` declaration from the current exact source. It requires that
this reconstructed source reproduce the predecessor source digest exactly and that
both predecessor and current source identities generate the same migrated mesh digest.
This is direct evidence of geometry invariance for this one metadata successor, not a
general rule that metadata changes are harmless.

## Ownership and handoff

Organic Form retains source/form/flex-metadata authority. Geometry retains topology
migration and source-identity binding. Rigging may continue using its pinned historical
or current source only by its own explicit rebind; this evidence does not adopt the
migrated mesh into Rigging. Technical Art, VFX, Animation, Runtime, Environment and
Art/QA retain their own exact-input adoption and acceptance gates.

## Limitations

No source merge/adoption, connected production vegetation topology, self-intersection
freedom, global outward-normal correctness, final normals/tangents/UVs/materials,
deformation quality, target-host receiving acceptance, runtime/device fitness,
collision/navigation/gameplay suitability, CANON, production readiness, game readiness
or Geometry mastery is claimed.

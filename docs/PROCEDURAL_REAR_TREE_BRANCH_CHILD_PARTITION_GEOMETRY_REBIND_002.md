# Procedural — East-Rear Branch Child Partition Geometry Receiver Rebind 002

Status: bounded review evidence only.

## Why this exists

The existing Procedural family derives five deterministic primary-branch child selections from the Organic east-rear tree: two generated branch regions plus the matching four-leaf cluster for each primary branch. That family was proven against the historical Organic-generated receiver mesh.

Geometry PR #9 now owns a distinct migrated-winding receiver. Its migration changes tapered-cap triangle ordering/winding while preserving source form, generated vertex positions, triangle membership, and generated region identity. A distinct receiver mesh identity must not silently inherit a prior Procedural PASS.

This successor therefore re-executes the existing family against the exact Geometry receiver instead of creating a second branch-selection generator.

## Exact lineage

- Organic source owner: PR #8 @ `fdc9d2b6ee729728551e22fd3eafa23ad60b6c7a`
- exact source digest: `178cd8cfb1a859bff411f60e13154109528062cf0ad2384b343d406cc0cc9d61`
- historical Organic receiver mesh: `d7fc5deaa1c12d1d8c7d7b6dc95bf1e8544ce26140ee2e4a7d2c67a2c4133e48`
- Geometry receiver: PR #9 @ `9b451ba1f65281f550a6754e18574f7ab2951e28`
- Geometry migrated receiver mesh: `aa9d450a78fef722672ea9af0f9aca98b4c1a0ca3705661784f5f61f3e9b6a31`
- predecessor Procedural family digest: `ab688f5281dc4e79770e133b49e7af3a533092acc1e0a0945bfa86e647e7b122`
- Rigging compatibility witness: PR #14 @ `f792d2369675d532be478e17c7a07f441d817c7c`, `north-top` only.

## Smallest reusable repair

`branch_partition_geometry_rebind.py` does not reconstruct Organic form or duplicate Geometry migration. It receives the two exact meshes and reuses `branch_partition_family.py`.

It requires:

1. different historical and Geometry receiver mesh identities;
2. exact generated vertex-position continuity;
3. exact unordered triangle-membership continuity;
4. exact generated region/range continuity;
5. at least one ordered triangle change so the receiver transition is real rather than relabelled;
6. exact re-execution of all five branch partitions;
7. identical branch region IDs, selected vertex indices, selected triangle indices, partition digests, and family digest across the receiver change;
8. no source, Geometry, Rigging, deformation, or downstream authority expansion.

The five outputs remain `south-low`, `north-low`, `east-mid`, `west-high`, and `north-top`. They must remain materially distinct from one another; a reverse declaration order must canonicalize to the same family digest.

## Failure boundary

Evidence fails closed on predecessor-contract drift, Organic owner drift, Geometry receiver drift, exact builder drift, either receiver mesh digest drifting, Geometry-authority transfer, automatic Rigging adoption, generated-region drift, triangle-membership drift, or mismatch with the current `north-top` Rigging witness counts.

## Truth boundary

A PASS proves only that the existing deterministic child-selection family survives this exact Geometry winding receiver migration after explicit re-execution.

It does not:

- transfer Geometry topology authority to Procedural;
- transfer the `north-top` Rigging result to four sibling branches;
- create joints, weights, motion, wind response, or deformation semantics;
- rewrite Organic source form or flex declarations;
- authorize Animation, VFX, Technical Art, Runtime, Map/Environment, Materials, Art Direction, or Visual QA adoption;
- establish CANON, production readiness, or Procedural mastery.

The four AXM roots remain the merge gate: Truth, Agency / non-domination, Continuity, and Wisdom before speed.

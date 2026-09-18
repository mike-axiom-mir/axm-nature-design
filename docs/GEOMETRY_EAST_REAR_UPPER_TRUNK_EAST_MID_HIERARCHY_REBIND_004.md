# Geometry east/rear upper-trunk -> east-mid hierarchy rebind 004

## Purpose

Rigging PR #14 advanced from the five-child shared-driver owner to an exact upper-trunk -> `east-mid` parent/child socket hierarchy. The new Rigging result is deliberately kinematic: it transports the existing child pivot/axis through a source-derived parent frame, but it does **not** define trunk mesh deformation, branch/trunk skin weighting, surface attachment, simultaneous trunk + five-branch motion, or collision.

Geometry therefore reuses PR #18 and answers one narrower structural question without changing the mesh:

> Does the exact existing `east-mid` triangle-closed child remain the same structural mesh under the new rigid hierarchical frame rebase?

## Reusable rule

`RIGID_HIERARCHICAL_FRAME_REBASE_PRESERVES_CHILD_TOPOLOGY_ONLY_AFTER_EXACT_OWNER_REBIND__NO_PARENT_MESH_DEFORMATION_OR_CLEARANCE_TRANSFER`

An unchanged source mesh does not authorize transfer of Geometry evidence across a changed Rigging owner. The exact new owner must be rebound and re-executed. A rigid child-frame proof can establish child topology/isometry continuity, but it cannot be promoted into a parent-mesh deformation, attachment, whole-tree clearance, collision, Animation, target-host or Runtime claim.

## Exact bounded check

The observer re-executes exact Rigging owner `6cf64925f0ea00737e4d3f2d4f15979c773f309d`, rebuilds the unchanged 390-vertex / 570-triangle migrated Nature receiver, and extracts only the existing `east-mid` child partition.

Required structure:

- 52 selected child vertices;
- 72 wholly owned child triangles;
- zero partially selected triangles;
- unchanged index topology;
- nondegenerate neutral owned triangles.

At all nine retained parent/child representative pairs (`-2.5/0/+2.5°` parent × `-5/0/+5°` child), Geometry recomputes the hierarchical pose and checks child pairwise distances and every owned triangle area against neutral.

The continuous structural result does **not** come from treating nine samples as exhaustive. It follows only after re-executing Rigging's continuous closed-product-domain isometry certificate: the child transform is a composition/conjugation of rigid rotations for every real parent/child parameter pair. A constant incidence/index structure plus a rigid isometry preserves distances and triangle area throughout that exact product domain.

## Historical clearance boundary

The previous Geometry PR #18 continuous five-child clearance receipt at `f4e8d408...` remains valid for its exact predecessor shared-driver owner `b4b480b4...`. It is **not transferred** to the new hierarchy owner. Rigging explicitly has not defined simultaneous upper-trunk + five-branch whole-tree motion, so Geometry has no authority to invent and certify that larger state space.

## Nonclaims

This evidence does not prove trunk mesh deformation or skin weights, branch/trunk surface attachment, the separate north-low overlap policy, simultaneous parent + five-branch motion, child-vs-parent/fixed-receiver clearance, collision, biological ROM, physical wind, Animation/VFX acceptance, target-host transport, Runtime/device behavior, gameplay, CANON, production readiness, game readiness, or Geometry mastery.

`axm-create-me` remains coordination-only. Truth, Agency / non-domination, Continuity, and Wisdom before speed remain the merge gate.

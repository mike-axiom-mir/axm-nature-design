# Rigging — north-low indexed receiver rebind 011

## Bounded question

Geometry PR #30 changed the diagnostic trunk-side `north-low` bridge receiver from the smooth analytic envelope to exact indexed faces on the generated ten-sided `mid->upper` trunk shell. Geometry explicitly does not transfer the preceding Rigging PASS. The bounded Rigging question is therefore: **does the existing north-low socket remain structurally valid when the fixed bridge boundary is rebound to that exact indexed receiver, without widening the diagnostic motion range or inventing new weights?**

## Exact lineage

- Rigging predecessor head: `efe99261459858636dbe65b16cbe1d5ad2b93a56`;
- predecessor continuous-span module blob: `96e9078afc9925dd9261ca9b3c03939fbd0e7aa2`;
- Geometry indexed-surface donor head: `8ab552710df21567cfd601af99181918e2cfadb3`;
- Geometry donor module blob: `af43e49bf6f14c050a3930d3258bc4ee50c0a9f3`;
- Geometry donor contract blob: `081e2a610a6938cb12c501b7f8a907e590a7214c`;
- exact source blob: `fb12b759e1abfd0455bf46fd39a0eba27095796b`.

The Geometry donor branches directly from the exact Rigging predecessor and changes only its own indexed-surface successor files. Rigging consumes the donor at its exact commit in CI; it does not absorb or rewrite the Geometry PR.

## Constraint

`INDEXED_SURFACE_RECEIVER_PIN_WITH_CONTINUOUS_PAIRED_SPAN_CERTIFICATE`

The existing eight branch endpoints retain diagnostic weight `1.0` under the unchanged source-derived `north-low` socket. The eight Geometry-owned indexed receiver endpoints retain diagnostic weight `0.0` and stay fixed. These are diagnostic endpoint ownership values, **not production skin weights**.

The child command remains exactly `[-5,+5]°`. Retained witnesses remain `-5 / -2.5 / 0 / +2.5 / +5°`. At each witness Rigging checks fixed-receiver drift, branch/trunk boundary edge preservation, bridge triangle area and paired span. For the continuous span claim, each moving/fixed pair is solved analytically from

`d(theta)^2 = K + 2*A*cos(theta) + 2*B*sin(theta)`

using both interval endpoints and every derivative-zero angle inside the interval. No dense sampling is used to promote the continuous span result.

## Why this is not duplicate work

The previous Rigging result was bound to the analytic trunk envelope. Geometry now measures up to millimetres of displacement when rebinding that loop to the actual indexed receiver. Since the fixed endpoints changed identity and position, the old paired-span certificate cannot be inherited. This successor reuses the existing Rigging lane and proof method but re-executes it against the exact new receiver.

## Truth boundary

A PASS here proves only: exact Geometry indexed-surface membership was consumed; the Rigging-owned branch boundary did not drift; the indexed receiver boundary remained fixed; representative bridge triangles stayed nondegenerate; and all eight paired connector spans remained strictly positive continuously through the unchanged diagnostic child interval.

It does **not** cut or weld the trunk, prove a connected junction, prove continuous triangle orientation/nondegeneracy, foldover freedom, collision/self-intersection freedom, production skinning/blending, botanical mechanics, Animation timing/interpolation/playback, Technical-Art target-host transport, Runtime/controller/device/performance acceptance, Art/Visual-QA acceptance, CANON or production readiness.

`axm-create-me` remains coordination-only. The four AXM roots remain the merge gate: Truth, Agency / non-domination, Continuity, Wisdom before speed.

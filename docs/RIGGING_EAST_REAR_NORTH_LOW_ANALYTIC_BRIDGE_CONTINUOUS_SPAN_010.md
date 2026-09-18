# Rigging — north-low analytic bridge continuous paired-span certificate

## Bounded question

The existing Rigging endpoint gate already proves that the exact eight branch-side bridge endpoints follow the existing `north-low` rigid child socket while the exact eight analytic trunk-side endpoints remain fixed. Its bridge triangle area and paired-span checks were intentionally representative-pose only.

This successor closes one smaller continuous question without changing source, topology, socket identity, weights, or motion range:

> Can any one-to-one branch/trunk bridge connector collapse to zero length between the retained `-5 / -2.5 / 0 / +2.5 / +5°` witnesses?

## Exact lineage

- Rigging endpoint predecessor: `5ca11b1577b6f4f4a2ee2b34f08ae02aa23aa079`.
- Endpoint module blob: `352e7c83e57779aef327390f5250875e26a7b610`.
- Geometry bridge donor: `14d05fdabc943376c231308001d00eb87dc23430`.
- Geometry bridge module blob: `47ba57110f43b0f3f1f29582b46a90505fa4515c`.
- Exact source blob: `fb12b759e1abfd0455bf46fd39a0eba27095796b`.

The predecessor socket pivot, source-derived axis, endpoint ownership `1.0 / 0.0`, and diagnostic child interval `[-5,+5]°` are consumed unchanged.

## Continuous proof

For each paired connector, the branch endpoint is one rigid Rodrigues rotation around the exact socket axis and the trunk endpoint is fixed. After decomposing the moving endpoint into axis-parallel and axis-perpendicular components, squared connector length has the exact form

`d(theta)^2 = K + 2*A*cos(theta) + 2*B*sin(theta)`.

On a closed angular interval, its minimum can occur only at an interval endpoint or where the derivative is zero: `theta = atan2(B,A) + k*pi`. The verifier evaluates that complete finite set independently for all eight paired spans. The retained five poses are also re-evaluated directly through the existing Rodrigues transform and must agree with the closed form.

This is therefore a continuous mathematical certificate for **paired connector non-collapse only**. It is not inferred from dense sampling.

## Scoped result

`PASS_NORTH_LOW_ANALYTIC_BRIDGE_PAIRED_SPAN_CONTINUOUS_NONCOLLAPSE_MINUS5_TO_PLUS5__HOLD_TRIANGLE_FOLDOVER_COLLISION`

Constraint:

`ANALYTIC_BRIDGE_PAIRED_SPAN_CONTINUOUS_NONCOLLAPSE_CERTIFICATE`

The exact numeric global minimum, responsible pair, and responsible child angle are generated into retained evidence by the workflow rather than pre-authored here.

## Held boundaries

A positive paired connector span does **not** prove that either of the two triangles attached to that connector stays continuously nondegenerate or orientation-preserving. It does not prove bridge foldover, collision or self-intersection freedom. It does not create an indexed trunk cut, connected branch/trunk junction, production skin-weight field, botanical mechanics, biological ROM, Animation timing/playback acceptance, Technical-Art target-host acceptance, Runtime/controller/device acceptance, Art/Visual-QA acceptance, CANON, or production readiness.

Geometry retains topology and bridge authority. Organic retains source/form authority. Rigging owns only this continuous connector-length constraint over its existing diagnostic child domain. `axm-create-me` remains coordination-only.

The merge gate remains the four AXM roots: **Truth, Agency / non-domination, Continuity, Wisdom before speed**.

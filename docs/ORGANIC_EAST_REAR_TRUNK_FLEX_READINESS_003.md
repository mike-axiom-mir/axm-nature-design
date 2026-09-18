# Organic east/rear trunk flex readiness 003

Status: **PASS_DECLARED_TRUNK_FLEX_ENVELOPES_BOUND__DEFORMATION_UNTESTED**

This is a bounded Organic Form source-readiness improvement for the existing east/rear Nature tree. It adds no source geometry, branch/trunk/leaf point, radius, flex-zone declaration, generated mesh, Geometry receiver, Rigging transform, VFX response, Animation timing, Technical-Art representation or Runtime behavior.

## Exact source identity retained

- Organic source/form owner head: `fdc9d2b6ee729728551e22fd3eafa23ad60b6c7a`
- source: `east-rear-tree-neutral-001`
- source digest: `178cd8cfb1a859bff411f60e13154109528062cf0ad2384b343d406cc0cc9d61`
- historical Organic generated mesh digest: `d7fc5deaa1c12d1d8c7d7b6dc95bf1e8544ce26140ee2e4a7d2c67a2c4133e48`
- generated source mesh: `390` vertices / `570` triangles
- immediately preceding Organic evidence head: `8caf09e8c021bbade52b04e65e3e05a388a85d13`

The prior branch-root readiness remains unchanged: all five primary branch roots retain positive neutral support and exact root-centered flex declarations, every declaration remains `DECLARED_NOT_DEFORMATION_TESTED`, and the minimum branch-root support margin remains `0.0010125868542811625 m` at `north-top`.

## Gap selected

The source already contained two additional Organic-owned trunk flex declarations, but the deformation-readiness observer previously measured only primary branch-root attachment. That left the trunk declarations structurally unbound: downstream specialists could see their metadata but had no exact source-side evidence that each declaration was centered on an authored trunk control point or even enclosed that point's authored neutral trunk radius.

The smallest useful repair is an observer/test extension, not a form edit.

## Bounded neutral-form method

For each source-declared flex zone whose ID begins `trunk-`, the Organic observer now:

1. requires the flex-zone center to match exactly one authored trunk control-point position;
2. records that exact trunk point identity and authored radius;
3. requires the declared flex-zone radius to enclose the authored neutral trunk cross-section at that point;
4. reports `neutral envelope margin = flex-zone radius - authored trunk radius`;
5. preserves the source status `DECLARED_NOT_DEFORMATION_TESTED` and refuses to infer bend range, weighting, stiffness or motion.

Exact retained current-source facts:

| flex zone | exact trunk point | flex radius | trunk radius | neutral envelope margin | status |
|---|---|---:|---:|---:|---|
| `trunk-lower-flex` | `lower` @ `[-0.02, 0.01, 0.78] m` | `0.28 m` | `0.15 m` | `0.13 m` | `DECLARED_NOT_DEFORMATION_TESTED` |
| `trunk-upper-flex` | `upper` @ `[-0.04, 0.02, 2.35] m` | `0.22 m` | `0.09 m` | `0.13 m` | `DECLARED_NOT_DEFORMATION_TESTED` |

Scoped result:

**`PASS_DECLARED_TRUNK_FLEX_ENVELOPES_BOUND__DEFORMATION_UNTESTED`**

The minimum current neutral trunk-envelope margin is therefore `0.13 m` across the two declarations.

Fail-closed controls now reject at least these source-readiness regressions:

- deleting all declared trunk flex zones -> `HOLD_TRUNK_FLEX_ZONE_COVERAGE`;
- shifting a trunk flex center away from its exact authored trunk point -> `FAIL_TRUNK_FLEX_ENVELOPE_BINDING`;
- shrinking a declared trunk flex radius below the authored neutral trunk radius -> `FAIL_TRUNK_FLEX_ENVELOPE_BINDING`;
- promoting any source flex status away from `DECLARED_NOT_DEFORMATION_TESTED` -> top-level `FAIL`.

## Downstream continuity

Fresh downstream Nature work remains separate evidence, not source authority:

- Rigging PR #14 current successor `754797a815266a643c6b08f1606eb76ba95dd8c6` provides a five-branch shared-command polarity adapter while keeping branch pivots, axes, partitions and `[-5,+5]°` diagnostic range unchanged. It does not test these trunk declarations and its command signs do not become Organic source flex semantics.
- VFX PR #19 `ba1c12dd527f1ecc6a0eb4bc0b4322f15ccad475` proves a bounded five-branch **static** visual-response envelope relative to Weather's visual direction. It does not establish trunk motion or physical wind.
- Geometry PR #18 `76c89348d63fd3523f81287767fc37527d6a8fcb` remains finite simultaneous child-child receiver evidence, not a trunk deformation proof.
- Animation, Technical Art and Runtime retain their own exact receiving identities and do not inherit this source-side readiness result automatically.

## Handoff

Rigging / Deformation may consume these two exact source declarations as better-grounded **source intent only**. A future trunk deformation experiment must independently bind the exact source identity and test any chosen pivot/axis/weight/range model. The `0.28 m` and `0.22 m` values are authored source flex-envelope metadata, not joint limits, skin weights, stiffness values or biological ranges.

VFX / Animation receive no timing, wind, sign, amplitude, cadence or natural-motion authority from this evidence. Geometry receives no topology migration or collision claim. Technical Art and Runtime receive no host/device readiness claim. Art Direction and Visual QA receive no perceptual acceptance claim.

## Truth boundary

This evidence establishes only that the two existing source-declared trunk flex envelopes are anchored to exact authored neutral trunk control points and enclose those points' authored neutral trunk radii under the stated source representation. It does **not** prove botanical or biological correctness, trunk/branch strength, stress, tissue mechanics, stiffness, fatigue, physical flex law, allowable range of motion, deformation quality, production skinning/weights, collision/self-intersection freedom, wind physics, Animation quality, target-host/device readiness, final Art/QA acceptance, CANON, production/game readiness or Organic mastery.

The four AXM roots remain the merge gate: **Truth, Agency / non-domination, Continuity, Wisdom before speed**.

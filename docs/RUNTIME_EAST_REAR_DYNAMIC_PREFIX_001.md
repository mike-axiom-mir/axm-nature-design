# Runtime east-rear existing dynamic-window proof 001

Status: **bounded Runtime position-update candidate**.

This lane consumes exact VFX PR #19 head `ba1c12dd527f1ecc6a0eb4bc0b4322f15ccad475` and its unchanged five-socket Rigging/shared-driver chain. It changes no Organic source form, Geometry receiver, Rigging pivot/axis/partition, VFX response sign, Weather semantics, Animation timing, Materials, Environment composition, gameplay or Universal Creation product code.

## Measure-before discovery

The exact receiver has `390` vertices. Rigging/VFX identify five pairwise-disjoint moving child partitions of `52` vertices each: `260` moving and `130` fixed.

The first green Runtime candidate at head `786cebc316b68e1d8cb0c8254cbfe9244f6a386c` repacked those movers into a synthetic prefix. Its own retained evidence exposed a stronger fact: the 260 moving vertices were **already** exactly one contiguous original-index run `[110, 370)`.

Runtime therefore did not promote the redundant repack. That first candidate remains historical evidence in workflow `35312645268`, artifact `10534745098`, SHA-256 `8f01b4da8941f2f0c0cb49326d2850a6ca78eab80fe24246dc5876d8e4bc5fc9`.

## Smaller successor representation

Use the existing source-index window directly:

- static original-index prefix: `[0,110)`;
- dynamic original-index window: `[110,370)` = exactly `260` vertices;
- static original-index suffix: `[370,390)`;
- vertex permutation: **none**;
- index-buffer rewrite: **none**.

For position-only float32 packets:

- full control packet: `390 * 3 * 4 = 4,680 B`;
- candidate dynamic-window packet: `260 * 3 * 4 = 3,120 B`;
- deterministic saving: `1,560 B / 33.33333333333333%` per position update;
- candidate dynamic-window regions: one.

This budget is a deterministic representation fact. It does **not** establish that a target engine performs one physical partial-buffer upload or that a target device becomes faster.

## Verification

The verifier requires:

- exact VFX PR #19 prerequisite identity;
- exact five Rigging branch identities and 52-vertex partitions;
- exact `260 moving / 130 fixed` split;
- exact moving-union equality to original indices `[110,370)`;
- no geometry reindex and no index-buffer change;
- exact reconstruction of the current full-control positions at shared driver `-5 / -2.5 / 0 / +2.5 / +5°`;
- smaller deterministic position packet;
- fail-closed rejection of window drift, reindex promotion, branch reduction and authority promotion.

CI additionally records an alternating Python proof-host benchmark comparing full `390`-position copy+deform preparation with direct `260`-position window preparation. Timing is observational only and never determines PASS.

## Visual tradeoff

Source geometry and index order are unchanged. Every retained static witness must reconstruct the exact full control positions (`0.0 m` maximum component delta).

No target-host shaded A/B is claimed here. Art Direction / Visual QA remain HOLD for receiving-scene adoption, and Runtime does not convert exact source-space positions into renderer-equivalence authority.

## Truth boundary

This lane does not establish a generic vegetation update policy, arbitrary future deformation coverage, target-host partial-buffer behavior, target-device CPU/GPU/FPS/VRAM/thermal/battery improvement, draw-call reduction, final Animation/wind behavior, collision/gameplay, Art/QA acceptance, CANON or production readiness.

`axm-create-me` remains coordination-only. The four AXM roots — Truth, Agency / non-domination, Continuity, Wisdom before speed — remain the merge gate.

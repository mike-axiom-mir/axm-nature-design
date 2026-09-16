# Procedural branch/crown cross-source probe 001

Status: DRAFT / SOURCE-BOUND PROCEDURAL EVIDENCE

## Repeated pattern

Nature now has three materially different source-owned vegetation studies that share the same authored structural vocabulary: a tapered trunk, explicit branch chains, leaf clusters and the same `axm.nature-organic-form-study/v0.1` evaluator. Re-authoring bounded branch/crown alternatives separately for each source would duplicate the same deterministic mutation mechanics.

This lane therefore reuses one **Nature-local** mutator across:

- `sapling-neutral-001`, source origin `fbc202449981f2bac153951c561ed0ed6120c936`;
- `compact-east-tree-neutral-001`, exact source `64116d63fc76daa1623b5fd5046a4e6074100bda`;
- `east-rear-tree-neutral-001`, exact source `a4e5ee011e1d87f47866a7e6c6f4e66f57b6af12`.

The generic v0.2 profile schema is `axm.nature-branch-crown-variation-family/v0.2`. The historical sapling v0.1 schema remains supported so the earlier retained evidence stays reproducible.

## What the mutator may change

Only already-authored branch/crown degrees of freedom:

- branch length scale;
- branch yaw;
- leaf length and width;
- leaf yaw and pitch;
- derived study/procedural provenance and appended truth-boundary text.

Branch attachment roots remain exact. Branch-associated leaf-cluster centers continue to follow their varied branch tips.

Every other top-level source field is treated as immutable automatically rather than by a sapling-specific field list. This includes source-specific fields such as the compact/rear `form_intent`, plus trunk, flex zones, design checks, donor provenance and Environment/Weather handoffs.

## Source-specific authority stays local

The mutator is shared, but each source profile retains its own:

- exact source repo/ref/path/digest;
- receiving envelope;
- mutation ranges;
- material-difference thresholds;
- failure policy and truth boundary.

No source is copied into this procedural branch. CI checks out the compact and rear sources at their exact revisions and reruns the existing Nature Organic Form evaluator in the receiving procedural lane.

## Evidence gate

The cross-source builder requires three retained seeds for each of the three source studies: **9 candidate outputs total**. Every candidate must:

- pass the source Organic Form structural/design checks;
- fit its exact source-specific receiving envelope;
- preserve branch attachment roots;
- preserve all non-authorized top-level source state;
- satisfy source-specific material-difference thresholds;
- retain distinct source and mesh digests.

Each source profile also receives an impossible-envelope three-attempt negative control. It must exhaust all attempts and return `HOLD_NO_VALID_VARIANT`; bounds may not be widened to manufacture a PASS.

## Placement boundary

This is evidence for one reusable **Nature-local** branch/crown mutator, not a universal vegetation language. It does not move botanical/form semantics into Universal Creation or Profession Fabric. A later Cartography pass may compare this pattern with other procedural families, but extraction requires literal shared machinery and preserved domain authority.

## Non-claims

A PASS does not establish species generation, biological growth, Art Direction or Environment acceptance, topology migration, rigging/deformation, wind response, materials/lookdev, target runtime fitness, gameplay, CANON, production readiness or Procedural Design mastery.

The four AXM roots remain the merge gate.

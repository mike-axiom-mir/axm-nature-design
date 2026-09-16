import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axm_nature_design.organic_form import digest, load_source
from axm_nature_design.procedural_family import (
    derive_candidate,
    family_digest,
    generate_accepted_variant,
    load_family,
    validate_family,
)

SOURCE = ROOT / "examples" / "sapling_neutral_001.json"
FAMILY = ROOT / "examples" / "sapling_variation_family_001.json"


class ProceduralSaplingFamilyTests(unittest.TestCase):
    def setUp(self):
        self.source = load_source(SOURCE)
        self.family = load_family(FAMILY)

    def test_same_seed_is_exactly_deterministic(self):
        a = generate_accepted_variant(self.source, self.family, 11)
        b = generate_accepted_variant(copy.deepcopy(self.source), copy.deepcopy(self.family), 11)
        self.assertEqual(a, b)
        self.assertEqual(a["receipt"]["state"], "PASS_BOUNDED_VARIANT")
        self.assertEqual(a["receipt"]["base_source_digest"], digest(self.source))
        self.assertEqual(a["receipt"]["family_digest"], family_digest(self.family))

    def test_retained_seeds_are_materially_different_and_pass_same_bounds(self):
        outputs = [generate_accepted_variant(self.source, self.family, seed) for seed in self.family["evidence_seeds"]]
        for result in outputs:
            receipt = result["receipt"]
            metrics = receipt["metrics"]
            self.assertEqual(receipt["state"], "PASS_BOUNDED_VARIANT")
            self.assertTrue(metrics["organic_checks_pass"])
            self.assertTrue(metrics["envelope_ok"])
            self.assertTrue(metrics["attachments_preserved"])
            self.assertTrue(metrics["immutable_fields_preserved"])
            self.assertGreaterEqual(metrics["moved_branch_tips"], self.family["acceptance"]["minimum_moved_branch_tips"])
            self.assertGreaterEqual(metrics["changed_leaf_blades"], self.family["acceptance"]["minimum_changed_leaf_blades"])
        self.assertEqual(len({r["receipt"]["candidate_source_digest"] for r in outputs}), len(outputs))
        self.assertEqual(len({r["receipt"]["candidate_mesh_digest"] for r in outputs}), len(outputs))

    def test_branch_attachments_and_source_owned_fields_remain_exact(self):
        result = generate_accepted_variant(self.source, self.family, 47)
        self.assertEqual(result["receipt"]["state"], "PASS_BOUNDED_VARIANT")
        candidate = result["candidate"]
        original_branches = {branch["id"]: branch for branch in self.source["branches"]}
        for branch in candidate["branches"]:
            self.assertEqual(branch["points"][0], original_branches[branch["id"]]["points"][0])
        for field in ("trunk", "flex_zones", "design_checks", "donor_provenance", "environment_handoff", "weather_handoff"):
            self.assertEqual(candidate[field], self.source[field])

    def test_branch_leaf_clusters_follow_varied_branch_tips(self):
        result = generate_accepted_variant(self.source, self.family, 101)
        self.assertEqual(result["receipt"]["state"], "PASS_BOUNDED_VARIANT")
        candidate = result["candidate"]
        clusters = {cluster["id"]: cluster for cluster in candidate["leaf_clusters"]}
        for branch in candidate["branches"]:
            cluster_id = f"{branch['id']}-leaves"
            self.assertIn(cluster_id, clusters)
            self.assertEqual(clusters[cluster_id]["center"], branch["points"][-1])

    def test_base_identity_mismatch_fails_closed(self):
        bad = copy.deepcopy(self.source)
        bad["trunk"][1]["position"][0] += 0.001
        with self.assertRaisesRegex(ValueError, "base source identity"):
            derive_candidate(bad, self.family, 11, 0)

    def test_unknown_mutation_axis_fails_closed(self):
        bad = copy.deepcopy(self.family)
        bad["bounds"]["trunk_height_scale"] = [0.9, 1.1]
        with self.assertRaisesRegex(ValueError, "declared v0.1 mutation contract"):
            validate_family(bad)

    def test_impossible_envelope_returns_hold_without_widening(self):
        impossible = copy.deepcopy(self.family)
        impossible["family_id"] = "sapling-impossible-envelope-negative-control"
        impossible["attempt_limit"] = 3
        impossible["acceptance"]["max_envelope_m"] = [1.0, 1.0, 4.0]
        result = generate_accepted_variant(self.source, impossible, 11)
        self.assertIsNone(result["candidate"])
        self.assertEqual(result["receipt"]["state"], "HOLD_NO_VALID_VARIANT")
        self.assertEqual(result["receipt"]["attempt_limit"], 3)
        self.assertEqual(len(result["receipt"]["rejected_attempts"]), 3)
        self.assertTrue(all(not row["envelope_ok"] for row in result["receipt"]["rejected_attempts"]))


if __name__ == "__main__":
    unittest.main()

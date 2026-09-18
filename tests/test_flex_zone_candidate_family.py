from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from axm_nature_design.flex_zone_candidate_family import (
    FLEX_STATUS,
    REVIEW_RELATION,
    assemble_family,
    derive_review_candidate,
    owner_backed_root_examples,
    validate_contract,
    validate_review_candidate,
)
from axm_nature_design.flex_zone_owner_adoption_rebind import (
    HISTORICAL_RELATION,
    OWNER_ADOPTED_RELATION,
    assemble_rebound_family,
    resolve_review_base,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "east_rear_tree_neutral_001.json"
CONTRACT = ROOT / "examples" / "rear_tree_root_flex_zone_review_family_001.json"


class RootFlexZoneReviewFamilyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.input_source = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.resolved = resolve_review_base(cls.input_source, cls.contract)
        cls.source = cls.resolved["review_base_source"]

    def test_contract_and_owner_examples(self):
        validate_contract(self.contract)
        examples = owner_backed_root_examples(self.source)
        self.assertEqual(4, len(examples))
        self.assertEqual(
            {"south-low", "north-low", "east-mid", "west-high"},
            {row["branch_id"] for row in examples},
        )
        self.assertEqual({0.12, 0.14}, {row["radius_m"] for row in examples})
        self.assertTrue(all(row["declaration_digest"] for row in examples))

    def test_family_has_three_distinct_source_states(self):
        family = assemble_family(self.source, self.contract)
        self.assertEqual(4, family["owner_example_count"])
        self.assertEqual(3, family["variant_count"])
        self.assertEqual(3, family["distinct_variant_source_digest_count"])
        reverse = copy.deepcopy(self.contract)
        reverse["allowed_review_radius_classes_m"] = list(reversed(reverse["allowed_review_radius_classes_m"]))
        self.assertEqual(family["family_digest"], assemble_family(self.source, reverse)["family_digest"])

    def test_local_owner_source_rebind_preserves_historical_family(self):
        historical = assemble_family(self.source, self.contract)
        rebound = assemble_rebound_family(self.input_source, self.contract)
        self.assertEqual(historical["family_digest"], rebound["family_digest"])
        self.assertEqual(historical["variant_count"], rebound["variant_count"])
        self.assertIn(rebound["input_relation"], {HISTORICAL_RELATION, OWNER_ADOPTED_RELATION})
        if rebound["input_relation"] == OWNER_ADOPTED_RELATION:
            self.assertEqual(0.12, rebound["adopted_radius_m"])
            self.assertEqual(5, rebound["current_owner_example_count"])
        else:
            self.assertIsNone(rebound["adopted_radius_m"])
            self.assertEqual(4, rebound["current_owner_example_count"])

    def test_two_owner_radius_classes_produce_distinct_review_candidates(self):
        low = derive_review_candidate(self.source, self.contract, 0.12)
        high = derive_review_candidate(self.source, self.contract, 0.14)
        self.assertEqual(REVIEW_RELATION, low["relation"])
        self.assertEqual(REVIEW_RELATION, high["relation"])
        self.assertNotEqual(low["source_candidate_digest"], high["source_candidate_digest"])
        self.assertEqual([0.01, 0.0, 3.16], low["zone"]["center"])
        self.assertEqual([0.01, 0.0, 3.16], high["zone"]["center"])
        self.assertEqual(FLEX_STATUS, low["zone"]["status"])
        self.assertEqual(FLEX_STATUS, high["zone"]["status"])
        for key in self.source:
            if key != "flex_zones":
                self.assertEqual(self.source[key], low["source_candidate"][key])
                self.assertEqual(self.source[key], high["source_candidate"][key])

    def test_non_owner_radius_rejected(self):
        with self.assertRaisesRegex(ValueError, "owner-authored"):
            derive_review_candidate(self.source, self.contract, 0.13)

    def test_existing_covered_root_rejected(self):
        contract = copy.deepcopy(self.contract)
        contract["target_branch_id"] = "west-high"
        with self.assertRaisesRegex(ValueError, "already has"):
            derive_review_candidate(self.source, contract, 0.12)

    def test_status_promotion_rejected(self):
        candidate = derive_review_candidate(self.source, self.contract, 0.12)["source_candidate"]
        candidate["flex_zones"][-1]["status"] = "DEFORMATION_READY"
        with self.assertRaisesRegex(ValueError, "drifted"):
            validate_review_candidate(self.source, candidate, self.contract, 0.12)

    def test_off_root_center_rejected(self):
        candidate = derive_review_candidate(self.source, self.contract, 0.12)["source_candidate"]
        candidate["flex_zones"][-1]["center"][0] += 0.001
        with self.assertRaisesRegex(ValueError, "exactly one"):
            validate_review_candidate(self.source, candidate, self.contract, 0.12)

    def test_automatic_adoption_rejected(self):
        contract = copy.deepcopy(self.contract)
        contract["automatic_source_adoption"] = True
        with self.assertRaisesRegex(ValueError, "automatic source adoption"):
            validate_contract(contract)


if __name__ == "__main__":
    unittest.main()

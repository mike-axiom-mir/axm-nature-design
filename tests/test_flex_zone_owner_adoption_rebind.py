from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from axm_nature_design.flex_zone_candidate_family import assemble_family, derive_review_candidate
from axm_nature_design.flex_zone_owner_adoption_rebind import (
    HISTORICAL_RELATION,
    OWNER_ADOPTED_RELATION,
    assemble_rebound_family,
    resolve_review_base,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "east_rear_tree_neutral_001.json"
CONTRACT = ROOT / "examples" / "rear_tree_root_flex_zone_review_family_001.json"
EXPECTED_HISTORICAL_FAMILY_DIGEST = "a513d5576655782e6cf333900c8cf0ab04d708021b2de43003ca92f52c23b14f"


class RootFlexZoneOwnerAdoptionRebindTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.input_source = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.review_base = resolve_review_base(cls.input_source, cls.contract)["review_base_source"]

    def test_historical_family_digest_remains_exact(self):
        family = assemble_family(self.review_base, self.contract)
        self.assertEqual(EXPECTED_HISTORICAL_FAMILY_DIGEST, family["family_digest"])
        self.assertEqual(3, family["variant_count"])
        self.assertEqual(3, family["distinct_variant_source_digest_count"])

    def test_two_materially_different_owner_adoptions_rebind_to_same_family(self):
        low = derive_review_candidate(self.review_base, self.contract, 0.12)["source_candidate"]
        high = derive_review_candidate(self.review_base, self.contract, 0.14)["source_candidate"]
        low_rebind = assemble_rebound_family(low, self.contract)
        high_rebind = assemble_rebound_family(high, self.contract)

        self.assertEqual(OWNER_ADOPTED_RELATION, low_rebind["input_relation"])
        self.assertEqual(OWNER_ADOPTED_RELATION, high_rebind["input_relation"])
        self.assertEqual(0.12, low_rebind["adopted_radius_m"])
        self.assertEqual(0.14, high_rebind["adopted_radius_m"])
        self.assertNotEqual(low_rebind["input_owner_source_digest"], high_rebind["input_owner_source_digest"])
        self.assertEqual(EXPECTED_HISTORICAL_FAMILY_DIGEST, low_rebind["family_digest"])
        self.assertEqual(EXPECTED_HISTORICAL_FAMILY_DIGEST, high_rebind["family_digest"])
        self.assertEqual(5, low_rebind["current_owner_example_count"])
        self.assertEqual(5, high_rebind["current_owner_example_count"])

    def test_historical_input_remains_a_valid_control(self):
        resolved = resolve_review_base(self.review_base, self.contract)
        self.assertEqual(HISTORICAL_RELATION, resolved["relation"])
        self.assertIsNone(resolved["adopted_radius_m"])

    def test_non_owner_adopted_radius_fails_closed(self):
        owner = derive_review_candidate(self.review_base, self.contract, 0.12)["source_candidate"]
        owner["flex_zones"][-1]["radius"] = 0.13
        with self.assertRaisesRegex(ValueError, "historical owner-backed review classes"):
            resolve_review_base(owner, self.contract)

    def test_off_root_adoption_fails_closed(self):
        owner = derive_review_candidate(self.review_base, self.contract, 0.12)["source_candidate"]
        owner["flex_zones"][-1]["center"][0] += 0.001
        with self.assertRaisesRegex(ValueError, "not centered"):
            resolve_review_base(owner, self.contract)

    def test_status_promotion_fails_closed(self):
        owner = derive_review_candidate(self.review_base, self.contract, 0.12)["source_candidate"]
        owner["flex_zones"][-1]["status"] = "DEFORMATION_READY"
        with self.assertRaisesRegex(ValueError, "promoted"):
            resolve_review_base(owner, self.contract)

    def test_duplicate_target_root_declaration_fails_closed(self):
        owner = derive_review_candidate(self.review_base, self.contract, 0.12)["source_candidate"]
        duplicate = copy.deepcopy(owner["flex_zones"][-1])
        duplicate["id"] = "north-top-branch-flex-duplicate"
        owner["flex_zones"].append(duplicate)
        with self.assertRaisesRegex(ValueError, "at most one"):
            resolve_review_base(owner, self.contract)


if __name__ == "__main__":
    unittest.main()

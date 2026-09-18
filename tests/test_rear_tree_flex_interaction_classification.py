import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axm_nature_design.organic_form import load_source
from axm_nature_design.rear_tree_flex_interaction_classification import (
    DISJOINT,
    FLEX_ENVELOPE_OVERLAP_ONLY,
    ROOT_CENTER_CONTAINED,
    evaluate,
)

SOURCE = ROOT / "examples" / "east_rear_tree_neutral_001.json"


class RearTreeFlexInteractionClassificationTests(unittest.TestCase):
    def setUp(self):
        self.source = load_source(SOURCE)

    def _pairs(self, report):
        return {
            (row["trunk_flex_zone_id"], row["branch_id"]): row
            for row in report["pairs"]
        }

    def test_current_source_separates_containment_overlap_only_and_disjoint(self):
        report = evaluate(self.source)
        self.assertEqual(
            report["state"],
            "PASS_EXACT_TRUNK_BRANCH_FLEX_INTERACTION_CLASSES__DEFORMATION_UNTESTED",
        )
        self.assertEqual(report["pair_count"], 10)
        self.assertEqual(
            report["interaction_class_counts"],
            {
                ROOT_CENTER_CONTAINED: 1,
                FLEX_ENVELOPE_OVERLAP_ONLY: 1,
                DISJOINT: 8,
            },
        )
        self.assertEqual(
            report["root_center_contained_pairs"],
            [
                {
                    "trunk_flex_zone_id": "trunk-upper-flex",
                    "branch_id": "east-mid",
                    "branch_flex_zone_id": "east-mid-branch-flex",
                }
            ],
        )
        self.assertEqual(
            report["flex_envelope_overlap_only_pairs"],
            [
                {
                    "trunk_flex_zone_id": "trunk-upper-flex",
                    "branch_id": "north-low",
                    "branch_flex_zone_id": "north-low-branch-flex",
                }
            ],
        )

    def test_north_low_is_overlap_only_with_positive_neutral_support(self):
        report = evaluate(self.source)
        row = self._pairs(report)[("trunk-upper-flex", "north-low")]
        self.assertEqual(row["interaction_class"], FLEX_ENVELOPE_OVERLAP_ONLY)
        self.assertAlmostEqual(
            row["trunk_flex_to_branch_root_center_distance_m"],
            0.3315116890850156,
            places=12,
        )
        self.assertAlmostEqual(
            row["branch_root_to_trunk_flex_boundary_signed_m"],
            0.1115116890850156,
            places=12,
        )
        self.assertAlmostEqual(
            row["declared_flex_envelope_boundary_signed_m"],
            -0.028488310914984383,
            places=12,
        )
        self.assertEqual(row["nearest_neutral_trunk_segment"], "mid->upper")
        self.assertAlmostEqual(row["nearest_neutral_trunk_segment_t"], 0.5877803557617942, places=12)
        self.assertAlmostEqual(
            row["neutral_root_centerline_distance_m"],
            0.006592784731672557,
            places=12,
        )
        self.assertAlmostEqual(
            row["neutral_local_trunk_radius_m"],
            0.10236658932714617,
            places=12,
        )
        self.assertAlmostEqual(row["branch_root_radius_m"], 0.055, places=12)
        self.assertAlmostEqual(
            row["neutral_support_margin_after_branch_radius_m"],
            0.040773804595473605,
            places=12,
        )
        self.assertTrue(row["full_branch_root_radius_supported_in_neutral_form"])

    def test_east_mid_is_root_contained_and_materially_different_from_north_low(self):
        report = evaluate(self.source)
        row = self._pairs(report)[("trunk-upper-flex", "east-mid")]
        self.assertEqual(row["interaction_class"], ROOT_CENTER_CONTAINED)
        self.assertAlmostEqual(
            row["branch_root_to_trunk_flex_boundary_signed_m"],
            -0.11369854187265342,
            places=12,
        )
        self.assertAlmostEqual(
            row["declared_flex_envelope_boundary_signed_m"],
            -0.23369854187265338,
            places=12,
        )
        self.assertEqual(row["nearest_neutral_trunk_segment"], "upper->crown")
        self.assertAlmostEqual(
            row["neutral_support_margin_after_branch_radius_m"],
            0.009731379482495778,
            places=12,
        )
        self.assertTrue(row["full_branch_root_radius_supported_in_neutral_form"])

    def test_upper_flex_radius_sensitivity_changes_classes_without_inventing_failure(self):
        candidate = copy.deepcopy(self.source)
        upper = next(
            zone for zone in candidate["flex_zones"] if zone["id"] == "trunk-upper-flex"
        )
        upper["radius"] = 0.10
        report = evaluate(candidate)
        self.assertEqual(
            report["state"],
            "PASS_EXACT_TRUNK_BRANCH_FLEX_INTERACTION_CLASSES__DEFORMATION_UNTESTED",
        )
        self.assertEqual(
            report["interaction_class_counts"],
            {
                ROOT_CENTER_CONTAINED: 0,
                FLEX_ENVELOPE_OVERLAP_ONLY: 1,
                DISJOINT: 9,
            },
        )
        pairs = self._pairs(report)
        self.assertEqual(
            pairs[("trunk-upper-flex", "north-low")]["interaction_class"],
            DISJOINT,
        )
        self.assertEqual(
            pairs[("trunk-upper-flex", "east-mid")]["interaction_class"],
            FLEX_ENVELOPE_OVERLAP_ONLY,
        )

    def test_truth_boundary_refuses_policy_or_deformation_promotion(self):
        boundary = evaluate(self.source)["truth_boundary"]
        self.assertTrue(boundary["source_metadata_spatial_relations_measured"])
        self.assertTrue(boundary["neutral_attachment_support_measured"])
        self.assertTrue(boundary["interaction_classes_are_source_geometry_only"])
        self.assertFalse(boundary["source_geometry_changed"])
        self.assertFalse(boundary["flex_zone_metadata_changed"])
        self.assertFalse(boundary["interaction_class_assigns_rig_policy"])
        self.assertFalse(boundary["neutral_attachment_support_is_deformation_proof"])
        self.assertFalse(boundary["deformation_simulated"])
        self.assertFalse(boundary["hierarchy_or_weighting_inferred"])
        self.assertFalse(boundary["biological_interpretation_claimed"])
        self.assertFalse(boundary["runtime_readiness_claimed"])

    def test_missing_exact_branch_flex_zone_fails_closed(self):
        candidate = copy.deepcopy(self.source)
        candidate["flex_zones"] = [
            zone
            for zone in candidate["flex_zones"]
            if zone["id"] != "north-low-branch-flex"
        ]
        with self.assertRaisesRegex(ValueError, "requires exactly one flex declaration"):
            evaluate(candidate)

    def test_promoted_flex_status_fails_closed(self):
        candidate = copy.deepcopy(self.source)
        candidate["flex_zones"][0]["status"] = "DEFORMATION_PROVEN"
        with self.assertRaisesRegex(ValueError, "remain unproven"):
            evaluate(candidate)

    def test_report_is_deterministic(self):
        self.assertEqual(evaluate(self.source), evaluate(copy.deepcopy(self.source)))


if __name__ == "__main__":
    unittest.main()

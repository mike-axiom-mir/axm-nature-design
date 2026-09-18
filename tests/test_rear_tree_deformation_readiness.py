import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axm_nature_design.organic_form import load_source
from axm_nature_design.rear_tree_deformation_readiness import evaluate

SOURCE = ROOT / "examples" / "east_rear_tree_neutral_001.json"


class RearTreeDeformationReadinessTests(unittest.TestCase):
    def setUp(self):
        self.source = load_source(SOURCE)

    def test_current_source_has_complete_unproven_branch_root_flex_metadata(self):
        report = evaluate(self.source)
        self.assertEqual(report["state"], "PASS_NEUTRAL_BRANCH_ROOT_SUPPORT__DEFORMATION_UNTESTED")
        self.assertTrue(report["checks"]["all_branch_roots_have_neutral_trunk_support"])
        self.assertTrue(report["checks"]["all_declared_flex_zones_remain_unproven"])
        self.assertTrue(report["checks"]["all_primary_branch_roots_have_exact_declared_flex_zone"])
        self.assertEqual(report["branch_count"], 5)
        self.assertEqual(report["branch_roots_with_exact_flex_zone"], 5)
        self.assertEqual(report["branch_roots_missing_exact_flex_zone"], [])
        self.assertGreater(report["minimum_neutral_support_margin_after_branch_radius_m"], 0.0)

    def test_exact_current_minimum_support_is_north_top_and_positive(self):
        report = evaluate(self.source)
        north_top = next(item for item in report["branch_roots"] if item["branch_id"] == "north-top")
        self.assertEqual(north_top["nearest_trunk_segment"], "crown->tip")
        self.assertAlmostEqual(
            north_top["neutral_support_margin_after_branch_radius_m"],
            0.0010125868542811625,
            places=12,
        )
        self.assertTrue(north_top["root_center_inside_local_trunk_radius"])
        self.assertTrue(north_top["full_branch_root_radius_supported_in_neutral_form"])
        self.assertEqual(north_top["exact_root_flex_zone_id"], "north-top-branch-flex")
        self.assertAlmostEqual(north_top["exact_root_flex_zone_radius_m"], 0.12, places=12)
        self.assertEqual(north_top["exact_root_flex_zone_status"], "DECLARED_NOT_DEFORMATION_TESTED")

    def test_removing_north_top_declaration_restores_coverage_hold(self):
        candidate = copy.deepcopy(self.source)
        candidate["flex_zones"] = [
            zone for zone in candidate["flex_zones"] if zone["id"] != "north-top-branch-flex"
        ]
        report = evaluate(candidate)
        self.assertEqual(report["state"], "HOLD_BRANCH_ROOT_FLEX_ZONE_COVERAGE")
        self.assertEqual(report["branch_roots_with_exact_flex_zone"], 4)
        self.assertEqual(report["branch_roots_missing_exact_flex_zone"], ["north-top"])
        self.assertFalse(report["truth_boundary"]["deformation_simulated"])
        self.assertFalse(report["truth_boundary"]["rigging_tested"])

    def test_detached_branch_root_fails_closed(self):
        bad = copy.deepcopy(self.source)
        bad["branches"][0]["points"][0][0] += 0.40
        report = evaluate(bad)
        self.assertEqual(report["state"], "FAIL")
        self.assertFalse(report["checks"]["all_branch_roots_have_neutral_trunk_support"])

    def test_promoted_flex_status_fails_closed(self):
        bad = copy.deepcopy(self.source)
        bad["flex_zones"][0]["status"] = "DEFORMATION_PROVEN"
        report = evaluate(bad)
        self.assertEqual(report["state"], "FAIL")
        self.assertFalse(report["checks"]["all_declared_flex_zones_remain_unproven"])

    def test_report_is_deterministic(self):
        self.assertEqual(evaluate(self.source), evaluate(copy.deepcopy(self.source)))

    def test_truth_boundary_remains_non_promotional(self):
        boundary = evaluate(self.source)["truth_boundary"]
        self.assertTrue(boundary["neutral_form_relationships_measured"])
        self.assertFalse(boundary["source_geometry_changed"])
        self.assertFalse(boundary["flex_zone_metadata_changed"])
        self.assertFalse(boundary["deformation_simulated"])
        self.assertFalse(boundary["rigging_tested"])
        self.assertFalse(boundary["wind_physics_tested"])
        self.assertFalse(boundary["botanical_correctness_claimed"])
        self.assertFalse(boundary["runtime_tested"])
        self.assertFalse(boundary["art_direction_accepted"])


if __name__ == "__main__":
    unittest.main()

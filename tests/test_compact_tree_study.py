import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axm_nature_design.compact_tree_study import evaluate
from axm_nature_design.organic_form import load_source

SOURCE = ROOT / "examples" / "compact_east_tree_neutral_001.json"


class CompactTreeStudyTests(unittest.TestCase):
    def setUp(self):
        self.source = load_source(SOURCE)

    def test_exact_source_passes_organic_and_reserved_envelope_gates(self):
        report = evaluate(self.source)
        self.assertEqual(report["status"], "PASS_COMPACT_SOURCE_ENVELOPE")
        self.assertTrue(report["checks"]["organic_source_pass"])
        self.assertTrue(report["checks"]["source_bounds_fit_reserved_envelope"])
        self.assertTrue(report["checks"]["clear_lower_trunk_intent_met"])
        self.assertEqual(report["receiving_context"]["replacement_target"], "proxy:nature-tree-east-b")
        self.assertEqual(report["reserved_proxy_size_m"], [1.6, 1.6, 4.0])
        self.assertTrue(all(value >= 0.0 for value in report["reserved_margin_m"]))

    def test_evaluation_is_deterministic(self):
        self.assertEqual(evaluate(self.source), evaluate(copy.deepcopy(self.source)))

    def test_smaller_reserved_envelope_fails_closed(self):
        bad = copy.deepcopy(self.source)
        bad["environment_handoff"]["proxy_size_m"] = [1.3, 1.0, 3.5]
        report = evaluate(bad)
        self.assertEqual(report["status"], "FAIL")
        self.assertFalse(report["checks"]["source_bounds_fit_reserved_envelope"])

    def test_hidden_receiver_scale_policy_is_rejected(self):
        bad = copy.deepcopy(self.source)
        bad["environment_handoff"]["placement_policy"] = "SCALE_TO_FIT"
        report = evaluate(bad)
        self.assertEqual(report["status"], "FAIL")
        self.assertFalse(report["checks"]["no_receiver_scale_or_rotation_policy"])

    def test_clear_lower_trunk_intent_is_falsifiable(self):
        bad = copy.deepcopy(self.source)
        bad["form_intent"]["minimum_clear_trunk_before_primary_branch_m"] = 1.8
        report = evaluate(bad)
        self.assertEqual(report["status"], "FAIL")
        self.assertFalse(report["checks"]["clear_lower_trunk_intent_met"])

    def test_truth_boundary_stays_non_promotional(self):
        report = evaluate(self.source)
        boundary = report["truth_boundary"]
        self.assertFalse(boundary["map_composition_tested"])
        self.assertFalse(boundary["visual_hierarchy_accepted"])
        self.assertFalse(boundary["botanical_correctness_claimed"])
        self.assertFalse(boundary["deformation_tested"])
        self.assertFalse(boundary["runtime_tested"])


if __name__ == "__main__":
    unittest.main()

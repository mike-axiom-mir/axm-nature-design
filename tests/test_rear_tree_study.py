import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axm_nature_design.organic_form import load_source
from axm_nature_design.rear_tree_study import evaluate

SOURCE = ROOT / "examples" / "east_rear_tree_neutral_001.json"
EXPECTED_SOURCE_DIGEST = "0adf2cde8cfc355ec21b6fb06c6759b753300164b5f72ba029dc1b8c6d2ef307"
EXPECTED_MESH_DIGEST = "d7fc5deaa1c12d1d8c7d7b6dc95bf1e8544ce26140ee2e4a7d2c67a2c4133e48"


class RearTreeStudyTests(unittest.TestCase):
    def setUp(self):
        self.source = load_source(SOURCE)

    def test_exact_source_passes_retained_rear_slot_gates(self):
        report = evaluate(self.source)
        self.assertEqual(report["status"], "PASS_REAR_SOURCE_ENVELOPE")
        self.assertTrue(all(report["checks"].values()))
        self.assertEqual(report["source_digest"], EXPECTED_SOURCE_DIGEST)
        self.assertEqual(report["mesh_digest"], EXPECTED_MESH_DIGEST)
        self.assertEqual(report["vertices"], 390)
        self.assertEqual(report["triangles"], 570)
        self.assertEqual(report["receiving_context"]["replacement_target"], "proxy:nature-tree-east-a")
        self.assertEqual(report["receiving_context"]["seed"], 29)
        self.assertTrue(all(value >= 0.0 for value in report["reserved_margin_m"]))

    def test_evaluation_is_deterministic(self):
        self.assertEqual(evaluate(self.source), evaluate(copy.deepcopy(self.source)))

    def test_smaller_reserved_envelope_fails_closed(self):
        bad = copy.deepcopy(self.source)
        bad["environment_handoff"]["proxy_size_m"] = [1.3, 1.0, 3.8]
        report = evaluate(bad)
        self.assertEqual(report["status"], "FAIL")
        self.assertFalse(report["checks"]["exact_retained_size_declared"])
        self.assertFalse(report["checks"]["source_bounds_fit_reserved_envelope"])

    def test_wrong_target_fails_closed(self):
        bad = copy.deepcopy(self.source)
        bad["environment_handoff"]["replacement_target"] = "proxy:nature-tree-east-b"
        report = evaluate(bad)
        self.assertEqual(report["status"], "FAIL")
        self.assertFalse(report["checks"]["exact_receiving_target_declared"])

    def test_hidden_receiver_scale_policy_is_rejected(self):
        bad = copy.deepcopy(self.source)
        bad["environment_handoff"]["placement_policy"] = "SCALE_TO_FIT"
        report = evaluate(bad)
        self.assertEqual(report["status"], "FAIL")
        self.assertFalse(report["checks"]["no_receiver_scale_or_extra_rotation_policy"])

    def test_clear_lower_trunk_intent_is_falsifiable(self):
        bad = copy.deepcopy(self.source)
        bad["form_intent"]["minimum_clear_trunk_before_primary_branch_m"] = 1.9
        report = evaluate(bad)
        self.assertEqual(report["status"], "FAIL")
        self.assertFalse(report["checks"]["clear_lower_trunk_intent_met"])

    def test_receiving_context_drift_fails_closed(self):
        bad = copy.deepcopy(self.source)
        bad["environment_handoff"]["seed"] = 83
        bad["environment_handoff"]["proxy_position_m"][0] += 0.01
        report = evaluate(bad)
        self.assertEqual(report["status"], "FAIL")
        self.assertFalse(report["checks"]["exact_retained_seed_declared"])
        self.assertFalse(report["checks"]["exact_retained_position_declared"])

    def test_truth_boundary_stays_non_promotional(self):
        boundary = evaluate(self.source)["truth_boundary"]
        self.assertFalse(boundary["map_composition_tested"])
        self.assertFalse(boundary["visual_hierarchy_accepted"])
        self.assertFalse(boundary["botanical_correctness_claimed"])
        self.assertFalse(boundary["production_topology_claimed"])
        self.assertFalse(boundary["deformation_tested"])
        self.assertFalse(boundary["runtime_tested"])


if __name__ == "__main__":
    unittest.main()

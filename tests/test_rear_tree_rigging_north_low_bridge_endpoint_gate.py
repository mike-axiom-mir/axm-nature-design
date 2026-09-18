from __future__ import annotations

import unittest
import json
from pathlib import Path

from axm_nature_design import rear_tree_rigging_north_low_bridge_endpoint_gate as subject

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"


def load_source():
    return json.loads(SOURCE_PATH.read_text(encoding="utf-8"))


class NorthLowBridgeEndpointGateTests(unittest.TestCase):
    def test_exact_endpoint_gate_passes(self):
        report = subject.evaluate(load_source())
        self.assertEqual(report["result"], subject.RESULT)
        constraint = report["endpoint_constraint"]
        self.assertEqual(constraint["mode"], "ANALYTIC_BRIDGE_TWO_BOUNDARY_DIAGNOSTIC_PIN")
        self.assertEqual(constraint["branch_boundary_vertices"], 8)
        self.assertEqual(constraint["trunk_boundary_vertices"], 8)
        self.assertEqual(constraint["interior_vertices"], 0)
        self.assertEqual(constraint["branch_endpoint_diagnostic_weight"], 1.0)
        self.assertEqual(constraint["trunk_endpoint_diagnostic_weight"], 0.0)
        self.assertFalse(constraint["production_skinning_weights_claimed"])

        poses = report["representative_pose_evidence"]
        self.assertEqual(poses["witness_count"], 5)
        self.assertLessEqual(poses["maximum_branch_endpoint_residual_m"], subject.TOL)
        self.assertLessEqual(poses["maximum_trunk_endpoint_drift_m"], subject.TOL)
        self.assertLessEqual(poses["maximum_branch_boundary_edge_length_drift_m"], subject.TOL)
        self.assertLessEqual(poses["maximum_trunk_boundary_edge_length_drift_m"], subject.TOL)
        self.assertGreater(poses["minimum_bridge_triangle_area_m2"], subject.TOL)
        self.assertGreater(poses["minimum_paired_bridge_span_m"], subject.TOL)
        self.assertGreater(poses["branch_fixed_counterfactual_m"], 1e-6)
        self.assertGreater(poses["trunk_follows_child_counterfactual_m"], 1e-6)

        continuous = report["continuous_endpoint_mapping_certificate"]
        self.assertEqual(continuous["child_domain_deg"], [-5.0, 5.0])
        self.assertTrue(continuous["continuous_for_every_real_child_command_in_domain"])
        self.assertFalse(continuous["continuous_bridge_triangle_nondegeneracy_or_collision_proven"])

    def test_exact_rigging_predecessor_is_required(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), requested_rigging_predecessor_head="0" * 40)

    def test_exact_geometry_bridge_donor_is_required(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), requested_geometry_bridge_head="0" * 40)

    def test_branch_endpoint_weight_drift_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), branch_endpoint_weight=0.5)

    def test_trunk_endpoint_weight_drift_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), trunk_endpoint_weight=1.0)

    def test_representative_schedule_rewrite_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), representative_angles_deg=(-5.0, 0.0, 5.0))

    def test_connected_topology_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_connected_branch_trunk_topology=True)

    def test_production_skinning_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_production_skinning=True)

    def test_continuous_foldover_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_continuous_bridge_foldover_clearance=True)

    def test_animation_acceptance_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_animation_acceptance=True)

    def test_technical_art_acceptance_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_technical_art_acceptance=True)

    def test_runtime_acceptance_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_runtime_acceptance=True)


if __name__ == "__main__":
    unittest.main()

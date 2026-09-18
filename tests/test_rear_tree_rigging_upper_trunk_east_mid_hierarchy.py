from __future__ import annotations

import json
import unittest
from pathlib import Path

from axm_nature_design import rear_tree_rigging_upper_trunk_east_mid_hierarchy as subject

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"


def load_source():
    return json.loads(SOURCE_PATH.read_text(encoding="utf-8"))


class UpperTrunkEastMidHierarchyRiggingTests(unittest.TestCase):
    def test_exact_parent_child_rebase_passes(self):
        report = subject.evaluate(load_source())
        self.assertEqual(report["result"], subject.RESULT)
        relation = report["organic_interaction_consumed"]
        self.assertAlmostEqual(
            relation["neutral_center_distance_m"],
            subject.EXPECTED_CENTER_DISTANCE_M,
            places=14,
        )
        self.assertAlmostEqual(
            relation["neutral_containment_margin_m"],
            subject.EXPECTED_CONTAINMENT_MARGIN_M,
            places=14,
        )
        self.assertAlmostEqual(
            relation["neutral_declared_flex_envelope_overlap_margin_m"],
            subject.EXPECTED_ENVELOPE_OVERLAP_MARGIN_M,
            places=14,
        )
        self.assertFalse(relation["north_low_overlap_policy_resolved"])

        measures = report["measurements"]
        self.assertEqual(measures["representative_parent_child_pose_count"], 9)
        self.assertLessEqual(measures["maximum_hierarchy_conjugation_residual_m"], subject.TOL)
        self.assertLessEqual(
            measures["maximum_rigid_child_pairwise_distance_drift_m"], subject.TOL
        )
        self.assertLessEqual(
            measures["maximum_transported_child_axis_projection_drift_m"], subject.TOL
        )
        self.assertLessEqual(
            measures["maximum_trunk_child_center_distance_drift_m"], subject.TOL
        )
        self.assertGreater(measures["maximum_parent_socket_displacement_m"], 1e-6)
        self.assertGreater(measures["maximum_stale_neutral_child_frame_error_m"], 1e-6)

        continuous = report["continuous_product_domain_certificate"]
        self.assertTrue(
            continuous["continuous_for_every_real_parent_child_pair_in_closed_product_domain"]
        )
        self.assertTrue(continuous["east_mid_containment_preserved_for_every_parent_angle"])
        self.assertTrue(
            continuous["declared_flex_overlap_margin_preserved_for_every_parent_angle"]
        )
        self.assertFalse(continuous["trunk_mesh_deformation_or_skin_weights_proven"])
        self.assertFalse(continuous["north_low_overlap_policy_proven"])

    def test_exact_rigging_predecessor_is_required(self):
        with self.assertRaises(ValueError):
            subject.evaluate(
                load_source(),
                requested_rigging_predecessor_head="0" * 40,
            )

    def test_exact_organic_readiness_donor_is_required(self):
        with self.assertRaises(ValueError):
            subject.evaluate(
                load_source(),
                requested_organic_readiness_head="0" * 40,
            )

    def test_parent_probe_interval_cannot_be_widened(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), parent_diagnostic_max_deg=3.0)

    def test_source_rom_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_source_rom=True)

    def test_trunk_mesh_deformation_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_trunk_mesh_deformation=True)

    def test_surface_attachment_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_surface_attachment=True)

    def test_north_low_overlap_resolution_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_north_low_overlap_resolved=True)

    def test_animation_acceptance_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_animation_acceptance=True)

    def test_runtime_acceptance_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_runtime_acceptance=True)


if __name__ == "__main__":
    unittest.main()

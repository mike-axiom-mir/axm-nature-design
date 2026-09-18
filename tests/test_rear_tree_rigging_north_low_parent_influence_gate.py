from __future__ import annotations

import json
import unittest
from pathlib import Path

from axm_nature_design import rear_tree_rigging_north_low_parent_influence_gate as subject

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"


def load_source():
    return json.loads(SOURCE_PATH.read_text(encoding="utf-8"))


class NorthLowParentInfluenceGateRiggingTests(unittest.TestCase):
    def test_exact_exclusion_gate_passes(self):
        report = subject.evaluate(load_source())
        self.assertEqual(report["result"], subject.RESULT)
        relation = report["organic_interaction_consumed"]
        self.assertEqual(relation["interaction_class"], "FLEX_ENVELOPE_OVERLAP_ONLY")
        self.assertAlmostEqual(
            relation["declared_flex_envelope_overlap_margin_m"],
            subject.EXPECTED_DECLARED_ENVELOPE_OVERLAP_M,
            places=14,
        )
        self.assertAlmostEqual(
            relation["neutral_attachment_cross_section_to_trunk_flex_boundary_signed_m"],
            subject.EXPECTED_ATTACHMENT_CROSS_SECTION_GAP_M,
            places=14,
        )
        self.assertFalse(relation["trunk_flex_intersects_neutral_attachment_cross_section"])
        self.assertFalse(
            report["rigging_constraint"]["upper_trunk_parent_influence_enabled_for_north_low"]
        )
        self.assertEqual(report["rigging_constraint"]["diagnostic_parent_weight"], 0.0)

        measures = report["measurements"]
        self.assertEqual(measures["representative_parent_child_pose_count"], 9)
        self.assertLessEqual(
            measures["maximum_gated_rigid_child_pairwise_distance_drift_m"], subject.TOL
        )
        self.assertLessEqual(measures["maximum_gated_parent_command_leak_m"], subject.TOL)
        self.assertGreater(
            measures["maximum_counterfactual_inherited_parent_socket_travel_m"], 0.01
        )
        self.assertGreater(measures["maximum_counterfactual_inherited_output_delta_m"], 0.01)

        continuous = report["continuous_product_domain_certificate"]
        self.assertTrue(continuous["continuous_for_every_real_parent_child_pair_under_gate"])
        self.assertFalse(continuous["parent_influence_weight_is_production_skin_weight"])
        self.assertFalse(continuous["source_or_biological_rom_proven"])

    def test_exact_rigging_predecessor_is_required(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), requested_rigging_predecessor_head="0" * 40)

    def test_exact_organic_interaction_donor_is_required(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), requested_organic_interaction_head="0" * 40)

    def test_parent_interval_cannot_be_widened(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), parent_diagnostic_max_deg=3.0)

    def test_forced_parent_influence_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), force_parent_influence=True)

    def test_source_rom_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_source_rom=True)

    def test_production_weighting_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_production_weighting=True)

    def test_surface_attachment_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_surface_attachment=True)

    def test_animation_acceptance_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_animation_acceptance=True)

    def test_runtime_acceptance_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_runtime_acceptance=True)


if __name__ == "__main__":
    unittest.main()

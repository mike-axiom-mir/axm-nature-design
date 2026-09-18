from __future__ import annotations

import json
import unittest
from pathlib import Path

from axm_nature_design import rear_tree_vfx_north_low_parent_gate_weather as subject

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"


def load_source():
    return json.loads(SOURCE_PATH.read_text(encoding="utf-8"))


class NorthLowParentGateWeatherVfxTests(unittest.TestCase):
    def test_exact_weather_direction_stays_stable_through_gate(self):
        report = subject.evaluate(load_source())
        self.assertEqual(report["result"], subject.RESULT)
        self.assertEqual(
            report["decision"]["state"],
            "KEEP_NORTH_LOW_MINUS5_REVIEW_POLARITY_WITH_PARENT_INFLUENCE_GATED",
        )
        self.assertEqual(report["measurements"]["parent_child_representative_count"], 9)
        self.assertAlmostEqual(
            report["measurements"]["neutral_parent_negative_child_parallel_m"],
            subject.PREDECESSOR_NORTH_LOW["negative_projection_m"],
            places=14,
        )
        self.assertAlmostEqual(
            report["measurements"]["neutral_parent_positive_child_parallel_m"],
            subject.PREDECESSOR_NORTH_LOW["positive_projection_m"],
            places=14,
        )
        self.assertEqual(
            report["measurements"]["review_only_downwind_alignment_angle_deg"], -5.0
        )
        self.assertLessEqual(
            report["measurements"]["maximum_weather_parallel_response_drift_across_parent_commands_m"],
            subject.TOL,
        )
        self.assertLessEqual(
            report["measurements"]["maximum_weather_cross_response_drift_across_parent_commands_m"],
            subject.TOL,
        )
        self.assertLessEqual(
            report["measurements"]["maximum_vertical_response_drift_across_parent_commands_m"],
            subject.TOL,
        )
        self.assertGreater(
            report["measurements"]["rigging_counterfactual_parent_inheritance_max_output_delta_m"],
            0.01,
        )

    def test_weather_direction_drift_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), wind_xy=(0.9, 0.35))

    def test_parent_range_widening_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), parent_angles_deg=(-3.0, 0.0, 3.0))

    def test_child_range_widening_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), child_angles_deg=(-6.0, 0.0, 6.0))

    def test_physical_wind_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_physical_wind=True)

    def test_animation_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_animation_adoption=True)

    def test_runtime_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_runtime_acceptance=True)

    def test_gameplay_or_physics_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_gameplay_or_physics=True)

    def test_biological_motion_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_biological_motion=True)

    def test_art_or_qa_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_art_or_qa_acceptance=True)

    def test_review_svg_is_generated_from_exact_evidence(self):
        svg = subject.build_review_svg(load_source())
        self.assertIn("Weather [1.0, 0.35]", svg)
        self.assertIn("parent -2.5 deg (gated)", svg)
        self.assertIn("parent +2.5 deg (gated)", svg)
        self.assertIn("parallel +17.58 mm", svg)


if __name__ == "__main__":
    unittest.main()

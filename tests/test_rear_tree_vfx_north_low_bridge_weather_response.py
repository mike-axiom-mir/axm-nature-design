from __future__ import annotations

import json
import unittest
from pathlib import Path

from axm_nature_design import rear_tree_vfx_north_low_bridge_weather_response as subject

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"


def load_source():
    return json.loads(SOURCE_PATH.read_text(encoding="utf-8"))


class NorthLowBridgeWeatherResponseTests(unittest.TestCase):
    def test_exact_visual_response_passes(self):
        report = subject.evaluate(load_source())
        self.assertEqual(report["result"], subject.RESULT)
        self.assertTrue(all(report["checks"].values()))
        self.assertEqual(report["receiver"]["branch_boundary_vertices"], 8)
        self.assertEqual(report["receiver"]["trunk_boundary_vertices"], 8)
        self.assertEqual(report["receiver"]["interior_vertices"], 0)
        self.assertEqual(len(report["measurements"]["rows"]), 5)
        self.assertEqual(report["measurements"]["weather_polarity_sign_violations"], 0)
        self.assertLessEqual(report["measurements"]["maximum_trunk_centroid_drift_m"], subject.TOL)
        self.assertLessEqual(report["measurements"]["maximum_bridge_vs_half_branch_centroid_residual_m"], subject.TOL)
        self.assertGreater(report["measurements"]["minus5_branch_downwind_parallel_m"], 0.0)
        self.assertGreater(report["measurements"]["minus5_bridge_downwind_parallel_m"], 0.0)
        self.assertLess(report["measurements"]["plus5_branch_upwind_parallel_m"], 0.0)
        self.assertLess(report["measurements"]["plus5_bridge_upwind_parallel_m"], 0.0)

    def test_exact_rigging_owner_head_is_required(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), requested_rigging_owner_head="0" * 40)

    def test_weather_direction_drift_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), wind_xy=(1.0, 0.36))

    def test_physical_wind_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_physical_wind=True)

    def test_production_skinning_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_production_skinning=True)

    def test_continuous_surface_safety_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_continuous_foldover_or_collision=True)

    def test_animation_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_animation_acceptance=True)

    def test_target_host_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_target_host_acceptance=True)

    def test_runtime_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_runtime_acceptance=True)

    def test_gameplay_or_physics_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_gameplay_or_physics=True)

    def test_art_or_qa_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_art_or_qa_acceptance=True)

    def test_review_svg_is_generated_from_exact_observer(self):
        svg = subject.build_review_svg(load_source())
        self.assertIn("north-low analytic bridge Weather-direction review", svg)
        self.assertIn("child -5.0 deg", svg)
        self.assertIn("child +0.0 deg", svg)
        self.assertIn("child +5.0 deg", svg)
        self.assertIn("Weather visual dir", svg)


if __name__ == "__main__":
    unittest.main()

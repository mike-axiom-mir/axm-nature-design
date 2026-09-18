from __future__ import annotations

import json
import unittest
from pathlib import Path

from axm_nature_design.rear_tree_vfx_upper_trunk_east_mid_weather_hierarchy import (
    HOLD_RESULT,
    PASS_RESULT,
    evaluate,
)


SOURCE = json.loads(Path("examples/east_rear_tree_neutral_001.json").read_text())


class VfxUpperTrunkEastMidWeatherHierarchyTests(unittest.TestCase):
    def test_exact_current_hierarchy_keeps_positive_east_mid_polarity(self):
        report = evaluate(SOURCE)
        self.assertEqual(report["result"], PASS_RESULT)
        self.assertTrue(report["decision"]["stable_positive_child_polarity"])
        self.assertEqual(
            report["decision"]["preferred_child_angle_deg_by_parent"],
            {"-2.5": 5.0, "0.0": 5.0, "2.5": 5.0},
        )
        self.assertTrue(report["vfx_predecessor"]["reproduced"])
        for row in report["measurements"]["parent_rows"]:
            self.assertGreater(row["positive_child_projection_m"], 0.0)
            self.assertLess(row["negative_child_projection_m"], 0.0)
            self.assertGreater(row["signed_child_projection_separation_m"], 0.0)

    def test_weather_direction_drift_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Weather visual-direction donor drift"):
            evaluate(SOURCE, wind_xy=(1.0, 0.36))

    def test_parent_interval_widening_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "parent diagnostic"):
            evaluate(SOURCE, parent_angles_deg=(-3.0, 0.0, 3.0))

    def test_child_interval_widening_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "child diagnostic"):
            evaluate(SOURCE, child_angles_deg=(-6.0, 0.0, 6.0))

    def test_authority_promotions_fail_closed(self):
        for kwargs in (
            {"claim_physical_wind": True},
            {"claim_animation_adoption": True},
            {"claim_runtime_controller": True},
            {"claim_gameplay": True},
            {"claim_art_acceptance": True},
        ):
            with self.assertRaises(ValueError):
                evaluate(SOURCE, **kwargs)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from axm_nature_design.rear_tree_vfx_shared_driver_response import (
    BRANCH_IDS,
    RESULT,
    SHARED_DRIVER_VALUES_DEG,
    WEATHER_WIND_XY,
    build_review_svg,
    evaluate,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"


class VfxSharedDriverResponseTests(unittest.TestCase):
    def setUp(self):
        self.source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))

    def test_exact_response_envelope_passes(self):
        before = copy.deepcopy(self.source)
        evidence = evaluate(self.source)
        self.assertEqual(self.source, before)
        self.assertEqual(evidence["result"], RESULT)
        self.assertEqual(tuple(evidence["review"]["branch_ids"]), BRANCH_IDS)
        self.assertEqual(tuple(evidence["review"]["shared_driver_values_deg"]), SHARED_DRIVER_VALUES_DEG)
        self.assertTrue(all(evidence["checks"].values()))
        self.assertFalse(any(evidence["truth_boundary"].values()))

    def test_positive_and_negative_family_response_signs(self):
        evidence = evaluate(self.source)
        poses = {float(row["shared_driver_deg"]): row for row in evidence["review"]["poses"]}
        self.assertGreater(poses[5.0]["family_weather_direction_projection_m"], 0.0)
        self.assertGreater(poses[2.5]["family_weather_direction_projection_m"], 0.0)
        self.assertEqual(poses[0.0]["family_weather_direction_projection_m"], 0.0)
        self.assertLess(poses[-2.5]["family_weather_direction_projection_m"], 0.0)
        self.assertLess(poses[-5.0]["family_weather_direction_projection_m"], 0.0)

    def test_review_svg_contains_exact_branch_family(self):
        svg = build_review_svg(self.source)
        for branch_id in BRANCH_IDS:
            self.assertIn(branch_id, svg)
        self.assertIn("Weather visual dir", svg)
        self.assertIn("shared +5", svg)
        self.assertIn("shared -5", svg)

    def test_rejects_weather_direction_drift(self):
        with self.assertRaises(ValueError):
            evaluate(self.source, wind_xy=(WEATHER_WIND_XY[1], WEATHER_WIND_XY[0]))

    def test_rejects_driver_field_drift(self):
        with self.assertRaises(ValueError):
            evaluate(self.source, shared_driver_values_deg=(-5.0, 0.0, 5.0))

    def test_rejects_authority_promotion(self):
        for kwargs in (
            {"claim_physical_wind": True},
            {"claim_animation_motion": True},
            {"claim_runtime_acceptance": True},
            {"claim_gameplay": True},
            {"claim_final_amplitude": True},
            {"claim_simultaneous_motion": True},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    evaluate(self.source, **kwargs)


if __name__ == "__main__":
    unittest.main()

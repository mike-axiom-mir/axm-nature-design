from __future__ import annotations

import json
import unittest
from pathlib import Path

from axm_nature_design.rear_tree_vfx_shared_driver_temporal_response import (
    RESULT,
    evaluate,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = json.loads((ROOT / "examples" / "east_rear_tree_neutral_001.json").read_text())


class TemporalWeatherDirectionVfxResponseTest(unittest.TestCase):
    def test_exact_review_passes(self) -> None:
        payload = evaluate(SOURCE)
        self.assertEqual(payload["result"], RESULT)
        self.assertEqual(payload["review"]["sample_count"], 41)
        self.assertEqual(payload["review"]["selected_vertex_union"], 260)
        self.assertTrue(all(payload["checks"].values()))
        self.assertTrue(payload["truth_boundary"]["source_space_temporal_visual_direction_response_proven"])
        self.assertFalse(payload["truth_boundary"]["vfx_motion_adopted"])
        self.assertFalse(payload["truth_boundary"]["physical_wind_force_speed_or_turbulence_claimed"])
        self.assertFalse(payload["truth_boundary"]["technical_art_target_host_playback_claimed"])

    def test_landmark_response_signs(self) -> None:
        payload = evaluate(SOURCE)
        samples = payload["review"]["samples"]
        for index in (0, 20, 40):
            self.assertAlmostEqual(samples[index]["family"]["parallel_m"], 0.0, places=12)
        self.assertGreater(samples[10]["family"]["parallel_m"], 0.0)
        self.assertLess(samples[30]["family"]["parallel_m"], 0.0)
        for branch in payload["review"]["branch_ids"]:
            self.assertGreater(samples[10]["branches"][branch]["parallel_m"], 0.0)
            self.assertLess(samples[30]["branches"][branch]["parallel_m"], 0.0)

    def test_donor_and_authority_drift_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "Animation owner head"):
            evaluate(SOURCE, requested_animation_head="0" * 40)
        with self.assertRaisesRegex(ValueError, "Weather owner head"):
            evaluate(SOURCE, requested_weather_owner_head="0" * 40)
        with self.assertRaisesRegex(ValueError, "Weather visual direction"):
            evaluate(SOURCE, requested_weather_direction_xy=(1.0, 0.36))
        with self.assertRaisesRegex(ValueError, "physical wind"):
            evaluate(SOURCE, claim_physical_wind=True)
        with self.assertRaisesRegex(ValueError, "natural vegetation"):
            evaluate(SOURCE, claim_natural_vegetation_motion=True)
        with self.assertRaisesRegex(ValueError, "target-engine"):
            evaluate(SOURCE, claim_target_engine_playback=True)
        with self.assertRaisesRegex(ValueError, "Art Direction"):
            evaluate(SOURCE, claim_art_or_visual_qa_acceptance=True)


if __name__ == "__main__":
    unittest.main()

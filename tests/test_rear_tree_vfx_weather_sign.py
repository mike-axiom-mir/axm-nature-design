from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from axm_nature_design.rear_tree_vfx_weather_sign import (
    RESULT,
    WEATHER_WIND_XY,
    build_review_svg,
    evaluate,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"


class RearTreeVfxWeatherSignTests(unittest.TestCase):
    def load_source(self):
        return json.loads(SOURCE_PATH.read_text(encoding="utf-8"))

    def test_exact_weather_visual_direction_resolves_one_review_only_socket_sign(self):
        source = self.load_source()
        before = copy.deepcopy(source)
        evidence = evaluate(source)
        self.assertEqual(source, before)
        self.assertEqual(evidence["result"], RESULT)
        self.assertTrue(all(evidence["checks"].values()))
        self.assertEqual(evidence["weather_visual_direction_donor"]["wind_xy"], list(WEATHER_WIND_XY))
        self.assertEqual(evidence["weather_visual_direction_donor"]["wind_semantics"], "VISUAL_DIRECTION_ONLY_NOT_PHYSICAL_WIND_SPEED")
        self.assertEqual(evidence["rigging_receiver"]["selected_vertices"], 52)
        self.assertEqual(evidence["decision"]["state"], "PASS_SIGN_COMPATIBILITY_ONLY_NO_MOTION_ADOPTION")
        preferred = evidence["decision"]["review_only_downwind_alignment_angle_deg"]
        self.assertIn(preferred, (-5.0, 5.0))
        self.assertGreater(evidence["measurements"]["signed_centroid_projection_separation_m"], 1e-9)
        self.assertGreater(
            evidence["measurements"]["preferred_centroid_downwind_projection_m"],
            evidence["measurements"]["alternate_centroid_downwind_projection_m"],
        )
        neutral = next(
            row for row in evidence["measurements"]["diagnostic_witnesses"] if row["angle_deg"] == 0.0
        )
        self.assertLessEqual(abs(neutral["centroid_downwind_projection_m"]), 1e-12)
        self.assertFalse(any(evidence["truth_boundary"].values()))

    def test_weather_direction_drift_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "donor drift"):
            evaluate(self.load_source(), wind_xy=(0.9, 0.35))

    def test_diagnostic_amplitude_or_witness_drift_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "diagnostic"):
            evaluate(self.load_source(), diagnostic_angles_deg=(-7.5, 0.0, 7.5))

    def test_physical_wind_claim_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "physical wind"):
            evaluate(self.load_source(), claim_physical_wind=True)

    def test_biological_response_claim_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "biological"):
            evaluate(self.load_source(), claim_biological_response=True)

    def test_animation_adoption_claim_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Animation"):
            evaluate(self.load_source(), claim_animation_adoption=True)

    def test_runtime_and_gameplay_claims_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "Runtime"):
            evaluate(self.load_source(), claim_runtime_controller=True)
        with self.assertRaisesRegex(ValueError, "gameplay"):
            evaluate(self.load_source(), claim_gameplay=True)

    def test_review_svg_is_deterministic_and_declares_visual_only_boundary(self):
        a = build_review_svg(self.load_source())
        b = build_review_svg(self.load_source())
        self.assertEqual(a, b)
        self.assertTrue(a.startswith("<svg"))
        self.assertIn("Weather visual direction only", a)
        self.assertIn("review-only downwind-alignment sign", a)
        self.assertIn("No wind strength/timing/amplitude/Animation/Runtime/gameplay adoption.", a)


if __name__ == "__main__":
    unittest.main()

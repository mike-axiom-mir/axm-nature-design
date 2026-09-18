from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from axm_nature_design.rear_tree_vfx_weather_sign_family import (
    BRANCH_IDS,
    DIAGNOSTIC_ANGLES_DEG,
    RESULT,
    WEATHER_WIND_XY,
    build_review_svg,
    evaluate,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"


class RearTreeVfxWeatherSignFamilyTests(unittest.TestCase):
    def setUp(self):
        self.source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))

    def test_exact_five_socket_sign_map_passes_without_mutation(self):
        before = copy.deepcopy(self.source)
        evidence = evaluate(self.source)
        self.assertEqual(self.source, before)
        self.assertEqual(evidence["result"], RESULT)
        self.assertEqual(
            list(evidence["measurements"]["review_only_downwind_alignment_angle_deg_by_branch"]),
            list(BRANCH_IDS),
        )
        self.assertTrue(all(evidence["checks"].values()))
        self.assertFalse(any(evidence["truth_boundary"].values()))
        for row in evidence["measurements"]["branch_signs"]:
            self.assertEqual(row["selected_vertices"], 52)
            self.assertEqual(
                [float(w["angle_deg"]) for w in row["diagnostic_witnesses"]],
                list(DIAGNOSTIC_ANGLES_DEG),
            )
            self.assertGreater(row["signed_centroid_projection_separation_m"], 1e-9)
            neutral = next(
                w for w in row["diagnostic_witnesses"] if float(w["angle_deg"]) == 0.0
            )
            self.assertAlmostEqual(neutral["centroid_downwind_projection_m"], 0.0, places=12)

    def test_predecessor_north_top_is_reproduced(self):
        evidence = evaluate(self.source)
        self.assertTrue(evidence["vfx_predecessor"]["reproduced"])
        self.assertEqual(
            evidence["measurements"]["review_only_downwind_alignment_angle_deg_by_branch"]["north-top"],
            5.0,
        )

    def test_review_svg_is_deterministic_and_bounded(self):
        first = build_review_svg(self.source)
        second = build_review_svg(self.source)
        self.assertEqual(first, second)
        self.assertIn("Weather visual direction only", first)
        self.assertIn("No wind force/timing/amplitude/Animation/Runtime/gameplay adoption.", first)
        for branch_id in BRANCH_IDS:
            self.assertIn(branch_id, first)

    def test_fail_closed_controls(self):
        with self.assertRaises(ValueError):
            evaluate(self.source, wind_xy=(WEATHER_WIND_XY[1], WEATHER_WIND_XY[0]))
        with self.assertRaises(ValueError):
            evaluate(self.source, branch_ids=BRANCH_IDS[:-1])
        with self.assertRaises(ValueError):
            evaluate(self.source, diagnostic_angles_deg=(-10.0, 0.0, 10.0))
        with self.assertRaises(ValueError):
            evaluate(self.source, claim_physical_wind=True)
        with self.assertRaises(ValueError):
            evaluate(self.source, claim_biological_response=True)
        with self.assertRaises(ValueError):
            evaluate(self.source, claim_animation_adoption=True)
        with self.assertRaises(ValueError):
            evaluate(self.source, claim_runtime_controller=True)
        with self.assertRaises(ValueError):
            evaluate(self.source, claim_gameplay=True)
        with self.assertRaises(ValueError):
            evaluate(self.source, claim_simultaneous_motion=True)


if __name__ == "__main__":
    unittest.main()

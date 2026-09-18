from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from axm_nature_design.rear_tree_animation import (
    RESULT,
    SAMPLE_COUNT,
    build_review_svg,
    evaluate,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"


class RearTreeAnimationTests(unittest.TestCase):
    def load_source(self):
        return json.loads(SOURCE_PATH.read_text(encoding="utf-8"))

    def test_exact_rig_socket_receives_one_closed_diagnostic_pulse(self):
        source = self.load_source()
        before = copy.deepcopy(source)
        evidence = evaluate(source)
        self.assertEqual(source, before)
        self.assertEqual(evidence["result"], RESULT)
        self.assertTrue(all(evidence["checks"].values()))
        self.assertEqual(evidence["motion"]["endpoint_inclusive_samples"], SAMPLE_COUNT)
        self.assertEqual(evidence["motion"]["visible_repeating_samples"], 40)
        samples = evidence["samples"]
        self.assertEqual(len(samples), 41)
        self.assertEqual([samples[i]["angle_deg"] for i in (0, 10, 20, 30, 40)], [0.0, 5.0, 0.0, -5.0, 0.0])
        self.assertEqual(samples[0]["pose_digest"], samples[40]["pose_digest"])
        self.assertNotEqual(samples[0]["pose_digest"], samples[10]["pose_digest"])
        self.assertNotEqual(samples[0]["pose_digest"], samples[30]["pose_digest"])
        m = evidence["measurements"]
        self.assertLessEqual(m["maximum_fixed_vertex_drift_m"], 1e-12)
        self.assertLessEqual(m["maximum_pivot_vertex_drift_m"], 1e-12)
        self.assertLessEqual(m["maximum_selected_pairwise_distance_drift_m"], 1e-12)
        self.assertLessEqual(m["maximum_selected_axis_projection_drift_m"], 1e-12)
        self.assertLessEqual(m["endpoint_closure_m"], 1e-12)
        self.assertLessEqual(m["wrap_step_residual_m"], 1e-12)
        self.assertLessEqual(m["angular_antisymmetry_error_deg"], 1e-12)
        self.assertLessEqual(m["maximum_rigging_witness_metric_residual"], 1e-12)
        self.assertGreater(m["maximum_selected_vertex_displacement_m"], 0.08)
        self.assertLess(m["maximum_selected_vertex_displacement_m"], 0.083)
        self.assertGreater(m["maximum_adjacent_selected_vertex_step_m"], 0.0)
        self.assertLess(m["maximum_adjacent_angular_step_deg"], 0.9)

    def test_duration_retime_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "duration"):
            evaluate(self.load_source(), duration_s=0.5)

    def test_sample_rate_retime_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "sample-rate"):
            evaluate(self.load_source(), sample_rate_hz=60)

    def test_rigging_probe_range_cannot_be_widened(self):
        with self.assertRaisesRegex(ValueError, "widen"):
            evaluate(self.load_source(), amplitude_deg=7.5)

    def test_wind_semantics_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "wind"):
            evaluate(self.load_source(), claim_wind_motion=True)

    def test_biological_rom_semantics_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "biological"):
            evaluate(self.load_source(), claim_biological_rom=True)

    def test_runtime_controller_acceptance_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Runtime"):
            evaluate(self.load_source(), claim_runtime_controller=True)

    def test_gameplay_acceptance_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "gameplay"):
            evaluate(self.load_source(), claim_gameplay_acceptance=True)

    def test_review_svg_is_deterministic_and_contains_five_pose_labels(self):
        a = build_review_svg(self.load_source())
        b = build_review_svg(self.load_source())
        self.assertEqual(a, b)
        self.assertTrue(a.startswith("<svg"))
        self.assertEqual(a.count(" deg</text>"), 5)
        self.assertIn("+5.0 deg", a)
        self.assertIn("-5.0 deg", a)


if __name__ == "__main__":
    unittest.main()

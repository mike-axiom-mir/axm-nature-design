from __future__ import annotations

import json
import unittest
from pathlib import Path

from axm_nature_design import rear_tree_rigging_north_low_attachment_representation_gate as attachment_gate
from axm_nature_design import rear_tree_vfx_north_low_parent_stress_weather as subject


class NorthLowParentStressWeatherVFXTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(Path("examples/east_rear_tree_neutral_001.json").read_text(encoding="utf-8"))
        cls.geometry_contract = attachment_gate.expected_geometry_contract()

    def test_temporal_weather_response_passes(self):
        report = subject.evaluate(self.source, self.geometry_contract)
        self.assertEqual(report["result"], subject.RESULT)
        m = report["measurements"]
        self.assertEqual(m["sample_count"], 41)
        self.assertEqual(m["owner_pose_digest_mismatches"], 0)
        self.assertEqual(m["weather_polarity_sign_violations"], 0)
        self.assertLessEqual(m["neutral_weather_parallel_error_m"], subject.TOL)
        self.assertLessEqual(m["endpoint_weather_parallel_error_m"], subject.TOL)
        self.assertGreater(m["minus5_peak_downwind_parallel_m"], 0.0)
        self.assertLess(m["plus5_peak_upwind_parallel_m"], 0.0)
        self.assertGreater(m["maximum_accepted_vs_wrong_parent_weather_parallel_delta_m"], 1e-6)
        self.assertGreater(m["maximum_accepted_vs_wrong_parent_vertex_delta_m"], 1e-6)

    def test_visual_only_authority_boundary(self):
        report = subject.evaluate(self.source, self.geometry_contract)
        truth = report["truth_boundary"]
        self.assertTrue(truth["source_space_visual_response_evidence_only"])
        self.assertFalse(truth["physical_wind_claimed"])
        self.assertFalse(truth["botanical_or_biological_motion_claimed"])
        self.assertFalse(truth["target_engine_playback_claimed"])
        self.assertFalse(truth["runtime_controller_or_device_claimed"])
        self.assertFalse(truth["gameplay_or_physics_claimed"])
        self.assertFalse(truth["art_direction_or_visual_qa_acceptance_claimed"])

    def assert_rejected(self, **kwargs):
        with self.assertRaises(ValueError):
            subject.evaluate(self.source, self.geometry_contract, **kwargs)

    def test_rejects_weather_and_authority_drift(self):
        self.assert_rejected(wind_xy=(1.0, 0.36))
        self.assert_rejected(claim_physical_wind=True)
        self.assert_rejected(claim_botanical_motion=True)
        self.assert_rejected(claim_animation_authorship=True)
        self.assert_rejected(claim_target_engine_playback=True)
        self.assert_rejected(claim_runtime_acceptance=True)
        self.assert_rejected(claim_gameplay_or_physics=True)
        self.assert_rejected(claim_art_or_qa_acceptance=True)


if __name__ == "__main__":
    unittest.main()

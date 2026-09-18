from __future__ import annotations

import json
import unittest
from pathlib import Path

from axm_nature_design import rear_tree_animation_north_low_parent_exclusion_temporal_rebind as subject
from axm_nature_design import rear_tree_rigging_north_low_attachment_representation_gate as attachment_gate


class NorthLowParentExclusionTemporalRebindTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(Path("examples/east_rear_tree_neutral_001.json").read_text(encoding="utf-8"))
        cls.geometry_contract = attachment_gate.expected_geometry_contract()

    def test_exact_temporal_rebind_passes(self):
        report = subject.evaluate(self.source, self.geometry_contract)
        self.assertEqual(report["result"], subject.RESULT)
        self.assertEqual(report["measurements"]["sample_count"], 41)
        self.assertEqual(report["motion_scope"]["attachment_mode"], "DETACHED_DIAGNOSTIC_CHILD_SOCKET_ONLY")
        self.assertEqual(report["motion_scope"]["diagnostic_parent_weight"], 0.0)
        self.assertLessEqual(report["measurements"]["maximum_parent_command_leak_m"], subject.TOL)
        self.assertLessEqual(report["measurements"]["endpoint_closure_m"], subject.TOL)
        self.assertLessEqual(report["measurements"]["repeat_seam_residual_m"], subject.TOL)
        self.assertGreater(report["measurements"]["maximum_counterfactual_inherited_parent_output_delta_m"], 1e-6)
        self.assertFalse(report["truth_boundary"]["target_engine_playback_claimed"])
        self.assertFalse(report["truth_boundary"]["runtime_controller_state_machine_input_or_device_claimed"])
        self.assertFalse(report["truth_boundary"]["physics_or_gameplay_claimed"])

    def test_landmarks_preserve_previous_north_low_child_timing(self):
        report = subject.evaluate(self.source, self.geometry_contract)
        samples = report["samples"]
        self.assertEqual([samples[i]["north_low_child_angle_deg"] for i in (0, 10, 20, 30, 40)], [0.0, -5.0, 0.0, 5.0, 0.0])
        self.assertEqual([samples[i]["previous_shared_driver_deg"] for i in (0, 10, 20, 30, 40)], [0.0, 5.0, 0.0, -5.0, 0.0])
        self.assertEqual([samples[i]["upper_trunk_parent_stress_command_deg"] for i in (0, 10, 20, 30, 40)], [0.0, 2.5, 0.0, -2.5, 0.0])

    def assert_rejected(self, **kwargs):
        with self.assertRaises(ValueError):
            subject.evaluate(self.source, self.geometry_contract, **kwargs)

    def test_rejects_timing_and_authority_drift(self):
        self.assert_rejected(duration_s=0.9)
        self.assert_rejected(sample_rate_hz=30)
        self.assert_rejected(child_amplitude_deg=5.1)
        self.assert_rejected(parent_stress_amplitude_deg=2.6)
        self.assert_rejected(inherit_parent_frame=True)
        self.assert_rejected(claim_wind_motion=True)
        self.assert_rejected(claim_biological_rom=True)
        self.assert_rejected(claim_connected_attachment=True)
        self.assert_rejected(claim_production_skinning=True)
        self.assert_rejected(claim_target_engine_playback=True)
        self.assert_rejected(claim_runtime_controller=True)
        self.assert_rejected(claim_gameplay_acceptance=True)


if __name__ == "__main__":
    unittest.main()

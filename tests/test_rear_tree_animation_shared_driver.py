from __future__ import annotations

import json
import unittest
from pathlib import Path

from axm_nature_design.rear_tree_animation_shared_driver import (
    AMPLITUDE_DEG,
    DURATION_S,
    RESULT,
    SAMPLE_COUNT,
    SAMPLE_RATE_HZ,
    evaluate,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"
CONTRACT_PATH = ROOT / "contracts" / "east-rear-shared-driver-animation-loop-003.json"


class RearTreeAnimationSharedDriverTests(unittest.TestCase):
    def load_source(self):
        return json.loads(SOURCE_PATH.read_text(encoding="utf-8"))

    def load_contract(self):
        return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_shared_driver_loop_exercises_all_five_children_with_owner_invariants(self):
        evidence = evaluate(self.load_source())
        self.assertEqual(evidence["result"], RESULT)
        self.assertEqual(len(evidence["samples"]), SAMPLE_COUNT)
        self.assertEqual(evidence["receiver"]["selected_vertex_union"], 260)
        self.assertEqual(evidence["receiver"]["globally_fixed_vertices"], 130)
        self.assertTrue(all(evidence["checks"].values()))
        self.assertLessEqual(evidence["measurements"]["maximum_composition_order_vertex_delta_m"], 1e-12)
        self.assertLessEqual(evidence["measurements"]["maximum_globally_fixed_vertex_drift_m"], 1e-12)
        self.assertLessEqual(evidence["measurements"]["maximum_pivot_vertex_drift_m"], 1e-12)
        self.assertLessEqual(evidence["measurements"]["maximum_rigid_child_pairwise_distance_drift_m"], 1e-12)
        self.assertLessEqual(evidence["measurements"]["maximum_child_axis_projection_drift_m"], 1e-12)
        self.assertLessEqual(evidence["measurements"]["endpoint_closure_m"], 1e-12)
        self.assertLessEqual(evidence["measurements"]["wrap_step_residual_m"], 1e-12)
        self.assertLessEqual(evidence["measurements"]["maximum_owner_replay_metric_residual"], 1e-12)

    def test_landmarks_preserve_mixed_rigging_polarity(self):
        evidence = evaluate(self.load_source())
        self.assertEqual(evidence["samples"][0]["shared_driver_deg"], 0.0)
        self.assertEqual(evidence["samples"][10]["shared_driver_deg"], 5.0)
        self.assertEqual(evidence["samples"][20]["shared_driver_deg"], 0.0)
        self.assertEqual(evidence["samples"][30]["shared_driver_deg"], -5.0)
        self.assertEqual(evidence["samples"][40]["shared_driver_deg"], 0.0)
        self.assertEqual(
            evidence["samples"][10]["local_angles_deg"],
            {
                "south-low": 5.0,
                "north-low": -5.0,
                "east-mid": 5.0,
                "west-high": -5.0,
                "north-top": 5.0,
            },
        )
        self.assertEqual(
            evidence["samples"][30]["local_angles_deg"],
            {
                "south-low": -5.0,
                "north-low": 5.0,
                "east-mid": -5.0,
                "west-high": 5.0,
                "north-top": -5.0,
            },
        )
        self.assertTrue(
            all(
                evidence["samples"][10]["per_branch"][branch_id]["maximum_selected_vertex_displacement_m"] > 0.0
                for branch_id in evidence["receiver"]["branch_ids"]
            )
        )

    def test_timing_identity_matches_previous_animation_family(self):
        evidence = evaluate(self.load_source())
        motion = evidence["motion"]
        self.assertEqual(motion["duration_s"], DURATION_S)
        self.assertEqual(motion["sample_rate_hz"], SAMPLE_RATE_HZ)
        self.assertEqual(motion["endpoint_inclusive_samples"], SAMPLE_COUNT)
        self.assertEqual(motion["visible_repeating_samples"], 40)
        self.assertEqual(motion["shared_driver_interval_deg"], [-AMPLITUDE_DEG, AMPLITUDE_DEG])
        self.assertLessEqual(evidence["measurements"]["shared_driver_antisymmetry_error_deg"], 1e-12)

    def test_contract_keeps_downstream_authority_false(self):
        contract = self.load_contract()
        self.assertEqual(contract["rigging_owner"]["head"], "bbc6584accb91204b02b8d11193768556da036e5")
        self.assertEqual(contract["previous_animation"]["head"], "b0771b3319b783103c8e4677d062c00419df7559")
        self.assertTrue(contract["sampled_simultaneous_motion_claimed"])
        self.assertFalse(contract["continuous_collision_clearance_claimed"])
        self.assertFalse(contract["physical_wind_claimed"])
        self.assertFalse(contract["target_engine_playback_claimed"])
        self.assertFalse(contract["runtime_acceptance_claimed"])
        self.assertFalse(contract["gameplay_acceptance_claimed"])

    def test_motion_and_authority_inflation_fail_closed(self):
        source = self.load_source()
        with self.assertRaisesRegex(ValueError, "duration drift"):
            evaluate(source, duration_s=1.1)
        with self.assertRaisesRegex(ValueError, "sample-rate drift"):
            evaluate(source, sample_rate_hz=60)
        with self.assertRaisesRegex(ValueError, "may not widen"):
            evaluate(source, amplitude_deg=5.25)
        with self.assertRaisesRegex(ValueError, "wind-motion"):
            evaluate(source, claim_wind_motion=True)
        with self.assertRaisesRegex(ValueError, "biological ROM"):
            evaluate(source, claim_biological_rom=True)
        with self.assertRaisesRegex(ValueError, "continuous collision"):
            evaluate(source, claim_continuous_collision_clearance=True)
        with self.assertRaisesRegex(ValueError, "target-engine"):
            evaluate(source, claim_target_engine_playback=True)
        with self.assertRaisesRegex(ValueError, "Runtime controller"):
            evaluate(source, claim_runtime_controller=True)
        with self.assertRaisesRegex(ValueError, "gameplay"):
            evaluate(source, claim_gameplay_acceptance=True)


if __name__ == "__main__":
    unittest.main()

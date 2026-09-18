from __future__ import annotations

import json
import math
import unittest
from pathlib import Path

from axm_nature_design.rear_tree_geometry_shared_driver_continuous_clearance import (
    EXPECTED_CROSS_TRIANGLE_PAIR_COUNT,
    HOLD_BUDGET,
    RESULT,
    RIGGING_CONTINUOUS_HEAD,
    SHARED_DRIVER_MAX_DEG,
    SHARED_DRIVER_MIN_DEG,
    _full_interval_motion_bound,
    evaluate,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = json.loads((ROOT / "examples" / "east_rear_tree_neutral_001.json").read_text(encoding="utf-8"))


class ContinuousSharedDriverGeometryClearanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = evaluate(SOURCE)

    def test_all_cross_branch_triangle_trajectories_are_certified(self):
        evidence = self.evidence
        self.assertEqual(evidence["result"], RESULT)
        self.assertEqual(evidence["scope"]["shared_driver_interval_deg"], [-5.0, 5.0])
        self.assertEqual(evidence["scope"]["branch_pair_count"], 10)
        self.assertEqual(evidence["scope"]["triangles_per_child"], 72)
        self.assertEqual(
            evidence["scope"]["cross_branch_triangle_pair_trajectories"],
            EXPECTED_CROSS_TRIANGLE_PAIR_COUNT,
        )
        self.assertEqual(
            evidence["measurements"]["triangle_pair_certificates_performed"],
            EXPECTED_CROSS_TRIANGLE_PAIR_COUNT,
        )
        self.assertEqual(evidence["measurements"]["uncertified_triangle_pair_count"], 0)
        self.assertGreater(evidence["measurements"]["minimum_certified_slack_m"], 0.02)
        self.assertTrue(evidence["truth_boundary"]["continuous_cross_branch_separation_proven"])
        self.assertFalse(evidence["prior_evidence"]["finite_static_witnesses_promoted_to_continuous"])

    def test_motion_bound_matches_rigid_rotation_chord_bound(self):
        expected = 2.0 * math.sin(math.radians(5.0) * 0.5)
        self.assertAlmostEqual(_full_interval_motion_bound(1.0), expected, places=15)
        self.assertEqual(SHARED_DRIVER_MIN_DEG, -5.0)
        self.assertEqual(SHARED_DRIVER_MAX_DEG, 5.0)

    def test_work_budget_fails_closed_before_pair_scan(self):
        hold = evaluate(
            SOURCE,
            max_triangle_pair_certificates=EXPECTED_CROSS_TRIANGLE_PAIR_COUNT - 1,
        )
        self.assertEqual(hold["result"], HOLD_BUDGET)
        self.assertEqual(hold["work"]["triangle_pair_certificates_performed"], 0)
        self.assertFalse(hold["work"]["partial_clearance_verdict_exposed"])
        self.assertFalse(hold["truth_boundary"]["continuous_cross_branch_separation_proven"])

    def test_owner_and_scope_promotions_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "Rigging donor head drift"):
            evaluate(SOURCE, requested_rigging_head="0" * 40)
        with self.assertRaisesRegex(ValueError, "exact Rigging interval"):
            evaluate(SOURCE, requested_interval_deg=(-5.0, 5.1))
        with self.assertRaisesRegex(ValueError, "child-vs-fixed-receiver"):
            evaluate(SOURCE, claim_child_fixed_receiver_clearance=True)
        with self.assertRaisesRegex(ValueError, "physical collision/gameplay"):
            evaluate(SOURCE, claim_physical_collision_or_gameplay=True)
        with self.assertRaisesRegex(ValueError, "target-host/Runtime"):
            evaluate(SOURCE, claim_target_host_or_runtime=True)
        self.assertEqual(len(RIGGING_CONTINUOUS_HEAD), 40)


if __name__ == "__main__":
    unittest.main()

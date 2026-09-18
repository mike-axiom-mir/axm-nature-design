from __future__ import annotations

import json
import math
import unittest
from pathlib import Path

from axm_nature_design import rear_tree_rigging_north_low_bridge_continuous_span as subject

ROOT = Path(__file__).resolve().parents[1]
SOURCE = json.loads((ROOT / "examples/east_rear_tree_neutral_001.json").read_text(encoding="utf-8"))


class NorthLowBridgeContinuousSpanRiggingTests(unittest.TestCase):
    def test_exact_continuous_span_certificate_passes(self):
        report = subject.evaluate(SOURCE)
        self.assertEqual(report["result"], subject.RESULT)
        cert = report["continuous_paired_span_certificate"]
        self.assertEqual(cert["child_domain_deg"], [-5.0, 5.0])
        self.assertEqual(cert["paired_span_count"], 8)
        self.assertGreater(cert["global_minimum_span_m"], subject.TOL)
        self.assertLessEqual(
            cert["global_minimum_span_m"],
            cert["representative_minimum_span_m"] + 1e-12,
        )
        self.assertLessEqual(cert["maximum_closed_form_vs_direct_residual_m"], 1e-10)
        self.assertTrue(all(report["checks"].values()))

    def test_closed_form_minimum_is_not_a_sampling_claim(self):
        report = subject.evaluate(SOURCE)
        for row in report["pair_certificates"]:
            self.assertGreaterEqual(row["candidate_count"], 2)
            self.assertGreater(row["minimum_span_m"], subject.TOL)
            # Dense points are only a test oracle: none may beat the analytic stationary-point minimum.
            moving_index = row["pair_index"]
            candidate = subject.endpoint_gate.geometry_bridge.build_candidate(SOURCE)
            points = candidate["bridge_only"]["vertices"]
            moving = points[moving_index]
            fixed = points[8 + moving_index]
            predecessor = subject.endpoint_gate.evaluate(SOURCE)
            pivot = predecessor["socket_identity"]["pivot_m"]
            axis = predecessor["socket_identity"]["source_derived_axis"]
            for step in range(401):
                angle = -5.0 + 10.0 * step / 400.0
                posed = subject.endpoint_gate.historical._rotate_about_axis(moving, pivot, axis, angle)
                sampled = subject._distance(posed, fixed)
                self.assertGreaterEqual(sampled + 1e-12, row["minimum_span_m"])

    def test_negative_controls_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "predecessor head drift"):
            subject.evaluate(SOURCE, requested_rigging_endpoint_predecessor_head="0" * 40)
        with self.assertRaisesRegex(ValueError, "may not widen"):
            subject.evaluate(SOURCE, requested_domain_deg=(-6.0, 6.0))
        with self.assertRaisesRegex(ValueError, "triangle nondegeneracy"):
            subject.evaluate(SOURCE, claim_continuous_triangle_nondegeneracy=True)
        with self.assertRaisesRegex(ValueError, "foldover/collision"):
            subject.evaluate(SOURCE, claim_continuous_foldover_or_collision_clearance=True)
        with self.assertRaisesRegex(ValueError, "connected"):
            subject.evaluate(SOURCE, claim_connected_topology=True)
        with self.assertRaisesRegex(ValueError, "production skinning"):
            subject.evaluate(SOURCE, claim_production_skinning=True)
        with self.assertRaisesRegex(ValueError, "Animation"):
            subject.evaluate(SOURCE, claim_animation_acceptance=True)
        with self.assertRaisesRegex(ValueError, "Technical Art"):
            subject.evaluate(SOURCE, claim_technical_art_acceptance=True)
        with self.assertRaisesRegex(ValueError, "Runtime"):
            subject.evaluate(SOURCE, claim_runtime_acceptance=True)

    def test_stationary_solver_handles_interior_extremum(self):
        # Synthetic coefficient sanity check independent of Nature geometry.
        # d^2 = 2 - 2*cos(theta) has its minimum at zero inside [-5,+5].
        candidates = subject._critical_angles_rad(-1.0, 0.0, math.radians(-5), math.radians(5))
        self.assertTrue(any(abs(value) <= 1e-15 for value in candidates))


if __name__ == "__main__":
    unittest.main()

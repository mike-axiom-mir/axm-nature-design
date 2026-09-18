from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from axm_nature_design import rear_tree_rigging_north_low_indexed_surface_rebind as subject

ROOT = Path(__file__).resolve().parents[1]
SOURCE = json.loads((ROOT / "examples/east_rear_tree_neutral_001.json").read_text(encoding="utf-8"))


def synthetic_indexed_donor():
    """Math fixture only; hosted evidence uses the exact Geometry PR #30 donor."""
    analytic = subject.analytic_span.endpoint_gate.geometry_bridge.build_candidate(SOURCE)
    candidate = {"bridge_only": copy.deepcopy(analytic["bridge_only"])}
    for point in candidate["bridge_only"]["vertices"][8:]:
        point[0] += 0.001
    source_digest = subject.analytic_span.evaluate(SOURCE)["source_digest"]
    report = {
        "result": subject.GEOMETRY_DONOR_RESULT,
        "source_digest": source_digest,
        "provenance": {"rigging_owner_head": subject.RIGGING_PREDECESSOR_HEAD},
        "indexed_surface_binding": {
            "loop_vertices": 8,
            "memberships": [{"triangle_index": 80 + i} for i in range(8)],
            "parameter_space_self_intersections": 0,
        },
        "truth_boundary": {
            "neutral_indexed_surface_membership_proven": True,
            "indexed_trunk_cut_integrated": False,
            "connected_branch_trunk_indexed_topology_proven": False,
            "analytic_rigging_pass_transferred": False,
        },
    }
    return report, candidate


class NorthLowIndexedSurfaceRiggingRebindTests(unittest.TestCase):
    def test_rebind_math_and_continuous_span_certificate_pass(self):
        geometry_report, geometry_candidate = synthetic_indexed_donor()
        report = subject.evaluate(SOURCE, geometry_report, geometry_candidate)
        self.assertEqual(report["result"], subject.RESULT)
        self.assertEqual(report["continuous_paired_span_certificate"]["child_domain_deg"], [-5.0, 5.0])
        self.assertEqual(report["continuous_paired_span_certificate"]["paired_span_count"], 8)
        self.assertGreater(report["continuous_paired_span_certificate"]["global_minimum_span_m"], subject.TOL)
        self.assertGreater(report["representative_pose_evidence"]["minimum_bridge_triangle_area_m2"], subject.TOL)
        self.assertEqual(report["representative_pose_evidence"]["maximum_fixed_indexed_receiver_drift_m"], 0.0)
        self.assertLessEqual(report["receiver_rebind"]["branch_endpoint_delta_from_analytic_m"], subject.TOL)
        self.assertGreater(report["receiver_rebind"]["minimum_fixed_receiver_delta_from_analytic_m"], 1e-6)
        self.assertTrue(all(report["checks"].values()))

    def test_dense_span_oracle_does_not_beat_analytic_minimum(self):
        geometry_report, geometry_candidate = synthetic_indexed_donor()
        report = subject.evaluate(SOURCE, geometry_report, geometry_candidate)
        points = geometry_candidate["bridge_only"]["vertices"]
        pivot = report["socket_identity"]["pivot_m"]
        axis = report["socket_identity"]["source_derived_axis"]
        rotate = subject.analytic_span.endpoint_gate.historical._rotate_about_axis
        for row in report["pair_certificates"]:
            index = row["pair_index"]
            moving = points[index]
            fixed = points[8 + index]
            for step in range(201):
                angle = -5.0 + 10.0 * step / 200.0
                sampled = subject._distance(rotate(moving, pivot, axis, angle), fixed)
                self.assertGreaterEqual(sampled + 1e-12, row["minimum_span_m"])

    def test_identity_and_authority_controls_fail_closed(self):
        geometry_report, geometry_candidate = synthetic_indexed_donor()
        with self.assertRaisesRegex(ValueError, "predecessor head drift"):
            subject.evaluate(SOURCE, geometry_report, geometry_candidate, requested_rigging_predecessor_head="0" * 40)
        with self.assertRaisesRegex(ValueError, "donor head drift"):
            subject.evaluate(SOURCE, geometry_report, geometry_candidate, requested_geometry_donor_head="0" * 40)
        with self.assertRaisesRegex(ValueError, "module blob drift"):
            subject.evaluate(SOURCE, geometry_report, geometry_candidate, requested_geometry_donor_module_blob="0" * 40)
        with self.assertRaisesRegex(ValueError, "may not widen"):
            subject.evaluate(SOURCE, geometry_report, geometry_candidate, requested_domain_deg=(-6.0, 6.0))
        with self.assertRaisesRegex(ValueError, "cut the trunk"):
            subject.evaluate(SOURCE, geometry_report, geometry_candidate, claim_indexed_trunk_cut_integrated=True)
        with self.assertRaisesRegex(ValueError, "connected topology"):
            subject.evaluate(SOURCE, geometry_report, geometry_candidate, claim_connected_topology=True)
        with self.assertRaisesRegex(ValueError, "triangle nondegeneracy"):
            subject.evaluate(SOURCE, geometry_report, geometry_candidate, claim_continuous_triangle_nondegeneracy=True)
        with self.assertRaisesRegex(ValueError, "foldover/collision"):
            subject.evaluate(SOURCE, geometry_report, geometry_candidate, claim_continuous_foldover_or_collision_clearance=True)
        with self.assertRaisesRegex(ValueError, "production skinning"):
            subject.evaluate(SOURCE, geometry_report, geometry_candidate, claim_production_skinning=True)
        with self.assertRaisesRegex(ValueError, "Animation"):
            subject.evaluate(SOURCE, geometry_report, geometry_candidate, claim_animation_acceptance=True)
        with self.assertRaisesRegex(ValueError, "Technical Art"):
            subject.evaluate(SOURCE, geometry_report, geometry_candidate, claim_technical_art_acceptance=True)
        with self.assertRaisesRegex(ValueError, "Runtime"):
            subject.evaluate(SOURCE, geometry_report, geometry_candidate, claim_runtime_acceptance=True)

    def test_geometry_must_not_claim_rigging_transfer(self):
        geometry_report, geometry_candidate = synthetic_indexed_donor()
        geometry_report["truth_boundary"]["analytic_rigging_pass_transferred"] = True
        with self.assertRaisesRegex(ValueError, "must not transfer"):
            subject.evaluate(SOURCE, geometry_report, geometry_candidate)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import unittest
from pathlib import Path

from axm_nature_design import rear_tree_geometry_north_low_transition_open_ring as subject

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"


def load_source():
    return json.loads(SOURCE_PATH.read_text(encoding="utf-8"))


class NorthLowTransitionOpenRingGeometryTests(unittest.TestCase):
    def test_exact_owner_transition_open_ring_candidate_passes(self):
        report = subject.evaluate(load_source())
        self.assertEqual(report["result"], subject.RESULT)
        topology = report["candidate_topology"]
        self.assertEqual(topology["vertices"], 17)
        self.assertEqual(topology["triangles"], 24)
        self.assertEqual(topology["edges"], 40)
        self.assertEqual(topology["triangle_components"], 1)
        self.assertEqual(topology["boundary_edges"], 8)
        self.assertEqual(topology["nonmanifold_edges"], 0)
        self.assertEqual(topology["winding_conflicts"], 0)
        self.assertEqual(topology["degenerate_triangles"], 0)
        self.assertEqual(topology["isolated_vertices"], 0)
        self.assertEqual(topology["euler_characteristic"], 1)
        self.assertEqual(topology["boundary_cycles"], 1)
        self.assertEqual(topology["boundary_cycle_lengths"], [8])
        self.assertTrue(all(report["checks"].values()))
        truth = report["truth_boundary"]
        self.assertFalse(truth["trunk_opening_generated_or_proven"])
        self.assertFalse(truth["branch_trunk_bridge_generated_or_proven"])
        self.assertFalse(truth["connected_branch_trunk_topology_proven"])

    def test_owner_transition_matches_exact_metric_length(self):
        report = subject.evaluate(load_source())
        transition = report["owner_transition"]
        self.assertAlmostEqual(
            transition["parameter_u"] * transition["first_segment_length_m"],
            transition["length_along_first_segment_m"],
            places=12,
        )
        self.assertAlmostEqual(transition["transition_radius_m"], 0.0518915887490702, places=15)

    def test_geometry_predecessor_drift_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), requested_geometry_predecessor_head="0" * 40)

    def test_current_rigging_owner_drift_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), requested_rigging_owner_head="0" * 40)

    def test_organic_owner_drift_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), requested_organic_owner_head="0" * 40)

    def test_procedural_owner_drift_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), requested_procedural_owner_head="0" * 40)

    def test_transition_parameter_drift_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), requested_transition_u=subject.TRANSITION_U + 1e-4)

    def test_transition_length_drift_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), requested_transition_length_m=subject.TRANSITION_LENGTH_M + 1e-4)

    def test_trunk_opening_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_trunk_opening_proven=True)

    def test_connected_junction_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_connected_branch_trunk_junction=True)

    def test_source_adoption_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_source_adoption=True)

    def test_rigging_rebind_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_rigging_rebind=True)

    def test_target_host_runtime_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_target_host_or_runtime=True)


if __name__ == "__main__":
    unittest.main()

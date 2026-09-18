import copy
import json
import unittest
from pathlib import Path

from axm_nature_design import rear_tree_geometry_north_low_trunk_bridge_candidate as subject

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "east_rear_tree_neutral_001.json"


def load_source():
    return json.loads(SOURCE.read_text(encoding="utf-8"))


class NorthLowAnalyticTrunkBridgeCandidateTests(unittest.TestCase):
    def test_exact_candidate_is_clean_and_bounded(self):
        report = subject.evaluate(load_source())
        self.assertEqual(report["result"], subject.RESULT)
        self.assertEqual(report["reusable_geometry_rule"], subject.RULE)

        binding = report["organic_exit_frame_binding"]
        self.assertEqual(binding["branch_id"], "north-low")
        self.assertEqual(binding["nearest_trunk_segment"], "mid->upper")
        self.assertAlmostEqual(binding["transition_u"], 0.14801958337760968, places=14)
        self.assertAlmostEqual(binding["exit_branch_radius_m"], 0.0518915887490702, places=14)
        self.assertLessEqual(binding["open_ring_center_residual_m"], subject.TOL)
        self.assertLessEqual(binding["open_ring_radius_residual_m"], subject.TOL)
        self.assertLessEqual(binding["branch_axis_residual"], subject.TOL)
        self.assertLessEqual(binding["neutral_full_radius_support_residual_m"], subject.TOL)

        trunk = report["analytic_trunk_loop"]
        self.assertEqual(trunk["vertices"], 8)
        self.assertGreater(trunk["minimum_segment_t"], 0.0)
        self.assertLess(trunk["maximum_segment_t"], 1.0)
        self.assertLessEqual(trunk["maximum_surface_residual_m"], subject.TOL)
        self.assertGreater(trunk["minimum_bridge_span_m"], 0.015)
        self.assertLess(trunk["maximum_bridge_span_m"], 0.087)
        self.assertFalse(trunk["indexed_trunk_vertices_or_faces_mutated"])
        self.assertTrue(trunk["analytic_envelope_only"])

        bridge = report["bridge_patch_topology"]
        self.assertEqual((bridge["vertices"], bridge["triangles"], bridge["edges"]), (16, 16, 32))
        self.assertEqual(bridge["triangle_components"], 1)
        self.assertEqual(bridge["boundary_edges"], 16)
        self.assertEqual(bridge["boundary_cycles"], 2)
        self.assertEqual(bridge["boundary_cycle_lengths"], [8, 8])
        self.assertEqual(bridge["nonmanifold_edges"], 0)
        self.assertEqual(bridge["winding_conflicts"], 0)
        self.assertEqual(bridge["euler_characteristic"], 0)

        combined = report["combined_candidate_topology"]
        self.assertEqual((combined["vertices"], combined["triangles"], combined["edges"]), (25, 40, 64))
        self.assertEqual(combined["triangle_components"], 1)
        self.assertEqual(combined["boundary_edges"], 8)
        self.assertEqual(combined["boundary_cycles"], 1)
        self.assertEqual(combined["boundary_cycle_lengths"], [8])
        self.assertEqual(combined["nonmanifold_edges"], 0)
        self.assertEqual(combined["winding_conflicts"], 0)
        self.assertEqual(combined["degenerate_triangles"], 0)
        self.assertEqual(combined["isolated_vertices"], 0)
        self.assertEqual(combined["euler_characteristic"], 1)
        self.assertGreater(report["minimum_combined_triangle_area_m2"], 0.00028)

        truth = report["truth_boundary"]
        self.assertTrue(truth["predecessor_branch_open_ring_reused"])
        self.assertTrue(truth["exact_organic_exit_frame_consumed"])
        self.assertTrue(truth["matching_eight_vertex_trunk_surface_loop_constructed"])
        self.assertTrue(truth["one_to_one_annular_bridge_patch_constructed"])
        self.assertFalse(truth["indexed_trunk_mesh_cut_or_mutated"])
        self.assertFalse(truth["connected_branch_trunk_indexed_topology_proven"])
        self.assertFalse(truth["bridge_self_intersection_freedom_proven"])
        self.assertFalse(truth["deformation_or_skinning_proven"])
        self.assertFalse(truth["target_host_or_runtime_proven"])
        self.assertFalse(truth["source_or_default_adopted"])

    def test_build_does_not_mutate_source(self):
        source = load_source()
        before = copy.deepcopy(source)
        subject.build_candidate(source)
        self.assertEqual(source, before)

    def test_owner_and_authority_drifts_fail_closed(self):
        source = load_source()
        failures = [
            {"requested_geometry_predecessor_head": "0" * 40},
            {"requested_organic_exit_frame_owner_head": "0" * 40},
            {"requested_organic_exit_frame_blob": "0" * 40},
            {"requested_rigging_owner_head": "0" * 40},
            {"claim_indexed_trunk_cut_integrated": True},
            {"claim_connected_branch_trunk_junction": True},
            {"claim_source_adoption": True},
            {"claim_rigging_rebind": True},
            {"claim_target_host_or_runtime": True},
        ]
        for kwargs in failures:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    subject.evaluate(source, **kwargs)


if __name__ == "__main__":
    unittest.main()

import json
import unittest
from pathlib import Path

from axm_nature_design import rear_tree_geometry_north_low_indexed_surface_rebind as subject

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "east_rear_tree_neutral_001.json"


def load_source():
    return json.loads(SOURCE.read_text(encoding="utf-8"))


class IndexedSurfaceRebindTests(unittest.TestCase):
    def test_exact_indexed_surface_loop_is_structurally_bound(self):
        report = subject.evaluate(load_source())
        self.assertEqual(report["result"], subject.RESULT)
        binding = report["indexed_surface_binding"]
        self.assertEqual(binding["loop_vertices"], 8)
        self.assertEqual(binding["touched_side_cells"], [0, 1, 2, 9])
        self.assertEqual(binding["parameter_space_self_intersections"], 0)
        self.assertLessEqual(binding["maximum_triangle_plane_residual_m"], 1e-10)
        self.assertGreaterEqual(binding["minimum_barycentric_coordinate"], -1e-10)
        self.assertEqual(len(binding["memberships"]), 8)

    def test_analytic_loop_is_not_silently_treated_as_indexed_surface(self):
        report = subject.evaluate(load_source())
        delta = report["analytic_to_indexed_surface_rebind"]
        self.assertGreater(delta["maximum_surface_delta_m"], 0.004)
        self.assertLess(delta["indexed_surface_minimum_bridge_span_m"], delta["analytic_minimum_bridge_span_m"])
        self.assertGreater(delta["indexed_surface_minimum_bridge_span_m"], 0.010)
        self.assertGreater(delta["minimum_neutral_bridge_triangle_area_m2"], 1e-4)

    def test_bridge_topology_remains_open_at_trunk_side(self):
        report = subject.evaluate(load_source())
        combined = report["combined_candidate_topology"]
        bridge = report["bridge_patch_topology"]
        self.assertEqual((combined["vertices"], combined["triangles"], combined["edges"]), (25, 40, 64))
        self.assertEqual(combined["boundary_cycle_lengths"], [8])
        self.assertEqual((bridge["vertices"], bridge["triangles"], bridge["edges"]), (16, 16, 32))
        self.assertEqual(bridge["boundary_cycle_lengths"], [8, 8])
        self.assertFalse(report["truth_boundary"]["indexed_trunk_cut_integrated"])
        self.assertFalse(report["truth_boundary"]["connected_branch_trunk_indexed_topology_proven"])

    def test_owner_and_claim_drift_fail_closed(self):
        source = load_source()
        controls = [
            {"requested_analytic_geometry_donor_head": "0" * 40},
            {"requested_analytic_geometry_module_blob": "0" * 40},
            {"requested_rigging_owner_head": "0" * 40},
            {"claim_indexed_trunk_cut_integrated": True},
            {"claim_connected_branch_trunk_junction": True},
            {"claim_continuous_deformation_clearance": True},
            {"claim_rigging_transfer": True},
            {"claim_target_host_or_runtime": True},
        ]
        for control in controls:
            with self.subTest(control=control):
                with self.assertRaises(ValueError):
                    subject.evaluate(source, **control)


if __name__ == "__main__":
    unittest.main()

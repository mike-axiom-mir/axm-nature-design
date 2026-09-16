import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axm_nature_design.organic_form import build_mesh, load_source
from axm_nature_design.topology_repair import evaluate, repair_tapered_segment_cap_winding

SOURCES = [
    ROOT / "examples" / "sapling_neutral_001.json",
    ROOT / "examples" / "compact_east_tree_neutral_001.json",
]


class TopologyRepairTests(unittest.TestCase):
    def test_two_real_nature_outputs_reproduce_and_clear_cap_winding_conflicts(self):
        for path in SOURCES:
            with self.subTest(path=path.name):
                report = evaluate(load_source(path))
                self.assertEqual(report["status"], "PASS_TAPERED_CAP_WINDING_REPAIR")
                self.assertEqual(report["before"]["shared_edge_orientation_conflicts"], 260)
                self.assertEqual(report["after"]["shared_edge_orientation_conflicts"], 0)
                self.assertEqual(report["flipped_triangle_count"], 260)
                self.assertEqual(report["before"]["boundary_edges"], 100)
                self.assertEqual(report["after"]["boundary_edges"], 100)
                self.assertEqual(report["before"]["nonmanifold_edges"], 0)
                self.assertEqual(report["after"]["nonmanifold_edges"], 0)
                self.assertEqual(report["before"]["edge_connected_components"], 40)
                self.assertEqual(report["after"]["edge_connected_components"], 40)

    def test_repair_is_reindex_only(self):
        source = load_source(SOURCES[1])
        baseline = build_mesh(source)
        candidate, flipped = repair_tapered_segment_cap_winding(baseline)
        self.assertEqual(candidate["vertices"], baseline["vertices"])
        self.assertEqual(candidate["regions"], baseline["regions"])
        self.assertEqual(len(candidate["triangles"]), len(baseline["triangles"]))
        self.assertTrue(flipped)
        for before, after in zip(baseline["triangles"], candidate["triangles"]):
            self.assertEqual(sorted(before), sorted(after))

    def test_invalid_tapered_layout_fails_closed(self):
        source = load_source(SOURCES[1])
        mesh = build_mesh(source)
        bad = copy.deepcopy(mesh)
        tapered = next(region for region in bad["regions"] if region["kind"] == "tapered-segment")
        tapered["triangle_count"] -= 1
        with self.assertRaises(ValueError):
            repair_tapered_segment_cap_winding(bad)

    def test_truth_boundary_does_not_promote_unproven_claims(self):
        report = evaluate(load_source(SOURCES[1]))
        boundary = report["truth_boundary"]
        self.assertFalse(boundary["production_connected_vegetation_topology_proven"])
        self.assertFalse(boundary["self_intersection_checked"])
        self.assertFalse(boundary["deformation_tested"])
        self.assertFalse(boundary["visual_acceptance_claimed"])
        self.assertFalse(boundary["runtime_or_gameplay_acceptance_claimed"])


if __name__ == "__main__":
    unittest.main()

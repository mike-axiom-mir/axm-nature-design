import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axm_nature_design.leaf_backface_candidate import add_explicit_leaf_backfaces, evaluate
from axm_nature_design.organic_form import build_mesh, load_source

SOURCES = [
    ROOT / "examples" / "sapling_neutral_001.json",
    ROOT / "examples" / "compact_east_tree_neutral_001.json",
    ROOT / "examples" / "east_rear_tree_neutral_001.json",
]


class LeafBackfaceCandidateTests(unittest.TestCase):
    def test_three_real_sources_pass_the_same_bounded_candidate_contract(self):
        for path in SOURCES:
            with self.subTest(path=path.name):
                report = evaluate(load_source(path))
                self.assertEqual(report["status"], "PASS_EXPLICIT_DISJOINT_LEAF_BACKFACE_CANDIDATE")
                self.assertEqual(report["baseline_vertices"], 390)
                self.assertEqual(report["baseline_triangles"], 570)
                self.assertEqual(report["pairs"]["leaf_blades"], 25)
                self.assertEqual(report["candidate_vertices"], 490)
                self.assertEqual(report["candidate_triangles"], 620)
                self.assertEqual(report["pairs"]["exact_position_pairs"], 25)
                self.assertEqual(report["pairs"]["opposite_winding_pairs"], 25)
                self.assertLessEqual(report["pairs"]["minimum_front_back_normal_cosine"], -0.999999999)
                self.assertEqual(report["topology"]["nonmanifold_edges"], 0)
                self.assertEqual(report["topology"]["shared_edge_orientation_conflicts"], 0)

    def test_original_migrated_mesh_remains_an_exact_prefix(self):
        source = load_source(SOURCES[2])
        baseline = build_mesh(source)
        candidate = add_explicit_leaf_backfaces(copy.deepcopy(baseline))
        self.assertEqual(candidate["vertices"][:len(baseline["vertices"])], baseline["vertices"])
        self.assertEqual(candidate["triangles"][:len(baseline["triangles"])], baseline["triangles"])
        self.assertEqual(candidate["regions"][:len(baseline["regions"])], baseline["regions"])

    def test_malformed_leaf_region_fails_closed(self):
        source = load_source(SOURCES[0])
        mesh = build_mesh(source)
        leaf = next(region for region in mesh["regions"] if region["kind"] == "leaf-blade")
        leaf["triangle_count"] = 1
        with self.assertRaises(ValueError):
            add_explicit_leaf_backfaces(mesh)

    def test_unknown_source_fails_closed(self):
        source = load_source(SOURCES[0])
        source["study_id"] = "unknown-source"
        with self.assertRaises(ValueError):
            evaluate(source)

    def test_truth_boundary_keeps_visual_runtime_and_game_acceptance_held(self):
        boundary = evaluate(load_source(SOURCES[2]))["truth_boundary"]
        self.assertTrue(boundary["candidate_is_derived_review_only"])
        self.assertFalse(boundary["renderer_backface_behavior_proven"])
        self.assertFalse(boundary["final_leaf_thickness_or_surface_quality_proven"])
        self.assertFalse(boundary["normals_tangents_uvs_materials_accepted"])
        self.assertFalse(boundary["deformation_or_wind_accepted"])
        self.assertFalse(boundary["runtime_cost_accepted"])
        self.assertFalse(boundary["receiving_scene_visual_acceptance"])
        self.assertFalse(boundary["gameplay_or_production_readiness"])


if __name__ == "__main__":
    unittest.main()

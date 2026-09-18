import copy
import unittest
from pathlib import Path

from axm_nature_design.organic_form import build_mesh, digest, load_source
from axm_nature_design.uc_surface_bridge import adapt_mesh_for_uc

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "sapling_neutral_001.json"


class NatureUCTopologyPreflightTests(unittest.TestCase):
    def test_explicit_source_owned_mesh_identity_survives_bridge(self):
        source = load_source(SOURCE)
        mesh = build_mesh(source)
        source_before = copy.deepcopy(source)
        mesh_before = copy.deepcopy(mesh)

        bridge = adapt_mesh_for_uc(source, mesh, mesh_relation="TEST_EXACT_MESH")

        self.assertEqual(source, source_before)
        self.assertEqual(mesh, mesh_before)
        self.assertEqual(bridge["source_mesh_digest"], digest(mesh))
        self.assertEqual(bridge["mesh_relation"], "TEST_EXACT_MESH")
        self.assertTrue(bridge["source_structural_checks"]["pass"])
        self.assertEqual(bridge["emitted_triangles"], 620)

    def test_reindex_only_candidate_gets_distinct_exact_mesh_digest(self):
        source = load_source(SOURCE)
        baseline = build_mesh(source)
        candidate = copy.deepcopy(baseline)
        a, b, c = candidate["triangles"][2]
        candidate["triangles"][2] = [a, c, b]

        baseline_bridge = adapt_mesh_for_uc(source, baseline, mesh_relation="BASELINE_CONTROL")
        candidate_bridge = adapt_mesh_for_uc(source, candidate, mesh_relation="REINDEX_ONLY_CANDIDATE")

        self.assertNotEqual(baseline_bridge["source_mesh_digest"], candidate_bridge["source_mesh_digest"])
        self.assertEqual(baseline_bridge["source_digest"], candidate_bridge["source_digest"])
        self.assertEqual(baseline_bridge["source_triangles"], candidate_bridge["source_triangles"])
        self.assertEqual(baseline_bridge["emitted_triangles"], candidate_bridge["emitted_triangles"])

    def test_invalid_explicit_mesh_fails_closed(self):
        source = load_source(SOURCE)
        mesh = build_mesh(source)
        mesh["triangles"][0] = [0, 0, 1]
        with self.assertRaisesRegex(ValueError, "structural checks"):
            adapt_mesh_for_uc(source, mesh)


if __name__ == "__main__":
    unittest.main()

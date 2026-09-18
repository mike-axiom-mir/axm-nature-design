import copy
import math
import unittest
from pathlib import Path

from axm_nature_design.organic_form import load_source
from axm_nature_design.uc_surface_bridge import (
    SOURCE_COORDINATES,
    adapt_source_for_uc,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "sapling_neutral_001.json"


def _cross(a, b):
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]


def _sub(a, b):
    return [a[i] - b[i] for i in range(3)]


class NatureUCSurfaceBridgeTests(unittest.TestCase):
    def test_exact_sapling_bridge_is_deterministic_and_source_owned(self):
        source = load_source(SOURCE)
        before = copy.deepcopy(source)
        first = adapt_source_for_uc(source)
        second = adapt_source_for_uc(source)
        self.assertEqual(source, before)
        self.assertEqual(first, second)
        self.assertEqual(first["source_triangles"], 570)
        self.assertEqual(first["source_leaf_triangles"], 50)
        self.assertEqual(first["emitted_triangles"], 620)
        self.assertEqual(first["emitted_vertices"], 1860)
        self.assertEqual(first["leaf_sidedness_strategy"], "EXPLICIT_OPPOSITE_WINDING_BACKFACE_GEOMETRY")

    def test_surface_contract_has_only_two_proof_groups(self):
        bridge = adapt_source_for_uc(load_source(SOURCE))
        surface = bridge["surface"]
        self.assertEqual(surface["schema"], "axm.surface-3d/v0.1")
        self.assertEqual([group["id"] for group in surface["primitives"]], ["woody", "foliage"])
        woody, foliage = surface["primitives"]
        self.assertEqual(len(woody["indices"]) // 3, 520)
        self.assertEqual(len(foliage["indices"]) // 3, 100)
        self.assertNotIn("double_sided", woody["material"])
        self.assertNotIn("double_sided", foliage["material"])
        self.assertEqual(bridge["material_scope"], "PROOF_ONLY_GROUPING_NOT_LOOKDEV")

    def test_emitted_winding_matches_emitted_normals(self):
        bridge = adapt_source_for_uc(load_source(SOURCE))
        for group in bridge["surface"]["primitives"]:
            positions = group["positions"]
            normals = group["normals"]
            for offset in range(0, len(group["indices"]), 3):
                ia, ib, ic = group["indices"][offset:offset + 3]
                a, b, c = positions[ia], positions[ib], positions[ic]
                cross = _cross(_sub(b, a), _sub(c, a))
                self.assertGreater(sum(cross[i] * normals[ia][i] for i in range(3)), 0.0)
                self.assertTrue(all(math.isfinite(value) for value in cross))

    def test_unknown_coordinate_contract_fails_closed(self):
        source = load_source(SOURCE)
        self.assertEqual(source["coordinate_system"], SOURCE_COORDINATES)
        source["coordinate_system"] = "+X right, +Y up, +Z forward; metres"
        with self.assertRaisesRegex(ValueError, "unsupported Nature coordinate system"):
            adapt_source_for_uc(source)


if __name__ == "__main__":
    unittest.main()

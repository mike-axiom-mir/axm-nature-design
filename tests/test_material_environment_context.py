from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

from build_material_environment_context import placement_translation


class MaterialEnvironmentContextTests(unittest.TestCase):
    def test_map_style_placement_preserves_xy_center_and_grounds_min_z(self) -> None:
        vertices = [
            [-1.0, -2.0, 0.25],
            [3.0, 4.0, 5.25],
            [1.0, 0.0, 2.0],
        ]
        target = [10.0, -5.0, 99.0]
        self.assertEqual(placement_translation(vertices, target), [9.0, -6.0, -0.25])

    def test_invalid_target_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            placement_translation([[0.0, 0.0, 0.0]], [1.0, 2.0])

    def test_empty_source_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            placement_translation([], [0.0, 0.0, 0.0])


if __name__ == "__main__":
    unittest.main()

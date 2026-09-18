from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axm_nature_design.materials_lookdev import apply_profile, build_material_evidence, validate_profile
from axm_nature_design.organic_form import load_source
from axm_nature_design.uc_surface_bridge import adapt_source_for_uc

PROFILE = ROOT / "lookdev" / "sapling_material_profile_001.json"
SOURCE = ROOT / "examples" / "sapling_neutral_001.json"


class MaterialsLookdevTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = json.loads(PROFILE.read_text(encoding="utf-8"))
        self.bridge = adapt_source_for_uc(load_source(SOURCE))
        self.surface = self.bridge["surface"]

    def test_profile_is_bounded(self) -> None:
        validate_profile(self.profile)
        self.assertEqual(set(self.profile["materials"]), {"woody", "foliage"})

    def test_apply_profile_changes_only_materials(self) -> None:
        candidate = apply_profile(self.surface, self.profile)
        for before, after in zip(self.surface["primitives"], candidate["primitives"]):
            self.assertEqual(before["id"], after["id"])
            self.assertEqual(before["positions"], after["positions"])
            self.assertEqual(before["normals"], after["normals"])
            self.assertEqual(before["indices"], after["indices"])
            self.assertNotEqual(before["material"], after["material"])

    def test_evidence_requires_increased_surface_separation_without_geometry_drift(self) -> None:
        candidate = apply_profile(self.surface, self.profile)
        evidence = build_material_evidence(self.surface, candidate, self.profile)
        self.assertEqual(evidence["state"], "PASS_BOUNDED_MATERIAL_PROFILE_STRUCTURE")
        self.assertTrue(evidence["checks"]["geometry_unchanged"])
        self.assertTrue(evidence["checks"]["candidate_roughness_separation_increased"])
        self.assertTrue(evidence["checks"]["candidate_luminance_separation_not_reduced"])

    def test_unknown_material_key_fails_closed(self) -> None:
        bad = copy.deepcopy(self.profile)
        bad["materials"]["foliage"]["subsurface"] = 0.5
        with self.assertRaises(ValueError):
            validate_profile(bad)

    def test_metallic_vegetation_profile_fails_closed(self) -> None:
        bad = copy.deepcopy(self.profile)
        bad["materials"]["woody"]["metallic"] = 0.2
        with self.assertRaises(ValueError):
            validate_profile(bad)


if __name__ == "__main__":
    unittest.main()

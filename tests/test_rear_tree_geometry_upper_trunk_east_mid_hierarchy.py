from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from axm_nature_design.rear_tree_geometry_upper_trunk_east_mid_hierarchy import (
    RESULT,
    RIGGING_OWNER_HEAD,
    TOL,
    evaluate,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"


class UpperTrunkEastMidGeometryRebindTests(unittest.TestCase):
    def source(self) -> dict:
        return json.loads(SOURCE_PATH.read_text(encoding="utf-8"))

    def test_exact_hierarchy_rebind_preserves_child_topology_isometry(self):
        source = self.source()
        before = copy.deepcopy(source)
        evidence = evaluate(source)
        self.assertEqual(source, before)
        self.assertEqual(evidence["result"], RESULT)
        self.assertEqual(evidence["lineage"]["rigging_hierarchy_owner_head"], RIGGING_OWNER_HEAD)
        self.assertEqual(evidence["receiver"]["vertices"], 390)
        self.assertEqual(evidence["receiver"]["triangles"], 570)
        self.assertEqual(evidence["receiver"]["selected_vertices"], 52)
        self.assertEqual(evidence["receiver"]["owned_triangles"], 72)
        self.assertEqual(evidence["receiver"]["partial_selected_triangles"], 0)
        self.assertTrue(evidence["receiver"]["triangle_closed_child_partition"])
        self.assertGreater(evidence["receiver"]["minimum_neutral_owned_triangle_area_m2"], TOL)
        self.assertEqual(evidence["representative_recheck"]["witness_count"], 9)
        self.assertLessEqual(evidence["representative_recheck"]["maximum_owned_triangle_area_drift_m2"], TOL)
        self.assertLessEqual(evidence["representative_recheck"]["maximum_selected_pairwise_distance_drift_m"], TOL)
        self.assertTrue(evidence["continuous_structural_certificate"]["continuous_child_topology_isometry"])
        self.assertFalse(evidence["continuous_structural_certificate"]["predecessor_five_child_continuous_clearance_transferred"])

    def test_rigging_owner_drift_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Rigging hierarchy owner head drift"):
            evaluate(self.source(), requested_rigging_owner_head="0" * 40)

    def test_predecessor_clearance_transfer_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "clearance cannot transfer"):
            evaluate(self.source(), claim_predecessor_five_child_clearance_transfer=True)

    def test_parent_mesh_deformation_promotion_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "trunk mesh deformation"):
            evaluate(self.source(), claim_trunk_mesh_deformation=True)

    def test_surface_attachment_promotion_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "surface attachment"):
            evaluate(self.source(), claim_surface_attachment=True)

    def test_collision_gameplay_promotion_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "collision/gameplay"):
            evaluate(self.source(), claim_collision_or_gameplay=True)


if __name__ == "__main__":
    unittest.main()

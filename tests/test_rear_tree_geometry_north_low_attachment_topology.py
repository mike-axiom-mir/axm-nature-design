from __future__ import annotations

import json
import unittest
from pathlib import Path

from axm_nature_design import rear_tree_geometry_north_low_attachment_topology as subject

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"


def load_source():
    return json.loads(SOURCE_PATH.read_text(encoding="utf-8"))


class NorthLowAttachmentTopologyGeometryTests(unittest.TestCase):
    def test_exact_topology_classification_passes(self):
        report = subject.evaluate(load_source())
        self.assertEqual(report["result"], subject.RESULT)
        topology = report["indexed_topology"]
        self.assertEqual(topology["selected_vertices"], 52)
        self.assertEqual(topology["selected_triangles"], 72)
        self.assertEqual(topology["edge_connected_components"], 6)
        self.assertEqual(topology["closed_edge_manifold_components"], 2)
        self.assertEqual(topology["open_components"], 4)
        self.assertEqual(topology["shared_indexed_vertices_with_trunk"], [])
        self.assertFalse(topology["indexed_branch_trunk_attachment_proven"])
        self.assertTrue(topology["root_branch_segment"]["closed_edge_manifold"])
        self.assertEqual(topology["root_branch_segment"]["boundary_edges"], 0)
        self.assertEqual(topology["root_branch_segment"]["euler_characteristic"], 2)
        self.assertTrue(all(report["checks"].values()))
        self.assertFalse(report["interpretation"]["current_child_is_one_connected_manifold"])
        self.assertFalse(report["interpretation"]["production_welded_branch_trunk_junction_proven"])

    def test_rigging_owner_drift_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), requested_rigging_owner_head="0" * 40)

    def test_geometry_predecessor_drift_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), requested_geometry_predecessor_head="0" * 40)

    def test_connected_attachment_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_connected_branch_trunk_attachment=True)

    def test_production_topology_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_production_topology=True)

    def test_skinning_acceptance_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_skinning_acceptance=True)

    def test_runtime_acceptance_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), claim_runtime_acceptance=True)


if __name__ == "__main__":
    unittest.main()

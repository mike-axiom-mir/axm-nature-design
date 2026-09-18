from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from axm_nature_design import rear_tree_rigging_north_low_attachment_representation_gate as subject

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"


def load_source():
    return json.loads(SOURCE_PATH.read_text(encoding="utf-8"))


def geometry_contract():
    return subject.expected_geometry_contract()


class NorthLowAttachmentRepresentationGateTests(unittest.TestCase):
    def test_exact_detached_attachment_gate_passes(self):
        report = subject.evaluate(load_source(), geometry_contract())
        self.assertEqual(report["result"], subject.RESULT)
        constraint = report["attachment_representation_constraint"]
        self.assertEqual(constraint["mode"], "DETACHED_DIAGNOSTIC_CHILD_SOCKET_ONLY")
        self.assertFalse(constraint["indexed_branch_trunk_connection_proven"])
        self.assertFalse(constraint["production_connected_skinning_allowed"])
        self.assertEqual(constraint["diagnostic_parent_weight"], 0.0)

        geometry = report["geometry_attachment_class"]
        self.assertEqual(geometry["selected_vertices"], 52)
        self.assertEqual(geometry["selected_triangles"], 72)
        self.assertEqual(geometry["edge_connected_components"], 6)
        self.assertEqual(geometry["closed_edge_manifold_components"], 2)
        self.assertEqual(geometry["open_components"], 4)
        self.assertEqual(geometry["shared_indexed_vertices_with_trunk"], 0)

        motion = report["preserved_rigging_motion_evidence"]
        self.assertEqual(motion["representative_parent_child_pose_count"], 9)
        self.assertLessEqual(motion["maximum_gated_parent_command_leak_m"], 1e-9)
        self.assertTrue(motion["continuous_transform_domain_preserved"])
        self.assertFalse(motion["connected_surface_continuity_proven"])

    def test_exact_rigging_predecessor_is_required(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), geometry_contract(), requested_rigging_predecessor_head="0" * 40)

    def test_exact_geometry_donor_is_required(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), geometry_contract(), requested_geometry_donor_head="0" * 40)

    def test_geometry_contract_drift_is_rejected(self):
        mutated = copy.deepcopy(geometry_contract())
        mutated["expected"]["shared_indexed_vertices_with_trunk"] = 1
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), mutated)

    def test_component_class_drift_is_rejected(self):
        mutated = copy.deepcopy(geometry_contract())
        mutated["expected"]["edge_connected_components"] = 1
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), mutated)

    def test_connected_attachment_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), geometry_contract(), claim_connected_branch_trunk_attachment=True)

    def test_production_skinning_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), geometry_contract(), claim_production_skinning=True)

    def test_production_parent_weight_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), geometry_contract(), claim_production_parent_weight=True)

    def test_animation_acceptance_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), geometry_contract(), claim_animation_acceptance=True)

    def test_technical_art_acceptance_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), geometry_contract(), claim_technical_art_acceptance=True)

    def test_runtime_acceptance_promotion_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.evaluate(load_source(), geometry_contract(), claim_runtime_acceptance=True)


if __name__ == "__main__":
    unittest.main()

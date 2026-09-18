from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from axm_nature_design.rear_tree_geometry_simultaneous_socket_audit import (
    RIGGING_PARENT_HEAD,
    TOL,
    evaluate,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"


class SimultaneousSocketGeometryAuditTests(unittest.TestCase):
    def source(self) -> dict:
        return json.loads(SOURCE_PATH.read_text(encoding="utf-8"))

    def test_exact_five_child_corner_family_preserves_composition_structure(self):
        source = self.source()
        before = copy.deepcopy(source)
        evidence = evaluate(source)
        self.assertEqual(source, before)
        self.assertIn(
            evidence["result"],
            {
                "PASS_SIMULTANEOUS_FIVE_CHILD_COMPOSITION_STRUCTURE_32_EXTREME_CORNERS",
                "HOLD_SIMULTANEOUS_FIVE_CHILD_COMPOSITION_PARTITION_STRUCTURE",
            },
        )
        self.assertEqual(evidence["lineage"]["rigging_parent_head"], RIGGING_PARENT_HEAD)
        self.assertEqual(evidence["receiver"]["vertices"], 390)
        self.assertEqual(evidence["receiver"]["triangles"], 570)
        self.assertEqual(evidence["receiver"]["selected_vertex_union"], 260)
        self.assertEqual(evidence["receiver"]["globally_fixed_vertices"], 130)
        self.assertTrue(evidence["receiver"]["pairwise_child_vertex_disjoint"])
        self.assertEqual(evidence["witness_family"]["extreme_corner_state_count"], 32)
        self.assertEqual(evidence["witness_family"]["total_state_count"], 33)
        self.assertLessEqual(
            evidence["witness_family"]["maximum_composition_order_vertex_delta_m"], TOL
        )
        self.assertLessEqual(
            evidence["witness_family"]["maximum_globally_fixed_vertex_drift_m"], TOL
        )
        self.assertLessEqual(
            evidence["witness_family"]["maximum_pivot_vertex_drift_m"], TOL
        )
        self.assertFalse(
            evidence["truth_boundary"]["self_intersection_freedom_claimed_by_this_module"]
        )

    def test_positions_are_optional_evidence_not_default_payload(self):
        evidence = evaluate(self.source())
        self.assertTrue(all("positions" not in state for state in evidence["witness_family"]["states"]))
        detailed = evaluate(self.source(), include_positions=True)
        self.assertTrue(all(len(state["positions"]) == 390 for state in detailed["witness_family"]["states"]))

    def test_rigging_parent_drift_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Rigging parent head drift"):
            evaluate(self.source(), requested_rigging_parent_head="0" * 40)

    def test_continuous_clearance_promotion_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "continuous clearance"):
            evaluate(self.source(), claim_continuous_deformation_clearance=True)

    def test_collision_gameplay_promotion_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "collision/gameplay"):
            evaluate(self.source(), claim_collision_or_gameplay=True)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from axm_nature_design.rear_tree_rigging import (
    BRANCH_ID,
    EXPECTED_MESH_DIGEST,
    EXPECTED_SOURCE_DIGEST,
    RESULT,
    evaluate,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"


class RearTreeRootSocketRiggingTests(unittest.TestCase):
    def load_source(self):
        return json.loads(SOURCE_PATH.read_text(encoding="utf-8"))

    def test_exact_source_passes_bounded_socket_probe(self):
        source = self.load_source()
        before = copy.deepcopy(source)
        evidence = evaluate(source)
        self.assertEqual(source, before)
        self.assertEqual(evidence["result"], RESULT)
        self.assertEqual(evidence["source_owner"]["source_digest"], EXPECTED_SOURCE_DIGEST)
        self.assertEqual(evidence["source_owner"]["generated_mesh_digest"], EXPECTED_MESH_DIGEST)
        probe = evidence["rigging_probe"]
        self.assertEqual(probe["branch_id"], BRANCH_ID)
        self.assertEqual(probe["joint_pivot_m"], [0.01, 0.0, 3.16])
        self.assertEqual(probe["source_flex_radius_m"], 0.12)
        self.assertEqual(probe["source_flex_status"], "DECLARED_NOT_DEFORMATION_TESTED")
        self.assertEqual(probe["local_trunk_segment"], "crown->tip")
        self.assertEqual(probe["selected_vertices"], 52)
        self.assertEqual(probe["selected_triangles"], 72)
        self.assertEqual(probe["fixed_vertices"], 338)
        self.assertEqual(probe["diagnostic_interval_deg"], [-5.0, 5.0])
        self.assertEqual(len(evidence["poses"]), 5)
        self.assertTrue(all(evidence["checks"].values()))
        self.assertLessEqual(evidence["measurements"]["maximum_fixed_vertex_drift_m"], 1e-12)
        self.assertLessEqual(evidence["measurements"]["maximum_pivot_vertex_drift_m"], 1e-12)
        self.assertLessEqual(evidence["measurements"]["maximum_selected_pairwise_distance_drift_m"], 1e-12)
        self.assertLessEqual(evidence["measurements"]["maximum_selected_axis_projection_drift_m"], 1e-12)
        self.assertGreater(evidence["measurements"]["maximum_selected_vertex_displacement_m"], 0.08)
        self.assertLess(evidence["measurements"]["maximum_selected_vertex_displacement_m"], 0.083)
        self.assertFalse(evidence["continuous_invariant"]["collision_or_clearance_proven"])
        self.assertFalse(evidence["truth_boundary"]["production_skin_weights_tested"])
        self.assertFalse(evidence["truth_boundary"]["animation_timing_or_playback_claimed"])
        self.assertFalse(evidence["truth_boundary"]["runtime_controller_or_device_claimed"])

    def test_pivot_drift_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "pivot"):
            evaluate(self.load_source(), joint_pivot_override=[0.011, 0.0, 3.16])

    def test_other_branch_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "north-top"):
            evaluate(self.load_source(), requested_branch_id="west-high")

    def test_flex_radius_drift_fails_closed(self):
        source = self.load_source()
        for zone in source["flex_zones"]:
            if zone["id"] == "north-top-branch-flex":
                zone["radius"] = 0.14
        with self.assertRaisesRegex(ValueError, "source identity drift"):
            evaluate(source)

    def test_probe_cannot_be_promoted_to_source_rom(self):
        with self.assertRaisesRegex(ValueError, "ROM"):
            evaluate(self.load_source(), claim_source_rom=True)

    def test_animation_acceptance_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Animation"):
            evaluate(self.load_source(), claim_animation_acceptance=True)

    def test_runtime_acceptance_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Runtime"):
            evaluate(self.load_source(), claim_runtime_acceptance=True)

    def test_probe_interval_cannot_silently_widen(self):
        with self.assertRaisesRegex(ValueError, "interval"):
            evaluate(self.load_source(), diagnostic_min_deg=-10.0, diagnostic_max_deg=10.0)


if __name__ == "__main__":
    unittest.main()

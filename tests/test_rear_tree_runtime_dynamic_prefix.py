from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from axm_nature_design.rear_tree_runtime_dynamic_prefix import (
    BRANCH_IDS,
    EXPECTED_DYNAMIC_WINDOW,
    RESULT,
    build_layout,
    evaluate,
    verify_layout,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"


class RuntimeDynamicWindowTests(unittest.TestCase):
    def setUp(self):
        self.source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))

    def test_exact_existing_window_proof_passes_without_mutating_source(self):
        before = copy.deepcopy(self.source)
        evidence = evaluate(self.source)
        self.assertEqual(self.source, before)
        self.assertEqual(evidence["result"], RESULT)
        self.assertTrue(all(evidence["checks"].values()))
        self.assertFalse(any(evidence["truth_boundary"].values()))

    def test_exact_window_and_packet_budget(self):
        evidence = evaluate(self.source)
        measured = evidence["measurements"]
        self.assertEqual(
            [measured["dynamic_window_start_vertex"], measured["dynamic_window_end_vertex_exclusive"]],
            list(EXPECTED_DYNAMIC_WINDOW),
        )
        self.assertEqual(measured["dynamic_vertices"], 260)
        self.assertEqual(measured["fixed_vertices"], 130)
        self.assertEqual(measured["control_full_position_packet_bytes"], 4680)
        self.assertEqual(measured["candidate_dynamic_window_position_packet_bytes"], 3120)
        self.assertEqual(measured["position_packet_bytes_saved"], 1560)
        self.assertAlmostEqual(measured["position_packet_reduction_percent"], 33.33333333333333)
        self.assertEqual(measured["dynamic_window_regions"], 1)
        self.assertFalse(measured["geometry_reindexed"])
        self.assertFalse(measured["index_buffer_changed"])

    def test_all_five_static_witnesses_reconstruct_control_exactly(self):
        rows = evaluate(self.source)["measurements"]["pose_rows"]
        self.assertEqual([row["shared_driver_deg"] for row in rows], [-5.0, -2.5, 0.0, 2.5, 5.0])
        self.assertTrue(all(row["control_candidate_max_vertex_component_delta_m"] == 0.0 for row in rows))
        self.assertTrue(all(row["candidate_dynamic_position_count"] == 260 for row in rows))

    def test_layout_fails_closed_on_window_drift(self):
        layout = build_layout(self.source)
        layout["dynamic_window_original_indices"] = [109, 370]
        with self.assertRaises(ValueError):
            verify_layout(self.source, layout)

    def test_layout_fails_closed_on_reindex_promotion(self):
        layout = build_layout(self.source)
        layout["geometry_reindexed"] = True
        with self.assertRaises(ValueError):
            verify_layout(self.source, layout)

    def test_rejects_branch_family_reduction(self):
        with self.assertRaises(ValueError):
            evaluate(self.source, requested_branch_ids=BRANCH_IDS[:-1])

    def test_rejects_authority_promotion(self):
        for kwargs in (
            {"claim_generic_vegetation_policy": True},
            {"claim_target_host_upload": True},
            {"claim_target_device_performance": True},
            {"claim_art_or_qa_acceptance": True},
            {"claim_animation_or_wind_semantics": True},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    evaluate(self.source, **kwargs)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from axm_nature_design.rear_tree_rigging_primary_branch_family import (
    BRANCH_IDS,
    EXPECTED_MIGRATED_MESH_DIGEST,
    EXPECTED_SOURCE_DIGEST,
    GEOMETRY_RECEIVER_HEAD,
    PROCEDURAL_DONOR_HEAD,
    PROCEDURAL_REBIND_CONTRACT_BLOB,
    RESULT,
    RIGGING_PREDECESSOR_HEAD,
    evaluate,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"
CONTRACT_PATH = ROOT / "contracts" / "east-rear-primary-branch-root-socket-rigging-family-003.json"


class RearTreePrimaryBranchRiggingFamilyTests(unittest.TestCase):
    def load_source(self):
        return json.loads(SOURCE_PATH.read_text(encoding="utf-8"))

    def load_contract(self):
        return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_exact_five_root_family_passes_on_geometry_receiver(self):
        source = self.load_source()
        before = copy.deepcopy(source)
        evidence = evaluate(source)
        self.assertEqual(source, before)
        self.assertEqual(evidence["result"], RESULT)
        self.assertEqual(evidence["lineage"]["source_digest"], EXPECTED_SOURCE_DIGEST)
        self.assertEqual(evidence["lineage"]["geometry_receiver_head"], GEOMETRY_RECEIVER_HEAD)
        self.assertEqual(evidence["lineage"]["geometry_migrated_mesh_digest"], EXPECTED_MIGRATED_MESH_DIGEST)
        self.assertEqual(evidence["lineage"]["rigging_predecessor_head"], RIGGING_PREDECESSOR_HEAD)
        self.assertEqual(evidence["lineage"]["procedural_donor_head"], PROCEDURAL_DONOR_HEAD)
        self.assertEqual(evidence["lineage"]["procedural_rebind_contract_blob"], PROCEDURAL_REBIND_CONTRACT_BLOB)
        family = evidence["rigging_family"]
        self.assertEqual(family["branch_ids"], list(BRANCH_IDS))
        self.assertEqual(family["branch_count"], 5)
        self.assertEqual(family["total_representative_pose_evaluations"], 25)
        self.assertEqual(family["diagnostic_interval_deg"], [-5.0, 5.0])
        self.assertTrue(family["pairwise_child_vertex_disjoint"])
        self.assertEqual(len(family["probes"]), 5)
        self.assertTrue(all(row["selected_vertices"] == 52 for row in family["probes"]))
        self.assertTrue(all(row["selected_triangles"] == 72 for row in family["probes"]))
        self.assertTrue(all(row["fixed_vertices"] == 338 for row in family["probes"]))
        self.assertTrue(all(row["source_flex_status"] == "DECLARED_NOT_DEFORMATION_TESTED" for row in family["probes"]))
        self.assertTrue(all(len(row["poses"]) == 5 for row in family["probes"]))
        self.assertTrue(all(all(row["checks"].values()) for row in family["probes"]))
        self.assertTrue(all(evidence["checks"].values()))
        self.assertLessEqual(evidence["measurements"]["maximum_fixed_vertex_drift_m"], 1e-12)
        self.assertLessEqual(evidence["measurements"]["maximum_pivot_vertex_drift_m"], 1e-12)
        self.assertLessEqual(evidence["measurements"]["maximum_selected_pairwise_distance_drift_m"], 1e-12)
        self.assertLessEqual(evidence["measurements"]["maximum_selected_axis_projection_drift_m"], 1e-12)
        self.assertGreater(evidence["measurements"]["maximum_selected_vertex_displacement_m"], 0.0)
        self.assertFalse(evidence["continuous_invariant"]["simultaneous_multi_branch_motion_proven"])
        self.assertFalse(evidence["continuous_invariant"]["collision_or_self_intersection_proven"])
        self.assertFalse(evidence["truth_boundary"]["animation_timing_interpolation_or_playback_claimed"])
        self.assertFalse(evidence["truth_boundary"]["runtime_controller_or_device_claimed"])

    def test_contract_pins_exact_handoffs_and_boundaries(self):
        contract = self.load_contract()
        self.assertEqual(contract["organic_source_owner"]["head"], "fdc9d2b6ee729728551e22fd3eafa23ad60b6c7a")
        self.assertEqual(contract["geometry_receiver"]["head"], GEOMETRY_RECEIVER_HEAD)
        self.assertEqual(contract["rigging_predecessor"]["head"], RIGGING_PREDECESSOR_HEAD)
        self.assertEqual(contract["procedural_selection_handoff"]["head"], PROCEDURAL_DONOR_HEAD)
        self.assertEqual(contract["procedural_selection_handoff"]["contract_blob"], PROCEDURAL_REBIND_CONTRACT_BLOB)
        self.assertEqual(contract["branch_ids"], list(BRANCH_IDS))
        self.assertFalse(contract["procedural_selection_handoff"]["automatic_rigging_adoption"])
        self.assertFalse(contract["procedural_authority_transferred"])
        self.assertFalse(contract["animation_acceptance_authorized"])
        self.assertFalse(contract["runtime_acceptance_authorized"])

    def test_procedural_donor_head_drift_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Procedural donor head"):
            evaluate(self.load_source(), requested_procedural_donor_head="deadbeef")

    def test_geometry_receiver_head_drift_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Geometry receiver head"):
            evaluate(self.load_source(), requested_geometry_receiver_head="deadbeef")

    def test_branch_family_cannot_be_reduced_reordered_or_widened(self):
        with self.assertRaisesRegex(ValueError, "exact five"):
            evaluate(self.load_source(), requested_branch_ids=BRANCH_IDS[:-1])
        with self.assertRaisesRegex(ValueError, "exact five"):
            evaluate(self.load_source(), requested_branch_ids=tuple(reversed(BRANCH_IDS)))
        with self.assertRaisesRegex(ValueError, "interval"):
            evaluate(self.load_source(), diagnostic_min_deg=-6.0, diagnostic_max_deg=6.0)

    def test_pivot_drift_fails_closed_per_branch(self):
        with self.assertRaisesRegex(ValueError, "pivot drift: south-low"):
            evaluate(self.load_source(), joint_pivot_overrides={"south-low": [0.011, -0.01, 1.82]})

    def test_source_identity_drift_fails_closed(self):
        source = self.load_source()
        for zone in source["flex_zones"]:
            if zone["id"] == "west-high-branch-flex":
                zone["radius"] = 0.14
        with self.assertRaisesRegex(ValueError, "source identity drift"):
            evaluate(source)

    def test_diagnostic_family_cannot_claim_other_authorities(self):
        with self.assertRaisesRegex(ValueError, "ROM"):
            evaluate(self.load_source(), claim_source_rom=True)
        with self.assertRaisesRegex(ValueError, "Procedural authority"):
            evaluate(self.load_source(), claim_procedural_authority_transfer=True)
        with self.assertRaisesRegex(ValueError, "Geometry acceptance"):
            evaluate(self.load_source(), claim_geometry_acceptance_transfer=True)
        with self.assertRaisesRegex(ValueError, "Animation"):
            evaluate(self.load_source(), claim_animation_acceptance=True)
        with self.assertRaisesRegex(ValueError, "Runtime"):
            evaluate(self.load_source(), claim_runtime_acceptance=True)


if __name__ == "__main__":
    unittest.main()

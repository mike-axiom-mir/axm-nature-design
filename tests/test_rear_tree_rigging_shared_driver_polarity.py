from __future__ import annotations

import json
import unittest
from pathlib import Path

from axm_nature_design.rear_tree_rigging_shared_driver_polarity import (
    BRANCH_IDS,
    COMMAND_SIGN_MULTIPLIER,
    REPRESENTATIVE_SHARED_DRIVER_DEG,
    RESULT,
    VFX_DONOR_HEAD,
    VFX_REVIEW_ONLY_PREFERRED_LOCAL_ANGLE_DEG,
    evaluate,
    local_angle_for_shared_driver,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"
CONTRACT_PATH = ROOT / "contracts" / "east-rear-primary-branch-shared-driver-polarity-rigging-004.json"


class RearTreeRiggingSharedDriverPolarityTests(unittest.TestCase):
    def load_source(self):
        return json.loads(SOURCE_PATH.read_text(encoding="utf-8"))

    def load_contract(self):
        return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_exact_mixed_sign_binding_passes_without_changing_socket_identity(self):
        evidence = evaluate(self.load_source())
        self.assertEqual(evidence["result"], RESULT)
        self.assertEqual(evidence["binding"]["branch_ids"], list(BRANCH_IDS))
        self.assertEqual(
            tuple(evidence["binding"]["command_sign_multiplier_by_branch"][b] for b in BRANCH_IDS),
            (1.0, -1.0, 1.0, -1.0, 1.0),
        )
        self.assertEqual(
            evidence["binding"]["representative_shared_driver_deg"],
            list(REPRESENTATIVE_SHARED_DRIVER_DEG),
        )
        self.assertEqual(evidence["lineage"]["vfx_donor_head"], VFX_DONOR_HEAD)
        self.assertTrue(all(evidence["checks"].values()))
        self.assertTrue(evidence["continuous_mapping"]["absolute_angle_isometry"])
        self.assertTrue(evidence["continuous_mapping"]["bijective_per_socket_on_closed_interval"])
        self.assertFalse(evidence["continuous_mapping"]["rigging_axis_or_pivot_changed"])
        self.assertFalse(evidence["continuous_mapping"]["rigging_child_partition_changed"])
        self.assertFalse(evidence["truth_boundary"]["animation_timing_interpolation_or_playback_claimed"])
        self.assertFalse(evidence["truth_boundary"]["runtime_controller_or_device_claimed"])

        for row in evidence["binding"]["sockets"]:
            self.assertEqual(row["selected_vertices"], 52)
            self.assertEqual(row["selected_triangles"], 72)
            self.assertEqual(row["fixed_vertices"], 338)
            self.assertEqual(len(row["representative_driver_mapping"]), 5)
            self.assertTrue(all(x["predecessor_pose_reused"] for x in row["representative_driver_mapping"]))

    def test_positive_shared_boundary_selects_exact_vfx_preferred_local_sign(self):
        for branch_id in BRANCH_IDS:
            preferred = VFX_REVIEW_ONLY_PREFERRED_LOCAL_ANGLE_DEG[branch_id]
            self.assertEqual(local_angle_for_shared_driver(branch_id, 5.0), preferred)
            self.assertEqual(local_angle_for_shared_driver(branch_id, -5.0), -preferred)
            self.assertEqual(local_angle_for_shared_driver(branch_id, 0.0), 0.0)
            self.assertEqual(abs(local_angle_for_shared_driver(branch_id, 2.5)), 2.5)

    def test_contract_pins_exact_vfx_handoff_and_authority_boundaries(self):
        contract = self.load_contract()
        self.assertEqual(contract["rigging_predecessor"]["head"], "898529f602893c8f6be179bd3e9b6821fc099904")
        self.assertEqual(contract["vfx_sign_map_handoff"]["head"], VFX_DONOR_HEAD)
        self.assertEqual(contract["branch_ids"], list(BRANCH_IDS))
        self.assertEqual(contract["command_sign_multiplier_by_branch"], COMMAND_SIGN_MULTIPLIER)
        self.assertFalse(contract["axis_direction_rewritten"])
        self.assertFalse(contract["automatic_animation_adoption"])
        self.assertFalse(contract["automatic_runtime_adoption"])
        self.assertFalse(contract["simultaneous_multi_branch_motion_claimed"])

    def test_uniform_global_sign_is_rejected(self):
        wrong = {branch_id: 5.0 for branch_id in BRANCH_IDS}
        with self.assertRaisesRegex(ValueError, "preferred local-angle map drift"):
            evaluate(self.load_source(), requested_preferred_local_angles=wrong)

    def test_vfx_donor_head_drift_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "VFX sign-map donor head drift"):
            evaluate(self.load_source(), requested_vfx_donor_head="deadbeef")

    def test_shared_driver_domain_cannot_be_widened_or_reshaped(self):
        with self.assertRaisesRegex(ValueError, "diagnostic interval"):
            local_angle_for_shared_driver("south-low", 5.01)
        with self.assertRaisesRegex(ValueError, "representative field"):
            evaluate(self.load_source(), representative_shared_driver_deg=(-6.0, 0.0, 6.0))
        with self.assertRaisesRegex(ValueError, "unknown Rigging socket"):
            local_angle_for_shared_driver("not-a-socket", 1.0)

    def test_binding_cannot_claim_vfx_animation_runtime_or_simultaneous_motion(self):
        source = self.load_source()
        with self.assertRaisesRegex(ValueError, "does not adopt VFX"):
            evaluate(source, claim_wind_motion=True)
        with self.assertRaisesRegex(ValueError, "not physical wind"):
            evaluate(source, claim_physical_wind=True)
        with self.assertRaisesRegex(ValueError, "Animation"):
            evaluate(source, claim_animation_acceptance=True)
        with self.assertRaisesRegex(ValueError, "Runtime"):
            evaluate(source, claim_runtime_acceptance=True)
        with self.assertRaisesRegex(ValueError, "simultaneous"):
            evaluate(source, claim_simultaneous_motion=True)


if __name__ == "__main__":
    unittest.main()

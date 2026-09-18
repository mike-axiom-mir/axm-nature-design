from __future__ import annotations

import json
import unittest
from pathlib import Path

from axm_nature_design.rear_tree_rigging_shared_driver_composition import (
    BRANCH_IDS,
    GEOMETRY_DONOR_HEAD,
    REPRESENTATIVE_SHARED_DRIVER_DEG,
    RESULT,
    VFX_STATIC_RESPONSE_HEAD,
    evaluate,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "examples" / "east_rear_tree_neutral_001.json"
CONTRACT_PATH = ROOT / "contracts" / "east-rear-primary-branch-shared-driver-rigging-composition-005.json"


class RearTreeRiggingSharedDriverCompositionTests(unittest.TestCase):
    def load_source(self):
        return json.loads(SOURCE_PATH.read_text(encoding="utf-8"))

    def load_contract(self):
        return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_exact_five_socket_shared_parameter_composes_with_rigid_invariants(self):
        evidence = evaluate(self.load_source())
        self.assertEqual(evidence["result"], RESULT)
        self.assertEqual(evidence["composition"]["branch_ids"], list(BRANCH_IDS))
        self.assertEqual(
            evidence["composition"]["representative_shared_driver_deg"],
            list(REPRESENTATIVE_SHARED_DRIVER_DEG),
        )
        self.assertEqual(evidence["composition"]["selected_vertex_union"], 260)
        self.assertEqual(evidence["composition"]["globally_fixed_vertices"], 130)
        self.assertEqual(
            evidence["composition"]["command_sign_multiplier_by_branch"],
            {
                "south-low": 1.0,
                "north-low": -1.0,
                "east-mid": 1.0,
                "west-high": -1.0,
                "north-top": 1.0,
            },
        )
        self.assertTrue(all(evidence["checks"].values()))
        self.assertLessEqual(evidence["measurements"]["maximum_composition_order_vertex_delta_m"], 1e-9)
        self.assertLessEqual(evidence["measurements"]["maximum_globally_fixed_vertex_drift_m"], 1e-9)
        self.assertLessEqual(evidence["measurements"]["maximum_pivot_vertex_drift_m"], 1e-9)
        self.assertLessEqual(evidence["measurements"]["maximum_rigid_child_pairwise_distance_drift_m"], 1e-9)
        self.assertLessEqual(evidence["measurements"]["maximum_child_axis_projection_drift_m"], 1e-9)

    def test_continuous_certificate_is_kinematic_not_animation_or_collision(self):
        evidence = evaluate(self.load_source())
        certificate = evidence["continuous_parameter_certificate"]
        self.assertTrue(certificate["continuous_for_every_real_parameter_in_closed_interval"])
        self.assertTrue(certificate["pairwise_disjoint_transform_support"])
        self.assertTrue(certificate["composition_order_independent_for_every_real_parameter"])
        self.assertTrue(certificate["fixed_receiver_identity_for_every_real_parameter"])
        self.assertTrue(certificate["pivot_invariant_for_every_real_parameter"])
        self.assertTrue(certificate["rigid_child_pairwise_distances_invariant_for_every_real_parameter"])
        self.assertTrue(certificate["child_axis_projection_invariant_for_every_real_parameter"])
        self.assertFalse(certificate["timing_or_playback_defined"])
        self.assertFalse(certificate["continuous_collision_clearance_proven"])
        self.assertFalse(evidence["truth_boundary"]["animation_timing_interpolation_or_playback_claimed"])
        self.assertFalse(evidence["truth_boundary"]["runtime_controller_or_device_claimed"])

    def test_contract_pins_exact_geometry_and_vfx_receivers(self):
        contract = self.load_contract()
        self.assertEqual(contract["rigging_predecessor"]["head"], "754797a815266a643c6b08f1606eb76ba95dd8c6")
        self.assertEqual(contract["geometry_static_receiver_donor"]["head"], GEOMETRY_DONOR_HEAD)
        self.assertEqual(contract["vfx_static_response_donor"]["head"], VFX_STATIC_RESPONSE_HEAD)
        self.assertEqual(contract["representative_shared_driver_deg"], list(REPRESENTATIVE_SHARED_DRIVER_DEG))
        self.assertFalse(contract["animation_acceptance_claimed"])
        self.assertFalse(contract["runtime_acceptance_claimed"])
        self.assertFalse(contract["continuous_collision_clearance_claimed"])

    def test_donor_identity_drift_is_rejected(self):
        source = self.load_source()
        with self.assertRaisesRegex(ValueError, "Geometry shared-driver donor head drift"):
            evaluate(source, requested_geometry_donor_head="deadbeef")
        with self.assertRaisesRegex(ValueError, "VFX static-response donor head drift"):
            evaluate(source, requested_vfx_static_response_head="deadbeef")

    def test_witness_field_cannot_be_silently_changed(self):
        with self.assertRaisesRegex(ValueError, "witness field drift"):
            evaluate(self.load_source(), representative_shared_driver_deg=(-5.0, 0.0, 5.0))

    def test_authority_promotions_fail_closed(self):
        source = self.load_source()
        with self.assertRaisesRegex(ValueError, "Animation"):
            evaluate(source, claim_animation_acceptance=True)
        with self.assertRaisesRegex(ValueError, "Runtime"):
            evaluate(source, claim_runtime_acceptance=True)
        with self.assertRaisesRegex(ValueError, "not physical wind"):
            evaluate(source, claim_physical_wind=True)
        with self.assertRaisesRegex(ValueError, "continuous collision"):
            evaluate(source, claim_continuous_collision_clearance=True)
        with self.assertRaisesRegex(ValueError, "biological ROM"):
            evaluate(source, claim_source_or_biological_rom=True)


if __name__ == "__main__":
    unittest.main()

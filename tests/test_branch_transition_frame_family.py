from __future__ import annotations

import copy
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from axm_nature_design.branch_transition_frame_family import (
    FRAME_CONVENTION,
    OWNER_PASS_STATE,
    OWNER_REPORT_SCHEMA,
    PREDECESSOR_PARAMETER_SCHEMA,
    RELATION,
    SCHEMA,
    assemble_transition_frame_family,
    validate_contract,
)


class BranchTransitionFrameFamilyTests(unittest.TestCase):
    def setUp(self):
        self.branch_ids = ["south-low", "north-low", "east-mid", "west-high", "north-top"]
        self.expected = {
            branch_id: {
                "transition_u": 0.05 + index * 0.02,
                "transition_length_m": 0.02 + index * 0.01,
            }
            for index, branch_id in enumerate(self.branch_ids)
        }
        self.contract = {
            "schema": SCHEMA,
            "family_id": "transition-frame-fixture",
            "owner_report_schema": OWNER_REPORT_SCHEMA,
            "predecessor_transition_family_schema": PREDECESSOR_PARAMETER_SCHEMA,
            "predecessor_transition_family_digest": "1" * 64,
            "authorized_branch_ids": list(self.branch_ids),
            "expected_transitions": copy.deepcopy(self.expected),
            "relation": RELATION,
            "frame_convention": FRAME_CONVENTION,
            "source_mutation_authorized": False,
            "junction_strategy_authorized": False,
            "connected_topology_claim_authorized": False,
            "weld_ring_authorized": False,
            "surface_normal_authorized": False,
            "automatic_geometry_adoption": False,
            "automatic_rigging_adoption": False,
            "automatic_animation_adoption": False,
            "automatic_vfx_adoption": False,
            "automatic_technical_art_adoption": False,
            "automatic_runtime_adoption": False,
            "production_weight_authorized": False,
        }

        frames = []
        for index, branch_id in enumerate(self.branch_ids):
            angle = 0.25 * index
            x_radial = [math.cos(angle), math.sin(angle), 0.0]
            y_azimuth = [-math.sin(angle), math.cos(angle), 0.0]
            z_trunk = [0.0, 0.0, 1.0]
            departure = math.radians(42.0 + index * 2.0)
            radial_component = math.sin(departure)
            azimuth_component = 0.0
            axial_component = math.cos(departure)
            branch_tangent = [
                radial_component * x_radial[0],
                radial_component * x_radial[1],
                axial_component,
            ]
            expected = self.expected[branch_id]
            frames.append({
                "branch_id": branch_id,
                "exact_root_flex_zone_id": f"{branch_id}-branch-flex",
                "exact_root_flex_zone_status": "DECLARED_NOT_DEFORMATION_TESTED",
                "transition_u": expected["transition_u"],
                "transition_length_along_first_segment_m": expected["transition_length_m"],
                "exit_center_m": [1.0 + index, -0.5 * index, 2.0 + 0.1 * index],
                "exit_branch_radius_m": 0.05 - 0.002 * index,
                "nearest_trunk_segment": "mid->upper",
                "nearest_trunk_segment_t": 0.3 + 0.05 * index,
                "nearest_trunk_centerline_point_m": [0.9 + index, -0.5 * index, 2.0 + 0.1 * index],
                "exit_centerline_distance_m": 0.1,
                "exit_local_trunk_radius_m": 0.12,
                "boundary_residual_m": 0.0,
                "branch_first_segment_tangent_unit": branch_tangent,
                "local_trunk_tangent_unit": z_trunk,
                "trunk_centerline_to_exit_radial_unit": x_radial,
                "exit_azimuth_unit": y_azimuth,
                "branch_tangent_components_in_exit_frame": {
                    "axial_along_trunk": axial_component,
                    "radial_away_from_trunk_centerline": radial_component,
                    "azimuthal_around_trunk": azimuth_component,
                },
                "branch_vs_local_trunk_departure_angle_deg": math.degrees(departure),
                "frame_orthogonality_max_abs_dot": 0.0,
                "frame_unit_length_max_error": 0.0,
                "branch_tangent_reconstruction_error": 0.0,
            })

        self.owner_report = {
            "schema": OWNER_REPORT_SCHEMA,
            "state": OWNER_PASS_STATE,
            "transition_owner_schema": "axm.nature-neutral-branch-transition-envelope/v0.1",
            "branch_count": 5,
            "frames": frames,
            "checks": {
                "all_five_primary_branch_exit_frames_measured": True,
                "all_frames_use_exact_transition_owner_boundaries": True,
                "all_exit_frames_orthonormal_within_tolerance": True,
                "all_branch_tangent_decompositions_close": True,
                "all_root_flex_declarations_remain_unproven": True,
            },
            "handoff": {
                "organic_claim": "AUTHORED_NEUTRAL_TRANSITION_EXIT_FRAME_ONLY",
                "connected_topology_state": "HELD_FOR_GEOMETRY",
                "frame_is_weld_ring": False,
                "frame_is_skinning_or_joint_frame": False,
                "source_compensation_authorized": False,
            },
            "truth_boundary": {
                "authored_centerlines_and_radii_measured": True,
                "existing_transition_owner_reused": True,
                "source_geometry_changed": False,
                "generated_mesh_connectivity_inspected": False,
                "connected_branch_trunk_topology_proven": False,
                "junction_strategy_selected": False,
                "deformation_simulated": False,
                "rigging_hierarchy_or_weights_inferred": False,
                "biological_attachment_or_rom_claimed": False,
                "runtime_readiness_claimed": False,
            },
        }

    def test_five_materially_different_frame_outputs(self):
        family = assemble_transition_frame_family(self.owner_report, self.contract)
        self.assertEqual(5, family["output_count"])
        self.assertEqual(5, len({row["parameter_digest"] for row in family["outputs"]}))
        self.assertEqual(5, len({row["origin_digest"] for row in family["outputs"]}))
        self.assertEqual(5, len({row["basis_digest"] for row in family["outputs"]}))
        self.assertFalse(family["geometry_junction_authority"])
        self.assertFalse(family["weld_ring_authority"])
        self.assertFalse(family["surface_normal_authority"])
        self.assertFalse(family["rigging_authority"])

    def test_matrix_uses_documented_right_handed_column_basis(self):
        family = assemble_transition_frame_family(self.owner_report, self.contract)
        row = {item["branch_id"]: item for item in family["outputs"]}["south-low"]
        self.assertEqual(FRAME_CONVENTION, row["frame_convention"])
        self.assertEqual(
            [
                [1.0, 0.0, 0.0, 1.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 2.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            row["local_to_source_matrix_4x4_column_basis"],
        )

    def test_owner_and_declaration_order_do_not_change_family(self):
        forward = assemble_transition_frame_family(self.owner_report, self.contract)
        reverse_report = copy.deepcopy(self.owner_report)
        reverse_report["frames"] = list(reversed(reverse_report["frames"]))
        reverse_contract = copy.deepcopy(self.contract)
        reverse_contract["authorized_branch_ids"] = list(reversed(reverse_contract["authorized_branch_ids"]))
        reverse = assemble_transition_frame_family(reverse_report, reverse_contract)
        self.assertEqual(forward["family_digest"], reverse["family_digest"])

    def test_transition_scalar_drift_from_predecessor_fails_closed(self):
        report = copy.deepcopy(self.owner_report)
        report["frames"][0]["transition_u"] += 0.001
        with self.assertRaises(ValueError):
            assemble_transition_frame_family(report, self.contract)

    def test_left_handed_owner_basis_fails_closed(self):
        report = copy.deepcopy(self.owner_report)
        report["frames"][0]["exit_azimuth_unit"] = [0.0, -1.0, 0.0]
        with self.assertRaises(ValueError):
            assemble_transition_frame_family(report, self.contract)

    def test_nonunit_owner_basis_fails_closed(self):
        report = copy.deepcopy(self.owner_report)
        report["frames"][1]["trunk_centerline_to_exit_radial_unit"] = [2.0, 0.0, 0.0]
        with self.assertRaises(ValueError):
            assemble_transition_frame_family(report, self.contract)

    def test_missing_owner_frame_fails_closed(self):
        report = copy.deepcopy(self.owner_report)
        report["frames"].pop()
        report["branch_count"] = 4
        with self.assertRaises(ValueError):
            assemble_transition_frame_family(report, self.contract)

    def test_owner_state_drift_fails_closed(self):
        report = copy.deepcopy(self.owner_report)
        report["state"] = "HOLD_FRAME_REVIEW"
        with self.assertRaises(ValueError):
            assemble_transition_frame_family(report, self.contract)

    def test_connected_topology_promotion_fails_closed(self):
        report = copy.deepcopy(self.owner_report)
        report["truth_boundary"]["connected_branch_trunk_topology_proven"] = True
        with self.assertRaises(ValueError):
            assemble_transition_frame_family(report, self.contract)

    def test_flex_status_promotion_fails_closed(self):
        report = copy.deepcopy(self.owner_report)
        report["frames"][0]["exact_root_flex_zone_status"] = "DEFORMATION_PROVEN"
        with self.assertRaises(ValueError):
            assemble_transition_frame_family(report, self.contract)

    def test_weld_and_rigging_authority_expansion_fails_closed(self):
        contract = copy.deepcopy(self.contract)
        contract["weld_ring_authorized"] = True
        with self.assertRaises(ValueError):
            validate_contract(contract)
        contract = copy.deepcopy(self.contract)
        contract["automatic_rigging_adoption"] = True
        with self.assertRaises(ValueError):
            validate_contract(contract)


if __name__ == "__main__":
    unittest.main()

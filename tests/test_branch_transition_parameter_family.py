from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from axm_nature_design.branch_transition_parameter_family import (
    OWNER_PASS_STATE,
    OWNER_REPORT_SCHEMA,
    RELATION,
    SCHEMA,
    assemble_transition_parameter_family,
    validate_contract,
)


class BranchTransitionParameterFamilyTests(unittest.TestCase):
    def setUp(self):
        self.branch_ids = ["south", "north", "east", "west", "top"]
        self.expected = {
            "south": {"embedded_fraction_of_first_segment": 0.14, "embedded_length_along_first_segment_m": 0.06},
            "north": {"embedded_fraction_of_first_segment": 0.15, "embedded_length_along_first_segment_m": 0.065},
            "east": {"embedded_fraction_of_first_segment": 0.05, "embedded_length_along_first_segment_m": 0.022},
            "west": {"embedded_fraction_of_first_segment": 0.085, "embedded_length_along_first_segment_m": 0.036},
            "top": {"embedded_fraction_of_first_segment": 0.052, "embedded_length_along_first_segment_m": 0.021},
        }
        self.contract = {
            "schema": SCHEMA,
            "family_id": "transition-fixture",
            "owner_report_schema": OWNER_REPORT_SCHEMA,
            "authorized_branch_ids": list(self.branch_ids),
            "expected_transitions": copy.deepcopy(self.expected),
            "relation": RELATION,
            "source_mutation_authorized": False,
            "junction_strategy_authorized": False,
            "connected_topology_claim_authorized": False,
            "automatic_geometry_adoption": False,
            "automatic_rigging_adoption": False,
            "automatic_animation_adoption": False,
            "automatic_vfx_adoption": False,
            "automatic_runtime_adoption": False,
            "production_weight_authorized": False,
        }
        rows = []
        for index, branch_id in enumerate(self.branch_ids):
            expected = self.expected[branch_id]
            length = expected["embedded_length_along_first_segment_m"]
            fraction = expected["embedded_fraction_of_first_segment"]
            first_length = length / fraction
            rows.append({
                "branch_id": branch_id,
                "root_radius_m": 0.05 - index * 0.002,
                "first_segment_end_radius_m": 0.03 - index * 0.001,
                "first_segment_length_m": first_length,
                "exact_root_flex_zone_id": f"{branch_id}-flex",
                "exact_root_flex_zone_status": "DECLARED_NOT_DEFORMATION_TESTED",
                "transition_state": "FULL_BRANCH_RADIUS_EXITS_TRUNK_RADIAL_ENVELOPE_WITHIN_FIRST_SEGMENT",
                "embedded_fraction_of_first_segment": fraction,
                "embedded_length_along_first_segment_m": length,
                "first_full_radius_exit_boundary": {"u": fraction},
            })
        self.owner_report = {
            "schema": OWNER_REPORT_SCHEMA,
            "state": OWNER_PASS_STATE,
            "branch_count": 5,
            "branches": rows,
            "checks": {
                "all_branch_roots_have_full_radius_neutral_support": True,
                "all_primary_branches_have_exact_unproven_root_flex_declaration": True,
                "all_primary_branches_have_measured_first_segment_transition": True,
            },
            "handoff": {
                "organic_claim": "AUTHORED_NEUTRAL_RADIAL_TRANSITION_GEOMETRY_ONLY",
                "connected_topology_state": "HELD_FOR_GEOMETRY",
                "junction_strategy_selected": False,
                "source_compensation_authorized": False,
            },
            "truth_boundary": {
                "source_geometry_changed": False,
                "flex_zone_metadata_changed": False,
                "generated_mesh_connectivity_inspected": False,
                "connected_branch_trunk_topology_proven": False,
                "weld_boolean_or_remesh_strategy_selected": False,
                "deformation_simulated": False,
                "rigging_hierarchy_or_weights_inferred": False,
                "biological_attachment_claimed": False,
                "runtime_readiness_claimed": False,
            },
        }

    def test_five_materially_different_parameter_windows(self):
        family = assemble_transition_parameter_family(self.owner_report, self.contract)
        self.assertEqual(5, family["output_count"])
        self.assertEqual(5, len({row["parameter_digest"] for row in family["outputs"]}))
        self.assertEqual(5, len({row["transition_length_m"] for row in family["outputs"]}))
        self.assertEqual(5, len({row["transition_u_max"] for row in family["outputs"]}))
        self.assertTrue(all(row["sample_u"][0] == 0.0 for row in family["outputs"]))
        self.assertTrue(all(row["sample_u"][-1] == row["transition_u_max"] for row in family["outputs"]))
        self.assertFalse(family["geometry_junction_authority"])
        self.assertFalse(family["rigging_authority"])

    def test_owner_row_order_does_not_change_family(self):
        forward = assemble_transition_parameter_family(self.owner_report, self.contract)
        reverse_report = copy.deepcopy(self.owner_report)
        reverse_report["branches"] = list(reversed(reverse_report["branches"]))
        reverse_contract = copy.deepcopy(self.contract)
        reverse_contract["authorized_branch_ids"] = list(reversed(reverse_contract["authorized_branch_ids"]))
        reverse = assemble_transition_parameter_family(reverse_report, reverse_contract)
        self.assertEqual(forward["family_digest"], reverse["family_digest"])

    def test_owner_transition_length_drift_fails_closed(self):
        report = copy.deepcopy(self.owner_report)
        report["branches"][0]["embedded_length_along_first_segment_m"] += 0.001
        with self.assertRaises(ValueError):
            assemble_transition_parameter_family(report, self.contract)

    def test_owner_transition_fraction_drift_fails_closed(self):
        report = copy.deepcopy(self.owner_report)
        report["branches"][1]["embedded_fraction_of_first_segment"] += 0.01
        with self.assertRaises(ValueError):
            assemble_transition_parameter_family(report, self.contract)

    def test_missing_branch_fails_closed(self):
        report = copy.deepcopy(self.owner_report)
        report["branches"].pop()
        report["branch_count"] = 4
        with self.assertRaises(ValueError):
            assemble_transition_parameter_family(report, self.contract)

    def test_owner_state_drift_fails_closed(self):
        report = copy.deepcopy(self.owner_report)
        report["state"] = "FAIL_NEUTRAL_BRANCH_ROOT_SUPPORT"
        with self.assertRaises(ValueError):
            assemble_transition_parameter_family(report, self.contract)

    def test_truth_boundary_widening_fails_closed(self):
        report = copy.deepcopy(self.owner_report)
        report["truth_boundary"]["connected_branch_trunk_topology_proven"] = True
        with self.assertRaises(ValueError):
            assemble_transition_parameter_family(report, self.contract)

    def test_junction_strategy_selection_fails_closed(self):
        report = copy.deepcopy(self.owner_report)
        report["handoff"]["junction_strategy_selected"] = True
        with self.assertRaises(ValueError):
            assemble_transition_parameter_family(report, self.contract)

    def test_authority_expansion_fails_closed(self):
        contract = copy.deepcopy(self.contract)
        contract["automatic_rigging_adoption"] = True
        with self.assertRaises(ValueError):
            validate_contract(contract)


if __name__ == "__main__":
    unittest.main()

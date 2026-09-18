from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from axm_nature_design.branch_partition_rigging_composition_rebind import (
    assemble_rigging_composition_rebind,
    validate_contract,
)


class BranchPartitionRiggingCompositionRebindTests(unittest.TestCase):
    def setUp(self):
        self.branches = ["alpha", "beta"]
        self.family = {
            "schema": "axm.nature-branch-child-partition-family/v0.1",
            "family_digest": "f" * 64,
            "pairwise_vertex_disjoint": True,
            "partitions": [
                {
                    "branch_id": "alpha",
                    "region_ids": ["branch:alpha:0", "leaf:alpha-leaves:0"],
                    "vertex_indices": [0, 1, 2],
                    "vertex_count": 3,
                    "triangle_count": 2,
                    "fixed_vertex_count": 3,
                    "partition_digest": "1" * 64,
                    "vertex_index_digest": "2" * 64,
                },
                {
                    "branch_id": "beta",
                    "region_ids": ["branch:beta:0", "leaf:beta-leaves:0"],
                    "vertex_indices": [3, 4, 5],
                    "vertex_count": 3,
                    "triangle_count": 2,
                    "fixed_vertex_count": 3,
                    "partition_digest": "3" * 64,
                    "vertex_index_digest": "4" * 64,
                },
            ],
        }
        self.rigging = {
            "result": "PASS_RIGGING",
            "lineage": {"procedural_rebind_contract_blob": "a" * 40},
            "rigging_family": {
                "branch_ids": self.branches,
                "probes": [
                    {
                        "branch_id": "alpha",
                        "selected_regions": ["branch:alpha:0", "leaf:alpha-leaves:0"],
                        "selected_vertex_indices": [0, 1, 2],
                        "selected_vertices": 3,
                        "selected_triangles": 2,
                        "fixed_vertices": 3,
                    },
                    {
                        "branch_id": "beta",
                        "selected_regions": ["branch:beta:0", "leaf:beta-leaves:0"],
                        "selected_vertex_indices": [3, 4, 5],
                        "selected_vertices": 3,
                        "selected_triangles": 2,
                        "fixed_vertices": 3,
                    },
                ],
            },
        }
        self.polarity = {
            "result": "PASS_POLARITY",
            "binding": {
                "branch_ids": self.branches,
                "sockets": [
                    {
                        "branch_id": "alpha",
                        "selected_vertices": 3,
                        "selected_triangles": 2,
                        "fixed_vertices": 3,
                        "command_sign_multiplier": 1.0,
                    },
                    {
                        "branch_id": "beta",
                        "selected_vertices": 3,
                        "selected_triangles": 2,
                        "fixed_vertices": 3,
                        "command_sign_multiplier": -1.0,
                    },
                ],
            },
        }
        self.composition = {
            "result": "PASS_COMPOSITION",
            "composition": {
                "branch_ids": self.branches,
                "selected_vertex_union": 6,
                "globally_fixed_vertices": 0,
                "per_branch_selected_vertices": {"alpha": 3, "beta": 3},
            },
            "continuous_parameter_certificate": {
                "timing_or_playback_defined": False,
                "continuous_collision_clearance_proven": False,
            },
        }
        self.contract = {
            "schema": "axm.nature-branch-child-partition-rigging-composition-rebind/v0.1",
            "family_id": "test-family-composition-rebind",
            "relation": "EXACT_CURRENT_RIGGING_COMPOSITION_REBIND_SELECTION_IDENTITY_ONLY",
            "branch_ids": self.branches,
            "procedural_provider": {
                "family_digest": "f" * 64,
                "predecessor_consumer_rebind_head": "9" * 40,
                "predecessor_consumer_rebind_digest": "8" * 64,
                "geometry_rebind_contract_blob": "a" * 40,
            },
            "rigging_consumer": {
                "repository": "owner/repo",
                "pr": 14,
                "ref": "b" * 40,
                "family_result": "PASS_RIGGING",
                "family_module_path": "family.py",
                "family_module_blob": "c" * 40,
                "polarity_result": "PASS_POLARITY",
                "polarity_module_path": "polarity.py",
                "polarity_module_blob": "d" * 40,
                "composition_result": "PASS_COMPOSITION",
                "composition_module_path": "composition.py",
                "composition_module_blob": "e" * 40,
                "composition_contract_path": "composition.json",
                "composition_contract_blob": "6" * 40,
                "expected_selected_vertex_union": 6,
                "expected_globally_fixed_vertices": 0,
                "expected_per_branch_selected_vertices": {"alpha": 3, "beta": 3},
            },
            "automatic_rigging_adoption": False,
            "rigging_authority_transferred": False,
            "deformation_semantics_authorized": False,
            "shared_driver_semantics_adopted": False,
            "animation_or_vfx_motion_adopted": False,
            "continuous_collision_claimed": False,
            "automatic_downstream_adoption": False,
        }

    def assemble(self, family=None, rigging=None, polarity=None, composition=None, contract=None):
        return assemble_rigging_composition_rebind(
            self.family if family is None else family,
            self.rigging if rigging is None else rigging,
            self.polarity if polarity is None else polarity,
            self.composition if composition is None else composition,
            self.contract if contract is None else contract,
            observed_rigging_head="b" * 40,
            observed_family_module_blob="c" * 40,
            observed_polarity_module_blob="d" * 40,
            observed_composition_module_blob="e" * 40,
            observed_composition_contract_blob="6" * 40,
        )

    def test_multiple_distinct_partitions_match_composition_consumer(self):
        result = self.assemble()
        self.assertEqual(2, result["branch_count"])
        self.assertTrue(result["all_exact_selection_identities_match"])
        self.assertEqual(2, len({row["partition_digest"] for row in result["comparisons"]}))
        self.assertTrue(result["rigging_composition_observed_not_adopted"])

    def test_procedural_partition_list_order_is_non_semantic(self):
        family = copy.deepcopy(self.family)
        family["partitions"] = list(reversed(family["partitions"]))
        result = self.assemble(family=family)
        self.assertEqual(self.branches, [row["branch_id"] for row in result["comparisons"]])
        self.assertTrue(result["all_exact_selection_identities_match"])

    def test_vertex_selection_drift_fails_closed(self):
        rigging = copy.deepcopy(self.rigging)
        rigging["rigging_family"]["probes"][1]["selected_vertex_indices"] = [0, 4, 5]
        with self.assertRaises(ValueError):
            self.assemble(rigging=rigging)

    def test_composition_branch_identity_drift_fails_closed(self):
        composition = copy.deepcopy(self.composition)
        composition["composition"]["branch_ids"] = ["beta", "alpha"]
        with self.assertRaises(ValueError):
            self.assemble(composition=composition)

    def test_composition_union_drift_fails_closed(self):
        composition = copy.deepcopy(self.composition)
        composition["composition"]["selected_vertex_union"] = 5
        with self.assertRaises(ValueError):
            self.assemble(composition=composition)

    def test_composition_may_not_claim_timing(self):
        composition = copy.deepcopy(self.composition)
        composition["continuous_parameter_certificate"]["timing_or_playback_defined"] = True
        with self.assertRaises(ValueError):
            self.assemble(composition=composition)

    def test_authority_expansion_fails_closed(self):
        for field in (
            "rigging_authority_transferred",
            "shared_driver_semantics_adopted",
            "animation_or_vfx_motion_adopted",
            "continuous_collision_claimed",
            "automatic_downstream_adoption",
        ):
            with self.subTest(field=field):
                contract = copy.deepcopy(self.contract)
                contract[field] = True
                with self.assertRaises(ValueError):
                    validate_contract(contract)


if __name__ == "__main__":
    unittest.main()

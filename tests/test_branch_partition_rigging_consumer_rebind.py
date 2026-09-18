from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from axm_nature_design.branch_partition_rigging_consumer_rebind import (
    assemble_rigging_consumer_rebind,
    validate_contract,
)


class BranchPartitionRiggingConsumerRebindTests(unittest.TestCase):
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
                ]
            },
        }
        self.shared = {
            "result": "PASS_SHARED",
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
            "continuous_mapping": {
                "rigging_child_partition_changed": False,
                "source_or_geometry_changed": False,
            },
        }
        self.contract = {
            "schema": "axm.nature-branch-child-partition-rigging-consumer-rebind/v0.1",
            "family_id": "test-family-rebind",
            "relation": "EXACT_RIGGING_CONSUMER_REBIND_SELECTION_IDENTITY_ONLY",
            "branch_ids": self.branches,
            "procedural_provider": {
                "family_digest": "f" * 64,
                "geometry_rebind_contract_path": "examples/rebind.json",
                "geometry_rebind_contract_blob": "a" * 40,
            },
            "rigging_consumer": {
                "repository": "owner/repo",
                "pr": 14,
                "ref": "b" * 40,
                "family_result": "PASS_RIGGING",
                "family_module_path": "family.py",
                "family_module_blob": "c" * 40,
                "shared_driver_result": "PASS_SHARED",
                "shared_driver_module_path": "shared.py",
                "shared_driver_module_blob": "d" * 40,
            },
            "automatic_rigging_adoption": False,
            "rigging_authority_transferred": False,
            "deformation_semantics_authorized": False,
            "animation_or_vfx_motion_adopted": False,
            "automatic_downstream_adoption": False,
        }

    def assemble(self, family=None, rigging=None, shared=None, contract=None):
        return assemble_rigging_consumer_rebind(
            self.family if family is None else family,
            self.rigging if rigging is None else rigging,
            self.shared if shared is None else shared,
            self.contract if contract is None else contract,
            observed_rigging_head="b" * 40,
            observed_family_module_blob="c" * 40,
            observed_shared_driver_module_blob="d" * 40,
        )

    def test_multiple_distinct_partitions_match_current_consumer(self):
        result = self.assemble()
        self.assertEqual(2, result["branch_count"])
        self.assertTrue(result["all_exact_selection_identities_match"])
        self.assertEqual(2, len({row["partition_digest"] for row in result["comparisons"]}))
        self.assertEqual([1.0, -1.0], [row["command_sign_multiplier"] for row in result["comparisons"]])

    def test_vertex_selection_drift_fails_closed(self):
        rigging = copy.deepcopy(self.rigging)
        rigging["rigging_family"]["probes"][1]["selected_vertex_indices"] = [0, 4, 5]
        with self.assertRaises(ValueError):
            self.assemble(rigging=rigging)

    def test_region_selection_drift_fails_closed(self):
        rigging = copy.deepcopy(self.rigging)
        rigging["rigging_family"]["probes"][0]["selected_regions"][0] = "branch:wrong:0"
        with self.assertRaises(ValueError):
            self.assemble(rigging=rigging)

    def test_shared_driver_partition_change_fails_closed(self):
        shared = copy.deepcopy(self.shared)
        shared["continuous_mapping"]["rigging_child_partition_changed"] = True
        with self.assertRaises(ValueError):
            self.assemble(shared=shared)

    def test_authority_expansion_fails_closed(self):
        contract = copy.deepcopy(self.contract)
        contract["rigging_authority_transferred"] = True
        with self.assertRaises(ValueError):
            validate_contract(contract)

    def test_automatic_downstream_adoption_fails_closed(self):
        contract = copy.deepcopy(self.contract)
        contract["automatic_downstream_adoption"] = True
        with self.assertRaises(ValueError):
            validate_contract(contract)


if __name__ == "__main__":
    unittest.main()

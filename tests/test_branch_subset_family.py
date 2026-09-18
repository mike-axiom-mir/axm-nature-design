from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from axm_nature_design.branch_subset_family import (
    PARTITION_SCHEMA,
    RELATION,
    SCHEMA,
    assemble_subset_family,
    compose_subset,
    digest,
    validate_contract,
)


class BranchChildSubsetFamilyTests(unittest.TestCase):
    def setUp(self):
        rows = []
        for index, branch_id in enumerate(("alpha", "beta", "gamma")):
            start_v = index * 6
            start_t = index * 2
            row = {
                "branch_id": branch_id,
                "region_ids": [f"branch:{branch_id}:0", f"leaf:{branch_id}-leaves:0"],
                "vertex_indices": list(range(start_v, start_v + 6)),
                "triangle_indices": list(range(start_t, start_t + 2)),
                "vertex_count": 6,
                "triangle_count": 2,
            }
            rows.append(row)
        family_core = {
            "schema": PARTITION_SCHEMA,
            "family_id": "partition-fixture",
            "relation": "DERIVED_REGION_PARTITION_REVIEW_ONLY_NOT_RIGGING_AUTHORITY",
            "branch_count": 3,
            "partitions": rows,
            "pairwise_vertex_disjoint": True,
        }
        self.partition_family = {**family_core, "family_digest": digest(family_core)}
        self.contract = {
            "schema": SCHEMA,
            "family_id": "subset-fixture",
            "partition_family_schema": PARTITION_SCHEMA,
            "expected_partition_family_digest": self.partition_family["family_digest"],
            "authorized_branch_ids": ["alpha", "beta", "gamma"],
            "total_vertices": 24,
            "subset_specs": [
                {"subset_id": "one", "branch_ids": ["alpha"]},
                {"subset_id": "two", "branch_ids": ["alpha", "beta"]},
                {"subset_id": "three", "branch_ids": ["alpha", "beta", "gamma"]},
            ],
            "relation": RELATION,
            "source_mutation_authorized": False,
            "automatic_rigging_adoption": False,
            "automatic_animation_adoption": False,
            "automatic_vfx_adoption": False,
            "automatic_runtime_adoption": False,
        }

    def test_materially_different_subset_outputs_are_deterministic(self):
        family = assemble_subset_family(self.partition_family, self.contract)
        reversed_specs = [copy.deepcopy(spec) for spec in reversed(self.contract["subset_specs"])]
        for spec in reversed_specs:
            spec["branch_ids"] = list(reversed(spec["branch_ids"]))
        reverse = assemble_subset_family(self.partition_family, self.contract, reversed_specs)
        self.assertEqual(family["family_digest"], reverse["family_digest"])
        self.assertEqual(3, family["output_count"])
        self.assertEqual([6, 12, 18], sorted(row["vertex_count"] for row in family["outputs"]))
        self.assertEqual([2, 4, 6], sorted(row["triangle_count"] for row in family["outputs"]))
        self.assertEqual(3, len({row["selection_digest"] for row in family["outputs"]}))
        self.assertEqual(3, len({row["vertex_index_digest"] for row in family["outputs"]}))

    def test_single_subset_keeps_authority_false(self):
        row = compose_subset(self.partition_family, self.contract, {"subset_id": "one", "branch_ids": ["alpha"]})
        self.assertEqual(["alpha"], row["branch_ids"])
        self.assertEqual(6, row["vertex_count"])
        self.assertEqual(18, row["fixed_vertex_count"])
        self.assertFalse(row["source_authorized"])
        self.assertFalse(row["rigging_authorized"])
        self.assertFalse(row["animation_authorized"])
        self.assertFalse(row["vfx_authorized"])
        self.assertFalse(row["runtime_authorized"])

    def test_duplicate_selection_under_different_id_fails_closed(self):
        contract = copy.deepcopy(self.contract)
        contract["subset_specs"][2]["branch_ids"] = ["beta", "alpha"]
        with self.assertRaises(ValueError):
            validate_contract(contract)

    def test_unknown_branch_fails_closed(self):
        contract = copy.deepcopy(self.contract)
        contract["subset_specs"][0]["branch_ids"] = ["delta"]
        with self.assertRaises(ValueError):
            validate_contract(contract)

    def test_duplicate_branch_in_subset_fails_closed(self):
        contract = copy.deepcopy(self.contract)
        contract["subset_specs"][0]["branch_ids"] = ["alpha", "alpha"]
        with self.assertRaises(ValueError):
            validate_contract(contract)

    def test_partition_digest_drift_fails_closed(self):
        family = copy.deepcopy(self.partition_family)
        family["family_digest"] = "0" * 64
        with self.assertRaises(ValueError):
            compose_subset(family, self.contract, self.contract["subset_specs"][0])

    def test_partition_overlap_fails_closed(self):
        family = copy.deepcopy(self.partition_family)
        family["partitions"][1]["vertex_indices"][0] = family["partitions"][0]["vertex_indices"][0]
        with self.assertRaises(ValueError):
            compose_subset(family, self.contract, self.contract["subset_specs"][1])

    def test_runtime_authority_expansion_fails_closed(self):
        contract = copy.deepcopy(self.contract)
        contract["automatic_runtime_adoption"] = True
        with self.assertRaises(ValueError):
            validate_contract(contract)


if __name__ == "__main__":
    unittest.main()

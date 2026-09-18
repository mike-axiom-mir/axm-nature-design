from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from axm_nature_design.branch_relation_subset_family import (
    MODE_ATTACHMENT_DISJOINT,
    MODE_ATTACHMENT_INTERSECTING,
    MODE_DECLARED_OVERLAP_ATTACHMENT_DISJOINT,
    OWNER_PASS_STATE,
    OWNER_REPORT_SCHEMA,
    RELATION,
    SCHEMA,
    assemble_relation_family,
    derive_branch_ids,
    validate_contract,
)
from axm_nature_design.branch_subset_family import PARTITION_SCHEMA, digest


class BranchOwnerRelationSubsetFamilyTests(unittest.TestCase):
    def setUp(self):
        branch_ids = ["south", "north", "east", "west", "top"]
        rows = []
        for index, branch_id in enumerate(branch_ids):
            start_v = index * 6
            start_t = index * 2
            rows.append(
                {
                    "branch_id": branch_id,
                    "region_ids": [f"branch:{branch_id}:0", f"leaf:{branch_id}:0"],
                    "vertex_indices": list(range(start_v, start_v + 6)),
                    "triangle_indices": list(range(start_t, start_t + 2)),
                    "vertex_count": 6,
                    "triangle_count": 2,
                }
            )
        core = {
            "schema": PARTITION_SCHEMA,
            "family_id": "partition-fixture",
            "relation": "DERIVED_REGION_PARTITION_REVIEW_ONLY_NOT_RIGGING_AUTHORITY",
            "branch_count": 5,
            "partitions": rows,
            "pairwise_vertex_disjoint": True,
        }
        self.partition_family = {**core, "family_digest": digest(core)}
        self.contract = {
            "schema": SCHEMA,
            "family_id": "relation-fixture",
            "partition_family_schema": PARTITION_SCHEMA,
            "owner_report_schema": OWNER_REPORT_SCHEMA,
            "expected_partition_family_digest": self.partition_family["family_digest"],
            "authorized_branch_ids": branch_ids,
            "total_vertices": 36,
            "expected_owner_pair_count": 10,
            "expected_pairs_per_branch": 2,
            "output_specs": [
                {
                    "output_id": "intersecting",
                    "mode": MODE_ATTACHMENT_INTERSECTING,
                    "expected_branch_ids": ["east"],
                },
                {
                    "output_id": "overlap-disjoint",
                    "mode": MODE_DECLARED_OVERLAP_ATTACHMENT_DISJOINT,
                    "expected_branch_ids": ["north"],
                },
                {
                    "output_id": "disjoint",
                    "mode": MODE_ATTACHMENT_DISJOINT,
                    "expected_branch_ids": ["south", "north", "west", "top"],
                },
            ],
            "relation": RELATION,
            "source_mutation_authorized": False,
            "automatic_rigging_adoption": False,
            "automatic_animation_adoption": False,
            "automatic_vfx_adoption": False,
            "automatic_runtime_adoption": False,
            "production_weight_authorized": False,
        }
        pairs = []
        for branch_id in branch_ids:
            for trunk_id in ("lower", "upper"):
                pairs.append(
                    {
                        "trunk_flex_zone_id": trunk_id,
                        "branch_id": branch_id,
                        "interaction_class": (
                            "FLEX_ENVELOPE_OVERLAP_ONLY"
                            if branch_id == "north" and trunk_id == "upper"
                            else "DISJOINT"
                        ),
                        "trunk_flex_intersects_neutral_attachment_cross_section": (
                            branch_id == "east" and trunk_id == "upper"
                        ),
                    }
                )
        self.owner_report = {
            "schema": OWNER_REPORT_SCHEMA,
            "state": OWNER_PASS_STATE,
            "pair_count": 10,
            "pairs": pairs,
            "truth_boundary": {
                "interaction_class_assigns_rig_policy": False,
                "attachment_cross_section_intersection_assigns_rig_policy": False,
                "neutral_attachment_support_is_deformation_proof": False,
                "neutral_attachment_cross_section_intersection_is_deformation_proof": False,
                "deformation_simulated": False,
                "hierarchy_or_weighting_inferred": False,
                "runtime_readiness_claimed": False,
            },
        }

    def test_three_materially_different_outputs(self):
        family = assemble_relation_family(self.partition_family, self.owner_report, self.contract)
        self.assertEqual(3, family["output_count"])
        by_id = {row["subset_id"]: row for row in family["outputs"]}
        self.assertEqual(["east"], by_id["intersecting"]["branch_ids"])
        self.assertEqual(["north"], by_id["overlap-disjoint"]["branch_ids"])
        self.assertEqual(["south", "north", "west", "top"], by_id["disjoint"]["branch_ids"])
        self.assertEqual([6, 6, 24], sorted(row["vertex_count"] for row in family["outputs"]))
        self.assertEqual(3, len({row["selection_digest"] for row in family["outputs"]}))
        self.assertEqual(3, len({row["vertex_index_digest"] for row in family["outputs"]}))
        self.assertFalse(family["rigging_authority"])

    def test_owner_pair_order_does_not_change_family(self):
        forward = assemble_relation_family(self.partition_family, self.owner_report, self.contract)
        reversed_report = copy.deepcopy(self.owner_report)
        reversed_report["pairs"] = list(reversed(reversed_report["pairs"]))
        reverse = assemble_relation_family(self.partition_family, reversed_report, self.contract)
        self.assertEqual(forward["family_digest"], reverse["family_digest"])

    def test_relation_modes_are_exact(self):
        self.assertEqual(["east"], derive_branch_ids(self.owner_report, self.contract, MODE_ATTACHMENT_INTERSECTING))
        self.assertEqual(["north"], derive_branch_ids(self.owner_report, self.contract, MODE_DECLARED_OVERLAP_ATTACHMENT_DISJOINT))
        self.assertEqual(["south", "north", "west", "top"], derive_branch_ids(self.owner_report, self.contract, MODE_ATTACHMENT_DISJOINT))

    def test_owner_relation_drift_fails_closed(self):
        report = copy.deepcopy(self.owner_report)
        for row in report["pairs"]:
            if row["branch_id"] == "north" and row["trunk_flex_zone_id"] == "upper":
                row["trunk_flex_intersects_neutral_attachment_cross_section"] = True
        with self.assertRaises(ValueError):
            assemble_relation_family(self.partition_family, report, self.contract)

    def test_pair_count_drift_fails_closed(self):
        report = copy.deepcopy(self.owner_report)
        report["pairs"].pop()
        report["pair_count"] = 9
        with self.assertRaises(ValueError):
            assemble_relation_family(self.partition_family, report, self.contract)

    def test_truth_boundary_widening_fails_closed(self):
        report = copy.deepcopy(self.owner_report)
        report["truth_boundary"]["hierarchy_or_weighting_inferred"] = True
        with self.assertRaises(ValueError):
            assemble_relation_family(self.partition_family, report, self.contract)

    def test_partition_identity_drift_fails_closed(self):
        family = copy.deepcopy(self.partition_family)
        family["family_digest"] = "0" * 64
        with self.assertRaises(ValueError):
            assemble_relation_family(family, self.owner_report, self.contract)

    def test_authority_expansion_fails_closed(self):
        contract = copy.deepcopy(self.contract)
        contract["production_weight_authorized"] = True
        with self.assertRaises(ValueError):
            validate_contract(contract)


if __name__ == "__main__":
    unittest.main()

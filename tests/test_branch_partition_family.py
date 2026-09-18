from __future__ import annotations

import copy
import unittest

from axm_nature_design.branch_partition_family import assemble_family, derive_partition, validate_contract


class BranchChildPartitionFamilyTests(unittest.TestCase):
    def setUp(self):
        self.source = {
            "branches": [
                {"id": "alpha", "points": [[0, 0, 0], [1, 0, 0]], "radii": [0.1, 0.05]},
                {"id": "beta", "points": [[0, 1, 0], [1, 1, 0]], "radii": [0.1, 0.05]},
            ],
            "leaf_clusters": [
                {"id": "alpha-leaves", "blades": [[0, 0], [10, 5]]},
                {"id": "beta-leaves", "blades": [[20, 0], [30, 5]]},
            ],
            "flex_zones": [
                {"id": "alpha-branch-flex", "center": [0, 0, 0], "radius": 0.12, "status": "DECLARED_NOT_DEFORMATION_TESTED"},
                {"id": "beta-branch-flex", "center": [0, 1, 0], "radius": 0.14, "status": "DECLARED_NOT_DEFORMATION_TESTED"},
            ],
        }
        vertices = [[float(i), 0.0, 0.0] for i in range(18)]
        triangles = [[i, i + 1, i + 2] for i in range(0, 18, 3)]
        self.mesh = {
            "vertices": vertices,
            "triangles": triangles,
            "regions": [
                {"id": "branch:alpha:0", "triangle_start": 0, "triangle_count": 1},
                {"id": "leaf:alpha-leaves:0", "triangle_start": 1, "triangle_count": 1},
                {"id": "leaf:alpha-leaves:1", "triangle_start": 2, "triangle_count": 1},
                {"id": "branch:beta:0", "triangle_start": 3, "triangle_count": 1},
                {"id": "leaf:beta-leaves:0", "triangle_start": 4, "triangle_count": 1},
                {"id": "leaf:beta-leaves:1", "triangle_start": 5, "triangle_count": 1},
            ],
        }
        self.contract = {
            "schema": "axm.nature-branch-child-partition-family/v0.1",
            "family_id": "test-family",
            "branch_ids": ["alpha", "beta"],
            "relation": "DERIVED_REGION_PARTITION_REVIEW_ONLY_NOT_RIGGING_AUTHORITY",
            "automatic_rigging_adoption": False,
            "source_mutation_authorized": False,
            "deformation_semantics_authorized": False,
            "organic_provider": {
                "repository": "owner/repo",
                "ref": "1" * 40,
                "source_path": "source.json",
                "source_blob": "2" * 40,
                "source_digest": "3" * 64,
                "builder_path": "builder.py",
                "builder_blob": "4" * 40,
                "generated_mesh_digest": "5" * 64,
            },
        }

    def test_two_materially_different_partitions_are_deterministic(self):
        family = assemble_family(self.source, self.mesh, self.contract)
        reverse = assemble_family(self.source, self.mesh, self.contract, ["beta", "alpha"])
        self.assertEqual(family["family_digest"], reverse["family_digest"])
        self.assertTrue(family["pairwise_vertex_disjoint"])
        self.assertEqual(2, family["branch_count"])
        self.assertEqual(2, len({row["partition_digest"] for row in family["partitions"]}))
        self.assertEqual(2, len({row["vertex_index_digest"] for row in family["partitions"]}))

    def test_partition_preserves_flex_truth_boundary(self):
        row = derive_partition(self.source, self.mesh, self.contract, "alpha")
        self.assertEqual("DECLARED_NOT_DEFORMATION_TESTED", row["flex_status"])
        self.assertFalse(row["deformation_tested"])
        self.assertFalse(row["source_authorized"])
        self.assertFalse(row["rigging_authorized"])

    def test_duplicate_branch_selector_fails_closed(self):
        with self.assertRaises(ValueError):
            assemble_family(self.source, self.mesh, self.contract, ["alpha", "alpha"])

    def test_unknown_branch_selector_fails_closed(self):
        with self.assertRaises(ValueError):
            derive_partition(self.source, self.mesh, self.contract, "gamma")

    def test_authority_expansion_fails_closed(self):
        contract = copy.deepcopy(self.contract)
        contract["automatic_rigging_adoption"] = True
        with self.assertRaises(ValueError):
            validate_contract(contract)

    def test_off_root_flex_zone_fails_closed(self):
        source = copy.deepcopy(self.source)
        source["flex_zones"][0]["center"][0] += 0.001
        with self.assertRaises(ValueError):
            derive_partition(source, self.mesh, self.contract, "alpha")

    def test_missing_generated_region_fails_closed(self):
        mesh = copy.deepcopy(self.mesh)
        mesh["regions"] = [row for row in mesh["regions"] if row["id"] != "leaf:alpha-leaves:1"]
        with self.assertRaises(ValueError):
            derive_partition(self.source, mesh, self.contract, "alpha")


if __name__ == "__main__":
    unittest.main()

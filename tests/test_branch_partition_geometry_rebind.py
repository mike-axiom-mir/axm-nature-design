from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from axm_nature_design.branch_partition_geometry_rebind import (
    assemble_geometry_rebind,
    validate_rebind_contract,
)


class BranchPartitionGeometryRebindTests(unittest.TestCase):
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
        regions = [
            {"id": "branch:alpha:0", "triangle_start": 0, "triangle_count": 1},
            {"id": "leaf:alpha-leaves:0", "triangle_start": 1, "triangle_count": 1},
            {"id": "leaf:alpha-leaves:1", "triangle_start": 2, "triangle_count": 1},
            {"id": "branch:beta:0", "triangle_start": 3, "triangle_count": 1},
            {"id": "leaf:beta-leaves:0", "triangle_start": 4, "triangle_count": 1},
            {"id": "leaf:beta-leaves:1", "triangle_start": 5, "triangle_count": 1},
        ]
        self.historical = {"vertices": vertices, "triangles": triangles, "regions": regions}
        self.migrated = {
            "vertices": copy.deepcopy(vertices),
            "triangles": [[tri[0], tri[2], tri[1]] for tri in triangles],
            "regions": copy.deepcopy(regions),
        }
        from axm_nature_design.branch_partition_family import assemble_family, digest
        self.predecessor_contract = {
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
                "generated_mesh_digest": digest(self.historical),
            },
        }
        self.rebind_contract = {
            "schema": "axm.nature-branch-child-partition-geometry-rebind/v0.1",
            "family_id": "test-rebind",
            "relation": "EXACT_GEOMETRY_RECEIVER_REBIND_SELECTION_ONLY",
            "branch_ids": ["alpha", "beta"],
            "predecessor_family_contract": {
                "path": "family.json",
                "blob": "5" * 40,
                "family_digest": assemble_family(self.source, self.historical, self.predecessor_contract)["family_digest"],
            },
            "organic_provider": {
                "repository": "owner/repo",
                "ref": "1" * 40,
                "source_path": "source.json",
                "source_blob": "2" * 40,
                "builder_path": "builder.py",
                "builder_blob": "4" * 40,
                "mesh_digest": digest(self.historical),
            },
            "geometry_receiver": {
                "repository": "owner/repo",
                "ref": "7" * 40,
                "source_path": "source.json",
                "source_blob": "2" * 40,
                "builder_path": "builder.py",
                "builder_blob": "8" * 40,
                "mesh_digest": digest(self.migrated),
            },
            "rigging_receiver_witness": {
                "repository": "owner/repo",
                "pr": 14,
                "head": "9" * 40,
                "branch_id": "beta",
                "selected_vertices": 9,
                "selected_triangles": 3,
                "fixed_vertices": 9,
            },
            "automatic_rigging_adoption": False,
            "source_mutation_authorized": False,
            "deformation_semantics_authorized": False,
            "geometry_authority_transferred": False,
            "automatic_downstream_adoption": False,
        }

    def test_two_materially_distinct_outputs_survive_receiver_winding_change(self):
        result = assemble_geometry_rebind(
            self.source,
            self.historical,
            self.migrated,
            self.predecessor_contract,
            self.rebind_contract,
        )
        self.assertEqual(2, result["branch_count"])
        self.assertEqual(2, len({row["partition_digest"] for row in result["comparisons"]}))
        self.assertTrue(all(row["selection_preserved"] for row in result["comparisons"]))
        self.assertTrue(result["receiver_mesh_identity_changed"])
        self.assertGreater(result["ordered_triangle_changes"], 0)
        self.assertEqual(result["historical_family_digest"], result["geometry_receiver_family_digest"])

    def test_geometry_authority_expansion_fails_closed(self):
        contract = copy.deepcopy(self.rebind_contract)
        contract["geometry_authority_transferred"] = True
        with self.assertRaises(ValueError):
            validate_rebind_contract(contract, self.predecessor_contract)

    def test_automatic_downstream_adoption_fails_closed(self):
        contract = copy.deepcopy(self.rebind_contract)
        contract["automatic_downstream_adoption"] = True
        with self.assertRaises(ValueError):
            validate_rebind_contract(contract, self.predecessor_contract)

    def test_region_identity_drift_fails_closed(self):
        migrated = copy.deepcopy(self.migrated)
        migrated["regions"][0]["id"] = "branch:alpha:renamed"
        from axm_nature_design.branch_partition_family import digest
        contract = copy.deepcopy(self.rebind_contract)
        contract["geometry_receiver"]["mesh_digest"] = digest(migrated)
        with self.assertRaises(ValueError):
            assemble_geometry_rebind(
                self.source, self.historical, migrated, self.predecessor_contract, contract
            )

    def test_triangle_membership_drift_fails_closed(self):
        migrated = copy.deepcopy(self.migrated)
        migrated["triangles"][0][0] = 17
        from axm_nature_design.branch_partition_family import digest
        contract = copy.deepcopy(self.rebind_contract)
        contract["geometry_receiver"]["mesh_digest"] = digest(migrated)
        with self.assertRaises(ValueError):
            assemble_geometry_rebind(
                self.source, self.historical, migrated, self.predecessor_contract, contract
            )


if __name__ == "__main__":
    unittest.main()

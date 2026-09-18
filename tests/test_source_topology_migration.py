import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axm_nature_design.organic_form import build_mesh, digest, load_source
from axm_nature_design.source_topology_migration import LINEAGE, evaluate, inspect_shared_edge_orientation

SOURCES = [
    ROOT / "examples" / "sapling_neutral_001.json",
    ROOT / "examples" / "compact_east_tree_neutral_001.json",
    ROOT / "examples" / "east_rear_tree_neutral_001.json",
]


class SourceTopologyMigrationTests(unittest.TestCase):
    def test_three_established_sources_match_exact_proven_reindex_digests(self):
        for path in SOURCES:
            with self.subTest(path=path.name):
                report = evaluate(load_source(path))
                self.assertEqual(report["status"], "PASS_SOURCE_GENERATOR_WINDING_MIGRATION")
                self.assertEqual(report["migrated_mesh_digest"], report["proven_reindex_digest"])
                self.assertNotEqual(report["migrated_mesh_digest"], report["historical_mesh_digest"])
                self.assertEqual(report["topology"]["shared_edge_orientation_conflicts"], 0)
                self.assertEqual(report["topology"]["boundary_edges"], 100)
                self.assertEqual(report["topology"]["nonmanifold_edges"], 0)
                self.assertEqual(report["vertices"], 390)
                self.assertEqual(report["triangles"], 570)

    def test_source_identity_is_not_rewritten_by_migration(self):
        for path in SOURCES:
            source = load_source(path)
            report = evaluate(copy.deepcopy(source))
            self.assertEqual(report["source_digest"], LINEAGE[source["study_id"]]["source_digest"])
            self.assertFalse(report["truth_boundary"]["source_json_rewritten"])
            self.assertTrue(report["truth_boundary"]["source_generator_index_emission_changed"])
            self.assertFalse(report["truth_boundary"]["predecessor_pass_transferred"])

    def test_east_rear_metadata_successor_rebind_preserves_migrated_mesh_identity(self):
        source = load_source(SOURCES[2])
        lineage = LINEAGE[source["study_id"]]
        self.assertEqual(digest(source), lineage["source_digest"])
        self.assertEqual(lineage["source_ref"], "fdc9d2b6ee729728551e22fd3eafa23ad60b6c7a")
        self.assertEqual(lineage["predecessor_source_ref"], "a4e5ee011e1d87f47866a7e6c6f4e66f57b6af12")

        predecessor = copy.deepcopy(source)
        predecessor["flex_zones"] = [
            zone for zone in predecessor["flex_zones"]
            if zone.get("id") != "north-top-branch-flex"
        ]
        self.assertEqual(digest(predecessor), lineage["predecessor_source_digest"])

        current_mesh_digest = digest(build_mesh(source))
        predecessor_mesh_digest = digest(build_mesh(predecessor))
        self.assertEqual(current_mesh_digest, lineage["proven_reindex_digest"])
        self.assertEqual(predecessor_mesh_digest, lineage["proven_reindex_digest"])
        self.assertEqual(current_mesh_digest, predecessor_mesh_digest)

        report = evaluate(source)
        self.assertFalse(report["truth_boundary"]["predecessor_pass_transferred"])
        self.assertEqual(report["predecessor_source_digest"], lineage["predecessor_source_digest"])

    def test_reversing_one_migrated_cap_face_reintroduces_a_shared_edge_conflict(self):
        source = load_source(SOURCES[0])
        mesh = build_mesh(source)
        tapered = next(region for region in mesh["regions"] if region["kind"] == "tapered-segment")
        cap_index = tapered["triangle_start"] + 2
        a, b, c = mesh["triangles"][cap_index]
        mesh["triangles"][cap_index] = [a, c, b]
        report = inspect_shared_edge_orientation(mesh)
        self.assertGreater(report["shared_edge_orientation_conflicts"], 0)

    def test_unknown_source_fails_closed(self):
        source = load_source(SOURCES[0])
        source["study_id"] = "unknown-source"
        with self.assertRaises(ValueError):
            evaluate(source)

    def test_truth_boundary_keeps_downstream_acceptance_held(self):
        report = evaluate(load_source(SOURCES[2]))
        boundary = report["truth_boundary"]
        self.assertFalse(boundary["connected_production_topology_proven"])
        self.assertFalse(boundary["self_intersection_checked"])
        self.assertFalse(boundary["normals_tangents_uvs_accepted"])
        self.assertFalse(boundary["deformation_accepted"])
        self.assertFalse(boundary["visual_receiving_scene_accepted"])
        self.assertFalse(boundary["runtime_or_gameplay_accepted"])


if __name__ == "__main__":
    unittest.main()

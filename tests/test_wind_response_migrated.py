import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from axm_nature_design.organic_form import build_mesh, digest, load_source
from axm_nature_design.source_topology_migration import inspect_shared_edge_orientation
from axm_nature_design.wind_response_migrated import (
    EXPECTED_SOURCE_DIGEST,
    HISTORICAL_NEUTRAL_MESH_DIGEST,
    MIGRATED_NEUTRAL_MESH_DIGEST,
    MIGRATION_HEAD,
    PROFILE,
    WEATHER_SEMANTICS,
    build_evidence,
    deform_mesh,
    load_spec,
    measure_sample,
    validate_spec,
)

SOURCE = ROOT / 'examples' / 'sapling_neutral_001.json'
SPEC = ROOT / 'examples' / 'sapling_wind_response_migrated_001.json'


class MigratedWindResponseTests(unittest.TestCase):
    def setUp(self):
        self.source = load_source(SOURCE)
        self.spec = load_spec(SPEC)

    def test_exact_source_and_migrated_generator_are_pinned(self):
        validate_spec(self.spec, self.source)
        self.assertEqual(digest(self.source), EXPECTED_SOURCE_DIGEST)
        self.assertEqual(digest(build_mesh(self.source)), MIGRATED_NEUTRAL_MESH_DIGEST)
        self.assertNotEqual(MIGRATED_NEUTRAL_MESH_DIGEST, HISTORICAL_NEUTRAL_MESH_DIGEST)
        self.assertEqual(self.spec['generator_migration']['head'], MIGRATION_HEAD)
        self.assertEqual(self.spec['weather_provenance']['semantics'], WEATHER_SEMANTICS)
        self.assertEqual(self.spec['response']['profile'], PROFILE)

    def test_neutral_endpoints_return_exact_migrated_mesh(self):
        neutral = build_mesh(self.source)
        start = deform_mesh(self.source, self.spec, 0.0)
        end = deform_mesh(self.source, self.spec, self.spec['response']['duration_s'])
        self.assertEqual(start, neutral)
        self.assertEqual(end, neutral)
        self.assertEqual(digest(start), MIGRATED_NEUTRAL_MESH_DIGEST)
        self.assertEqual(inspect_shared_edge_orientation(start)['shared_edge_orientation_conflicts'], 0)

    def test_peak_preserves_bounded_hierarchical_response(self):
        neutral = build_mesh(self.source)
        peak = deform_mesh(self.source, self.spec, 0.25)
        measured = measure_sample(
            neutral,
            peak,
            self.spec['weather_provenance']['visual_wind_xy'],
            self.spec['response']['anchor_z_m'],
        )
        self.assertAlmostEqual(measured['max_displacement_m'], 0.18, places=12)
        self.assertGreater(measured['max_downwind_projection_m'], 0.179999999)
        self.assertGreaterEqual(measured['min_downwind_projection_m'], -1e-12)
        self.assertLessEqual(measured['max_abs_crosswind_drift_m'], 1e-12)
        self.assertLessEqual(measured['max_anchor_displacement_m'], 1e-12)
        self.assertTrue(measured['structural']['pass'])
        self.assertEqual(neutral['triangles'], peak['triangles'])
        self.assertEqual(neutral['regions'], peak['regions'])
        self.assertEqual(inspect_shared_edge_orientation(peak)['shared_edge_orientation_conflicts'], 0)

    def test_all_samples_preserve_migrated_topology_and_exact_neutral_return(self):
        neutral = build_mesh(self.source)
        for time_s in self.spec['response']['sample_times_s']:
            deformed = deform_mesh(self.source, self.spec, time_s)
            self.assertEqual(neutral['triangles'], deformed['triangles'])
            self.assertEqual(neutral['regions'], deformed['regions'])
            self.assertEqual(len(neutral['vertices']), len(deformed['vertices']))
            self.assertEqual(inspect_shared_edge_orientation(deformed)['shared_edge_orientation_conflicts'], 0)

    def test_evidence_records_rebind_without_profile_rewrite(self):
        evidence = build_evidence(self.source, self.spec)
        self.assertEqual(evidence['state'], 'PASS_BOUNDED_VISUAL_WIND_RESPONSE')
        self.assertTrue(all(evidence['checks'].values()))
        self.assertFalse(evidence['migration_rebind']['response_profile_changed'])
        self.assertFalse(evidence['migration_rebind']['source_json_changed'])
        self.assertTrue(evidence['migration_rebind']['generator_triangle_winding_changed'])
        self.assertEqual(evidence['migration_rebind']['migrated_neutral_mesh_digest'], MIGRATED_NEUTRAL_MESH_DIGEST)

    def test_migration_identity_drift_fails_closed(self):
        bad = copy.deepcopy(self.spec)
        bad['generator_migration']['head'] = '0' * 40
        with self.assertRaises(ValueError):
            validate_spec(bad, self.source)


if __name__ == '__main__':
    unittest.main()

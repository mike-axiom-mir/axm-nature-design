import copy
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from axm_nature_design.organic_form import build_mesh, digest, load_source
from axm_nature_design.wind_response import (
    EXPECTED_NEUTRAL_MESH_DIGEST,
    EXPECTED_PRIOR_ARTIFACT_ID,
    EXPECTED_PRIOR_VFX_HEAD,
    EXPECTED_SOURCE_DIGEST,
    PROFILE,
    WEATHER_SEMANTICS,
    build_evidence,
    deform_mesh,
    load_spec,
    measure_sample,
    validate_spec,
    write_comparison_svg,
)

SOURCE = ROOT / 'examples' / 'sapling_neutral_001.json'
SPEC = ROOT / 'examples' / 'sapling_wind_response_001.json'


class WindResponseTests(unittest.TestCase):
    def setUp(self):
        self.source = load_source(SOURCE)
        self.spec = load_spec(SPEC)

    def test_exact_source_weather_and_before_evidence_are_pinned(self):
        validate_spec(self.spec, self.source)
        self.assertEqual(digest(self.source), EXPECTED_SOURCE_DIGEST)
        self.assertEqual(digest(build_mesh(self.source)), EXPECTED_NEUTRAL_MESH_DIGEST)
        self.assertEqual(self.spec['weather_provenance']['semantics'], WEATHER_SEMANTICS)
        self.assertEqual(self.spec['weather_provenance']['visual_wind_xy'], self.source['weather_handoff']['visual_wind_xy'])
        self.assertEqual(self.spec['prior_visual_baseline']['head'], EXPECTED_PRIOR_VFX_HEAD)
        self.assertEqual(self.spec['prior_visual_baseline']['artifact_id'], EXPECTED_PRIOR_ARTIFACT_ID)

    def test_neutral_endpoints_are_exact_meshes(self):
        neutral = build_mesh(self.source)
        at_start = deform_mesh(self.source, self.spec, 0.0)
        at_end = deform_mesh(self.source, self.spec, self.spec['response']['duration_s'])
        self.assertEqual(neutral, at_start)
        self.assertEqual(neutral, at_end)
        self.assertEqual(digest(at_start), EXPECTED_NEUTRAL_MESH_DIGEST)
        self.assertEqual(digest(at_end), EXPECTED_NEUTRAL_MESH_DIGEST)

    def test_peak_response_is_bounded_downwind_anchor_fixed_and_hierarchical(self):
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

        evidence = build_evidence(self.source, self.spec)
        hierarchy = evidence['hierarchy']
        self.assertAlmostEqual(hierarchy['primary_height_component_cap_m'], 0.12, places=12)
        self.assertAlmostEqual(hierarchy['branch_tip_secondary_component_cap_m'], 0.045, places=12)
        self.assertAlmostEqual(hierarchy['leaf_tip_secondary_component_cap_m'], 0.015, places=12)
        self.assertAlmostEqual(hierarchy['declared_displacement_ceiling_m'], 0.18, places=12)
        self.assertAlmostEqual(hierarchy['max_branch_secondary_weight'], 1.0, places=12)
        self.assertAlmostEqual(hierarchy['max_leaf_secondary_weight'], 1.0, places=12)
        self.assertLessEqual(hierarchy['max_leaf_base_support_gap_m'], 1e-12)

    def test_topology_and_region_identity_are_preserved(self):
        neutral = build_mesh(self.source)
        for time_s in self.spec['response']['sample_times_s']:
            deformed = deform_mesh(self.source, self.spec, time_s)
            self.assertEqual(neutral['triangles'], deformed['triangles'])
            self.assertEqual(neutral['regions'], deformed['regions'])
            self.assertEqual(len(neutral['vertices']), len(deformed['vertices']))

    def test_evidence_passes_only_bounded_visual_response_claim(self):
        evidence = build_evidence(self.source, self.spec)
        self.assertEqual(evidence['state'], 'PASS_BOUNDED_VISUAL_WIND_RESPONSE')
        self.assertTrue(all(evidence['checks'].values()))
        self.assertEqual([s['time_s'] for s in evidence['samples']], [0.0, 0.125, 0.25, 0.375, 0.5])
        self.assertIn('does not establish physical wind', evidence['truth_boundary'])

    def test_physical_semantics_are_rejected(self):
        bad = copy.deepcopy(self.spec)
        bad['weather_provenance']['semantics'] = 'PHYSICAL_WIND_SPEED'
        with self.assertRaises(ValueError):
            validate_spec(bad, self.source)

    def test_wrong_source_identity_is_rejected(self):
        bad = copy.deepcopy(self.spec)
        bad['source_provenance']['source_digest'] = '0' * 64
        with self.assertRaises(ValueError):
            validate_spec(bad, self.source)

    def test_held_global_shear_profile_cannot_silently_return(self):
        bad = copy.deepcopy(self.spec)
        bad['response']['profile'] = 'HEIGHT_WEIGHTED_HALF_SINE_DOWNWIND_VISUAL_SWAY'
        with self.assertRaises(ValueError):
            validate_spec(bad, self.source)
        self.assertEqual(self.spec['response']['profile'], PROFILE)

    def test_visual_comparisons_are_deterministic_and_contain_five_panels(self):
        meshes = [(t, deform_mesh(self.source, self.spec, t)) for t in self.spec['response']['sample_times_s']]
        with tempfile.TemporaryDirectory() as d:
            a = Path(d) / 'a.svg'
            b = Path(d) / 'b.svg'
            write_comparison_svg(meshes, a, 'front')
            write_comparison_svg(meshes, b, 'front')
            self.assertEqual(a.read_bytes(), b.read_bytes())
            text = a.read_text(encoding='utf-8')
            self.assertEqual(text.count('>t='), 5)
            self.assertIn('hierarchical visual-only', text)
            self.assertIn('<line', text)


if __name__ == '__main__':
    unittest.main()

import copy
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from axm_nature_design.organic_form import build_evidence, build_mesh, design_checks, digest, load_source, structural_checks, write_obj, write_svg

SOURCE=ROOT/'examples'/'sapling_neutral_001.json'

class OrganicFormTests(unittest.TestCase):
    def setUp(self):
        self.source=load_source(SOURCE)

    def test_baseline_is_deterministic_and_passes_authored_intent(self):
        a=build_evidence(self.source); b=build_evidence(copy.deepcopy(self.source))
        self.assertEqual(a,b)
        self.assertEqual(a['state'],'PASS_AUTHORED_ORGANIC_FORM_INTENT')
        self.assertEqual(a['source_digest'],digest(self.source))
        self.assertTrue(a['structural']['pass'])
        self.assertTrue(a['design']['pass'])

    def test_triangle_geometry_is_finite_bounded_and_non_degenerate(self):
        check=structural_checks(build_mesh(self.source))
        self.assertTrue(check['finite_vertices'])
        self.assertTrue(check['bounded_indices'])
        self.assertEqual(check['degenerate_triangles'],0)

    def test_donor_provenance_is_exact_and_pass_is_not_inherited(self):
        donor=self.source['donor_provenance']
        self.assertEqual(donor['repository'],'mike-axiom-mir/axm-universal-creation')
        self.assertEqual(donor['commit'],'b434a349cf159b392148b4dc9d68146573531a60')
        self.assertEqual(donor['path'],'src/axm_uc/rts_mesh.py')
        self.assertEqual(donor['license'],'Apache-2.0')
        self.assertEqual(donor['evidence_relation'],'DONOR_HINT_NOT_INHERITED_PASS')

    def test_trunk_taper_tamper_fails(self):
        bad=copy.deepcopy(self.source)
        bad['trunk'][3]['radius']=bad['trunk'][2]['radius']
        result=design_checks(bad,build_mesh(bad))
        self.assertFalse(result['checks']['trunk_taper_strict'])
        self.assertFalse(result['pass'])

    def test_crown_width_contract_is_falsifiable(self):
        bad=copy.deepcopy(self.source)
        bad['design_checks']['crown_width_x_m']=[2.8,3.0]
        result=design_checks(bad,build_mesh(bad))
        self.assertFalse(result['checks']['crown_width_x_range'])
        self.assertFalse(result['pass'])

    def test_flex_zones_remain_unproven(self):
        evidence=build_evidence(self.source)
        self.assertGreaterEqual(len(evidence['flex_zones']),4)
        self.assertTrue(all(z['status']=='DECLARED_NOT_DEFORMATION_TESTED' for z in evidence['flex_zones']))

    def test_environment_and_weather_handoffs_do_not_claim_integration(self):
        evidence=build_evidence(self.source)
        self.assertEqual(evidence['environment_handoff']['status'],'CANDIDATE_REPLACEMENT_NOT_COMPOSED')
        self.assertEqual(evidence['weather_handoff']['status'],'CONTEXT_ONLY_NOT_APPLIED_TO_FORM')

    def test_generated_obj_and_views_are_deterministic_and_distinct(self):
        mesh=build_mesh(self.source)
        with tempfile.TemporaryDirectory() as d:
            d=Path(d); write_obj(mesh,d/'a.obj'); write_obj(mesh,d/'b.obj')
            self.assertEqual((d/'a.obj').read_bytes(),(d/'b.obj').read_bytes())
            for view in ('front','side','top'): write_svg(mesh,d/f'{view}.svg',view)
            views=[(d/f'{view}.svg').read_bytes() for view in ('front','side','top')]
            self.assertEqual(len(set(views)),3)
            self.assertIn(b'<line',views[0])

if __name__=='__main__': unittest.main()

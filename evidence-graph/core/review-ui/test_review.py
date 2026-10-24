"""L7 data boundaries and generated-view lifecycle tests. Trusted captures only."""
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch
from build_review import build,bundle,read_reference,pointer,digest,CORE
sys.path.insert(0,str(CORE/'evaluation/refinement'))
import run_refinement

class ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.temp.cleanup)
        cls.root=Path(cls.temp.name);cls.ref=cls.root/'reference'
        run_refinement.execute(cls.ref);cls.files,cls.manifest=read_reference(cls.ref)
        cls.b=bundle(cls.files,'review');cls.v=bundle(cls.files,'validation')
    def row(self,id,cohort='review'):
        b=self.b if cohort=='review' else self.v
        return next(r for r in b['results'][0]['consumers'] if r['consumer']=='l7-'+id)
    def test_01_all_cases_not_cherry_picked(self):
        self.assertEqual((13,12),(len(self.b['assets']),len(self.b['relations'])))
        self.assertEqual((9,8),(len(self.v['assets']),len(self.v['relations'])))
    def test_02_signal_is_not_exception(self):
        r=self.row('c06')['review'];self.assertEqual('YES',r['prediction']['observed_field_access'])
        self.assertEqual('NO',r['prediction']['predicted_exception']);self.assertEqual('COMPLETED',r['tests']['execution'])
    def test_03_unsupported_preserves_unknown_even_after_failure(self):
        r=self.row('c10')['review'];self.assertEqual('UNKNOWN',r['prediction']['predicted_exception'])
        self.assertEqual('FAILED',r['tests']['execution'])
    def test_04_semantics_separate(self):
        a=self.row('n01','validation')['review'];b=self.row('n02','validation')['review']
        self.assertEqual(a['prediction']['predicted_exception'],b['prediction']['predicted_exception'])
        self.assertEqual('VIOLATED',a['tests']['business']);self.assertEqual('MET',b['tests']['business'])
    def test_05_three_silent_errors_visible(self):
        rows=self.v['results'][0]['consumers'];self.assertEqual(3,sum(r['review']['tests']['execution']=='COMPLETED' and r['review']['tests']['business']=='VIOLATED' for r in rows))
    def test_06_predictions_never_confirmed_by_execution(self):
        for b in [self.b,self.v]:
            for r in b['results'][0]['consumers']:
                self.assertEqual('NOT_TESTED',r['review']['prediction']['failure_confirmed_by_execution'])
                self.assertEqual('UNKNOWN',r['review']['prediction']['semantic_correctness'])
    def test_07_before_and_after_proof_ids_disjoint(self):
        for r in self.b['results'][0]['consumers']:
            a=r['review'];self.assertFalse(set(a['pre_evidence_ids'])&set(a['test_evidence_ids']))
            self.assertEqual(a['pre_evidence_ids'],r['evidence_ids'])
    def test_08_all_pointers_resolve(self):
        for b in [self.b,self.v]:
            for e in b['evidence']:self.assertEqual(e['details'],pointer(self.files,e['reference']))
    def test_09_no_fake_business_ownership(self):
        for a in self.b['assets']:self.assertEqual([],a['processes']);self.assertEqual('not_assessed',a['criticality'])
    def test_10_fixture_edges_not_claimed_http(self):
        self.assertTrue(all(r['kind']=='USES_RESPONSE' for r in self.v['relations']))
    def test_11_test_reference_not_used_for_prediction(self):
        files=deepcopy(self.files);truth=json.loads(files['truth-original.json'])
        truth['functional_outcomes']['c06'][0]['v2']['completed']=False
        files['truth-original.json']=json.dumps(truth).encode()
        new=bundle(files,'review');r=next(r for r in new['results'][0]['consumers'] if r['consumer']=='l7-c06')
        self.assertEqual(self.row('c06')['review']['prediction'],r['review']['prediction'])
        self.assertEqual('FAILED',r['review']['tests']['execution'])
    def test_12_prediction_tamper_refused(self):
        files=deepcopy(self.files);p=json.loads(files['predictions/base.json'])
        p['with_S']['c06']['predicted_exception']='YES';files['predictions/base.json']=json.dumps(p).encode()
        with self.assertRaises(ValueError):bundle(files,'review')
    def test_13_unsupported_cohort_refused(self):
        with self.assertRaises(ValueError):bundle(self.files,'other')
    def test_14_input_integrity(self):
        with tempfile.TemporaryDirectory() as t:
            import shutil
            root=Path(t)/'copy';shutil.copytree(self.ref,root);(root/'truth-original.json').write_text('{}')
            with self.assertRaises(ValueError):read_reference(root)
    def test_15_bootstrap_last_and_no_eager_boot(self):
        out=self.root/'view';build(self.ref,out)
        html=(out/'index.html').read_text();scripts=re.findall(r'<script src="([^"]+)" defer',html)
        self.assertEqual('view_bootstrap.js',scripts[-1]);self.assertIn('id="workspaceSource" disabled',html)
        self.assertNotIn('\nboot();',(out/'app.js').read_text());self.assertIn('window.EGStart = boot;',(out/'app.js').read_text())
        self.assertIn('window.EGStart();',(out/'EvidentGraph_L7.html').read_text())
    def test_16_m3_sources_untouched(self):
        from build_review import PREVIEW
        before={p.name:p.read_bytes() for p in PREVIEW.iterdir() if p.is_file()}
        build(self.ref,self.root/'preservation');self.assertEqual(before,{p.name:p.read_bytes() for p in PREVIEW.iterdir() if p.is_file()})
    def test_17_output_manifest(self):
        out=self.root/'checksums';m=build(self.ref,out)
        for name,h in m['outputs_sha256'].items():self.assertEqual(h,digest((out/name).read_bytes()))
    def test_18_no_overwrite(self):
        out=self.root/'existing';out.mkdir()
        with self.assertRaises(FileExistsError):build(self.ref,out)
    def test_19_no_write_to_project_source(self):
        with self.assertRaises(ValueError):build(self.ref,CORE.parent/'preview-m2/forbidden')
    def test_20_prechange_evidence_does_not_contain_posttest_outcome(self):
        for b in [self.b,self.v]:
            proof={e['id']:e for e in b['evidence']}
            for r in b['results'][0]['consumers']:
                text=json.dumps([proof[i] for i in r['review']['pre_evidence_ids']])
                self.assertNotIn('meets_requirement',text);self.assertNotIn('functional_outcomes',text)

if __name__=='__main__':unittest.main()

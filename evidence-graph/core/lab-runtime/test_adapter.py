"""Tests of L1-to-M3 adaptation. Actual L1 capture plus evidence mutation cases."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import lab
from adapt_run import adapt
from build_view import build, PREVIEW, FILES

class AdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        lab.execute(cls.root/'capture')
        cls.raw = (cls.root/'capture/run.json').read_bytes()
        cls.capture = json.loads(cls.raw)
    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()
    def bundle(self, edit=None):
        r = deepcopy(self.capture)
        if edit: edit(r)
        return adapt(lab.dump(r).encode())
    def row(self, b, name='pedidos'):
        return next(r for r in b['results'][0]['consumers'] if r['consumer']=='l1-'+name)
    def test_counts(self):
        b=self.bundle();self.assertEqual((5,4,17),(len(b['assets']),len(b['relations']),len(b['evidence'])))
    def test_origin_and_hash(self):
        b=adapt(self.raw);self.assertFalse(b['synthetic']);self.assertEqual(hashlib.sha256(self.raw).hexdigest(),b['provenance']['source_sha256'])
    def test_reference_result(self):
        b=self.bundle();self.assertEqual('FAIL_OBSERVED_IN_LAB',self.row(b)['lab_regression']);self.assertEqual('INCOMPATIBILITY',self.row(b)['impact'])
    def test_portal(self):
        r=self.row(self.bundle(),'portal');self.assertEqual('NO_INCOMPATIBILITY',r['impact']);self.assertEqual('PASS_IN_EXECUTED_CHECK',r['lab_regression'])
    def test_exportador(self):
        r=self.row(self.bundle(),'exportador');self.assertEqual(('INCOMPATIBILITY','UNKNOWN','NOT_VERIFIED'),(r['impact'],r['activity'],r['lab_regression']))
    def test_no_invented_process_or_iam(self):
        b=self.bundle();self.assertEqual([],b['processes']);self.assertTrue(all(a['criticality']=='not_assessed' for a in b['assets']));self.assertTrue(all(r['authorization']==r['field_access']=='NOT_EVALUATED' for r in b['results'][0]['consumers']))
    def test_referential_integrity(self):
        b=self.bundle();a={x['id'] for x in b['assets']};e={x['id'] for x in b['evidence']};sources={x['id'] for x in b['sources']}
        for rel in b['relations']:self.assertTrue({rel['source'],rel['target']}<=a);self.assertTrue(set(rel['evidence_ids'])<=e)
        for ev in b['evidence']:self.assertIn(ev['source'],sources)
        for r in b['results'][0]['consumers']:self.assertTrue(r['origin_ids']);self.assertTrue(set(r['evidence_ids'])<=e)
    def test_references_point_to_source(self):
        for e in self.bundle()['evidence']:
            value=self.capture
            for part in e['reference'].split('#/',1)[1].split('/'):
                value=value[int(part)] if isinstance(value,list) else value[part]
            self.assertIsNotNone(value)
    def test_no_business_values(self):
        b=self.bundle();self.assertNotIn('LAB-001',json.dumps(b['evidence']));self.assertNotIn('ativo',json.dumps(b['evidence']))
    def test_loss_of_all_spans_is_not_success(self):
        b=self.bundle(lambda r:r.update(spans=[]));self.assertEqual(4,len(b['assets']));self.assertTrue(all(c['activity']=='UNKNOWN' and c['lab_regression']=='NOT_VERIFIED' for c in b['results'][0]['consumers']));self.assertEqual('INCOMPATIBILITY',self.row(b)['impact'])
    def test_loss_of_after_preserves_before(self):
        b=self.bundle(lambda r:r.update(spans=[s for s in r['spans'] if s['attributes']['lab.api_version']=='v1']));r=self.row(b);self.assertEqual(('OBSERVED','NOT_VERIFIED'),(r['activity'],r['lab_regression']))
    def test_unknown_contract(self):
        b=self.bundle(lambda r:r['consumers'][0].update(required_fields=None));self.assertEqual('INCONCLUSIVE',self.row(b)['impact']);self.assertEqual('FAIL_OBSERVED_IN_LAB',self.row(b)['lab_regression'])
    def test_requirement_change_does_not_rewrite_test(self):
        b=self.bundle(lambda r:r['consumers'][0].update(required_fields=['status']));r=self.row(b);self.assertEqual(('NO_INCOMPATIBILITY','FAIL_OBSERVED_IN_LAB'),(r['impact'],r['lab_regression']))
    def test_orphan_server_not_observed(self):
        def mutate(r):
            for s in r['spans']:
                if s['kind']=='SERVER':s['parent_span_id']='0'*16
        b=self.bundle(mutate);self.assertTrue(all(x['activity']=='UNKNOWN' for x in b['results'][0]['consumers']))
    def test_database_orphan_no_read_claim(self):
        def mutate(r):
            for s in r['spans']:
                if s['attributes'].get('db.system.name'):s['parent_span_id']='0'*16
        b=self.bundle(mutate);self.assertFalse(any(e['kind']=='READS' for e in b['relations']));self.assertEqual('OBSERVED',self.row(b)['activity'])
    def test_database_version_mismatch(self):
        def mutate(r):
            for s in r['spans']:
                if s['attributes'].get('db.system.name'):s['attributes']['lab.api_version']='v0'
        b=self.bundle(mutate);self.assertEqual(3,len(b['relations']))
    def test_replayed_span_rejected(self):
        with self.assertRaises(ValueError):self.bundle(lambda r:r['spans'].append(deepcopy(r['spans'][0])))
    def test_unsupported_schema(self):
        with self.assertRaises(ValueError):self.bundle(lambda r:r.update(schema='unknown'))
    def test_outside_interval(self):
        with self.assertRaises(ValueError):self.bundle(lambda r:r['spans'][0].update(start_ns=1))
    def test_duplicate_consumer(self):
        with self.assertRaises(ValueError):self.bundle(lambda r:r['consumers'][0].update(id='portal'))
    def test_missing_openapi(self):
        with self.assertRaises(ValueError):self.bundle(lambda r:r['openapi'].pop('v2'))
    def test_determinism(self):self.assertEqual(adapt(self.raw),adapt(self.raw))
    def test_separate_capture_id(self):
        newer=lab.dump(self.capture).encode()+b' ';self.assertNotEqual(adapt(self.raw)['dataset_version'],adapt(newer)['dataset_version'])
    def test_build_preserves_m3_sources(self):
        before={n:(PREVIEW/n).read_bytes() for n in FILES}
        out=self.root/'view';info=build(self.root/'capture/run.json',out)
        self.assertEqual((5,240),(info['lab_assets'],info['aurora_assets']))
        self.assertEqual(before,{n:(PREVIEW/n).read_bytes() for n in FILES})
        self.assertIn('location.hash', (out/'data.js').read_text())
        self.assertTrue((out/'EvidentGraph_L2.html').is_file())
        self.assertFalse((out/'lab.sqlite').exists())
        with self.assertRaises(FileExistsError):build(self.root/'capture/run.json',out)

if __name__=='__main__':unittest.main()

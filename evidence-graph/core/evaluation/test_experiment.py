"""Test measurement, data separation and failure preservation, not guaranteed gains."""
import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import collect_experiment as collector
from metrics import score
import oracle_consumers
from predict_sources import predict, MODES, QUESTIONS
import run_experiment as runner


class MetricsTests(unittest.TestCase):
    def test_perfect(self):
        m=score(['YES','NO'],['YES','NO']);self.assertEqual(2,m['correct']);self.assertEqual(1,m['precision'])
    def test_no_answers_is_not_perfect(self):
        m=score(['YES','NO'],['UNKNOWN','UNKNOWN'])
        self.assertEqual(0,m['coverage']);self.assertEqual(0,m['correct_over_known']);self.assertIsNone(m['accuracy_decided'])
    def test_abstained_positives_stay_in_denominator(self):
        m=score(['YES','YES','NO'],['YES','UNKNOWN','NO'])
        self.assertEqual(.5,m['positive_recovery']);self.assertEqual(1,m['recall_decided'])
    def test_errors_counted(self):
        m=score(['YES','NO'],['NO','YES']);self.assertEqual((1,1),(m['fp'],m['fn']));self.assertEqual(0,m['correct'])
    def test_unknown_truth_excluded_not_correct(self):
        m=score(['UNKNOWN','YES'],['UNKNOWN','YES']);self.assertEqual(1,m['known_reference']);self.assertEqual(1,m['correct'])
    def test_assertion_without_known_reference_reported(self):
        m=score(['UNKNOWN'],['YES']);self.assertEqual(1,m['asserted_on_unknown_reference']);self.assertIsNone(m['precision'])
    def test_undefined_precision(self):
        m=score(['NO'],['NO']);self.assertIsNone(m['precision']);self.assertIsNone(m['positive_recovery'])
    def test_invalid(self):
        for t,p in [(['YES'],[]),(['YES'],['SAFE']),(['MAYBE'],['YES'])]:
            with self.assertRaises(ValueError):score(t,p)


class ExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.temp.cleanup)
        cls.root=Path(cls.temp.name)/'result';cls.results=runner.execute(cls.root)
        cls.evidence=json.loads((cls.root/'evidence.json').read_text())
        cls.truth=json.loads((cls.root/'truth.json').read_text())
        cls.audit=json.loads((cls.root/'audit.json').read_text())
    def setUp(self):self.e=deepcopy(self.evidence)
    def test_real_transport_and_baseline_only(self):
        self.assertEqual('HTTP loopback TCP',self.audit['transport'])
        self.assertEqual((22,11),(self.audit['baseline_spans'],self.audit['baseline_traces']))
        self.assertEqual(0,self.audit['oracle_spans_in_input'])
        self.assertTrue(all(s['attributes']['eval.phase']=='baseline' for s in self.e['R']))
    def test_ground_truth_is_behavior_not_requirement_list(self):
        labels=self.truth['labels']
        self.assertEqual('YES',labels['c07'][QUESTIONS[0]])
        self.assertEqual(['status'],self.e['C']['c07']['required_fields'])
        self.assertEqual('NO',labels['c12'][QUESTIONS[0]])
        self.assertEqual(['cliente_id'],self.e['C']['c12']['required_fields'])
    def test_future_probe_not_input(self):
        serialized=json.dumps(self.e)
        for key in ['functional_outcomes','permission_probes','reference-reader','lab.check','regression_after_change']:
            self.assertNotIn(key,serialized)
    def test_oracle_module_has_no_predictor_import(self):
        tree=ast.parse(Path(oracle_consumers.__file__).read_text())
        names=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
        self.assertTrue(set(names)<= {'collections.abc','typing'})
        accessed = [n.id for n in ast.walk(tree) if isinstance(n, ast.Name)]
        indexed = [n.slice.value for n in ast.walk(tree) if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant)]
        self.assertNotIn('required_fields', accessed + indexed)
    def test_predictor_does_not_open_labels_or_import_oracle(self):
        text=(runner.HERE/'predict_sources.py').read_text();tree=ast.parse(text)
        imports=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
        self.assertNotIn('oracle_consumers',imports);self.assertNotIn('collect_experiment',imports)
        reads=[ast.unparse(n) for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='read_text']
        self.assertEqual(["args.evidence.read_text(encoding='utf-8')"],reads)
    def test_oracle_not_changed_by_declarations(self):
        with patch.dict(collector.DECLARED,{s:[] for s in self.e['subjects']},clear=True):
            _,truth,_=collector.collect()
        self.assertEqual(self.truth['labels'],truth['labels'])
    def test_read_before_change_is_not_oracle_of_failure(self):
        self.assertEqual('NO',self.truth['labels']['c06'][QUESTIONS[0]])
        self.assertEqual('YES',predict(self.e,'R')['c06'][QUESTIONS[0]])
    def test_optional_lookup_can_still_fail(self):
        self.assertEqual('YES',self.truth['labels']['c11'][QUESTIONS[0]])
        self.assertEqual('UNKNOWN',predict(self.e,'R')['c11'][QUESTIONS[0]])
    def test_unseen_branch_not_declared_safe(self):
        self.assertEqual('YES',self.truth['labels']['c10'][QUESTIONS[0]])
        self.assertEqual('UNKNOWN',predict(self.e,'CRA')['c10'][QUESTIONS[0]])
    def test_missing_runtime_not_safe(self):
        self.e['R']=[];pred=predict(self.e,'CRA')
        self.assertEqual('YES',pred['c01'][QUESTIONS[0]])
        self.assertTrue(all(p[QUESTIONS[1]]=='UNKNOWN' for p in pred.values()))
    def test_conflict_abstains_instead_of_hiding(self):
        pred=predict(self.e,'CR')['c07'];self.assertEqual('UNKNOWN',pred[QUESTIONS[0]])
        self.assertIn('conflicting_sources:abstain',pred['reasons'])
    def test_denial_does_not_hide_intrinsic_incompatibility(self):
        r=predict(self.e,'CRA')['c08'];self.assertEqual('NO',r[QUESTIONS[2]])
        self.assertEqual('YES',r[QUESTIONS[0]]);self.assertEqual('UNKNOWN',r[QUESTIONS[1]])
    def test_unknown_policy_stays_unknown(self):
        self.assertEqual('UNKNOWN',predict(self.e,'CRA')['c09'][QUESTIONS[2]])
    def test_replayed_spans_do_not_multiply_support(self):
        base=predict(self.e,'CRA');self.e['R']+=deepcopy(self.e['R'])
        self.assertEqual(base,predict(self.e,'CRA'))
    def test_conflicting_duplicate_span_not_accepted(self):
        s=deepcopy(next(s for s in self.e['R'] if s['kind']=='CLIENT' and s['attributes']['eval.subject']=='c04'))
        s['attributes']['eval.indexed_fields']=['status'];self.e['R'].append(s)
        self.assertEqual('UNKNOWN',predict(self.e,'R')['c04'][QUESTIONS[1]])
    def test_wrong_environment_not_correlated(self):
        for s in self.e['R']:s['attributes']['eval.environment']='other'
        self.assertTrue(all(r[QUESTIONS[1]]=='UNKNOWN' for r in predict(self.e,'R').values()))
    def test_post_change_spans_not_used(self):
        for s in self.e['R']:s['attributes']['eval.phase']='oracle'
        self.assertTrue(all(r[QUESTIONS[1]]=='UNKNOWN' for r in predict(self.e,'R').values()))
    def test_wrong_parent_not_correlated(self):
        for s in self.e['R']:
            if s['kind']=='SERVER':s['parent_span_id']='f'*16
        self.assertTrue(all(r[QUESTIONS[1]]=='UNKNOWN' for r in predict(self.e,'R').values()))
    def test_wrong_version_not_correlated(self):
        for s in self.e['R']:
            if s['kind']=='SERVER':s['attributes']['eval.version']='v2'
        self.assertEqual('UNKNOWN',predict(self.e,'R')['c04'][QUESTIONS[1]])
    def test_outside_time_not_correlated(self):
        self.e['context']['window_end_ns']=0
        self.assertEqual('UNKNOWN',predict(self.e,'R')['c04'][QUESTIONS[1]])
    def test_expired_document_ignored(self):
        for d in self.e['C'].values():d['valid_until']=self.e['context']['at']
        self.assertEqual('UNKNOWN',predict(self.e,'C')['c01'][QUESTIONS[0]])
    def test_no_silent_oracle_input(self):
        self.e['truth']=self.truth
        with self.assertRaises(ValueError):predict(self.e,'CRA')
    def test_unknown_condition_refused(self):
        with self.assertRaises(ValueError):predict(self.e,'ALL')
    def test_no_secrets_or_business_values_in_inputs(self):
        s=json.dumps(self.e)
        for k in ['Bearer ','L6-001','Authorization','ativo']:self.assertNotIn(k,s)
    def test_frozen_protocol(self):
        lock=json.loads((self.root/'protocol-lock.json').read_text())
        self.assertEqual(lock['sha256'],{n:runner.sha(runner.HERE/n) for n in runner.FREEZE})
    def test_artifact_hashes(self):
        m=json.loads((self.root/'manifest.json').read_text())
        for name,h in m['files_sha256'].items():self.assertEqual(h,runner.sha(self.root/name))
    def test_existing_output_not_overwritten(self):
        before=runner.sha(self.root/'evidence.json')
        with self.assertRaises(FileExistsError):runner.execute(self.root)
        self.assertEqual(before,runner.sha(self.root/'evidence.json'))
    def test_output_parent_traversal_refused(self):
        path=runner.HERE/'runs'/'..'/'..'/'lab-runtime'/'forbidden-output'
        with self.assertRaises(ValueError):runner.execute(path)
        self.assertFalse(path.resolve().exists())
    def test_symlink_output_refused(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'alias';p.symlink_to(self.root,target_is_directory=True)
            with self.assertRaises(ValueError):runner.execute(p/'new')
    def test_no_hiding_errors_from_report(self):
        m=self.results['base']['CRA'][QUESTIONS[0]]
        self.assertGreater(m['fp'],0);self.assertGreater(m['abstained'],0)
        self.assertLess(m['precision'],self.results['base']['C'][QUESTIONS[0]]['precision'])
    def test_denominators_and_view_sizes(self):
        self.assertEqual(set(runner.VIEWS),set(self.results))
        for v in self.results.values():
            self.assertEqual(set(MODES),set(v))
            for q in v.values():
                for m in q.values():
                    self.assertEqual(12,m['n']);self.assertEqual(12,m['decided']+m['abstained']+m['unknown_reference'])
    def test_unauthenticated_server_not_correlated(self):
        for s in self.e['R']:
            if s['kind']=='SERVER':s['attributes']['eval.authenticated']=False
        self.assertEqual('UNKNOWN',predict(self.e,'R')['c04'][QUESTIONS[1]])
    def test_source_masks_do_not_mutate_capture(self):
        before=deepcopy(self.e);list(runner.variants(self.e));self.assertEqual(before,self.e)
    def test_case_table_contains_all_answers(self):
        import csv
        with (self.root/'cases.csv').open() as f:rows=list(csv.DictReader(f))
        self.assertEqual(12*3*7*6,len(rows))
    def test_can_permission_does_not_improve_break_by_magic(self):
        for view in self.results:
            self.assertEqual(self.results[view]['CR'][QUESTIONS[0]],self.results[view]['CRA'][QUESTIONS[0]])

if __name__=='__main__':unittest.main()

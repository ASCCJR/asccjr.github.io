"""Tests of the bounded analyzer, source separation and complete experiment.

No score is presented as generalization. Unsupported cases must abstain.
"""
import ast
from copy import deepcopy
import inspect
import json
from pathlib import Path
import tempfile
import textwrap
import unittest
from unittest.mock import patch

from bounded_static import analyze, source_hash
from candidate import refine
import challenges
import run_refinement as runner
from run_refinement import exact_shape

BEFORE = exact_shape(['cliente_id','status'])
AFTER = exact_shape(['status'])

class StaticTests(unittest.TestCase):
    def check(self, source, answer, **kwargs):
        r=analyze(textwrap.dedent(source),kwargs.get('before',BEFORE),kwargs.get('after',AFTER))
        self.assertEqual(answer,r['answer'],r);return r
    def expression(self, expression, answer):
        return self.check('def client(body, options):\n    return '+expression+'\n',answer)
    def test_01_unhandled_index(self):self.expression("body['cliente_id']",'YES')
    def test_02_status_only(self):self.expression("body['status']",'NO')
    def test_03_upper_index(self):self.expression("'pedido:' + body['cliente_id'].upper()",'YES')
    def test_04_get_default(self):self.expression("body.get('cliente_id','ANONIMO')",'NO')
    def test_05_optional_get_can_raise(self):
        r=self.expression("body.get('cliente_id').upper()",'YES');self.assertEqual('AttributeError',r['after'])
    def test_06_none_return_completes_but_not_semantic_proof(self):self.expression("body.get('cliente_id')",'NO')
    def test_07_caught_keyerror(self):
        self.check("""\
def client(body, options):
    try:
        return body['cliente_id']
    except KeyError:
        return 'ANONIMO'
""",'NO')
    def test_08_catch_not_attributeerror(self):
        self.check("""\
def client(body, options):
    try:
        return body.get('cliente_id').upper()
    except KeyError:
        return 'ANONIMO'
""",'YES')
    def test_09_unsupported_handler_even_if_not_taken(self):
        self.check("""\
def client(body, options):
    try:
        return body['status']
    except KeyError:
        return external()
""",'UNKNOWN')
    def test_10_condition_abstains(self):
        self.check("""\
def client(body, options):
    if options.get('full'):
        return body['cliente_id']
    return body['status']
""",'UNKNOWN')
    def test_11_dynamic_index_abstains(self):self.expression("body[options['field']]",'UNKNOWN')
    def test_12_external_call_abstains(self):self.expression("normalize(body['cliente_id'])",'UNKNOWN')
    def test_13_loop_abstains(self):self.check("def f(body, options):\n for x in body:\n  return x",'UNKNOWN')
    def test_14_unsupported_slice(self):self.expression("body.get('cliente_id','000')[-3:]",'UNKNOWN')
    def test_15_unsupported_len(self):self.expression("len(body.get('cliente_id',''))",'UNKNOWN')
    def test_16_baseline_failure_not_change_failure(self):
        r=self.expression("body['inexistente']",'UNKNOWN');self.assertEqual('baseline_not_established',r['basis'])
    def test_17_open_object_not_assumed_closed(self):
        schema=deepcopy(AFTER);schema['additionalProperties']=True
        self.check("def c(body, options):\n return body['cliente_id']",'UNKNOWN',after=schema)
    def test_18_optional_property_rejected(self):
        schema=deepcopy(BEFORE);schema['required']=['status']
        self.check("def c(body, options):\n return body['cliente_id']",'UNKNOWN',before=schema)
    def test_19_nullable_schema_rejected(self):
        schema=deepcopy(BEFORE);schema['properties']['cliente_id']={'type':['string','null']}
        self.check("def c(body, options):\n return body['cliente_id']",'UNKNOWN',before=schema)
    def test_20_numeric_type_rejected(self):
        schema=deepcopy(BEFORE);schema['properties']['cliente_id']={'type':'number'}
        self.check("def c(body, options):\n return body['cliente_id']",'UNKNOWN',before=schema)
    def test_21_no_execution_of_source(self):
        with tempfile.TemporaryDirectory() as t:
            target=Path(t)/'should-not-exist'
            self.expression(f"open({str(target)!r},'w').write('bad')",'UNKNOWN')
            self.assertFalse(target.exists())
    def test_22_decorator_rejected(self):self.check("@dangerous\ndef c(body, options):\n return body['status']",'UNKNOWN')
    def test_23_async_rejected(self):self.check("async def c(body, options):\n return body['status']",'UNKNOWN')
    def test_24_multiple_functions_rejected(self):self.check("def a(body, options):\n return 'a'\ndef b(body, options):\n return 'b'",'UNKNOWN')
    def test_25_syntax_error_abstains(self):self.check('def :::','UNKNOWN')
    def test_26_source_size_bounded(self):self.check('#'+'x'*16001,'UNKNOWN')
    def test_27_keyword_call_abstains(self):self.expression("body.get('cliente_id',default='x')",'UNKNOWN')
    def test_28_upper_none_error(self):self.expression("'route:' + body.get('cliente_id')",'YES')
    def test_29_try_else_rejected(self):
        self.check("""\
def c(body, options):
    try:
        return body['cliente_id']
    except KeyError:
        return 'x'
    finally:
        external()
""",'UNKNOWN')
    def test_duplicate_args_rejected(self):
        self.check("def f(body, body):\n return body['status']",'UNKNOWN')
    def test_30_names_do_not_encode_subject_ids(self):
        a=self.expression("body['cliente_id']",'YES')
        b=analyze("def arbitrary(response, ignored):\n return response['cliente_id']\n",BEFORE,AFTER)
        self.assertEqual(a['answer'],b['answer'])


class ExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.tmp.cleanup)
        cls.root=Path(cls.tmp.name)/'run';cls.result=runner.execute(cls.root)
        cls.e=json.loads((cls.root/'inputs/base-evidence.json').read_text())
        cls.s=json.loads((cls.root/'inputs/base-sources.json').read_text())
        cls.b=json.loads((cls.root/'predictions/base.json').read_text())
    def test_01_original_baseline_reproduced(self):
        m=self.result['original_12']['base']['A_CRA']
        self.assertEqual((7,2,0,3),(m['correct'],m['fp'],m['fn'],m['abstained']))
    def test_02_no_evidence_not_success(self):
        m=self.result['original_12']['base']['B_without_S'];self.assertEqual(12,m['abstained']);self.assertEqual(0,m['correct'])
    def test_03_extra_source_not_claimed_as_fusion_gain(self):
        for group in self.result['original_12'].values():self.assertEqual(group['S_only'],group['B_with_S'])
    def test_04_caught_read_stays_observed_without_predicted_exception(self):
        r=self.b['with_S']['c06'];self.assertEqual('YES',r['observed_field_access']);self.assertEqual('NO',r['predicted_exception'])
        self.assertEqual('YES',r['potential_impact']);self.assertEqual('UNKNOWN',r['semantic_correctness'])
    def test_05_false_manifest_not_hidden(self):
        for subject in ('c07','c12'):self.assertTrue(self.b['with_S'][subject]['declaration_source_disagreement'])
    def test_06_unseen_branch_stays_unknown(self):self.assertEqual('UNKNOWN',self.b['with_S']['c10']['predicted_exception'])
    def test_07_unsafe_optional_get(self):self.assertEqual('YES',self.b['with_S']['c11']['predicted_exception'])
    def test_08_no_confirmation_from_prechange_inputs(self):
        for arm in self.b.values():self.assertTrue(all(r['failure_confirmed_by_execution']=='NOT_TESTED' for r in arm.values()))
    def test_09_sources_expire(self):self.assertEqual(12,self.result['original_12']['stale_source']['B_with_S']['abstained'])
    def test_10_hash_failure_abstains(self):self.assertEqual(12,self.result['original_12']['wrong_source_hash']['B_with_S']['abstained'])
    def test_11_wrong_version_abstains(self):
        s=deepcopy(self.s)
        for r in s.values():r['version']='v999'
        self.assertTrue(all(r['predicted_exception']=='UNKNOWN' for r in refine(self.e,s).values()))
    def test_12_wrong_environment_abstains(self):
        s=deepcopy(self.s)
        for r in s.values():r['environment']='production'
        self.assertTrue(all(r['predicted_exception']=='UNKNOWN' for r in refine(self.e,s).values()))
    def test_13_no_synthetic_runtime_for_expanded_cases(self):
        e=json.loads((self.root/'inputs/new_cases-evidence.json').read_text());self.assertEqual([],e['R']);self.assertEqual({},e['C'])
    def test_14_silent_errors_separate_from_exceptions(self):
        rows=self.result['new_cases'];self.assertEqual(3,sum(r['silent_wrong_result'] for r in rows.values()))
        for s in ('n01','n03','n07'):
            self.assertEqual('NO',rows[s]['exception_regression']);self.assertEqual('YES',rows[s]['requirement_regression'])
    def test_15_identical_code_different_business_rule(self):
        rows=self.result['new_cases'];sources=json.loads((self.root/'inputs/new_cases-sources.json').read_text())
        self.assertEqual(sources['n01']['source_sha256'],sources['n02']['source_sha256'])
        self.assertNotEqual(rows['n01']['requirement_regression'],rows['n02']['requirement_regression'])
        self.assertEqual(rows['n01']['prediction'],rows['n02']['prediction'])
    def test_16_expanded_unsupported_not_marked_safe(self):
        rows=self.result['new_cases']
        for s in ('n03','n04','n05','n06','n07'):self.assertEqual('UNKNOWN',rows[s]['prediction'])
    def test_17_semantic_reference_uses_http(self):
        audit=json.loads((self.root/'audit-semantic.json').read_text())
        self.assertEqual('HTTP loopback TCP',audit['transport']);self.assertEqual(18,len(audit['receipts']))
        self.assertTrue(all(r['status']==200 for r in audit['receipts']))
    def test_18_predictor_reads_no_truth_requirements_or_oracle(self):
        tree=ast.parse((runner.HERE/'candidate.py').read_text())
        imports=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
        self.assertNotIn('challenges',imports);self.assertNotIn('oracle_consumers',imports)
        reads=[ast.unparse(n.func.value) for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='read_text']
        self.assertEqual({'args.evidence','args.sources'},set(reads))
    def test_19_unknown_reference_targets_not_inserted_in_source_inputs(self):
        for path in (self.root/'inputs').glob('*.json'):
            s=path.read_text()
            for key in ('meets_requirement','functional_outcomes','requirement_regression','truth.json'):
                self.assertNotIn(key,s)
    def test_20_manifest(self):
        manifest=json.loads((self.root/'manifest.json').read_text())
        for name,h in manifest['files_sha256'].items():self.assertEqual(h,runner.sha(self.root/name))
    def test_21_frozen_sources_unchanged(self):
        self.assertEqual(runner.freeze(),json.loads((self.root/'protocol-lock.json').read_text())['files_sha256'])
    def test_22_no_overwrite(self):
        h=runner.sha(self.root/'results.json')
        with self.assertRaises(FileExistsError):runner.execute(self.root)
        self.assertEqual(h,runner.sha(self.root/'results.json'))
    def test_23_forbidden_project_output(self):
        with self.assertRaises(ValueError):runner.execute(runner.EVALUATION.parent/'lab-runtime/forbidden')
    def test_24_symlink_refused(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'alias';p.symlink_to(self.root,target_is_directory=True)
            with self.assertRaises(ValueError):runner.execute(p/'child')
    def test_25_denominators_preserved(self):
        for view in self.result['original_12'].values():
            for m in view.values():self.assertEqual(12,m['correct']+m['fp']+m['fn']+m['abstained'])
        m=self.result['new_8_metrics'];self.assertEqual(8,m['correct']+m['fp']+m['fn']+m['abstained'])
    def test_26_policy_does_not_erase_exception_risk(self):
        r=self.b['with_S']['c08'];self.assertEqual('NO',r['can_access_endpoint']);self.assertEqual('YES',r['predicted_exception'])
    def test_27_changing_expectation_not_prediction(self):
        inputs=deepcopy(self.e);sources=deepcopy(self.s)
        with patch.dict(runner.__dict__,{'semantic_reference':lambda:({}, {})}):
            self.assertEqual(self.b['with_S'],refine(inputs,sources))
    def test_28_partial_not_published_as_success(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'fail'
            with patch.object(runner,'collect',side_effect=RuntimeError('test injected')):
                with self.assertRaises(RuntimeError):runner.execute(p)
            self.assertTrue((p/'INCOMPLETE.txt').exists());self.assertFalse((p/'manifest.json').exists())
    def test_29_source_strings_never_executed(self):
        code=(runner.HERE/'bounded_static.py').read_text();tree=ast.parse(code)
        calls={n.func.id for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)}
        self.assertFalse(calls & {'eval','exec','compile','__import__'})
    def test_source_for_different_change_not_reused(self):
        e=deepcopy(self.e);e['change']['removed_fields']=['status']
        for row in refine(e,self.s).values():
            self.assertEqual('UNKNOWN',row['predicted_exception'])
            self.assertEqual('source_change_mismatch',row['prediction_basis']['basis'])
    def test_30_full_report_preserves_costs_and_limits(self):
        s=(self.root/'report.md').read_text()
        for term in ('Comparação desigual','12','5 inconclusivas','3 casos','não são holdout','regra de negócio'):
            self.assertIn(term,s)

if __name__ == '__main__':unittest.main()

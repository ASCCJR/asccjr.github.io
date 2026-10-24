"""L5 policy, actual HTTP enforcement, evidence loss and view-contract regressions."""
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest
import httpx
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
import lab
import auth_lab as a
from auth_policy import evaluate, ACTION, RESOURCE, ENVIRONMENT
from auth_adapter import adapt
from build_auth_view import build
from build_view import PREVIEW


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime.now(timezone.utc);self.p=a.policy_fixture(self.now)
    def eval(self,subject='pedidos',**kw):
        args=dict(policy=self.p,subject=subject,action=ACTION,resource=RESOURCE,
                  environment=ENVIRONMENT,at=self.now.isoformat());args.update(kw)
        return evaluate(**args)
    def test_allow(self):self.assertEqual('ALLOW',self.eval()['decision'])
    def test_deny(self):self.assertEqual('DENY',self.eval('portal')['decision'])
    def test_default_deny(self):self.assertEqual('DEFAULT_DENY',self.eval('other')['reason'])
    def test_missing_policy(self):self.assertEqual('INDETERMINATE',self.eval(policy=None)['decision'])
    def test_identity_unknown(self):self.assertEqual('IDENTITY_UNRESOLVED',self.eval(subject=None)['reason'])
    def test_wrong_action(self):self.assertEqual('INDETERMINATE',self.eval(action='customers:delete')['decision'])
    def test_wrong_resource(self):self.assertEqual('INDETERMINATE',self.eval(resource=RESOURCE+':cpf')['decision'])
    def test_wrong_environment(self):self.assertEqual('INDETERMINATE',self.eval(environment='production')['decision'])
    def test_expired(self):self.p['valid_until']=self.now.isoformat();self.assertEqual('OUTSIDE_VALIDITY',self.eval()['reason'])
    def test_future(self):self.p['valid_from']=(self.now+timedelta(days=1)).isoformat();self.assertEqual('INDETERMINATE',self.eval()['decision'])
    def test_naive_time(self):self.assertEqual('INDETERMINATE',self.eval(at='2026-10-16')['decision'])
    def test_incomplete_cannot_allow(self):self.p['complete']=False;self.assertEqual('INDETERMINATE',self.eval()['decision'])
    def test_incomplete_retains_deny(self):self.p['complete']=False;self.assertEqual('DENY',self.eval('portal')['decision'])
    def test_deny_overrides(self):self.p['rules'].append({'id':'block','subject':'pedidos','effect':'DENY'});self.assertEqual('DENY',self.eval()['decision'])
    def test_bad_rule_invalidates(self):self.p['rules'].append({'id':'bad'});self.assertEqual('INVALID_POLICY',self.eval()['reason'])
    def test_duplicate_rule(self):self.p['rules'].append(self.p['rules'][0]);self.assertEqual('INVALID_POLICY',self.eval()['reason'])
    def test_bad_completeness(self):self.p['complete']='true';self.assertEqual('INVALID_POLICY',self.eval()['reason'])
    def test_bad_schema(self):self.p['schema']='other';self.assertEqual('INDETERMINATE',self.eval()['decision'])


class AuthorizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.temp.cleanup)
        cls.root=Path(cls.temp.name);cls.reference=a.execute(cls.root/'capture');cls.raw=lab.dump(cls.reference).encode()
    def setUp(self):self.capture=deepcopy(self.__class__.reference)
    def row(self,id):return next(r for r in a.analyze(self.capture)['consumers'] if r['consumer']==id)
    def test_reference_counts(self):
        self.assertEqual(14,len(self.capture['spans']));self.assertEqual(6,len({s['trace_id'] for s in self.capture['spans']}))
    def test_allowed_can_fail_contract(self):
        r=self.row('pedidos');self.assertEqual('ALLOW',r['phases']['v2']['policy']['decision'])
        self.assertEqual('FAIL_OBSERVED_IN_LAB',r['phases']['v2']['regression'])
        self.assertEqual('OBSERVED',r['phases']['v1']['successful_use'])
    def test_denied_is_not_success(self):
        p=self.row('portal')['phases']['v1'];self.assertEqual('OBSERVED',p['attempt'])
        self.assertEqual('NOT_COMPLETED_IN_OBSERVED_ATTEMPT',p['successful_use'])
        self.assertEqual([403],[e['status'] for e in p['events']]);self.assertEqual('NOT_VERIFIED',p['regression'])
    def test_indeterminate_is_blocked_but_not_deny(self):
        p=self.row('exportador')['phases']['v2'];self.assertEqual('INDETERMINATE',p['policy']['decision'])
        self.assertEqual([503],[e['status'] for e in p['events']]);self.assertEqual('NOT_VERIFIED',p['regression'])
    def test_allowed_without_execution(self):
        p=self.row('conciliacao')['phases']['v1'];self.assertEqual('ALLOW',p['policy']['decision'])
        self.assertEqual('UNKNOWN',p['attempt']);self.assertEqual('UNKNOWN',p['successful_use'])
    def test_blocked_do_not_query_database(self):
        for r in a.analyze(self.capture)['consumers']:
            for p in r['phases'].values():
                for e in p['events']:
                    if e['enforcement']=='BLOCKED':self.assertEqual([],e['database_indices'])
                    else:self.assertEqual(1,len(e['database_indices']))
    def test_no_telemetry_no_did_it(self):
        self.capture['spans']=[];p=self.row('pedidos')['phases']['v1']
        self.assertEqual('ALLOW',p['policy']['decision']);self.assertEqual('UNKNOWN',p['successful_use'])
    def test_missing_snapshot_preserves_observed_decision(self):
        self.capture['phases']['v1']['policies']['pedidos']=None;p=self.row('pedidos')['phases']['v1']
        self.assertEqual('INDETERMINATE',p['policy']['decision']);self.assertEqual('OBSERVED',p['successful_use'])
        self.assertEqual('CONFLICT_OR_MISSING',p['events'][0]['policy_consistency'])
    def test_revocation_does_not_rewrite_history(self):
        p=self.capture['phases']['v2']['policies']['pedidos'];p['rules'][0]['effect']='DENY'
        r=self.row('pedidos');self.assertEqual('ALLOW',r['phases']['v1']['policy']['decision'])
        self.assertEqual('DENY',r['phases']['v2']['policy']['decision'])
        self.assertEqual('CONFLICT_OR_MISSING',r['phases']['v2']['events'][0]['policy_consistency'])
    def test_unmatched_parent_is_not_observed(self):
        for s in self.capture['spans']:
            if s['kind']=='SERVER':s['parent_span_id']='f'*16
        self.assertEqual('UNKNOWN',self.row('pedidos')['phases']['v1']['successful_use'])
    def test_wrong_identity_is_not_correlated(self):
        for s in self.capture['spans']:
            if s['kind']=='SERVER':s['attributes']['auth.subject']='other'
        self.assertEqual('UNKNOWN',self.row('pedidos')['phases']['v1']['attempt'])
    def test_unauthenticated_not_correlated(self):
        for s in self.capture['spans']:
            if s['kind']=='SERVER':s['attributes']['auth.authenticated']=False
        self.assertEqual('UNKNOWN',self.row('pedidos')['phases']['v1']['attempt'])
    def test_cross_environment_not_correlated(self):
        for s in self.capture['spans']:
            if s['kind']=='SERVER':s['attributes']['auth.environment']='production'
        self.assertEqual('UNKNOWN',self.row('pedidos')['phases']['v1']['attempt'])
    def test_cross_version_not_correlated(self):
        for s in self.capture['spans']:
            if s['kind']=='SERVER':s['attributes']['auth.phase']='other'
        self.assertEqual('UNKNOWN',self.row('pedidos')['phases']['v1']['attempt'])
    def test_duplicate_spans_rejected(self):
        self.capture['spans'].append(deepcopy(self.capture['spans'][0]))
        with self.assertRaises(ValueError):a.analyze(self.capture)
    def test_unknown_contract_stays_unknown(self):
        self.capture['consumers'][0]['required_fields']=None;self.assertEqual('INCONCLUSIVE',self.row('pedidos')['contract'])
    def test_credentials_not_in_capture(self):
        raw=self.raw.decode();self.assertNotIn('Bearer ',raw);self.assertNotIn('LAB-001',raw)
        self.assertNotIn('Authorization',raw)
    def test_unsafe_attribute_rejected(self):
        self.capture['spans'][0]['attributes']['authorization']='secret'
        with self.assertRaises(ValueError):a.analyze(self.capture)
    def test_no_overwrite(self):
        before=(self.root/'capture/run.json').read_bytes()
        with self.assertRaises(FileExistsError):a.execute(self.root/'capture')
        self.assertEqual(before,(self.root/'capture/run.json').read_bytes())
    def test_graph_references(self):
        b=adapt(self.raw);ids={x['id'] for x in b['assets']};eids={e['id'] for e in b['evidence']}
        self.assertEqual((10,9),(len(ids),len(b['relations'])))
        for r in b['relations']:
            self.assertIn(r['source'],ids);self.assertIn(r['target'],ids);self.assertLessEqual(set(r['evidence_ids']),eids)
    def test_actual_json_references_resolve(self):
        for e in adapt(self.raw)['evidence']:
            val=self.capture
            for part in e['reference'].split('#/')[1].split('/'):
                val=val[int(part)] if isinstance(val,list) else val[part]
    def test_capture_identity_isolated(self):
        b=adapt(self.raw);other=deepcopy(self.capture);other['consumers'][0]['name']='Outro nome'
        self.assertNotEqual(b['dataset_version'],adapt(lab.dump(other).encode())['dataset_version'])
    def test_adapter_does_not_promote_denial_to_runtime_use(self):
        b=adapt(self.raw);r=next(r for r in b['results'][0]['consumers'] if r['consumer']=='l5-portal')
        self.assertEqual('UNKNOWN',r['activity']);self.assertEqual('DENY',r['authorization'])
        self.assertFalse(any(e['claim']=='observed_use' for e in b['evidence']))
    def test_builder_preserves_sources(self):
        before={p.name:p.read_bytes() for p in PREVIEW.iterdir() if p.is_file()}
        with tempfile.TemporaryDirectory() as t:
            m=build(self.root/'capture/run.json',Path(t)/'view');self.assertEqual(10,m['assets'])
        self.assertEqual(before,{p.name:p.read_bytes() for p in PREVIEW.iterdir() if p.is_file()})
    @contextmanager
    def server(self,policies=None):
        creds=a.Credentials([s['id'] for s in a.CONSUMERS]);rec=lab.Recorder();p=TracerProvider(shutdown_on_exit=False)
        p.add_span_processor(SimpleSpanProcessor(rec));tr=p.get_tracer('auth.tests')
        if policies is None:
            policy=a.policy_fixture(datetime.now(timezone.utc));policies={s['id']:policy for s in a.CONSUMERS}
        try:
            with lab.serve(a.make_app('v1',self.root/'capture/lab.sqlite',tr,creds,policies)) as url:
                with httpx.Client(timeout=5,trust_env=False) as client:yield client,url,creds,rec
        finally:p.shutdown()
    def test_name_header_cannot_impersonate(self):
        with self.server() as (c,url,creds,rec):
            h=creds.header('portal');h['x-lab-consumer']='pedidos'
            self.assertEqual(403,c.get(url+'/customers/LAB-001',headers=h).status_code)
            self.assertFalse(any(s['attributes'].get('db.operation.name') for s in rec.records))
    def test_missing_credentials_401(self):
        with self.server() as (c,url,creds,rec):
            r=c.get(url+'/customers/LAB-001',headers={'x-lab-consumer':'pedidos'})
            self.assertEqual(401,r.status_code);self.assertFalse(any(s['attributes'].get('db.operation.name') for s in rec.records))
    def test_invalid_credentials_401(self):
        with self.server() as (c,url,creds,rec):
            self.assertEqual(401,c.get(url+'/customers/LAB-001',headers={'Authorization':'Bearer invalid'}).status_code)
    def test_policy_change_enforced_by_api(self):
        pol=a.policy_fixture(datetime.now(timezone.utc));pol['rules'][0]['effect']='DENY'
        with self.server({'pedidos':pol}) as (c,url,creds,rec):
            self.assertEqual(403,c.get(url+'/customers/LAB-001',headers=creds.header('pedidos')).status_code)
            self.assertFalse(any(s['attributes'].get('db.operation.name') for s in rec.records))
    def test_incomplete_allow_cannot_execute(self):
        pol=a.policy_fixture(datetime.now(timezone.utc));pol['complete']=False
        with self.server({'pedidos':pol}) as (c,url,creds,rec):
            self.assertEqual(503,c.get(url+'/customers/LAB-001',headers=creds.header('pedidos')).status_code)
            self.assertFalse(any(s['attributes'].get('db.operation.name') for s in rec.records))
    def test_ephemeral_token_not_exported(self):
        with self.server() as (c,url,creds,rec):
            h=creds.header('pedidos');self.assertEqual(200,c.get(url+'/customers/LAB-001',headers=h).status_code)
            self.assertNotIn(h['Authorization'].split()[1],lab.dump(rec.records))


if __name__=='__main__':unittest.main()

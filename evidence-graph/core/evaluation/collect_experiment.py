"""Collect baseline evidence and a separate behavioral reference through real HTTP.

Only transport/SDK helpers are reused. No call to lab.analyze or auth_policy.evaluate.
No private service, cloud credential, real business payload or production client is used.
"""
from __future__ import annotations
from collections.abc import Mapping
from contextlib import ExitStack
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
from pathlib import Path
import secrets
import sys
import time

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.trace import SpanKind
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'lab-runtime'))
from lab import serve, Recorder, CustomerV1, CustomerV2
from oracle_consumers import PROGRAMS, CASES, SCHEDULE, BASELINE_OPTIONS, DEPLOYED_ACCESS, task_outcome

ENV = 'loopback-l6'; RESOURCE = 'aurora:api:customers'; ACTION = 'customers:read'
ROUTE = '/customers/{customer_id}'
# Intentionally imperfect documentation. These declarations do NOT drive program behavior.
DECLARED = {'c01':['cliente_id'], 'c02':['status'], 'c03':['cliente_id'],
            'c04':None, 'c05':['status'], 'c06':None, 'c07':['status'],
            'c08':['cliente_id'], 'c09':['cliente_id'], 'c10':None,
            'c11':None, 'c12':['cliente_id']}


class TrackedResponse(Mapping):
    def __init__(self, payload):
        self.payload = payload; self.indexed = set(); self.optional = set()
    def __getitem__(self, key):
        self.indexed.add(key)
        return self.payload[key]
    def __iter__(self):
        return iter(self.payload)
    def __len__(self):
        return len(self.payload)
    def get(self, key, default=None):
        self.optional.add(key)
        return self.payload.get(key, default)


def collect() -> tuple[dict, dict, dict]:
    start = datetime.now(timezone.utc)
    credentials = {s:secrets.token_urlsafe(32) for s in (*PROGRAMS, 'reference-reader')}
    recorder = Recorder(); provider = TracerProvider(shutdown_on_exit=False)
    provider.add_span_processor(SimpleSpanProcessor(recorder))
    tracer = provider.get_tracer('evidentgraph.l6', '0.1')
    server_receipts = []; client_receipts = []
    def header(subject):
        return {'Authorization':'Bearer '+credentials[subject]}
    def resolve(value):
        if not value or not value.startswith('Bearer '): return None
        value = value[7:].encode()
        return next((s for s,t in credentials.items() if hmac.compare_digest(t.encode(), value)), None)
    def app_for(version):
        app = FastAPI(title='L6 reference endpoint', version=version, docs_url=None, redoc_url=None)
        @app.get(ROUTE, response_model=CustomerV1 if version=='v1' else CustomerV2)
        def get_customer(customer_id: str, request: Request):
            subject = resolve(request.headers.get('authorization'))
            # Independent enforcement fixture: no policy evaluator or consumer manifest.
            if subject == 'reference-reader': status = 200
            elif subject not in credentials: status = 401
            elif DEPLOYED_ACCESS[subject] is None: status = 503
            else: status = 200 if DEPLOYED_ACCESS[subject] else 403
            def response():
                if status != 200: return JSONResponse({'detail':'blocked in fixture'}, status_code=status)
                body = {'status':'ativo'}
                if version == 'v1': body['cliente_id'] = 'L6-001'
                return body
            if request.headers.get('x-l6-phase') == 'baseline':
                parent = TraceContextTextMapPropagator().extract(dict(request.headers))
                with tracer.start_as_current_span('GET customer baseline', context=parent, kind=SpanKind.SERVER) as span:
                    span.set_attributes({'eval.subject':subject or 'unresolved', 'eval.authenticated':subject is not None,
                        'eval.phase':'baseline','eval.version':version,'eval.environment':ENV,'eval.resource':RESOURCE,
                        'http.response.status_code':status})
                    server_receipts.append({'subject':subject, 'status':status, 'version':version})
                    return response()
            return response()
        return app
    evidence = None; truth = None; audit = None
    try:
        with ExitStack() as stack:
            urls = {v:stack.enter_context(serve(app_for(v))) for v in ('v1','v2')}
            http = stack.enter_context(httpx.Client(timeout=5, trust_env=False))
            producer = {}
            for v in ('v1','v2'):
                r = http.get(urls[v]+'/openapi.json'); r.raise_for_status(); producer[v] = r.json()
            baseline_start = time.time_ns()
            for subject in SCHEDULE:
                with tracer.start_as_current_span('baseline client', kind=SpanKind.CLIENT) as span:
                    span.set_attributes({'eval.subject':subject, 'eval.phase':'baseline','eval.version':'v1',
                                         'eval.environment':ENV,'eval.resource':RESOURCE})
                    headers = header(subject); headers['x-l6-phase'] = 'baseline'
                    TraceContextTextMapPropagator().inject(headers)
                    r = http.get(urls['v1']+'/customers/L6-001', headers=headers)
                    span.set_attribute('http.response.status_code', r.status_code)
                    client_receipts.append({'subject':subject, 'status':r.status_code})
                    if r.status_code == 200:
                        tracked = TrackedResponse(r.json())
                        # Outcome is deliberately not exported into prediction inputs.
                        task_outcome(subject, tracked, BASELINE_OPTIONS[subject])
                        span.set_attribute('eval.indexed_fields', tuple(sorted(tracked.indexed)))
                        span.set_attribute('eval.optional_fields', tuple(sorted(tracked.optional)))
            provider.force_flush()
            baseline_end = time.time_ns()
            at = datetime.now(timezone.utc).isoformat()
            spans = sorted(recorder.records, key=lambda x:x['start_ns'])
            before_oracle_count = len(spans)
            # Separate oracle probes: their responses/outcomes NEVER enter input telemetry.
            probes = {}
            for subject in PROGRAMS:
                r = http.get(urls['v1']+'/customers/L6-001', headers=header(subject))
                probes[subject] = {'http_status':r.status_code,
                    'answer':{200:'YES',403:'NO',503:'UNKNOWN'}[r.status_code]}
            payloads = {}
            for v in ('v1','v2'):
                r = http.get(urls[v]+'/customers/L6-001', headers=header('reference-reader'))
                r.raise_for_status(); payloads[v] = r.json()
            rows = {}
            behavior = {}
            for subject in PROGRAMS:
                behavior[subject] = [{v:task_outcome(subject, payloads[v], options) for v in ('v1','v2')}
                                     for options in CASES[subject]]
                pairs = behavior[subject]
                # A task already failing before the change would be an UNKNOWN label.
                breaks = 'UNKNOWN' if not all(p['v1']['completed'] for p in pairs) else (
                    'YES' if any(not p['v2']['completed'] for p in pairs) else 'NO')
                # Truth has complete access to the scheduled, observed baseline receipts.
                used = any(x['subject']==subject and x['status']==200 for x in client_receipts)
                received = any(x['subject']==subject and x['status']==200 for x in server_receipts)
                if used != received: raise RuntimeError('Incomplete observation in reference recorder')
                rows[subject] = {'breaks_when_response_available':breaks,
                    'used_in_baseline_window':'YES' if used else 'NO',
                    'can_access_endpoint':probes[subject]['answer']}
            if len(recorder.records) != before_oracle_count:
                raise RuntimeError('Oracle telemetry leaked into baseline')
            ctx = {'environment':ENV,'resource':RESOURCE,'action':ACTION,'version':'v1','at':at,
                   'window_start_ns':baseline_start,'window_end_ns':baseline_end}
            begin = (start-timedelta(minutes=1)).isoformat(); end = (start+timedelta(hours=1)).isoformat()
            configs = {s:dict(required_fields=fields,complete=True,environment=ENV,resource=RESOURCE,
                        version='v1',valid_from=begin,valid_until=end) for s,fields in DECLARED.items() if fields is not None}
            snapshot = {'schema':'evidentgraph-local-policy-1','revision':'l6-frozen',
                'environment':ENV,'resource':RESOURCE,'action':ACTION,'valid_from':begin,'valid_until':end,
                'complete':True,'rules':[{'id':'rule-'+s,'subject':s,'effect':'ALLOW' if value else 'DENY'}
                                       for s,value in DEPLOYED_ACCESS.items() if value is not None]}
            # Policy is an evidence representation; enforcement used the separate table above.
            policies = {s:snapshot if value is not None else None for s,value in DEPLOYED_ACCESS.items()}
            def properties(v):
                schema = producer[v]['components']['schemas']['CustomerV1' if v=='v1' else 'CustomerV2']
                return set(schema['properties'])
            evidence = {'schema':'l6-evidence-1','context':ctx,'subjects':list(PROGRAMS),
                'change':{'removed_fields':sorted(properties('v1')-properties('v2'))},
                'C':configs,'R':spans,'A':policies}
            truth = {'schema':'l6-reference-1','labels':rows,'functional_outcomes':behavior,
                'permission_probes':probes,'baseline_client_receipts':client_receipts,
                'baseline_server_receipts':server_receipts,
                'note':'Functional tasks get actual v1/v2 responses with a designated fixture reader; permission is a separate target.'}
            audit = {'started_at':start.isoformat(),'finished_at':datetime.now(timezone.utc).isoformat(),
                'transport':'HTTP loopback TCP','baseline_spans':len(spans),
                'baseline_traces':len({x['trace_id'] for x in spans}),
                'oracle_spans_in_input':0,'subjects':len(PROGRAMS),'scheduled_baseline_attempts':len(SCHEDULE),
                'probe_requests':len(probes)+2, 'producer_openapi':producer,
                'shared_fixture_warning':'Same author and controlled server; behavioral independence is not external validation.'}
    finally:
        provider.shutdown()
    return evidence, truth, audit

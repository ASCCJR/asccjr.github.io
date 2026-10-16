"""L5 authorization experiment: actual loopback HTTP, local decisions and OTel.

Fictitious business data. Ephemeral opaque credentials stay in memory only.
An identity registry and a bounded policy are lab controls, not production IAM.
"""
from __future__ import annotations
import argparse
from contextlib import closing
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
from pathlib import Path
import re
import secrets
import sqlite3
from typing import Any

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.trace import SpanKind
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
import lab
from auth_policy import ACTION, ENVIRONMENT, RESOURCE, SCHEMA as POLICY_SCHEMA, evaluate, instant

SCHEMA = 'evidentgraph-auth-capture-1'
CONSUMERS = [
    {'id': 'pedidos', 'name': 'Cliente de pedidos', 'owner': 'Comercial',
     'required_fields': ['cliente_id'], 'run': True},
    {'id': 'portal', 'name': 'Portal de consulta', 'owner': 'Atendimento',
     'required_fields': ['status'], 'run': True},
    {'id': 'exportador', 'name': 'Exportador financeiro', 'owner': 'Financeiro',
     'required_fields': ['cliente_id'], 'run': True},
    {'id': 'conciliacao', 'name': 'Rotina de conciliação', 'owner': 'Financeiro',
     'required_fields': ['status'], 'run': False},
]
ATTRIBUTES = {'auth.phase', 'auth.action', 'auth.resource', 'auth.environment',
              'auth.claimed_consumer', 'auth.subject', 'auth.authenticated',
              'auth.decision', 'auth.reason', 'auth.policy_hash', 'auth.check',
              'auth.missing_fields', 'http.route', 'http.request.method',
              'http.response.status_code', 'db.system.name', 'db.collection.name',
              'db.operation.name'}


def digest(value: Any) -> str:
    return hashlib.sha256(lab.dump(value).encode()).hexdigest()


def policy_fixture(now: datetime) -> dict:
    return {'schema': POLICY_SCHEMA, 'revision': 'local-policy-v1',
            'environment': ENVIRONMENT, 'resource': RESOURCE, 'action': ACTION,
            'valid_from': (now-timedelta(minutes=1)).isoformat(),
            'valid_until': (now+timedelta(hours=1)).isoformat(), 'complete': True,
            'rules': [{'id': 'allow-orders', 'subject': 'pedidos', 'effect': 'ALLOW'},
                      {'id': 'deny-portal', 'subject': 'portal', 'effect': 'DENY'},
                      {'id': 'allow-unused', 'subject': 'conciliacao', 'effect': 'ALLOW'}]}


class Credentials:
    """Opaque bearer tokens for loopback only; never serialize this object."""
    def __init__(self, subjects: list[str]):
        self._by_subject = {subject: secrets.token_urlsafe(32) for subject in subjects}

    def header(self, subject: str) -> dict[str, str]:
        return {'Authorization': 'Bearer ' + self._by_subject[subject]}

    def resolve(self, authorization: str | None) -> str | None:
        if not authorization:
            return None
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        candidate = parts[1].encode()
        found = None
        for subject, token in self._by_subject.items():
            if hmac.compare_digest(candidate, token.encode()):
                found = subject
        return found


def make_app(version: str, db: Path, tracer: Any, credentials: Credentials,
             policies: dict[str, Any]) -> FastAPI:
    if version not in {'v1', 'v2'}:
        raise ValueError('Unsupported API version')
    # Snapshot isolated from subsequent caller mutation. None means source unavailable.
    policies = deepcopy(policies)
    app = FastAPI(title='Aurora — controle de acesso local', version=version,
                  docs_url=None, redoc_url=None)

    @app.get(lab.ROUTE, response_model=lab.CustomerV1 if version == 'v1' else lab.CustomerV2)
    def customer(customer_id: str, request: Request):
        parent = TraceContextTextMapPropagator().extract(dict(request.headers))
        with tracer.start_as_current_span('authorized customer API', context=parent,
                                          kind=SpanKind.SERVER) as span:
            subject = credentials.resolve(request.headers.get('authorization'))
            policy = policies.get(subject)
            decision = evaluate(policy, subject, ACTION, RESOURCE, ENVIRONMENT,
                                datetime.now(timezone.utc).isoformat())
            status = 401 if subject is None else {'ALLOW': 200, 'DENY': 403,
                                                  'INDETERMINATE': 503}[decision['decision']]
            span.set_attributes({'auth.phase': version, 'auth.action': ACTION,
                'auth.resource': RESOURCE, 'auth.environment': ENVIRONMENT,
                'auth.subject': subject or 'unresolved', 'auth.authenticated': subject is not None,
                'auth.decision': decision['decision'], 'auth.reason': decision['reason'],
                'auth.policy_hash': digest(policy), 'http.route': lab.ROUTE,
                'http.request.method': 'GET', 'http.response.status_code': status})
            if status != 200:
                # Early return: neither SQL nor business payload construction is reached.
                headers = {'WWW-Authenticate': 'Bearer'} if status == 401 else None
                return JSONResponse({'detail': 'Acesso não concluído'}, status_code=status,
                                    headers=headers)
            with tracer.start_as_current_span('authorized SELECT customers', kind=SpanKind.CLIENT) as child:
                child.set_attributes({'auth.phase': version, 'auth.environment': ENVIRONMENT,
                    'db.system.name': 'sqlite', 'db.collection.name': 'customers',
                    'db.operation.name': 'SELECT'})
                with closing(sqlite3.connect(db)) as conn:
                    row = conn.execute('SELECT cliente_id,status FROM customers WHERE cliente_id=?',
                                       (customer_id,)).fetchone()
            if row is None:
                span.set_attribute('http.response.status_code', 404)
                return JSONResponse({'detail': 'Não encontrado'}, status_code=404)
            result = {'status': row[1]}
            if version == 'v1':
                result['cliente_id'] = row[0]
            return result
    return app


def consume(client: httpx.Client, url: str, spec: dict, phase: str,
            credentials: Credentials, tracer: Any) -> None:
    with tracer.start_as_current_span('access attempt '+spec['id'], kind=SpanKind.CLIENT) as span:
        span.set_attributes({'auth.claimed_consumer': spec['id'], 'auth.phase': phase,
            'auth.environment': ENVIRONMENT, 'auth.action': ACTION, 'auth.resource': RESOURCE,
            'http.route': lab.ROUTE, 'http.request.method': 'GET'})
        headers = credentials.header(spec['id'])
        TraceContextTextMapPropagator().inject(headers)
        response = client.get(url+'/customers/LAB-001', headers=headers)
        span.set_attribute('http.response.status_code', response.status_code)
        if response.status_code == 200:
            missing = sorted(set(spec['required_fields'])-set(response.json()))
            span.set_attribute('auth.check', 'FAIL' if missing else 'PASS')
            span.set_attribute('auth.missing_fields', tuple(missing))
        else:
            span.set_attribute('auth.check', 'NOT_RUN')


def validate(run: dict) -> None:
    if (run.get('schema') != SCHEMA or run.get('environment') != ENVIRONMENT
            or run.get('transport') != 'HTTP over loopback TCP'):
        raise ValueError('Unsupported authorization capture')
    lo, hi = instant(run['started_at']), instant(run['finished_at'])
    if hi < lo or set(run['phases']) != {'v1', 'v2'} or set(run['openapi']) != {'v1', 'v2'}:
        raise ValueError('Invalid capture phases')
    specs = run['consumers']
    if {s['id'] for s in specs} != {s['id'] for s in CONSUMERS} or len(specs) != 4:
        raise ValueError('Expected distinct known laboratory consumers')
    for spec in specs:
        req = spec.get('required_fields')
        if req is not None and (not isinstance(req, list) or any(not isinstance(f,str) for f in req)):
            raise ValueError('Invalid requirements')
    for phase in run['phases'].values():
        if (not lo <= instant(phase['at']) <= instant(phase['finished_at']) <= hi
                or not isinstance(phase['policies'], dict)):
            raise ValueError('Invalid phase context')
    if not isinstance(run['spans'], list) or len(run['spans']) > 4096:
        raise ValueError('Invalid spans')
    seen = set()
    for span in run['spans']:
        for key, length in [('span_id',16), ('trace_id',32)]:
            if not re.fullmatch('[0-9a-f]{'+str(length)+'}',span[key]) or int(span[key],16)==0:
                raise ValueError('Invalid trace identifier')
        parent = span.get('parent_span_id')
        if parent is not None and not re.fullmatch('[0-9a-f]{16}',parent):
            raise ValueError('Invalid parent')
        key = (span['trace_id'],span['span_id'])
        if key in seen:
            raise ValueError('Duplicate span')
        seen.add(key)
        if span['kind'] not in {'CLIENT','SERVER','INTERNAL'}:
            raise ValueError('Invalid span kind')
        a,b = span['start_ns'],span['end_ns']
        if (type(a) is not int or type(b) is not int or not
                lo.timestamp() <= a/1e9 <= b/1e9 <= hi.timestamp()):
            raise ValueError('Invalid span time')
        if not isinstance(span['attributes'],dict) or set(span['attributes'])-ATTRIBUTES:
            raise ValueError('Unexpected attributes; do not import credentials or payloads')


def child_of(child: dict, parent: dict) -> bool:
    return (child['trace_id']==parent['trace_id'] and child['parent_span_id']==parent['span_id']
            and parent['start_ns']<=child['start_ns']<=child['end_ns']<=parent['end_ns']
            and child['attributes'].get('auth.phase')==parent['attributes'].get('auth.phase')
            and child['attributes'].get('auth.environment')==ENVIRONMENT)


def attempts(run: dict, subject: str, phase: str) -> list[dict]:
    """Caller label alone is not identity proof. Require a matching verified server span."""
    events = []
    for ci,c in enumerate(run['spans']):
        a = c['attributes']
        ctx = run['phases'][phase]
        in_phase = (instant(ctx['at']).timestamp() <= c['start_ns']/1e9
                    <= c['end_ns']/1e9 <= instant(ctx['finished_at']).timestamp())
        if (not in_phase or c['kind']!='CLIENT' or a.get('auth.claimed_consumer')!=subject
                or a.get('auth.phase')!=phase or a.get('auth.environment')!=ENVIRONMENT
                or a.get('http.route')!=lab.ROUTE or a.get('http.request.method')!='GET'
                or a.get('auth.action')!=ACTION or a.get('auth.resource')!=RESOURCE):
            continue
        for si,s in enumerate(run['spans']):
            b = s['attributes']
            if (s['kind']!='SERVER' or not child_of(s,c)
                    or b.get('auth.authenticated') is not True or b.get('auth.subject')!=subject
                    or b.get('http.route')!=lab.ROUTE or b.get('http.request.method')!='GET'
                    or b.get('auth.resource')!=RESOURCE or b.get('auth.action')!=ACTION
                    or b.get('http.response.status_code')!=a.get('http.response.status_code')):
                continue
            status = b.get('http.response.status_code')
            decision = b.get('auth.decision')
            policy = run['phases'][phase]['policies'].get(subject)
            computed = evaluate(policy,subject,ACTION,RESOURCE,ENVIRONMENT,
                                datetime.fromtimestamp(s['start_ns']/1e9,timezone.utc).isoformat())
            match = (decision==computed['decision'] and b.get('auth.reason')==computed['reason']
                     and b.get('auth.policy_hash')==digest(policy))
            database = [i for i,d in enumerate(run['spans']) if d['kind']=='CLIENT'
                        and child_of(d,s) and d['attributes'].get('db.system.name')=='sqlite'
                        and d['attributes'].get('db.collection.name')=='customers'
                        and d['attributes'].get('db.operation.name')=='SELECT']
            success = status==200 and decision=='ALLOW'
            events.append({'trace_id': c['trace_id'], 'span_indices':[ci,si],
                'database_indices':database, 'status':status, 'decision':decision,
                'policy_consistency':'CONSISTENT' if match else 'CONFLICT_OR_MISSING',
                'successful':success, 'check':a.get('auth.check') if success else 'NOT_RUN',
                'enforcement':'COMPLETED' if success else 'BLOCKED' if
                    ((decision=='DENY' and status==403) or
                     (decision=='INDETERMINATE' and status==503)) else 'INCONSISTENT'})
    return events


def analyze(run: dict) -> dict:
    validate(run)
    removed = sorted(lab.response_fields(run['openapi']['v1'])-lab.response_fields(run['openapi']['v2']))
    rows=[]
    for spec in run['consumers']:
        req=spec.get('required_fields')
        missing=sorted(set(req or [])&set(removed))
        contract='INCONCLUSIVE' if req is None else 'INCOMPATIBILITY' if missing else 'NO_INCOMPATIBILITY'
        phases={}
        for v,ctx in run['phases'].items():
            ev=attempts(run,spec['id'],v)
            decision=evaluate(ctx['policies'].get(spec['id']),spec['id'],ACTION,RESOURCE,ENVIRONMENT,ctx['at'])
            successful=[e for e in ev if e['successful']]
            check='FAIL_OBSERVED_IN_LAB' if any(e['check']=='FAIL' for e in successful) else (
                'PASS_IN_EXECUTED_CHECK' if successful and all(e['check']=='PASS' for e in successful)
                else 'NOT_VERIFIED')
            phases[v]={'policy':decision, 'attempt':'OBSERVED' if ev else 'UNKNOWN',
                'successful_use':'OBSERVED' if successful else 'NOT_COMPLETED_IN_OBSERVED_ATTEMPT' if ev else 'UNKNOWN',
                'regression':check,'events':ev}
        rows.append({'consumer':spec['id'],'name':spec['name'],'owner':spec['owner'],
                     'contract':contract,'removed_required_fields':missing,'phases':phases})
    return {'schema':SCHEMA,'environment':ENVIRONMENT,'removed_fields':removed,'consumers':rows,
            'authorization_scope':{'action':ACTION,'resource':RESOURCE,'environment':ENVIRONMENT},
            'business_data':'synthetic','telemetry':'real_local_execution','scope_complete':False}


def report(run: dict) -> str:
    result=analyze(run)
    label={'ALLOW':'Permitido','DENY':'Negado','INDETERMINATE':'Indeterminado',
           'OBSERVED':'Observado','UNKNOWN':'Não confirmado',
           'NOT_COMPLETED_IN_OBSERVED_ATTEMPT':'Não concluído na tentativa',
           'FAIL_OBSERVED_IN_LAB':'Falhou no teste','PASS_IN_EXECUTED_CHECK':'Passou no teste',
           'NOT_VERIFIED':'Não verificado','INCOMPATIBILITY':'Incompatibilidade declarada',
           'NO_INCOMPATIBILITY':'Não identificada no contrato','INCONCLUSIVE':'Contrato insuficiente'}
    lines=['# EvidentGraph — autorização local L5','',
        '**Execução real em loopback; dados fictícios; captura histórica.**','',
        '| Consumidor | Política v1 | Tentativa v1 | Acesso concluído v1 | Contrato | Teste v2 |',
        '|---|---|---|---|---|---|']
    for r in result['consumers']:
        p=r['phases'];lines.append('| '+' | '.join([r['name'],label[p['v1']['policy']['decision']],
            label[p['v1']['attempt']],label[p['v1']['successful_use']],label[r['contract']],
            label[p['v2']['regression']]])+' |')
    lines += ['', '## Interpretação','',
        '- Política, tentativa, acesso concluído e contrato são dimensões separadas.',
        '- O controle local só executa a consulta após ALLOW. DENY e INDETERMINATE bloqueiam.',
        '- Ausência de tentativa não transforma uma permissão em acesso observado.',
        '- Um teste bloqueado não prova que o consumidor é compatível com a nova API.',
        '', '## Limites','',
        'Política local exata para identidade/ação/recurso, não IAM corporativo ou autorização por coluna. '
        'Token opaco efêmero em memória, sem OAuth, JWT ou gestão de credenciais de produção. '
        'Cabeçalho de nome não autentica. A interface não aplica controles; apenas lê a captura. '
        'PASS cobre só a verificação executada. Ausência de span não prova ausência de uso. '
        'Requisitos compartilhados pelos clientes e comparador: não é benchmark independente.', '',
        'Período: '+run['started_at']+' a '+run['finished_at']+'.',
        'SHA-256 do run.json: `'+digest(run)+'`.']
    return '\n'.join(lines)+'\n'


def execute(out: Path) -> dict:
    from capture_history import permitted_output
    out = permitted_output(out)
    out.mkdir(parents=True, exist_ok=False)
    db=out/'lab.sqlite'
    with closing(sqlite3.connect(db)) as conn:
        conn.execute('CREATE TABLE customers(cliente_id TEXT PRIMARY KEY,status TEXT NOT NULL)')
        conn.execute('INSERT INTO customers VALUES (?,?)',('LAB-001','ativo'));conn.commit()
    start=datetime.now(timezone.utc)
    policy=policy_fixture(start)
    # Missing policy source for Exportador is intentional. Other subjects have a complete snapshot.
    policies={s['id']:deepcopy(policy) if s['id']!='exportador' else None for s in CONSUMERS}
    credentials=Credentials([s['id'] for s in CONSUMERS])
    recorder=lab.Recorder();provider=TracerProvider(shutdown_on_exit=False)
    provider.add_span_processor(SimpleSpanProcessor(recorder));tracer=provider.get_tracer('evidentgraph.auth','0.1')
    run={'schema':SCHEMA,'environment':ENVIRONMENT,'transport':'HTTP over loopback TCP',
         'started_at':start.isoformat(),'consumers':deepcopy(CONSUMERS),'phases':{},'openapi':{},'spans':[]}
    try:
        for v in ['v1','v2']:
            run['phases'][v]={'at':datetime.now(timezone.utc).isoformat(),'policies':deepcopy(policies)}
            with lab.serve(make_app(v,db,tracer,credentials,policies)) as url, httpx.Client(timeout=5,trust_env=False) as client:
                response=client.get(url+'/openapi.json');response.raise_for_status();run['openapi'][v]=response.json()
                for spec in CONSUMERS:
                    if spec['run']:
                        consume(client,url,spec,v,credentials,tracer)
            run['phases'][v]['finished_at'] = datetime.now(timezone.utc).isoformat()
        provider.force_flush()
    finally:
        provider.shutdown()
    run['spans']=sorted(recorder.records,key=lambda s:s['start_ns'])
    run['finished_at']=datetime.now(timezone.utc).isoformat()
    result=analyze(run)
    files={'run.json':lab.dump(run),'analysis.json':lab.dump(result),'report.md':report(run)}
    for name,text in files.items():
        (out/name).write_text(text,encoding='utf-8')
    manifest={'schema':SCHEMA,'files_sha256':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in files.items()},
              'spans':len(run['spans']),'traces':len({s['trace_id'] for s in run['spans']}),
              'secret_values_exported':False}
    (out/'manifest.json').write_text(lab.dump(manifest),encoding='utf-8')
    return run


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    try:
        capture=execute(args.out)
        print(report(capture))
    except Exception as error:
        parser.exit(1,'Execução não concluída: '+str(error)+'\nSem fallback ou publicação.\n')

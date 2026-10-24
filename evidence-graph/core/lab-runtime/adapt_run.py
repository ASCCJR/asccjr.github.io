"""Adapt one L1 capture to the M3 view contract, without joining the Aurora dataset."""
from __future__ import annotations
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import lab

VERSION = 'lab-view-0.1'
NAMES = {'pedidos': 'Cliente de pedidos', 'portal': 'Portal de consulta',
         'exportador': 'Exportador financeiro'}
DOMAINS = {'Comercial': 'comercial', 'Atendimento': 'atendimento', 'Financeiro': 'financeiro'}
SAFE_ATTRIBUTES = {'lab.consumer', 'lab.api_version', 'lab.check', 'lab.missing_fields',
                   'lab.received_fields', 'lab.response_fields', 'http.request.method',
                   'http.response.status_code', 'http.route', 'db.system.name',
                   'db.collection.name', 'db.operation.name'}

def moment(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Capture times must include a timezone')
    return parsed


def validate_capture(run: dict[str, Any]) -> None:
    """Bounded schema validation, not authenticity verification of third-party telemetry."""
    if run.get('schema') != lab.SCHEMA or run.get('transport') != 'HTTP over loopback TCP':
        raise ValueError('Only the L1 loopback capture is supported')
    start, end = moment(run['started_at']), moment(run['finished_at'])
    if end < start:
        raise ValueError('Invalid capture interval')
    if set(run['openapi']) != {'v1', 'v2'}:
        raise ValueError('Both captured OpenAPI versions are required')
    consumers = run['consumers']
    if len(consumers) != 3 or {c['id'] for c in consumers} != set(NAMES):
        raise ValueError('Expected the three distinct L1 consumers')
    if any(c['owner'] not in DOMAINS for c in consumers):
        raise ValueError('Unknown declared lab owner')
    if not isinstance(run['spans'], list) or len(run['spans']) > 4096:
        raise ValueError('Invalid or oversized span collection')
    for span in run['spans']:
        for key, length in [('trace_id', 32), ('span_id', 16)]:
            if not re.fullmatch('[0-9a-f]{'+str(length)+'}', span[key]):
                raise ValueError('Invalid trace/span ID')
        parent = span.get('parent_span_id')
        if parent is not None and not re.fullmatch('[0-9a-f]{16}', parent):
            raise ValueError('Invalid parent span ID')
        if span['kind'] not in {'CLIENT', 'SERVER', 'INTERNAL'}:
            raise ValueError('Unsupported span kind')
        lo, hi = span['start_ns'], span['end_ns']
        if type(lo) is not int or type(hi) is not int or hi < lo:
            raise ValueError('Invalid span interval')
        if lo / 1e9 < start.timestamp() or hi / 1e9 > end.timestamp():
            raise ValueError('Span lies outside the capture interval')
        if not isinstance(span['attributes'], dict):
            raise ValueError('Invalid attributes')


def children(records: list[dict], parent: dict) -> list[dict]:
    return [s for s in records if s['parent_span_id'] == parent['span_id']
            and s['trace_id'] == parent['trace_id']
            and s['attributes'].get('lab.api_version') == parent['attributes'].get('lab.api_version')
            and parent['start_ns'] <= s['start_ns'] <= s['end_ns'] <= parent['end_ns']]


def adapt(raw: bytes) -> dict[str, Any]:
    if len(raw) > 5_000_000:
        raise ValueError('Capture exceeds 5 MB')
    run = json.loads(raw)
    validate_capture(run)
    analysis = lab.analyze(run)  # Recompute; never trust a supplied analysis.json.
    if len(analysis['removed_fields']) != 1:
        raise ValueError('This adapter supports exactly one removed field')
    sha = hashlib.sha256(raw).hexdigest()
    version = VERSION + '-' + sha
    clock, api, table = run['finished_at'], 'l1-api-clientes', 'l1-tbl-customers'
    teams = [{'id': 'l1-team-'+v, 'domain': v, 'name': 'Equipe '+k} for k, v in DOMAINS.items()]
    teams.append({'id': 'l1-team-plataforma', 'domain': 'plataforma', 'name': 'Equipe Plataforma'})
    assets, evidence, relations, rows, database_refs = [], [], [], [], []
    def asset(id: str, name: str, kind: str, domain: str, ver: str = '1.0') -> dict:
        return {'id': id, 'name': name, 'kind': kind, 'domain': domain,
                'owner': 'l1-team-'+domain, 'environment': 'loopback-lab', 'version': ver,
                'processes': [], 'criticality': 'not_assessed', 'metadata_origin': 'adapter_mapping'}
    assets.append(asset(api, 'API de clientes', 'api', 'plataforma', 'v1 / v2'))
    def ev(id: str, family: str, subject: str, target: str, ref: str,
           claim: str, details: dict, ver: str = 'v1 / v2') -> str:
        evidence.append({'id': id, 'family': family, 'source': 'l1-'+family,
                         'origin_id': sha+':'+ref, 'reference': 'run.json'+ref,
                         'subject': subject, 'target': target, 'subject_version': ver,
                         'target_version': ver, 'environment': 'loopback-lab',
                         'collected_at': clock, 'valid_from': None,
                         'valid_until': None, 'claim': claim, 'details': details})
        return id
    api_refs = [ev('l1-openapi-'+v, 'code', api, api, '#/openapi/'+v,
                   'api_contract', {'response_fields': sorted(lab.response_fields(doc)),
                                    'collection': 'OpenAPI obtido por HTTP no laboratório'}, v)
                for v, doc in run['openapi'].items()]
    indices = {s['span_id']: i for i, s in enumerate(run['spans'])}
    used_ids: set[str] = set()
    def span_ref(span: dict, subject: str, target: str) -> str:
        id = 'l1-span-'+span['span_id']
        if id not in used_ids:
            used_ids.add(id)
            details = {k: v for k, v in span['attributes'].items() if k in SAFE_ATTRIBUTES}
            details.update(trace_id=span['trace_id'], span_id=span['span_id'],
                           parent_span_id=span['parent_span_id'], kind=span['kind'],
                           at=datetime.fromtimestamp(span['start_ns']/1e9, timezone.utc).isoformat())
            ev(id, 'runtime', subject, target, '#/spans/'+str(indices[span['span_id']]),
               'observed_use', details, span['attributes']['lab.api_version'])
        return id
    for index, source in enumerate(analysis['consumers']):
        id = 'l1-'+source['consumer']
        domain = DOMAINS[source['owner']]
        assets.append(asset(id, NAMES[source['consumer']], 'application', domain))
        # No invented process mapping: L1 did not collect business processes.
        declaration = ev('l1-contract-'+source['consumer'], 'config', id, api,
                         '#/consumers/'+str(index), 'consumer_fields',
                         {'required_fields': run['consumers'][index].get('required_fields'),
                          'origin': 'Declaração do cliente de teste, não descoberta no código'})
        refs, phases = [declaration, *api_refs], {}
        for v in ['v1', 'v2']:
            requests = lab.correlated_requests(run['spans'], source['consumer'], v)
            phases[v] = {'usage': 'OBSERVED' if requests else 'UNKNOWN',
                         'checks': [s['attributes'].get('lab.check', 'NOT_VERIFIED') for s in requests],
                         'trace_ids': sorted({s['trace_id'] for s in requests})}
            for client in requests:
                refs.append(span_ref(client, id, api))
                for server in children(run['spans'], client):
                    if (server['kind'] != 'SERVER' or server['attributes'].get('http.route') != lab.ROUTE
                            or server['attributes'].get('http.response.status_code') != 200):
                        continue
                    refs.append(span_ref(server, id, api))
                    for db in children(run['spans'], server):
                        a = db['attributes']
                        if (db['kind'] == 'CLIENT' and a.get('db.system.name') == 'sqlite'
                                and a.get('db.collection.name') == 'customers'
                                and a.get('db.operation.name') == 'SELECT'):
                            database_refs.append(span_ref(db, api, table))
        rid = 'l1-calls-'+source['consumer']
        relations.append({'id': rid, 'source': id, 'target': api, 'kind': 'CALLS',
                          'evidence_ids': list(dict.fromkeys(refs))})
        impact = {'INCOMPATIBILITY': 'INCOMPATIBILITY', 'INCONCLUSIVE': 'INCONCLUSIVE',
                  'NO_INCOMPATIBILITY_IN_DECLARED_CONTRACT': 'NO_INCOMPATIBILITY'}[source['contract']]
        rows.append({'consumer': id, 'name': NAMES[source['consumer']], 'owner': 'l1-team-'+domain,
                     'processes': [], 'criticality': 'not_assessed', 'impact': impact,
                     'activity': source['usage_before_change'], 'paths': [[rid]],
                     'evidence_ids': list(dict.fromkeys(refs)), 'origin_ids': [],
                     'authorization': 'NOT_EVALUATED', 'field_access': 'NOT_EVALUATED',
                     'contract_conflict': False, 'next_step': source['next_step'],
                     'limitations': ['Processos de negócio e criticidade não foram coletados.',
                                     'Atividade refere-se à versão v1; regressão é um resultado separado.',
                                     'Resultado válido somente para esta captura de laboratório.'],
                     'lab_regression': source['regression_after_change'], 'lab_phases': phases})
    for row in rows:
        row['origin_ids'] = sorted({e['origin_id'] for e in evidence if e['id'] in row['evidence_ids']})
    if database_refs:
        assets.append(asset(table, 'customers · SQLite', 'table', 'plataforma'))
        relations.append({'id': 'l1-reads-customers', 'source': api, 'target': table,
                          'kind': 'READS', 'evidence_ids': sorted(set(database_refs))})
    change = {'id': 'LAB-001', 'target': api, 'operation': 'remove_field',
              'field': analysis['removed_fields'][0], 'before_version': 'v1', 'after_version': 'v2',
              'environment': 'loopback-lab', 'window_start': run['started_at'], 'window_end': clock}
    result = {'change': change, 'consumers': rows, 'truncated': False, 'scope_complete': False,
              'dataset_version': version, 'clock': clock,
              'scope_note': 'Captura local delimitada. Uso anterior (v1), contrato e teste posterior (v2) são avaliações distintas.',
              'counts': {'consumers': len(rows), 'impact': dict(Counter(r['impact'] for r in rows)),
                         'activity': dict(Counter(r['activity'] for r in rows))}}
    limitations = [x for x in analysis['limitations'] if not x.startswith('Sem IAM, PostgreSQL')]
    limitations += ['Sem IAM, MCP, agentes de IA ou integração corporativa.',
                    'Hash identifica o arquivo; não autentica telemetria enviada por terceiros.',
                    'SQLite foi lido, mas isso não prova acesso ao campo pelo consumidor.',
                    'Captura histórica, não monitoramento em tempo real.']
    return {'synthetic': False, 'dataset_version': version, 'clock': clock,
            'assets': assets, 'teams': teams, 'processes': [],
            'domains': [{'id': x['domain'], 'name': x['name'].removeprefix('Equipe ')} for x in teams],
            'sources': [{'id': 'l1-'+f, 'family': f, 'origin': 'captured' if f!='config' else 'declared_fixture'} for f in ['code','config','runtime']], 'relations': relations, 'evidence': evidence, 'coverage': [],
            'results': [result], 'full_catalog_counts': {'assets': len(assets), 'relations': len(relations)},
            'provenance': {'kind': 'l1_capture', 'adapter_version': VERSION, 'source_sha256': sha,
                           'business_data': 'synthetic', 'telemetry': 'real_local_execution',
                           'started_at': run['started_at'], 'finished_at': clock,
                           'spans_in_capture': len(run['spans']),
                           'spans_used': len(used_ids), 'limitations': limitations}}

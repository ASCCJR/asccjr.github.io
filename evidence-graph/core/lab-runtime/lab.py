"""Local evidence experiment: synthetic business data, real HTTP/SQLite/OTel execution.

Python 3.10+. No credentials, external endpoints, UI changes or production use.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager, closing
import hashlib
import json
from pathlib import Path
import socket
import sqlite3
import threading
import time
from typing import Any, Iterator
from datetime import datetime, timezone

import httpx
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import uvicorn
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.trace import SpanKind, Status, StatusCode
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

SCHEMA = 'evidentgraph-lab-0.1'
ROUTE = '/customers/{customer_id}'
CONSUMERS = [
    {'id': 'pedidos', 'owner': 'Comercial', 'required_fields': ['cliente_id'], 'run': True},
    {'id': 'portal', 'owner': 'Atendimento', 'required_fields': ['status'], 'run': True},
    {'id': 'exportador', 'owner': 'Financeiro', 'required_fields': ['cliente_id'], 'run': False},
]

def dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n'

class Recorder(SpanExporter):
    """Collect SDK spans locally; do not publish to an OTLP endpoint."""
    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []
        self.lock = threading.Lock()

    def export(self, spans: Any) -> SpanExportResult:
        with self.lock:
            for s in spans:
                self.records.append({
                    'trace_id': format(s.context.trace_id, '032x'),
                    'span_id': format(s.context.span_id, '016x'),
                    'parent_span_id': format(s.parent.span_id, '016x') if s.parent else None,
                    'name': s.name, 'kind': s.kind.name,
                    'start_ns': s.start_time, 'end_ns': s.end_time,
                    'status': s.status.status_code.name,
                    'attributes': dict(s.attributes or {}),
                })
        return SpanExportResult.SUCCESS

    def shutdown(self) -> None:
        pass

class CustomerV1(BaseModel):
    cliente_id: str
    status: str

class CustomerV2(BaseModel):
    status: str


def make_app(version: str, db: Path, tracer: Any) -> FastAPI:
    if version not in {'v1', 'v2'}:
        raise ValueError('Only the v1/v2 laboratory contracts are supported')
    app = FastAPI(title='Aurora Customer API — laboratório', version=version,
                  docs_url=None, redoc_url=None)

    @app.get(ROUTE, response_model=CustomerV1 if version == 'v1' else CustomerV2)
    def get_customer(customer_id: str, request: Request) -> dict[str, str]:
        context = TraceContextTextMapPropagator().extract(dict(request.headers))
        with tracer.start_as_current_span('GET ' + ROUTE, context=context,
                                          kind=SpanKind.SERVER) as span:
            span.set_attributes({'http.request.method': 'GET', 'http.route': ROUTE,
                                 'lab.api_version': version,
                                 'lab.caller_label': request.headers.get('x-lab-consumer', 'unknown')})
            with tracer.start_as_current_span('SELECT customers', kind=SpanKind.CLIENT) as dbspan:
                dbspan.set_attributes({'db.system.name': 'sqlite', 'db.collection.name': 'customers',
                                       'db.operation.name': 'SELECT', 'lab.api_version': version})
                with closing(sqlite3.connect(db)) as conn:
                    row = conn.execute('SELECT cliente_id, status FROM customers WHERE cliente_id = ?',
                                       (customer_id,)).fetchone()
            if row is None:
                span.set_attribute('http.response.status_code', 404)
                raise HTTPException(status_code=404, detail='Cliente não encontrado')
            payload = {'status': row[1]}
            if version == 'v1':
                payload['cliente_id'] = row[0]
            # Names only: do not record customer values or response bodies in telemetry.
            span.set_attribute('lab.response_fields', tuple(sorted(payload)))
            span.set_attribute('http.response.status_code', 200)
            return payload
    return app


@contextmanager
def serve(app: FastAPI) -> Iterator[str]:
    """Real loopback TCP, ephemeral port, bounded start/stop; no public binding."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', 0))
    sock.listen(128)
    port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, host='127.0.0.1', port=port,
                            access_log=False, log_level='error', lifespan='off', ws='none'))
    thread = threading.Thread(target=server.run, kwargs={'sockets': [sock]}, daemon=True)
    thread.start()
    try:
        deadline = time.monotonic() + 5
        while not server.started:
            if not thread.is_alive() or time.monotonic() > deadline:
                raise RuntimeError('Local API did not start; no mock fallback was used')
            time.sleep(0.01)
        yield f'http://127.0.0.1:{port}'
    finally:
        server.should_exit = True
        thread.join(5)
        sock.close()
        if thread.is_alive():
            raise RuntimeError('Local server did not stop within the expected time')


def consume(client: httpx.Client, base: str, spec: dict[str, Any], version: str,
            tracer: Any) -> None:
    with tracer.start_as_current_span('GET customer — ' + spec['id'], kind=SpanKind.CLIENT) as span:
        span.set_attributes({'lab.consumer': spec['id'], 'lab.api_version': version,
                             'http.request.method': 'GET', 'http.route': ROUTE})
        headers = {'x-lab-consumer': spec['id']}
        TraceContextTextMapPropagator().inject(headers)
        response = client.get(base + '/customers/LAB-001', headers=headers)
        span.set_attribute('http.response.status_code', response.status_code)
        response.raise_for_status()
        fields = sorted(response.json().keys())
        missing = sorted(set(spec['required_fields']) - set(fields))
        span.set_attribute('lab.received_fields', tuple(fields))
        span.set_attribute('lab.missing_fields', tuple(missing))
        span.set_attribute('lab.check', 'FAIL' if missing else 'PASS')
        if missing:
            span.set_status(Status(StatusCode.ERROR, 'Declared consumer field missing'))


def response_fields(document: dict[str, Any]) -> set[str]:
    """Only local OpenAPI $ref and object schemas for this GET/200 lab endpoint."""
    schema = document['paths'][ROUTE]['get']['responses']['200']['content']['application/json']['schema']
    seen: set[str] = set()
    while '$ref' in schema:
        ref = schema['$ref']
        if not ref.startswith('#/') or ref in seen:
            raise ValueError('Unsupported or cyclic OpenAPI reference')
        seen.add(ref)
        node: Any = document
        for part in ref[2:].split('/'):
            node = node[part.replace('~1', '/').replace('~0', '~')]
        schema = node
    if schema.get('type') != 'object' or 'properties' not in schema:
        raise ValueError('Expected a bounded object response schema')
    return set(schema['properties'])


def correlated_requests(records: list[dict[str, Any]], consumer: str, version: str) -> list[dict[str, Any]]:
    """Require CLIENT -> SERVER parenting, common trace, same API version and route."""
    valid = []
    for client in records:
        a = client['attributes']
        if client['kind'] != 'CLIENT' or a.get('lab.consumer') != consumer:
            continue
        if a.get('lab.api_version') != version or a.get('http.route') != ROUTE:
            continue
        servers = [s for s in records if s['kind'] == 'SERVER'
                   and s['trace_id'] == client['trace_id']
                   and s['parent_span_id'] == client['span_id']
                   and s['attributes'].get('http.route') == ROUTE
                   and s['attributes'].get('lab.api_version') == version
                   and s['attributes'].get('http.response.status_code') == 200]
        if (a.get('http.response.status_code') == 200
                and any(client['start_ns'] <= s['start_ns'] <= s['end_ns'] <= client['end_ns']
                        for s in servers)):
            valid.append(client)
    return valid


def analyze(run: dict[str, Any]) -> dict[str, Any]:
    if run.get('schema') != SCHEMA:
        raise ValueError('Unsupported laboratory record schema')
    spans = run['spans']
    ids = [s['span_id'] for s in spans]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicated span IDs; do not count replay as independent evidence')
    removed = sorted(response_fields(run['openapi']['v1']) - response_fields(run['openapi']['v2']))
    rows = []
    for spec in run['consumers']:
        required = spec.get('required_fields')
        if required is not None and (not isinstance(required, list)
                                     or any(not isinstance(x, str) for x in required)):
            raise ValueError('required_fields must be a list of strings or unknown')
        missing = sorted(set(required or []) & set(removed))
        contract = ('INCONCLUSIVE' if required is None else
                    'INCOMPATIBILITY' if missing else 'NO_INCOMPATIBILITY_IN_DECLARED_CONTRACT')
        before = correlated_requests(spans, spec['id'], 'v1')
        after = correlated_requests(spans, spec['id'], 'v2')
        if any(s['attributes'].get('lab.check') == 'FAIL' for s in after):
            regression = 'FAIL_OBSERVED_IN_LAB'
        elif after and all(s['attributes'].get('lab.check') == 'PASS' for s in after):
            regression = 'PASS_IN_EXECUTED_CHECK'
        else:
            regression = 'NOT_VERIFIED'
        rows.append({'consumer': spec['id'], 'owner': spec['owner'], 'contract': contract,
                     'removed_required_fields': missing,
                     'usage_before_change': 'OBSERVED' if before else 'UNKNOWN',
                     'regression_after_change': regression,
                     'trace_ids': sorted({s['trace_id'] for s in before + after}),
                     'evidence_refs': ['contracts.json#' + spec['id'], 'openapi-v1.json', 'openapi-v2.json']
                                      + ['spans.json#' + s['span_id'] for s in before + after],
                     'authorization': 'NOT_EVALUATED', 'business_values': 'NOT_COLLECTED',
                     'next_step': 'Validar migração com a equipe responsável' if missing
                     else 'Confirmar limites do contrato e ampliar testes'})
    return {'schema': SCHEMA, 'environment': 'loopback-lab',
            'business_data': 'synthetic', 'telemetry': 'real_local_execution',
            'scope_complete': False, 'removed_fields': removed, 'consumers': rows,
            'limitations': ['Contratos de consumo declarados; não extraídos automaticamente do código.',
                            'Somente GET/200 e remoção de propriedades no contrato deste laboratório.',
                            'Não observar chamadas não prova ausência de dependência.',
                            'Headers identificam os clientes do laboratório; não são autenticação.',
                            'PASS cobre somente o teste executado; não garante funcionamento completo.',
                            'Sem IAM, PostgreSQL, agentes ou integração com a interface pública.']}


def report(result: dict[str, Any]) -> str:
    labels = {'INCOMPATIBILITY': 'Incompatibilidade no contrato declarado',
              'NO_INCOMPATIBILITY_IN_DECLARED_CONTRACT': 'Sem incompatibilidade nesse contrato',
              'INCONCLUSIVE': 'Contrato insuficiente', 'OBSERVED': 'Uso observado',
              'UNKNOWN': 'Uso não confirmado', 'FAIL_OBSERVED_IN_LAB': 'Falha observada no teste',
              'PASS_IN_EXECUTED_CHECK': 'Passou no teste executado', 'NOT_VERIFIED': 'Não verificado'}
    lines = ['# EvidentGraph — primeira coleta em laboratório', '',
             '**Dados de negócio fictícios; chamadas HTTP e spans produzidos por execução real local.**', '',
             'Mudança: remover `' + ', '.join(result['removed_fields']) + '` da resposta da API de clientes.', '',
             '| Consumidor | Contrato | Uso antes | Teste após mudança | Responsável |',
             '|---|---|---|---|---|']
    for r in result['consumers']:
        lines.append('| ' + ' | '.join([r['consumer'], labels[r['contract']],
                     labels[r['usage_before_change']], labels[r['regression_after_change']], r['owner']]) + ' |')
    lines += ['', '## O que isto demonstra', '',
              'No recorte executado, é possível correlacionar contrato da API, contrato declarado do consumidor '
              'e execução instrumentada. O resultado de regressão é separado da previsão de incompatibilidade.',
              '', '## Limites', ''] + ['- ' + s for s in result['limitations']]
    lines += ['', '## Evidências por consumidor', '']
    for r in result['consumers']:
        lines += ['### ' + r['consumer'], '', 'Próximo passo: ' + r['next_step'], '',
                  'Referências: ' + ', '.join('`' + x + '`' for x in r['evidence_refs']), '',
                  'Traces correlacionados: ' + (', '.join('`' + x + '`' for x in r['trace_ids']) or 'nenhum'), '']
    return '\n'.join(lines) + '\n'


def execute(out: Path) -> dict[str, Any]:
    """Fresh run; refuse overwrite. Never switch to synthetic spans on failure."""
    out.mkdir(parents=True, exist_ok=False)
    db = out / 'lab.sqlite'
    with closing(sqlite3.connect(db)) as conn:
        conn.execute('CREATE TABLE customers (cliente_id TEXT PRIMARY KEY, status TEXT NOT NULL)')
        conn.execute('INSERT INTO customers VALUES (?, ?)', ('LAB-001', 'ativo'))
        conn.commit()
    recorder = Recorder()
    provider = TracerProvider(shutdown_on_exit=False)
    provider.add_span_processor(SimpleSpanProcessor(recorder))
    tracer = provider.get_tracer('evidentgraph.lab', '0.1.0')
    run: dict[str, Any] = {'schema': SCHEMA, 'started_at': datetime.now(timezone.utc).isoformat(),
                           'transport': 'HTTP over loopback TCP',
                           'consumers': CONSUMERS, 'openapi': {}, 'spans': []}
    try:
        for version in ['v1', 'v2']:
            with serve(make_app(version, db, tracer)) as url, httpx.Client(timeout=5, trust_env=False) as client:
                response = client.get(url + '/openapi.json')
                response.raise_for_status()
                run['openapi'][version] = response.json()
                for spec in CONSUMERS:
                    if spec['run']:
                        consume(client, url, spec, version, tracer)
        provider.force_flush()
    finally:
        provider.shutdown()
    run['spans'] = sorted(recorder.records, key=lambda s: s['start_ns'])
    run['finished_at'] = datetime.now(timezone.utc).isoformat()
    result = analyze(run)
    outputs = {'run.json': dump(run), 'spans.json': dump(run['spans']),
               'contracts.json': dump(CONSUMERS), 'analysis.json': dump(result), 'report.md': report(result)}
    outputs.update({f'openapi-{v}.json': dump(doc) for v, doc in run['openapi'].items()})
    for name, text in outputs.items():
        (out / name).write_text(text, encoding='utf-8')
    manifest = {'schema': SCHEMA, 'business_data': 'synthetic', 'telemetry': 'real_local_execution',
                'transport': run['transport'], 'spans': len(run['spans']),
                'sha256': {name: hashlib.sha256(text.encode('utf-8')).hexdigest() for name, text in outputs.items()}}
    (out / 'manifest.json').write_text(dump(manifest), encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path(__file__).parent / 'runs' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    args = parser.parse_args()
    try:
        result = execute(args.out)
    except (OSError, ValueError, RuntimeError, httpx.HTTPError) as exc:
        parser.exit(1, f'Laboratório não concluído: {exc}\nNão foi usado fallback de simulação.\n')
    print(report(result))
    print('Artefatos locais:', args.out)

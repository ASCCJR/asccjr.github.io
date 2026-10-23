"""Execute two small, owned consumers against explicitly synthetic invoice excerpts.

No HTTP, Stripe SDK, credentials, arbitrary plugins or production data. Expectations
are authored for this demonstration, not inferred from the contract or by an LLM.
"""
from __future__ import annotations
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BEFORE = '2025-02-24.acacia'
AFTER = '2025-03-31.basil'


def decision(status, subscription_id=None):
    return {'status': status, 'subscription_id': subscription_id}


def legacy_invoice(invoice, api_version):
    """Deliberately limited example: absent and null both mean no subscription.

    This is our example implementation, not code from Stripe or a customer.
    Its ignored version argument illustrates upgrading the response without
    migrating the consumer. A missing optional field already exposes a limitation.
    """
    value = invoice.get('subscription')
    if isinstance(value, dict):
        value = value.get('id')
    return decision('LINKED', value) if value else decision('NO_SUBSCRIPTION')


def migrated_invoice(invoice, api_version):
    """Basil-only reader; uncertain/unsupported input stays a review request."""
    if api_version != AFTER or not isinstance(invoice, dict) or 'parent' not in invoice:
        return decision('REVIEW')
    parent = invoice['parent']
    if parent is None:
        return decision('NO_SUBSCRIPTION')
    if not isinstance(parent, dict):
        return decision('REVIEW')
    kind = parent.get('type')
    if kind == 'quote_details':
        return decision('NO_SUBSCRIPTION')
    if kind != 'subscription_details':
        return decision('REVIEW')
    details = parent.get('subscription_details')
    if not isinstance(details, dict):
        return decision('REVIEW')
    value = details.get('subscription')
    if isinstance(value, dict):
        value = value.get('id')
    if not isinstance(value, str) or not value.strip():
        return decision('REVIEW')
    return decision('LINKED', value)


def check_contract_scope(facts, inputs):
    """Check only the specific field shapes used by this demonstration.

    Fixtures are excerpts, not fully validated invoice responses. Expanded
    subscriptions contain only the ID used by the demonstration consumer.
    """
    from build_case import field_at, dereference
    if ([s['version'] for s in facts['sources']] != [BEFORE, AFTER]
            or facts['endpoint'] != '/v1/invoices/{invoice}' or facts['method'] != 'GET'
            or facts['response_status'] != '200' or facts['field'] != ['subscription']
            or facts['replacement_field'] != ['parent', 'subscription_details', 'subscription']):
        raise ValueError('The simulated consumer is limited to the documented Stripe invoice case')
    before, after = [json.loads(inputs[k + '.json']) for k in ['before', 'after']]
    old = field_at(before, facts, ['subscription'])
    parent = field_at(after, facts, ['parent'])
    kind = field_at(after, facts, ['parent', 'type'])
    details = field_at(after, facts, ['parent', 'subscription_details'])
    new = field_at(after, facts, facts['replacement_field'])
    def id_shape(schema):
        choices = schema.get('anyOf', [])
        return (any(x.get('type') == 'string' for x in choices)
                and any(x.get('$ref') == '#/components/schemas/subscription' for x in choices))
    shape = (not old['required'] and old['schema'].get('nullable') is True
             and not parent['required'] and parent['schema'].get('nullable') is True
             and kind['required'] and set(kind['schema']['enum']) == {'quote_details', 'subscription_details'}
             and not details['required'] and details['schema'].get('nullable') is True
             and new['required'] and id_shape(old['schema']) and id_shape(new['schema']))
    if not shape:
        raise ValueError('The preserved contracts differ from the selected demonstration field shapes')
    for spec in [before, after]:
        schema, _ = dereference(spec, {'$ref': '#/components/schemas/subscription'}, '#')
        if schema['properties']['id'].get('type') != 'string':
            raise ValueError('Expanded subscription ID is not the expected string')
    return {'status': 'SELECTED_FIELD_SHAPES_CHECKED', 'complete_response_validation': False,
            'pointers': [old['pointer'], parent['pointer'], kind['pointer'], details['pointer'], new['pointer']],
            'note': 'Recortes sintéticos; somente os tipos e condições selecionados foram conferidos. Casos de robustez incluem entradas incompletas ou fora do contrato.'}


def execute_cases(cases):
    rows = []
    for case in cases:
        for stage, implementation, function in [('before', 'legacy', legacy_invoice),
                                                 ('after', 'legacy', legacy_invoice),
                                                 ('after', 'migrated', migrated_invoice)]:
            if stage not in case:
                continue
            fixture = case[stage]
            actual, exception = None, None
            try:
                actual = function(copy.deepcopy(fixture['payload']), BEFORE if stage == 'before' else AFTER)
            except Exception as error:
                exception = {'type': type(error).__name__, 'message': str(error)}
            expected = fixture['expected']
            rows.append({'case_id': case['id'], 'label': case['label'], 'category': case['category'],
                         'stage': stage, 'implementation': implementation,
                         'api_version': BEFORE if stage == 'before' else AFTER,
                         'input': fixture['payload'], 'expected': expected, 'actual': actual,
                         'exception': exception, 'matches_expectation': exception is None and actual == expected})
    return rows


def summarize(rows):
    groups = []
    for stage, implementation in [('before', 'legacy'), ('after', 'legacy'), ('after', 'migrated')]:
        selected = [r for r in rows if r['stage'] == stage and r['implementation'] == implementation]
        groups.append({'stage': stage, 'implementation': implementation, 'total': len(selected),
                       'matched': sum(r['matches_expectation'] for r in selected),
                       'mismatched': sum(not r['matches_expectation'] for r in selected),
                       'exceptions': sum(r['exception'] is not None for r in selected)})
    return groups


def run(facts, inputs):
    scope = check_contract_scope(facts, inputs)
    fixtures_raw = (HERE / 'consumer_demo_cases.json').read_bytes()
    fixtures = json.loads(fixtures_raw)
    if fixtures['synthetic'] is not True or fixtures['schema_version'] != 'eg-consumer-demo-cases/v1':
        raise ValueError('Expected explicitly synthetic demonstration fixtures')
    rows = execute_cases(fixtures['cases'])
    code_raw = Path(__file__).read_bytes()
    report = {
        'schema_version': 'eg-consumer-demo/v1', 'synthetic': True, 'material_kind': 'simulated_consumer',
        'title': 'Associar uma fatura à assinatura · demonstração simulada',
        'executed_at': datetime.now(timezone.utc).isoformat(),
        'execution_scope': 'LOCAL_PYTHON_SYNTHETIC_EXCERPTS', 'external_api_called': False,
        'real_consumer_coverage': 'UNKNOWN', 'real_consumer_runtime': 'NOT_VERIFIED',
        'business_expectation': 'No exemplo, preservar a referência da assinatura quando presente; separar ausência explícita de informação insuficiente.',
        'contract_scope': scope, 'contract_sources': facts['sources'],
        'files': [{'file': 'demo/consumer_demo.py', 'sha256': hashlib.sha256(code_raw).hexdigest()},
                  {'file': 'demo/consumer_demo_cases.json', 'sha256': hashlib.sha256(fixtures_raw).hexdigest()}],
        'summary': summarize(rows), 'runs': rows,
        'limitations': ['Código, recortes e expectativas foram preparados pelo mesmo autor; não é avaliação independente.',
                        'Não há consumidor, cliente, incidente, ganho de tempo ou perda financeira real identificado.',
                        'O leitor antigo é um exemplo controlado; não representa todas as integrações existentes.',
                        'O leitor adaptado cobre somente a versão Basil e estes campos. Pedir revisão também pode ser o resultado correto.',
                        'Uma execução sem exceção pode descumprir a expectativa. Passar nestes exemplos não garante migração segura.']}
    files = {'demo/consumer_demo.py': code_raw, 'demo/consumer_demo_cases.json': fixtures_raw,
             'demo/result.json': (json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode()}
    return report, files


def attach(bundle, report, files):
    """Attach explicitly labeled demonstration evidence, never real consumers."""
    bundle['synthetic'] = True  # The combined workspace includes an authored simulation.
    bundle['provenance']['consumer_demo'] = report
    bundle['provenance']['material_mix'] = ['public_contracts', 'simulated_consumer']
    bundle['dataset_version'] += '-demo-' + hashlib.sha256(files['demo/result.json']).hexdigest()[:12]
    bundle['domains'].append({'id': 'demonstracao', 'name': 'Consumidor simulado'})
    for implementation, stage, label in [('legacy', 'before', 'Leitor antigo · simulado'),
                                         ('migrated', 'after', 'Leitor adaptado · simulado')]:
        asset_id, ev_id = 'demo-' + implementation, 'demo-evidence-' + implementation
        runs = [r for r in report['runs'] if r['implementation'] == implementation]
        bundle['assets'].append({'id': asset_id, 'name': label, 'kind': 'service', 'domain': 'demonstracao',
                                 'owner': 'unknown', 'environment': 'simulation', 'version': 'demo-v1',
                                 'processes': [], 'evidence_ids': [ev_id], 'material_kind': 'simulated_consumer'})
        bundle['evidence'].append({'id': ev_id, 'family': 'runtime', 'claim': 'local_simulation_result',
                                   'reference': 'demo/result.json', 'collected_at': report['executed_at'],
                                   'environment': 'simulation', 'version': 'demo-v1',
                                   'sha256': hashlib.sha256(files['demo/result.json']).hexdigest(),
                                   'implementation': implementation, 'synthetic': True,
                                   'details': {'runs': runs, 'source_files': report['files']},
                                   'limitation': 'Execução local de código próprio em recortes fictícios. Nenhuma chamada à Stripe ou descoberta de consumidor real.'})
        bundle['relations'].append({'id': 'demo-read-' + implementation, 'source': asset_id,
                                    'target': 'field-' + stage, 'kind': 'DEMO_READS',
                                    'environment': 'simulation', 'evidence_ids': [ev_id],
                                    'material_kind': 'simulated_consumer',
                                    'limitation': 'Vínculo declarado para o código deste exemplo; não é chamada HTTP nem dependência descoberta em produção.'})

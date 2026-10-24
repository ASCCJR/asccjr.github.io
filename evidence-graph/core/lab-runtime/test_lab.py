"""Real loopback fixture plus negative controls; no injected fake runtime on failure."""
import copy
import hashlib
import json
from pathlib import Path
import socket
import tempfile
import unittest
import httpx
from opentelemetry.sdk.trace import TracerProvider

import lab


class LabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name) / 'run'
        cls.result = lab.execute(cls.out)
        cls.record = json.loads((cls.out / 'run.json').read_text(encoding='utf-8'))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def altered(self, mutate):
        run = copy.deepcopy(self.record)
        mutate(run)
        return lab.analyze(run)

    @staticmethod
    def row(result, consumer):
        return next(r for r in result['consumers'] if r['consumer'] == consumer)

    def test_real_tcp_transport(self):
        self.assertEqual(self.record['transport'], 'HTTP over loopback TCP')

    def test_collected_openapi_versions(self):
        self.assertEqual(self.record['openapi']['v1']['info']['version'], 'v1')
        self.assertEqual(self.record['openapi']['v2']['info']['version'], 'v2')
        self.assertEqual(lab.response_fields(self.record['openapi']['v1']), {'cliente_id', 'status'})
        self.assertEqual(lab.response_fields(self.record['openapi']['v2']), {'status'})

    def test_removed_field(self):
        self.assertEqual(self.result['removed_fields'], ['cliente_id'])

    def test_count_actual_spans(self):
        self.assertEqual(len(self.record['spans']), 12)
        self.assertEqual(len({s['trace_id'] for s in self.record['spans']}), 4)

    def test_parenting_all_database_spans(self):
        for s in self.record['spans']:
            if s['attributes'].get('db.system.name') == 'sqlite':
                parent = next(p for p in self.record['spans'] if p['span_id'] == s['parent_span_id'])
                self.assertEqual(parent['kind'], 'SERVER')
                self.assertEqual(parent['trace_id'], s['trace_id'])

    def test_pedidos_failure_is_observed(self):
        r = self.row(self.result, 'pedidos')
        self.assertEqual(r['contract'], 'INCOMPATIBILITY')
        self.assertEqual(r['usage_before_change'], 'OBSERVED')
        self.assertEqual(r['regression_after_change'], 'FAIL_OBSERVED_IN_LAB')

    def test_portal_does_not_depend_on_removed_field(self):
        r = self.row(self.result, 'portal')
        self.assertEqual(r['contract'], 'NO_INCOMPATIBILITY_IN_DECLARED_CONTRACT')
        self.assertEqual(r['regression_after_change'], 'PASS_IN_EXECUTED_CHECK')

    def test_not_executed_does_not_mean_safe(self):
        r = self.row(self.result, 'exportador')
        self.assertEqual(r['contract'], 'INCOMPATIBILITY')
        self.assertEqual(r['usage_before_change'], 'UNKNOWN')
        self.assertEqual(r['regression_after_change'], 'NOT_VERIFIED')

    def test_no_runtime_preserves_declared_incompatibility(self):
        result = self.altered(lambda r: r.update(spans=[]))
        row = self.row(result, 'pedidos')
        self.assertEqual(row['contract'], 'INCOMPATIBILITY')
        self.assertEqual(row['usage_before_change'], 'UNKNOWN')
        self.assertEqual(row['regression_after_change'], 'NOT_VERIFIED')

    def test_no_contract_does_not_hide_execution(self):
        result = self.altered(lambda r: r['consumers'][0].update(required_fields=None))
        row = self.row(result, 'pedidos')
        self.assertEqual(row['contract'], 'INCONCLUSIVE')
        self.assertEqual(row['usage_before_change'], 'OBSERVED')

    def test_trace_mismatch_never_correlates(self):
        def mutation(r):
            for s in r['spans']:
                if s['kind'] == 'SERVER': s['trace_id'] = '0' * 32
        result = self.altered(mutation)
        self.assertTrue(all(r['usage_before_change'] == 'UNKNOWN' for r in result['consumers']))

    def test_parent_mismatch_never_correlates(self):
        def mutation(r):
            for s in r['spans']:
                if s['kind'] == 'SERVER': s['parent_span_id'] = '0' * 16
        result = self.altered(mutation)
        self.assertEqual(self.row(result, 'pedidos')['usage_before_change'], 'UNKNOWN')

    def test_version_mismatch_never_correlates(self):
        def mutation(r):
            for s in r['spans']:
                if s['kind'] == 'SERVER': s['attributes']['lab.api_version'] = 'v99'
        self.assertEqual(self.row(self.altered(mutation), 'pedidos')['usage_before_change'], 'UNKNOWN')

    def test_events_outside_client_window_never_correlate(self):
        def mutation(r):
            for s in r['spans']:
                if s['kind'] == 'SERVER':
                    s['start_ns'] = 0
                    s['end_ns'] = 1
        self.assertEqual(self.row(self.altered(mutation), 'pedidos')['usage_before_change'], 'UNKNOWN')

    def test_server_absence_is_inconclusive(self):
        r = self.altered(lambda r: r.update(spans=[s for s in r['spans'] if s['kind'] != 'SERVER']))
        self.assertEqual(self.row(r, 'pedidos')['regression_after_change'], 'NOT_VERIFIED')

    def test_duplicate_spans_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicated'):
            self.altered(lambda r: r['spans'].append(copy.deepcopy(r['spans'][0])))

    def test_external_openapi_reference_rejected(self):
        doc = copy.deepcopy(self.record['openapi']['v1'])
        doc['paths'][lab.ROUTE]['get']['responses']['200']['content']['application/json']['schema'] = {'$ref':'https://example.invalid/contract'}
        with self.assertRaises(ValueError): lab.response_fields(doc)

    def test_cyclic_openapi_reference_rejected(self):
        doc = copy.deepcopy(self.record['openapi']['v1'])
        doc['components']['schemas']['CustomerV1'] = {'$ref':'#/components/schemas/CustomerV1'}
        with self.assertRaises(ValueError): lab.response_fields(doc)

    def test_bad_consumer_field_type_rejected(self):
        with self.assertRaises(ValueError):
            self.altered(lambda r: r['consumers'][0].update(required_fields='cliente_id'))

    def test_wrong_schema_rejected(self):
        with self.assertRaises(ValueError): self.altered(lambda r: r.update(schema='unknown'))

    def test_no_personal_or_business_values_in_spans(self):
        text = lab.dump(self.record['spans'])
        self.assertNotIn('LAB-001', text)
        self.assertNotIn('"ativo"', text)
        self.assertNotIn('127.0.0.1', text)
        self.assertNotIn('authorization', text.lower())

    def test_output_checksums(self):
        manifest = json.loads((self.out / 'manifest.json').read_text())
        for name, digest in manifest['sha256'].items():
            self.assertEqual(hashlib.sha256((self.out / name).read_bytes()).hexdigest(), digest)

    def test_report_contains_scope_and_all_consumers(self):
        report = (self.out / 'report.md').read_text(encoding='utf-8')
        for x in ['pedidos', 'portal', 'exportador', 'Dados de negócio fictícios', 'Não verificado']:
            self.assertIn(x, report)

    def test_existing_output_not_overwritten(self):
        sentinel = self.out / 'sentinel'
        sentinel.write_text('preserve')
        with self.assertRaises(FileExistsError): lab.execute(self.out)
        self.assertEqual(sentinel.read_text(), 'preserve')

    def test_404_and_loopback_binding(self):
        provider = TracerProvider(shutdown_on_exit=False)
        try:
            with lab.serve(lab.make_app('v1', self.out / 'lab.sqlite', provider.get_tracer('test'))) as url:
                self.assertTrue(url.startswith('http://127.0.0.1:'))
                response = httpx.get(url + '/customers/missing', timeout=3, trust_env=False)
                self.assertEqual(response.status_code, 404)
                port = int(url.rsplit(':', 1)[1])
            with self.assertRaises(OSError): socket.create_connection(('127.0.0.1', port), timeout=1)
        finally:
            provider.shutdown()

    def test_unknown_version_rejected(self):
        provider = TracerProvider(shutdown_on_exit=False)
        try:
            with self.assertRaises(ValueError):
                lab.make_app('v3', self.out / 'lab.sqlite', provider.get_tracer('test'))
        finally:
            provider.shutdown()

    def test_authorization_never_assumed(self):
        self.assertTrue(all(r['authorization'] == 'NOT_EVALUATED' for r in self.result['consumers']))
        self.assertFalse(self.result['scope_complete'])

    def test_results_recalculated_from_openapi(self):
        r = self.altered(lambda r: r['openapi'].update(v2=copy.deepcopy(r['openapi']['v1'])))
        self.assertEqual(r['removed_fields'], [])
        self.assertEqual(self.row(r, 'pedidos')['contract'], 'NO_INCOMPATIBILITY_IN_DECLARED_CONTRACT')
        # Past observation is a distinct fact and is not rewritten with the contract.
        self.assertEqual(self.row(r, 'pedidos')['regression_after_change'], 'FAIL_OBSERVED_IN_LAB')

if __name__ == '__main__':
    unittest.main(verbosity=2)

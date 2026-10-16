"""Real browser navigation tests; no DOM injection or mocked network fallback.

Run with `python -m unittest -v test_browser_http` after installing Playwright
and its Chromium browser. EG_BROWSER_PATH can select an existing executable.
A blocked navigation fails the suite: it is not skipped or counted as success.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright, expect
import lab
from build_view import build


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


class BrowserHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        for name in ('a', 'b'):
            lab.execute(cls.root / ('capture-' + name))
            build(cls.root / ('capture-' + name) / 'run.json', cls.root / name)
        handler = partial(QuietHandler, directory=str(cls.root))
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.addClassCleanup(cls.stop_server)
        cls.origin = f'http://127.0.0.1:{cls.server.server_port}'
        cls.pw = sync_playwright().start()
        cls.addClassCleanup(cls.pw.stop)
        options = {'headless': True}
        if os.environ.get('EG_BROWSER_PATH'):
            options['executable_path'] = os.environ['EG_BROWSER_PATH']
        cls.browser = cls.pw.chromium.launch(**options)
        cls.addClassCleanup(cls.browser.close)

    @classmethod
    def stop_server(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 1366, 'height': 768}, accept_downloads=True)
        self.addCleanup(self.context.close)
        self.page = self.context.new_page()
        self.page.set_default_timeout(8000)
        self.errors = []
        self.external = []
        self.page.on('pageerror', lambda e: self.errors.append(str(e)))
        self.page.on('request', lambda r: self.external.append(r.url)
                     if urlsplit(r.url).scheme in ('http', 'https') and not r.url.startswith(self.origin + '/') else None)

    def tearDown(self):
        self.assertEqual([], self.errors, 'Uncaught browser errors')
        self.assertEqual([], self.external, 'Unexpected external HTTP requests')

    def ready(self, source='lab'):
        self.page.wait_for_function("""s => typeof data !== 'undefined' && !!data &&
            typeof EGGraph !== 'undefined' && document.querySelectorAll('[data-node]').length > 0 &&
            document.getElementById('workspaceSource').value === s &&
            (s === 'lab' ? data.provenance?.kind === 'l1_capture' : data.synthetic === true)""", arg=source)

    def open(self, name='a', source='lab', standalone=False, fragment=''):
        filename = 'EvidentGraph_L2.html' if standalone else 'index.html'
        suffix = ('?source=' + source) if source else ''
        response = self.page.goto(f'{self.origin}/{name}/{filename}{suffix}{fragment}', wait_until='load')
        self.assertEqual(200, response.status)
        self.ready(source or ('aurora' if fragment == '#aurora' else 'lab'))

    def switch(self, source):
        self.page.select_option('#workspaceSource', source)
        self.page.wait_for_url('**/*source=' + source)
        self.ready(source)

    def review(self):
        if self.page.locator('#graphView').is_visible():
            self.page.click('#graphReview')
        expect(self.page.locator('#analysisResult')).to_be_visible()

    def note(self, text):
        self.review()
        self.page.click('[data-detail="l1-pedidos"]')
        self.page.fill('#reviewNote', text)
        self.page.click('#closeDetail')

    def stored_note(self):
        self.review()
        self.page.click('[data-detail="l1-pedidos"]')
        text = self.page.locator('#reviewNote').input_value()
        self.page.click('#closeDetail')
        return text

    def test_01_http_assets_and_graph_list(self):
        statuses = []
        self.page.on('response', lambda r: statuses.append((r.url, r.status)))
        self.open()
        ids = self.page.locator('[data-node]').evaluate_all('(xs)=>xs.map(x=>x.dataset.node).sort()')
        self.assertEqual(5, len(ids))
        self.assertEqual(4, self.page.locator('[data-edge]').count())
        self.page.click('#graphToList')
        self.assertEqual(ids, self.page.locator('[data-explore-row]').evaluate_all('(xs)=>xs.map(x=>x.dataset.exploreRow).sort()'))
        assets = [(u, s) for u, s in statuses if urlsplit(u).path.endswith(('.js', '.css', '.html'))]
        self.assertGreater(len(assets), 8)
        self.assertTrue(all(s == 200 for _, s in assets), assets)

    def test_02_source_roundtrip_and_full_aurora(self):
        self.open()
        self.switch('aurora')
        self.page.select_option('#graphScope', 'all')
        self.assertEqual(240, self.page.locator('[data-node]').count())
        self.assertEqual(512, self.page.locator('[data-edge]').count())
        self.switch('lab')
        self.assertEqual(5, self.page.locator('[data-node]').count())
        self.assertEqual(3, self.page.evaluate('result.consumers.length'))

    def test_03_note_and_check_survive_reload_without_erasing_failure(self):
        self.open()
        self.note('Revisar contrato com Comercial.')
        self.page.check('[data-check="l1-pedidos"]')
        self.page.reload(wait_until='load')
        self.ready()
        self.assertEqual('Revisar contrato com Comercial.', self.stored_note())
        expect(self.page.locator('[data-check="l1-pedidos"]')).to_be_checked()
        self.assertIn('Falhou no teste executado', self.page.locator('#consumerRows').inner_text())

    def test_04_notes_isolated_between_sources(self):
        self.open()
        self.note('SOMENTE_LAB')
        self.switch('aurora')
        self.review()
        self.assertNotIn('SOMENTE_LAB', self.page.evaluate('report()'))
        self.switch('lab')
        self.assertEqual('SOMENTE_LAB', self.stored_note())

    def test_05_notes_isolated_between_capture_hashes(self):
        self.open('a')
        self.note('CAPTURA_A')
        first = self.page.evaluate('data.provenance.source_sha256')
        self.open('b')
        self.assertNotEqual(first, self.page.evaluate('data.provenance.source_sha256'))
        self.assertEqual('', self.stored_note())
        self.open('a')
        self.assertEqual('CAPTURA_A', self.stored_note())

    def test_06_source_survives_accessibility_anchor_and_reload(self):
        self.open(source='aurora')
        self.page.locator('.skip').focus()
        self.page.keyboard.press('Enter')
        self.page.reload(wait_until='load')
        self.ready('aurora')
        self.assertTrue(self.page.evaluate('data.synthetic'))

    def test_07_legacy_hash_link_normalized(self):
        self.open(source='', fragment='#aurora')
        self.assertIn('source=aurora', self.page.url)
        self.page.reload(wait_until='load')
        self.ready('aurora')

    def test_08_back_and_forward_keep_source_consistent(self):
        self.open()
        self.switch('aurora')
        self.page.go_back(wait_until='load')
        self.ready('lab')
        self.page.go_forward(wait_until='load')
        self.ready('aurora')

    def test_09_unavailable_storage_warns_and_allows_cancel(self):
        # Deliberate storage failure injection, not a navigation/network substitute.
        self.context.add_init_script("Storage.prototype.setItem = function(){throw new DOMException('Blocked test','SecurityError');};")
        self.open()
        self.note('Nota temporária para exportar')
        expect(self.page.locator('#storageNotice')).to_be_visible()
        self.page.once('dialog', lambda d: d.dismiss())
        self.page.select_option('#workspaceSource', 'aurora')
        self.assertEqual('lab', self.page.locator('#workspaceSource').input_value())
        self.assertEqual('Nota temporária para exportar', self.stored_note())
        with self.page.expect_download() as downloaded:
            self.page.click('#exportBtn')
        content = Path(downloaded.value.path()).read_text(encoding='utf-8')
        self.assertIn('Nota temporária para exportar', content)

    def test_10_filtered_export_and_unknown_stays_unknown(self):
        self.open()
        self.review()
        self.page.fill('#search', 'Exportador')
        with self.page.expect_download() as downloaded:
            self.page.click('#exportBtn')
        content = Path(downloaded.value.path()).read_text(encoding='utf-8')
        self.assertIn('Consumidores exportados: 1 de 3', content)
        self.assertIn('Não verificado', content)
        self.assertNotIn('| Cliente de pedidos |', content)
        self.assertIn(self.page.evaluate('data.provenance.source_sha256'), content)

    def test_11_standalone_has_same_persistent_capture(self):
        self.open(standalone=True)
        self.note('HTML_UNICO')
        self.page.reload(wait_until='load')
        self.ready()
        self.assertEqual('HTML_UNICO', self.stored_note())
        self.switch('aurora')
        self.switch('lab')
        self.assertEqual('HTML_UNICO', self.stored_note())

    def test_12_corrupt_storage_does_not_prevent_opening(self):
        self.open()
        self.page.evaluate("localStorage.setItem('eg-m2:' + data.dataset_version, '{invalid-json')")
        self.page.reload(wait_until='load')
        self.ready()
        self.assertEqual('', self.stored_note())
        expect(self.page.locator('#storageNotice')).to_be_visible()
        self.page.screenshot(path=str(self.root / 'browser-validation.png'), full_page=True)


if __name__ == '__main__':
    unittest.main()

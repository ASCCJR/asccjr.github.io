"""Actual HTTP browser checks for L5. Blocked navigation fails; no injection fallback."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.parse import urlsplit, parse_qs
from playwright.sync_api import sync_playwright, expect
import auth_lab
from build_auth_view import build

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

class AuthBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.tmp.cleanup);cls.root=Path(cls.tmp.name)
        auth_lab.execute(cls.root/'capture');build(cls.root/'capture/run.json',cls.root/'view')
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(cls.root)))
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.addClassCleanup(cls.stop);cls.origin=f'http://127.0.0.1:{cls.server.server_port}'
        cls.pw=sync_playwright().start();cls.addClassCleanup(cls.pw.stop)
        options={'headless':True}
        if os.environ.get('EG_BROWSER_PATH'):options['executable_path']=os.environ['EG_BROWSER_PATH']
        cls.browser=cls.pw.chromium.launch(**options);cls.addClassCleanup(cls.browser.close)
    @classmethod
    def stop(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join(5)
    def setUp(self):
        self.context=self.browser.new_context(viewport={'width':1366,'height':768},accept_downloads=True)
        self.addCleanup(self.context.close);self.page=self.context.new_page();self.page.set_default_timeout(7000)
        self.errors=[];self.external=[];self.page.on('pageerror',lambda e:self.errors.append(str(e)))
        self.page.on('request',lambda r:self.external.append(r.url) if not r.url.startswith(self.origin) else None)
    def tearDown(self):self.assertEqual([],self.errors);self.assertEqual([],self.external)
    def ready(self,source='access'):
        self.page.wait_for_function("s => typeof data!=='undefined'&&!!data&&typeof EGGraph!=='undefined'&&document.querySelectorAll('[data-node]').length>0&&document.getElementById('workspaceSource').value===s",arg=source)
    def open(self,standalone=False):
        name='EvidentGraph_L5.html' if standalone else 'index.html'
        response=self.page.goto(self.origin+'/view/'+name+'?source=access');self.assertEqual(200,response.status);self.ready()
    def review(self):
        if self.page.locator('#lineageView').is_visible():self.page.click('#graphReview')
        expect(self.page.locator('#analysisResult')).to_be_visible()
    def switch(self,s):
        self.page.select_option('#workspaceSource',s)
        self.page.wait_for_url(lambda u:parse_qs(urlsplit(u).query).get('source')==[s]);self.ready(s)
    def test_01_graph_and_list_same_context(self):
        self.open();self.page.select_option('#graphScope','all');self.page.check('#graphTechnical')
        ids=self.page.locator('[data-node]').evaluate_all('(xs)=>xs.map(x=>x.dataset.node).sort()');self.assertEqual(10,len(ids))
        self.assertEqual(9,self.page.locator('[data-edge]').count());self.page.click('#graphToList')
        self.assertEqual(ids,self.page.locator('[data-explore-row]').evaluate_all('(xs)=>xs.map(x=>x.dataset.exploreRow).sort()'))
    def test_02_policy_attempt_and_success_visible(self):
        self.open();self.review();self.page.click('[data-detail="l5-portal"]')
        t=self.page.locator('#detailBody').inner_text();self.assertIn('Negado',t);self.assertIn('HTTP 403',t)
        self.assertIn('Não concluído na tentativa',t);self.assertNotIn('Autorização: não avaliada',t)
    def test_03_unknown_not_failed_contract(self):
        self.open();self.review();self.page.click('[data-detail="l5-exportador"]')
        t=self.page.locator('.auth-panel').inner_text();self.assertIn('Indeterminado',t);self.assertIn('HTTP 503',t)
        self.assertIn('Não verificado',t)
    def test_04_allowed_not_executed(self):
        self.open();self.review();self.page.click('[data-detail="l5-conciliacao"]')
        t=self.page.locator('#detailBody .auth-panel').inner_text();self.assertIn('Permitido',t);self.assertIn('Não confirmado',t)
    def test_05_notes_reload_and_failure_preserved(self):
        self.open();self.review();self.page.click('[data-detail="l5-pedidos"]');self.page.fill('#reviewNote','NOTA_L5')
        self.page.click('#closeDetail');self.page.check('#consumerRows [data-check="l5-pedidos"]')
        self.page.reload();self.ready();self.review();self.page.click('[data-detail="l5-pedidos"]')
        self.assertEqual('NOTA_L5',self.page.locator('#reviewNote').input_value())
        self.assertIn('Falhou no teste',self.page.locator('#detailBody').inner_text())
    def test_06_aurora_preserved(self):
        self.open();self.switch('aurora');self.page.select_option('#graphScope','all');self.page.check('#graphTechnical')
        self.assertEqual(240,self.page.locator('[data-node]').count());self.assertEqual(512,self.page.locator('[data-edge]').count())
        self.switch('access');self.assertEqual(10,self.page.evaluate('data.assets.length'))
    def test_07_export_uses_filtered_decisions(self):
        self.open();self.review();self.page.fill('#search','Exportador')
        with self.page.expect_download() as d:self.page.click('#exportBtn')
        text=Path(d.value.path()).read_text();self.assertIn('Exportados: 1 de 4',text);self.assertIn('Indeterminado',text)
        self.assertIn('HTTP 503',text);self.assertNotIn('| Cliente de pedidos |',text)
    def test_08_standalone(self):
        self.open(standalone=True);self.review();self.assertIn('Negado',self.page.locator('#consumerRows').inner_text())
    def test_09_about_discloses_scope(self):
        self.open();self.page.click('#aboutBtn');t=self.page.locator('#aboutDialog').inner_text()
        self.assertIn('O HTML não possui tokens',t);self.assertIn('captura',t)
    def test_10_narrow_screen_no_page_overflow(self):
        self.open();self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),1366)

if __name__=='__main__':unittest.main()

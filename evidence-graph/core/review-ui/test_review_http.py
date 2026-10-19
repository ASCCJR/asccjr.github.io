"""Real browser HTTP only. Deterministic delayed-extension regression, no retry/fallback."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import threading
import unittest
from urllib.parse import urlsplit,parse_qs
from playwright.sync_api import sync_playwright,expect
from build_review import build,CORE
sys.path.insert(0,str(CORE/'evaluation/refinement'))
import run_refinement
from auth_lab import execute as collect_auth
from build_auth_view import build as build_auth

class ScriptGate:
    """Hold the real HTTP response until the test observes the required order."""
    def __init__(self):
        self.requested=threading.Event()
        self.release=threading.Event()

class Handler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        gate=getattr(self.server,'script_gate',None)
        if gate is not None and urlsplit(self.path).path.endswith('/auth_view.js'):
            gate.requested.set()
            if not gate.release.wait(8):
                self.send_error(504,'Test did not release the extension response')
                return
        super().do_GET()

class ReviewHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.tmp.cleanup);cls.root=Path(cls.tmp.name)
        run_refinement.execute(cls.root/'reference');build(cls.root/'reference',cls.root/'view')
        collect_auth(cls.root/'capture');build_auth(cls.root/'capture/run.json',cls.root/'auth')
        # Recreate precisely the old eager-boot pattern, never run it in a production origin.
        shutil.copytree(cls.root/'auth',cls.root/'legacy')
        p=cls.root/'legacy/app.js';p.write_text(p.read_text().replace('window.EGStart = boot;','boot();'))
        p=cls.root/'legacy/index.html';p.write_text(p.read_text().replace('<script src="view_bootstrap.js" defer></script>','').replace(' disabled aria-busy="true"',''))
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(cls.root)))
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start();cls.addClassCleanup(cls.stop)
        cls.url=f'http://127.0.0.1:{cls.server.server_port}'
        cls.pw=sync_playwright().start();cls.addClassCleanup(cls.pw.stop)
        opts={'headless':True,'chromium_sandbox':True}
        if os.getenv('EG_BROWSER_PATH'):opts['executable_path']=os.environ['EG_BROWSER_PATH']
        cls.browser=cls.pw.chromium.launch(**opts);cls.addClassCleanup(cls.browser.close)
    @classmethod
    def stop(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join(5)
    def setUp(self):
        self.ctx=self.browser.new_context(viewport={'width':1366,'height':900},accept_downloads=True);self.addCleanup(self.ctx.close)
        self.p=self.ctx.new_page();self.p.set_default_timeout(8000);self.errors=[]
        self.p.on('pageerror',lambda e:self.errors.append(str(e)))
        # Observe the real event; do not replace the HTML, bootstrap or network.
        self.p.add_init_script("window.__eg_ready_count=0;document.addEventListener('eg:ready',()=>window.__eg_ready_count++);")
    def tearDown(self):self.assertEqual([],self.errors)
    def ready(self):
        self.p.wait_for_function('window.EG_WORKSPACE_READY===true')
        expect(self.p.locator('#workspaceSource')).to_be_enabled()
    def open(self,source='review',file='index.html'):
        r=self.p.goto(self.url+'/view/'+file+'?source='+source);self.assertEqual(200,r.status);self.ready()
    def switch(self,source):
        self.p.select_option('#workspaceSource',source)
        self.p.wait_for_url(lambda u:parse_qs(urlsplit(u).query).get('source')==[source]);self.ready()
    def review(self):
        if self.p.locator('#lineageView').is_visible():self.p.click('#graphReview')
        expect(self.p.locator('#analysisResult')).to_be_visible()
    def gate_extension(self):
        gate=ScriptGate();self.server.script_gate=gate
        self.addCleanup(setattr,self.server,'script_gate',None)
        self.addCleanup(gate.release.set)
        return gate
    def test_01_reproduce_legacy_late_listener(self):
        gate=self.gate_extension()
        self.p.goto(self.url+'/legacy/index.html?source=access',wait_until='commit')
        self.p.wait_for_function("window.__eg_ready_count===1 && typeof data!=='undefined' && data && !!document.querySelector('[data-node]')")
        self.assertTrue(gate.requested.wait(8),'Extension request did not reach the HTTP gate')
        self.assertFalse(gate.release.is_set())
        # Core readiness happened while the extension response was withheld.
        gate.release.set();self.p.wait_for_load_state('load')
        self.assertEqual('l5_capture',self.p.evaluate('data.provenance.kind'))
        self.assertEqual(1,self.p.evaluate('window.__eg_ready_count'))
        # The late listener missed eg:ready: company still Aurora, and selector has no behavior.
        self.assertIn('Grupo Aurora',self.p.locator('.company').inner_text())
        self.p.select_option('#workspaceSource','aurora')
        self.p.evaluate('() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))')
        self.assertEqual(['access'],parse_qs(urlsplit(self.p.url).query)['source'])
        self.assertEqual('l5_capture',self.p.evaluate('data.provenance.kind'))
    def test_02_delayed_extension_is_safe_after_fix(self):
        gate=self.gate_extension()
        self.p.goto(self.url+'/auth/index.html?source=access',wait_until='commit')
        self.p.wait_for_function("typeof window.EGStart==='function'")
        self.assertTrue(gate.requested.wait(8),'Extension request did not reach the HTTP gate')
        self.assertFalse(gate.release.is_set())
        expect(self.p.locator('#workspaceSource')).to_be_disabled()
        self.assertEqual(0,self.p.evaluate('window.__eg_ready_count'))
        gate.release.set()
        self.ready();self.assertIn('Aurora Acesso',self.p.locator('.company').inner_text())
        self.assertEqual('l5_capture',self.p.evaluate('data.provenance.kind'))
        for s in ['aurora','access','aurora','access']:
            self.p.select_option('#workspaceSource',s)
            self.p.wait_for_url(lambda u:parse_qs(urlsplit(u).query).get('source')==[s]);self.ready()
            self.assertEqual(240 if s=='aurora' else 10,self.p.evaluate('data.assets.length'))
            self.assertEqual(s,self.p.locator('#workspaceSource').input_value())
            self.assertEqual(1,self.p.evaluate('window.__eg_ready_count'))
    def test_03_graph_list_same_ids(self):
        self.open();ids=self.p.locator('[data-node]').evaluate_all('(xs)=>xs.map(x=>x.dataset.node).sort()')
        self.assertEqual(13,len(ids));self.p.click('#graphToList')
        self.assertEqual(ids,self.p.locator('[data-explore-row]').evaluate_all('(xs)=>xs.map(x=>x.dataset.exploreRow).sort()'))
    def test_04_caught_field_not_shown_as_failure(self):
        self.open();self.review();self.p.click('[data-detail="l7-c06"]')
        t=self.p.locator('#detailBody').inner_text();self.assertIn('Leitura do campo observada',t)
        self.assertIn('Sem exceção prevista no recorte',t);self.assertNotIn('truth-original.json',t)
    def test_05_unsupported_inference_stays_unknown_after_reveal(self):
        self.open();self.p.check('#showRecordedTests');self.review();self.p.click('[data-detail="l7-c10"]')
        t=self.p.locator('#detailBody').inner_text();self.assertIn('Inferência inconclusiva',t);self.assertIn('Exceção observada no teste',t)
    def test_06_same_code_business_difference(self):
        self.open('validation');self.p.check('#showRecordedTests');self.review()
        for key,expected in [('n01','Requisito violado no teste'),('n02','Requisito atendido no teste')]:
            self.p.click('[data-detail="l7-'+key+'"]');t=self.p.locator('#detailBody').inner_text()
            self.assertIn('Sem exceção prevista no recorte',t);self.assertIn(expected,t);self.p.click('#closeDetail')
    def test_07_notes_reload_and_source_isolation(self):
        self.open();self.review();self.p.click('[data-detail="l7-c06"]');self.p.fill('#reviewNote','NOTA_C06');self.p.click('#closeDetail')
        self.p.reload();self.ready();self.review();self.p.click('[data-detail="l7-c06"]')
        self.assertEqual('NOTA_C06',self.p.locator('#reviewNote').input_value());self.p.click('#closeDetail')
        self.switch('validation');self.review();self.p.click('[data-detail="l7-n01"]');self.assertEqual('',self.p.locator('#reviewNote').input_value())
        self.p.click('#closeDetail');self.switch('review');self.review();self.p.click('[data-detail="l7-c06"]');self.assertEqual('NOTA_C06',self.p.locator('#reviewNote').input_value())
    def test_08_export_only_requested_evidence(self):
        self.open('validation');self.review();self.p.fill('#search','Pedido identificado')
        with self.p.expect_download() as d:self.p.click('#exportBtn')
        before=Path(d.value.path()).read_text();self.assertIn('Exportados: 1 de 8',before);self.assertNotIn('truth-semantic.json',before)
        self.p.check('#showRecordedTests')
        with self.p.expect_download() as d:self.p.click('#exportBtn')
        after=Path(d.value.path()).read_text();self.assertIn('Requisito violado no teste',after);self.assertIn('truth-semantic.json',after)
    def test_09_full_aurora_remains_available(self):
        self.open();self.switch('aurora');self.p.select_option('#graphScope','all');self.p.check('#graphTechnical')
        self.assertEqual(240,self.p.locator('[data-node]').count());self.assertEqual(512,self.p.locator('[data-edge]').count())
        self.switch('review');self.assertEqual(13,self.p.locator('[data-node]').count())
    def test_10_standalone_and_history(self):
        self.open(file='EvidentGraph_L7.html');self.switch('validation');self.p.go_back();self.ready()
        self.assertEqual('review',self.p.locator('#workspaceSource').input_value())
        self.p.go_forward();self.ready();self.assertEqual('validation',self.p.locator('#workspaceSource').input_value())
    def test_11_no_horizontal_document_overflow(self):
        self.open();self.assertLessEqual(self.p.evaluate('document.documentElement.scrollWidth'),1366)
    def test_12_manual_mark_never_changes_outcome(self):
        self.open('validation');self.p.check('#showRecordedTests');self.review();self.p.check('#consumerRows [data-check="l7-n01"]')
        self.p.click('[data-detail="l7-n01"]');self.assertIn('Requisito violado no teste',self.p.locator('#detailBody').inner_text())
    def test_13_graph_export_matches_selected_source(self):
        self.open()
        for source,name,count in [('review','Aurora Revisão',12),('validation','Aurora Validação',8)]:
            if source!='review':self.switch(source)
            text=self.p.evaluate('EGInvestigation.report()')
            self.assertIn(name,text);self.assertIn(f'{count} consumidores',text)
            self.assertIn('não executa novos testes',text)
            self.assertNotIn('três cenários preparados',text)
            self.p.check('#showRecordedTests')
            self.assertEqual(text,self.p.evaluate('EGInvestigation.report()'))
        self.switch('aurora')
        text=self.p.evaluate('EGInvestigation.report()')
        self.assertIn('Grupo Aurora: organização e dados fictícios',text)
        self.assertIn('três cenários preparados',text)
        self.assertNotIn('consumidores de Aurora Validação',text)
    def test_14_notes_isolated_between_l7_captures(self):
        run_refinement.execute(self.root/'reference-b');build(self.root/'reference-b',self.root/'view-b')
        self.open();self.review();self.p.click('[data-detail="l7-c06"]')
        self.p.fill('#reviewNote','SOMENTE_CAPTURA_A');self.p.click('#closeDetail')
        first=self.p.evaluate('data.dataset_version')
        response=self.p.goto(self.url+'/view-b/index.html?source=review')
        self.assertEqual(200,response.status);self.ready()
        self.assertNotEqual(first,self.p.evaluate('data.dataset_version'))
        self.review();self.p.click('[data-detail="l7-c06"]')
        self.assertEqual('',self.p.locator('#reviewNote').input_value())
        self.open();self.review();self.p.click('[data-detail="l7-c06"]')
        self.assertEqual('SOMENTE_CAPTURA_A',self.p.locator('#reviewNote').input_value())

if __name__=='__main__':unittest.main()

"""DOM-only Chromium checks: no claim of hosted navigation or persistent storage."""
from pathlib import Path
import tempfile
import unittest
from playwright.sync_api import sync_playwright
import lab
from build_view import build

class ViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.root=Path(cls.temp.name)
        lab.execute(cls.root/'capture');build(cls.root/'capture/run.json',cls.root/'view')
        cls.html=(cls.root/'view/EvidentGraph_L2.html').read_text()
        cls.pw=sync_playwright().start();cls.browser=cls.pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    @classmethod
    def tearDownClass(cls):cls.browser.close();cls.pw.stop();cls.temp.cleanup()
    def setUp(self):
        self.page=self.browser.new_page(viewport={'width':1920,'height':1080});self.page.set_default_timeout(4000)
        self.errors=[];self.page.on('pageerror',lambda e:self.errors.append(str(e)))
        self.page.set_content(self.html);self.page.wait_for_selector('[data-node]')
    def tearDown(self):self.assertEqual([],self.errors);self.page.close()
    def test_graph_preserved(self):self.assertEqual(5,self.page.locator('[data-node]').count());self.assertEqual(4,self.page.locator('[data-edge]').count())
    def test_provenance_visible(self):self.assertIn('Captura de execução local',self.page.locator('#captureNotice').inner_text());self.assertEqual('lab',self.page.locator('#workspaceSource').input_value())
    def test_list_same_recorte(self):
        ids=self.page.locator('[data-node]').evaluate_all('(xs)=>xs.map(x=>x.dataset.node).sort()');self.page.click('#graphToList')
        self.assertEqual(ids,self.page.locator('[data-explore-row]').evaluate_all('(xs)=>xs.map(x=>x.dataset.exploreRow).sort()'))
    def test_contract_and_failure_separate(self):
        self.page.click('#graphReview');s=self.page.locator('#consumerRows').inner_text();self.assertIn('Falhou no teste executado',s);self.assertIn('Passou no teste executado',s);self.assertIn('Não verificado',s)
    def test_consumer_trace_details(self):
        self.page.click('#graphReview');self.page.click('[data-detail="l1-pedidos"]');s=self.page.locator('.lab-result').inner_text();self.assertIn('ANTES · v1',s);self.assertIn('DEPOIS · v2',s);self.assertIn('FAIL',s)
    def test_filter_and_export(self):
        self.page.click('#graphReview');self.page.fill('#search','Exportador');r=self.page.evaluate('report()');self.assertIn('Consumidores exportados: 1 de 3',r);self.assertNotIn('| Cliente de pedidos |',r);self.assertIn('Uso anterior não confirmado',r)
    def test_user_check_does_not_erase_failed_test(self):
        self.page.click('#graphReview');self.page.check('[data-check="l1-pedidos"]');r=self.page.evaluate('report()');self.assertIn('Falhou no teste executado',r);self.assertIn('registrada; não altera o teste',r)
    def test_note_escaping(self):
        self.page.click('#graphReview');self.page.click('[data-detail="l1-pedidos"]');self.page.fill('#reviewNote','<img src=x onerror="window.BAD=1">');self.page.click('#closeDetail');self.page.click('[data-detail="l1-pedidos"]');self.assertIsNone(self.page.evaluate('window.BAD'));self.assertIn('<img',self.page.locator('#reviewNote').input_value())
    def test_context_export_origin(self):
        r=self.page.evaluate('EGInvestigation.report()');self.assertIn('Aurora Lab',r);self.assertIn('Fonte SHA-256:',r);self.assertNotIn('Grupo Aurora: organização',r)
    def test_about_limits(self):
        self.page.click('#aboutBtn');s=self.page.locator('#aboutDialog').inner_text();self.assertIn('captura histórica',s);self.assertIn('não autentica',s);self.assertIn('não é benchmark',self.page.evaluate('report()'))
    def test_browser_export_download(self):
        self.page.click('#graphReview')
        with self.page.expect_download() as info:self.page.click('#exportBtn')
        text=Path(info.value.path()).read_text();self.assertIn('SHA-256 do run.json',text);self.assertIn('Falhou',text)
    def test_no_duplicate_test_blocks_after_filters(self):
        self.page.click('#graphReview');self.page.fill('#search','portal');self.page.fill('#search','');self.assertEqual(3,self.page.locator('.lab-test').count())
    def test_narrow_layout(self):
        self.page.set_viewport_size({'width':1366,'height':768});self.assertTrue(self.page.locator('#graphReview').is_visible());self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),1366)
    def test_aurora_boot_remains_synthetic_and_large(self):
        # Separate initialization: actual URL switching/reload is NOT exercised by this test.
        p=self.browser.new_page();p.set_content(self.html.replace('location.hash === "#aurora"','true'));p.wait_for_selector('[data-node]')
        self.assertEqual('aurora',p.locator('#workspaceSource').input_value());self.assertTrue(p.locator('#captureNotice').is_hidden());self.assertEqual(27,p.locator('[data-node]').count());p.select_option('#graphScope','all');self.assertEqual(240,p.locator('[data-node]').count());self.assertEqual(512,p.locator('[data-edge]').count());self.assertTrue(p.evaluate('data.synthetic'));p.close()

if __name__=='__main__':unittest.main()

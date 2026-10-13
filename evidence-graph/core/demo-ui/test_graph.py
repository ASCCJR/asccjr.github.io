"""Local DOM/Chromium regression tests. No HTTP/file navigation claims."""
import re, unittest
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]; P=ROOT/'preview-m2'
def html_bundle():
    html=(P/'index.html').read_text()
    for name in ['styles.css','lineage.css']:
        html=html.replace('<link rel="stylesheet" href="'+name+'">','<style>'+(P/name).read_text()+'</style>')
    html=re.sub(r'<script src="[^"]+" defer></script>','',html)
    return html.replace('</body>','<script>'+'\n'.join((P/n).read_text() for n in ['data.js','app.js','lineage.js'])+'</script></body>')
class GraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw=sync_playwright().start();cls.browser=cls.pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    @classmethod
    def tearDownClass(cls):cls.browser.close();cls.pw.stop()
    def setUp(self):
        self.page=self.browser.new_page(viewport={'width':1920,'height':1080});self.errors=[]
        self.page.on('pageerror',lambda e:self.errors.append(str(e)))
        self.page.set_content(html_bundle());self.page.wait_for_selector('#lineageView:not([hidden]) [data-node]')
    def tearDown(self):self.assertEqual([],self.errors);self.page.close()
    def test_01_graph_first(self):
        self.assertTrue(self.page.locator('#lineageView').is_visible());self.assertFalse(self.page.locator('#analysisView').is_visible());self.assertEqual(27,self.page.locator('[data-node]').count())
    def test_02_full_enterprise(self):
        self.page.select_option('#graphScope','all');self.assertEqual(240,self.page.locator('[data-node]').count());self.assertEqual(512,self.page.locator('[data-edge]').count())
    def test_03_scope_counts(self):
        self.assertIn('27 ativos · 46 relações',self.page.locator('#graphVisibleCount').inner_text())
    def test_04_names(self):
        text=self.page.locator('body').inner_text();self.assertIn('Grupo Aurora',text);self.assertNotIn('Demo',text);self.assertNotIn('prod-demo',text)
    def test_05_about(self):
        self.page.click('#aboutBtn');self.assertIn('fictícia',self.page.locator('#aboutDialog').inner_text());self.assertIn('sintéticos',self.page.locator('#aboutDialog').inner_text())
    def test_06_node_selection(self):
        self.page.locator('[data-node="agent-atendimento"]').click();self.assertIn('Impacto possível',self.page.locator('#graphInspector').inner_text());self.assertEqual(2,self.page.locator('.edge-selected').count())
    def test_07_detail(self):
        self.page.locator('[data-node="agent-atendimento"]').click();self.page.click('[data-inspect="agent-atendimento"]');self.assertTrue(self.page.locator('#detailDialog').is_visible());self.assertIn('Agente de atendimento',self.page.locator('#detailTitle').inner_text())
    def test_08_zoom(self):
        v=self.page.locator('#graphZoomLabel').inner_text();self.page.click('#graphZoomIn');self.assertNotEqual(v,self.page.locator('#graphZoomLabel').inner_text());self.page.click('#graphFit');self.assertEqual(v,self.page.locator('#graphZoomLabel').inner_text())
    def test_09_search(self):
        self.page.fill('#graphSearch','tbl-previsao-saida');self.page.click('#graphFind');self.assertIn('Resultados de previsão',self.page.locator('#graphFocusName').inner_text())
    def test_10_scenario_synced(self):
        self.page.select_option('#graphChange','CHG-002');self.page.click('#graphToList');self.assertEqual('CHG-002',self.page.locator('#changeSelect').input_value());self.assertEqual(2,self.page.locator('#consumerRows tr').count())
    def test_11_list_kept(self):
        self.page.click('#graphToList');self.assertEqual(4,self.page.locator('#consumerRows tr').count());self.page.fill('#search','Agente');self.assertEqual(1,self.page.locator('#consumerRows tr').count());self.page.click('#analysisToGraph');self.page.click('#graphToList');self.assertEqual('Agente',self.page.locator('#search').input_value());self.assertEqual(1,self.page.locator('#consumerRows tr').count())
    def test_12_analysis_paths(self):
        self.page.select_option('#graphScope','impact');self.assertEqual(6,self.page.locator('[data-node]').count());self.assertEqual(5,self.page.locator('[data-edge]').count())
    def test_13_domain(self):
        self.page.select_option('#graphScope','all');self.page.select_option('#graphDomain','dados');self.assertGreater(self.page.locator('[data-node]').count(),20);self.assertLess(self.page.locator('[data-node]').count(),240)
    def test_14_inventory_to_graph(self):
        self.page.click('[data-view="inventory"]');self.page.fill('#inventorySearch','api-legado');self.page.click('[data-asset="api-legado"]');self.page.click('[data-map="api-legado"]');self.assertIn('API de arquivo legado',self.page.locator('#graphFocusName').inner_text())
    def test_15_expand(self):
        n=self.page.locator('[data-node]').count();self.page.locator('[data-node="agent-atendimento"]').click();self.page.click('[data-expand="agent-atendimento"]');self.assertGreaterEqual(self.page.locator('[data-node]').count(),n)
    def test_16_export(self):
        self.page.click('#graphToList');self.page.fill('#search','Agente');content=self.page.evaluate('report()');self.assertIn('1 de 4',content);self.assertIn('sintéticos',content);self.assertIn('Agente de atendimento',content)
    def test_17_keyboard_select(self):
        node=self.page.locator('[data-node="svc-comercial-pedidos"]');node.focus();self.page.keyboard.press('Enter');self.assertIn('Incompatibilidade de contrato',self.page.locator('#graphInspector').inner_text())
    def test_18_narrow_layout(self):
        self.page.set_viewport_size({'width':1366,'height':768});self.page.wait_for_timeout(80);self.assertTrue(self.page.locator('#lineageView').is_visible());self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),1366)
    def test_19_unknown_stays_unknown(self):
        self.page.select_option('#graphChange','CHG-003');self.page.click('#graphToList');self.assertIn('Inconclusivo',self.page.locator('#consumerRows').inner_text())
    def test_20_edge_provenance(self):
        key=self.page.locator('[data-edge]').first.get_attribute('data-edge');self.page.locator('[data-edge]').first.dispatch_event('click');self.assertTrue(self.page.locator('#detailDialog').is_visible());self.assertIn('Evidências de origem',self.page.locator('#detailBody').inner_text())
if __name__=='__main__':unittest.main(verbosity=2)

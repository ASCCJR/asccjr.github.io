"""M3 Chromium tests. set_content because managed browser blocks navigation."""
from pathlib import Path
import re, unittest
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]; P=ROOT/'preview-m2'
def html_bundle():
    html=(P/'index.html').read_text()
    for name in ['styles.css','lineage.css','investigation.css']:
        html=html.replace('<link rel="stylesheet" href="'+name+'">','<style>'+(P/name).read_text()+'</style>')
    html=re.sub(r'<script src="[^"]+" defer></script>','',html)
    return html.replace('</body>','<script>'+'\n'.join((P/n).read_text() for n in ['data.js','app.js','lineage.js','exploration.js','investigation.js'])+'</script></body>')
class NavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw=sync_playwright().start();cls.browser=cls.pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    @classmethod
    def tearDownClass(cls):cls.browser.close();cls.pw.stop()
    def setUp(self):
        self.page=self.browser.new_page(viewport={'width':1920,'height':1080});self.errors=[];self.page.set_default_timeout(3500)
        self.page.on('pageerror',lambda e:self.errors.append(str(e)))
        self.page.set_content(html_bundle());self.page.wait_for_selector('[data-node]')
    def tearDown(self):self.assertEqual([],self.errors);self.page.close()
    def test_initial(self):
        self.assertEqual(27,self.page.locator('[data-node]').count());self.assertEqual(3,self.page.locator('[data-investigate]').count())
    def test_direct_consumers(self):
        self.page.click('[data-investigate="downstream"]')
        self.assertIn('Consultar cliente',self.page.locator('#lineageSvg').text_content())
        self.assertEqual(5,self.page.locator('[data-node]').count())
    def test_indirect_consumers(self):
        self.page.click('[data-investigate="downstream"]');self.page.select_option('#investigationDepth','2')
        self.assertEqual(9,self.page.locator('[data-node]').count());self.assertEqual(1,self.page.locator('[data-node="agent-atendimento"]').count())
    def test_upstream_dashboard(self):
        self.page.fill('#graphSearch','dash-operacoes-portal');self.page.click('#graphFind');self.page.click('[data-investigate="upstream"]')
        self.assertEqual(1,self.page.locator('[data-node="tbl-previsao-saida"]').count())
    def test_process(self):
        self.page.click('[data-investigate="process"]');self.assertIn('Associação não comprova',self.page.locator('#investigationNote').inner_text())
        self.assertFalse(self.page.locator('#depthControl').is_visible())
    def test_tabs_same_ids(self):
        ids=self.page.locator('[data-node]').evaluate_all('(els)=>els.map(e=>e.dataset.node).sort()')
        self.page.click('#graphToList');listed=self.page.locator('[data-explore-row]').evaluate_all('(els)=>els.map(e=>e.dataset.exploreRow).sort()')
        self.assertEqual(ids,listed);self.page.click('#graphAsGraph');self.assertEqual(ids,self.page.locator('[data-node]').evaluate_all('(els)=>els.map(e=>e.dataset.node).sort()'))
    def test_list_selection(self):
        self.page.click('#graphToList');self.page.click('[data-select-asset="agent-atendimento"]');self.assertIn('Agente de atendimento',self.page.locator('#graphInspector').inner_text())
        self.page.click('#graphAsGraph');self.assertTrue(self.page.locator('[data-node="agent-atendimento"]').evaluate('n=>n.classList.contains("selected")'))
    def test_filtered_list(self):
        self.page.select_option('#graphScope','all');self.page.select_option('#graphDomain','dados');n=self.page.locator('[data-node]').count();self.page.click('#graphToList');self.assertEqual(n,self.page.locator('[data-explore-row]').count())
    def test_review_and_back(self):
        self.page.locator('[data-node="agent-atendimento"]').click();self.page.click('[data-review-selected="agent-atendimento"]');self.assertEqual(1,self.page.locator('#consumerRows tr').count());self.page.click('[data-return-graph="agent-atendimento"]');self.assertTrue(self.page.locator('[data-node="agent-atendimento"]').evaluate('n=>n.classList.contains("selected")'))
    def test_context_export(self):
        self.page.click('[data-investigate="downstream"]');s=self.page.evaluate('EGInvestigation.report()');self.assertIn('dados fictícios',s);self.assertIn('Ativos: 5',s)
        with self.page.expect_download() as d:self.page.click('#exportContext')
        self.assertEqual('EvidentGraph_investigacao.md',d.value.suggested_filename)
    def test_analysis_export_and_note(self):
        self.page.click('#graphReview');self.page.fill('#search','Agente');self.page.click('[data-detail="agent-atendimento"]');self.page.fill('[data-note="agent-atendimento"]','Verificar contrato antes de publicar.');self.page.click('#closeDetail');self.assertIn('Verificar contrato',self.page.evaluate('report()'));self.assertIn('1 de 4',self.page.evaluate('report()'))
    def test_unknown_unchanged(self):
        self.page.select_option('#graphChange','CHG-003');self.page.click('#graphReview');self.assertIn('Inconclusivo',self.page.locator('#consumerRows').inner_text())
    def test_full_graph(self):
        self.page.select_option('#graphScope','all');self.assertEqual(240,self.page.locator('[data-node]').count());self.assertEqual(512,self.page.locator('[data-edge]').count())
    def test_keyboard_actions(self):
        n=self.page.locator('[data-node="svc-comercial-pedidos"]');n.focus();self.page.keyboard.press('Enter');self.page.locator('[data-investigate="upstream"]').focus();self.page.keyboard.press('Enter');self.assertIn('De que depende?',self.page.locator('#investigationTitle').inner_text())
    def test_1366(self):
        self.page.set_viewport_size({'width':1366,'height':768});self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),1366)
    def test_semantic_queries_no_qa(self):
        self.page.click('[data-investigate="downstream"]');self.page.select_option('#investigationDepth','4');self.assertEqual(0,self.page.locator('[data-node="api-clientes-qa"]').count())
    def test_no_repeated_demo(self):
        self.assertNotIn('Demo',self.page.locator('body').inner_text());self.assertIn('Grupo Aurora',self.page.locator('body').inner_text())
    def test_zero_dependencies(self):
        self.page.fill('#graphSearch','api-clientes-qa');self.page.click('#graphFind');self.page.click('[data-investigate="downstream"]');self.assertEqual(1,self.page.locator('[data-node]').count());self.assertIn('Homologação',self.page.locator('#workspaceEnvironment').inner_text())
    def test_escape_details(self):
        self.page.locator('[data-node="agent-atendimento"]').click();self.page.click('[data-inspect="agent-atendimento"]');self.page.keyboard.press('Escape');self.assertFalse(self.page.locator('#detailDialog').is_visible())
    def test_depth_after_selection(self):
        self.page.click('[data-investigate="downstream"]');self.page.locator('[data-node="svc-comercial-pedidos"]').click();self.page.select_option('#investigationDepth','2');self.assertIn('GET /customers',self.page.locator('#investigationTitle').inner_text())
if __name__=='__main__':unittest.main()

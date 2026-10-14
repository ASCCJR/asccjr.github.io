"""M2 tests: Chromium DOM rendering with inline local files, no remote navigation.
Requires Playwright and a local Chromium executable. No production integrations.
"""
import base64
import gzip
import json
import os
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright
from build_preview import build, ROOT

UI = ROOT/'preview-m2'

class PreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle=build()
        cls.pw=sync_playwright().start()
        cls.browser=cls.pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
        cls.html=(UI/'index.html').read_text().replace('<link rel="stylesheet" href="styles.css">','<style>'+(UI/'styles.css').read_text()+'</style>').replace('<script src="data.js" defer></script><script src="app.js" defer></script>','')
    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.pw.stop()
    def setUp(self):
        self.context=self.browser.new_context(viewport={'width':1366,'height':768},accept_downloads=True)
        self.page=self.context.new_page();self.page.set_default_timeout(3000)
        self.errors=[];self.page.on('pageerror',lambda e:self.errors.append(str(e)))
        self.page.set_content(self.html)
        self.page.add_script_tag(content=(UI/'data.js').read_text())
        self.page.add_script_tag(content=(UI/'app.js').read_text())
        self.page.locator('#analysisResult').wait_for(state='visible')
    def tearDown(self):
        self.assertEqual(self.errors,[])
        self.context.close()
    def rows(self):return self.page.locator('#consumerRows tr').count()
    def scenario(self,cid):
        self.page.select_option('#changeSelect',cid);self.page.click('#openAnalysis')
    def test_01_initial_four_consumers(self):
        self.assertEqual(self.rows(),4)
        self.assertIn('Revisão necessária',self.page.inner_text('#conclusionTitle'))
    def test_02_other_scenarios(self):
        self.scenario('CHG-002');self.assertEqual(self.rows(),2)
        self.scenario('CHG-003');self.assertEqual(self.rows(),1)
        self.assertIn('faltam informações',self.page.inner_text('#conclusionTitle'))
    def test_03_pending_selection_hides_old_result(self):
        self.page.select_option('#changeSelect','CHG-002')
        self.assertFalse(self.page.locator('#analysisResult').is_visible())
        self.assertTrue(self.page.locator('#notAnalyzed').is_visible())
    def test_04_search_accent_insensitive(self):
        self.page.fill('#search','SERVICO DE PEDIDOS');self.assertEqual(self.rows(),1)
    def test_05_impact_chips_match_counts(self):
        for state in ['INCOMPATIBILITY','POSSIBLE','INCONCLUSIVE','NO_INCOMPATIBILITY']:
            self.page.click(f'[data-impact="{state}"]');self.assertEqual(self.rows(),1)
        self.page.click('[data-impact=""]');self.assertEqual(self.rows(),4)
    def test_06_owner_and_activity_intersection(self):
        self.page.select_option('#ownerFilter','team-financeiro');self.assertEqual(self.rows(),1)
        self.page.select_option('#activityFilter','OBSERVED');self.assertEqual(self.rows(),0)
        self.assertTrue(self.page.locator('#exportBtn').is_disabled())
    def test_07_clear_restores(self):
        self.page.fill('#search','zzzz');self.page.click('#clearFilters');self.assertEqual(self.rows(),4)
    def test_08_sort_toggle(self):
        self.page.click('#sortName');self.assertIn('Agente',self.page.locator('#consumerRows tr').first.inner_text())
        self.page.click('#sortName');self.assertIn('Serviço',self.page.locator('#consumerRows tr').first.inner_text())
    def test_09_drawer_evidence_and_focus(self):
        self.page.fill('#search','Agente');button=self.page.locator('[data-detail]').first;button.click()
        self.assertEqual(self.page.locator('#detailBody .path').count(),1)
        self.assertEqual(self.page.locator('#detailBody details.ev').count(),5)
        self.assertIn('não avaliada',self.page.inner_text('#detailBody'))
        self.page.keyboard.press('Escape');self.assertEqual(self.rows(),1)
        self.assertTrue(button.evaluate('(e)=>e===document.activeElement'))
    def test_10_check_and_note_stay_local(self):
        self.page.locator('[data-detail]').first.click()
        self.page.locator('#detailBody [data-check]').check();self.page.fill('#reviewNote','Rever com o responsável.');self.page.keyboard.press('Escape')
        self.assertTrue(self.page.locator('#consumerRows [data-check]').first.is_checked())
        self.page.locator('[data-detail]').first.click();self.assertEqual(self.page.input_value('#reviewNote'),'Rever com o responsável.')
    def test_11_export_filtered_markdown(self):
        self.page.fill('#search','Exportador')
        with self.page.expect_download() as dl:self.page.click('#exportBtn')
        text=Path(dl.value.path()).read_text()
        self.assertIn('1 de 4',text);self.assertIn('Exportador financeiro',text)
        self.assertNotIn('## Serviço de pedidos',text)
        self.assertIn('não avaliados',text)
    def test_12_inventory_and_pagination(self):
        self.page.click('[data-view="inventory"]')
        self.assertIn('240 de 240',self.page.inner_text('#inventoryCount'))
        self.assertEqual(self.page.locator('#inventoryRows tr').count(),15)
        self.page.click('#nextPage');self.assertEqual(self.page.inner_text('#pageNumber'),'2 / 16')
    def test_13_inventory_filters(self):
        self.page.click('[data-view="inventory"]');self.page.select_option('#kindFilter','agent')
        self.assertIn('8 de 240',self.page.inner_text('#inventoryCount'))
        self.page.fill('#inventorySearch','INVALID-ID');self.assertIn('Nenhum ativo',self.page.inner_text('#inventoryRows'))
    def test_14_inventory_analysis_link(self):
        self.page.click('[data-view="inventory"]');self.page.fill('#inventorySearch','api-clientes-v2')
        self.page.locator('[data-asset]').click();self.page.locator('[data-goto="CHG-001"]').click();self.assertEqual(self.rows(),4)
    def test_15_reference_results_unmodified(self):
        from build_preview import model
        d=model.make_dataset()
        self.assertEqual(self.bundle['results'],[model.analyze(d,c['id']) for c in d['changes']])
        packed=json.loads((UI/'data.js').read_text().split(' = ',1)[1].strip().rstrip(';'))
        self.assertEqual(json.loads(gzip.decompress(base64.b64decode(packed))),self.bundle)
    def test_16_no_external_requests(self):
        self.assertEqual(self.page.evaluate('performance.getEntriesByType("resource").length'),0)
    def test_17_narrow_layout_all_actions_accessible(self):
        self.page.set_viewport_size({'width':683,'height':384})
        self.assertTrue(self.page.locator('#exportBtn').is_visible())
        self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),683)
    def test_18_html_in_notes_not_executed(self):
        self.page.locator('[data-detail]').first.click();self.page.fill('#reviewNote','<img src=x onerror="window.BAD=true">');self.page.keyboard.press('Escape');self.page.locator('[data-detail]').first.click()
        self.assertIsNone(self.page.evaluate('window.BAD'))
        self.assertIn('<img',self.page.input_value('#reviewNote'))

if __name__=='__main__':unittest.main(verbosity=2)

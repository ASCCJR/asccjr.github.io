"""Opt-in browser checks for an actual served URL; no set_content fallback.

Set EG_PREVIEW_URL to the local HTTP preview or reviewed Sites URL.
Requires Playwright and Chromium. Tests use isolated browser contexts.
"""
import os
import shutil
import unittest
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

URL = os.environ.get("EG_PREVIEW_URL", "")


@unittest.skipUnless(URL, "Set EG_PREVIEW_URL to an HTTP(S) URL")
class HostedPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if urlsplit(URL).scheme not in ("http", "https"):
            raise ValueError("EG_PREVIEW_URL must be HTTP(S)")
        cls.pw = sync_playwright().start()
        executable = os.environ.get("CHROMIUM_PATH") or shutil.which("chromium")
        options = {"executable_path": executable} if executable else {}
        cls.browser = cls.pw.chromium.launch(**options)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.context = self.browser.new_context(viewport={"width": 1366, "height": 768})
        self.addCleanup(self.context.close)
        self.page = self.context.new_page()
        self.errors = []
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        self.page.set_default_timeout(5000)
        response = self.page.goto(URL, wait_until="networkidle", timeout=15000)
        self.assertTrue(response and response.ok)
        self.page.wait_for_selector("[data-node]")

    def tearDown(self):
        self.assertEqual([], self.errors)

    def open_agent_note(self):
        self.page.click("#graphReview")
        self.page.fill("#search", "Agente")
        self.page.click('[data-detail="agent-atendimento"]')

    def test_start_and_full_catalog(self):
        self.assertIn("Grupo Aurora", self.page.locator("body").inner_text())
        self.assertEqual(27, self.page.locator("[data-node]").count())
        self.page.select_option("#graphScope", "all")
        self.assertEqual(240, self.page.locator("[data-node]").count())
        self.assertEqual(512, self.page.locator("[data-edge]").count())

    def test_graph_list_share_ids(self):
        self.page.click('[data-investigate="downstream"]')
        self.page.select_option("#investigationDepth", "2")
        ids = self.page.locator("[data-node]").evaluate_all("es=>es.map(e=>e.dataset.node).sort()")
        self.page.click("#graphToList")
        listed = self.page.locator("[data-explore-row]").evaluate_all("es=>es.map(e=>e.dataset.exploreRow).sort()")
        self.assertEqual(ids, listed)

    def test_review_returns_to_selected_asset(self):
        self.page.locator('[data-node="agent-atendimento"]').click()
        self.page.click('[data-review-selected="agent-atendimento"]')
        self.assertEqual(1, self.page.locator("#consumerRows tr").count())
        self.page.click('[data-return-graph="agent-atendimento"]')
        self.assertTrue(self.page.locator('[data-node="agent-atendimento"]').evaluate('n=>n.classList.contains("selected")'))

    def test_note_survives_reload_same_origin(self):
        self.open_agent_note()
        self.page.fill('[data-note="agent-atendimento"]', "Teste local de persistência; sem dados pessoais.")
        self.page.click("#closeDetail")
        self.page.reload(wait_until="networkidle")
        self.page.wait_for_selector("[data-node]")
        self.open_agent_note()
        self.assertEqual("Teste local de persistência; sem dados pessoais.", self.page.locator('[data-note="agent-atendimento"]').input_value())

    def test_filtered_report_download(self):
        self.open_agent_note()
        self.page.fill('[data-note="agent-atendimento"]', "Revisar contrato sintético.")
        self.page.click("#closeDetail")
        with self.page.expect_download() as event:
            self.page.click("#exportBtn")
        download = event.value
        self.assertTrue(download.suggested_filename.endswith(".md"))
        from pathlib import Path
        text = Path(download.path()).read_text(encoding="utf-8")
        self.assertIn("Revisar contrato sintético.", text)
        self.assertIn("1 de 4", text)

    def test_legacy_case_remains_inconclusive(self):
        self.page.select_option("#graphChange", "CHG-003")
        self.page.click("#graphReview")
        self.assertIn("Inconclusivo", self.page.locator("#consumerRows").inner_text())


if __name__ == "__main__":
    unittest.main()

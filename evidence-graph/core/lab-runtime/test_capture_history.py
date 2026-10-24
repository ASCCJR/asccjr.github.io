"""L4 archive tests. Reference snapshots use real HTTP; mocks only exercise error branches."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import capture_history as h


class CaptureHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work = tempfile.TemporaryDirectory()
        cls.archive = Path(cls.work.name) / 'reference'
        cls.first = h.capture(cls.archive, 'capture-a')
        cls.hashes = h.inventory(cls.archive / 'capture-a')
        cls.second = h.capture(cls.archive, 'capture-b')

    @classmethod
    def tearDownClass(cls):
        cls.work.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def copied(self):
        return Path(shutil.copytree(self.archive, self.root / 'copied'))

    def test_01_real_captures_distinct_and_prior_preserved(self):
        self.assertNotEqual(self.first['source_sha256'], self.second['source_sha256'])
        self.assertEqual(self.hashes, h.inventory(self.archive / 'capture-a'))
        self.assertEqual(12, self.first['summary']['spans'])
        self.assertEqual(4, self.first['summary']['traces'])

    def test_02_view_uses_exact_capture(self):
        for key in ['capture-a', 'capture-b']:
            d, _, _ = h.load_capture(self.archive, key)
            m = json.loads((self.archive/key/'view/manifest.json').read_text())
            self.assertEqual(d['source_sha256'], m['source_run_sha256'])
            self.assertEqual(240, m['aurora_assets'])
            self.assertTrue((self.archive/key/'view/EvidentGraph_L2.html').is_file())

    def test_03_existing_id_refused_without_mutation(self):
        with self.assertRaises(FileExistsError):
            h.capture(self.archive, 'capture-a')
        self.assertEqual(self.hashes, h.inventory(self.archive / 'capture-a'))

    def test_04_invalid_ids(self):
        for value in ['../outside', '', '.hidden', 'a/b', 'a\\b', 'a'*97]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                h.capture(self.root/'invalid', value)
        self.assertFalse((self.root/'invalid').exists())

    def test_05_foreign_directory_preserved(self):
        path = self.root/'foreign'
        path.mkdir()
        (path/'notes.md').write_text('preserve')
        with self.assertRaises(ValueError):
            h.capture(path, 'x')
        self.assertEqual(['notes.md'], [f.name for f in path.iterdir()])

    def test_06_public_sources_not_output(self):
        with self.assertRaises(ValueError):
            h.permitted_output(h.build_view.PREVIEW/'captures')

    def test_07_symlink_output_refused(self):
        (self.root/'alias').symlink_to(self.archive, target_is_directory=True)
        with self.assertRaises(ValueError):
            h.capture(self.root/'alias', 'new')

    def test_08_partial_capture_is_not_success(self):
        root = h.init_archive(self.root/'partial')
        (root/'unfinished').mkdir()
        self.assertEqual([{'id':'unfinished','status':'incomplete'}], h.history(root))

    def test_09_source_tamper_rejected(self):
        root = self.copied()
        p = root/'capture-a/evidence/run.json'
        p.write_text(p.read_text()+' ')
        with self.assertRaisesRegex(ValueError, 'integrity'):
            h.load_capture(root, 'capture-a')

    def test_10_view_tamper_rejected(self):
        root = self.copied()
        (root/'capture-a/view/index.html').write_text('changed')
        with self.assertRaisesRegex(ValueError, 'integrity'):
            h.load_capture(root, 'capture-a')

    def test_11_missing_artifact_rejected(self):
        root = self.copied()
        (root/'capture-a/evidence/spans.json').unlink()
        with self.assertRaisesRegex(ValueError, 'integrity'):
            h.load_capture(root, 'capture-a')

    def test_12_extra_artifact_rejected(self):
        root = self.copied()
        (root/'capture-a/extra.txt').write_text('unexpected')
        with self.assertRaisesRegex(ValueError, 'integrity'):
            h.load_capture(root, 'capture-a')

    def test_13_summary_is_recomputed(self):
        root = self.copied()
        p = root/'capture-a/capture.json'
        d = json.loads(p.read_text())
        d['summary']['consumers'][0]['contract'] = 'SAFE'
        p.write_text(json.dumps(d))
        with self.assertRaisesRegex(ValueError, 'metadata'):
            h.load_capture(root, 'capture-a')

    def test_14_equivalent_runs_have_no_invented_business_delta(self):
        d = h.compare(self.archive, 'capture-a', 'capture-b')
        self.assertEqual(0, d['changed_consumers'])
        self.assertEqual([], d['openapi_changed'])
        self.assertEqual([12, 12], d['capture_spans'])
        self.assertFalse(d['consumer_declarations_changed'])

    def test_15_same_capture_not_independent(self):
        with self.assertRaisesRegex(ValueError, 'same capture'):
            h.compare(self.archive, 'capture-a', 'capture-a')

    def test_16_reversed_captures_rejected(self):
        with self.assertRaisesRegex(ValueError, 'reverse'):
            h.compare(self.archive, 'capture-b', 'capture-a')

    def test_17_incompatible_context_rejected(self):
        a = h.load_capture(self.archive, 'capture-a')
        b = copy.deepcopy(h.load_capture(self.archive, 'capture-b'))
        b[0]['context']['environment'] = 'different'
        with patch.object(h, 'load_capture', side_effect=[a,b]):
            with self.assertRaisesRegex(ValueError, 'Incompatible'):
                h.compare(self.archive, 'capture-a', 'capture-b')

    def test_18_lost_evidence_is_unknown_not_success(self):
        a = h.load_capture(self.archive, 'capture-a')
        b = copy.deepcopy(h.load_capture(self.archive, 'capture-b'))
        b[1]['spans'] = []
        changed = h.lab.analyze(b[1])
        with patch.object(h, 'load_capture', side_effect=[a,(b[0],b[1],changed)]):
            diff = h.compare(self.archive, 'capture-a', 'capture-b')
        pedidos = next(r for r in diff['consumers'] if r['consumer']=='pedidos')
        self.assertEqual('UNKNOWN', pedidos['after']['usage_before_change'])
        self.assertEqual('NOT_VERIFIED', pedidos['after']['regression_after_change'])
        self.assertEqual('INCOMPATIBILITY', pedidos['after']['contract'])

    def test_19_missing_commit_marker_not_loaded(self):
        root = self.copied()
        (root/'capture-a/capture.json').unlink()
        with self.assertRaises(FileNotFoundError):
            h.load_capture(root, 'capture-a')

    def test_20_execution_failure_preserves_partial_not_success(self):
        root = self.root/'failure'
        with patch.object(h.lab, 'execute', side_effect=RuntimeError('injected failure')):
            with self.assertRaisesRegex(RuntimeError, 'injected'):
                h.capture(root, 'failed')
        self.assertTrue((root/'failed/INCOMPLETE.txt').exists())
        self.assertFalse((root/'failed/capture.json').exists())
        self.assertEqual('incomplete', h.history(root)[0]['status'])

    def test_21_notes_and_results_are_not_authenticated_by_checksum(self):
        diff = h.compare(self.archive, 'capture-a', 'capture-b')
        text = h.comparison_markdown(diff)
        self.assertIn('não autenticam', text)
        self.assertIn('NOT_VERIFIED', text)
        self.assertIn('FAIL_OBSERVED_IN_LAB', text)
        self.assertIn('IAM não avaliado', text)

    def test_22_different_toolchain_rejected(self):
        root = self.copied()
        p = root/'capture-a/capture.json'
        d = json.loads(p.read_text())
        d['toolchain_sha256']['lab.py'] = 'changed'
        p.write_text(json.dumps(d))
        with self.assertRaisesRegex(ValueError, 'Toolchain'):
            h.load_capture(root, 'capture-a')

    def test_23_invalid_manifest_path_rejected(self):
        root = self.copied()
        p = root/'capture-a/capture.json'
        d = json.loads(p.read_text())
        d['files_sha256']['../other'] = 'bad'
        p.write_text(json.dumps(d))
        with self.assertRaisesRegex(ValueError, 'manifest path'):
            h.load_capture(root, 'capture-a')

    def test_24_history_read_only(self):
        before = h.inventory(self.archive)
        self.assertEqual(2, len(h.history(self.archive)))
        self.assertEqual(before, h.inventory(self.archive))


if __name__ == '__main__':
    unittest.main()

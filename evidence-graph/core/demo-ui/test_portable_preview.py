"""Regression tests for packaging; no network or Sites account required."""
from pathlib import Path
import hashlib
import json
import shutil
import tempfile
import unittest
from prepare_portable_preview import FILES, SOURCE, inspect, prepare


class PortablePreviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        shutil.copytree(SOURCE, self.source)

    def test_manifest_and_counts(self):
        report = inspect(self.source)
        self.assertEqual(240, report["counts"]["assets"])
        self.assertEqual(512, report["counts"]["relations_in_preview"])
        self.assertEqual(3, report["counts"]["scenarios"])

    def test_copy_preserves_every_source_byte(self):
        before = {n: (self.source/n).read_bytes() for n in FILES}
        out = self.root / "site"
        prepare(self.source, out)
        for name in FILES:
            self.assertEqual(before[name], (out/name).read_bytes())
            self.assertEqual(before[name], (self.source/name).read_bytes())

    def test_no_claim_of_sites_deployment(self):
        report = prepare(self.source, self.root / "site")
        self.assertFalse(report["sites_project_created"])
        self.assertFalse(report["sites_version_saved"])
        self.assertFalse(report["sites_deployment_performed"])

    def test_unlisted_files_are_not_published(self):
        (self.source/"private-notes.txt").write_text("TEST FIXTURE ONLY")
        (self.source/".env").write_text("TEST FIXTURE ONLY")
        out = self.root / "site"
        prepare(self.source, out)
        self.assertEqual(set(FILES) | {"portability-report.json"}, {p.name for p in out.iterdir()})

    def test_refuses_existing_directory(self):
        out = self.root / "site"
        out.mkdir()
        (out/"keep.txt").write_text("keep")
        with self.assertRaises(FileExistsError): prepare(self.source, out)
        self.assertEqual("keep", (out/"keep.txt").read_text())

    def test_refuses_output_inside_source(self):
        with self.assertRaises(ValueError): prepare(self.source, self.source / "site")

    def test_missing_asset_rejected(self):
        (self.source/"lineage.js").unlink()
        with self.assertRaises(ValueError): inspect(self.source)

    def test_symlink_rejected(self):
        f = self.source/"styles.css"
        target = self.root/"original.css"
        f.rename(target)
        f.symlink_to(target)
        with self.assertRaises(ValueError): inspect(self.source)

    def test_external_entrypoint_dependency_rejected(self):
        f = self.source/"index.html"
        f.write_text(f.read_text().replace('src="app.js"', 'src="https://example.invalid/app.js"'))
        with self.assertRaises(ValueError): inspect(self.source)

    def test_absolute_dependency_rejected(self):
        f = self.source/"index.html"
        f.write_text(f.read_text().replace('src="app.js"', 'src="/app.js"'))
        with self.assertRaises(ValueError): inspect(self.source)

    def test_changed_manifest_rejected(self):
        f = self.source/"manifest.json"
        m = json.loads(f.read_text()); m["assets"] = 999
        f.write_text(json.dumps(m))
        with self.assertRaises(ValueError): inspect(self.source)

    def test_corrupt_hash_rejected(self):
        f = self.source/"manifest.json"
        m = json.loads(f.read_text()); m["bundle_sha256"] = "0" * 64
        f.write_text(json.dumps(m))
        with self.assertRaises(ValueError): inspect(self.source)

    def test_deterministic_reports(self):
        a,b = self.root/"a", self.root/"b"
        prepare(self.source, a); prepare(self.source, b)
        self.assertEqual((a/"portability-report.json").read_bytes(), (b/"portability-report.json").read_bytes())


if __name__ == "__main__":
    unittest.main()

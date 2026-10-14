"""Package the existing M3 static UI without changing source files or deploying.

Standard library only. This verifies a portable static bundle, not Sites hosting.
"""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "preview-m2"
FILES = (
    "index.html", "styles.css", "lineage.css", "investigation.css",
    "data.js", "app.js", "lineage.js", "exploration.js", "investigation.js",
    "manifest.json",
)


class AssetReferences(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.assets: list[str] = []
        self.unsafe: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == "base":
            self.unsafe.append("base element changes relative URL resolution")
        if tag == "script" and a.get("src"):
            self.assets.append(a["src"])
        if tag == "link" and a.get("rel") == "stylesheet" and a.get("href"):
            self.assets.append(a["href"])


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def inspect(source: Path) -> dict:
    """Validate the prepared M3 bundle, its relative entrypoint and manifest."""
    source = source.resolve()
    for name in FILES:
        item = source / name
        if not item.is_file() or item.is_symlink():
            raise ValueError(f"Missing or symlinked asset: {name}")
    refs = AssetReferences()
    refs.feed((source / "index.html").read_text(encoding="utf-8"))
    if refs.unsafe:
        raise ValueError("; ".join(refs.unsafe))
    for ref in refs.assets:
        url = urlsplit(ref)
        if url.scheme or url.netloc or url.path.startswith("/"):
            raise ValueError(f"Non-relative entrypoint dependency: {ref}")
        if url.path not in FILES:
            raise ValueError(f"Dependency not in the static allowlist: {ref}")

    # Do not execute JavaScript when reading the data envelope.
    envelope = (source / "data.js").read_text(encoding="utf-8")
    match = re.search(r'window\.EG_PACKED\s*=\s*("[A-Za-z0-9+/=]+")\s*;', envelope)
    if not match:
        raise ValueError("Missing EG_PACKED data envelope")
    raw = gzip.decompress(base64.b64decode(json.loads(match.group(1)), validate=True))
    data = json.loads(raw)
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    if data.get("synthetic") is not True:
        raise ValueError("Only the synthetic dataset may be packaged")
    if sha256(raw) != manifest.get("bundle_sha256"):
        raise ValueError("Dataset hash differs from manifest")
    checks = {
        "assets": len(data["assets"]), "scenarios": len(data["results"]),
        "relations_in_preview": len(data["relations"]),
        "evidence_in_preview": len(data["evidence"]),
    }
    for key, value in checks.items():
        if manifest.get(key) != value:
            raise ValueError(f"Manifest count differs: {key}")
    return {
        "status": "static_bundle_verified_not_sites_validated",
        "dataset_version": data["dataset_version"], "counts": checks,
        "bundle_sha256": sha256(raw),
        "files": {name: sha256((source / name).read_bytes()) for name in FILES},
        "runtime": "browser_only",
        "browser_requirements": ["DecompressionStream(gzip)", "HTMLDialogElement", "SVG", "Blob downloads"],
        "storage": "localStorage in the current browser origin; no cross-origin migration",
        "sites_project_created": False, "sites_version_saved": False,
        "sites_deployment_performed": False,
    }


def prepare(source: Path, output: Path) -> dict:
    """Write a new directory only, copying an explicit allowlist byte-for-byte."""
    source, output = source.resolve(), output.resolve()
    if output == source or source in output.parents or output in source.parents:
        raise ValueError("Output must not overlap the source directory")
    if output.exists():
        raise FileExistsError("Output exists; choose a new directory (no overwrite)")
    report = inspect(source)
    output.mkdir(parents=True)
    for name in FILES:
        shutil.copyfile(source / name, output / name)
        if sha256((output / name).read_bytes()) != report["files"][name]:
            raise ValueError(f"Copy integrity failure: {name}")
    (output / "portability-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--out", type=Path, help="New directory; existing directories are never overwritten")
    parser.add_argument("--check", action="store_true", help="Check the source without writing")
    args = parser.parse_args()
    if not args.check and not args.out:
        parser.error("Choose --check or --out NEW_DIRECTORY")
    try:
        result = inspect(args.source) if args.check else prepare(args.source, args.out)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"ERROR: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

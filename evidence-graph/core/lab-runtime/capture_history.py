"""L4: run, seal and compare local L1 captures without overwriting history.

No network beyond lab.execute's loopback API. No UI edits, git push or deployment.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import uuid
from typing import Any
import lab
import adapt_run
import build_view

HERE = Path(__file__).resolve().parent
ARCHIVE_SCHEMA = 'evidentgraph-history-1'
CAPTURE_SCHEMA = 'evidentgraph-capture-1'
NAME = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,95}')


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def write_new(path: Path, value: Any) -> None:
    with path.open('x', encoding='utf-8') as handle:
        handle.write(lab.dump(value))


def permitted_output(path: Path) -> Path:
    path = path.absolute()
    if any(p.is_symlink() for p in [path, *path.parents]):
        raise ValueError('Output paths must not contain symlinks')
    path = path.resolve()
    project = HERE.parents[1]
    if path.is_relative_to(project) and not path.is_relative_to(HERE / 'runs'):
        raise ValueError('Inside evidence-graph, outputs must be under lab-runtime/runs')
    return path


def init_archive(path: Path) -> Path:
    path = permitted_output(path)
    marker = path / 'archive.json'
    if path.exists() and not marker.exists() and any(path.iterdir()):
        raise ValueError('Refusing to use an unrecognized nonempty archive')
    path.mkdir(parents=True, exist_ok=True)
    expected = {'schema': ARCHIVE_SCHEMA, 'kind': 'local_lab_only'}
    if not marker.exists():
        try:
            write_new(marker, expected)
        except FileExistsError:  # Another capture initialized the same archive.
            pass
    if marker.is_symlink() or json.loads(marker.read_text()) != expected:
        raise ValueError('Unrecognized archive marker')
    return path


def toolchain() -> dict[str, str]:
    files = ['lab.py', 'adapt_run.py', 'build_view.py', 'lab_view.js', 'capture_history.py']
    return {name: sha((HERE / name).read_bytes()) for name in files}


def inventory(path: Path) -> dict[str, str]:
    result = {}
    for entry in sorted(path.rglob('*')):
        if entry.is_symlink():
            raise ValueError('Symlinks are not allowed in captures')
        if entry.is_file() and entry != path / 'capture.json':
            result[entry.relative_to(path).as_posix()] = sha(entry.read_bytes())
    return result


def context(run: dict) -> dict:
    return {'schema': run['schema'], 'transport': run['transport'],
            'environment': 'loopback-lab', 'route': lab.ROUTE,
            'versions': sorted(run['openapi']),
            'consumers': sorted(c['id'] for c in run['consumers'])}


def summarize(run: dict, result: dict) -> dict:
    return {'started_at': run['started_at'], 'finished_at': run['finished_at'],
            'spans': len(run['spans']),
            'traces': len({s['trace_id'] for s in run['spans']}),
            'removed_fields': result['removed_fields'],
            'consumers': result['consumers']}


def capture(archive: Path, capture_id: str | None = None) -> dict:
    if capture_id is None:
        capture_id = (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
                      + '_' + uuid.uuid4().hex[:8])
    if not NAME.fullmatch(capture_id):
        raise ValueError('Invalid capture ID')
    archive = init_archive(archive)
    target = archive / capture_id
    target.mkdir(exist_ok=False)
    # capture.json is the final commit marker. Interrupted directories are not complete.
    before = toolchain()
    try:
        lab.execute(target / 'evidence')
        raw = (target / 'evidence/run.json').read_bytes()
        run = json.loads(raw)
        adapt_run.validate_capture(run)
        result = lab.analyze(run)
        view = build_view.build(target / 'evidence/run.json', target / 'view')
        if view['source_run_sha256'] != sha(raw) or toolchain() != before:
            raise ValueError('Capture source or toolchain changed during preparation')
        descriptor = {'schema': CAPTURE_SCHEMA, 'id': capture_id, 'status': 'complete',
                      'source_sha256': sha(raw), 'context': context(run),
                      'toolchain_sha256': before, 'summary': summarize(run, result),
                      'business_data': 'synthetic', 'telemetry': 'real_local_execution',
                      'historical': True, 'files_sha256': inventory(target)}
        write_new(target / 'capture.json', descriptor)
        return descriptor
    except Exception:
        # Preserve the partial directory for diagnosis; do not publish a success marker.
        if not (target / 'capture.json').exists():
            (target / 'INCOMPLETE.txt').write_text(
                'Captura incompleta. Nada foi publicado. Use outro ID para tentar novamente.\n',
                encoding='utf-8')
        raise


def load_capture(archive: Path, capture_id: str) -> tuple[dict, dict, dict]:
    if not NAME.fullmatch(capture_id):
        raise ValueError('Invalid capture ID')
    archive = permitted_output(archive)
    target = archive / capture_id
    if target.is_symlink() or (target / 'capture.json').is_symlink():
        raise ValueError('Symlink capture rejected')
    descriptor = json.loads((target / 'capture.json').read_text(encoding='utf-8'))
    if (descriptor.get('schema') != CAPTURE_SCHEMA or descriptor.get('id') != capture_id
            or descriptor.get('status') != 'complete'):
        raise ValueError('Unsupported or incomplete capture')
    manifest = descriptor['files_sha256']
    if not isinstance(manifest, dict) or not manifest:
        raise ValueError('Missing capture manifest')
    for name in manifest:
        rel = PurePosixPath(name)
        if rel.is_absolute() or '..' in rel.parts or '\\' in name:
            raise ValueError('Invalid manifest path')
    if inventory(target) != manifest:
        raise ValueError('Capture integrity check failed: missing, extra or changed file')
    raw = (target / 'evidence/run.json').read_bytes()
    if sha(raw) != descriptor['source_sha256']:
        raise ValueError('Source checksum mismatch')
    if descriptor['toolchain_sha256'] != toolchain():
        raise ValueError('Toolchain differs; use the recorded revision, not silent reinterpretation')
    run = json.loads(raw)
    adapt_run.validate_capture(run)
    result = lab.analyze(run)  # Never trust an edited cached conclusion.
    if descriptor['context'] != context(run) or descriptor['summary'] != summarize(run, result):
        raise ValueError('Capture metadata differs from its source')
    return descriptor, run, result


def history(archive: Path) -> list[dict]:
    archive = permitted_output(archive)
    entries = []
    for target in sorted(archive.iterdir()):
        if target.is_symlink():
            raise ValueError('Archive contains symlinks')
        if not target.is_dir():
            continue
        if not (target / 'capture.json').exists():
            entries.append({'id': target.name, 'status': 'incomplete'})
        else:
            descriptor, _, _ = load_capture(archive, target.name)
            entries.append({'id': target.name, 'status': 'complete',
                            'source_sha256': descriptor['source_sha256'],
                            **descriptor['summary']})
    return entries


def compare(archive: Path, before_id: str, after_id: str) -> dict:
    a, arun, aresult = load_capture(archive, before_id)
    b, brun, bresult = load_capture(archive, after_id)
    if a['context'] != b['context']:
        raise ValueError('Incompatible entity/environment/scope; comparison refused')
    if a['source_sha256'] == b['source_sha256']:
        raise ValueError('The same capture is not an independent execution')
    if adapt_run.moment(arun['finished_at']) > adapt_run.moment(brun['started_at']):
        raise ValueError('Captures overlap or were supplied in reverse order')
    fields = ['contract', 'removed_required_fields', 'usage_before_change',
              'regression_after_change', 'authorization']
    aa = {r['consumer']: r for r in aresult['consumers']}
    bb = {r['consumer']: r for r in bresult['consumers']}
    rows = []
    for key in sorted(aa):
        changes = {f: {'before': aa[key][f], 'after': bb[key][f]}
                   for f in fields if aa[key][f] != bb[key][f]}
        rows.append({'consumer': key, 'changes': changes,
                     'before': {f: aa[key][f] for f in fields},
                     'after': {f: bb[key][f] for f in fields}})
    return {'schema': 'evidentgraph-capture-diff-1', 'before': a['id'], 'after': b['id'],
            'source_hashes': [a['source_sha256'], b['source_sha256']], 'context': a['context'],
            'changed_consumers': sum(bool(r['changes']) for r in rows), 'consumers': rows,
            'capture_spans': [a['summary']['spans'], b['summary']['spans']],
            'openapi_changed': [v for v in arun['openapi']
                                if arun['openapi'][v] != brun['openapi'][v]],
            'consumer_declarations_changed': arun['consumers'] != brun['consumers'],
            'limitations': [
                'Comparação de capturas históricas de laboratório, não de produção.',
                'Menos spans ou uso UNKNOWN não provam remoção de dependência.',
                'Sem mudança de conclusão não significa ausência de risco.',
                'Hashes verificam consistência; não autenticam a origem de terceiros.',
                'PASS vale apenas para a verificação executada. IAM não avaliado.']}


def comparison_markdown(diff: dict) -> str:
    lines = ['# EvidentGraph — comparação de capturas', '',
             f"Antes: `{diff['before']}`  ", f"Depois: `{diff['after']}`", '',
             f"Consumidores com alteração de conclusão: **{diff['changed_consumers']}**.", '',
             '| Consumidor | Contrato antes → depois | Teste antes → depois |',
             '|---|---|---|']
    for r in diff['consumers']:
        lines.append(f"| {r['consumer']} | {r['before']['contract']} → {r['after']['contract']} | "
                     f"{r['before']['regression_after_change']} → {r['after']['regression_after_change']} |")
    lines += ['', '## Limites', ''] + ['- ' + x for x in diff['limitations']]
    lines += ['', '## Fontes SHA-256', ''] + ['`' + x + '`' for x in diff['source_hashes']]
    return '\n'.join(lines) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, default=HERE / 'runs' / 'captures')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('capture').add_argument('--id')
    commands.add_parser('list')
    cmd = commands.add_parser('compare')
    cmd.add_argument('before')
    cmd.add_argument('after')
    cmd.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'capture':
            info = capture(args.archive, args.id)
            print(lab.dump({'id': info['id'], 'sha256': info['source_sha256'],
                           'open': str(args.archive / info['id'] / 'view/EvidentGraph_L2.html')}))
        elif args.command == 'list':
            print(lab.dump(history(args.archive)))
        else:
            diff = compare(args.archive, args.before, args.after)
            out = permitted_output(args.out)
            out.mkdir(parents=True, exist_ok=False)
            write_new(out / 'comparison.json', diff)
            (out / 'comparison.md').write_text(comparison_markdown(diff), encoding='utf-8')
            print(lab.dump(diff))
    except Exception as error:
        parser.exit(1, f'Operação não concluída: {error}\nNenhum fallback sintético ou deploy foi executado.\n')


if __name__ == '__main__':
    main()

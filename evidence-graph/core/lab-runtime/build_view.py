"""Build an isolated, portable M3 viewer for L1 evidence. Does not edit the published UI."""
from __future__ import annotations
import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path
import re
from adapt_run import adapt

HERE = Path(__file__).resolve().parent
PREVIEW = HERE.parents[1] / 'preview-m2'
FILES = ['index.html', 'styles.css', 'lineage.css', 'investigation.css', 'data.js',
         'app.js', 'lineage.js', 'exploration.js', 'investigation.js', 'manifest.json']


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise ValueError('M3 source changed; review the adapter patch: '+old[:60])
    return text.replace(old, new)


def build(run_path: Path, out: Path, preview: Path = PREVIEW) -> dict:
    raw = run_path.read_bytes()
    bundle = adapt(raw)
    texts = {name: (preview / name).read_text(encoding='utf-8') for name in FILES}
    original = dict(texts)
    packed = re.search(r'window.EG_PACKED\s*=\s*("[^"\n]+")\s*;', texts['data.js'])
    if not packed:
        raise ValueError('Missing M3 dataset')
    aurora = json.loads(packed[1])
    original_data = json.loads(gzip.decompress(base64.b64decode(aurora)))
    if not original_data.get('synthetic') or len(original_data['assets']) != 240:
        raise ValueError('Unexpected Aurora baseline')
    lab_packed = base64.b64encode(gzip.compress(json.dumps(bundle, ensure_ascii=False,
                                 sort_keys=True, separators=(',', ':')).encode(), mtime=0)).decode()
    texts['data.js'] = '// Two independent read-only datasets; selected before M3 boots.\nwindow.EG_PACKED = location.hash === "#aurora" ? '+json.dumps(aurora)+' : '+json.dumps(lab_packed)+';\n'
    texts['app.js'] = replace_once(texts['app.js'], "const SCENARIOS = {", "const SCENARIOS = {'LAB-001':'Remover cliente_id · coleta v1/v2',")
    texts['app.js'] = replace_once(texts['app.js'], "data.synthetic!==true||", "(data.synthetic!==true&&data.provenance?.kind!=='l1_capture')||")
    html = texts['index.html']
    html = replace_once(html, '<div>Grupo Aurora <span class="slash">', '<div><span id="contextName">Grupo Aurora</span> <span class="slash">')
    html = replace_once(html, '<nav aria-label="Navegação principal">', '<label class="workspace-picker" for="workspaceSource">Fonte de evidências<select id="workspaceSource"><option value="lab">Aurora Lab</option><option value="aurora">Grupo Aurora</option></select></label><nav aria-label="Navegação principal">')
    html = replace_once(html, '<div id="loadStatus"', '<div id="captureNotice" class="capture-notice" hidden></div><div id="loadStatus"')
    html = replace_once(html, '</head>', '<script src="lab_view.js" defer></script><link rel="stylesheet" href="lab_view.css"></head>')
    texts['index.html'] = html
    texts['lab_view.js'] = (HERE/'lab_view.js').read_text(encoding='utf-8')
    texts['lab_view.css'] = '.workspace-picker{display:block;padding:0 18px 20px;font-size:12px;color:#b8c6d8}.workspace-picker select{width:100%;margin-top:8px;padding:9px 4px;border-radius:5px}.capture-notice{padding:10px 14px;border:1px solid #c6d5e3;border-radius:6px;background:#f4f8fb;font-size:12px;margin-bottom:18px;color:#33465a}.capture-notice[hidden]{display:none}.lab-test{margin-top:9px}.lab-test small{display:block;font-size:10px;margin-bottom:4px;color:#596a7b}.lab-result{padding-bottom:12px;border-bottom:1px solid #dae2ea;margin-bottom:16px}.lab-result code{font-size:11px;overflow-wrap:anywhere}.lab-inspector{border-top:1px solid #dae2ea;margin-top:12px;padding-top:14px}.lab-inspector small{font-size:11px}.lab-inspector p{margin:8px 0}\n'
    # The existing export must not call real telemetry a fully synthetic catalog.
    texts['investigation.js'] = replace_once(texts['investigation.js'], "'**Grupo Aurora: organização e dados fictícios.**'", "(data.provenance?'**Aurora Lab: dados fictícios; telemetria de execução local capturada. Não é produção.**':'**Grupo Aurora: organização e dados fictícios.**')")
    texts['investigation.js'] = replace_once(texts['investigation.js'], '`Dataset: ${data.dataset_version}. Relógio: ${data.clock}.`', '`Dataset: ${data.dataset_version}. Referência temporal: ${data.clock}. Fonte SHA-256: ${data.provenance?.source_sha256||"cenário sintético versionado"}.`')
    texts['investigation.js'] = replace_once(texts['investigation.js'], 'A análise de impacto específica permanece limitada aos três cenários preparados.', 'A análise de impacto é limitada aos casos disponíveis no conjunto de evidências selecionado.')
    out.mkdir(parents=True, exist_ok=False)  # Never overwrite a capture or public directory.
    for name, text in texts.items():
        if name != 'manifest.json':
            (out/name).write_text(text, encoding='utf-8')
    (out/'lab-bundle.json').write_text(json.dumps(bundle, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    manifest = {'adapter': bundle['provenance']['adapter_version'],
                'source_run_sha256': hashlib.sha256(raw).hexdigest(),
                'm3_sources_sha256': {n: hashlib.sha256(t.encode()).hexdigest() for n,t in original.items()},
                'outputs_sha256': {n: hashlib.sha256(t.encode()).hexdigest() for n,t in texts.items() if n!='manifest.json'},
                'lab_assets': len(bundle['assets']), 'lab_relations': len(bundle['relations']),
                'aurora_assets': len(original_data['assets']), 'aurora_relations': len(original_data['relations'])}
    (out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    # Offline single-file companion, using the exact prepared assets.
    standalone = texts['index.html']
    for name in ['styles.css','lineage.css','investigation.css','lab_view.css']:
        standalone = standalone.replace('<link rel="stylesheet" href="'+name+'">','<style>'+texts[name]+'</style>')
    scripts = re.findall(r'<script src="([^"]+)" defer></script>', standalone)
    standalone = re.sub(r'<script src="[^"]+" defer></script>', '', standalone)
    code = '\n'.join(texts[n].replace('</script', '<\\/script') for n in scripts)
    standalone = standalone.replace('</body>', '<script>'+code+'</script></body>')
    (out/'EvidentGraph_L2.html').write_text(standalone, encoding='utf-8')
    return manifest

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        info = build(args.run, args.out)
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, 'Prévia não criada: '+str(error)+'\n')
    print(json.dumps(info, indent=2))

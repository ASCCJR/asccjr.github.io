"""Build a read-only L5 viewer from the M3 sources without modifying them."""
import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path
import re
from auth_adapter import adapt
from view_lifecycle import prepare as prepare_lifecycle
from build_view import FILES, PREVIEW, HERE, replace_once
from capture_history import permitted_output


def build(run_path: Path, out: Path) -> dict:
    raw=run_path.read_bytes();bundle=adapt(raw)
    texts={name:(PREVIEW/name).read_text(encoding='utf-8') for name in FILES}
    hashes={name:hashlib.sha256(text.encode()).hexdigest() for name,text in texts.items()}
    match=re.search(r'window.EG_PACKED\s*=\s*("[^"\n]+")\s*;',texts['data.js'])
    if not match:raise ValueError('Missing Aurora bundle')
    aurora=json.loads(match[1]);original=json.loads(gzip.decompress(base64.b64decode(aurora)))
    if len(original['assets'])!=240 or len(original['relations'])!=512 or not original['synthetic']:
        raise ValueError('Unexpected Aurora baseline')
    packed=base64.b64encode(gzip.compress(json.dumps(bundle,ensure_ascii=False,sort_keys=True,
                          separators=(',',':')).encode(),mtime=0)).decode()
    texts['data.js']='window.EG_SOURCE=new URLSearchParams(location.search).get("source")==="aurora"?"aurora":"access";\nwindow.EG_PACKED=window.EG_SOURCE==="aurora"?'+json.dumps(aurora)+':'+json.dumps(packed)+';\n'
    texts['app.js']=replace_once(texts['app.js'],'const SCENARIOS = {',"const SCENARIOS = {'AUTH-001':'Permissão e mudança de contrato · v1/v2',")
    texts['app.js']=replace_once(texts['app.js'],'data.synthetic!==true||',"(data.synthetic!==true&&data.provenance?.kind!=='l5_capture')||")
    html=texts['index.html']
    html=replace_once(html,'<div>Grupo Aurora <span class="slash">','<div><span id="contextName">Grupo Aurora</span> <span class="slash">')
    html=replace_once(html,'<nav aria-label="Navegação principal">','<label class="workspace-picker" for="workspaceSource">Fonte de evidências<select id="workspaceSource"><option value="access">Aurora Acesso</option><option value="aurora">Grupo Aurora</option></select></label><nav aria-label="Navegação principal">')
    html=replace_once(html,'<div id="loadStatus"','<div id="captureNotice" class="capture-notice" hidden></div><div id="loadStatus"')
    html=replace_once(html,'</head>','<link rel="stylesheet" href="auth_view.css"><script src="auth_view.js" defer></script></head>')
    texts['index.html']=html;texts['auth_view.js']=(HERE/'auth_view.js').read_text()
    texts['auth_view.css']='.workspace-picker{display:block;padding:0 18px 20px;font-size:12px;color:#b8c6d8}.workspace-picker select{width:100%;margin-top:8px;padding:9px 4px;border-radius:5px}.capture-notice{padding:10px 14px;border:1px solid #c6d5e3;border-radius:6px;background:#f4f8fb;font-size:12px;margin-bottom:18px;color:#33465a}.auth-inspect{background:#f5f8fb;border:1px solid #dce3ec;padding:10px 12px;margin:12px 0;border-radius:5px;font-size:12px}.auth-inspect small{font-size:10px;color:#52657b}.auth-inspect p{margin:8px 0;line-height:1.5}.auth-panel{border-top:1px solid #dce3ec;margin-top:16px;padding-top:14px}.auth-panel p{line-height:1.6;margin:10px 0}.auth-panel code{overflow-wrap:anywhere;font-size:11px}.auth-mini{margin-top:10px}.auth-mini small{display:block;margin:8px 0 4px;color:#65758a;font-size:10px}.auth-panel .detail-grid{display:block}.dialog-body .auth-panel .detail-grid{display:grid;grid-template-columns:1fr 1fr}\n'
    texts['investigation.js']=replace_once(texts['investigation.js'],"'**Grupo Aurora: organização e dados fictícios.**'", "(data.provenance?'**Aurora Acesso: dados fictícios; execução local capturada; escopo de autorização limitado.**':'**Grupo Aurora: organização e dados fictícios.**')")
    texts['investigation.js']=replace_once(texts['investigation.js'],'`Dataset: ${data.dataset_version}. Relógio: ${data.clock}.`','`Dataset: ${data.dataset_version}. Referência: ${data.clock}. SHA-256: ${data.provenance?.source_sha256||"sintético"}.`')
    prepare_lifecycle(texts)
    html=texts['index.html']
    out=permitted_output(out);out.mkdir(parents=True,exist_ok=False)
    for name,text in texts.items():
        if name!='manifest.json':(out/name).write_text(text,encoding='utf-8')
    (out/'auth-bundle.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    standalone=html
    for name in ['styles.css','lineage.css','investigation.css','auth_view.css']:
        standalone=standalone.replace('<link rel="stylesheet" href="'+name+'">','<style>'+texts[name]+'</style>')
    scripts=re.findall(r'<script src="([^"]+)" defer></script>',standalone)
    standalone=re.sub(r'<script src="[^"]+" defer></script>','',standalone)
    standalone=standalone.replace('</body>','<script>'+ '\n'.join(texts[n].replace('</script','<\\/script') for n in scripts)+'</script></body>')
    (out/'EvidentGraph_L5.html').write_text(standalone,encoding='utf-8')
    manifest={'source_run_sha256':hashlib.sha256(raw).hexdigest(),'m3_sources_sha256':hashes,
              'assets':len(bundle['assets']),'relations':len(bundle['relations']),
              'outputs_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file()}}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    return manifest


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    try:print(json.dumps(build(a.run,a.out),indent=2))
    except Exception as e:p.exit(1,'Visualização não criada: '+str(e)+'\n')

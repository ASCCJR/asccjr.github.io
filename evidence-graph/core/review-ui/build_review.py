"""L7 read-only review of an intact L6-B result. Reuses M3; no promotion of heuristics.

Trusted local experiment output only, not a universal upload/import endpoint.
Predictions are recalculated from pre-change inputs; post-test outcomes stay separate.
"""
from __future__ import annotations
import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

HERE = Path(__file__).resolve().parent
CORE = HERE.parent
sys.path.insert(0, str(CORE / 'evaluation/refinement'))
sys.path.insert(0, str(CORE / 'lab-runtime'))
from candidate import refine
from build_view import FILES, PREVIEW, replace_once
from view_lifecycle import prepare as prepare_lifecycle

LABELS = {
 'c01':'Cliente de pedidos', 'c02':'Consulta de situação', 'c03':'Rotina mensal',
 'c04':'Consumidor sem manifesto', 'c05':'Consulta com alternativa', 'c06':'Consulta resiliente',
 'c07':'Consumidor divergente', 'c08':'Cliente com acesso negado', 'c09':'Política indisponível',
 'c10':'Consulta condicional', 'c11':'Normalização sem alternativa', 'c12':'Manifesto excessivo',
 'n01':'Pedido identificado', 'n02':'Consulta anônima', 'n03':'Contagem do identificador',
 'n04':'Entrega com identificador', 'n05':'Normalização delegada', 'n06':'Consulta completa',
 'n07':'Roteamento por sufixo', 'n08':'Situação em maiúsculas',
}


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_reference(root: Path) -> tuple[dict, dict]:
    if root.is_symlink():
        raise ValueError('Reference symlinks are not supported')
    manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('status') != 'complete' or not isinstance(manifest.get('files_sha256'), dict):
        raise ValueError('Expected completed L6-B manifest')
    files = {}
    for name, checksum in manifest['files_sha256'].items():
        rel = PurePosixPath(name)
        if rel.is_absolute() or '..' in rel.parts or '\\' in name:
            raise ValueError('Invalid reference path')
        path = root / name
        if any(p.is_symlink() for p in [path, *path.parents]):
            raise ValueError('Reference path contains a symlink')
        if path.stat().st_size > 5_000_000:
            raise ValueError('Reference file exceeds 5 MB')
        raw = path.read_bytes()
        if digest(raw) != checksum:
            raise ValueError('Reference integrity mismatch: ' + name)
        files[name] = raw
    return files, manifest


def pointer(files: dict[str, bytes], reference: str):
    """Resolve only local experiment file JSON pointers; never follow a URL."""
    name, fragment = reference.split('#', 1)
    value = json.loads(files[name])
    for key in fragment.removeprefix('/').split('/') if fragment else []:
        key = key.replace('~1', '/').replace('~0', '~')
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def bundle(files: dict[str, bytes], cohort: str) -> dict:
    if cohort not in {'review', 'validation'}:
        raise ValueError('Unknown cohort')
    stem = 'base' if cohort == 'review' else 'new_cases'
    epath, spath = f'inputs/{stem}-evidence.json', f'inputs/{stem}-sources.json'
    evidence, sources = json.loads(files[epath]), json.loads(files[spath])
    predictions = refine(evidence, sources)
    if predictions != json.loads(files[f'predictions/{stem}.json'])['with_S']:
        raise ValueError('Candidate revision differs from the recorded predictions')
    expected = {f'c{i:02d}' for i in range(1,13)} if cohort == 'review' else {f'n{i:02d}' for i in range(1,9)}
    if set(predictions) != expected:
        raise ValueError('This presentation supports only the known L6-B cohorts')
    tpath = 'truth-original.json' if cohort == 'review' else 'truth-semantic.json'
    truth = json.loads(files[tpath])
    captured = json.loads(files['audit-original.json'])['finished_at']
    refs_hash = digest(b''.join(name.encode() + files[name] for name in sorted(files)))
    ctx = evidence['context']
    endpoint = 'l7-' + cohort + '-response'
    assets, relations, proofs, rows = [], [], [], []
    proof_map = {}
    def proof(subject, family, reference, title):
        id = 'e-' + digest(reference.encode())[:16]
        if id not in proof_map:
            item = {'id':id, 'family':family, 'source':'l6b-'+family,
                    'reference':reference, 'origin_id':reference, 'claim':'scoped_evidence',
                    'environment':ctx['environment'], 'subject':subject, 'target':endpoint,
                    'subject_version':'v1', 'target_version':'v1 → v2',
                    'collected_at':captured, 'valid_from':None, 'valid_until':None,
                    'title':title, 'details':pointer(files, reference)}
            proofs.append(item); proof_map[id] = item
        return id
    def asset(id, name, kind):
        assets.append({'id':id,'name':name,'kind':kind,'domain':'plataforma',
          'owner':'review-owner','environment':ctx['environment'],'version':'v1 → v2',
          'processes':[],'criticality':'not_assessed','metadata_origin':'explicit_presentation_mapping'})
    asset(endpoint, 'Resposta da API de clientes', 'api')
    for key, p in predictions.items():
        id = 'l7-' + key; asset(id, LABELS[key], 'application')
        pre = [proof(id,'code',f'{spath}#/{key}', 'Código e hipóteses da inferência')]
        if key in evidence['C']:
            pre.append(proof(id,'config',f'{epath}#/C/{key}', 'Manifesto declarado'))
        for i, span in enumerate(evidence['R']):
            if span['attributes'].get('eval.subject') == key:
                pre.append(proof(id,'runtime',f'{epath}#/R/{i}', 'Execução anterior à mudança'))
        if key in evidence['A']:
            pre.append(proof(id,'authorization',f'{epath}#/A/{key}', 'Política do endpoint'))
        test_ref = f'{tpath}#/functional_outcomes/{key}' if cohort == 'review' else f'{tpath}#/{key}'
        post = [proof(id, 'runtime', test_ref, 'Teste posterior · referência separada')]
        pairs = truth['functional_outcomes'][key] if cohort == 'review' else truth[key]['cases']
        if not pairs or any(not x['v1']['completed'] for x in pairs):
            execution = 'BASELINE_NOT_ESTABLISHED'
        elif any(not x['v2']['completed'] for x in pairs):
            execution = 'FAILED'
        else:
            execution = 'COMPLETED'
        semantic = 'NOT_EVALUATED'
        requirement = None
        if cohort == 'validation':
            target = truth[key]
            semantic = {'YES':'VIOLATED','NO':'MET','UNKNOWN':'NOT_EVALUATED'}[target['requirement_regression']]
            requirement = target['requirement']
        # Do not label a pre-change risk as a confirmed failure or a NO as safe.
        impact = 'POSSIBLE' if p['potential_impact'] == 'YES' else 'INCONCLUSIVE'
        next_step = ('Validar o requisito de negócio e revisar a alteração.' if p['predicted_exception'] == 'NO'
                     else 'Executar teste funcional com a resposta alterada.' if p['predicted_exception'] == 'UNKNOWN'
                     else 'Revisar o consumo do campo e testar a migração.')
        rid = 'r-' + key
        # These relationships express fixture response consumption, NOT discovered HTTP calls.
        relations.append({'id':rid,'source':id,'target':endpoint,'kind':'USES_RESPONSE',
             'evidence_ids':pre, 'meaning':'Resposta fornecida ao programa na fixture; não afirma chamada HTTP autônoma.'})
        rows.append({'consumer':id,'name':LABELS[key],'owner':'review-owner','processes':[],
          'criticality':'not_assessed','impact':impact,
          'activity':'OBSERVED' if p['used_in_baseline_window']=='YES' else 'UNKNOWN',
          'paths':[[rid]],'evidence_ids':pre,'origin_ids':pre,'next_step':next_step,
          'authorization':'NOT_EVALUATED','field_access':'NOT_EVALUATED','contract_conflict':False,
          'limitations':['Inferência experimental restrita; não é aprovação de publicação.',
             'Código, hipóteses e identificação dos casos pertencem ao laboratório.',
             'Resultado funcional e requisito de negócio são verificações distintas.'],
          'review':{'prediction':p,'pre_evidence_ids':pre,'test_evidence_ids':post,
             'tests':{'execution':execution,'business':semantic,'requirement':requirement,
                      'input_cases':len(pairs)},'scope':'remover cliente_id · resposta disponível',
             'case_id':key}})
    change = {'id':'REV-001' if cohort=='review' else 'VAL-001','target':endpoint,
        'operation':'remove_field','field':'cliente_id','before_version':'v1','after_version':'v2',
        'environment':ctx['environment'],'window_start':ctx['at'],'window_end':ctx['at']}
    result = {'change':change,'consumers':rows,'truncated':False,'scope_complete':False,
       'scope_note':'Comparação histórica do laboratório. As previsões usam entradas anteriores; os testes posteriores são consultados separadamente.'}
    return {'synthetic':False, 'dataset_version':'l7-'+cohort+'-'+refs_hash,
        'clock':captured,'assets':assets,'relations':relations,'evidence':proofs,
        'teams':[{'id':'review-owner','name':'Responsável a definir','domain':'plataforma'}],
        'processes':[],'domains':[{'id':'plataforma','name':'Plataforma'}],'coverage':[],
        'sources':[], 'results':[result], 'provenance':{'kind':'l7_review','cohort':cohort,
          'source_sha256':refs_hash,'captured_at':captured,'business_data':'synthetic',
          'origin':'L6-B trusted local capture and post-test reference',
          'limitations':['Captura histórica de laboratório; não há execução ao clicar.',
            'Predições e testes de referência do mesmo autor; não é validação externa.',
            'Relações representam consumo de resposta na fixture, não descoberta de arquitetura.',
            'Sem CNPJ, clientes reais ou resultados de negócio inferidos.']}}


def build(reference: Path, out: Path) -> dict:
    out = out.absolute()
    if any(p.is_symlink() for p in [out, *out.parents]):
        raise ValueError('Output symlinks refused')
    out = out.resolve()
    if out.is_relative_to(CORE.parent) and not out.is_relative_to(HERE/'runs'):
        raise ValueError('Inside the project use review-ui/runs')
    files, manifest = read_reference(reference)
    datasets = {c:bundle(files,c) for c in ['review','validation']}
    texts = {n:(PREVIEW/n).read_text(encoding='utf-8') for n in FILES}
    source_hashes = {n:digest(s.encode()) for n,s in texts.items()}
    match = re.search(r'window.EG_PACKED\s*=\s*("[^"\n]+")\s*;', texts['data.js'])
    if not match: raise ValueError('Missing original Aurora data')
    packed = {'aurora':json.loads(match[1])}
    original = json.loads(gzip.decompress(base64.b64decode(packed['aurora'])))
    if (len(original['assets']),len(original['relations'])) != (240,512):
        raise ValueError('Unexpected Aurora baseline')
    for name,b in datasets.items():
        packed[name] = base64.b64encode(gzip.compress(json.dumps(b,ensure_ascii=False,separators=(',',':')).encode(),mtime=0)).decode()
    texts['data.js'] = ('const bundles='+json.dumps(packed)+';\nconst requested=new URLSearchParams(location.search).get("source");\n'
        'window.EG_SOURCE=Object.hasOwn(bundles,requested)?requested:"review";window.EG_PACKED=bundles[window.EG_SOURCE];\n')
    texts['app.js'] = replace_once(texts['app.js'],'data.synthetic!==true||',"(data.synthetic!==true&&data.provenance?.kind!=='l7_review')||")
    texts['app.js'] = replace_once(texts['app.js'],'const SCENARIOS = {',"const SCENARIOS = {'REV-001':'Remover cliente_id · consumidores','VAL-001':'Remover cliente_id · resultados de negócio',")
    html = replace_once(texts['index.html'],'<div>Grupo Aurora <span class="slash">','<div><span id="contextName">Grupo Aurora</span> <span class="slash">')
    html = replace_once(html,'<nav aria-label="Navegação principal">','<label class="workspace-picker" for="workspaceSource">Fonte de evidências<select id="workspaceSource"><option value="review">Aurora Revisão</option><option value="validation">Aurora Validação</option><option value="aurora">Grupo Aurora</option></select></label><nav aria-label="Navegação principal">')
    html = replace_once(html,'<div id="loadStatus"','<div id="captureNotice" class="capture-notice" hidden></div><div id="loadStatus"')
    html = replace_once(html,'</head>','<link rel="stylesheet" href="review.css"><script src="review.js" defer></script></head>')
    texts['index.html'] = html
    for n in ['review.js','review.css']: texts[n]=(HERE/n).read_text(encoding='utf-8')
    # Only the generated copy understands the fixture relation. No production graph mutation.
    texts['lineage.js'] = texts['lineage.js'].replace("const relNames={", "const relNames={USES_RESPONSE:'Consome resposta',")
    texts['exploration.js'] = texts['exploration.js'].replace("'CALLS'", "'USES_RESPONSE','CALLS'")
    cohort_name = "(data.provenance.cohort==='review'?'Aurora Revisão':'Aurora Validação')"
    texts['investigation.js'] = replace_once(texts['investigation.js'],
       "'**Grupo Aurora: organização e dados fictícios.**'",
       "(data.provenance?.kind==='l7_review'?'**'+"+cohort_name+"+': relações de consumo de resposta em laboratório; captura histórica.**':'**Grupo Aurora: organização e dados fictícios.**')")
    context_limit = 'A análise de impacto específica permanece limitada aos três cenários preparados.'
    context_common = 'Relações do catálogo não comprovam acesso efetivo, permissão, quebra ou causalidade. Processos são vínculos declarados. '
    texts['investigation.js'] = replace_once(texts['investigation.js'],
       "'"+context_common+context_limit+"'",
       json.dumps(context_common,ensure_ascii=False)+"+(data.provenance?.kind==='l7_review'?'A revisão limita-se aos '+result.consumers.length+' consumidores de '+"+cohort_name+"+'. Inferência restrita às hipóteses do experimento; exportar não executa novos testes. Testes posteriores permanecem no relatório de análise quando solicitados.':'"+context_limit+"')")
    prepare_lifecycle(texts)
    out.mkdir(parents=True,exist_ok=False)
    for n,s in texts.items():
        if n!='manifest.json': (out/n).write_text(s,encoding='utf-8')
    standalone=texts['index.html']
    for n in re.findall(r'<link rel="stylesheet" href="([^"]+)">', standalone):
        standalone=standalone.replace('<link rel="stylesheet" href="'+n+'">','<style>'+texts[n]+'</style>')
    scripts=re.findall(r'<script src="([^"]+)" defer></script>',standalone)
    standalone=re.sub(r'<script src="[^"]+" defer></script>','',standalone)
    standalone=standalone.replace('</body>','<script>'+ '\n'.join(texts[n].replace('</script','<\\/script') for n in scripts)+'</script></body>')
    (out/'EvidentGraph_L7.html').write_text(standalone,encoding='utf-8')
    for c,b in datasets.items(): (out/(c+'-bundle.json')).write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    result={'version':'L7','reference_manifest_sha256':digest((reference/'manifest.json').read_bytes()),
        'm3_sources_sha256':source_hashes,'source_counts':{c:len(b['assets']) for c,b in datasets.items()},
        'outputs_sha256':{p.name:digest(p.read_bytes()) for p in out.iterdir() if p.is_file()}}
    (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--reference',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();print(json.dumps(build(a.reference,a.out),indent=2))

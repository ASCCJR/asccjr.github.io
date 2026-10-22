"""Versioned L6-B pilot: preserve A, add bounded code evidence S and semantic cases.

Trusted fixtures only. The prediction subprocess reads evidence/code, not the
post-change outcomes or business requirements. No UI, hosting or product mutation.
"""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import sys
import textwrap
from contextlib import ExitStack

HERE = Path(__file__).resolve().parent
EVALUATION = HERE.parent
sys.path.insert(0, str(EVALUATION))
from collect_experiment import collect
from oracle_consumers import PROGRAMS
from predict_sources import predict, QUESTIONS
from run_experiment import variants
from metrics import score
from lab import serve
import httpx
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict
import challenges
from bounded_static import source_hash


def dump(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, value):
    with path.open('x', encoding='utf-8') as f: f.write(dump(value))

def freeze():
    paths = list(HERE.glob('*.py')) + [HERE/'PROTOCOL.md', HERE/'semantic_requirements.json']
    paths += [EVALUATION/n for n in ('collect_experiment.py','oracle_consumers.py','predict_sources.py','metrics.py','run_experiment.py')]
    paths += [EVALUATION.parent/'lab-runtime'/n for n in ('lab.py','auth_policy.py')]
    return {str(p.relative_to(EVALUATION.parent)): sha(p) for p in sorted(paths)}


def exact_shape(fields):
    return {'type':'object', 'properties':{f:{'type':'string'} for f in fields},
            'required':list(fields), 'additionalProperties':False}


def source_envelopes(programs, context):
    # This is EXTRA information: trusted association and closed-world shape of the fixture.
    # Original OpenAPI does not automatically prove absence of extra response fields.
    result = {}
    for key, program in programs.items():
        source = textwrap.dedent(inspect.getsource(program))
        result[key] = dict(environment=context['environment'], resource=context['resource'],
            version=context['version'], valid_from=context['at'], valid_until=(datetime.fromisoformat(context['at'])+timedelta(hours=1)).isoformat(),
            source=source, source_sha256=source_hash(source),
            before=exact_shape(['cliente_id','status']), after=exact_shape(['status']),
            origin='trusted_fixture_code_mapping_and_exact_dict_assumption')
    return result


class StrictV1(BaseModel):
    model_config = ConfigDict(extra='forbid')
    cliente_id: str
    status: str

class StrictV2(BaseModel):
    model_config = ConfigDict(extra='forbid')
    status: str


def semantic_reference():
    """Execute authored consumers against actual local HTTP response objects.

No telemetry is supplied for these new cases. Business expectations are used only
here, after inference inputs are formed, not as a hidden prediction feature.
"""
    requirements = json.loads((HERE/'semantic_requirements.json').read_text())
    def app(version):
        api = FastAPI(title='L6-B semantic fixture', version=version, docs_url=None, redoc_url=None)
        @api.get('/customer', response_model=StrictV1 if version=='v1' else StrictV2)
        def customer():
            return {'cliente_id':'L6-001','status':'ativo'} if version=='v1' else {'status':'ativo'}
        return api
    rows = {}; receipts = []; contracts = {}
    with ExitStack() as stack:
        urls = {v:stack.enter_context(serve(app(v))) for v in ('v1','v2')}
        client = stack.enter_context(httpx.Client(timeout=5, trust_env=False))
        for v in urls:
            response = client.get(urls[v]+'/openapi.json'); response.raise_for_status()
            contracts[v] = response.json()
        for key, program in challenges.PROGRAMS.items():
            pairs = []
            for i, options in enumerate(challenges.OPTIONS[key]):
                entry = {}
                for version, url in urls.items():
                    response = client.get(url+'/customer'); response.raise_for_status()
                    receipts.append({'subject':key,'input_index':i,'version':version,'status':response.status_code})
                    try:
                        output = program(response.json(), options)
                        ok = output == requirements[key][version][i]
                        entry[version] = {'completed':True,'meets_requirement':ok,'exception':None}
                    except (KeyError, AttributeError, ValueError, TypeError) as error:
                        entry[version] = {'completed':False,'meets_requirement':False,'exception':type(error).__name__}
                pairs.append(entry)
            before_ok = all(p['v1']['completed'] for p in pairs)
            baseline_meets = all(p['v1']['meets_requirement'] for p in pairs)
            rows[key] = {
                'exception_regression': 'UNKNOWN' if not before_ok else 'YES' if any(not p['v2']['completed'] for p in pairs) else 'NO',
                'requirement_regression': 'UNKNOWN' if not baseline_meets else 'YES' if any(not p['v2']['meets_requirement'] for p in pairs) else 'NO',
                'silent_wrong_result': baseline_meets and any(p['v2']['completed'] and not p['v2']['meets_requirement'] for p in pairs),
                'cases':pairs, 'requirement':requirements[key]['description'],
            }
    return rows, {'transport':'HTTP loopback TCP','receipts':receipts,'producer_openapi':contracts}


def run_candidate(out, evidence, sources, name):
    epath = out/'inputs'/(name+'-evidence.json'); spath = out/'inputs'/(name+'-sources.json')
    target = out/'predictions'/(name+'.json')
    write(epath, evidence); write(spath, sources)
    subprocess.run([sys.executable, str(HERE/'candidate.py'), '--evidence',str(epath),
                    '--sources',str(spath),'--out',str(target)], check=True, timeout=30, capture_output=True)
    return json.loads(target.read_text())


def render(result):
    base = result['original_12']['base']
    lines = ['# EvidentGraph — L6-B: dependência, previsão e resultado','',
        '**Piloto exploratório. Nenhuma regra foi publicada no produto.**','',
        '## Mesmos 12 casos da L6-A — alvo: exceção após remoção do campo','',
        '| Condição | Corretas | FP | FN | Inconclusivas |','|---|---:|---:|---:|---:|']
    for name in ('A_CRA','B_without_S','S_only','B_with_S'):
        m = base[name]
        lines.append(f"| {name} | {m['correct']} | {m['fp']} | {m['fn']} | {m['abstained']} |")
    lines += ['',
        '**Comparação desigual em informação:** S acrescenta código do consumidor e a hipótese explícita de resposta exata do laboratório. Não é ganho apenas por combinar melhor C/R/A. S_only e B_with_S têm a mesma decisão de exceção: C/R/A enriquecem o contexto, não causam esse ganho.',
        'B_without_S não transforma leitura ou manifesto em prova de exceção. A abstenção total tem custo de cobertura e não é considerada sucesso.', '',
        '## O que foi separado','',
        '- Dependência declarada e campo observado são fatos relativos às suas fontes.',
        '- Impacto potencial é uma indicação para investigar; não equivale a previsão de exceção.',
        '- S faz inferência restrita, sem executar o código recebido, sob hipóteses explícitas de tipo/escopo.',
        '- Falha confirmada requer execução posterior. O preditor deixa essa dimensão em NOT_TESTED.',
        '- Terminar sem exceção não demonstra atender à regra de negócio. Essa resposta permanece UNKNOWN no candidato.', '',
        '## Oito casos novos — exceção e requisito de negócio','',
        '| Caso | Previsão de exceção S | Exceção executada | Requisito violado | Resultado errado sem exceção |',
        '|---|---|---|---|---|']
    for key, r in result['new_cases'].items():
        lines.append(f"| {key} | {r['prediction']} | {r['exception_regression']} | {r['requirement_regression']} | {'sim' if r['silent_wrong_result'] else 'não'} |")
    m = result['new_8_metrics']
    silent = sum(r['silent_wrong_result'] for r in result['new_cases'].values())
    lines += ['', f"Nos novos casos: {m['correct']} previsões de exceção corretas, {m['fp']+m['fn']} erros e {m['abstained']} inconclusivas. **{silent} casos violam o requisito sem lançar exceção**.",
        'n01 e n02 usam exatamente o mesmo código de fallback, mas têm requisitos diferentes. Em n01, perder o identificador é incorreto; em n02, o anonimato é aceito. O candidato não recebe esses requisitos e não finge decidir a correção de negócio.', '',
        '## Robustez nos 12 casos — B com S','',
        '| Vista | Corretas | Erros | Inconclusivas |','|---|---:|---:|---:|']
    for name, group in result['original_12'].items():
        m = group['B_with_S']; lines.append(f"| {name} | {m['correct']} | {m['fp']+m['fn']} | {m['abstained']} |")
    lines += ['', '## Limites e próxima decisão','',
        'A análise aceita apenas returns simples, string, acesso literal ao dicionário, get, upper/lower, concatenação e um try/except KeyError restrito. Código condicional, chamadas externas, índices dinâmicos, loops e formas não reconhecidas permanecem inconclusivos. Não é parser geral, prova formal ou sandbox de código hostil.',
        'Os casos antigos foram conhecidos antes desta revisão. Os novos também foram escritos pelo mesmo autor, não são holdout externo. Não há validação independente, significância estatística ou integração com a interface. As vistas são perturbações dos mesmos casos, não novas amostras.',
        'Um S com hash, versão ou validade incorretos deixa de sustentar a previsão. Hash de conteúdo não autentica origem; a associação entre código e consumidor ainda é controlada manualmente no laboratório.',
        'Próximo passo: revisão de casos por outra pessoa e levar a distinção entre indicação e confirmação à apresentação, sem promover a inferência restrita a um detector universal.', '']
    return '\n'.join(lines)


def execute(out: Path):
    out = out.absolute()
    if any(p.is_symlink() for p in [out, *out.parents]): raise ValueError('Output symlink rejected')
    out = out.resolve()
    project = EVALUATION.parent.parent
    if out.is_relative_to(project) and not out.is_relative_to(EVALUATION/'runs'):
        raise ValueError('Inside project use evaluation/runs')
    out.mkdir(parents=True, exist_ok=False)
    lock = freeze(); write(out/'protocol-lock.json', {'at':datetime.now(timezone.utc).isoformat(),'files_sha256':lock})
    try:
        (out/'inputs').mkdir(); (out/'predictions').mkdir()
        evidence, truth, audit = collect()
        write(out/'truth-original.json',truth); write(out/'audit-original.json',audit)
        sources = source_envelopes(PROGRAMS, evidence['context'])
        result = {'original_12':{},'new_cases':{}}
        details = []
        configurations = [(name, e, sources) for name,e in variants(evidence)]
        stale = json.loads(dump(sources))
        for item in stale.values(): item['valid_until'] = evidence['context']['at']
        wrong = json.loads(dump(sources))
        for item in wrong.values(): item['source_sha256'] = '0'*64
        configurations += [('stale_source',evidence,stale),('wrong_source_hash',evidence,wrong)]
        for name, e, src in configurations:
            b = run_candidate(out, e, src, name)
            a = predict(e, 'CRA')
            target = [truth['labels'][key][QUESTIONS[0]] for key in e['subjects']]
            values = {'A_CRA':[a[key][QUESTIONS[0]] for key in e['subjects']],
                      'B_without_S':[b['without_S'][key]['predicted_exception'] for key in e['subjects']],
                      'S_only':[b['with_S'][key]['prediction_basis']['answer'] for key in e['subjects']],
                      'B_with_S':[b['with_S'][key]['predicted_exception'] for key in e['subjects']]}
            result['original_12'][name] = {arm:score(target, pred) for arm,pred in values.items()}
            for arm, pred in values.items():
                for key,t,p in zip(e['subjects'],target,pred): details.append({'cohort':'original','view':name,'arm':arm,'subject':key,'reference':t,'prediction':p})
        # New cases: only S is offered. No fabricated traces or claim of C/R parity.
        expanded = dict(evidence, subjects=list(challenges.PROGRAMS), C={}, R=[], A={})
        predicted = run_candidate(out, expanded, source_envelopes(challenges.PROGRAMS, evidence['context']), 'new_cases')
        reference, sem_audit = semantic_reference()
        write(out/'truth-semantic.json',reference); write(out/'audit-semantic.json',sem_audit)
        for key, r in reference.items():
            result['new_cases'][key] = dict(r, prediction=predicted['with_S'][key]['predicted_exception'])
        for key,r in result['new_cases'].items():
            details.append({'cohort':'new','view':'base','arm':'B_with_S','subject':key,
                'reference':r['exception_regression'],'prediction':r['prediction']})
        result['new_8_metrics'] = score([r['exception_regression'] for r in reference.values()],
            [predicted['with_S'][key]['predicted_exception'] for key in reference])
        if freeze() != lock: raise RuntimeError('Frozen source changed during execution')
        write(out/'results.json', result)
        with (out/'cases.csv').open('x',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(details[0]));w.writeheader();w.writerows(details)
        (out/'report.md').write_text(render(result),encoding='utf-8')
        write(out/'manifest.json',{'status':'complete','schema':'l6b-results-1',
            'files_sha256':{str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file()}})
        return result
    except Exception:
        (out/'INCOMPLETE.txt').write_text('Incomplete. No fallback or deploy.\n')
        raise


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();execute(a.out);print(a.out/'report.md')

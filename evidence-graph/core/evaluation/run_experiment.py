"""Run the L6-A pilot; freeze files, collect, predict without labels, then score.

All outputs are local under a fresh directory. No UI change, upload or deploy.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from collect_experiment import collect
from metrics import score
from predict_sources import QUESTIONS, MODES

HERE = Path(__file__).resolve().parent
VIEWS = ('base','no_runtime','stale_contract','incomplete_policy','replayed_runtime','wrong_environment_runtime')
FREEZE = ('PROTOCOL.md','oracle_consumers.py','collect_experiment.py','predict_sources.py','metrics.py','run_experiment.py')


def dump(obj):return json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+'\n'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,obj):
    with path.open('x',encoding='utf-8') as f:f.write(dump(obj))


def variants(evidence):
    for name in VIEWS:
        e = deepcopy(evidence)
        if name == 'no_runtime':e['R']=[]
        if name == 'stale_contract':
            for d in e['C'].values():d['valid_until']=e['context']['at']
        if name == 'incomplete_policy':
            for p in e['A'].values():
                if p is not None:p['complete']=False
        if name == 'replayed_runtime':e['R'] += deepcopy(e['R'])
        if name == 'wrong_environment_runtime':
            for s in e['R']:s['attributes']['eval.environment']='other-environment'
        yield name,e


def report(results):
    lines=['# EvidentGraph L6-A — primeiro experimento de fontes','',
        '**Piloto controlado com 12 consumidores de teste. Não é benchmark externo ou prova de superioridade.**','',
        'C = contratos declarados dos consumidores; R = execução anterior à mudança (inclui instrumentação de nomes de campos); A = política local.',
        'Todas as condições recebem a mesma alteração proposta da API. Não recebem o resultado do teste posterior.','',
        'Os programas de referência não consultam os contratos declarados. Suas funções recebem respostas v1/v2 obtidas por HTTP; a referência registra conclusão ou exceção. O servidor de referência não usa o avaliador de políticas sob teste.','',
        '## Impacto condicionado à resposta estar disponível — captura base','',
        '| Fontes | Corretas / 12 | Erros (FP / FN) | Inconclusivas | Precisão positiva | Recuperação de positivos* |',
        '|---|---:|---:|---:|---:|---:|']
    def pct(x):return 'não definida' if x is None else f'{100*x:.1f}%'
    for mode in MODES:
        m=results['base'][mode]['breaks_when_response_available']
        lines.append(f"| {mode} | {m['correct']} / {m['n']} | {m['fp']} / {m['fn']} | {m['abstained']} | {pct(m['precision'])} | {pct(m['positive_recovery'])} |")
    lines += ['', '*Recuperação = TP / todos os positivos conhecidos, incluindo positivos sem resposta. Não escondemos abstenções na acurácia dos casos respondidos.', '',
        '## Mesmos consumidores, outras perguntas','',
        '| Fontes | Uso: corretas / referência conhecida | Uso: sem resposta | Permissão: corretas / referência conhecida | Permissão: sem resposta |','|---|---:|---:|---:|---:|']
    for mode in MODES:
        u=results['base'][mode]['used_in_baseline_window'];a=results['base'][mode]['can_access_endpoint']
        lines.append(f"| {mode} | {u['correct']} / {u['known_reference']} | {u['abstained']} | {a['correct']} / {a['known_reference']} | {a['abstained']} |")
    lines += ['', 'Um consumidor tem referência de permissão UNKNOWN (503 por fonte indisponível). Ele é contado à parte, não como acerto binário. A ausência de uso tem referência negativa no roteiro completo, mas o analisador não recebe esse roteiro: silêncio da telemetria permanece inconclusivo.', '',
        '## Perturbações — combinação CRA','',
        '| Vista da evidência | Impacto correto / erro / inconclusivo | Uso correto / inconclusivo | Permissão correta / inconclusiva |','|---|---|---|---|']
    for view in VIEWS:
        b=results[view]['CRA']['breaks_when_response_available'];u=results[view]['CRA']['used_in_baseline_window'];a=results[view]['CRA']['can_access_endpoint']
        lines.append(f"| {view} | {b['correct']} / {b['fp']+b['fn']} / {b['abstained']} | {u['correct']} / {u['abstained']} | {a['correct']} / {a['abstained']} |")
    lines += ['', 'As seis vistas reutilizam as mesmas 12 referências. Não são 72 consumidores independentes. Duplicar spans não cria confirmação independente; ambientes incompatíveis e evidência vencida são descartados.', '',
        '## Como interpretar','',
        '- Consulte cases.csv para cada resposta, inclusive os erros. Não há ganho garantido por combinar fontes.',
        '- O baseline R usa acesso direto a campo como sinal de risco; try/except pode tornar essa hipótese falsa. A heurística é experimental e não foi promovida ao produto.',
        '- Uma declaração completa também pode estar errada. Conflito explícito vira UNKNOWN; documentação incorreta sem contradição continua um risco.',
        '- Permissões não determinam a compatibilidade intrínseca de uma tarefa. A não melhora essa pergunta por construção; ajuda a responder outra pergunta.',
        '- O alvo de impacto é exceção após a mudança para os inputs preparados, sob disponibilidade da resposta. Não inclui resultado numérico errado, efeitos indiretos, latência ou quebra universal.',
        '- Casos e regras foram escritos pelo mesmo autor. Há separação de código/arquivos entre referência e previsão, mas não revisão externa, teste cego ou conjunto representativo de clientes.',
        '- Instrumentação de campos é manual e exclusiva deste experimento; traces HTTP genéricos não fornecem automaticamente esses dados.',
        '- Não foram calculados significância, intervalos populacionais, economia ou ganho de mercado. Não houve treinamento de IA.',
        '', '## Reprodução e auditoria','',
        'protocol-lock.json contém hashes anteriores à coleta; audit.json registra execução; inputs/ contém só evidências de cada vista; predictions/ não recebe truth.json; results.json contém contagens e denominadores. Arquivos e manifesto têm SHA-256. Capturas e resultados são locais, sem publicar no Pages.','']
    return '\n'.join(lines)


def execute(out:Path):
    out=out.absolute()
    if any(p.is_symlink() for p in [out,*out.parents]):raise ValueError('Output symlink forbidden')
    out=out.resolve()
    core=HERE.parent
    if out.is_relative_to(core.parent) and not out.is_relative_to(HERE/'runs'):
        raise ValueError('Inside project use evaluation/runs only')
    out.mkdir(parents=True,exist_ok=False)
    lock={n:sha(HERE/n) for n in FREEZE}
    write(out/'protocol-lock.json',{'at':datetime.now(timezone.utc).isoformat(),'sha256':lock,
        'meaning':'Local pre-execution freeze; not an external preregistration or blind holdout.'})
    try:
        evidence,truth,audit=collect()
        write(out/'evidence.json',evidence);write(out/'truth.json',truth);write(out/'audit.json',audit)
        (out/'inputs').mkdir();(out/'predictions').mkdir()
        all_results={};cases=[]
        for name,e in variants(evidence):
            source=out/'inputs'/f'{name}.json';target=out/'predictions'/f'{name}.json';write(source,e)
            subprocess.run([sys.executable,str(HERE/'predict_sources.py'),'--evidence',str(source),'--out',str(target)],
                           check=True,timeout=30,capture_output=True,text=True)
            predicted=json.loads(target.read_text(encoding='utf-8'));all_results[name]={}
            for mode in MODES:
                all_results[name][mode]={}
                for q in QUESTIONS:
                    ids=e['subjects'];actual=[truth['labels'][s][q] for s in ids]
                    guess=[predicted[mode][s][q] for s in ids]
                    all_results[name][mode][q]=score(actual,guess)
                    for s,t,p in zip(ids,actual,guess):
                        cases.append({'view':name,'sources':mode,'question':q,'subject':s,'reference':t,'prediction':p,
                                      'reason':';'.join(predicted[mode][s]['reasons'])})
        if lock!={n:sha(HERE/n) for n in FREEZE}:raise RuntimeError('Frozen source changed during experiment')
        write(out/'results.json',all_results)
        with (out/'cases.csv').open('x',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(cases[0]));w.writeheader();w.writerows(cases)
        (out/'report.md').write_text(report(all_results),encoding='utf-8')
        manifest={p.relative_to(out).as_posix():sha(p) for p in sorted(out.rglob('*')) if p.is_file()}
        write(out/'manifest.json',{'schema':'l6-results-1','status':'complete','files_sha256':manifest})
        return all_results
    except Exception:
        (out/'INCOMPLETE.txt').write_text('Execução incompleta; não interpretar como resultado concluído.\n')
        raise


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    execute(args.out)
    print(str(args.out/'report.md'))

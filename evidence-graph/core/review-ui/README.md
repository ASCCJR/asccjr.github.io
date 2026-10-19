# L7 — revisão por níveis de evidência

Checkpoint 3 concluído em 2026-10-19: **L7 pronta para revisão de merge; publicação não autorizada.** PR #3 continua rascunho. Código/workflows testados em `1a1324c56694474dcf76a16466c0c22693d808a9`; os três runs usaram o checkout de merge temporário `3f07940e795ec69561e69a57116b5b241dde16e0`, cuja árvore é idêntica. Depois desses runs, só `00_START_HERE.md`, `30_L7_EVIDENCE_REVIEW.md` e este README foram atualizados.

Resultados: [avaliação 39335649585](https://github.com/ASCCJR/asccjr.github.io/actions/runs/39335649585) (124 + 43 + 62 Python), [laboratório 39335649610](https://github.com/ASCCJR/asccjr.github.io/actions/runs/39335649610) (124 Python repetidos + 12/10 HTTP), [revisão 39335649617](https://github.com/ASCCJR/asccjr.github.io/actions/runs/39335649617) (20 Python + 14 HTTP + três repetições adicionais da inicialização corrigida). Total: **249 Python e 36 HTTP distintos**, sem falhas/erros/skips nesses runs. As duas verificações preliminares, os 124 repetidos e as três repetições não aumentam esses totais.

As 12 screenshots foram abertas e inspecionadas. Os níveis de evidência, c10 inconclusivo, diferença n01/n02, fontes, grafo/lista e Aurora 240/512 estão preservados. Notas isoladas e exportações filtradas foram confirmadas por HTTP; o campo de nota fica fora da área visível das três PNG de notas. Ver o [checkpoint 30](../docs/30_L7_EVIDENCE_REVIEW.md) para a avaliação das imagens, histórico de falhas e limites. Avaliação independente e decisão de merge/publicação permanecem pendentes.

Interface isolada sobre uma saída íntegra da L6-B. Reutiliza grafo/lista M3 e o Grupo Aurora; não altera a aplicação publicada nem amplia o analisador experimental.

```sh
python -m pip install -r evidence-graph/core/lab-runtime/requirements.txt
python evidence-graph/core/evaluation/refinement/run_refinement.py --out evidence-graph/core/evaluation/runs/l6b-review
python evidence-graph/core/review-ui/build_review.py --reference evidence-graph/core/evaluation/runs/l6b-review --out evidence-graph/core/review-ui/runs/view-01
```

Abrir `review-ui/runs/view-01/EvidentGraph_L7.html`. A saída deve ser nova. Para a versão em arquivos separados, servir a pasta gerada por HTTP. Fontes independentes: Aurora Revisão (12 casos e a resposta da API), Aurora Validação (8 casos e a resposta) e Grupo Aurora (240 ativos/512 relações). Não são conjuntos unidos.

A previsão é recalculada dos inputs anteriores e comparada com a versão registrada. Os resultados posteriores só alimentam o painel de teste, não a previsão. A opção **Mostrar testes registrados** revela a referência histórica; não executa testes. Não é controle de confidencialidade: o HTML já contém as referências dos casos fictícios.

As relações `USES_RESPONSE` representam consumo de respostas na fixture, não chamadas HTTP descobertas. Equipes/processos não foram inventados. Os rótulos amigáveis são mapeamentos de apresentação; exemplos: Consulta resiliente=c06, Pedido identificado=n01, Consulta anônima=n02.

Para revisar: abrir c06 e distinguir leitura observada de exceção; revelar os testes; abrir n01/n02 em Aurora Validação e comparar o requisito de negócio. Em c10, a inferência continua inconclusiva mesmo quando o teste posterior registra uma exceção. Anotações não modificam evidências.

Testes: `python -m unittest -v test_review` e, com Chromium/Playwright instalado, `python -m unittest -v test_review_http`. A suíte HTTP não usa fallback DOM ou retries. A reprodução de inicialização antiga existe apenas dentro da fixture do teste, nunca no site. O servidor retém a resposta da extensão até a ordem relevante ser observada; não usa uma espera fixa para presumir essa ordem.

Use o Chromium correspondente ao Playwright 1.57.0 em uma plataforma suportada. As suítes HTTP mantêm o sandbox habilitado. No Ubuntu 26.04 desta integração, a instalação do navegador foi recusada pelo instalador oficial: não existe URL de download para a chave detectada. Essa limitação local permanece; não forçar outra identificação de plataforma ou usar um navegador diferente para apresentar aprovação.

No GitHub Actions, somente os jobs de navegador de `evidentgraph-review.yml` e `evidentgraph-runtime-lab.yml` usam Ubuntu 22.04, mantendo Python 3.12 e Playwright 1.57.0/Chromium correspondente, com sandbox habilitado e usuário não root. Antes das suítes, `lab-runtime/check_browser_environment.py` registra versões/opções, abre uma página real em HTTP loopback, verifica um clique JavaScript e encerra os recursos; falha de capacidade impede as suítes e conserva diagnóstico de leitura. Não é teste funcional nem auditoria de segurança. Nos runs acima, ambos passaram com Chromium 143.0.7499.4/revisão 1200 e UID 1001. O WSL local continua bloqueado; os runs anteriores em Ubuntu 24.04 falharam por `No usable sandbox!` antes de executar casos HTTP.

Após a checagem de capacidade, o job de revisão tenta os 20 casos Python L7, os 14 HTTP e as três repetições corrigidas; o laboratório tenta os 124 Python e as duas suítes HTTP (12 e 10). Os códigos de saída de cada suíte são registrados e qualquer falha faz o job falhar, preservando os resultados das demais. Consulte o SHA efetivamente testado nos logs; o checkout de PR pode ser um merge temporário. O workflow de avaliação anterior mantém as 229 regressões Python. Execuções repetidas não são testes distintos.

Para guardar screenshots e observações locais em um ambiente suportado, defina `EG_TEST_EVIDENCE_DIR` com um diretório de evidências fora da árvore versionada antes de executar `test_review_http`. Os casos usam capturas próprias, HTTP real e dados de negócio fictícios. O CI seleciona explicitamente apenas logs e screenshots, com retenção de sete dias; não disponibiliza o viewer como site. Examinar os arquivos produzidos continua necessário para afirmar revisão visual.

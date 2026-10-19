# L7 — revisão por níveis de evidência

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

No GitHub Actions, `evidentgraph-review.yml` usa Ubuntu 24.04 e Python 3.12, roda os 20 casos Python L7 e os 14 casos HTTP, e repete o cenário corrigido de extensão atrasada três vezes. `evidentgraph-runtime-lab.yml` executa as 22 regressões HTTP anteriores. Consulte o SHA efetivamente testado nos logs; o checkout de PR pode ser um merge temporário. O workflow de avaliação anterior mantém as 229 regressões Python. Execuções repetidas não são testes distintos.

Para guardar screenshots e observações locais em um ambiente suportado, defina `EG_TEST_EVIDENCE_DIR` com um diretório de evidências fora da árvore versionada antes de executar `test_review_http`. Os casos usam capturas próprias, HTTP real e dados de negócio fictícios. O CI seleciona explicitamente apenas logs e screenshots, com retenção de sete dias; não disponibiliza o viewer como site. Examinar os arquivos produzidos continua necessário para afirmar revisão visual.

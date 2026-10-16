# L6-A — experimento com referências comportamentais separadas

**Data:** 2026-10-16. **Base:** L5, commit `12bfa8dbb662712b177a8cb2d5740b301c7a8a13`.  
**Escopo:** primeiro piloto controlado de avaliação, não conclusão de validação científica do Core. Trabalho no PR #3, sem merge ou deploy.

## O que mudou

A pasta `core/evaluation/` implementa coleta por HTTP, referência comportamental separada, comparação de sete combinações de fontes, perturbações e métricas com abstenção. Nenhum arquivo de UI, dataset M1, código L1–L5 ou oportunidade foi alterado. Os novos candidatos não foram promovidos ao analisador do produto.

A diferença para os testes anteriores é que o resultado funcional não é inferido do mesmo `required_fields` usado pelo comparador: o consumidor executa uma função real com as respostas anteriores/posteriores da API. Alguns manifestos estão deliberadamente incorretos, e as funções não os consultam.

O código do servidor de referência aplica uma tabela congelada de acesso diretamente. Não chama o avaliador `auth_policy.evaluate`, que é utilizado pelo candidato de autorização. A referência usa a resposta HTTP da sonda, não o resultado devolvido pelo avaliador.

São **12 casos de consumidor derivados de seis funções**, do mesmo autor, em laboratório. Não é benchmark externo, teste cego, holdout independente de autoria, validação empresarial ou prova de ganho significativo. Essa limitação é parte do resultado, não apenas uma nota de rodapé.

## Perguntas separadas

- **Impacto condicionado:** recebendo a resposta v2, a tarefa que completava em v1 passa a lançar exceção em algum input preparado? Não é previsão de falha em produção. O teste funcional usa um leitor autorizado da fixture para obter as duas respostas, separando compatibilidade de autorização.
- **Uso na janela anterior:** houve chamada concluída? Referência por recibos HTTP completos do roteiro, que não são entregues ao candidato.
- **Permissão no endpoint:** a sonda autorizada conclui, é negada ou fica indeterminada? O último estado ocorre quando a fonte de política não está disponível.

Todas as condições conhecem a mesma alteração proposta da API. Não recebem resultados posteriores de regressão, `truth.json`, código do consumidor ou spans das sondas de referência.

## Fontes e condições

**C:** manifesto de consumo. **R:** spans CLIENT/SERVER anteriores à mudança, incluindo instrumentação manual de nomes de campos acessados. **A:** snapshot da política local.

Combinações: C, R, A, CR, CA, RA, CRA. A instrumentação de nomes de campos é adicional e específica deste experimento: não pode ser presumida em traces HTTP genéricos. A regra experimental que interpreta indexação direta de um campo removido como risco é uma heurística, não garantia.

Seis vistas: base, runtime ausente, declaração vencida, política incompleta, spans repetidos e runtime de outro ambiente. Elas reutilizam as mesmas referências e não são contadas como 72 consumidores independentes.

## Resultado base: impacto em 12 casos

| Condição | Respostas corretas | FP | FN | Inconclusivas | Precisão positiva | Positivos recuperados, incluindo abstenções no denominador |
|---|---:|---:|---:|---:|---:|---:|
| C | 6 | 1 | 1 | 4 | 80,0% | 4/8 = 50,0% |
| R | 3 | 1 | 0 | 8 | 75,0% | 3/8 = 37,5% |
| A | 0 | 0 | 0 | 12 | não definida | 0/8 |
| CR | 7 | 2 | 0 | 3 | 71,4% | 5/8 = 62,5% |
| CA | 6 | 1 | 1 | 4 | 80,0% | 4/8 |
| RA | 3 | 1 | 0 | 8 | 75,0% | 3/8 |
| CRA | 7 | 2 | 0 | 3 | 71,4% | 5/8 |

**Não houve superioridade inequívoca.** A combinação identificou um positivo adicional e ampliou a quantidade de respostas corretas, mas a precisão das afirmações positivas piorou. O falso negativo da declaração incorreta virou inconclusivo diante do conflito, não uma correção confirmada. A leitura em um bloco try/except gerou novo falso positivo na heurística de runtime.

A autorização não melhora a previsão de compatibilidade nesta formulação, e isso é esperado: responde outra pergunta. Ela não foi usada para descartar uma incompatibilidade só porque o acesso atual está negado.

## Outros resultados

Na janela de baseline, R e suas combinações identificaram **9 acessos concluídos**, mantendo os três casos sem conclusão observada como desconhecidos para o candidato. O oráculo conhece a ausência no roteiro completo, mas não se concede artificialmente essa cobertura ao preditor.

Na permissão, A e suas combinações acertaram os **11 casos com referência binária**; o décimo segundo permaneceu indeterminado e foi contado à parte. Isso verifica o recorte controlado, não certifica o avaliador para IAM de produção.

Duplicar spans não modificou resultados. Sem runtime, a resposta de uso permaneceu inconclusiva. Declarações vencidas deixaram de sustentar conclusões. Política incompleta conservou a negativa explícita e absteve-se de confirmar permissões. Esses resultados são controles de medição, não descobertas de benefício comercial.

## O que o experimento revelou para o produto

1. **Campo acessado não implica falha:** a função pode tratar a ausência com fallback. Não promover essa heurística de runtime como prova de quebra.
2. **Manifesto completo pode estar errado:** sem outra evidência suficiente, a fusão conserva um falso positivo. Concordância/quantidade de fontes não garante verdade.
3. **Ramos não observados permanecem um limite:** não ver o campo em execução não exclui dependência em outros inputs.
4. **Boa avaliação pode mostrar piora:** preservar os erros e separar cobertura, precisão e desconhecimento é mais útil do que relatar um número agregado favorável.

## Execução e rastreabilidade

Captura de referência: **2026-10-16T18:00:13.655936+00:00 a 2026-10-16T18:00:13.756793+00:00**. Foram 11 tentativas no baseline, **22 spans em 11 traces**, mais 14 requisições de sondas/obtenção de respostas para referência. Nenhum span de oráculo foi entregue ao candidato.

```text
evidence.json SHA-256: b034b44b13d649e21f0b45181e1417fd85273ab9d97d433e3caf5d3d3660c4c1
truth.json SHA-256: e628e47efa63d09f28cf5b3974b800e86d0d33810407082d51fba12038cbcdc3
results.json SHA-256: 5488b533ff85bb17996add9bcd62ef1edf8dc904ad740ea27aac3875838da1e4
```

Protocolo e seis fontes foram congelados por hash antes da coleta. Isso é congelamento local, não pré-registro externo. `truth.json` fica separado; o preditor é executado em subprocesso e recebe só o arquivo de evidência. Não é sandbox de segurança contra código hostil. O output preserva cada resposta em CSV e as contagens em JSON, sem payloads ou credenciais.

**167 testes locais passaram nesta rodada:** 124 regressões anteriores (28 L1, 24 adaptador, 24 histórico, 48 L5) e 43 testes de separação, coleta e métricas. A falha inicial de um teste que buscava um nome também em docstrings foi corrigida usando AST para verificar acessos reais; não houve alteração da heurística para apagar resultados adversos. Não houve teste novo de navegador porque a interface não mudou.

O workflow de avaliação adicionado roda esses testes com acesso somente de leitura. Consultar o commit/run antes de afirmar sucesso em CI. Os testes de software medem se o experimento registra corretamente os erros; seu sucesso não significa que as previsões estejam todas corretas.

## Reproduzir

```sh
python -m pip install -r evidence-graph/core/lab-runtime/requirements.txt
python evidence-graph/core/evaluation/run_experiment.py --out evidence-graph/core/evaluation/runs/l6-01
cd evidence-graph/core/evaluation
python -m unittest -v test_experiment
```

Destino existente é recusado. Não há publicação, coleta externa ou reescrita da M3. Saídas ficam em `evaluation/runs/`, ignoradas no Git. O pacote da conversa contém uma execução pronta.

## Próximo ponto

Manter este L6-A como baseline. A próxima rodada deverá melhorar o tratamento de leitura potencial versus falha, explicitar a confiabilidade da declaração e usar uma avaliação nova com casos revisados por outra pessoa. Registrar uma versão nova, sem reescrever os resultados anteriores. Testes de tarefa sem exceção mas com resultado errado também precisam de oráculo próprio.

O L6 completo — contribuição generalizável, casos externos e avaliação com usuários — continua aberto. Não reiniciar visual, abrir hospedagem nova ou usar o edital como pretexto para inserir IA decorativa. A candidatura ao CTE-IA permanece para depois do marco funcional definido pelo proponente.

Ver [protocolo completo](../evaluation/PROTOCOL.md), [reprodução e casos](../evaluation/README.md) e [roadmap](./24_CORE_NEXT_STEPS.md).

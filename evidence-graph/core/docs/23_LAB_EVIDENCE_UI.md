# L2 — Evidências capturadas na experiência de grafo e análise

**Escopo:** adaptador do laboratório L1 para uma cópia isolada da interface M3. Sem merge ou publicação nesta etapa.

## Resultado

O arquivo `run.json` produzido pela execução local é validado e analisado novamente pelo `lab.analyze`. O adaptador gera o catálogo, as relações e os resultados no formato utilizado pela interface. Não lê um `analysis.json` pronto como se fosse prova de execução.

Há dois conjuntos separados, selecionados antes de iniciar a aplicação:

- **Aurora Lab:** 5 ativos, 4 relações e 17 evidências na captura de referência. São três clientes, a API e a tabela SQLite. A API foi executada com dois contratos, preservados nas evidências v1/v2.
- **Grupo Aurora:** o cenário anterior, com 240 ativos e 512 relações, permanece independente. Não foi substituído ou enriquecido silenciosamente com a captura local.

A primeira captura L2 utilizada no pacote ocorreu de `2026-10-15T23:41:18.155683+00:00` a `2026-10-15T23:41:18.583589+00:00`. Ela contém 12 spans em quatro traces de chamadas de negócio. SHA-256 de `run.json`: `f4bb00c68fd5ddf9ddd04c6681befa96c3c71e9ecfdfc80c4695b6f81ae9b7f4`.

Os hashes e os IDs mudam em novas execuções. Hash identifica o conteúdo; não autentica a origem de telemetria de terceiros.

## O que a interface responde

| Cliente | Contrato | Uso anterior · v1 | Teste posterior · v2 |
|---|---|---|---|
| Pedidos | Exige campo removido | Observado | Falhou no teste executado |
| Portal | Não exige o campo removido no contrato declarado | Observado | Passou no teste executado |
| Exportador | Exige campo removido | Não confirmado | Não verificado |

Incompatibilidade, execução e teste de regressão são dimensões distintas. Uma anotação manual não muda o resultado do teste. PASS não é garantia de funcionamento universal. Remover spans não converte desconhecimento em sucesso.

Os detalhes mostram versões, IDs de trace/span e referências JSON Pointer para a captura. A relação API → SQLite exige parentesco, trace, versão e intervalo temporal coerentes. Sua existência não comprova acesso do consumidor a um campo específico.

## Separação e proveniência

`synthetic=false` neste bundle significa que ele não é inteiramente sintético; `provenance.business_data=synthetic` e `telemetry=real_local_execution` detalham as origens. Não foi usado `synthetic=true` apenas para satisfazer o carregador antigo.

Identificadores, rótulos e agrupamento de ativos são mapeados pelo adaptador (`metadata_origin=adapter_mapping`). Responsáveis dos clientes vêm das declarações do laboratório. O agrupamento Plataforma para API/banco é convenção de apresentação, não organização descoberta. Não foram inferidos processos de negócio ou criticidade. Sem avaliação IAM, MCP, agentes, produção ou ganho de precisão comprovado.

As evidências são históricas. Não foram inventados intervalos de validade de contratos. As duas versões da API são agregadas visualmente no mesmo ativo lógico, mas as evidências mantêm a versão e os traces; isso não indica execução simultânea.

## Como reproduzir

Na raiz do repositório, com os requisitos L1 instalados:

```sh
python evidence-graph/core/lab-runtime/lab.py --out evidence-graph/core/lab-runtime/runs/l2
python evidence-graph/core/lab-runtime/build_view.py --run evidence-graph/core/lab-runtime/runs/l2/run.json --out evidence-graph/core/lab-runtime/runs/l2-view
```

Abrir `runs/l2-view/EvidentGraph_L2.html`. Ele inclui os dois conjuntos para leitura offline. O seletor muda a origem e recarrega; não une catálogos. Notas usam chaves distintas por dataset/captura. A pasta de destino deve ser nova: o builder recusa sobrescrita e não altera `preview-m2/`.

## Validação executada

- 28 testes L1, 43 testes M1 e 13 testes Node de exploração executados novamente: 84 passaram.
- 24 testes novos do adaptador: referências, proveniência, perda de evidência, versões, duplicação, mutações, determinismo e preservação da M3.
- 14 testes novos de Chromium/Playwright: grafo/lista, resultados, filtros, detalhes, notas em sessão, exportação Markdown, layout e inicialização separada dos dois conjuntos.
- Total nesta rodada: **122 testes locais aprovados**. Não é CI, teste com usuários ou benchmark empresarial.

Navegação HTTP do Chromium para loopback foi bloqueada com `ERR_BLOCKED_BY_ADMINISTRATOR`. Os testes de interface foram executados por carregamento direto do HTML no DOM. Isso não comprova troca pelo seletor seguida de reload, execução hospedada ou persistência de notas entre recargas. O teste de Grupo Aurora inicializa separadamente a aplicação com a outra fonte; não é apresentado como teste ponta a ponta da troca.

As chamadas HTTP de negócio do L1 foram realmente executadas via cliente Python. O bloqueio do navegador não foi convertido em resultado positivo nem contornado.

## Limites e retomada

O adaptador é restrito ao esquema L1 e a três clientes conhecidos. Não é importador universal, parser independente de código ou validação de autenticidade. A interface consulta resultados recalculados na preparação; não realiza ingestão contínua. Referências `run.json#/...` são auditáveis no arquivo do pacote, não links para sistemas empresariais.

Os testes de regressão e comparador ainda compartilham requisitos declarados, portanto não são benchmark independente. Os arquivos publicados, o dataset M1, Campus Mobile, currículo removido e documentos da equipe permaneceram intactos.

**Próximo passo:** revisar esta ligação no navegador, conferir troca de origem e notas após reload e, então, decidir sobre publicação isolada. Não aumentar conectores ou redesenhar antes dessa revisão.

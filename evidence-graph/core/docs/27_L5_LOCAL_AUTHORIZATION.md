# L5 — autorização local, tentativa e acesso concluído

**Data:** 2026-10-16. **Base:** L4, commit `7fb3ba3910203ed9e9e597182cba074f5c251e2a`.  
**Estado:** implementação de laboratório na branch do PR #3, sem merge ou deploy.  
**Escopo:** continuar o Core; nenhuma candidatura ou adaptação ao edital foi desenvolvida nesta etapa.

## 1. O que foi implementado

A API local agora verifica a identidade por um token opaco efêmero e avalia uma política explícita antes de consultar SQLite. Somente a decisão **ALLOW** permite chegar à consulta. A execução continua em HTTP loopback, com dados fictícios e spans OpenTelemetry emitidos pelo SDK.

A análise separa quatro dimensões: política no instante da captura; tentativa observada; chamada concluída; incompatibilidade do contrato/teste após remover `cliente_id`. O componente de apresentação reutiliza os fontes da M3 em uma cópia separada. O HTML é leitor da captura; não é o mecanismo que protege a API.

Não foram adicionados IAM corporativo, OAuth, JWT, RBAC, MCP, LLM, acesso por coluna, bloqueio de deploy ou conectores empresariais. A API é o recurso de teste desta etapa. Os consumidores são programas de teste convencionais, não agentes autônomos.

## 2. Cenários executados

| Consumidor | Política local | Execução v1/v2 | Teste de contrato v2 |
|---|---|---|---|
| Cliente de pedidos | Permitido | HTTP 200 nas duas versões; consulta ao banco | Falha: `cliente_id` foi removido |
| Portal de consulta | Negado por regra explícita | HTTP 403 nas duas versões; sem consulta ao banco | Não executado/verificado |
| Exportador financeiro | Indeterminado: fonte de política indisponível para esse sujeito | HTTP 503 nas duas versões; bloqueio preventivo, sem consulta | Não executado/verificado |
| Rotina de conciliação | Permitido no recorte | Não foi executada no experimento | Não verificado |

O Portal desta captura está sujeito a uma política diferente do laboratório L1. Não mudamos retroativamente o resultado anterior: os arquivos e conjuntos de evidência são distintos.

Uma chamada bloqueada não é classificada como leitura bem-sucedida. O Exportador continua tendo incompatibilidade no contrato declarado, embora não tenha conseguido executar o teste posterior. A Conciliação demonstra que uma permissão não comprova uso.

## 3. Política e identidade

`auth_policy.py` avalia apenas o conjunto exato identidade + `customers:read` + `aurora:api:customers` + ambiente + instante. Uma regra DENY tem precedência sobre ALLOW. Ausência de regra em snapshot explicitamente completo produz DEFAULT_DENY. Snapshot ausente, inválido, fora de validade ou fora de escopo produz INDETERMINATE. Um snapshot incompleto não prova ALLOW, porque pode omitir uma negativa.

A API responde 403 a DENY; 503 a INDETERMINATE com identidade resolvida; 401 quando a credencial não resolve uma identidade. São convenções deste laboratório, não uma implementação normativa completa de autorização. O bloqueio ocorre antes do SQL, incluindo os casos de incerteza.

Os tokens são gerados em memória a cada execução. Não são salvos no JSON, no HTML, nos logs de evidência ou no Git. O nome informado em um cabeçalho não autentica o cliente: o teste tenta usar o nome de Pedidos com a credencial do Portal e recebe 403.

O registro de identidades e as políticas são fixtures controladas. Isso não substitui um provedor de identidade real, TLS, gestão de chaves, revogação distribuída, auditoria de produção ou análise de ameaças de uma implantação empresarial. O servidor só escuta em 127.0.0.1 e usa portas temporárias.

## 4. Como a evidência é interpretada

O analisador valida a captura e recalcula a resposta; não importa `analysis.json` como fonte de verdade. Requer correlação CLIENT → SERVER pelo trace, parentesco, versões, intervalo, ambiente, rota e identidade verificada no servidor. Um rótulo declarado no CLIENT isolado não confirma acesso.

A decisão aplicada registrada no servidor permanece separada da decisão recalculada do snapshot. Se o snapshot está ausente ou discordante, a conferência é `CONFLICT_OR_MISSING`, sem apagar a observação histórica nem fingir que há uma política completa.

A consulta API → SQLite é exibida apenas com a cadeia correlacionada de uma chamada concluída. Ela não prova que um consumidor recebeu uma coluna sensível. A avaliação permanece no endpoint; `field_access` continua não avaliado.

A validação e os checksums não autenticam capturas de terceiros. O importador é delimitado ao esquema L5 e quatro consumidores conhecidos, não um parser seguro universal de telemetria arbitrária.

## 5. Visualização

O novo conjunto chama-se **Aurora Acesso**, com **10 ativos e 9 relações**: quatro consumidores, suas quatro identidades, uma API e uma tabela. Identidades são relações estruturais, não chamadas de runtime. O mapa inicialmente esconde os nós técnicos; a opção de colunas/identidades permite abri-los.

O cenário maior **Grupo Aurora**, com 240 ativos e 512 relações, continua selecionável e independente. Não é substituído, unido ao laboratório ou apresentado como se tivesse novas integrações reais.

Selecionar um consumidor mostra a política e o acesso concluído no painel lateral. Detalhes exibem v1/v2, regra/razão, tentativa, decisão aplicada, resposta HTTP e teste de contrato. A lista mantém incompatibilidade, observação e autorização como dimensões diferentes. Exportação Markdown inclui a origem, os filtros, traces e notas locais.

As notas ficam separadas pelo identificador do dataset e hash da captura. Marcar uma verificação não altera o resultado registrado. A aparência base, o grafo, a lista, o inventário e a navegação da M3 foram preservados.

## 6. Reprodução

Com as dependências existentes de `lab-runtime/requirements.txt`, na raiz do repositório:

```sh
python evidence-graph/core/lab-runtime/auth_lab.py --out evidence-graph/core/lab-runtime/runs/l5-01
python evidence-graph/core/lab-runtime/build_auth_view.py --run evidence-graph/core/lab-runtime/runs/l5-01/run.json --out evidence-graph/core/lab-runtime/runs/l5-01-view
```

Abrir `runs/l5-01-view/EvidentGraph_L5.html`. A captura e o viewer recusam sobrescrita. São artefatos históricos locais; não há atualização contínua ou deploy.

O esquema de captura L5 é separado do L1. O comando de histórico L4 continua dedicado ao L1: não passamos dados de autorização para ele fingindo compatibilidade. Generalizar o histórico para outros esquemas é trabalho posterior e deve preservar as versões anteriores.

## 7. Registro de execução e testes

Captura de referência desta entrega: **2026-10-16T17:24:45.778137+00:00 a 2026-10-16T17:24:46.339170+00:00**. Foram seis tentativas de negócio, **14 spans em seis traces**, e duas consultas SQL correspondentes às duas chamadas permitidas de Pedidos.

SHA-256 de `run.json`:

```text
30b88d3f7127e08a165cbc2255db60b4f9cbd2dccc1a85e7e7a9291f8dd1124d
```

**124 testes locais passaram nesta rodada:** 28 L1, 24 adaptador L2, 24 histórico L4 e 48 novos L5. Não são somados a testes históricos que não foram reexecutados. Os sete novos arquivos de código e testes foram conferidos por hash de blob contra os arquivos locais.

A suíte L5 cobre política permitida/negada/indeterminada, validade, escopo, política incompleta, prioridade de negativa, credencial inválida/ausente, tentativa de falsificar nome, bloqueio antes do SQL, perda de telemetria, divergência de snapshot, preservação dos arquivos M3 e referências do grafo.

Uma tentativa de navegador HTTP local foi bloqueada por `ERR_BLOCKED_BY_ADMINISTRATOR` e registrada como erro, não sucesso. A inspeção visual offline por carregamento do HTML no DOM confirmou exibição, detalhes, nota em sessão e exportação filtrada; isso não valida recarga HTTP. Dez novos testes de navegador HTTP foram adicionados ao workflow de CI, junto aos 12 anteriores. Consultar o run do commit correspondente para saber se passaram; a existência do workflow não demonstra sucesso.

Nenhum teste nesta etapa representa entrevista, benchmark independente, ganho de precisão ou certificação de segurança.

## 8. Limites e próximo ponto

L5 fecha o recorte local de autorização por endpoint. Não transforma o EvidentGraph em controle de segurança de produção. A validação é sobre o comportamento do código e os casos preparados; a avaliação independente da fusão continua pendente.

Próximo ponto: revisar este recorte e o resultado HTTP do CI; então preparar **L6, com casos de referência independentes e comparação das fontes isoladas/combinação**, conforme `24_CORE_NEXT_STEPS.md`. Uma ferramenta MCP real pode ser um recorte futuro, não foi implementada ou simulada como tal nesta entrega.

O Pages, fontes M3, L1/L4, Campus Mobile, equipes, dados pessoais e edital CTE-IA não foram modificados. A candidatura será trabalhada separadamente após o marco funcional, conforme a orientação do proponente.

## Referências técnicas consultadas

- OWASP Authorization Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html — checagem por requisição e negação por padrão.
- OpenTelemetry Python instrumentation: https://opentelemetry.io/docs/languages/python/instrumentation/ — emissão de spans pelo SDK.
- OpenTelemetry Python propagation: https://opentelemetry.io/docs/languages/python/propagation/ — correlação de contexto entre cliente e servidor.

Essas fontes orientam práticas técnicas; não validam a implementação do EvidentGraph nem demonstram novidade.

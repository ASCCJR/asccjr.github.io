# EvidentGraph — Cenários e respostas esperadas

**Data:** 2026-10-13 · **Versão:** 0.1.0  
**Fonte de escopo:** [12_PRODUCT_UX_VISION.md](./12_PRODUCT_UX_VISION.md).  
**Oráculo independente:** [expected.json](../demo-data/expected.json).

## 1. O que a próxima interface precisa responder

Não basta mostrar nós. O usuário precisa saber **qual consequência verificar, quem procurar e qual informação falta**. Estes cenários congelam esse contrato antes da implementação das telas.

As entradas são produzidas pelo gerador; o oráculo foi escrito separadamente, e não extraído do analisador. Os testes comparam a saída calculada com o oráculo e também alteram evidências para verificar mudança de comportamento. Isso valida nossa especificação sintética, não a verdade de um ambiente real.

Todos os cenários usam produção fictícia, versões `1.0 → 2.0`, relógio `2026-10-13T12:00:00Z` e janela `2026-09-13T12:00:00Z` a `2026-10-13T12:00:00Z`.

## 2. CHG-001 — Remover `cliente_id` da API de clientes

**Pergunta:** o que exige revisão antes da publicação dessa mudança?

**Recurso:** `api-clientes-v2`, exibido como `GET /customers/{id} v2`. O `v2` pertence ao nome da rota/produto; as versões `1.0/2.0` são snapshots do contrato nessa simulação.

| Consumidor | Resultado de impacto | Atividade | Responsável | Ação |
|---|---|---|---|---|
| Serviço de pedidos | Incompatibilidade identificada: contrato exige `cliente_id` | Observado | Comercial | Validar migração do contrato |
| Agente de atendimento, via MCP | Impacto possível: não sabemos se depende do campo | Caminho observado com correlação | Atendimento | Testar consumo do campo |
| Exportador financeiro | Inconclusivo: dependência configurada sem contrato de campo | Cobertura insuficiente | Financeiro | Verificar rotina, contrato e cobertura |
| Portal de acompanhamento | Nenhuma incompatibilidade no contrato avaliado | Observado | Atendimento | Registrar limites da verificação |

### Resumo operacional esperado

> Quatro consumidores conhecidos foram identificados no recorte. Um tem incompatibilidade de contrato identificada, um tem impacto possível, um permanece inconclusivo e um não apresenta incompatibilidade no contrato avaliado. Três têm uso observado; para o exportador financeiro, faltam informações de execução. A análise não autoriza a publicação automaticamente.

Essas contagens são calculadas. A ferramenta MCP é intermediária e não vira um quinto consumidor. O agente tem caminho `agent-atendimento → tool-atendimento → api-clientes-v2` com o mesmo identificador sintético de execução nos dois elos.

### Critérios de não engano

O contrato completo do Portal exige `nome` e `situacao`, não `cliente_id`. Isso sustenta apenas a verificação do contrato fornecido, não a afirmação de que nenhum trecho do código usa o campo. O agente chamar uma API tampouco comprova que recebeu um dado sensível.

### Alterações que os testes exercitam

| Mutação | Resultado esperado |
|---|---|
| Retirar o contrato do serviço de pedidos | De incompatibilidade identificada para impacto possível |
| Retirar sua evidência de execução e manter cobertura completa | Incompatibilidade permanece; atividade vira “não observado na janela” |
| Retirar também a cobertura | Atividade vira desconhecida |
| Trocar o campo removido para `nome` | Portal passa a ter incompatibilidade; pedidos deixa de ter incompatibilidade no contrato avaliado |
| Trocar o contrato por uma versão anterior, expirada ou de outro ambiente | Contrato é desconsiderado, não tratado como confirmação |
| Adicionar contrato válido contraditório | Impacto inconclusivo, com conflito visível |
| Usar traces não correlacionados nos elos do agente | Caminho completo deixa de ser classificado como observado |
| Adicionar um segundo caminho do agente até a mesma API | Ainda quatro consumidores; dois caminhos para o agente |

## 3. CHG-002 — Remover `quantidade_prevista` da saída de previsão

**Pergunta:** o que pode ser afetado na reposição se a estrutura dos resultados mudar?

**Recurso:** `tbl-previsao-saida`, produzido pela rotina de previsão.

| Consumidor | Impacto | Atividade | Responsável |
|---|---|---|---|
| Dashboard de reposição | Incompatibilidade identificada: contrato exige o campo | Observado | Operações |
| Rotina de reposição | Possível: uso da tabela observado, contrato de campo não informado | Observado | Operações |

**Contagem esperada:** dois consumidores. A rotina que escreve a previsão não é classificada como consumidor afetado só por escrever nessa tabela.

A futura interface deverá explicar a consequência no processo de reposição, permitindo explorar dados e modelo como contexto. Não deve prometer avaliar qualidade da previsão, abrir variáveis do modelo como tela principal ou inferir que toda previsão ficou incorreta.

## 4. CHG-003 — Propor desativação da API legada

**Pergunta:** o que falta verificar antes de desligar esse recurso?

**Recurso:** `api-legado`. Há dependência configurada da rotina mensal de fechamento (`job-financeiro-cobranca`), sem execução observada e com cobertura parcial.

**Resultado esperado:** um consumidor conhecido, impacto inconclusivo e atividade desconhecida. A equipe Financeiro precisa verificar a rotina e sua cobertura. A ausência de observação no recorte não demonstra que a API pode ser removida.

A ação continua humana. Não há botão ou comando de desativação executado pelo analisador.

## 5. Teste negativo — API de homologação sem cobertura

Selecionar `api-clientes-qa` no ambiente `qa-demo` retorna zero consumidores conhecidos no recorte, sem cruzar com produção. O resultado mantém `scope_complete=false` e a ressalva de cobertura. **Zero resultados não significa zero dependências reais.**

## 6. O que já está pronto para consumo futuro

O analisador gera resultados estruturados com consumidor, nome, equipe, processo, criticidade declarada, impacto, atividade, caminhos, referências, limitações e próximo passo. Também gera relatórios Markdown de conferência.

O resultado não calcula IAM, acesso a CPF, propagação arbitrária de campos por pipelines, causa raiz ou economia financeira. Não existem integrações reais, usuários operacionais nem testes de usabilidade concluídos.

## 7. Próximo marco

Construir **M2: a fatia funcional de CHG-001** — selecionar mudança, exibir resposta, filtrar consumidores, abrir evidências e responsáveis, registrar verificações e exportar. Usar este oráculo para testes de equivalência caso a lógica seja portada para JavaScript. A interface atual só será substituída após revisão, conforme UX-15.

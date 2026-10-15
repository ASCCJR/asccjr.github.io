# Retomada do Core — Pages mantido e primeiro laboratório de coleta

**Data:** 2026-10-15. **Checkpoint:** L1, independente da M3 visual.

## Decisão de continuidade

O proponente decidiu abandonar a migração para Sites e continuar o EvidentGraph no repositório existente. O PR #2 de preparação foi encerrado sem merge. Sua branch foi preservada como histórico; não é dependência de desenvolvimento. A exclusão do projeto no Sites fica com o usuário, que informou que a fará; não foi executada por esta revisão.

Mantemos o GitHub Pages para a experiência atual. Não haverá outra reescrita visual ou troca de plataforma. O grafo, a lista e o Grupo Aurora ficam preservados. A hospedagem futura de backend/coletores será decidida quando existir requisito concreto.

## Entrega técnica

Foi criado `core/lab-runtime/`, com API e clientes de teste executados por HTTP real sobre loopback, banco SQLite descartável, contratos OpenAPI obtidos da API e instrumentação manual pelo SDK OpenTelemetry. Não usa credenciais, serviços externos nem dados de empresa.

As duas versões da API diferem na presença de `cliente_id`. O laboratório compara o contrato e executa verificações de consumo. Os requisitos do consumidor são declarados e fornecidos ao teste, não descobertos automaticamente no código.

| Cliente | Incompatibilidade no contrato | Uso antes da alteração | Resultado do teste após alteração |
|---|---|---|---|
| pedidos | Identificada | Observado | Verificação de campo falhou |
| portal | Não identificada nesse contrato | Observado | Verificação executada passou |
| exportador | Identificada | Não confirmado | Não executado |

A tabela é resultado desta execução controlada, não resultado obtido em cliente. O SDK produziu **12 spans em 4 traces**: duas chamadas de negócio por versão, com span de cliente, servidor e consulta SQLite. As duas buscas HTTP dos OpenAPI não entram nessa contagem.

**Diferença para a M1:** os dados de negócio continuam fictícios, mas os registros de execução agora foram emitidos por software realmente executado, e não preparados como fixtures. Não se deve chamar esses registros de telemetria empresarial.

## Verificação realizada

Execução de referência: `2026-10-15T23:30:15.727030+00:00` a `2026-10-15T23:30:16.162675+00:00`, Python 3.13.5.

- 28 testes do laboratório passaram localmente, incluindo execução real e controles negativos por mutação.
- 43 testes M1 passaram novamente.
- 13 testes Node de exploração passaram novamente.
- Total desta rodada: **84 testes**, não incluindo reteste da interface Chromium.

Hash SHA-256 do `run.json` da execução de referência incluída no pacote de evidências entregue na conversa:

`cab655ca006f779c348277b0a0baf0781c637f47bb41b551af8726eac67ec2c2`

Os artefatos completos dessa execução ficam no pacote entregue, não no Git. Novas execuções têm timestamps e IDs de trace diferentes; espera-se o mesmo comportamento, não o mesmo hash. Não foi alegada execução de CI nesta etapa.

Os testes verificam parent/trace, versão, intervalo temporal, ausência de spans, contratos insuficientes, duplicação de registros, privacidade dos spans, hashes, resposta 404, encerramento dos sockets e recusa de sobrescrita.

## Conferência do Pages

A URL de avaliação foi tentada nesta sessão, mas o ambiente não conseguiu resolver o host; a ferramenta web também não conseguiu abrir a página. **Isso é uma limitação da verificação, não evidência de que o site está fora do ar.** A navegação publicada e a persistência após recarregar continuam pendentes de teste no navegador do usuário. Não houve contorno do bloqueio nem alegação de sucesso.

## Limites preservados

Não há adaptação para a UI/M1, grafo de laboratório carregado no site, autorização efetiva, prova de vazamento, detector universal de mudança ou validação de mercado. SQLite é uma simplificação deste primeiro laboratório; não substitui a arquitetura-alvo de PostgreSQL. Não há agente generativo neste recorte.

Os contratos usados pelo cliente e pelo comparador compartilham a mesma declaração, portanto esta rodada demonstra funcionamento da coleta/correlação, não benefício estatístico de evidence fusion. A revisão do site e a avaliação com pessoas não foram substituídas pelo teste técnico.

## Próximo passo exato

1. Usar `22_ROTEIRO_AVALIACAO_M3.md` para conferir a navegação hospedada e realizar sessões exploratórias, sem inventar resultados.
2. Revisar o pacote L1 e seu contrato separado; depois definir um adaptador pequeno para apresentar as evidências coletadas no contexto do grafo, distinguindo laboratório e dataset fictício.
3. Antes de alegar contribuição, desenhar comparação independente entre configuração/contrato, runtime e autorização, com casos positivos, negativos e desconhecidos.

Não recriar Sites, não retirar o lineage, não crescer o inventário por estética, não trazer dados profissionais/pessoais para o repositório. Campus Mobile, documentos acadêmicos, nomes da equipe e HTML/CSS/JS publicados não são alterados por esta entrega.

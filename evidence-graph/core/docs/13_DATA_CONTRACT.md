# EvidentGraph — Contrato de dados da demonstração

**Versão:** 0.1.0 · **Marco:** M1 · **Data:** 2026-10-13  
**Base:** [Visão de produto e UX](./12_PRODUCT_UX_VISION.md).  
**Implementação:** [model.py](../demo-data/model.py), exclusivamente com dados sintéticos.

## 1. O que foi construído

Um gerador determinístico de **240 ativos e 512 relações**, validação de integridade e um analisador de referência para os três casos delimitados na visão de UX. O resultado pode ser exportado em JSON e Markdown. Ainda não há uma nova interface, coletores reais ou avaliação com usuários.

O catálogo é maior que os recortes de análise: os cenários selecionam um recurso e um conjunto explícito de relações, não exibem a empresa inteira. Gerar e testar esse catálogo não comprova escalabilidade de produção.

A especificação inicial sugeria 600–900 relações como referência ajustável. Ficamos em **512**, produzidas por modelos de domínio e vínculos de negócio explícitos. Não foram adicionadas ligações arbitrárias para atingir uma quantidade decorativa.

## 2. Pacote versionado e geração

Os arquivos-fonte ficam em `core/demo-data/`. O gerador não usa rede, relógio do computador, aleatoriedade ou credenciais. A reprodução decorre de templates fixos, não de dependência em uma semente aleatória.

```sh
cd evidence-graph/core/demo-data
python -m unittest -v test_model
python model.py --out build
```

Requisito: Python 3.10 ou superior; somente biblioteca padrão. A pasta `build/` é regenerável e não fica versionada. O gerador, o oráculo `expected.json`, os testes e este contrato são versionados.

Saídas: `enterprise.json`, `manifest.json`, `CHG-001.json/.md`, `CHG-002.json/.md`, `CHG-003.json/.md`. São arquivos de dados e relatórios, não um novo site.

## 3. Entidades e significado dos campos

| Coleção | Campos principais | Regra |
|---|---|---|
| Dataset | `schema_version`, `dataset_version`, `synthetic`, `clock` | `synthetic=true`; relógio fixo `2026-10-13T12:00:00Z` |
| Ativos | `id`, `kind`, `name`, `domain`, `owner`, `environment`, `version`, `processes`, `criticality` | Identificador estável; responsável e processos são referências explícitas, não inferências pelo nome |
| Domínios | `id`, `name` | Comercial, Atendimento, Operações, Financeiro, Dados, Plataforma |
| Equipes | `id`, `domain`, `name` | Equipes fictícias; não há dados de pessoas |
| Processos | `id`, `domain`, `name` | Contextualizam a tarefa; ficam fora da contagem de ativos |
| Relações | `id`, `source`, `target`, `kind`, `evidence_ids` | Direção e tipo preservados; referências válidas; sem atravessar ambientes |
| Evidências | `id`, `family`, `source`, `origin_id`, `reference`, `subject`, `target`, versões, ambiente, validade, coleta, `claim`, `details` | Referências `synthetic://`; proveniência preservada; cópias não contam como novas origens |
| Fontes | `id`, `family`, `synthetic`, `max_age_hours` | O limiar de 48 horas é parâmetro do cenário, não regra universal |
| Cobertura | relação, fonte, estado, início/fim, coleta, versões, ambiente | `complete`, `partial`, `unavailable`; cobre a relação e a janela, não toda a empresa |
| Mudanças | recurso, operação, campo, versões, ambiente, janela, relações consultadas, limites | Operações iniciais: `remove_field`, `retire`; escopo fechado |
| Resultado | consumidores, caminhos, evidências, processos, responsáveis, impacto, atividade, limites, contagens | Consumidores deduplicados; não equivale a garantia de publicação segura |

Este é um **contrato lógico com validador Python**, não uma implementação do padrão JSON Schema. Chaves obrigatórias, enums, referências, tipos de ponta de relação e intervalos relevantes são verificados por `validate()`; ele não é um sanitizador de toda entrada arbitrária de produção.

## 4. Inventário gerado

| Tipo | Quantidade |
|---|---:|
| Aplicações | 12 |
| APIs | 28 |
| Serviços | 24 |
| Pipelines/jobs | 24 |
| Tabelas | 52 |
| Colunas selecionadas | 48 |
| Dashboards | 12 |
| Modelos | 8 |
| Agentes | 8 |
| Servidores MCP | 4 |
| Ferramentas MCP | 4 |
| Identidades | 16 |
| **Total** | **240** |

As 48 colunas não representam todos os campos de todas as tabelas. Há uma API de homologação deliberadamente sem coleta nem consumidores conhecidos para testar resultado vazio. Relações entre produção e homologação são rejeitadas.

Vínculos principais: gravação operacional em dados brutos, transformações para dados tratados, leitura por painéis, treinamento de modelos, uso de modelos em rotinas, agentes/ferramentas e entregas entre pedidos, pagamento, expedição e atendimento. A cadeia de previsão chega à tabela de resultados e ao dashboard de reposição.

Os cinco planos de evidência estão no vocabulário. Isso **não significa que todos já sejam avaliados**: há evidências sintéticas de configuração, código, lineage e runtime; **autorização não está implementada no analisador**. `HAS_IDENTITY` registra associação, não permissão efetiva.

## 5. Direção das relações

| Relação | Direção armazenada | Tratamento inicial |
|---|---|---|
| `CALLS` | Consumidor → API/serviço | Busca reversa de consumidores |
| `USES_TOOL` | Agente → ferramenta | Conecta o agente ao caminho; ferramenta é intermediária |
| `READS` | Consumidor → tabela | Busca reversa na revisão de saída analítica |
| `WRITES` | Produtor → tabela | Contexto; não torna o produtor consumidor afetado |
| `DERIVES_TO` | Origem → derivado | Lineage para exploração futura; não é chamada |
| `CONTAINS` | Tabela → coluna | Estrutura; não é observação de leitura de campo |
| `ROUTES_TO` | API → serviço | Contexto; não propaga automaticamente remoção de campo |
| `HAS_IDENTITY` | Ativo → identidade | Contexto; não autoriza acesso |
| `HOSTS` | Servidor MCP → ferramenta | Estrutura |
| `USES_MODEL` | Rotina/agente → modelo | Contexto de execução |
| `TRAINED_ON` | Modelo → tabela de treinamento | Proveniência; não prova acesso em uma inferência específica |

A análise inicial **não é traversal universal do catálogo**. Usa `CALLS`/`USES_TOOL` em CHG-001/003 e `READS` em CHG-002. Não propaga uma quebra por todo o negócio sem mapeamento de contrato/campo. `scope_complete=false` permanece explícito mesmo quando todos os caminhos do recorte foram percorridos.

## 6. Evidência, tempo e desconhecimento

Uma evidência só entra no resultado se corresponder ao ambiente e versões dos ativos, tiver validade no relógio simulado e coleta suficientemente recente para a fonte. A validade termina em intervalo aberto: uma evidência que expira exatamente no relógio já não é válida.

`collected_at` é momento de coleta, não o momento da chamada. O evento de runtime tem `details.at` e deve estar na janela consultada. Para atribuir um caminho de várias chamadas à mesma execução, os elos precisam compartilhar `trace_id`. Spans de execuções diferentes não viram uma execução ponta a ponta.

Para cobertura, vence o registro mais recente; empate conserva o estado mais restritivo. Cobertura completa e nenhum evento no recorte permitem **“não observado na janela”**, não “não existe”. Eventos sem correlação ponta a ponta ou lacunas levam a `UNKNOWN`.

## 7. Estados da resposta

**Impacto** e **atividade** são separados. Um consumidor pode ter incompatibilidade de contrato mesmo sem uso observado.

| Estado de impacto | Interpretação |
|---|---|
| `INCOMPATIBILITY` | Contrato válido do consumidor exige o campo que será removido |
| `NO_INCOMPATIBILITY` | Contrato declarado completo não exige o campo; nenhuma incompatibilidade nesse contrato, não garantia sobre todo o código |
| `POSSIBLE` | Uso observado, mas incompatibilidade específica não demonstrada |
| `INCONCLUSIVE` | Falta evidência suficiente ou existem contratos conflitantes |

`required_fields` representa requisitos declarados de contrato, não uma análise exaustiva do código nem campos efetivamente retornados. `exhaustive=false` impede usar ausência de um campo como prova negativa de contrato. Contratos válidos que discordam produzem conflito; versões antigas não são combinadas silenciosamente com atuais.

Atividade: `OBSERVED`, `NOT_OBSERVED`, `UNKNOWN`. Autorização e acesso efetivo ao campo ficam sempre `NOT_EVALUATED` nesta versão. Nenhum retorno afirma vazamento, causa de incidente ou bloqueio executado.

## 8. Contagem e casos de borda

Ferramentas MCP intermediárias aparecem no caminho e nas evidências, mas não são somadas como consumidores finais adicionais. Vários caminhos para o mesmo ativo preservam o ativo uma vez e todos os caminhos encontrados.

Ciclos são tratados sem revisitar um nó no mesmo caminho. Limites de profundidade e de caminhos interrompem a exploração e sinalizam `truncated=true`. A lista truncada não pode ser apresentada como cobertura completa.

Os resultados de referência, incluindo oráculos independentes e limitações, estão em [14_SCENARIOS_AND_EXPECTED_RESULTS.md](./14_SCENARIOS_AND_EXPECTED_RESULTS.md).

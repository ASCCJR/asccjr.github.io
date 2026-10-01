# EvidentGraph — resumo para feedback técnico

## Contexto

O **EvidentGraph** é um projeto de pesquisa aplicada em engenharia de software, dados e IA.

A ideia surgiu a partir de um problema recorrente em ambientes corporativos: dependências importantes ficam espalhadas entre várias fontes diferentes — código, APIs, catálogos de dados, IAM/permissões, lineage e telemetria de runtime.

Uma ferramenta pode saber que uma API existe. Outra sabe quem tem permissão para chamá-la. Outra registra chamadas em produção. Outra conhece a relação entre um serviço e uma tabela. O problema é que essas evidências normalmente ficam separadas.

## Hipótese central

A hipótese do projeto é que **correlacionar essas evidências em um mesmo grafo, preservando a origem e o tipo de cada relação**, pode melhorar a análise de dependências e impacto de mudanças.

Em vez de representar apenas:

```text
A DEPENDE_DE B
```

o sistema tentaria distinguir, por exemplo:

```text
Declarado     SIM
Código        SIM
Autorizado    SIM
Runtime       NÃO OBSERVADO
Lineage       SIM
```

ou:

```text
Declarado     NÃO
Código        NÃO
Runtime       SIM
```

Nesse segundo caso, a divergência entre as fontes seria tratada como uma descoberta, e não escondida.

## Três perguntas que orientam o projeto

### CAN IT?
Um agente, serviço, aplicação ou identidade consegue alcançar determinado recurso?

Aqui entram topologia + identidade + autorização.

### DID IT?
Esse caminho realmente aconteceu em produção?

Aqui entram traces, logs, chamadas de ferramentas e consultas a banco.

### WHAT BREAKS?
Se uma API, schema, ferramenta, política ou serviço mudar, quem pode ser afetado?

A ideia é diferenciar dependências apenas potenciais das que estão efetivamente ativas.

## Por que agentes de IA aparecem bastante na demo

Agentes são um bom caso de uso porque combinam vários elementos ao mesmo tempo:

```text
Agente
→ identidade
→ permissões
→ MCP/tool
→ API
→ serviço
→ banco/dado
```

Isso torna visível a diferença entre:

- o que o agente está configurado para usar;
- o que ele tem permissão para usar;
- o que ele realmente usou;
- quais dados estão no caminho.

Mas o projeto não é limitado a agentes. Aplicações, serviços e pipelines continuam sendo entidades de primeira classe.

## Estado atual

Hoje o projeto está em **pesquisa aplicada / pré-MVP**.

Já existe um protótipo sintético que demonstra:

- Agent Review;
- CAN IT?;
- DID IT?;
- WHAT BREAKS?;
- autorização separada de runtime;
- dependência oculta encontrada em runtime;
- blast radius com dependência ativa vs. dormente.

O protótipo usa dados fictícios. Ainda não há collectors reais.

## Arquitetura que estamos considerando

Fontes:

- OpenAPI / contratos;
- GitHub / código;
- IAM, OAuth scopes e RBAC;
- OpenTelemetry;
- metadata e query logs de banco;
- MCP configuration;
- plataformas como Databricks.

Pipeline conceitual:

```text
fontes
  ↓
collectors
  ↓
normalização
  ↓
entity resolution
  ↓
reconciliação de evidências
  ↓
grafo
  ↓
CAN IT? / DID IT? / WHAT BREAKS?
```

Stack pensada para o primeiro MVP:

- Python / FastAPI
- Neo4j / Cypher
- PostgreSQL
- OpenAPI
- OpenTelemetry
- MCP Python SDK
- Docker Compose

## O que já pesquisamos sobre concorrência

A ideia ampla de "ligar dados, APIs, serviços e agentes em um grafo" **não é nova**.

Já existem soluções maduras como:

- DataHub;
- Atlan;
- Databricks Unity Catalog + Unity Gateway;
- Holistic AI;
- Sensedia;
- outras plataformas de governança, observabilidade e segurança.

Por isso, o projeto deixou de tentar se diferenciar pelo grafo em si.

A hipótese mais específica passou a ser:

> **cross-source / cross-control-plane evidence fusion**

Ou seja: verificar se correlacionar evidências vindas de sistemas diferentes, mantendo provenance, conflito, confiança e freshness, produz uma análise melhor do que usar apenas metadata/catalog ou apenas runtime.

Databricks, por exemplo, pode ser tanto benchmark quanto uma futura fonte de evidência para o EvidentGraph.

## Primeiro experimento real que estamos considerando

Em vez de tentar mapear uma empresa inteira, começar com um recorte pequeno:

```text
1 agente
→ 1 identidade
→ 1 MCP/tool
→ 1 API
→ 1 serviço
→ 1 banco
```

E comparar três condições:

1. metadata/config apenas;
2. metadata + runtime;
3. metadata + runtime + autorização.

Métricas possíveis:

- precision;
- recall;
- falsos positivos;
- falsos negativos;
- freshness;
- evidence coverage;
- tempo para responder uma pergunta de impacto.

## Feedback que eu gostaria de receber

Tenho principalmente estas dúvidas:

1. **A formulação tem substância suficiente como problema de engenharia de software/pesquisa aplicada?**
2. **O recorte de evidence fusion faz sentido como contribuição técnica, ou ainda está amplo demais?**
3. **Qual seria o menor experimento convincente para demonstrar valor técnico sem tentar integrar uma empresa inteira?**
4. **Entity resolution entre fontes heterogêneas deveria fazer parte do primeiro MVP ou ficar fora do escopo inicial?**
5. **Você vê algum risco arquitetural importante nessa abordagem que eu esteja subestimando?**
6. **Esse problema te parece mais próximo de observabilidade, arquitetura, segurança, data governance ou software intelligence?**
7. **Se você fosse orientar esse projeto, qual parte reduziria primeiro?**

## Link da demo

https://asccjr.github.io/evidence-graph/

A demo é sintética e serve apenas para comunicar a hipótese e os fluxos principais.

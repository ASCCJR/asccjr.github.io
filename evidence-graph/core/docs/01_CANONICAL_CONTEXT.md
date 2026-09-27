# Canonical Context — EvidentGraph

**Working name:** EvidentGraph  
**Subtitle:** Dependency Intelligence for Data, Software & AI  
**Updated:** 2026-09-27  
**Stage:** applied research / discovery / pre-MVP

## 1. Origin

The project began from an abandoned internal sketch mentioning:
- lineage;
- governance;
- APIs;
- AI agents;
- data flows.

The original interpretation was a broad enterprise graph connecting data, software, and AI.

Competitive research showed that much of that broad category already exists, so the project narrowed to an evidence-fusion research hypothesis.

## 2. Current thesis

EvidentGraph investigates whether correlating **metadata, lineage, code/contracts, authorization, and runtime telemetry** in an evidence-aware graph can improve dependency, reachability, and change-impact analysis.

The graph is not the product by itself. The intended value is **dependency intelligence with provenance and uncertainty**.

## 3. Core questions

### CAN IT?
Can an agent, application, service, or identity reach a resource under current topology and authorization?

### DID IT?
Was that path actually observed in runtime evidence?

### WHAT BREAKS?
What may be affected if an asset, schema, API, MCP tool, policy, model endpoint, or dependency changes?

## 4. Evidence planes

1. **Declared** — config, catalog, manifests.
2. **Static** — source code, SQL, IaC, SDK references, OpenAPI.
3. **Authorization** — IAM, OAuth scopes, RBAC, gateway policies.
4. **Lineage** — data derivation and movement.
5. **Runtime** — OpenTelemetry, gateway traces, database query logs, agent tool calls.

The system should preserve disagreement between evidence sources instead of forcing a single unqualified “truth” edge.

## 5. Key distinction

Possible is not the same as observed.

Examples:
- an agent may be authorized to call 7 APIs but have runtime evidence for only 3;
- a dependency may be declared but dormant;
- a runtime dependency may exist without appearing in the catalog or static analysis;
- lack of runtime evidence must not automatically be interpreted as proof of absence.

## 6. Research question

> To what extent does correlating metadata, lineage, code/contracts, authorization, and runtime telemetry in an evidence graph improve identification of dependencies, access paths, and change impact in architectures that include AI agents?

## 7. Novelty / invention status

Do not claim that these are novel by themselves:
- data lineage;
- knowledge graphs;
- API dependency mapping;
- agent registries;
- MCP governance;
- OpenTelemetry;
- IAM;
- impact analysis;
- runtime observability.

The possible technical contribution is narrower:

> correlate heterogeneous evidence, preserve provenance/conflict/uncertainty, and test whether this improves reachability and impact analysis.

Current classification:
- **applied research + portfolio project**;
- **potential invention**, not proven;
- not yet “innovation” in the commercial sense because it has not generated validated real-world value.

## 8. Agentic AI role

Agentic AI is the strongest current demonstration domain because agents combine:
- identity;
- permissions;
- tools;
- MCP servers;
- APIs;
- models;
- data;
- external destinations.

The Core remains broader than agent governance.

## 9. Competitive correction

The broad category is already active.

Important benchmarks include:
- DataHub;
- Atlan;
- Collibra;
- Holistic AI;
- Sensedia;
- Databricks Unity Catalog + Unity Gateway;
- adjacent AI/data security and observability platforms.

Therefore:
- do not pitch “we connect data, APIs and agents in a graph” as the unique innovation;
- investigate **cross-control-plane evidence fusion** instead.

## 10. Databricks position

Databricks is both:
- a major competitive benchmark;
- a possible future evidence source / connector.

Unity Catalog + Unity Gateway already cover substantial data + AI governance, lineage, agents, MCP services, access controls, and runtime policies.

The project should not assume everything must be built natively inside Databricks. External assets can be registered/connected/routed through its control plane.

The stronger EvidentGraph hypothesis is to correlate Databricks evidence with other systems such as GitHub/OpenAPI, OpenTelemetry, IAM, gateways, and non-Databricks infrastructure.

See `10_DATABRICKS_STRATEGIC_NOTE.md`.

## 11. Current synthetic demo

A reusable synthetic web demo exists at:

https://asccjr.github.io/evidence-graph/

It currently demonstrates:
- Agent Review;
- authorization check;
- runtime trace;
- CAN IT?;
- DID IT?;
- WHAT BREAKS?;
- hidden dependency conflict.

The presentation that motivated the demo was canceled, but the artifact remains useful for:
- portfolio;
- future academic presentations;
- future editais;
- validating UX concepts;
- communicating the research hypothesis.

It was **not wasted work**.

## 12. Planned MVP stack

- Python / FastAPI
- Neo4j / Cypher
- PostgreSQL / SQL
- OpenAPI
- OpenTelemetry
- MCP Python SDK
- Docker Compose
- TypeScript / Next.js later if useful

## 13. First real experiment

Build a controlled chain:

Agent → Identity → MCP tool → API → Service → PostgreSQL table/column

Then compare:

1. metadata/config only;
2. metadata + runtime;
3. metadata + runtime + authorization.

Measure:
- precision;
- recall;
- false positives;
- false negatives;
- freshness;
- evidence coverage;
- time-to-answer.

## 14. Project boundaries

### Core
`core/`

Canonical research/product project. Independent from external calls and course-specific framing.

### Claro / Campus Mobile opportunity
`opportunities/claro-campus-mobile-2026/`

A separate mobile-specific adaptation created only to satisfy the Campus Mobile program requirements.

### Disciplina de Projetos
`core/academic/project-discipline/`

The discipline will use the **Core project** for activities.

Course exercises can generate hypotheses and feedback, but do not automatically redefine the Core.

## 15. Source-of-truth rule

GitHub is the persistent project memory.

When resuming:
1. read `00_START_HERE.md`;
2. read this file;
3. read `08_DECISION_LOG.md`;
4. read `09_RESEARCH_LOG.md`;
5. load task-specific documents.

Chat history is not the authoritative source of truth.

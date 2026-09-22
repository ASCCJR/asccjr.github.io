# Canonical Context — Evidence Graph / Dependency Intelligence

**Updated:** 2026-09-22  
**Stage:** applied research / discovery / pre-MVP

## Current thesis

The project investigates whether correlating **metadata, lineage, code/contracts, authorization and runtime telemetry** in an evidence-aware graph can improve dependency and impact analysis.

The core questions are:

- **CAN IT?** — can an agent, application or identity reach a resource?
- **DID IT?** — was that path actually observed?
- **WHAT BREAKS?** — what may be affected if an asset, contract or permission changes?

## Evidence planes

A relationship may be supported by different evidence types:

1. **Declared** — configuration, catalog, manifests.
2. **Static** — code, SQL, IaC, SDK references.
3. **Authorization** — IAM, OAuth scopes, RBAC, policy.
4. **Lineage** — data derivation and movement.
5. **Runtime** — traces, gateway logs, query logs, agent tool calls.

The project must preserve disagreement between sources instead of collapsing everything into a single unqualified edge.

## Research question

> To what extent does correlating metadata, lineage, code/contracts, authorization and runtime telemetry in an evidence graph improve identification of dependencies, access paths and change impact in architectures that include AI agents?

## Important competitive correction

The broad idea of connecting data, services, APIs and agents in a graph is **not itself novel**. DataHub, Atlan, Holistic AI, Sensedia and other vendors already cover major portions of this space.

The hypothesis under investigation is narrower: whether **cross-source evidence fusion**, especially the distinction between possible, authorized and observed dependencies, can improve reachability and impact analysis.

## Core vs opportunity variants

The canonical project is independent of specific calls or competitions.

- `core` = research, portfolio, possible academic work, future startup exploration.
- `opportunities/*` = isolated adaptations to external requirements.

Rule:

> Adapt the proposal to the opportunity; do not permanently adapt the core to the opportunity.

## Current MVP

The synthetic MVP models:

`Sales Agent → Identity → MCP Tool → API → Service → Table → PII Column`

It demonstrates:

- authorized reachability;
- observed runtime usage;
- change-impact simulation;
- dormant dependencies;
- hidden runtime dependencies.

## Planned stack

- Python / FastAPI
- Neo4j / Cypher
- PostgreSQL / SQL
- OpenAPI
- OpenTelemetry
- MCP Python SDK
- Next.js / TypeScript later
- Docker Compose

## Validation metrics

- precision
- recall
- false positives
- false negatives
- freshness
- evidence coverage
- time-to-answer

## Current positioning

Today this is best described as **applied research + portfolio project**. Startup positioning remains a hypothesis to validate later.

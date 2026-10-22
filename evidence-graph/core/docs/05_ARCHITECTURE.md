# Architecture — v0 Concept

## Implementation status at integral transfer, 2026-10-20

This file preserves the conceptual architecture, not a list of delivered components. The implemented laboratory uses Python/FastAPI, HTTPX/Uvicorn, SQLite and manual OpenTelemetry instrumentation, with HTML/CSS/JavaScript views and Python/Playwright tests. L7 presents bounded evidence in the existing experience; it does not introduce a general collector or inference engine. See [checkpoint 30](./30_L7_EVIDENCE_REVIEW.md).

Neo4j, PostgreSQL, Docker Compose, enterprise connectors, MCP/LLM tools and a Next.js application remain conceptual or conditional choices. No privileged installation, connector access or architecture expansion is authorized by this transfer. NLP/generative extraction of references from heterogeneous documents is a research hypothesis for discussion, not an approved implementation.

## Evidence sources

### Metadata / lineage
Examples:
- Databricks Unity Catalog
- DataHub / Atlan
- OpenLineage / dbt
- warehouse metadata

### Code / contracts
Examples:
- GitHub
- OpenAPI
- SQL
- IaC / Terraform
- MCP manifests

### Authorization
Examples:
- cloud IAM
- OAuth scopes
- RBAC
- API/MCP gateways
- service identities

### Runtime
Examples:
- OpenTelemetry
- API-gateway traces
- agent tool calls
- database query logs

## Core pipeline

Sources  
→ collectors  
→ normalization  
→ entity resolution  
→ evidence reconciliation  
→ graph store  
→ query/analysis engines  
→ product workflows

## Core graph semantics

The project must not collapse all relationships into a generic DEPENDS_ON edge.

Important distinctions include:
- configured vs observed;
- can-call vs observed-call;
- can-read vs observed-read;
- lineage-derived vs code-derived;
- authorized vs blocked;
- known vs unknown.

Each edge should support, where applicable:
- source;
- evidence reference;
- detection mode;
- environment;
- first seen;
- last seen;
- confidence;
- active/inactive state.

## MVP stack

- Python / FastAPI
- Neo4j / Cypher
- PostgreSQL / SQL
- OpenAPI
- OpenTelemetry
- MCP Python SDK
- Docker Compose
- web UI later with TypeScript / Next.js if useful

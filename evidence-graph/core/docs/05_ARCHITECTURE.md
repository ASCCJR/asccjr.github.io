# Architecture — v0 Concept

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

# Evidence Graph / Dependency Intelligence

Synthetic research prototype for correlating **metadata, lineage, contracts/code, authorization and runtime telemetry** into an evidence-aware dependency graph.

## Core questions
- **CAN IT?** — can an agent, service or identity reach a resource?
- **DID IT?** — was the path actually observed at runtime?
- **WHAT BREAKS?** — what is the potential and active blast radius of a change?

## Status
`research / discovery / synthetic MVP`

The current web demo uses a fictional company and synthetic telemetry. It is designed to communicate the research hypothesis before real collectors are implemented.

## Project boundary
The canonical core remains independent from specific calls, competitions or grants. Opportunity-specific adaptations live under `opportunities/` and must not redefine the core.

## Next technical milestone
Replace synthetic evidence incrementally with real collectors:
1. OpenAPI
2. OpenTelemetry
3. PostgreSQL metadata
4. MCP configuration
5. IAM / OAuth scopes
6. Neo4j-backed traversal

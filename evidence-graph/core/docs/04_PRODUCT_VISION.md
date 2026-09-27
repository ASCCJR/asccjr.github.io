# Product Vision

## Problem

Enterprises increasingly distribute dependency knowledge across separate systems:

- data catalogs and lineage;
- source repositories and API contracts;
- IAM and gateways;
- observability and OpenTelemetry;
- AI-agent platforms and MCP registries;
- cloud/data platforms such as Databricks.

Each system sees only part of the architecture.

## Proposed value

EvidentGraph investigates a cross-platform evidence layer that can answer:

### CAN IT?
Can an agent, service, application, or identity reach a target resource under current topology and authorization?

### DID IT?
Was that path actually observed in runtime telemetry?

### WHAT BREAKS?
If a schema, API, MCP tool, permission, model endpoint, or dependency changes, what is the potential and active blast radius?

## Agentic AI as flagship use case

Agentic AI is the most visually compelling current use case because an agent may combine:
- an identity;
- scopes / permissions;
- tools;
- MCP servers;
- APIs;
- models;
- databases / knowledge bases;
- external destinations.

Agentic AI is a flagship use case, not the full scope of the Core.

## Long-term product possibilities

Possible delivery modes include:
- web graph/explorer;
- pre-change GitHub/CI check;
- agent risk passport/review;
- architecture black-box / forensic timeline;
- API for programmatic dependency queries;
- natural-language interface over verified graph queries.

These are product hypotheses, not yet validated business decisions.

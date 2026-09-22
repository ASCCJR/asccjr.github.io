# Evidence Graph / Dependency Intelligence

Interactive **synthetic research prototype** for exploring whether fusing heterogeneous evidence can make dependency analysis more reliable in modern data, software and **agentic AI** environments.

## Agent-first framing

An AI agent is modeled not as "just an LLM", but as an operational entity with:

- identity;
- scopes / permissions;
- tools;
- MCP servers;
- APIs;
- services;
- data reachability;
- runtime traces;
- external model destinations.

This makes agentic AI a concrete use case for the broader Evidence Graph research hypothesis.

## Research hypothesis

Instead of storing only:

```text
A --DEPENDS_ON--> B
```

the project preserves *why* a relationship is believed to exist:

- declared configuration;
- static/code evidence;
- authorization and identity;
- data lineage;
- runtime telemetry.

The working hypothesis is that this fusion can improve reachability and impact analysis while exposing disagreements between the architecture that is **declared**, **allowed** and **observed**.

## Demo scenarios

1. **Agent Review** — identity, tools, MCP, reachable APIs, sensitive data and possible overprivilege.
2. **CAN IT?** — permission-aware reachability from an AI agent to sensitive data.
3. **DID IT?** — runtime-observed path.
4. **WHAT BREAKS?** — potential vs active blast radius for a simulated contract change.
5. **Hidden dependency** — runtime behavior that conflicts with declared architecture.

## Simulated agent run

The demo can animate a synthetic production trace:

```text
Sales Agent
  → MCP tool
  → Customer API
  → Customer Service
  → customers
  → customers.cpf
```

The animation is intentionally synthetic. Its purpose is to communicate what real OpenTelemetry / gateway / database evidence could later populate.

## Demo URL

https://asccjr.github.io/evidence-graph/

## Status

`research / discovery / synthetic MVP v0.4`

All companies, assets, calls and telemetry shown in the interface are fictional.

## Presentation controls

- `←` / `→`: navigate scenarios
- `1`–`5`: jump directly to a scenario
- `P`: presentation layout
- `N`: presenter notes
- `F`: browser fullscreen
- **Simulate agent run**: animate the synthetic runtime path

## Project boundary

The canonical core remains **Evidence Graph / Dependency Intelligence**.

Agentic AI is a high-value, current use case — not a restriction of the core.

Opportunity-specific adaptations remain under:

```text
opportunities/
```

## Next technical milestone

Replace synthetic signals incrementally with real collectors:

1. OpenAPI contracts
2. OpenTelemetry traces
3. PostgreSQL metadata/query evidence
4. MCP configuration
5. IAM / OAuth scopes
6. Neo4j-backed traversal

Then compare:

- metadata/config only;
- metadata + runtime;
- metadata + runtime + authorization.

Candidate evaluation metrics: precision, recall, false positives, false negatives, freshness and time-to-answer.

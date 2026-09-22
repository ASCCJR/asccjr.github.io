# Evidence Graph / Dependency Intelligence

Interactive **synthetic research prototype** for exploring whether fusing heterogeneous evidence can make enterprise dependency analysis more reliable.

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

1. **Overview** — cross-domain graph.
2. **CAN IT?** — permission-aware reachability from an AI agent to sensitive data.
3. **DID IT?** — runtime-observed path.
4. **WHAT BREAKS?** — potential vs active blast radius for a simulated contract change.
5. **Hidden dependency** — runtime behavior that conflicts with declared architecture.

## Demo URL

https://asccjr.github.io/evidence-graph/

## Status

`research / discovery / synthetic MVP v0.2`

All companies, assets, calls and telemetry shown in the interface are fictional.

## Project boundary

The canonical **core** is independent from calls, competitions and grants.

Opportunity-specific adaptations must stay under:

```text
opportunities/
```

For example:

```text
opportunities/campus-mobile-2026/
```

The mobile requirement from Campus Mobile does not redefine the canonical core.

## Presentation controls

- `←` / `→`: navigate scenarios
- `F`: toggle presentation layout
- fullscreen button: browser fullscreen
- Enter in the search field: opens the CAN IT? scenario

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

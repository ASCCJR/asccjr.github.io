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

1. **Overview** — cross-domain graph and research hypothesis.
2. **CAN IT?** — permission-aware reachability from an AI agent to sensitive data.
3. **DID IT?** — runtime-observed path.
4. **WHAT BREAKS?** — potential vs active blast radius for a simulated contract change.
5. **Hidden dependency** — runtime behavior that conflicts with declared architecture.

## Demo URL

https://asccjr.github.io/evidence-graph/

## Status

`research / discovery / synthetic MVP v0.3`

All companies, assets, calls and telemetry shown in the interface are fictional.

## Presentation controls

- `←` / `→`: navigate scenarios
- `1`–`5`: jump directly to a scenario
- `P`: presentation layout
- `N`: presenter notes
- `F`: browser fullscreen
- Enter in the search field: opens **CAN IT?**

## v0.3 changes

- directed arrows on graph relationships;
- active runtime paths animate to emphasize observed behavior;
- edge labels are generated from the graph model and filtered per scenario;
- explicit evidence-source ribbon: CONFIG / CODE / IAM / OTEL / LINEAGE;
- presenter notes with a short talk track for each scenario;
- stronger visual distinction between reachability, runtime, change impact and evidence conflict.

## Project boundary

The canonical **core** is independent from calls, competitions and grants.

Opportunity-specific adaptations stay under:

```text
opportunities/
```

For example:

```text
opportunities/campus-mobile-2026/
```

The mobile requirement from Campus Mobile does not redefine the canonical core.

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

# Research Hypothesis

## Research question

> To what extent does correlating metadata, lineage, code/contracts, authorization, and runtime telemetry in an evidence graph improve identification of dependencies, access paths, and change impact in architectures that include AI agents?

## Evidence planes

1. Declared — catalog, config, manifests.
2. Static — code, SQL, IaC, SDK references.
3. Authorization — IAM, OAuth scopes, RBAC, policies.
4. Lineage — data derivation and movement.
5. Runtime — traces, gateway logs, query logs, agent tool calls.

## Main hypotheses

### H1 — Active dependency precision
Metadata + runtime should reduce false positives when identifying active dependencies compared with metadata/config alone.

### H2 — Reachability
Authorization evidence should reveal possible access paths that traditional lineage alone cannot express.

### H3 — Hidden dependencies
Runtime evidence should reveal dependencies that are absent from declared architecture or static inventory.

### H4 — Explainability
Preserving provenance/evidence per relationship should make reachability and impact analysis more explainable and auditable.

## What would count as a negative result

The project should be reconsidered if:
- evidence fusion does not materially improve precision/recall;
- telemetry gaps make conclusions too unreliable;
- incumbent platforms already correlate the same evidence sufficiently well;
- cross-system entity resolution is too inaccurate;
- the operational value does not justify another integration layer.

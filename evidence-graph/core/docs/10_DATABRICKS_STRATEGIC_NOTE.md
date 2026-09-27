# Databricks Strategic Note — Unity Catalog + Unity Gateway

**Date:** 2026-09-25  
**Status:** verified against public Databricks product materials.

## Why it matters

Databricks is one of the strongest overlaps with the broad original EvidentGraph vision.

Unity Catalog + Unity Gateway unify significant parts of:
- data governance;
- AI governance;
- discovery;
- lineage;
- access control;
- agent inventory;
- MCP governance;
- runtime policies;
- tracing / observability;
- AI cost controls.

This validates the problem but narrows our differentiation.

## External assets

Databricks governance is not limited to assets built natively inside Databricks.

Its public materials describe governance/connection patterns for:
- external model providers;
- external MCP servers registered as MCP Services;
- external coding agents when routed through governed services;
- external lineage assets such as upstream sources and downstream BI.

Therefore do **not** describe Databricks as “only working if everything lives inside Databricks.”

A better description:

> Databricks can serve as a governance/control plane for assets that are registered, connected, or routed through it.

## Important lineage limitation

Databricks documentation for model API/provider lineage states that service lineage captures dependencies from the service definition, but does not capture:
- workloads and agents that call the service at runtime;
- the data those callers access through the service.

This distinction is directly relevant to the EvidentGraph hypothesis.

## EvidentGraph implication

Do not compete with Databricks on native governance.

Instead investigate correlation across evidence planes:

Databricks Unity Catalog / Unity Gateway  
→ lineage + assets + permissions + AI activity

GitHub / OpenAPI  
→ code + contracts

OpenTelemetry / gateway traces  
→ runtime evidence

Cloud IAM / OAuth / RBAC  
→ authorization evidence

Other catalogs / gateways / databases  
→ non-Databricks evidence

Then correlate them in EvidentGraph.

## Potential future Databricks connector inputs

- Unity Catalog assets and lineage;
- tags/classification;
- model services/provider lineage;
- MCP Services;
- agent/tool inventory;
- Unity Gateway activity;
- permissions / policies;
- external lineage assets.

## Sources

- https://www.databricks.com/blog/whats-new-unity-catalog-data-ai-summit-2026
- https://www.databricks.com/blog/ai-governance-data-ai-summit-2026-whats-new-unity-ai-gateway
- https://docs.databricks.com/aws/en/ai-gateway/ai-governance
- https://docs.databricks.com/gcp/en/data-governance/unity-catalog/ai-gateway-service-lineage
- https://docs.databricks.com/gcp/en/agents/mcp-tools/mcp-services

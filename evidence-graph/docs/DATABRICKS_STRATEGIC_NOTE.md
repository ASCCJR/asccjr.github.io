# Databricks Strategic Note — Unity Catalog + Unity Gateway

**Date:** 2026-09-25  
**Status:** verified against Databricks public product documentation and 2026 Summit announcements.

## Why this matters

Databricks is now one of the strongest overlaps with the broad original project vision.

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

This strongly validates the underlying problem: enterprises need unified governance for data and increasingly autonomous AI systems.

## External assets

The Databricks model is not limited to assets created natively in Databricks.

Public documentation describes governance for:

- external model providers;
- external MCP servers registered as MCP Services;
- external coding agents such as Claude Code, Codex, Cursor and Gemini CLI when routed through governed model services;
- external lineage assets such as upstream sources and downstream BI systems.

Therefore:

> "Everything must live inside Databricks" is not an accurate description.

A better description is:

> Databricks becomes the governance/control plane for assets that are registered, connected or routed through it.

## Important lineage limitation

Databricks documentation for model API/provider lineage states that service lineage captures dependencies from the service definition.

It explicitly notes that Unity Catalog does **not** capture:

- workloads and agents that call a service at runtime;
- the data those callers access through that service.

This limitation is especially relevant to the Evidence Graph research hypothesis.

## Implication for Evidence Graph

The project should investigate correlation across different evidence planes rather than compete with Databricks on native governance.

Conceptually:

```text
Databricks Unity Catalog / Unity Gateway
        ↓
lineage + assets + permissions + AI activity

GitHub / OpenAPI
        ↓
code + contracts

OpenTelemetry / gateway traces
        ↓
runtime evidence

Cloud IAM / OAuth / RBAC
        ↓
authorization evidence

Other catalogs / gateways / databases
        ↓
non-Databricks evidence

                ↓
          EVIDENCE GRAPH
                ↓
        CAN IT? / DID IT? / WHAT BREAKS?
```

## Strategic interpretation

Databricks can be simultaneously:

- **competitor** — because it already solves substantial governance and lineage problems;
- **integration partner / evidence source** — because its metadata and runtime signals can feed a cross-platform graph.

## What remains worth researching

Not:

> Can we build data + AI governance?

But:

> Can we correlate multiple control planes and evidence sources well enough to improve reachability, dependency classification and impact analysis?

In particular:

- declared vs observed;
- allowed vs exercised;
- Databricks-native vs external dependencies;
- conflicts between catalog, code, IAM and runtime;
- cross-platform blast radius.

## Sources

- Databricks — What's new with Unity Catalog at Data + AI Summit 2026  
  https://www.databricks.com/blog/whats-new-unity-catalog-data-ai-summit-2026

- Databricks — AI governance at Data + AI Summit 2026: What's new with Unity Gateway  
  https://www.databricks.com/blog/ai-governance-data-ai-summit-2026-whats-new-unity-ai-gateway

- Databricks — AI governance guide  
  https://docs.databricks.com/aws/en/ai-gateway/ai-governance

- Databricks — Track model API and provider lineage  
  https://docs.databricks.com/gcp/en/data-governance/unity-catalog/ai-gateway-service-lineage

- Databricks — MCP Services  
  https://docs.databricks.com/gcp/en/agents/mcp-tools/mcp-services

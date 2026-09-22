# Decision Log — Evidence Graph

Append-only log of important project decisions.

---

## D-001 — Keep a canonical core independent from opportunity-specific requirements
**Date:** 2026-09-22  
**Status:** DECIDED

The Evidence Graph / Dependency Intelligence core remains independent from specific competitions, grants or calls.

Opportunity-specific adaptations belong under `opportunities/`.

Reason: requirements such as Campus Mobile's mobile constraint should not permanently redefine the research thesis.

---

## D-002 — Use GitHub as the source of truth
**Date:** 2026-09-22  
**Status:** DECIDED

GitHub is the persistent, versioned source of truth for:

- canonical documentation;
- demo code;
- research decisions;
- opportunity variants.

ChatGPT is a working environment, not the authoritative project memory.

---

## D-003 — Use an agent-first demo while preserving a broader core
**Date:** 2026-09-22  
**Status:** DECIDED

The public/demo experience starts from an AI agent because agentic AI makes the dependency problem immediately visible.

The demo may highlight:

`Agent → Identity → Permission → MCP → API → Service → Data`

This does **not** change the canonical scope. Applications and services remain first-class entities in the Evidence Graph.

Reason:
- agentic AI is a current high-interest domain;
- it provides a strong visual and conceptual demonstration;
- identity, tools, permissions and data access naturally illustrate evidence fusion.

---

## D-004 — Simulated agent execution is allowed in the synthetic MVP
**Date:** 2026-09-22  
**Status:** DECIDED

The v0.4 demo includes an animated synthetic trace.

It must remain clearly labeled as synthetic.

Its purpose is to communicate what later real collectors such as OpenTelemetry, gateway traces and database evidence could populate.

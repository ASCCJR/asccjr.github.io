# Decision Log — EvidentGraph Core

Append-only log. Do not silently delete old decisions; supersede them explicitly.

---

## D-001 — Keep a canonical Core independent from opportunity-specific requirements
**Date:** 2026-09-22  
**Status:** DECIDED

The Core remains independent from competitions, grants, and calls.

External requirements belong under `opportunities/`.

---

## D-002 — Use GitHub as the source of truth
**Date:** 2026-09-22  
**Status:** DECIDED

GitHub stores canonical documentation, decisions, research, demos, and opportunity variants.

ChatGPT is a working environment, not the authoritative project memory.

---

## D-003 — Use an agent-first demo while preserving a broader Core
**Date:** 2026-09-22  
**Status:** DECIDED

Agentic AI is the strongest current demonstration domain, but the project remains broader than agent governance.

---

## D-004 — Synthetic execution is allowed in the demo
**Date:** 2026-09-22  
**Status:** DECIDED

Synthetic traces may be used for communication as long as they are clearly labeled synthetic.

---

## D-005 — Treat Databricks as both benchmark and evidence source
**Date:** 2026-09-25  
**Status:** DECIDED

Do not position the project as a replacement for Unity Catalog / Unity Gateway.

Databricks can become a connector/evidence source for cross-platform correlation.

---

## D-006 — Adopt “EvidentGraph” as the working project name
**Date:** 2026-09-27  
**Status:** DECIDED — working name

Project name: **EvidentGraph**

Subtitle: **Dependency Intelligence for Data, Software & AI**

This is a working name, not a trademark/domain clearance.

Reason:
- emphasizes evidence and explainability;
- preserves the graph concept;
- is not vendor-specific;
- does not constrain the project to AI agents only.

---

## D-007 — Separate Core and Claro Campus Mobile into distinct workspaces
**Date:** 2026-09-27  
**Status:** DECIDED

Canonical project:
`core/`

Claro/Campus Mobile variant:
`opportunities/claro-campus-mobile-2026/`

The mobile requirement must not permanently change the Core.

---

## D-008 — Use EvidentGraph Core in the Disciplina de Projetos
**Date:** 2026-09-27  
**Status:** DECIDED

The Core project will be reused for class activities instead of inventing a second unrelated project.

Course answers live under:
`core/academic/project-discipline/`

Durable insights can later be promoted into canonical files after feedback/validation.

---

## D-009 — Preserve the synthetic HTML demo
**Date:** 2026-09-27  
**Status:** DECIDED

The original professor presentation was canceled, but the HTML demo remains valuable.

Keep it published as a reusable:
- portfolio artifact;
- future demo;
- UX prototype;
- explanatory tool.

Do not treat it as the canonical technical implementation.

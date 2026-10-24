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

---

## D-010 — Make the next Core experience task-first and decision-oriented
**Date:** 2026-10-13  
**Status:** DECIDED for product direction; implementation pending

The proponent reported professor feedback that the public demo is too small and presentation-oriented, emphasizing the technical mechanism rather than a business task. This is qualitative reported feedback, not customer validation.

The next experience prioritizes **change-impact review**: select a change, understand consequences and uncertainty, identify owners, record checks and export an analysis. The graph is contextual exploration; detailed evidence remains inspectable.

This supersedes D-003 only as the opening/navigation strategy for the next demo. Agentic AI remains an important use case, and the Core still covers data, software, models and agents. D-009 remains valid: preserve the current demo until the replacement is reviewed.

Specification: `12_PRODUCT_UX_VISION.md`. Dataset sizes, screen details and test thresholds are proposed design parameters, not validated results.

---

## D-011 — Separate enterprise-scale simulation, real PoC and business discovery
**Date:** 2026-10-13  
**Status:** DECIDED for sequencing; tests and implementation pending

Use a larger coherent synthetic enterprise environment to test product UX, while keeping real collectors and evidence-fusion evaluation in a controlled small PoC. A larger synthetic graph does not demonstrate production scalability.

Run discovery and usability in parallel with development. This supersedes the previous roadmap placement of customer discovery only after the technical experiment.

Do not hide uncertainty, equate missing traces with absent dependencies, count structural relations as runtime calls, or claim that a dependency alone proves breakage.

This documentation revision does not change public demo code, Campus Mobile, academic submissions, contributor names or personal material.

---

## D-012 — Abandon Sites migration and resume the Core on GitHub Pages
**Date:** 2026-10-15  
**Status:** DECIDED by the proponent

The user decided to discard the Sites experiment and keep GitHub Pages for the current interface. PR #2 was closed without merge; its branch is historical, not a prerequisite. Deleting the Sites project is the user's own action and was not performed here.

Retain the accepted M3 graph-plus-list experience and Grupo Aurora identity. Continue with usability evaluation and a restricted runtime-evidence laboratory, not another visual rewrite or hosting migration. This confirms the graph-restoration correction recorded in `17_M2_GRAPH_REVIEW.md`; task-first does not mean graph removal.

The L1 laboratory collects real loopback HTTP/SQLite execution via manual OpenTelemetry instrumentation while using fictitious business data. It is separate from the M1 synthetic schema and published UI. It does not demonstrate IAM, enterprise collectors, real customers or statistically validated superiority.

See `21_RETOMADA_CORE_E_LABORATORIO.md` and `22_ROTEIRO_AVALIACAO_M3.md`. Preserve prior publications, Campus Mobile, academic files, team names and personal-material exclusions.

---

## D-013 — Transfer all project continuity to this environment
**Date:** 2026-10-20
**Status:** DECIDED by the proponent; integral package received and reconciled

Implementation, maintenance, research, architecture, product, UX, business, documentation, presentations, academic activities and opportunities continue here. This supersedes instructions to reserve strategy for another chat or return outputs to the previous assistant. No approval in the source chat is needed. Consolidated documents and source copies sustain continuity; this is not a verbatim export of every message.

D-002 remains valid for public technical/project memory. Private memory, original call PDF, contacts and confidential drafts are preserved outside public Git; the repository-local `evidentgraph.privateContext` pointer locates the private receipt/index without committing its value. Public team names already recorded remain; removed personal/professional material must not be recovered or reintroduced.

The source package is additive historical/context material. It does not replace the directly verified L7 state or authorize reapplying patches, rebuilding the environment or restarting Checkpoints 1–3. Earlier statements that L7 was only local/unsent are superseded, with their records retained. The scoped instructions are in `evidence-graph/AGENTS.md`.

Normal documentation commits/pushes on the existing authorized feature branch are allowed after diff/trigger review. Merge, deploy, push to main, publication/release, destructive actions, privileged installations, spending, third-party contact, submissions and declarations require the user's specific approval here. Source-chat deletion is the user's action and is not automated.

---

## D-014 — Resume CTE-IA proposal after the completed L7 cycle
**Date:** 2026-10-20
**Status:** DECIDED for continuity; proposal and implementation choices remain open

The technical cycle requested before the application is closed by the validated L7. Preparing the CTE-IA proposal does not require merging, deploying, opening L8, expanding the parser or redesigning the interface. Keep it in `opportunities/cte-ia-2026/`, distinct from Campus Mobile and academic deliveries.

Discuss the business problem, initial audience, differentiation, team, measurable targets, Annex I gaps and an honest role for AI. Deterministic rules, the bounded AST analyzer, mapping an agent and using Codex during development do not establish AI as a central product component. NLP/generative extraction and reconciliation of references in documents is a hypothesis, not an approved architecture or delivered feature. Compare against conventional rules/IDs/parsers before claiming an advantage.

The supplied call v1 is a dated source. Confirm official amendments, dates, eligibility and live form limits before relying on them for submission. Team roles, availability, rights/permissions and application commitments remain unconfirmed; do not invent them. Independent user/research validation remains pending. This decision does not authorize an application or new product implementation.

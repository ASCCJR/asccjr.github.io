# START HERE — EvidentGraph Core

This directory is the persistent memory of the canonical project.

## Source-of-truth hierarchy

1. `01_CANONICAL_CONTEXT.md` — current truth of the research project.
2. `08_DECISION_LOG.md` — append-only decisions and changes in direction.
3. `09_RESEARCH_LOG.md` — research findings, hypotheses, and external evidence.
4. [12_PRODUCT_UX_VISION.md](./12_PRODUCT_UX_VISION.md) — product/UX specification; graph-first opening was restored by the review below.
5. [21_RETOMADA_CORE_E_LABORATORIO.md](./21_RETOMADA_CORE_E_LABORATORIO.md) — latest checkpoint: abandon Sites migration, preserve Pages/M3 and run a small local evidence experiment. This checkpoint supersedes old statements that no runtime collection exists, but does not claim enterprise connectors or UI integration.
6. [18_ASSET_INVESTIGATION.md](./18_ASSET_INVESTIGATION.md) — published M3 implementation checkpoint: shared graph/list workspace and asset investigation. Earlier checkpoints: `15_M1_VALIDATION.md`, `16_M2_PREVIEW.md`, `17_M2_GRAPH_REVIEW.md`.
7. Other files — detailed views of product, research, architecture, market, and roadmap.

## Rules

- Separate **fact**, **hypothesis**, **decision**, and **idea**.
- Do not turn repeated hypotheses into facts.
- Do not claim novelty merely because a feature is new to this project.
- Keep the Core independent from edital/course-specific constraints.
- GitHub is the project memory. Chat conversations are working sessions.
- If an opportunity requires an adaptation, create or update its own folder under `opportunities/`.

## Current project name

**EvidentGraph**

Why this name:
- “Evident” emphasizes evidence, explainability, and provenance.
- “Graph” reflects the dependency/path model.
- It is broad enough for data, software, APIs, agents, identity, and runtime.
- It does not lock the project to a single vendor or to agentic AI only.

This is a **working project name**, not a trademark/domain clearance.

## Current work — 2026-10-15, Core resumed

Sites migration was abandoned by the proponent. PR #2 is closed without merge; its branch is historical only. GitHub Pages remains the current presentation host. Preserve the M3 graph plus list and Grupo Aurora identity.

The isolated [runtime laboratory](../lab-runtime/README.md) now runs a FastAPI API, test consumers and SQLite through actual loopback HTTP, with manually instrumented OpenTelemetry spans. Business data remains fictitious. Twenty-eight lab tests, 43 M1 tests and 13 traversal tests passed locally in this round. No new hosted-browser or CI success is claimed.

This does not integrate laboratory evidence into the public graph or extend the M1 analyzer to real corporate sources. The lab uses a separate schema, declared consumer requirements and a deliberately small GET/200 field-removal scenario.

Read [21_RETOMADA_CORE_E_LABORATORIO.md](./21_RETOMADA_CORE_E_LABORATORIO.md) for evidence and limits, and [22_ROTEIRO_AVALIACAO_M3.md](./22_ROTEIRO_AVALIACAO_M3.md) for the pending hosted check and user sessions.

Next: review the lab and define a small adapter to the existing graph, while testing the M3 experience with people. Do not restart design, remove the graph, create another hosting workflow or change Campus Mobile, academic submissions, contributors or personal material.

## Previous checkpoint — 2026-10-14, M3 evaluation

M1 has 240 synthetic assets, 512 relations, a bounded reference impact analyzer and 43 model tests. M2 introduced review, inventory and evidence; the proponent then requested restoring the graph. The accepted direction is **graph plus operational analysis**, with a fictional Grupo Aurora and no repeated demo labels.

M3 adds three questions per asset, depth-limited typed traversal, explicit process associations, shared graph/list filters and selection, return from review to the selected asset, and context export. Source: `preview-m2/`. The original public files at `evidence-graph/index.html`, `app.js`, `styles.css` are not replaced.

The user authorized a separate evaluation address at `/evidence-graph/preview-m2/`. Verify the actual merge and deployment in PR #1; do not confuse local tests or this note with a successful deployment. Generated `data.js` and `manifest.json` must be present before merge; the restricted PR build workflow supplies them.

Read [18_ASSET_INVESTIGATION.md](./18_ASSET_INVESTIGATION.md) for the test record and limitations. Twenty UI tests ran using direct DOM loading because browser HTTP navigation was blocked. This does not validate hosted localStorage persistence. The 13 pure traversal tests do not turn catalog exploration into impact or authorization analysis.

At that checkpoint the next steps were hosted evaluation and a small real-collector PoC. See the latest checkpoint above for progress; hosted user evaluation and enterprise integrations remain pending.

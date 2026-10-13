# START HERE — EvidentGraph Core

This directory is the persistent memory of the canonical project.

## Source-of-truth hierarchy

1. `01_CANONICAL_CONTEXT.md` — current truth of the project.
2. `08_DECISION_LOG.md` — append-only decisions and changes in direction.
3. `09_RESEARCH_LOG.md` — research findings, hypotheses, and external evidence.
4. [12_PRODUCT_UX_VISION.md](./12_PRODUCT_UX_VISION.md) — product/UX specification for the next Core experience.
5. [15_M1_VALIDATION.md](./15_M1_VALIDATION.md) — latest implementation checkpoint: synthetic data and reference tests, not a replacement UI.
6. Other files — detailed views of product, research, architecture, market, and roadmap.

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

## Current work — 2026-10-13, M1

The next Core experience is task-first, starting with change-impact analysis. M0 defined the UX; M1 now implements a deterministic generator, integrity validator, bounded reference analysis and 43 local tests for three scenarios.

Start with [13_DATA_CONTRACT.md](./13_DATA_CONTRACT.md), [14_SCENARIOS_AND_EXPECTED_RESULTS.md](./14_SCENARIOS_AND_EXPECTED_RESULTS.md) and [the reproducible data package](../demo-data/README.md).

The generated dataset contains 240 assets and 512 relations. Its outputs are regenerable in `demo-data/build/`, not embedded in the public site. The prior M0 documents describe an earlier checkpoint; this section and `15_M1_VALIDATION.md` update implementation status without rewriting historical decisions.

Next: M2, the CHG-001 interface workflow. Preserve the existing public demo until the replacement is reviewed. The real-collector PoC stays small and remains pending; business discovery runs in parallel. Campus Mobile, contributor names and academic submissions are unchanged.

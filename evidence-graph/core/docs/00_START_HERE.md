# START HERE — EvidentGraph Core

This directory is the persistent memory of the canonical project.

## Current checkpoint — L6-A evidence evaluation, 2026-10-16

Read [28_L6_EVIDENCE_EXPERIMENT.md](./28_L6_EVIDENCE_EXPERIMENT.md) and [evaluation/PROTOCOL.md](../evaluation/PROTOCOL.md). The work remains in PR #3, branch `feat/core-runtime-lab-20261015`; no merge or deploy.

L6-A implements a first controlled comparison of consumer declarations (C), prior runtime (R), and local authorization (A), alone and combined. The behavioral oracle executes functions on real HTTP v1/v2 responses without consulting the manifest used by the predictor. Oracle outcomes and subsequent probes are not prediction inputs. The policy reference server uses a separate direct access table, not the L5 evaluator under test.

This is structural/behavioral separation, not independent authorship, blind holdout or external validation. There are 12 consumer cases built from six functions, and six perturbed views of the same cases. Do not count them as independent samples or claim statistical significance.

Base impact results: C gives 6 correct, 2 errors and 4 abstentions; CR/CRA give 7 correct, 2 errors and 3 abstentions. Positive precision falls from 80.0% to 71.4%; recovery of known positives rises from 4/8 to 5/8. A required-looking read inside try/except creates a false positive. A conflict turns a false negative into an abstention, not confirmed correctness. This is not unequivocal superiority of fusion.

167 local tests passed: 124 previous lab/history/authorization regressions plus 43 evaluation tests. No new UI or hosted-browser result is claimed. The read-only evaluation workflow runs the same suites; consult the actual head/run before claiming CI success. Tests verify measurement and preservation of adverse results, not that predictions are all correct.

Candidate heuristics in `core/evaluation/` are NOT promoted to the product analyzer. The M3/Pages UI, L1–L5 code, 240-asset Grupo Aurora dataset, contributor information, academic submissions and opportunity variants remain unchanged. Sites stays abandoned; the CTE-IA application is a later parallel task, not a blocker for Core work.

## Resume here

1. Inspect PR #3 and its CI status.
2. Read `28_L6_EVIDENCE_EXPERIMENT.md`, `evaluation/PROTOCOL.md` and `evaluation/README.md`.
3. Preserve this baseline and its errors. Refine candidate reasoning in a new version: potential field dependency is not confirmed failure, and complete documentation can be wrong.
4. Add independently reviewed challenge cases and semantic outcomes, plus pending user sessions. No automatic publication or new redesign.

The L4 history command stays limited to L1 captures. L5 uses a separate schema/builder. L6-A outputs measurements, not an additional application. No silent dataset mixing or modification of historical runs. MCP, LLM agents, production IAM and corporate connectors remain unimplemented.

## Source-of-truth hierarchy

1. `01_CANONICAL_CONTEXT.md` — research thesis/boundaries; current implementation status is in checkpoints.
2. `08_DECISION_LOG.md` — append-only decisions.
3. `09_RESEARCH_LOG.md` — research notes; L6-A results are in checkpoint 28.
4. `12_PRODUCT_UX_VISION.md` — UX specification; graph-first opening restored in `17_M2_GRAPH_REVIEW.md`.
5. `28_L6_EVIDENCE_EXPERIMENT.md` — current evaluation checkpoint and limits.
6. Other detailed architecture, roadmap and opportunity documents.

## Checkpoint history

- [M1: data/reference model](./15_M1_VALIDATION.md).
- [M2: review](./16_M2_PREVIEW.md) and [graph + list restoration](./17_M2_GRAPH_REVIEW.md).
- [M3: asset investigation](./18_ASSET_INVESTIGATION.md). Published evaluation: `/evidence-graph/preview-m2/`; older `/evidence-graph/` preserved.
- [L1: local HTTP/SQLite/OTel](./21_RETOMADA_CORE_E_LABORATORIO.md).
- [L2: capture adapter](./23_LAB_EVIDENCE_UI.md).
- [L3: source/notes/HTTP tests](./25_L3_BROWSER_VALIDATION.md).
- [L4: capture history](./26_L4_CAPTURE_HISTORY.md).
- [L5: endpoint-scoped local authorization](./27_L5_LOCAL_AUTHORIZATION.md).
- [Roadmap](./24_CORE_NEXT_STEPS.md) and [user evaluation script](./22_ROTEIRO_AVALIACAO_M3.md).

Historical counts describe their revisions and conditions. Do not add overlapping suites or turn unit-test success into production/market validation.

## Rules

- Separate fact, hypothesis, decision and idea.
- Repetition does not make a hypothesis true; no novelty claim solely because a feature is new here.
- Preserve graph/lineage and operational analysis as complementary views.
- Keep the Core independent from edital/course requirements; adaptations belong in `opportunities/`.
- GitHub is the project memory; chat is a working environment.
- No fabricated interviews, adoption, commercial outcomes or safety guarantees.
- Preserve public site, team documents and personal-material removals unless expressly authorized.

## Working name

**EvidentGraph — Dependency Intelligence for Data, Software & AI.**

Working name, not trademark/domain clearance. Broad Core; agents are one use case.

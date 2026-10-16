# START HERE — EvidentGraph Core

Persistent memory of the canonical project. GitHub is the source of truth; chat is a working environment.

## Current checkpoint — L6-B, 2026-10-16

Read [29_L6B_INFERENCE_AND_SEMANTICS.md](./29_L6B_INFERENCE_AND_SEMANTICS.md) and [refinement/PROTOCOL.md](../evaluation/refinement/PROTOCOL.md). Work is in PR #3, branch `feat/core-runtime-lab-20261015`; no automatic merge or deploy.

L6-B separates declared requirements, observed field access, potential impact, bounded exception inference, execution confirmation and semantic correctness. It adds source evidence S through a deliberately limited AST analyzer, under exact local response assumptions. Unsupported syntax and invalid scope/hash/validity produce UNKNOWN.

Old 12 cases: unchanged A_CRA = 7 correct, 2 FP, 3 unknown; B+S = 11 correct, 0 observed binary errors, 1 unknown. This is **extra information**, not superior fusion at equal information. S alone produces the same exception predictions. Without S, B abstains in all 12 cases; zero errors through abstention is not success.

Eight new cases: 3 correct exception predictions, 5 unknown. Three tasks violate business expectations without exceptions. The evaluator discovers them; the predictor does not claim semantic correctness. Old cases were known; new cases are also same-author, not an external holdout. No statistical significance, independent validation or product promotion is claimed.

229 local tests passed: 124 previous lab regressions, 43 L6-A, 62 L6-B. The workflow includes all three groups; consult the actual commit/run for CI status. No new UI/Pages/browser claim. The five new Python blobs match the locally tested files.

## Resume here

1. Inspect PR #3 and CI status.
2. Read checkpoint 29 and `evaluation/refinement/README.md`.
3. Preserve L6-A and L6-B results, including abstentions and extra-information caveats.
4. Next bounded milestone: independent case review and a truthful presentation of potential impact, inference and tested outcomes, without a redesign or treating unsupported code as safe.

Independent review and user sessions have not occurred. Do not fabricate their completion. The CTE-IA application stays separate until the functional Core milestone is consolidated.

## Source-of-truth hierarchy

1. `01_CANONICAL_CONTEXT.md` — research thesis/boundaries; implementation checkpoints provide newer status.
2. `08_DECISION_LOG.md` — append-only decisions.
3. `09_RESEARCH_LOG.md` — research notes; experimental results are in checkpoints 28 and 29.
4. `12_PRODUCT_UX_VISION.md` — product/UX; graph-first was restored in checkpoint 17.
5. `29_L6B_INFERENCE_AND_SEMANTICS.md` — current experiment and its limitations.
6. Detailed architecture, roadmap and opportunity documents.

## Checkpoint history

- [M1: data/reference model](./15_M1_VALIDATION.md).
- [M2: review](./16_M2_PREVIEW.md), [graph/list restoration](./17_M2_GRAPH_REVIEW.md).
- [M3: asset investigation](./18_ASSET_INVESTIGATION.md). Evaluation at `/evidence-graph/preview-m2/`; older `/evidence-graph/` preserved.
- [L1: real local HTTP/SQLite/OTel](./21_RETOMADA_CORE_E_LABORATORIO.md).
- [L2: capture adapter](./23_LAB_EVIDENCE_UI.md).
- [L3: source, notes and HTTP tests](./25_L3_BROWSER_VALIDATION.md).
- [L4: capture history](./26_L4_CAPTURE_HISTORY.md), limited to L1 schema.
- [L5: local endpoint authorization](./27_L5_LOCAL_AUTHORIZATION.md), separate schema/viewer.
- [L6-A: baseline source evaluation](./28_L6_EVIDENCE_EXPERIMENT.md), unchanged.
- [Roadmap](./24_CORE_NEXT_STEPS.md), [user evaluation script](./22_ROTEIRO_AVALIACAO_M3.md).

## Rules

- Separate fact, hypothesis, decision and idea; repetition does not turn a hypothesis into fact.
- No novelty claim merely because a feature is new here.
- Preserve graph/lineage and operational analysis as complementary views.
- Do not sum overlapping test runs or equate passing implementation tests with correct predictions, market validation or production security.
- Keep Core independent from edital/course requirements. Adaptations belong in `opportunities/`.
- No fabricated interviews, adoption, commercial outcomes or safety guarantees.
- Preserve public site, team records and personal-material removals unless expressly authorized.
- Sites remains abandoned. MCP, LLM agents, corporate connectors and production IAM have not been implemented by these milestones.

## Working name

**EvidentGraph — Dependency Intelligence for Data, Software & AI.** Working name, not trademark/domain clearance. Agents are one use case in a broader Core.

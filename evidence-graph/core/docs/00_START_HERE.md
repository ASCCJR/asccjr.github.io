# START HERE — EvidentGraph Core

Persistent memory of the canonical project. GitHub is the source of truth; chat is a working environment.

## Current checkpoint — L7, 2026-10-19

Read [30_L7_EVIDENCE_REVIEW.md](./30_L7_EVIDENCE_REVIEW.md) and [review-ui/README.md](../review-ui/README.md). PR [#3](https://github.com/ASCCJR/asccjr.github.io/pull/3) remains a draft on `feat/core-runtime-lab-20261015`. **L7 pronta para revisão de merge; publicação não autorizada.** No merge, deploy or push to `main` is authorized.

L7 presents indication, bounded inference and recorded test outcomes separately in the existing graph/list and operational review. Aurora Revisão (13 assets/12 relations) and Aurora Validação (9/8) are separate from the preserved Grupo Aurora (240/512). Showing historical results does not execute tests; UNKNOWN remains inconclusive. Notes do not change evidence or outcomes.

Validated code head: `1a1324c56694474dcf76a16466c0c22693d808a9`. All three runs checked out temporary PR merge `3f07940e795ec69561e69a57116b5b241dde16e0`, with that head and `main` as parents; its tree was verified equal to the code head.

| Run | Confirmed result |
| --- | --- |
| [39335649585 — evaluation](https://github.com/ASCCJR/asccjr.github.io/actions/runs/39335649585) | 124 lab + 43 L6-A + 62 L6-B Python tests passed |
| [39335649610 — runtime](https://github.com/ASCCJR/asccjr.github.io/actions/runs/39335649610) | Capability check passed; 124 repeated Python tests; 12 navigation + 10 authorization HTTP cases passed |
| [39335649617 — review](https://github.com/ASCCJR/asccjr.github.io/actions/runs/39335649617) | Capability check passed; 20 L7 Python + 14 HTTP cases passed; three additional corrected-startup repetitions passed |

Totals: **249 distinct Python tests and 36 distinct HTTP cases**, zero failures/errors/skips in these runs. The repeated 124 tests, three startup repetitions and two capability checks do not increase those totals. Twelve actual HTTP screenshots were opened and inspected; see checkpoint 30 for observations and capture limits. Only the two browser jobs moved to Ubuntu 22.04, retaining Python 3.12, Playwright 1.57.0, Chromium 143.0.7499.4/revision 1200 and `chromium_sandbox=True`, as non-root UID 1001. No protection policy was disabled. This is an environment capability check, not a full security audit.

Local WSL remains Ubuntu 26.04 and unsupported by the pinned browser installer. Earlier Ubuntu 24.04 CI attempts failed at sandbox launch before executing HTTP cases; those failures remain recorded. The isolated legacy fixture now demonstrates a missed late listener; the corrected bootstrap and three repeats passed. The earlier L6-B timeout's cause remains unproven.

Changes after the validated code head are limited to this file, checkpoint 30 and `review-ui/README.md`: continuity documentation only. No application, harness, dependency or workflow changed after these successful runs. Logs and PNG artifacts have seven-day GitHub retention; necessary local evidence is outside the repository in `EvidentGraph-L7-evidencias-20261019/etapa3-ubuntu22/` beside this clone. No viewer was uploaded as an artifact or published.

## Previous checkpoint — L6-B, 2026-10-16

Read [29_L6B_INFERENCE_AND_SEMANTICS.md](./29_L6B_INFERENCE_AND_SEMANTICS.md) and [refinement/PROTOCOL.md](../evaluation/refinement/PROTOCOL.md). Work is in PR #3, branch `feat/core-runtime-lab-20261015`; no automatic merge or deploy.

L6-B separates declared requirements, observed field access, potential impact, bounded exception inference, execution confirmation and semantic correctness. It adds source evidence S through a deliberately limited AST analyzer, under exact local response assumptions. Unsupported syntax and invalid scope/hash/validity produce UNKNOWN.

Old 12 cases: unchanged A_CRA = 7 correct, 2 FP, 3 unknown; B+S = 11 correct, 0 observed binary errors, 1 unknown. This is **extra information**, not superior fusion at equal information. S alone produces the same exception predictions. Without S, B abstains in all 12 cases; zero errors through abstention is not success.

Eight new cases: 3 correct exception predictions, 5 unknown. Three tasks violate business expectations without exceptions. The evaluator discovers them; the predictor does not claim semantic correctness. Old cases were known; new cases are also same-author, not an external holdout. No statistical significance, independent validation or product promotion is claimed.

229 local tests passed: 124 previous lab regressions, 43 L6-A, 62 L6-B. The workflow includes all three groups; consult the actual commit/run for CI status. No new UI/Pages/browser claim. The five new Python blobs match the locally tested files.

## Resume here

1. Review PR #3, checkpoint 30 and the exact successful runs above; keep the PR a draft until the owner decides otherwise.
2. Read checkpoint 29 and `evaluation/refinement/README.md` for the unchanged experimental limits.
3. Preserve L6-A and L6-B results, abstentions, additional-information caveats and previous CI failures.
4. Remaining: independent task/case review and an explicit owner decision about merge/publication. No independent user evaluation has occurred, and this checkpoint authorizes no further product work.

Independent review and user sessions have not occurred. Do not fabricate their completion. The CTE-IA application stays separate until the functional Core milestone is consolidated.

## Source-of-truth hierarchy

1. `01_CANONICAL_CONTEXT.md` — research thesis/boundaries; implementation checkpoints provide newer status.
2. `08_DECISION_LOG.md` — append-only decisions.
3. `09_RESEARCH_LOG.md` — research notes; experimental results are in checkpoints 28 and 29.
4. `12_PRODUCT_UX_VISION.md` — product/UX; graph-first was restored in checkpoint 17.
5. `30_L7_EVIDENCE_REVIEW.md` — current integration and confirmed browser validation; `29_L6B_INFERENCE_AND_SEMANTICS.md` — unchanged experiment and limitations.
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
- [L6-B: bounded inference and semantics](./29_L6B_INFERENCE_AND_SEMANTICS.md), unchanged.
- [L7: review by evidence level and HTTP validation](./30_L7_EVIDENCE_REVIEW.md).
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

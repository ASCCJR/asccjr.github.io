# START HERE — EvidentGraph Core

This directory is the persistent memory of the canonical project.

## Current checkpoint — L5 local authorization, 2026-10-16

Read [27_L5_LOCAL_AUTHORIZATION.md](./27_L5_LOCAL_AUTHORIZATION.md) for the latest implementation and validation boundary. This index now links the previous checkpoints instead of repeating their older pending-status paragraphs.

The work remains in PR #3, branch `feat/core-runtime-lab-20261015`. L5 adds an exact-tuple local policy, ephemeral verified identities, actual HTTP allow/deny/indeterminate handling, and a read-only viewer using the existing graph/list components. The `Aurora Acesso` capture has 10 assets and 9 relations; the 240-asset Grupo Aurora is kept separate and unchanged.

Policy decisions, attempted calls, completed calls, contract incompatibility and executed checks remain separate. A denied attempt is not a successful read. An allowed but unexecuted consumer remains unobserved. The API performs the local check; the browser only reads the evidence.

124 local Python tests passed: 28 L1, 24 L2 adapter, 24 L4 history and 48 L5. Browser HTTP navigation was blocked locally, not counted as success. Ten L5 HTTP browser tests were added to CI; consult the actual head/run before claiming success. Offline DOM inspection is not an HTTP or reload test.

No merge or deploy is authorized by this checkpoint. No public HTML/CSS/JS, Pages configuration, previous datasets, contributor information, academic submission or opportunity variant was changed. Sites remains abandoned. The user explicitly directed completing the Core milestone first and improving the CTE-IA application afterwards.

## Resume here

1. Inspect PR #3 and CI for its actual status.
2. Read `27_L5_LOCAL_AUTHORIZATION.md`; inspect `auth_policy.py`, `auth_lab.py`, `auth_adapter.py`, `build_auth_view.py` and the tests under `lab-runtime/`.
3. Review the read-only viewer without replacing the M3 public site.
4. Next research milestone: L6 independent reference cases and comparison of evidence sources. Do not claim novelty or precision improvements from implementation tests.

The L4 history command remains restricted to L1 captures; L5 uses a separate schema and builder. Do not silently mix them or mutate old captures. MCP, LLM agents, IAM providers, corporate connectors and production security are not implemented by this stage.

## Source-of-truth hierarchy

1. `01_CANONICAL_CONTEXT.md` — research thesis and project boundaries; consult implementation checkpoints for newer capabilities.
2. `08_DECISION_LOG.md` — append-only decisions and changes in direction.
3. `09_RESEARCH_LOG.md` — research findings, hypotheses and external evidence.
4. `12_PRODUCT_UX_VISION.md` — product/UX specification; graph-first opening was restored in `17_M2_GRAPH_REVIEW.md`.
5. `27_L5_LOCAL_AUTHORIZATION.md` — current implementation checkpoint.
6. Other detailed research, architecture, product, roadmap and opportunity documents.

## Checkpoint history

- [M1: synthetic data and reference model](./15_M1_VALIDATION.md).
- [M2: review workflow](./16_M2_PREVIEW.md) and [restoration of graph + list](./17_M2_GRAPH_REVIEW.md).
- [M3: asset investigation](./18_ASSET_INVESTIGATION.md). Published evaluation path: `/evidence-graph/preview-m2/`; the older `/evidence-graph/` site is preserved.
- [L1: actual local HTTP/SQLite/OTel](./21_RETOMADA_CORE_E_LABORATORIO.md).
- [L2: capture-to-view adapter](./23_LAB_EVIDENCE_UI.md).
- [L3: source switching, notes and HTTP tests](./25_L3_BROWSER_VALIDATION.md).
- [L4: capture history and comparison](./26_L4_CAPTURE_HISTORY.md).
- [Development roadmap](./24_CORE_NEXT_STEPS.md) and [user evaluation script](./22_ROTEIRO_AVALIACAO_M3.md).

Historical test counts refer to their own revisions and conditions. They are not added together as distinct tests or treated as current production validation.

## Rules

- Separate fact, hypothesis, decision and idea.
- Repetition does not turn hypotheses into facts.
- No novelty claim merely because a feature is new to this project.
- Preserve graph/lineage and operational analysis as complementary views.
- Keep the Core independent from edital/course-specific constraints.
- GitHub is the project memory; chat is a working environment.
- Adaptations belong in their own `opportunities/` directory.
- No fabricated interviews, customer adoption, safety guarantees or commercial results.
- Preserve public site, team documents and personal-material removals unless a task explicitly authorizes changing them.

## Working name

**EvidentGraph — Dependency Intelligence for Data, Software & AI.**

The name emphasizes evidence/provenance and the dependency model; it is not vendor-specific and does not restrict the Core to agents. This is a working name, not trademark/domain clearance.

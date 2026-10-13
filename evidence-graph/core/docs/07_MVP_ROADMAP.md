# MVP & Roadmap

**Updated:** 2026-10-13, M1 checkpoint  
**Status:** M0 documented; M1 synthetic data/reference implementation tested; replacement UI and real PoC pending  
**Product specification:** [12_PRODUCT_UX_VISION.md](./12_PRODUCT_UX_VISION.md)

## Current artifact and boundary

The existing synthetic web demo is preserved. It demonstrates agent review, authorization versus runtime, reachability, impact and hidden dependencies. It is not research validation or a production system.

This roadmap separates three tracks: business discovery, a more complete synthetic product experience, and a small real-collector PoC. Campus Mobile and academic deliverables are not changed.

## Track A — discovery and usability, in parallel

- Interview a small exploratory sample of people who review changes, including a potential buyer and an integration/security stakeholder.
- Ask about recent work and current alternatives before presenting the concept.
- Test whether users can identify consequences, owners and missing information using the prototype.
- Record adoption barriers and willingness to commit resources separately from willingness to pay.

These activities no longer wait until after the technical experiment. The previous sequencing of customer discovery under “Only after the experiment” is superseded by D-011. No interviews or usability sessions were conducted during M1.

## Track B — synthetic product experience

### M0 — product/UX specification — documented

Record the task-first workflow, business hypotheses, evidence semantics, screens, synthetic environment and acceptance criteria in Markdown. The specification is preserved; it does not change the public site.

### M1 — dataset and expected answers — implemented for bounded scenarios

A deterministic generator, stable IDs, evidence fixtures, integrity validation and a reference analyzer are implemented in `../demo-data/`. The generated environment contains **240 assets and 512 meaningful typed relations** across six domains. The count differs from the initial 600–900 illustrative relation range; no random filler was added.

Independent expected answers cover:
1. removal of a field in a customer API;
2. change in forecast output used by a replenishment dashboard;
3. proposed retirement of a legacy service with insufficient observation coverage.

**43 local tests passed.** They cover references, environment/version separation, time windows, deduplication, mutations, cycles, limits and uncertainty. See [15_M1_VALIDATION.md](./15_M1_VALIDATION.md) for reproducibility and limitations.

The analyzer performs bounded consumer review, not unrestricted change propagation, IAM evaluation or proof of field access. Generated JSON and Markdown are reproducible build outputs, not a newly published interface.

### M2 — one complete workflow — next

Implement CHG-001: select change, analyze, filter consumers, inspect owners/evidence, record checks and export Markdown. Start with the answer and table; do not make the graph a prerequisite for understanding the result. Reuse the independent scenario oracles to check any JavaScript port.

### M3 — contextual graph and additional scenarios

Add progressive exploration and inventory navigation, reusing the same model for analytical and legacy-service scenarios. Do not display the entire enterprise graph by default.

### M4 — review before replacement

Check functionality, keyboard navigation, layout and uncertainty states; conduct exploratory usability sessions. Retain the existing public demo until the replacement is explicitly reviewed for publication.

A larger synthetic dataset demonstrates only prototype behavior under its tested conditions, not production scalability or real data coverage.

## Track C — small real-collector PoC

### Technical milestone 0.1

Retain the controlled environment from the original plan:

Agent → MCP tool → API → Service → PostgreSQL table/column

Identity and authorization are evaluated as context, not fabricated runtime calls. Add a non-agent consumer only when needed for the impact experiment.

Minimum evidence sources:
- OpenAPI contract;
- OpenTelemetry traces;
- PostgreSQL metadata/query evidence;
- MCP configuration;
- explicit, simplified authorization/scopes.

Use controlled entity identifiers first. Broad automated entity resolution, enterprise credentials and multiple platform connectors remain out of scope.

### Technical milestone 0.2

Compare the original three conditions on the same controlled cases:
1. metadata/config only;
2. metadata + runtime;
3. metadata + runtime + authorization.

Specify the target separately for possible dependency, observed dependency and incompatibility under a change. Prepare positive, negative and unknown cases. Measure precision, recall, false positives/negatives, freshness, coverage, unknown rate and time-to-answer.

Do not score absent telemetry as proof of a negative. Do not infer a sensitive field was accessed only because its table was queried. No technical gains are claimed before testing.

## Later, subject to evidence

- Databricks and other platform connectors;
- actual GitHub/CI integration;
- larger-scale entity resolution;
- access review and agent passport workflows;
- temporal investigation;
- broader impact analysis;
- commercial pilot and operational security controls.

The forecast dashboard scenario does not turn EvidentGraph into a forecasting product. It is a test of dependencies spanning data, models and business-facing outputs.

## Publication and completion rules

The Core has no mandatory mobile platform. Do not change the current demo URL, recreate the removed root landing page, import personal/professional material, or alter opportunity files as part of this roadmap update.

M0 is documented and M1 has local synthetic-data/reference tests. M2–M5, real user sessions, collectors and commercial validation remain pending. See the UX acceptance checklist in `12_PRODUCT_UX_VISION.md` before declaring the next demo complete.

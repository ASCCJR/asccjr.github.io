# Product Vision

## Problem

Enterprises increasingly distribute dependency knowledge across separate systems:

- data catalogs and lineage;
- source repositories and API contracts;
- IAM and gateways;
- observability and OpenTelemetry;
- AI-agent platforms and MCP registries;
- cloud/data platforms such as Databricks.

Each system sees only part of the architecture.

## Proposed value

EvidentGraph investigates a cross-platform evidence layer that can answer:

### CAN IT?
Can an agent, service, application, or identity reach a target resource under current topology and authorization?

### DID IT?
Was that path actually observed in runtime telemetry?

### WHAT BREAKS?
If a schema, API, MCP tool, permission, model endpoint, or dependency changes, what is the potential and active blast radius?

## Agentic AI as flagship use case

Agentic AI is an important demonstration domain because an agent may combine:
- an identity;
- scopes / permissions;
- tools;
- MCP servers;
- APIs;
- models;
- databases / knowledge bases;
- external destinations.

Agentic AI is a flagship use case, not the full scope of the Core. The next interface starts from a user task, not necessarily from an agent profile.

## Long-term product possibilities

Possible delivery modes include:
- web graph/explorer;
- pre-change GitHub/CI check;
- agent risk passport/review;
- architecture black-box / forensic timeline;
- API for programmatic dependency queries;
- natural-language interface over verified graph queries.

These are product hypotheses, not yet validated business decisions.

## Current product/UX specification — 2026-10-13

See [12_PRODUCT_UX_VISION.md](./12_PRODUCT_UX_VISION.md).

The first complete workflow is **change-impact review**: select an API change, understand possible consequences, inspect consumers and evidence, identify owners, record checks and export a report.

Results and decision-relevant uncertainty precede graph exploration. A larger, coherent synthetic enterprise environment supports UX testing; it does not replace the small real-collector PoC. User, buyer, adoption process and commercial value remain discovery hypotheses.

The initial experience includes non-agent operational consumers and an analytical chain involving a forecast model and dashboard. No mobile requirement is added to the Core, and no enforcement or production-readiness claim follows from this revision.

## Reconciled product direction — 2026-10-20

The later graph-restoration decision and implemented M3/L7 supersede any reading of the 2026-10-13 proposal as removal of the graph. Graph/lineage and the operational change-review table work together: inspect dependencies and context, identify consumers/owners, preserve uncertainty, record checks and export a scoped analysis. Keep the accepted visual experience and the complete synthetic Aurora separate from small execution captures; no new redesign follows from this transfer.

The initial audience remains a hypothesis: the technical owner of an API/application/pipeline change, collaborating with consumer owners. Engineering/Platform leadership is a possible buyer and Security/source owners possible integration approvers. Begin with one team/flow and explicitly permitted evidence. Time saved, incidents avoided, willingness to pay and ROI have not been measured. A fixed-scope diagnostic/pilot and recurring use are commercial hypotheses, not established revenue.

An academic “Pre-Change Evidence Gate” is one possible way to deliver the value within a PR/change workflow; a production blocking integration has not been implemented, and the Core is not restricted to a plugin. The next proposal work is in [CTE-IA](../../opportunities/cte-ia-2026/README.md), under D-014, without adding decorative AI to fit a call.

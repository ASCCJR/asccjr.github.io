# EvidentGraph — Core

**Working name:** EvidentGraph  
**Subtitle:** Dependency Intelligence for Data, Software & AI  
**Status:** applied research / discovery / pre-MVP

This folder is the canonical home of the project.

The Core is independent from competitions, grants, academic assignments, or a specific vendor. Opportunity-specific adaptations must not rewrite the Core.

## What EvidentGraph investigates

EvidentGraph investigates whether correlating multiple evidence planes can improve dependency, reachability, and change-impact analysis:

- declared configuration;
- static code/contracts;
- authorization / IAM;
- lineage;
- runtime telemetry.

The three core questions remain:

- **CAN IT?** — can an agent, application, service, or identity reach a resource?
- **DID IT?** — was that path actually observed?
- **WHAT BREAKS?** — what may be affected if an asset, contract, policy, or dependency changes?

## Memory protocol

When resuming the project in a new chat or after context compaction, read in this order:

1. `docs/00_START_HERE.md`
2. `docs/01_CANONICAL_CONTEXT.md`
3. `docs/08_DECISION_LOG.md`
4. `docs/09_RESEARCH_LOG.md`

Then load task-specific files such as architecture, competition, roadmap, or course activities.

## Important separation

- `core/` = canonical project
- `opportunities/claro-campus-mobile-2026/` = Campus Mobile variant
- `core/academic/project-discipline/` = coursework using the Core as the project
- the published synthetic demo remains at the repository root and is a reusable artifact, not the source of truth

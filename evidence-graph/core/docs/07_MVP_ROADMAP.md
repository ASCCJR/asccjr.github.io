# MVP & Roadmap

## Current artifact

A synthetic web demo exists and is intentionally preserved for future presentations and portfolio use.

It demonstrates:
- agent risk review;
- authorization check;
- runtime trace;
- CAN IT?;
- DID IT?;
- WHAT BREAKS?;
- hidden dependency conflict.

The synthetic demo is not the research validation.

## MVP 0.1 — real collectors

Target a small, controlled chain:

Agent  
→ Identity  
→ MCP tool  
→ API  
→ Service  
→ PostgreSQL table/column

Minimum real evidence:
- OpenAPI contract;
- OpenTelemetry trace;
- PostgreSQL metadata/query evidence;
- MCP configuration;
- simple authorization/scopes.

## MVP 0.2 — evidence comparison experiment

Compare:
1. metadata/config only;
2. metadata + runtime;
3. metadata + runtime + authorization.

Measure:
- precision;
- recall;
- false positives;
- false negatives;
- freshness;
- evidence coverage;
- time-to-answer.

## Later

Only after the experiment:
- Databricks connector;
- GitHub/CI integration;
- automatic entity resolution at larger scale;
- agent passport / risk review;
- pre-change blast radius;
- temporal graph;
- customer discovery / startup validation.

# Mobile Adaptation — EvidentGraph Mobile

## Goal

Create a Campus Mobile-compliant version without distorting the Core.

## Strongest working concept

### Mobile dependency intelligence for agentic systems

Use a mobile application/service ecosystem as the target architecture:

Mobile App  
→ API Gateway  
→ Customer API  
→ Customer Service  
→ Data  
→ AI Agent / MCP / external model

EvidentGraph Mobile reconstructs and explains paths across that ecosystem.

## Possible mobile user

A platform/SRE/security engineer receives a mobile alert about a change or risky agent path and can quickly inspect:

- which mobile service/app journey is affected;
- which API changed;
- which agent/tool depends on it;
- whether PII is reachable;
- whether the path was observed recently.

## Demonstrable scenarios

### Scenario A — mobile API change
A mobile app depends on an endpoint whose contract changes.

Question:
**WHAT BREAKS?**

Output:
- affected mobile app journey;
- API consumers;
- active agents;
- observed vs dormant paths.

### Scenario B — agent + mobile customer data
An AI agent can call a tool that reaches customer data used by a mobile app.

Questions:
**CAN IT?**
**DID IT?**

### Scenario C — incident response on mobile
A production alert appears on a phone; the engineer opens the dependency path and sees the active blast radius.

## Anti-pattern

Do not claim compliance simply because the existing desktop dashboard is responsive/mobile-friendly.

The mobile use case should be part of the problem and value proposition.

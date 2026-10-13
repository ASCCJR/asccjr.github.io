"""Synthetic data and bounded reference analysis. Python 3.10+, standard library only.

Not a production dependency engine, an IAM evaluator or a real collector.
Run: python model.py --out build
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

VERSION = "0.1.0"
CLOCK = "2026-10-13T12:00:00Z"
START = "2026-09-13T12:00:00Z"
DOMAINS = {
    "comercial": ["clientes", "pedidos", "precos", "catalogo"],
    "atendimento": ["conversas", "chamados", "conhecimento", "satisfacao"],
    "operacoes": ["estoque", "expedicao", "entregas", "reposicao"],
    "financeiro": ["pagamentos", "faturas", "conciliacao", "cobranca"],
    "dados": ["ingestao", "qualidade", "previsao", "indicadores"],
    "plataforma": ["identidade", "configuracao", "auditoria", "notificacoes"],
}
TARGET_COUNTS = {"application": 12, "api": 28, "service": 24, "pipeline": 24,
                 "table": 52, "column": 48, "dashboard": 12, "model": 8,
                 "agent": 8, "mcp_server": 4, "mcp_tool": 4, "identity": 16}
FAMILIES = ("config", "code", "authorization", "lineage", "runtime")
# Stored arrow: source -> target. Only CALLS / USES_TOOL / READS participate
# in the initial bounded consumer query; structural relations are not calls.
RELATIONS = {
    "ROUTES_TO": ({"api"}, {"service"}),
    "READS": ({"service", "pipeline", "dashboard"}, {"table"}),
    "WRITES": ({"service", "pipeline"}, {"table"}),
    "DERIVES_TO": ({"table"}, {"table"}),
    "CONTAINS": ({"table"}, {"column"}),
    "CALLS": ({"application", "service", "agent", "mcp_tool", "pipeline"}, {"api", "service"}),
    "USES_TOOL": ({"agent"}, {"mcp_tool"}),
    "HOSTS": ({"mcp_server"}, {"mcp_tool"}),
    "HAS_IDENTITY": ({"agent", "pipeline", "service"}, {"identity"}),
    "USES_MODEL": ({"pipeline", "agent"}, {"model"}),
    "TRAINED_ON": ({"model"}, {"table"}),
}
LABELS = {
    "INCOMPATIBILITY": "Incompatibilidade identificada no contrato avaliado",
    "POSSIBLE": "Impacto possível; consumo do campo não confirmado",
    "INCONCLUSIVE": "Impacto inconclusivo; verificar dependência",
    "NO_INCOMPATIBILITY": "Sem incompatibilidade identificada no contrato avaliado",
}


def instant(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return dt.astimezone(timezone.utc)


def encode(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def make_dataset() -> dict[str, Any]:
    """Deterministic templates, no random filler and no external requests."""
    data: dict[str, Any] = {
        "schema_version": VERSION, "dataset_version": "enterprise-demo-0.1.0",
        "synthetic": True, "clock": CLOCK,
        "domains": [{"id": d, "name": d.capitalize()} for d in DOMAINS],
        "teams": [{"id": "team-" + d, "domain": d, "name": "Equipe Demo " + d.capitalize()} for d in DOMAINS],
        "processes": [{"id": f"proc-{d}-{t}", "domain": d, "name": t.replace("-", " ")} for d, ts in DOMAINS.items() for t in ts],
        "sources": [{"id": "src-" + f, "family": f, "synthetic": True,
                     "max_age_hours": 48} for f in FAMILIES],
        "assets": [], "relations": [], "evidence": [], "coverage": [], "changes": [],
    }
    assets: dict[str, dict[str, Any]] = {}

    def asset(aid: str, kind: str, domain: str, topic: str, name: str | None = None,
              env: str = "prod-demo") -> None:
        a = {"id": aid, "kind": kind, "name": name or aid, "domain": domain,
             "owner": "team-" + domain, "environment": env, "version": "1.0",
             "processes": [f"proc-{domain}-{topic}"], "criticality": "standard"}
        assets[aid] = a
        data["assets"].append(a)

    def evidence(eid: str, family: str, subject: str, target: str, claim: str,
                 **extra: Any) -> str:
        e = {"id": eid, "family": family, "source": "src-" + family,
             "origin_id": eid, "reference": "synthetic://" + eid,
             "subject": subject, "target": target, "claim": claim,
             "environment": assets[subject]["environment"],
             "subject_version": assets[subject]["version"],
             "target_version": assets[target]["version"],
             "valid_from": "2026-09-01T00:00:00Z", "valid_until": None,
             "collected_at": "2026-10-13T11:00:00Z", "details": extra}
        data["evidence"].append(e)
        return eid

    def relation(src: str, dst: str, kind: str, rid: str | None = None) -> str:
        rid = rid or f"rel:{kind}:{src}:{dst}"
        family = "lineage" if kind in {"DERIVES_TO", "CONTAINS", "TRAINED_ON"} else "config"
        eid = evidence("ev:" + rid, family, src, dst, "dependency")
        data["relations"].append({"id": rid, "source": src, "target": dst,
                                   "kind": kind, "evidence_ids": [eid]})
        return rid

    for d, topics in DOMAINS.items():
        for t in topics:
            for prefix, kind in [("svc", "service"), ("api", "api"), ("job", "pipeline")]:
                asset(f"{prefix}-{d}-{t}", kind, d, t)
            for layer in ("raw", "curated"):
                tid = f"tbl-{d}-{t}-{layer}"
                asset(tid, "table", d, t)
                asset(tid + ".id", "column", d, t)
        for suffix in ("portal", "console"):
            asset(f"app-{d}-{suffix}", "application", d, topics[0])
            asset(f"dash-{d}-{suffix}", "dashboard", d, topics[0])
        asset("agent-" + d, "agent", d, topics[0])
        asset("model-" + d, "model", d, topics[0])
        for suffix in ("agent", "batch"):
            asset(f"identity-{d}-{suffix}", "identity", d, topics[0])
    for d, t in [("dados", "previsao"), ("operacoes", "reposicao")]:
        asset(f"model-{d}-{t}", "model", d, t)
        asset(f"agent-{d}-{t}", "agent", d, t)
    for d in list(DOMAINS)[:4]:
        t = DOMAINS[d][0]
        asset("mcp-" + d, "mcp_server", d, t)
        asset("tool-" + d, "mcp_tool", d, t)
        asset("identity-" + d + "-service", "identity", d, t)
    for aid, kind, d, t, name, env in [
        ("api-clientes-v2", "api", "comercial", "clientes", "GET /customers/{id} v2", "prod-demo"),
        ("api-clientes-qa", "api", "comercial", "clientes", "GET /customers/{id} v2 QA", "qa-demo"),
        ("api-previsao", "api", "dados", "previsao", "API de previsão", "prod-demo"),
        ("api-legado", "api", "plataforma", "configuracao", "API de arquivo legado", "prod-demo"),
        ("tbl-previsao-saida", "table", "dados", "previsao", "Resultados de previsão", "prod-demo"),
        ("tbl-clientes-historico", "table", "comercial", "clientes", "Histórico de clientes", "prod-demo"),
        ("tbl-rotina-mensal", "table", "financeiro", "cobranca", "Fechamento mensal", "prod-demo"),
        ("tbl-metricas", "table", "plataforma", "auditoria", "Métricas técnicas", "prod-demo"),
    ]:
        asset(aid, kind, d, t, name, env)

    for d, ts in DOMAINS.items():
        for t in ts:
            svc, api, job = (f"{p}-{d}-{t}" for p in ("svc", "api", "job"))
            raw, curated = (f"tbl-{d}-{t}-{layer}" for layer in ("raw", "curated"))
            relation(api, svc, "ROUTES_TO")
            relation(svc, raw, "WRITES")
            relation(svc, curated, "READS")
            relation(job, raw, "READS")
            relation(job, curated, "WRITES")
            relation(raw, curated, "DERIVES_TO")
            relation(job, f"identity-{d}-batch", "HAS_IDENTITY")
            for tid in (raw, curated):
                relation(tid, tid + ".id", "CONTAINS")
            for suffix in ("portal", "console"):
                relation(f"app-{d}-{suffix}", api, "CALLS")
                relation(f"dash-{d}-{suffix}", curated, "READS")
            relation("agent-" + d, api, "CALLS")
            relation("model-" + d, raw, "TRAINED_ON")
            relation(job, "model-" + d, "USES_MODEL")
        relation("agent-" + d, "identity-" + d + "-agent", "HAS_IDENTITY")
        relation("agent-" + d, "model-" + d, "USES_MODEL")
    for d in list(DOMAINS)[:4]:
        relation("agent-" + d, "tool-" + d, "USES_TOOL")
        relation("mcp-" + d, "tool-" + d, "HOSTS")
        relation("tool-" + d, f"api-{d}-{DOMAINS[d][0]}", "CALLS")
        for t in DOMAINS[d]:
            relation(f"svc-{d}-{t}", "identity-" + d + "-service", "HAS_IDENTITY")
    # Explicit named joins in each domain, not a random graph.
    joins = {
        "comercial": [("pedidos", "clientes"), ("pedidos", "precos"), ("pedidos", "catalogo"), ("precos", "catalogo")],
        "atendimento": [("chamados", "conversas"), ("conversas", "conhecimento"), ("satisfacao", "chamados"), ("satisfacao", "conversas")],
        "operacoes": [("expedicao", "estoque"), ("entregas", "expedicao"), ("reposicao", "estoque"), ("reposicao", "entregas")],
        "financeiro": [("faturas", "pagamentos"), ("conciliacao", "pagamentos"), ("conciliacao", "faturas"), ("cobranca", "faturas")],
        "dados": [("qualidade", "ingestao"), ("previsao", "qualidade"), ("indicadores", "qualidade"), ("indicadores", "previsao")],
        "plataforma": [("configuracao", "identidade"), ("auditoria", "identidade"), ("notificacoes", "auditoria"), ("auditoria", "configuracao")],
    }
    for d, pairs in joins.items():
        for target_topic, source_topic in pairs:
            src, dst = f"tbl-{d}-{source_topic}-curated", f"tbl-{d}-{target_topic}-curated"
            relation(f"job-{d}-{target_topic}", src, "READS")
            relation(src, dst, "DERIVES_TO")
    # Cross-domain business handoffs (order, payment, dispatch, support, forecasting).
    cross = [("comercial-pedidos", "financeiro-pagamentos"), ("comercial-pedidos", "operacoes-expedicao"),
             ("comercial-clientes", "atendimento-chamados"), ("operacoes-entregas", "atendimento-satisfacao"),
             ("comercial-pedidos", "dados-ingestao"), ("operacoes-estoque", "dados-ingestao"),
             ("financeiro-pagamentos", "dados-indicadores"), ("dados-previsao", "operacoes-reposicao")]
    for src, dst in cross:
        relation("job-" + dst, "tbl-" + src + "-curated", "READS")
        relation("tbl-" + src + "-curated", "tbl-" + dst + "-curated", "DERIVES_TO")
    for d, t in [("dados", "previsao"), ("operacoes", "reposicao")]:
        relation(f"agent-{d}-{t}", f"api-{d}-{t}", "CALLS")
        relation(f"agent-{d}-{t}", f"identity-{d}-agent", "HAS_IDENTITY")
        relation(f"agent-{d}-{t}", f"model-{d}-{t}", "USES_MODEL")
        relation(f"job-{d}-{t}", f"model-{d}-{t}", "USES_MODEL")
        relation(f"model-{d}-{t}", f"tbl-{d}-{t}-raw", "TRAINED_ON")
    relation("api-clientes-v2", "svc-comercial-clientes", "ROUTES_TO")
    relation("api-previsao", "svc-dados-previsao", "ROUTES_TO")
    relation("api-legado", "svc-plataforma-configuracao", "ROUTES_TO")
    relation("job-comercial-clientes", "tbl-clientes-historico", "WRITES")
    relation("job-dados-previsao", "tbl-previsao-saida", "WRITES")
    relation("job-financeiro-cobranca", "tbl-rotina-mensal", "WRITES")
    relation("job-plataforma-auditoria", "tbl-metricas", "WRITES")

    def call(src: str, target: str, rid: str, kind: str = "CALLS",
             observed: bool = False, coverage: str = "unavailable",
             fields: list[str] | None = None, exhaustive: bool = False,
             trace: str = "trace-chg001") -> None:
        relation(src, target, kind, rid)
        if observed:
            eid = evidence("obs:" + rid, "runtime", src, target, "observed_use",
                           at="2026-10-12T10:00:00Z", trace_id=trace)
            data["relations"][-1]["evidence_ids"].append(eid)
        data["coverage"].append({"relation": rid, "source": "src-runtime", "status": coverage,
                                  "start": START, "end": CLOCK, "collected_at": CLOCK,
                                  "environment": assets[src]["environment"],
                                  "subject_version": "1.0", "target_version": "1.0"})
        if fields is not None:
            evidence("contract:" + rid, "code", src, target, "consumer_fields",
                     required_fields=fields, exhaustive=exhaustive)

    # Existing USES_TOOL edge gets positive correlated telemetry below.
    rid_tool = "rel:USES_TOOL:agent-atendimento:tool-atendimento"
    evidence("obs:agent-tool", "runtime", "agent-atendimento", "tool-atendimento", "observed_use",
             at="2026-10-12T10:00:00Z", trace_id="trace-chg001")
    next(r for r in data["relations"] if r["id"] == rid_tool)["evidence_ids"].append("obs:agent-tool")
    call("svc-comercial-pedidos", "api-clientes-v2", "rel-order-customer", observed=True,
         coverage="complete", fields=["cliente_id"], exhaustive=True)
    call("tool-atendimento", "api-clientes-v2", "rel-tool-customer", observed=True, coverage="partial")
    call("job-financeiro-conciliacao", "api-clientes-v2", "rel-export-customer")
    call("app-atendimento-portal", "api-clientes-v2", "rel-portal-customer", observed=True,
         coverage="complete", fields=["nome", "situacao"], exhaustive=True)
    call("dash-operacoes-portal", "tbl-previsao-saida", "rel-dashboard-forecast", "READS",
         True, "complete", ["quantidade_prevista"], True, "trace-forecast")
    call("job-operacoes-reposicao", "tbl-previsao-saida", "rel-job-forecast", "READS",
         True, "partial", trace="trace-forecast")
    call("job-financeiro-cobranca", "api-legado", "rel-monthly-legacy", coverage="partial")
    assets["svc-comercial-pedidos"]["criticality"] = "high"
    assets["job-financeiro-cobranca"]["schedule"] = "monthly"
    for cid, target, operation, field, kinds in [
        ("CHG-001", "api-clientes-v2", "remove_field", "cliente_id", ["CALLS", "USES_TOOL"]),
        ("CHG-002", "tbl-previsao-saida", "remove_field", "quantidade_prevista", ["READS"]),
        ("CHG-003", "api-legado", "retire", None, ["CALLS", "USES_TOOL"]),
    ]:
        data["changes"].append({"id": cid, "target": target, "operation": operation,
                                "field": field, "before_version": "1.0", "after_version": "2.0",
                                "environment": "prod-demo", "window_start": START,
                                "window_end": CLOCK, "consumer_relations": kinds,
                                "max_depth": 8, "max_paths": 500})
    data["inventory_limits"] = ["Selected columns only; not a complete database schema.",
                                "QA API deliberately has no collectors or known consumers.",
                                "Most catalog links are configuration/lineage only; not runtime observations."]
    aliases = {
        "svc-comercial-pedidos": "Serviço de pedidos",
        "agent-atendimento": "Agente de atendimento",
        "job-financeiro-conciliacao": "Exportador financeiro",
        "app-atendimento-portal": "Portal de acompanhamento",
        "dash-operacoes-portal": "Dashboard de reposição",
        "job-operacoes-reposicao": "Rotina de reposição",
        "job-financeiro-cobranca": "Rotina de fechamento mensal",
        "tool-atendimento": "Consultar cliente (MCP)",
    }
    for aid, name in aliases.items():
        assets[aid]["name"] = name
    for aid, pid in {
        "svc-comercial-pedidos": "proc-comercial-pedidos",
        "agent-atendimento": "proc-atendimento-chamados",
        "app-atendimento-portal": "proc-comercial-pedidos",
        "dash-operacoes-portal": "proc-operacoes-reposicao",
    }.items():
        assets[aid]["processes"] = [pid]
    validate(data)
    return data


def _validate(data: dict[str, Any]) -> None:
    """Cross-reference, enum, type and temporal validation; raises ValueError."""
    def require(condition: bool, reason: str) -> None:
        if not condition:
            raise ValueError(reason)
    require(data.get("synthetic") is True and data.get("schema_version") == VERSION, "unsupported dataset")
    now = instant(data["clock"])
    indexes = {}
    for section in ("assets", "domains", "teams", "processes", "sources", "relations", "evidence", "changes"):
        values = data[section]
        require(isinstance(values, list), "collection must be list: " + section)
        ids = [v["id"] for v in values]
        require(len(set(ids)) == len(ids), "duplicate id: " + section)
        indexes[section] = {v["id"]: v for v in values}
    a, e = indexes["assets"], indexes["evidence"]
    for asset in a.values():
        require(asset["kind"] in TARGET_COUNTS, "unknown asset kind")
        require(asset["domain"] in indexes["domains"], "orphan domain")
        require(asset["owner"] in indexes["teams"], "orphan owner")
        require(all(p in indexes["processes"] for p in asset["processes"]), "orphan process")
        require(asset["environment"] in {"prod-demo", "qa-demo"}, "unknown environment")
        require(isinstance(asset["version"], str) and bool(asset["version"]), "invalid version")
    for ev in e.values():
        require(ev["subject"] in a and ev["target"] in a, "orphan evidence asset")
        require(ev["family"] in FAMILIES, "unknown evidence family")
        require(ev["source"] in indexes["sources"], "orphan evidence source")
        require(indexes["sources"][ev["source"]]["family"] == ev["family"], "source family mismatch")
        require(ev["reference"].startswith("synthetic://"), "non-synthetic reference")
        require(instant(ev["collected_at"]) <= now, "future collection")
        if ev["valid_until"]:
            require(instant(ev["valid_from"]) < instant(ev["valid_until"]), "invalid validity interval")
        require(ev["claim"] in {"dependency", "observed_use", "consumer_fields"}, "unknown claim")
        require(ev["claim"] != "observed_use" or ev["family"] == "runtime", "runtime family required")
        require(ev["claim"] != "consumer_fields" or ev["family"] == "code", "code family required")
        if ev["claim"] == "observed_use":
            require(instant(ev["details"]["at"]) <= instant(ev["collected_at"]), "future observation")
            require(bool(ev["details"].get("trace_id")), "trace id required")
        if ev["claim"] == "consumer_fields":
            require(isinstance(ev["details"].get("exhaustive"), bool), "contract completeness required")
            fields = ev["details"].get("required_fields")
            require(isinstance(fields, list) and all(isinstance(x, str) for x in fields), "fields must be a string list")
    triples = set()
    for r in data["relations"]:
        require(r["source"] in a and r["target"] in a, "orphan relation asset")
        require(r["kind"] in RELATIONS, "unknown relation kind")
        require(a[r["source"]]["environment"] == a[r["target"]]["environment"], "cross-environment relation")
        pair = RELATIONS[r["kind"]]
        require(a[r["source"]]["kind"] in pair[0] and a[r["target"]]["kind"] in pair[1], "invalid relation endpoints")
        triple = (r["source"], r["target"], r["kind"])
        require(triple not in triples, "duplicate relation")
        triples.add(triple)
        for eid in r["evidence_ids"]:
            require(eid in e, "orphan evidence reference")
            require((e[eid]["subject"], e[eid]["target"]) == (r["source"], r["target"]), "evidence endpoint mismatch")
            require(e[eid]["claim"] in {"dependency", "observed_use"}, "invalid relation evidence")
            require(e[eid]["claim"] != "observed_use" or r["kind"] in {"CALLS", "USES_TOOL", "READS"}, "structural edge is not runtime")
    for source in data["sources"]:
        require(source["synthetic"] is True and source["family"] in FAMILIES, "invalid source")
        require(isinstance(source["max_age_hours"], (int, float)) and source["max_age_hours"] > 0, "invalid freshness limit")
    for c in data["coverage"]:
        require(c["relation"] in indexes["relations"], "orphan coverage")
        require(c["source"] in indexes["sources"] and indexes["sources"][c["source"]]["family"] == "runtime", "invalid coverage source")
        require(c["status"] in {"complete", "partial", "unavailable"}, "invalid coverage status")
        require(instant(c["start"]) <= instant(c["end"]) <= instant(c["collected_at"]) <= now, "invalid coverage interval")
    for c in data["changes"]:
        require(c["target"] in a, "orphan change target")
        require(c["operation"] in {"remove_field", "retire"}, "unsupported operation")
        require(c["operation"] != "remove_field" or bool(c["field"]), "field required")
        require(c["environment"] == a[c["target"]]["environment"], "change environment mismatch")
        require(c["before_version"] == a[c["target"]]["version"], "change version mismatch")
        require(instant(c["window_start"]) <= instant(c["window_end"]) <= now, "invalid query interval")
        require(set(c["consumer_relations"]) <= {"CALLS", "USES_TOOL", "READS"}, "unsupported traversal")
        require(isinstance(c["max_depth"], int) and c["max_depth"] > 0, "invalid depth")
        require(isinstance(c["max_paths"], int) and c["max_paths"] > 0, "invalid path limit")


def validate(data: dict[str, Any]) -> None:
    """Normalize malformed input errors while preserving specific validation errors."""
    try:
        _validate(data)
    except (KeyError, TypeError, AttributeError, IndexError) as exc:
        raise ValueError("malformed dataset: " + str(exc)) from exc


def analyze(data: dict[str, Any], change_id: str) -> dict[str, Any]:
    """Bounded consumer review, not unrestricted graph-wide breakage prediction."""
    validate(data)
    changes = {x["id"]: x for x in data["changes"]}
    if change_id not in changes:
        raise ValueError("unknown change: " + change_id)
    c = changes[change_id]
    assets = {a["id"]: a for a in data["assets"]}
    evidences = {e["id"]: e for e in data["evidence"]}
    sources = {s["id"]: s for s in data["sources"]}
    now, start, end = instant(data["clock"]), instant(c["window_start"]), instant(c["window_end"])

    def eligible(ev: dict[str, Any]) -> bool:
        return (ev["environment"] == c["environment"]
                and ev["subject_version"] == assets[ev["subject"]]["version"]
                and ev["target_version"] == assets[ev["target"]]["version"]
                and instant(ev["valid_from"]) <= now
                and (ev["valid_until"] is None or now < instant(ev["valid_until"]))
                and now - instant(ev["collected_at"]) <= timedelta(hours=sources[ev["source"]]["max_age_hours"]))

    active = {eid: e for eid, e in evidences.items() if eligible(e)}
    incoming: dict[str, list[dict[str, Any]]] = {}
    for r in data["relations"]:
        if (r["kind"] in c["consumer_relations"]
                and any(eid in active for eid in r["evidence_ids"])):
            incoming.setdefault(r["target"], []).append(r)
    for links in incoming.values():
        links.sort(key=lambda r: r["id"])
    paths: dict[str, list[list[dict[str, Any]]]] = {}
    stack = [(c["target"], [], {c["target"]})]
    examined, truncated = 0, False
    while stack:
        target, suffix, visited = stack.pop()
        for r in incoming.get(target, []):
            src = r["source"]
            if src in visited:
                continue
            if len(suffix) >= c["max_depth"] or examined >= c["max_paths"]:
                truncated = True
                continue
            path = [r] + suffix
            examined += 1
            if assets[src]["kind"] not in {"mcp_tool", "mcp_server"}:
                paths.setdefault(src, []).append(path)
            stack.append((src, path, visited | {src}))

    def observed(path: list[dict[str, Any]]) -> bool:
        traces = []
        for r in path:
            traces.append({active[eid]["details"]["trace_id"] for eid in r["evidence_ids"]
                           if eid in active and active[eid]["claim"] == "observed_use"
                           and start <= instant(active[eid]["details"]["at"]) <= end})
        return bool(traces and set.intersection(*traces))

    def covered(r: dict[str, Any]) -> bool:
        records = [v for v in data["coverage"] if v["relation"] == r["id"]]
        if not records:
            return False
        # A newer outage must supersede an older complete-coverage claim.
        v = max(records, key=lambda item: (instant(item["collected_at"]),
                                          {"complete": 0, "partial": 1, "unavailable": 2}[item["status"]]))
        return (v["status"] == "complete" and v["environment"] == c["environment"]
                and v["subject_version"] == assets[r["source"]]["version"]
                and v["target_version"] == assets[r["target"]]["version"]
                and instant(v["start"]) <= start and instant(v["end"]) >= end
                and now - instant(v["collected_at"]) <= timedelta(hours=sources[v["source"]]["max_age_hours"]))

    rows = []
    for aid, alternatives in sorted(paths.items()):
        is_observed = any(observed(p) for p in alternatives)
        has_any_event = any(eid in active and active[eid]["claim"] == "observed_use"
                            and start <= instant(active[eid]["details"]["at"]) <= end
                            for p in alternatives for r in p for eid in r["evidence_ids"])
        # Uncorrelated multi-hop spans are not an observed end-to-end path.
        complete = all(covered(r) for p in alternatives for r in p)
        activity = "OBSERVED" if is_observed else "NOT_OBSERVED" if complete and not has_any_event else "UNKNOWN"
        contracts = [e for e in active.values() if e["subject"] == aid and e["target"] == c["target"]
                     and e["claim"] == "consumer_fields"]
        requires = any(c["field"] in e["details"]["required_fields"] for e in contracts)
        excludes = any(e["details"]["exhaustive"] and c["field"] not in e["details"]["required_fields"] for e in contracts)
        conflict = c["operation"] == "remove_field" and requires and excludes
        if conflict:
            impact = "INCONCLUSIVE"
        elif c["operation"] == "remove_field" and requires:
            impact = "INCOMPATIBILITY"
        elif c["operation"] == "remove_field" and excludes:
            impact = "NO_INCOMPATIBILITY"
        else:
            impact = "POSSIBLE" if is_observed else "INCONCLUSIVE"
        refs = sorted({eid for p in alternatives for r in p for eid in r["evidence_ids"] if eid in active}
                      | {e["id"] for e in contracts})
        limitations = []
        if conflict:
            limitations.append("Conflito entre contratos válidos no mesmo escopo; resolver antes de concluir.")
        if activity == "UNKNOWN":
            limitations.append("Não há observação correlacionada suficiente deste caminho na janela.")
        if not contracts and c["operation"] == "remove_field":
            limitations.append("Não há contrato de consumo do campo para este consumidor e recurso.")
        if c["operation"] == "retire":
            limitations.append("Ausência de uso na janela não autoriza desativação; verificar rotinas esporádicas.")
        rows.append({"consumer": aid, "name": assets[aid]["name"], "owner": assets[aid]["owner"],
                     "processes": assets[aid]["processes"], "criticality": assets[aid]["criticality"],
                     "impact": impact, "activity": activity, "contract_conflict": conflict,
                     "authorization": "NOT_EVALUATED", "field_access": "NOT_EVALUATED",
                     "paths": [[r["id"] for r in p] for p in alternatives],
                     "evidence_ids": refs, "origin_ids": sorted({active[eid]["origin_id"] for eid in refs}),
                     "limitations": limitations,
                     "next_step": "Resolver contratos conflitantes" if conflict else
                                  "Validar migração do contrato" if impact == "INCOMPATIBILITY" else
                                  "Registrar limites da verificação" if impact == "NO_INCOMPATIBILITY" else
                                  "Verificar consumo e cobertura com a equipe responsável"})
    return {"schema_version": VERSION, "synthetic": True, "dataset_version": data["dataset_version"],
            "change": copy.deepcopy(c), "clock": data["clock"], "consumers": rows,
            "counts": {"consumers": len(rows), "impact": dict(sorted(Counter(r["impact"] for r in rows).items())),
                       "activity": dict(sorted(Counter(r["activity"] for r in rows).items()))},
            "truncated": truncated, "scope_complete": False,
            "scope_note": "Consumidores conhecidos nas relações selecionadas; não prova cobertura corporativa nem segurança de publicação."}


def report(result: dict[str, Any]) -> str:
    """UTF-8 Markdown export for human review. Never reports a deployment action."""
    lines = [f"# {result['change']['id']} — análise sintética", "",
             f"Dataset: `{result['dataset_version']}` · relógio: `{result['clock']}`", "",
             "**Dados fictícios. Análise de referência; não há integrações reais.**", "",
             f"Recurso: `{result['change']['target']}` · operação: `{result['change']['operation']}` · campo: `{result['change']['field']}`", "",
             f"Versões: `{result['change']['before_version']}` → `{result['change']['after_version']}` · ambiente: `{result['change']['environment']}`", "",
             f"Janela: `{result['change']['window_start']}` a `{result['change']['window_end']}`", "",
             f"Consumidores distintos no escopo: **{result['counts']['consumers']}**.", "",
             "| Consumidor | Impacto | Observação | Responsável | Próximo passo |",
             "|---|---|---|---|---|"]
    for r in result["consumers"]:
        lines.append(f"| {r['consumer']} | {LABELS[r['impact']]} | {r['activity']} | {r['owner']} | {r['next_step']} |")
    lines += ["", result["scope_note"], "", f"Busca truncada: {result['truncated']}. Autorização e acesso ao campo não avaliados."]
    for row in result["consumers"]:
        lines += ["", "## " + row["consumer"], "", "Processos: " + ", ".join(row["processes"]), "",
                  "Evidências: " + ", ".join(f"`{x}`" for x in row["evidence_ids"])]
        lines += ["", "Caminhos:"]
        lines += ["- " + " → ".join(f"`{rid}`" for rid in path) for path in row["paths"]]
        lines += ["- " + limit for limit in row["limitations"]]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path(__file__).parent / "build")
    args = parser.parse_args()
    data = make_dataset()
    args.out.mkdir(parents=True, exist_ok=True)
    dataset_text = encode(data)
    (args.out / "enterprise.json").write_text(dataset_text, encoding="utf-8")
    for c in data["changes"]:
        result = analyze(data, c["id"])
        (args.out / (c["id"] + ".json")).write_text(encode(result), encoding="utf-8")
        (args.out / (c["id"] + ".md")).write_text(report(result), encoding="utf-8")
    summary = {"assets": len(data["assets"]), "relations": len(data["relations"]),
               "evidence": len(data["evidence"]), "coverage": len(data["coverage"]),
               "asset_counts": dict(sorted(Counter(a["kind"] for a in data["assets"]).items())),
               "sha256": hashlib.sha256(dataset_text.encode()).hexdigest()}
    (args.out / "manifest.json").write_text(encode(summary), encoding="utf-8")
    print(encode(summary))


if __name__ == "__main__":
    main()

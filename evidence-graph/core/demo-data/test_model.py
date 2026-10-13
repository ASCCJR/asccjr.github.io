"""Independent scenario oracles and negative/mutation tests; no network."""
import copy
import json
import unittest
from collections import Counter
from pathlib import Path

from model import CLOCK, TARGET_COUNTS, analyze, encode, make_dataset, report, validate


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template = make_dataset()
        cls.expected = json.loads(Path(__file__).with_name("expected.json").read_text(encoding="utf-8"))

    def setUp(self):
        self.data = copy.deepcopy(self.template)

    def row(self, aid="svc-comercial-pedidos", cid="CHG-001"):
        return next(r for r in analyze(self.data, cid)["consumers"] if r["consumer"] == aid)

    def ev(self, eid):
        return next(e for e in self.data["evidence"] if e["id"] == eid)

    def remove_ev(self, eid):
        self.data["evidence"] = [e for e in self.data["evidence"] if e["id"] != eid]
        for r in self.data["relations"]:
            r["evidence_ids"] = [x for x in r["evidence_ids"] if x != eid]

    def edge(self, rid, src, dst, kind="CALLS"):
        ev = copy.deepcopy(self.ev("ev:rel-order-customer"))
        ev.update(id="ev:" + rid, subject=src, target=dst)
        self.data["evidence"].append(ev)
        self.data["relations"].append({"id": rid, "source": src, "target": dst,
                                        "kind": kind, "evidence_ids": [ev["id"]]})

    def test_asset_counts(self):
        self.assertEqual(Counter(a["kind"] for a in self.data["assets"]), TARGET_COUNTS)
        self.assertEqual(len(self.data["assets"]), 240)

    def test_relation_count(self):
        self.assertEqual(len(self.data["relations"]), 512)

    def test_reproducible(self):
        self.assertEqual(encode(self.data), encode(make_dataset()))

    def check_golden(self, cid):
        result = analyze(self.data, cid)
        got = {r["consumer"]: [r["impact"], r["activity"]] for r in result["consumers"]}
        self.assertEqual(got, self.expected[cid])
        self.assertEqual(result["counts"]["consumers"], len(got))
        self.assertFalse(result["truncated"])

    def test_golden_chg001(self): self.check_golden("CHG-001")
    def test_golden_chg002(self): self.check_golden("CHG-002")
    def test_golden_chg003(self): self.check_golden("CHG-003")

    def test_complete_agent_path(self):
        self.assertEqual(self.row("agent-atendimento")["paths"],
                         [["rel:USES_TOOL:agent-atendimento:tool-atendimento", "rel-tool-customer"]])

    def test_internal_tool_not_consumer_count(self):
        self.assertNotIn("tool-atendimento", [r["consumer"] for r in analyze(self.data, "CHG-001")["consumers"]])

    def test_non_agent_consumers(self):
        self.assertEqual(len(self.expected["CHG-001"]), 4)
        self.assertIn("app-atendimento-portal", self.expected["CHG-001"])

    def test_remove_contract_changes_answer(self):
        self.remove_ev("contract:rel-order-customer")
        self.assertEqual(self.row()["impact"], "POSSIBLE")

    def test_remove_runtime_keeps_contract(self):
        self.remove_ev("obs:rel-order-customer")
        self.assertEqual(self.row()["impact"], "INCOMPATIBILITY")
        self.assertEqual(self.row()["activity"], "NOT_OBSERVED")

    def test_no_coverage_is_unknown(self):
        self.remove_ev("obs:rel-order-customer")
        self.data["coverage"] = []
        self.assertEqual(self.row()["activity"], "UNKNOWN")

    def test_partial_coverage_positive_evidence(self):
        for c in self.data["coverage"]:
            c["status"] = "partial"
        self.assertEqual(self.row()["activity"], "OBSERVED")

    def test_uncorrelated_agent_path_not_observed(self):
        self.ev("obs:agent-tool")["details"]["trace_id"] = "different-trace"
        self.assertEqual(self.row("agent-atendimento")["activity"], "UNKNOWN")

    def test_old_contract_version_not_used(self):
        self.ev("contract:rel-order-customer")["target_version"] = "0.9"
        self.assertEqual(self.row()["impact"], "POSSIBLE")

    def test_stale_contract_not_used(self):
        self.ev("contract:rel-order-customer")["collected_at"] = "2026-10-01T12:00:00Z"
        self.assertEqual(self.row()["impact"], "POSSIBLE")

    def test_expired_contract_not_used(self):
        self.ev("contract:rel-order-customer")["valid_until"] = CLOCK
        self.assertEqual(self.row()["impact"], "POSSIBLE")

    def test_future_validity_not_used(self):
        self.ev("contract:rel-order-customer")["valid_from"] = "2026-10-14T00:00:00Z"
        self.assertEqual(self.row()["impact"], "POSSIBLE")

    def test_wrong_environment_evidence_not_used(self):
        self.ev("contract:rel-order-customer")["environment"] = "qa-demo"
        self.assertEqual(self.row()["impact"], "POSSIBLE")

    def test_required_fields_are_change_specific(self):
        self.data["changes"][0]["field"] = "nome"
        self.assertEqual(self.row()["impact"], "NO_INCOMPATIBILITY")
        self.assertEqual(self.row("app-atendimento-portal")["impact"], "INCOMPATIBILITY")

    def test_partial_contract_does_not_prove_negative(self):
        self.ev("contract:rel-portal-customer")["details"]["exhaustive"] = False
        self.assertEqual(self.row("app-atendimento-portal")["impact"], "POSSIBLE")

    def test_current_contract_conflict(self):
        ev = copy.deepcopy(self.ev("contract:rel-order-customer"))
        ev["id"] = "conflicting-contract"
        ev["details"]["required_fields"] = ["nome"]
        self.data["evidence"].append(ev)
        self.assertEqual(self.row()["impact"], "INCONCLUSIVE")
        self.assertTrue(self.row()["contract_conflict"])

    def test_duplicate_origin_does_not_multiply_origins(self):
        before = self.row()["origin_ids"]
        ev = copy.deepcopy(self.ev("contract:rel-order-customer"))
        ev["id"] = "copy-contract"
        self.data["evidence"].append(ev)
        self.assertEqual(self.row()["origin_ids"], before)

    def test_deduplicate_two_paths(self):
        self.edge("direct-agent", "agent-atendimento", "api-clientes-v2")
        result = analyze(self.data, "CHG-001")
        self.assertEqual(result["counts"]["consumers"], 4)
        self.assertEqual(len(self.row("agent-atendimento")["paths"]), 2)

    def test_cycle_terminates(self):
        self.edge("cycle-in", "svc-atendimento-chamados", "svc-comercial-pedidos")
        self.edge("cycle-out", "svc-comercial-pedidos", "svc-atendimento-chamados")
        result = analyze(self.data, "CHG-001")
        self.assertFalse(result["truncated"])
        self.assertEqual(result["counts"]["consumers"], 5)

    def test_depth_limit_visible(self):
        self.data["changes"][0]["max_depth"] = 1
        self.assertTrue(analyze(self.data, "CHG-001")["truncated"])

    def test_path_limit_visible(self):
        self.data["changes"][0]["max_paths"] = 1
        self.assertTrue(analyze(self.data, "CHG-001")["truncated"])

    def test_unknown_change_rejected(self):
        with self.assertRaises(ValueError): analyze(self.data, "CHG-999")

    def test_empty_result_not_safe(self):
        self.data["changes"][0].update(target="api-clientes-qa", environment="qa-demo")
        result = analyze(self.data, "CHG-001")
        self.assertEqual(result["counts"]["consumers"], 0)
        self.assertFalse(result["scope_complete"])

    def test_orphan_asset_rejected(self):
        self.data["relations"][0]["target"] = "missing"
        with self.assertRaises(ValueError): validate(self.data)

    def test_orphan_evidence_rejected(self):
        self.data["relations"][0]["evidence_ids"].append("missing")
        with self.assertRaises(ValueError): validate(self.data)

    def test_duplicate_asset_rejected(self):
        self.data["assets"].append(copy.deepcopy(self.data["assets"][0]))
        with self.assertRaises(ValueError): validate(self.data)

    def test_cross_environment_relation_rejected(self):
        self.edge("cross-env", "agent-atendimento", "api-clientes-qa")
        with self.assertRaises(ValueError): validate(self.data)

    def test_future_collection_rejected(self):
        self.data["evidence"][0]["collected_at"] = "2027-01-01T00:00:00Z"
        with self.assertRaises(ValueError): validate(self.data)

    def test_unknown_family_rejected(self):
        self.data["evidence"][0]["family"] = "made_up"
        with self.assertRaises(ValueError): validate(self.data)

    def test_structure_cannot_be_observed_use(self):
        self.data["evidence"][0].update(family="runtime", source="src-runtime", claim="observed_use",
                                       details={"at": CLOCK, "trace_id": "x"}, collected_at=CLOCK)
        with self.assertRaises(ValueError): validate(self.data)

    def test_no_iam_or_field_access_claim(self):
        for r in analyze(self.data, "CHG-001")["consumers"]:
            self.assertEqual(r["authorization"], "NOT_EVALUATED")
            self.assertEqual(r["field_access"], "NOT_EVALUATED")

    def test_lineage_not_reversed_as_consumer_calls(self):
        result = analyze(self.data, "CHG-002")
        self.assertNotIn("job-dados-previsao", [r["consumer"] for r in result["consumers"]])

    def test_monthly_job_no_safety_claim(self):
        row = self.row("job-financeiro-cobranca", "CHG-003")
        self.assertEqual(row["activity"], "UNKNOWN")
        self.assertTrue(any("rotinas esporádicas" in x for x in row["limitations"]))

    def test_fresh_unavailable_supersedes_old_coverage(self):
        self.remove_ev("obs:rel-order-customer")
        old = next(c for c in self.data["coverage"] if c["relation"] == "rel-order-customer")
        old["collected_at"] = "2026-10-13T11:00:00Z"
        old["end"] = "2026-10-13T11:00:00Z"
        new = dict(old, status="unavailable", collected_at=CLOCK, end=CLOCK)
        self.data["coverage"].append(new)
        self.assertEqual(self.row()["activity"], "UNKNOWN")

    def test_bad_change_version_rejected(self):
        self.data["changes"][0]["before_version"] = "0.1"
        with self.assertRaises(ValueError): analyze(self.data, "CHG-001")

    def test_bad_operation_rejected(self):
        self.data["changes"][0]["operation"] = "execute_deployment"
        with self.assertRaises(ValueError): analyze(self.data, "CHG-001")

    def test_markdown_matches_result(self):
        result = analyze(self.data, "CHG-001")
        text = report(result)
        self.assertIn("**4**", text)
        self.assertIn("Dados fictícios", text)
        self.assertIn("cliente_id", text)
        for row in result["consumers"]:
            self.assertIn(row["consumer"], text)
            self.assertIn(row["owner"], text)
            for eid in row["evidence_ids"]: self.assertIn(eid, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)

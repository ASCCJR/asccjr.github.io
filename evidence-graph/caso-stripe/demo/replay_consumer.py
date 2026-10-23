"""Replay the owned synthetic examples; no network or contract revalidation."""
import json
from pathlib import Path
from consumer_demo import execute_cases, summarize

folder = Path(__file__).resolve().parent
fixtures = json.loads((folder / "consumer_demo_cases.json").read_text())
assert fixtures["synthetic"] is True
runs = execute_cases(fixtures["cases"])
recorded = json.loads((folder / "result.json").read_text())["runs"]
if runs != recorded:
    raise SystemExit("Observed output differs from the preserved record; review the code and fixtures.")
print(json.dumps({"synthetic": True, "matches_preserved_record": True,
                  "execution_records": len(runs), "summary": summarize(runs)}, indent=2))

"""Frozen L6-A candidates: consumes evidence only, never oracle code or truth.json.

These experimental rules are NOT changes to the M3/L5 product analyzer.
R field reads are a deliberately limited heuristic, not proof of failure.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from datetime import datetime
import itertools
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'lab-runtime'))
from auth_policy import evaluate

QUESTIONS = ('breaks_when_response_available', 'used_in_baseline_window', 'can_access_endpoint')
MODES = tuple(''.join(x) for n in (1, 2, 3) for x in itertools.combinations('CRA', n))
UNKNOWN = 'UNKNOWN'


def instant(s: str) -> datetime:
    dt = datetime.fromisoformat(s.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('Expected timezone')
    return dt


def active(record: dict, context: dict) -> bool:
    try:
        return (record['environment'] == context['environment']
                and record['resource'] == context['resource']
                and record['version'] == context['version']
                and instant(record['valid_from']) <= instant(context['at']) < instant(record['valid_until']))
    except (KeyError, ValueError, TypeError):
        return False


def valid_runtime(records: list[dict], subject: str, ctx: dict) -> list[dict]:
    """Require correlated client/server; duplicates don't create extra support.

Conflicting duplicates are rejected, not arbitrarily selected. No negative from silence.
"""
    unique = {}; ambiguous = set()
    for s in records:
        key = (s['trace_id'], s['span_id'])
        if key in unique and unique[key] != s:
            ambiguous.add(key)
        else:
            unique[key] = s
    spans = [s for key, s in unique.items() if key not in ambiguous]
    good = []
    for c in spans:
        a = c['attributes']
        if (c['kind'] != 'CLIENT' or a.get('eval.subject') != subject
                or a.get('eval.phase') != 'baseline' or a.get('eval.environment') != ctx['environment']
                or a.get('eval.resource') != ctx['resource'] or a.get('eval.version') != ctx['version']
                or a.get('http.response.status_code') != 200):
            continue
        if not (ctx['window_start_ns'] <= c['start_ns'] <= c['end_ns'] <= ctx['window_end_ns']):
            continue
        for s in spans:
            b = s['attributes']
            if (s['kind'] == 'SERVER' and s['trace_id'] == c['trace_id']
                    and s['parent_span_id'] == c['span_id']
                    and c['start_ns'] <= s['start_ns'] <= s['end_ns'] <= c['end_ns']
                    and b.get('eval.subject') == subject and b.get('eval.authenticated') is True
                    and b.get('eval.phase') == 'baseline' and b.get('eval.environment') == ctx['environment']
                    and b.get('eval.resource') == ctx['resource'] and b.get('eval.version') == ctx['version']
                    and b.get('http.response.status_code') == 200):
                good.append(c)
                break
    return good


def predict(evidence: dict, mode: str) -> dict:
    if mode not in MODES or evidence.get('schema') != 'l6-evidence-1':
        raise ValueError('Unsupported mode or evidence')
    if set(evidence) != {'schema', 'context', 'subjects', 'change', 'C', 'R', 'A'}:
        raise ValueError('Unexpected input key (truth/labels are forbidden)')
    ctx = evidence['context']; removed = set(evidence['change']['removed_fields'])
    result = {}
    for subject in evidence['subjects']:
        canswer = UNKNOWN; ranswer = UNKNOWN; reasons = []
        # All arms receive the same proposed producer diff. C = consumer declarations.
        declaration = evidence['C'].get(subject) if 'C' in mode else None
        if declaration is not None and active(declaration, ctx):
            req = declaration.get('required_fields')
            if (declaration.get('complete') is True and isinstance(req, list)
                    and all(isinstance(k, str) for k in req)):
                canswer = 'YES' if set(req) & removed else 'NO'
                reasons.append('consumer_manifest:' + canswer)
        runtime = valid_runtime(evidence['R'], subject, ctx) if 'R' in mode else []
        if any(set(s['attributes'].get('eval.indexed_fields', [])) & removed for s in runtime):
            ranswer = 'YES'
            reasons.append('indexed_field_seen_before_change:heuristic')
        # Optional read or absent field is NOT a negative: other branches may exist.
        votes = {v for v in (canswer, ranswer) if v != UNKNOWN}
        impact = UNKNOWN if len(votes) != 1 else next(iter(votes))
        if len(votes) > 1:
            reasons.append('conflicting_sources:abstain')
        access = UNKNOWN
        if 'A' in mode:
            d = evaluate(evidence['A'].get(subject), subject, ctx['action'], ctx['resource'],
                         ctx['environment'], ctx['at'])
            access = {'ALLOW': 'YES', 'DENY': 'NO', 'INDETERMINATE': UNKNOWN}[d['decision']]
        result[subject] = {
            'breaks_when_response_available': impact,
            'used_in_baseline_window': 'YES' if runtime else UNKNOWN,
            'can_access_endpoint': access,
            'reasons': reasons,
        }
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--evidence', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    # The predictor receives only this path. It never opens reference/consumer files.
    value = json.loads(args.evidence.read_text(encoding='utf-8'))
    predictions = {m: predict(value, m) for m in MODES}
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(predictions, f, ensure_ascii=False, indent=2)
        f.write('\n')

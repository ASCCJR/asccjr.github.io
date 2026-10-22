"""L6-B: separate observations, declared risk, source inference and confirmation.

S is additional bounded source evidence. Removing S loses exception answers;
this is not attributed to better fusion at equal information. No truth/test results.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from predict_sources import predict, active, valid_runtime
from bounded_static import analyze, source_hash


def refine(evidence: dict, sources: dict, use_source: bool = True) -> dict:
    base = predict(evidence, 'CRA')
    ctx = evidence['context']; removed = set(evidence['change']['removed_fields'])
    rows = {}
    for subject in evidence['subjects']:
        declaration = evidence['C'].get(subject)
        required = None
        if declaration and active(declaration, ctx) and declaration.get('complete') is True:
            required = declaration.get('required_fields')
        declared = 'UNKNOWN' if required is None else 'YES' if removed & set(required) else 'NO'
        runtime = valid_runtime(evidence['R'], subject, ctx)
        fields = set()
        for span in runtime:
            for kind in ('eval.indexed_fields', 'eval.optional_fields'):
                fields.update(span['attributes'].get(kind, []))
        observed = 'YES' if fields & removed else 'UNKNOWN'
        assessment = {'answer': 'UNKNOWN', 'basis': 'source_unavailable', 'field_references': []}
        snapshot = sources.get(subject) if use_source else None
        if snapshot and active(snapshot, ctx):
            if source_hash(snapshot.get('source', '')) == snapshot.get('source_sha256'):
                if set(snapshot['before']['properties']) - set(snapshot['after']['properties']) != removed:
                    assessment['basis'] = 'source_change_mismatch'
                else:
                    assessment = analyze(snapshot['source'], snapshot['before'], snapshot['after'])
            else:
                assessment['basis'] = 'source_hash_mismatch'
        elif snapshot:
            assessment['basis'] = 'source_outside_scope_or_validity'
        answer = assessment['answer']
        conflict = declared != 'UNKNOWN' and answer != 'UNKNOWN' and declared != answer
        rows[subject] = {
            'declared_requirement': declared,
            'observed_field_access': observed,
            'potential_impact': 'YES' if 'YES' in (declared, observed) or answer == 'YES' else 'UNKNOWN',
            'predicted_exception': answer,
            'prediction_basis': assessment,
            'declaration_source_disagreement': conflict,
            'failure_confirmed_by_execution': 'NOT_TESTED',
            'semantic_correctness': 'UNKNOWN',
            'used_in_baseline_window': base[subject]['used_in_baseline_window'],
            'can_access_endpoint': base[subject]['can_access_endpoint'],
        }
    return rows


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--evidence', type=Path, required=True)
    p.add_argument('--sources', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    evidence = json.loads(args.evidence.read_text())
    sources = json.loads(args.sources.read_text())
    with args.out.open('x', encoding='utf-8') as f:
        json.dump({'without_S': refine(evidence, sources, False), 'with_S': refine(evidence, sources)}, f, ensure_ascii=False, indent=2)
        f.write('\n')

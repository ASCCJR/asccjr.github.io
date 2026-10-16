"""Counts before percentages; abstentions never disappear from the denominator."""
VALID = {'YES', 'NO', 'UNKNOWN'}


def divide(a, b):
    return a / b if b else None


def score(truth: list[str], predicted: list[str]) -> dict:
    if len(truth) != len(predicted) or any(v not in VALID for v in truth + predicted):
        raise ValueError('Aligned tri-state labels required')
    counts = {k: 0 for k in ('tp', 'tn', 'fp', 'fn', 'abstain_positive', 'abstain_negative',
                              'unknown_reference', 'asserted_on_unknown_reference')}
    for t, p in zip(truth, predicted):
        if t == 'UNKNOWN':
            counts['unknown_reference'] += 1
            counts['asserted_on_unknown_reference'] += p != 'UNKNOWN'
        elif p == 'UNKNOWN':
            counts['abstain_positive' if t == 'YES' else 'abstain_negative'] += 1
        else:
            counts[{('YES','YES'):'tp', ('YES','NO'):'fn', ('NO','YES'):'fp', ('NO','NO'):'tn'}[t,p]] += 1
    known = len(truth) - counts['unknown_reference']
    decided = sum(counts[k] for k in ('tp','tn','fp','fn'))
    correct = counts['tp'] + counts['tn']
    counts.update(n=len(truth), known_reference=known, decided=decided, correct=correct,
        abstained=counts['abstain_positive'] + counts['abstain_negative'],
        coverage=divide(decided, known), accuracy_decided=divide(correct, decided),
        correct_over_known=divide(correct, known), precision=divide(counts['tp'], counts['tp']+counts['fp']),
        recall_decided=divide(counts['tp'], counts['tp']+counts['fn']),
        positive_recovery=divide(counts['tp'], counts['tp']+counts['fn']+counts['abstain_positive']))
    return counts

"""L5 exact-tuple local policy. Three decisions; only ALLOW permits execution.

Not an IAM implementation: no roles, inheritance, delegation or column permissions.
"""
from __future__ import annotations
from datetime import datetime
from typing import Any

SCHEMA = 'evidentgraph-local-policy-1'
ENVIRONMENT = 'loopback-auth-lab'
RESOURCE = 'aurora:api:customers'
ACTION = 'customers:read'


def instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Timezone required')
    return parsed


def evaluate(policy: Any, subject: str | None, action: str, resource: str,
             environment: str, at: str) -> dict[str, Any]:
    """Fail closed while retaining epistemic uncertainty in the analysis."""
    def answer(decision: str, reason: str, rules: list[str] | None = None) -> dict:
        return {'decision': decision, 'reason': reason, 'rule_ids': rules or []}
    if subject is None:
        return answer('INDETERMINATE', 'IDENTITY_UNRESOLVED')
    try:
        now = instant(at)
        if not isinstance(policy, dict) or policy.get('schema') != SCHEMA:
            return answer('INDETERMINATE', 'POLICY_UNAVAILABLE')
        if (policy['environment'] != environment or policy['action'] != action
                or policy['resource'] != resource):
            return answer('INDETERMINATE', 'OUTSIDE_POLICY_SCOPE')
        if not isinstance(policy['revision'], str) or not policy['revision']:
            raise ValueError('Missing revision')
        start, end = instant(policy['valid_from']), instant(policy['valid_until'])
        if not start <= now < end:
            return answer('INDETERMINATE', 'OUTSIDE_VALIDITY')
        if type(policy['complete']) is not bool or not isinstance(policy['rules'], list):
            raise ValueError('Invalid rule set')
        seen, matched = set(), []
        for rule in policy['rules']:
            if (not isinstance(rule, dict) or set(rule) != {'id', 'subject', 'effect'}
                    or any(not isinstance(v, str) or not v for v in rule.values())
                    or rule['effect'] not in {'ALLOW', 'DENY'} or rule['id'] in seen):
                raise ValueError('Invalid rule')
            seen.add(rule['id'])
            if rule['subject'] == subject:
                matched.append(rule)
        if any(r['effect'] == 'DENY' for r in matched):
            return answer('DENY', 'EXPLICIT_DENY', sorted(r['id'] for r in matched))
        # An incomplete snapshot might omit a deny. It cannot establish an allow.
        if not policy['complete']:
            return answer('INDETERMINATE', 'INCOMPLETE_POLICY')
        if matched:
            return answer('ALLOW', 'EXPLICIT_ALLOW', sorted(r['id'] for r in matched))
        return answer('DENY', 'DEFAULT_DENY')
    except (KeyError, TypeError, ValueError, AttributeError):
        return answer('INDETERMINATE', 'INVALID_POLICY')

"""Behavioral reference tasks. No imports of analyzers, manifests or predicted labels.

These are authored challenge programs, not external/held-out production clients.
"""
from collections.abc import Mapping
from typing import Any


def orders(body: Mapping, options: dict) -> str:
    return 'pedido:' + body['cliente_id'].upper()


def status(body: Mapping, options: dict) -> str:
    return 'situacao:' + body['status']


def fallback_get(body: Mapping, options: dict) -> str:
    return 'consulta:' + body.get('cliente_id', 'ANONIMO')


def fallback_exception(body: Mapping, options: dict) -> str:
    try:
        return 'consulta:' + body['cliente_id']
    except KeyError:
        return 'consulta:ANONIMO'


def conditional(body: Mapping, options: dict) -> str:
    if options.get('full'):
        return 'completo:' + body['cliente_id']
    return 'resumo:' + body['status']


def unsafe_optional(body: Mapping, options: dict) -> str:
    # An optional lookup is not necessarily safe: None has no upper method.
    return body.get('cliente_id').upper()


PROGRAMS = {
    'c01': orders, 'c02': status, 'c03': orders, 'c04': orders,
    'c05': fallback_get, 'c06': fallback_exception, 'c07': orders,
    'c08': orders, 'c09': orders, 'c10': conditional,
    'c11': unsafe_optional, 'c12': status,
}
CASES = {key: [{}] for key in PROGRAMS}
CASES['c10'] = [{'full': False}, {'full': True}]
BASELINE_OPTIONS = {key: {} for key in PROGRAMS}
BASELINE_OPTIONS['c10'] = {'full': False}
# Baseline runs intentionally do not cover the monthly client or every branch.
SCHEDULE = tuple(key for key in PROGRAMS if key != 'c03')
# The test server enforces this table directly. It does NOT call auth_policy.evaluate.
DEPLOYED_ACCESS = {key: True for key in PROGRAMS}
DEPLOYED_ACCESS.update(c08=False, c09=None)


def task_outcome(subject: str, body: Mapping[str, Any], options: dict) -> dict:
    """Exception/no exception oracle, independent of declared required_fields.

Return no business output or payload. Successful execution is not a full semantic oracle.
"""
    try:
        PROGRAMS[subject](body, options)
    except (KeyError, AttributeError, TypeError) as exc:
        return {'completed': False, 'exception': type(exc).__name__}
    return {'completed': True, 'exception': None}

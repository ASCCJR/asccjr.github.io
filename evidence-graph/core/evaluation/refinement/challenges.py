"""New authored challenge programs; expected business outcomes live separately.

Not an external holdout. Execute only these trusted laboratory fixtures.
"""

def routing(body, options):
    return 'route:' + body.get('cliente_id', 'ANONIMO')


def identifier_length(body, options):
    return len(body.get('cliente_id', ''))


def translated_error(body, options):
    try:
        return body['cliente_id']
    except KeyError:
        raise ValueError('Identifier required')


def normalize(value):
    return value.upper()


def delegated(body, options):
    return normalize(body.get('cliente_id', 'ANONIMO'))


def conditional(body, options):
    if options['full']:
        return body['cliente_id']
    return body['status']


def routing_suffix(body, options):
    return body.get('cliente_id', '000000')[-3:]


def status_upper(body, options):
    return body['status'].upper()


PROGRAMS = {'n01': routing, 'n02': routing, 'n03': identifier_length,
            'n04': translated_error, 'n05': delegated, 'n06': conditional,
            'n07': routing_suffix, 'n08': status_upper}
OPTIONS = {s: [{}] for s in PROGRAMS}
OPTIONS['n06'] = [{'full': False}, {'full': True}]

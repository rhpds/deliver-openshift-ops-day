"""Conservative, side-effect-free readiness predicates for Ops Day polling."""
from collections.abc import Mapping
import json
import re


def _map(value):
    return value if isinstance(value, Mapping) else {}


def _int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def resources(result):
    result = _map(result)
    if result.get('failed') or result.get('unreachable') or result.get('skipped'):
        return []
    items = result.get('resources')
    if not isinstance(items, list) or not all(isinstance(r, Mapping) for r in items):
        return []
    return items


def conditions(resource, expected):
    values = _map(resource.get('status')).get('conditions')
    if not isinstance(values, list):
        return False
    return all([c.get('status') for c in values if isinstance(c, Mapping)
                and c.get('type') == key] == [value]
               for key, value in expected.items())


def ops_permanent_error(result):
    """Stop retries on clear authorization/validation errors, never on 5xx/429.

    The module must still be failed: returning True from an until condition
    stops polling but does not turn that failed Ansible result into success.
    """
    result = _map(result)
    if not result.get('failed'):
        return False
    code = _int(result.get('code'), _int(result.get('status')))
    message = str(result.get('msg') or '')
    if not code and '{' in message:
        try:
            status, _ = json.JSONDecoder().raw_decode(message[message.index('{'):])
            code = _int(_map(status).get('code'))
        except (ValueError, TypeError):
            pass
    if code:
        return code in (400, 401, 403, 405, 415, 422)
    return bool(re.search(r'\b(forbidden|unauthorized|permission denied)\b', message, re.I))


def ops_data_ready(result, keys):
    items = resources(result)
    return bool(items) and all(all(_map(obj.get('data')).get(key) not in (None, '')
                                   for key in keys) for obj in items)


def ops_ready(result, kind='exists', host=''):
    items = resources(result)
    if not items:
        return False
    if kind == 'exists':
        return True
    if kind == 'deployment':
        for obj in items:
            status, spec = _map(obj.get('status')), _map(obj.get('spec'))
            desired = _int(spec.get('replicas'), 1)
            if (desired < 1 or _int(status.get('observedGeneration')) <
                    _int(_map(obj.get('metadata')).get('generation'), 1) or
                    _int(status.get('readyReplicas')) < desired or
                    _int(status.get('availableReplicas')) < desired):
                return False
        return True
    if kind == 'pods':
        return all(_map(obj.get('status')).get('phase') == 'Running'
                   and conditions(obj, {'Ready': 'True'}) for obj in items)
    if kind == 'nodes':
        for obj in items:
            if not conditions(obj, {'Ready': 'True'}):
                return False
            annotations = _map(_map(obj.get('metadata')).get('annotations'))
            current = annotations.get('machineconfiguration.openshift.io/currentConfig')
            desired = annotations.get('machineconfiguration.openshift.io/desiredConfig')
            if not current or current != desired or annotations.get(
                    'machineconfiguration.openshift.io/state') != 'Done':
                return False
        return True
    if kind == 'pool':
        for obj in items:
            status, spec = _map(obj.get('status')), _map(obj.get('spec'))
            count = _int(status.get('machineCount'))
            target = _map(spec.get('configuration')).get('name')
            if (count < 1 or not target or
                    _map(status.get('configuration')).get('name') != target or
                    _int(status.get('observedGeneration')) <
                    _int(_map(obj.get('metadata')).get('generation'), 1) or
                    _int(status.get('updatedMachineCount')) != count or
                    _int(status.get('readyMachineCount')) != count or
                    _int(status.get('unavailableMachineCount'), -1) != 0 or
                    _int(status.get('degradedMachineCount'), -1) != 0 or not
                    conditions(obj, {'Updated': 'True', 'Updating': 'False', 'Degraded': 'False'})):
                return False
        return True
    if kind == 'kubeletconfig':
        return all(_int(_map(obj.get('status')).get('observedGeneration')) >=
                   _int(_map(obj.get('metadata')).get('generation'), 1) and
                   conditions(obj, {'Success': 'True'}) for obj in items)
    if kind == 'packageserver':
        return all(conditions(obj, {'Available': 'True', 'Degraded': 'False',
                                    'Progressing': 'False'}) for obj in items)
    if kind == 'catalog':
        return all(_map(_map(obj.get('status')).get('connectionState')).get(
            'lastObservedState') == 'READY' for obj in items)
    if kind == 'route':
        for obj in items:
            if host and _map(obj.get('spec')).get('host') != host:
                return False
            ingress = _map(obj.get('status')).get('ingress') or []
            if not any(isinstance(i, Mapping) and any(
                    isinstance(c, Mapping) and c.get('type') == 'Admitted' and
                    c.get('status') == 'True' for c in (i.get('conditions') or []))
                    for i in ingress):
                return False
        return True
    raise ValueError('Unsupported Ops Day readiness kind: ' + str(kind))


class FilterModule:
    def filters(self):
        return {'ops_ready': ops_ready, 'ops_data_ready': ops_data_ready,
                'ops_permanent_error': ops_permanent_error}

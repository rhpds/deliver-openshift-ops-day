"""Readiness predicates plus real-Ansible fault injection across audited tasks."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
ROLES = ROOT / 'automation/ansible/roles'
spec = importlib.util.spec_from_file_location(
    'ops_readiness', ROOT / 'automation/ansible/plugins/filter/ops_readiness.py')
readiness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(readiness)
F = 'deliver_openshift_ops_day.automation.ops_ready'


def resources(*items):
    return {'resources': list(items)}


def healthy(kind):
    obj = {'metadata': {'name': 'other-route', 'generation': 2},
           'spec': {'replicas': 1, 'host': 'central.example.test', 'domain': 'apps.example.test',
                    'configuration': {'name': 'rendered-master-new'}},
           'status': {'observedGeneration': 2, 'readyReplicas': 1, 'availableReplicas': 1,
                      'phase': 'Ready', 'state': 'Ready', 'installedCSV': 'operator.v1',
                      'currentCSV': 'operator.v1', 'connectionState': {'lastObservedState': 'READY'},
                      'conditions': [{'type': key, 'status': value} for key, value in {
                          'Ready': 'True', 'Available': 'True', 'Degraded': 'False',
                          'Progressing': 'False', 'Updating': 'False', 'Updated': 'True',
                          'Success': 'True'}.items()],
                      'ingress': [{'conditions': [{'type': 'Admitted', 'status': 'True'}]}]},
           'data': {k: 'synthetic-data' for k in ['token', '.dockerconfigjson', 'tls.crt',
                    'tls.key', 'ca.pem', 'ca-bundle.crt', 'kubeconfig', 'BUCKET_NAME',
                    'BUCKET_HOST', 'BUCKET_PORT', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']}}
    if kind == 'Pod':
        obj['status'].update(phase='Running', containerStatuses=[{'ready': True}])
    if kind == 'IngressController':
        obj['spec']['replicas'] = 2
        obj['status']['availableReplicas'] = 2
    if kind == 'Node':
        obj['metadata']['annotations'] = {
            'machineconfiguration.openshift.io/currentConfig': 'rendered-node-new',
            'machineconfiguration.openshift.io/desiredConfig': 'rendered-node-new',
            'machineconfiguration.openshift.io/state': 'Done'}
    if kind == 'MachineConfigPool':
        obj['status'].update(configuration={'name': 'rendered-master-new'}, machineCount=3,
                             updatedMachineCount=3, readyMachineCount=3,
                             unavailableMachineCount=0, degradedMachineCount=0)
    if kind == 'ClusterServiceVersion':
        obj['status']['phase'] = 'Succeeded'
    return resources(obj)


def walk(tasks):
    for task in tasks:
        yield task
        for key in ('block', 'rescue', 'always'):
            yield from walk(task.get(key, []))


class PredicateTests(unittest.TestCase):
    def test_invalid_or_failed_results_never_pass_any_gate(self):
        for kind in ['exists', 'deployment', 'pods', 'nodes', 'pool', 'kubeletconfig',
                     'packageserver', 'catalog', 'route']:
            for result in [None, {}, {'resources': None}, {'resources': [None]},
                           resources(), {'failed': True, **healthy('Deployment')},
                           {'unreachable': True, **healthy('Deployment')},
                           {'skipped': True, **healthy('Deployment')}]:
                with self.subTest(kind=kind, result=result):
                    self.assertFalse(readiness.ops_ready(result, kind))

    def test_delayed_secret_and_configmap_data_must_be_populated(self):
        self.assertFalse(readiness.ops_data_ready(resources({}), ['tls.key']))
        self.assertFalse(readiness.ops_data_ready(resources({'data': {'tls.key': ''}}), ['tls.key']))
        self.assertFalse(readiness.ops_data_ready(resources({'data': {'tls.key': 'present'}}), ['tls.key', 'tls.crt']))
        self.assertTrue(readiness.ops_data_ready(healthy('Secret'), ['tls.key', 'tls.crt']))
        self.assertFalse(readiness.ops_data_ready({'failed': True, **healthy('Secret')}, ['tls.key']))

    def test_permanent_error_classification_preserves_transient_retries(self):
        for code in [400, 401, 403, 405, 415, 422]:
            self.assertTrue(readiness.ops_permanent_error({'failed': True, 'status': code}))
            self.assertTrue(readiness.ops_permanent_error({
                'failed': True, 'msg': 'Failed to patch object: ' + json.dumps({'code': code})}))
        for code in [404, 408, 409, 410, 429, 500, 502, 503, 504]:
            self.assertFalse(readiness.ops_permanent_error({'failed': True, 'status': code}))
        self.assertFalse(readiness.ops_permanent_error({'failed': False, 'status': 401}))
        self.assertTrue(readiness.ops_permanent_error({'failed': True, 'msg': 'Forbidden'}))
        self.assertFalse(readiness.ops_permanent_error({
            'failed': True, 'status': 500, 'msg': 'backend unauthorized during startup'}))

    def test_deployment_requires_fresh_generation_and_all_desired_replicas(self):
        for field, value in [('observedGeneration', 1), ('readyReplicas', 0),
                             ('availableReplicas', 0)]:
            result = healthy('Deployment')
            result['resources'][0]['status'][field] = value
            self.assertFalse(readiness.ops_ready(result, 'deployment'))
        self.assertTrue(readiness.ops_ready(healthy('Deployment'), 'deployment'))
        result = healthy('Deployment')
        result['resources'][0]['spec']['replicas'] = 0
        self.assertFalse(readiness.ops_ready(result, 'deployment'))

    def test_running_pods_are_not_necessarily_ready(self):
        result = healthy('Pod')
        self.assertTrue(readiness.ops_ready(result, 'pods'))
        result['resources'][0]['status']['conditions'] = []
        self.assertFalse(readiness.ops_ready(result, 'pods'))

    def test_preflight_requires_observed_generations_and_completed_configs(self):
        for kind, gate in [('MachineConfigPool', 'pool'), ('KubeletConfig', 'kubeletconfig')]:
            result = healthy(kind)
            self.assertTrue(readiness.ops_ready(result, gate))
            result['resources'][0]['status']['observedGeneration'] = 1
            self.assertFalse(readiness.ops_ready(result, gate))
        for field, value in [('unavailableMachineCount', 1), ('degradedMachineCount', 1),
                             ('updatedMachineCount', 2), ('readyMachineCount', 2)]:
            result = healthy('MachineConfigPool')
            result['resources'][0]['status'][field] = value
            self.assertFalse(readiness.ops_ready(result, 'pool'))
        result = healthy('MachineConfigPool')
        result['resources'][0]['status']['configuration']['name'] = 'old-render'
        self.assertFalse(readiness.ops_ready(result, 'pool'))

    def test_nodes_must_be_ready_and_done_with_desired_configuration(self):
        result = healthy('Node')
        self.assertTrue(readiness.ops_ready(result, 'nodes'))
        a = result['resources'][0]['metadata']['annotations']
        a['machineconfiguration.openshift.io/state'] = 'Working'
        self.assertFalse(readiness.ops_ready(result, 'nodes'))
        a['machineconfiguration.openshift.io/state'] = 'Done'
        a['machineconfiguration.openshift.io/currentConfig'] = 'old'
        self.assertFalse(readiness.ops_ready(result, 'nodes'))

    def test_catalog_and_route_require_actual_readiness_not_just_existence(self):
        self.assertTrue(readiness.ops_ready(healthy('CatalogSource'), 'catalog'))
        result = healthy('CatalogSource')
        result['resources'][0]['status']['connectionState']['lastObservedState'] = 'TRANSIENT_FAILURE'
        self.assertFalse(readiness.ops_ready(result, 'catalog'))
        self.assertTrue(readiness.ops_ready(healthy('Route'), 'route', 'central.example.test'))
        self.assertFalse(readiness.ops_ready(healthy('Route'), 'route', 'wrong.example.test'))
        result = healthy('Route')
        result['resources'][0]['status']['ingress'] = []
        self.assertFalse(readiness.ops_ready(result, 'route'))


API_STUB = '''
from ansible.module_utils.basic import AnsibleModule
from pathlib import Path
import json
m = AnsibleModule(argument_spec={
    'key': {'type': 'str'}, 'kind': {'type': 'str'},
    'config': {'type': 'path'}, 'failure': {'type': 'bool', 'default': False},
    'denied': {'type': 'bool', 'default': False},
})
c = json.loads(Path(m.params['config']).read_text())
p = Path(c['state'])
s = json.loads(p.read_text()) if p.exists() else {}
k = m.params['key']; n = s.get(k, 0); s[k] = n + 1
p.write_text(json.dumps(s))
if m.params['denied']:
    m.fail_json(msg='Forbidden', status=403)
if n == 0 or m.params['failure']:
    m.fail_json(msg='500: temporary admission webhook outage')
r = c['responses'].get(m.params['kind'], {'resources': [{'metadata': {'name': 'test'}}]})
m.exit_json(changed=False, **r)
'''


class BroadAnsibleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paths = [ROLES / role / 'tasks/workload.yml' for role in [
            'ocp4_days_workload_rhdh', 'ocp4_days_workload_ztwim', 'ocp4_days_workload_vault',
            'ocp4_workload_acm_multicluster_observability', 'ocp4_workload_prepare_hcp',
            'ocp4_workload_create_hcp_cluster', 'ocp4_workload_hcp_kubevirt',
            'ocp4_workload_openshift_gitops', 'ocp4_workload_rhacs_console_embed',
            'ocp4_workload_virtualization_boot_image_trim']]
        cls.paths += [ROLES / 'ocp4_workload_cluster_cleanup_preflight/tasks/main.yml',
                      ROLES / 'ocp4_workload_days_ops_track/tasks/workload.yml']

    def execute(self, tasks, failure=False, variables=None, allow_failure=False, denied=False):
        with tempfile.TemporaryDirectory(prefix='ops-broad-test-') as d:
            tmp = Path(d)
            (tmp / 'library').mkdir()
            (tmp / 'library/api_stub.py').write_text(API_STUB)
            collection = tmp / 'collections/ansible_collections/deliver_openshift_ops_day'
            collection.mkdir(parents=True)
            (collection / 'automation').symlink_to(ROOT / 'automation/ansible', target_is_directory=True)
            kinds = ['Deployment', 'Pod', 'Node', 'MachineConfigPool', 'KubeletConfig',
                     'ClusterOperator', 'CatalogSource', 'Route', 'IngressController',
                     'NooBaa', 'HostedCluster', 'Secret', 'ConfigMap', 'Ingress', 'Subscription', 'ClusterServiceVersion',
                     'LVMCluster', 'ArgoCD']
            config = {'state': str(tmp / 'state.json'),
                      'responses': {k: healthy(k) for k in kinds}}
            (tmp / 'config.json').write_text(json.dumps(config))
            converted, expected = [], []
            for index, production in enumerate(tasks):
                task = copy.deepcopy(production)
                module = next((k for k in ['kubernetes.core.k8s', 'kubernetes.core.k8s_info',
                                          'k8s', 'k8s_info', 'ansible.builtin.uri'] if k in task), None)
                if not module or 'until' not in task:
                    continue
                args = task[module]
                kind = args.get('kind', '')
                # Preserve actual production gates; only IO, caller-specific
                # conditions/loops, and test timing are replaced here.
                for k in ['when', 'loop', 'loop_control', 'with_items', 'with_dict',
                          'with_fileglob', 'delegate_to', 'become', module, 'ignore_errors']:
                    task.pop(k, None)
                task['retries'] = 2
                task['delay'] = 0
                key = str(index)
                expected.append(key)
                if module.endswith('uri'):
                    config['responses']['URI'] = {'status': 200}
                    kind = 'URI'
                task['api_stub'] = {'key': key, 'kind': kind,
                                    'config': str(tmp / 'config.json'), 'failure': failure, 'denied': denied}
                if failure or denied:
                    converted.append({'block': [task], 'rescue': [
                        {'ansible.builtin.debug': {'msg': 'Expected bounded failure'}}]})
                else:
                    converted.append(task)
            (tmp / 'config.json').write_text(json.dumps(config))
            variables = {'ansible_python_interpreter': sys.executable,
                         '_rhacs_central_reencrypt_host': 'central.example.test',
                         'ACTION': 'provision', 'r_kubelet_config': {'changed': False},
                         '_ops_day_shared_catalog_required': True,
                         **(variables or {})}
            (tmp / 'play.yml').write_text(yaml.safe_dump([dict(hosts='localhost', gather_facts=False,
                connection='local', vars=variables, tasks=converted)], sort_keys=False))
            env = dict(os.environ, ANSIBLE_LIBRARY=str(tmp / 'library'),
                       ANSIBLE_COLLECTIONS_PATH=str(tmp / 'collections'),
                       ANSIBLE_LOCAL_TEMP=str(tmp / 'local'), ANSIBLE_REMOTE_TEMP=str(tmp / 'remote'),
                       ANSIBLE_NOCOLOR='1')
            r = subprocess.run([sys.executable, '-m', 'ansible.cli.playbook', '-i', 'localhost,',
                                str(tmp / 'play.yml')], cwd=tmp, env=env,
                               capture_output=True, text=True, timeout=180)
            output = r.stdout + r.stderr
            if not allow_failure:
                self.assertEqual(r.returncode, 0, output)
            self.assertNotIn('Error while evaluating conditional', output)
            state = json.loads((tmp / 'state.json').read_text())
            self.assertEqual(set(state), set(expected), output)
            self.assertTrue(all(n == (1 if denied else 3 if failure else 2) for n in state.values()), output)
            return state

    def candidates(self):
        result = []
        for path in self.paths:
            for task in walk(yaml.safe_load(path.read_text())):
                if ('until' in task and not task.get('ignore_errors') and
                        not task.get('name', '').startswith(('DEBUG', 'DIAG'))):
                    result.append(task)
        return result

    def test_audited_api_gates_recover_after_a_transient_failure(self):
        state = self.execute(self.candidates())
        self.assertGreater(len(state), 75)

    def test_persistent_api_failures_exhaust_finite_retry_budgets(self):
        state = self.execute(self.candidates(), failure=True)
        self.assertGreater(len(state), 75)

    def test_authorization_failures_remain_fatal_without_retrying(self):
        state = self.execute(self.candidates(), denied=True)
        self.assertGreater(len(state), 75)

    def test_preflight_final_gates_do_not_depend_on_apply_changed_flag(self):
        path = ROLES / 'ocp4_workload_cluster_cleanup_preflight/tasks/main.yml'
        tasks = yaml.safe_load(path.read_text())
        gates = [t for t in tasks if t['name'] in [
            'Wait for MachineConfigPool master to finish rolling update',
            'Wait for nodes to finish configuration and return Ready',
            'Wait for OLM packageserver to recover after MCP rollout']]
        for task in gates:
            self.assertEqual(task['when'], 'ACTION == "provision"')
            self.assertNotIn('ignore_errors', task)
        self.assertEqual(len(self.execute(gates)), 3)

    def test_resource_payload_contracts_are_preserved(self):
        contracts = json.loads((ROOT / 'tests/fixtures/ops_resource_contracts.json').read_text())
        for contract in contracts:
            with self.subTest(path=contract['path'], name=contract['name']):
                tasks = [t for t in walk(yaml.safe_load((ROOT / contract['path']).read_text()))
                         if t.get('name') == contract['name']]
                task = tasks[contract['occurrence']]
                key = next(k for k in task if k.split('.')[-1] == contract['module'])
                args = copy.deepcopy(task[key])
                if contract['name'] in ['Wait for Showroom deployment to exist',
                                        'Wait for Showroom deployment to roll out after patching',
                                        'Extract master_url from console route (fallback)']:
                    args.pop('api_version', None)  # Intentional discovery correction.
                digest = hashlib.sha256(json.dumps(args, sort_keys=True).encode()).hexdigest()
                self.assertEqual(digest, contract['sha256'])

    def local_play(self, tasks, variables=None, role_payload=None):
        with tempfile.TemporaryDirectory(prefix='ops-control-test-') as d:
            tmp = Path(d)
            if role_payload is not None:
                directory = tmp / 'roles/control_test/tasks'
                directory.mkdir(parents=True)
                (directory / 'main.yml').write_text(yaml.safe_dump(role_payload, sort_keys=False))
            (tmp / 'play.yml').write_text(yaml.safe_dump([dict(hosts='localhost', gather_facts=False,
                connection='local', vars=variables or {}, tasks=tasks)], sort_keys=False))
            env = dict(os.environ, ANSIBLE_ROLES_PATH=str(tmp / 'roles'),
                       ANSIBLE_LOCAL_TEMP=str(tmp / 'local'), ANSIBLE_REMOTE_TEMP=str(tmp / 'remote'))
            r = subprocess.run([sys.executable, '-m', 'ansible.cli.playbook', '-i', 'localhost,',
                                str(tmp / 'play.yml')], cwd=tmp, env=env,
                               capture_output=True, text=True, timeout=30)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            return r.stdout + r.stderr

    def test_skipping_configured_roles_never_ends_subsequent_host_work(self):
        for role, variables in [
            ('ocp4_workload_rhacs_console_embed', {'r_central_cr': resources({
                'spec': {'central': {'exposure': {'route': {'reencrypt': {'enabled': True}}}}}})}),
            ('ocp4_workload_virtualization_boot_image_trim', {
                'ocp4_workload_virtualization_boot_image_trim_disabled_images': []}),
        ]:
            with self.subTest(role=role):
                skip = next(t for t in yaml.safe_load((ROLES / role / 'tasks/workload.yml').read_text())
                            if t.get('ansible.builtin.meta') == 'end_role')
                output = self.local_play([
                    {'ansible.builtin.include_role': {'name': 'control_test'}},
                    {'ansible.builtin.debug': {'msg': 'AFTER_ROLE_REACHED'}},
                ], variables, [skip, {'ansible.builtin.fail': {'msg': 'role should have ended'}}])
                self.assertIn('AFTER_ROLE_REACHED', output)

    def test_boot_image_override_generation_is_idempotent_across_role_reruns(self):
        tasks = yaml.safe_load((ROLES / 'ocp4_workload_virtualization_boot_image_trim/tasks/workload.yml').read_text())
        build = [t for t in tasks if t['name'] in [
            'Reset boot image overrides for this invocation',
            'Build disabled boot image DataImportCron overrides']]
        self.local_play(build + build + [{'ansible.builtin.assert': {'that': [
            '_ocp4_workload_virtualization_boot_image_trim_overrides | length == 2']}}],
            {'ocp4_workload_virtualization_boot_image_trim_disabled_images': ['image-one', 'image-two']})

    def test_rhdh_url_fallbacks_do_not_evaluate_when_urls_are_supplied(self):
        path = ROLES / 'ocp4_days_workload_rhdh/tasks/workload.yml'
        task = next(t for t in walk(yaml.safe_load(path.read_text())) if t.get('name') == 'Set cluster URLs')
        self.local_play([task, {'ansible.builtin.assert': {'that': [
            "_rhdh_api_url == 'https://provided-api.example.test'",
            "_rhdh_console_url == 'https://provided-console.example.test'"]}}],
            {'ocp4_days_workload_rhdh_api_url': 'https://provided-api.example.test',
             'ocp4_days_workload_rhdh_console_url': 'https://provided-console.example.test'})
        self.local_play([task, {'ansible.builtin.assert': {'that': [
            "_rhdh_api_url == 'https://fallback-api.example.test'",
            "_rhdh_console_url == 'https://central.example.test'"]}}],
            {'_ops_rhdh_api_url': {'stdout': 'https://fallback-api.example.test'},
             '_ops_rhdh_console_route': healthy('Route')})

    def test_shared_catalog_is_required_only_for_enabled_snapshot_consumers(self):
        path = ROLES / 'ocp4_workload_days_ops_track/tasks/workload.yml'
        task = next(t for t in yaml.safe_load(path.read_text())
                    if t.get('name') == 'Determine whether enabled workloads require the shared snapshot catalog')
        off = {k: False for k in ['module_enable_gitops', 'module_enable_acm', 'module_enable_devhub',
                                  'module_enable_security', 'module_enable_ztwim', 'module_enable_ols',
                                  'ocp4_workload_web_terminal_use_catalog_snapshot']}
        snapshot_flags = {k: True for k in [
            'ocp4_workload_openshift_gitops_use_catalog_snapshot',
            'ocp4_workload_metallb_use_catalog_snapshot', 'ocp4_days_workload_rhdh_use_catalog_snapshot',
            'ocp4_days_workload_ztwim_use_catalog_snapshot', 'ocp5_workload_ols_use_catalog_snapshot']}
        for extra, expected in [({}, False), ({'module_enable_acm': True}, True),
                                ({'module_enable_devhub': True}, True),
                                ({'ops_day_shared_catalog_required': True}, True),
                                ({'module_enable_acm': True, 'ops_day_shared_catalog_required': False}, False)]:
            with self.subTest(extra=extra):
                self.local_play([task, {'ansible.builtin.assert': {'that': [
                    '_ops_day_shared_catalog_required == expected']}}],
                    {**off, **snapshot_flags, **extra, 'expected': expected})

    def test_local_installer_grace_preserves_names_and_rejects_unrelated_errors(self):
        # Reuse the real include_role/rescue harness, including the upstream
        # task action/name/register shape. The collection filter is loaded as
        # it will be from a built/installed collection.
        from test_operator_resilience import OperatorResilienceTests, subscription, csv
        OperatorResilienceTests.setUpClass()
        harness = OperatorResilienceTests('test_default_budgets_and_no_suppressed_readiness_failures')
        tasks = yaml.safe_load((ROLES / 'ocp4_workload_operator_install/tasks/main.yml').read_text())
        variables = {'install_operator_name': 'rhdh', 'install_operator_namespace': 'rhdh-operator',
                     'ops_day_readiness_retries': 2, 'ops_day_retry_delay': 0}
        upstream = {'name': 'Wait until CSV is installed ({{ install_operator_name }})',
                    'kubernetes.core.k8s_info': {'kind': 'ClusterServiceVersion'}, 'register': 'r_csv'}
        state, _ = harness.run_tasks(tasks, {
            'ClusterServiceVersion': [{'failed': True, 'msg': 'CSV timeout'}, csv()],
            'Subscription': [subscription()]}, extra_vars=variables, upstream_task=upstream)
        self.assertEqual(state['counts']['ClusterServiceVersion'], 2)
        self.assertTrue(any(c['kind'] == 'Subscription' and c['name'] == 'rhdh'
                            for c in state['calls']))
        for name, message, code in [('Create subscription', 'invalid channel', 0),
                                    ('Wait until CSV is installed', 'Forbidden', 403)]:
            failing = copy.deepcopy(upstream)
            failing['name'] = name
            state, _ = harness.run_tasks(tasks, {'ClusterServiceVersion': [
                {'failed': True, 'msg': message, 'status': code}]}, False,
                extra_vars=variables, upstream_task=failing)
            self.assertNotIn('Subscription', state['counts'])

    def test_required_ztwim_gate_cannot_silently_report_success(self):
        path = ROLES / 'ocp4_days_workload_ztwim/tasks/workload.yml'
        task = next(t for t in yaml.safe_load(path.read_text())
                    if t['name'] == 'Wait for ZTWIM operator deployment to be ready')
        self.assertNotIn('ignore_errors', task)
        self.assertIn("ops_ready('deployment')", task['until'])


if __name__ == '__main__':
    unittest.main()

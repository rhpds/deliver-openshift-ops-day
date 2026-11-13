"""Offline execution of production virtctl route/proxy fallback and archive checks."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[2]
ROLE = ROOT / 'automation/ansible/roles/ocp4_workload_openshift_virtualization'
PREFIX = 'ocp4_workload_openshift_virtualization_'
TOKEN = 'synthetic-credential-for-offline-test'
ROUTE = 'https://cli-download.apps.example.test/amd64/linux/virtctl.tar.gz'
API = 'https://api.example.test:6443'

DOWNLOAD_STUB = '''
from ansible.module_utils.basic import AnsibleModule
from pathlib import Path
import io, json, tarfile
module = AnsibleModule(argument_spec={
    'url': {'type': 'str'}, 'dest': {'type': 'path'}, 'mode': {'type': 'str'},
    'validate_certs': {'type': 'bool'}, 'force': {'type': 'bool'},
    'timeout': {'type': 'int'}, 'headers': {'type': 'dict', 'default': {}},
    'unredirected_headers': {'type': 'list', 'default': []},
    'test_config': {'type': 'path'},
})
config = json.loads(Path(module.params['test_config']).read_text())
url = module.params['url']
path = 'proxy' if '/api/v1/' in url else 'route'
with Path(config['requests']).open('a') as output:
    output.write(json.dumps({'path': path, 'url': url,
        'headers': module.params['headers'],
        'unredirected_headers': module.params['unredirected_headers']}) + '\\n')
behavior = config[path]
if isinstance(behavior, list):
    calls = [json.loads(x) for x in Path(config['requests']).read_text().splitlines()]
    attempt = sum(1 for r in calls if r['path'] == path) - 1
    behavior = behavior[min(attempt, len(behavior) - 1)]
if behavior == 'refused':
    module.fail_json(msg='Connection refused')
if behavior == 'corrupt':
    Path(module.params['dest']).write_bytes(b'not a gzip archive')
else:
    with tarfile.open(module.params['dest'], 'w:gz') as archive:
        data = b'offline executable placeholder'
        entry = tarfile.TarInfo('virtctl' if behavior == 'valid' else 'unexpected-file')
        entry.size = len(data)
        archive.addfile(entry, io.BytesIO(data))
module.exit_json(changed=True)
'''

API_STUB = '''
from ansible.module_utils.basic import AnsibleModule
from pathlib import Path
import json
module = AnsibleModule(argument_spec={
    'api_version': {'type': 'str'}, 'kind': {'type': 'str'},
    'name': {'type': 'str'}, 'namespace': {'type': 'str'},
    'test_config': {'type': 'path'}, 'label_selectors': {'type': 'list'},
})
config = json.loads(Path(module.params['test_config']).read_text())
requests_file = Path(config['api_requests'])
previous = [json.loads(x) for x in requests_file.read_text().splitlines()] if requests_file.exists() else []
attempt = sum(1 for r in previous if r['kind'] == module.params['kind'])
with requests_file.open('a') as output:
    output.write(json.dumps({'kind': module.params['kind'],
                             'name': module.params['name']}) + '\\n')
if module.params['kind'] == 'Route':
    resources = config['routes']
elif module.params['kind'] == 'EndpointSlice':
    if module.params['label_selectors'] != ['kubernetes.io/service-name=cli-download']:
        module.fail_json(msg='EndpointSlice selector must match the actual Service')
    resources = [{'endpoints': [{'conditions': {'ready': True}, 'addresses': ['192.0.2.1']}]}]
else:
    resources = [{'metadata': {'name': 'cli-download'}, 'spec': {
        'ports': [{'name': 'http', 'port': 80, 'targetPort': 8080}]}}]
sequence = config.get('api_sequences', {}).get(module.params['kind'])
if sequence:
    result = sequence[min(attempt, len(sequence) - 1)]
    if result.get('failed'):
        module.fail_json(**{k: v for k, v in result.items() if k != 'failed'})
    resources = result.get('resources', [])
# Unlike the old stub, model real name/namespace lookup semantics. Returning a
# Route for ANY requested name hid the generated-hostname bug in job 92239.
if module.params['name']:
    resources = [r for r in resources if r.get('metadata', {}).get('name') == module.params['name']]
if module.params['namespace'] != 'openshift-cnv':
    resources = []
module.exit_json(changed=False, resources=resources)
'''


class VirtctlDownloadTests(unittest.TestCase):
    def run_download(self, route, proxy, success, expected_paths, credentials=True,
                     target_port='http', route_url=ROUTE, routes=None, api_sequences=None):
        with tempfile.TemporaryDirectory(prefix='virtctl-download-test-') as directory:
            tmp = Path(directory)
            library = tmp / 'library'
            library.mkdir()
            (library / 'fake_download.py').write_text(DOWNLOAD_STUB)
            (library / 'fake_k8s_info.py').write_text(API_STUB)
            if routes is None:
                routes = [{'metadata': {'name': 'cli-download'}, 'spec': {
                    'host': urlsplit(route_url).hostname,
                    'to': {'name': 'cli-download'}, 'port': {'targetPort': target_port}}}]
            config = dict(route=route, proxy=proxy, requests=str(tmp / 'requests.jsonl'),
                          routes=routes, api_requests=str(tmp / 'api_requests.jsonl'),
                          api_sequences=api_sequences or {})
            (tmp / 'config.json').write_text(json.dumps(config))
            # Replace network IO only; keep production retries, rescue, delegation,
            # secret suppression, URL/port resolution, and real tar validation.
            tasks = yaml.safe_load((ROLE / 'tasks/download_virtctl.yml').read_text())

            def replace_network(value):
                if isinstance(value, list):
                    return [replace_network(item) for item in value]
                if not isinstance(value, dict):
                    return value
                result = {key: replace_network(item) for key, item in value.items()}
                if 'ansible.builtin.get_url' in result:
                    result['fake_download'] = result.pop('ansible.builtin.get_url')
                    result['fake_download']['test_config'] = str(tmp / 'config.json')
                if 'kubernetes.core.k8s_info' in result:
                    result['fake_k8s_info'] = result.pop('kubernetes.core.k8s_info')
                    result['fake_k8s_info']['test_config'] = str(tmp / 'config.json')
                return result

            tasks = replace_network(tasks)
            text = yaml.safe_dump(tasks, sort_keys=False).replace('/tmp/virtctl.tar.gz', str(tmp / 'virtctl.tar.gz'))
            (tmp / 'download_virtctl.yml').write_text(text)
            validation = (ROLE / 'tasks/validate_virtctl_archive.yml').read_text()
            (tmp / 'validate_virtctl_archive.yml').write_text(
                validation.replace('/tmp/virtctl.tar.gz', str(tmp / 'virtctl.tar.gz')))
            variables = yaml.safe_load((ROLE / 'defaults/main.yml').read_text())
            variables.update({PREFIX + 'virtctl_download_retries': 1,
                              PREFIX + 'virtctl_download_delay': 0,
                              PREFIX + 'virtctl_backend_wait_retries': 1,
                              PREFIX + 'virtctl_backend_wait_delay': 0,
                              '_ocp4_workload_openshift_virtualization_virtctl_url': route_url,
                              'ansible_python_interpreter': sys.executable})
            if credentials:
                variables.update(openshift_api_url=API + '/', openshift_api_key=TOKEN)
            playbook = tmp / 'playbook.yml'
            playbook.write_text(yaml.safe_dump([dict(hosts='localhost', connection='local',
                gather_facts=False, vars=variables,
                tasks=[{'ansible.builtin.include_tasks': str(tmp / 'download_virtctl.yml')}])], sort_keys=False))
            inventory = tmp / 'inventory.json'
            inventory.write_text(json.dumps({'all': {'children': {'bastions': {'hosts': {
                'bastion': {'ansible_connection': 'local', 'ansible_python_interpreter': sys.executable}}}}}}))
            environment = dict(os.environ, ANSIBLE_LIBRARY=str(library),
                               ANSIBLE_LOCAL_TEMP=str(tmp / 'local'),
                               ANSIBLE_REMOTE_TEMP=str(tmp / 'remote'), ANSIBLE_NOCOLOR='1')
            result = subprocess.run([sys.executable, '-m', 'ansible.cli.playbook',
                                     '-i', str(inventory), str(playbook)], cwd=tmp,
                                    env=environment, capture_output=True, text=True, timeout=60)
            output = result.stdout + result.stderr
            self.assertEqual(result.returncode == 0, success, output)
            self.assertNotIn(TOKEN, output)
            requests = [json.loads(line) for line in (tmp / 'requests.jsonl').read_text().splitlines()]
            self.assertEqual([r['path'] for r in requests], expected_paths, output)
            if (tmp / 'api_requests.jsonl').exists():
                api_requests = [json.loads(line) for line in
                                (tmp / 'api_requests.jsonl').read_text().splitlines()]
                for request in api_requests:
                    if request['kind'] == 'Route':
                        self.assertIsNone(request['name'], 'Do not infer Route names from hostnames')
            for request in requests:
                if request['path'] == 'route':
                    self.assertEqual(request['headers'], {})
                else:
                    self.assertEqual(request['url'], API + '/api/v1/namespaces/openshift-cnv/'
                        'services/http:cli-download:80/proxy/amd64/linux/virtctl.tar.gz')
                    self.assertEqual(request['headers'], {'Authorization': 'Bearer ' + TOKEN})
                    self.assertEqual(request['unredirected_headers'], ['Authorization'])

    def test_healthy_route_needs_no_api_credentials(self):
        self.run_download('valid', 'refused', True, ['route'], credentials=False)

    def test_route_outage_uses_api_proxy(self):
        self.run_download('refused', 'valid', True, ['route', 'route', 'proxy'])

    def test_numeric_route_target_resolves_exposed_service_port(self):
        self.run_download('refused', 'valid', True, ['route', 'route', 'proxy'], target_port=8080)

    def test_unresolved_service_port_fails_without_trying_arbitrary_port(self):
        self.run_download('refused', 'valid', False, ['route', 'route'], target_port='missing')

    def test_generated_hostname_with_namespace_suffix_uses_actual_route_backend(self):
        # Exact hostname shape from job 92239: hostname != metadata.name.
        url = ('https://hyperconverged-cluster-cli-download-openshift-cnv.'
               'apps.cluster-wwxjl.dyn.redhatworkshops.io/amd64/linux/virtctl.tar.gz')
        routes = [{'metadata': {'name': 'hyperconverged-cluster-cli-download'},
                   'spec': {'host': urlsplit(url).hostname, 'to': {'name': 'cli-download'},
                            'port': {'targetPort': 'http'}}}]
        self.run_download('refused', 'valid', True, ['route', 'route', 'proxy'],
                          route_url=url, routes=routes)

    def test_custom_hostname_does_not_need_to_match_route_name(self):
        self.run_download('refused', 'valid', True, ['route', 'route', 'proxy'],
                          route_url='https://downloads.example.test/amd64/linux/virtctl.tar.gz')

    def test_unrelated_routes_are_not_selected_as_download_backend(self):
        routes = [
            {'metadata': {'name': 'cli-download'}, 'spec': {
                'host': 'unrelated.apps.example.test', 'to': {'name': 'wrong-service'}}},
            {'metadata': {'name': 'actual-download'}, 'spec': {
                'host': urlsplit(ROUTE).hostname, 'to': {'name': 'cli-download'},
                'port': {'targetPort': 'http'}}},
        ]
        self.run_download('refused', 'valid', True, ['route', 'route', 'proxy'], routes=routes)

    def test_missing_or_ambiguous_host_fails_without_guessing_backend(self):
        matching = {'metadata': {'name': 'one'}, 'spec': {
            'host': urlsplit(ROUTE).hostname, 'to': {'name': 'cli-download'},
            'port': {'targetPort': 'http'}}}
        for routes in [[], [{'spec': {}}], [matching, matching]]:
            with self.subTest(routes=routes):
                self.run_download('refused', 'valid', False, ['route', 'route'], routes=routes)

    def test_route_without_service_backend_fails_before_download(self):
        routes = [{'metadata': {'name': 'cli-download'}, 'spec': {
            'host': urlsplit(ROUTE).hostname, 'to': {'kind': 'Other', 'name': 'wrong'}}}]
        self.run_download('refused', 'valid', False, ['route', 'route'], routes=routes)

    def test_transient_route_download_failure_recovers_without_fallback(self):
        self.run_download(['refused', 'valid'], 'refused', True, ['route', 'route'],
                          credentials=False)

    def test_transient_proxy_failure_recovers_within_download_budget(self):
        self.run_download('refused', ['refused', 'valid'], True,
                          ['route', 'route', 'proxy', 'proxy'])

    def test_slow_backend_recovers_after_endpoint_api_error(self):
        ready = {'resources': [{'endpoints': [
            {'conditions': {'ready': True}, 'addresses': ['192.0.2.1']}]}]}
        self.run_download('refused', 'valid', True, ['route', 'route', 'proxy'],
                          api_sequences={'EndpointSlice': [
                              {'failed': True, 'msg': 'API unavailable'}, ready]})

    def test_slow_route_discovery_recovers_after_initial_empty_list(self):
        route = {'metadata': {'name': 'actual-download'}, 'spec': {
            'host': urlsplit(ROUTE).hostname, 'to': {'name': 'cli-download'},
            'port': {'targetPort': 'http'}}}
        self.run_download('refused', 'valid', True, ['route', 'route', 'proxy'],
                          api_sequences={'Route': [{'resources': []}, {'resources': [route]}]})

    def test_missing_service_or_endpoints_fail_after_bounded_wait(self):
        for kind, result in [('Service', {'resources': []}),
                             ('EndpointSlice', {'resources': []}),
                             ('EndpointSlice', {'resources': [{'endpoints': [{}]}]}),
                             ('EndpointSlice', {'resources': [{'endpoints': [
                                 {'conditions': {'ready': False}, 'addresses': ['192.0.2.1']}]}]})]:
            with self.subTest(kind=kind, result=result):
                self.run_download('refused', 'valid', False, ['route', 'route'],
                                  api_sequences={kind: [result]})

    def test_corrupt_route_archive_uses_api_proxy(self):
        self.run_download('corrupt', 'valid', True, ['route', 'proxy'])

    def test_route_archive_without_executable_uses_api_proxy(self):
        self.run_download('missing-executable', 'valid', True, ['route', 'proxy'])

    def test_both_paths_unavailable_fail_with_bounded_retries(self):
        self.run_download('refused', 'refused', False, ['route', 'route', 'proxy', 'proxy'])

    def test_missing_api_credentials_fail_without_leaking_secrets(self):
        self.run_download('refused', 'valid', False, ['route', 'route'], credentials=False)

    def test_corrupt_fallback_archive_fails(self):
        self.run_download('refused', 'corrupt', False, ['route', 'route', 'proxy'])


if __name__ == '__main__':
    unittest.main()

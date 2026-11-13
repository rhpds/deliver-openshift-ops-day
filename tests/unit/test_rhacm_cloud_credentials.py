"""Production ACM credential retries and HCP discovery, using synthetic secrets."""
import base64
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml

ROLE = (Path(__file__).resolve().parents[2] / 'automation/ansible/roles'
        / 'ocp4_workload_rhacm_cloud_credentials')
PREFIX = 'ocp4_workload_rhacm_cloud_credentials_'
SECRET = 'synthetic-private-credential-do-not-log'

STUB = '''
from ansible.module_utils.basic import AnsibleModule
from pathlib import Path
import json
m = AnsibleModule(argument_spec={
    'state': {'type': 'str'}, 'definition': {'type': 'raw'},
    'api_version': {'type': 'str'}, 'kind': {'type': 'str'},
    'name': {'type': 'str'}, 'namespace': {'type': 'str'},
    'test_config': {'type': 'path', 'required': True},
})
c = json.loads(Path(m.params['test_config']).read_text())
p = Path(c['requests'])
previous = p.read_text().splitlines() if p.exists() else []
with p.open('a') as f:
    f.write(json.dumps({k: v for k, v in m.params.items() if k != 'test_config'}) + '\\n')
r = c['sequence'][min(len(previous), len(c['sequence']) - 1)]
if r.get('failed'):
    m.fail_json(**{k: v for k, v in r.items() if k != 'failed'})
m.exit_json(changed=False, **r)
'''


class ACMCloudCredentialsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workload = yaml.safe_load((ROLE / 'tasks/workload.yml').read_text())
        cls.providers = [t for t in cls.workload if 'block' in t]
        cls.hcp = yaml.safe_load((ROLE / 'tasks/install_hcp_cli.yaml').read_text())
        cls.defaults = yaml.safe_load((ROLE / 'defaults/main.yml').read_text())

    def run_tasks(self, tasks, sequence, success=True, variables=None):
        with tempfile.TemporaryDirectory(prefix='acm-credentials-test-') as d:
            tmp = Path(d)
            (tmp / 'library').mkdir()
            (tmp / 'library/api_stub.py').write_text(STUB)
            shutil.copytree(ROLE / 'templates', tmp / 'templates')
            (tmp / 'config.json').write_text(json.dumps({
                'sequence': sequence, 'requests': str(tmp / 'requests.jsonl')}))

            def stub(task):
                task = copy.deepcopy(task)
                for key in ['kubernetes.core.k8s', 'kubernetes.core.k8s_info']:
                    if key in task:
                        task['api_stub'] = task.pop(key)
                        task['api_stub']['test_config'] = str(tmp / 'config.json')
                for key in ['block', 'rescue', 'always']:
                    if key in task:
                        task[key] = [stub(t) for t in task[key]]
                return task

            v = {**self.defaults,
                 PREFIX + 'api_retries': 2, PREFIX + 'hcp_wait_retries': 2,
                 PREFIX + 'retry_delay': 0,
                 PREFIX + 'kubevirt': True,
                 PREFIX + 'kubevirt_pubkey': '',
                 'set_aws_acm_secret': True, 'set_azr_acm_secret': True,
                 'guid': 'offline', 'ocp4_pull_secret': {'auths': {'example.test': {'auth': SECRET}}},
                 'account_user_access_key': SECRET, 'account_user_secret_access_key': SECRET,
                 'ocp4_base_domain': 'example.test', 'ocp4_token': SECRET,
                 'ssh_privatekey': SECRET, 'ssh_publickey': 'synthetic-public-key',
                 'azure_root_dns_zone': 'example.test',
                 'az_resource_group_name': 'offline',
                 'az_service_principal': {'clientSecret': SECRET},
                 'ansible_python_interpreter': sys.executable,
                 **(variables or {})}
            play = [dict(hosts='localhost', connection='local', gather_facts=False,
                         vars=v, tasks=[stub(t) for t in tasks])]
            (tmp / 'play.yml').write_text(yaml.safe_dump(play, sort_keys=False))
            env = dict(os.environ, ANSIBLE_LIBRARY=str(tmp / 'library'),
                       ANSIBLE_LOCAL_TEMP=str(tmp / 'local'),
                       ANSIBLE_REMOTE_TEMP=str(tmp / 'remote'), ANSIBLE_NOCOLOR='1')
            result = subprocess.run([sys.executable, '-m', 'ansible.cli.playbook',
                                     '-i', 'localhost,', str(tmp / 'play.yml')], cwd=tmp,
                                    env=env, capture_output=True, text=True, timeout=60)
            out = result.stdout + result.stderr
            self.assertEqual(result.returncode == 0, success, out)
            self.assertNotIn(SECRET, out)
            self.assertNotIn(base64.b64encode(SECRET.encode()).decode(), out)
            self.assertNotIn('Error while evaluating conditional', out)
            p = tmp / 'requests.jsonl'
            return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []

    def provider_block(self, index):
        block = copy.deepcopy(self.providers[index])
        # Leave the production provider condition, vars and actual templating
        # intact; omit only diagnostic queries after the actual mutation.
        block['block'] = [t for t in block['block'] if 'kubernetes.core.k8s' in t]
        return block

    def test_all_provider_writes_retry_and_replay_identical_present_objects(self):
        for index in range(3):
            with self.subTest(provider=index):
                requests = self.run_tasks([self.provider_block(index)], [
                    {'failed': True, 'msg': '500 namespace webhook has no endpoints'}, {}])
                self.assertEqual(len(requests), 2)
                self.assertEqual(requests[0], requests[1])
                self.assertEqual(requests[0]['state'], 'present')
                definition = requests[0]['definition']
                if index == 2:
                    self.assertEqual([r['kind'] for r in definition], ['Namespace', 'Secret'])
                    self.assertEqual(definition[1]['metadata']['name'], 'kubevirt-secret')
                    self.assertEqual(definition[1]['metadata']['namespace'], 'open-cluster-management')
                    self.assertEqual(set(definition[1]['data']), {'pullSecret', 'ssh-publickey'})
                else:
                    self.assertEqual(definition['kind'], 'Secret')

    def test_permanent_provider_failure_is_fatal_after_finite_retries(self):
        for index in range(3):
            with self.subTest(provider=index):
                requests = self.run_tasks([self.provider_block(index)], [
                    {'failed': True, 'msg': 'persistent webhook or permission failure'}], False)
                self.assertEqual(len(requests), 3)

    def test_disabled_providers_do_not_write_objects(self):
        requests = self.run_tasks([self.provider_block(i) for i in range(3)], [{}],
                                  variables={'set_aws_acm_secret': False,
                                             'set_azr_acm_secret': False,
                                             PREFIX + 'kubevirt': False})
        self.assertEqual(requests, [])

    def test_healthy_credential_reruns_need_no_retries(self):
        for _ in range(2):
            requests = self.run_tasks([self.provider_block(2)], [{}])
            self.assertEqual(len(requests), 1)

    def test_hcp_deployment_uses_apps_api_and_retries_transient_errors(self):
        ready = {'resources': [{'metadata': {'generation': 2}, 'spec': {'replicas': 1},
                                'status': {'observedGeneration': 2, 'readyReplicas': 1}}]}
        requests = self.run_tasks([self.hcp[0]], [
            {'failed': True, 'msg': 'API unavailable'}, {'resources': []}, ready])
        self.assertEqual(len(requests), 3)
        self.assertEqual(requests[0]['api_version'], 'apps/v1')

    def test_hcp_deployment_cannot_pass_on_stale_or_empty_status(self):
        for response in [{'resources': []}, {'resources': [{}]},
                         {'resources': [{'metadata': {'generation': 2}, 'spec': {'replicas': 1},
                                         'status': {'observedGeneration': 1, 'readyReplicas': 1}}]}]:
            with self.subTest(response=response):
                requests = self.run_tasks([self.hcp[0]], [response], False)
                self.assertEqual(len(requests), 3)

    def test_hcp_link_discovery_waits_for_actual_linux_url(self):
        requests = self.run_tasks([self.hcp[1], self.hcp[2]], [
            {'resources': [{}]}, {'resources': [{'spec': {'links': []}}]},
            {'resources': [{'spec': {'links': [
                {'href': 'https://example.test/hcp-linux-amd64.tar.gz'}]}}]}])
        self.assertEqual(len(requests), 3)

    def test_hcp_missing_linux_url_is_a_bounded_failure(self):
        requests = self.run_tasks([self.hcp[1]], [{'resources': []}], False)
        self.assertEqual(len(requests), 3)

    def test_defaults_preserve_slow_hcp_budget_and_secret_suppression(self):
        self.assertEqual(self.defaults[PREFIX + 'api_retries'], 120)
        self.assertEqual(self.defaults[PREFIX + 'hcp_wait_retries'], 180)
        self.assertEqual(self.defaults[PREFIX + 'retry_delay'], 10)
        for i in range(3):
            task = self.provider_block(i)['block'][0]
            self.assertIs(task['no_log'], True)
            self.assertNotIn('ignore_errors', task)
        text = (ROLE / 'tasks/workload.yml').read_text()
        self.assertNotIn('first 50 chars', text)


if __name__ == '__main__':
    unittest.main()

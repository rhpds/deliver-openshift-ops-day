"""Regression tests for truthful QA prerequisites and owned-resource cleanup."""
import copy
from pathlib import Path
import unittest
import yaml

import test_operator_resilience as harness_module

ROOT = Path(__file__).resolve().parents[2]
QA = ROOT / 'qa-automation'


def load(file):
    return yaml.safe_load((QA / file).read_text())


def walk(tasks):
    for t in tasks:
        yield t
        for k in ('block', 'rescue', 'always'):
            yield from walk(t.get(k, []))


class FullE2ESafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        harness_module.OperatorResilienceTests.setUpClass()
        cls.harness = harness_module.OperatorResilienceTests('test_default_budgets_and_no_suppressed_readiness_failures')
        cls.ols = load('tasks/e2e/ols.yml')
        cls.analysis = load('tasks/e2e/ols_agentic_analysis.yml')

    def update_tasks(self):
        ts = [copy.deepcopy(t) for t in self.ols if t.get('name') in [
            'Ols | Verify the cluster update feed is healthy',
            'Ols | Require an offered update when the update demo is explicitly required',
            'Ols | Record update-UI coverage when no update is offered']]
        ts[0]['retries'] = 2
        ts[0]['delay'] = 0
        return ts

    def test_latest_release_without_offered_update_is_valid_but_reported(self):
        r = {'resources': [{'status': {'availableUpdates': None, 'conditions': [
            {'type': 'RetrievedUpdates', 'status': 'True'}]}}]}
        state, _ = self.harness.run_tasks(self.update_tasks(), {'ClusterVersion': [r]})
        self.assertEqual(state['counts']['ClusterVersion'], 1)
        notes = next(t for t in self.update_tasks() if 'qa_coverage_notes' in t.get('ansible.builtin.set_fact', {}))
        self.assertIn('not exercised', notes['ansible.builtin.set_fact']['qa_coverage_notes'])

    def test_explicitly_required_update_demo_still_fails_without_an_update(self):
        r = {'resources': [{'status': {'conditions': [{'type': 'RetrievedUpdates', 'status': 'True'}]}}]}
        self.harness.run_tasks(self.update_tasks(), {'ClusterVersion': [r]}, False,
                              extra_vars={'qa_require_cluster_update_demo': True})

    def test_unhealthy_update_feed_is_not_accepted(self):
        r = {'resources': [{'status': {'conditions': [{'type': 'RetrievedUpdates', 'status': 'False'}]}}]}
        state, _ = self.harness.run_tasks(self.update_tasks(), {'ClusterVersion': [r]}, False)
        self.assertEqual(state['counts']['ClusterVersion'], 3)

    def test_agentic_test_is_analysis_only_and_does_not_mutate_shared_adapter(self):
        tasks = list(walk(self.analysis))
        create = next(t for t in tasks if t.get('name') == 'Ols | Create QA-owned advisory AgenticRun')
        spec = create['kubernetes.core.k8s']['definition']['spec']
        self.assertEqual(spec['analysisOutput']['mode'], 'Minimal')
        self.assertEqual(spec['analysis']['agent'], 'default')
        self.assertNotIn('execution', spec)
        self.assertNotIn('verification', spec)
        self.assertNotIn('tools', spec)
        text = (QA / 'tasks/e2e/ols.yml').read_text()
        self.assertNotIn('ocp4_workload_ols_agentic_enable_cluster_updates: true', text)
        self.assertNotIn('configmap\n          - alerts-adapter-config', text)
        self.assertNotIn('Delete any AgenticRuns', text)
        self.assertNotIn('hc_ols_e2e_agenticruns.stdout_lines', text)

    def test_agentic_analysis_requires_real_success_not_only_existence(self):
        check = next(t for t in walk(self.analysis) if t.get('name') ==
                     'Ols | Require successful analysis with no execution or verification')
        for outcome, success in [('Succeeded', True), ('Failed', False)]:
            result = {'resources': [{'status': {'terminalTime': '2026-11-17T11:00:00Z',
                'steps': {'analysis': {'results': [{'name': 'qa-result', 'outcome': outcome}]}}}}]}
            self.harness.run_tasks([check], {}, success,
                                  extra_vars={'qa_ols_analysis_observed': result})
        result = {'resources': [{'status': {'terminalTime': '2026-11-17T11:00:00Z', 'steps': {}}}]}
        self.harness.run_tasks([check], {}, False,
                              extra_vars={'qa_ols_analysis_observed': result})

    def test_agentic_cleanup_is_name_scoped_and_ownership_guarded(self):
        tasks = list(walk(self.analysis))
        delete = next(t for t in tasks if t.get('name') == 'Ols | Delete only this QA-owned AgenticRun')
        self.assertEqual(delete['kubernetes.core.k8s']['name'], '{{ qa_ols_analysis_name }}')
        self.assertEqual(delete['kubernetes.core.k8s']['namespace'], 'openshift-lightspeed')
        guard = next(t for t in tasks if t.get('name') ==
                     'Ols | Refuse to delete an AgenticRun not owned by this QA run')
        for marker, success in [('qa-owned', True), ('someone-else', False)]:
            self.harness.run_tasks([guard], {}, success, extra_vars={
                'qa_ols_analysis_name': 'qa-owned', 'qa_ols_cleanup_run': {
                    'resources': [{'metadata': {'labels': {'qa.ops-day/run': marker}}}]}})

    def test_acm_default_binding_never_touches_shared_policies_namespace(self):
        acm = list(walk(load('tasks/e2e/acm.yml')))
        apply = next(t for t in acm if t.get('name') ==
                     'Acm | Apply isolated namespace, binding, Policy and Placement')
        binding = next(o for o in apply['loop'] if o['kind'] == 'ManagedClusterSetBinding')
        self.assertEqual(binding['metadata']['name'], 'default')
        self.assertEqual(binding['metadata']['namespace'], 'qa-e2e-acm-policy')
        for t in acm:
            args = t.get('kubernetes.core.k8s', {})
            self.assertNotEqual(args.get('namespace'), 'policies')
            if args.get('state') == 'absent':
                self.assertTrue(args['name'].startswith('qa-e2e-'))

    def test_namespace_deletion_does_not_treat_cli_permission_failure_as_absence(self):
        found = 0
        for file in (QA / 'tasks/e2e').glob('*.yml'):
            for t in walk(yaml.safe_load(file.read_text())):
                cmd = t.get('ansible.builtin.command', '')
                self.assertFalse(isinstance(cmd, str) and cmd.startswith('oc get project '), t.get('name'))
                args = t.get('kubernetes.core.k8s_info', {})
                if args.get('kind') == 'Namespace' and 'deleted' in t.get('name', '').lower():
                    found += 1
                    self.assertIn('is succeeded', str(t['until']))
                    self.assertNotIn('failed_when', t)
        self.assertGreater(found, 10)

    def test_network_policy_wait_rejects_cli_errors_and_allows_convergence(self):
        task = copy.deepcopy(next(t for t in walk(load('tasks/e2e/netsec.yml'))
                                  if t.get('name') == 'Netsec | Confirm connectivity is now blocked'))
        task.pop('ansible.builtin.command')
        task['kubernetes.core.k8s_info'] = {'kind': 'NetworkProbe'}
        task['retries'] = 2
        task['delay'] = 0
        state, _ = self.harness.run_tasks([task], {'NetworkProbe': [{'rc': 0}, {'rc': 28}]})
        self.assertEqual(state['counts']['NetworkProbe'], 2)
        state, _ = self.harness.run_tasks([task], {'NetworkProbe': [{'rc': 1}]}, False)
        self.assertEqual(state['counts']['NetworkProbe'], 1)
        final_guard = next(t for t in walk(load('tasks/e2e/netsec.yml'))
                           if t.get('name') == 'Netsec | Fail if deny-all NetworkPolicy did not block traffic')
        state, _ = self.harness.run_tasks([task, final_guard], {'NetworkProbe': [{'rc': 0}]}, False)
        self.assertEqual(state['counts']['NetworkProbe'], 3)

    def test_observability_requires_firing_metric_and_does_not_ignore_failure(self):
        t = next(t for t in walk(load('tasks/e2e/observability.yml'))
                 if t.get('name') == 'Observability | Require the test alert to reach Firing in Thanos')
        self.assertNotIn('ignore_errors', t)
        self.assertIn('alertstate="firing"', t['ansible.builtin.uri']['url'])
        self.assertIn('json.data.result', str(t['until']))
        self.assertIs(t['no_log'], True)

    def test_vault_uses_private_auth_mount_not_learner_backend(self):
        text = (QA / 'tasks/e2e/vault.yml').read_text()
        self.assertNotIn('auth/kubernetes/config', text)
        self.assertNotIn('auth/kubernetes/role/', text)
        self.assertIn('auth/qa-e2e-kubernetes/config', text)
        self.assertIn('vault.hashicorp.com/auth-path: "auth/qa-e2e-kubernetes"', text)
        parent = next(t for t in load('tasks/e2e/vault.yml') if t.get('name') ==
                      'Vault | Deploy, validate, and clean up Agent Injector pattern')
        self.assertTrue(any(t.get('name') == 'Vault | Remove only the QA Kubernetes auth mount'
                            for t in parent['always']))

    def test_all_original_module_includes_remain_present(self):
        play = load('e2e.yml')[0]
        includes = {t['ansible.builtin.include_tasks'] for t in play['tasks'] if
                    'ansible.builtin.include_tasks' in t}
        expected = {'tasks/_auth.yml'} | {f'tasks/e2e/{name}.yml' for name in [
            'overview', 'virt', 'gitops', 'devhub', 'security', 'ols', 'acm', 'vault',
            'install', 'appmgmt', 'ingress', 'netsec', 'debugging', 'observability', 'performance']}
        self.assertEqual(includes, expected)


if __name__ == '__main__':
    unittest.main()

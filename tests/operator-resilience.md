# GPTEINFRA-18460: Ops Day operator resilience

## Scope

This branch is based on `dev` and retains the merged HCO readiness and virtctl
route/API-proxy fallback fixes. It changes only the copied Compliance and
MetalLB roles plus their regression tests. It does not change operator versions,
cluster resources, module selection, IP pool/advertisement templates, lab
content, preflight, or global `install_operator` behavior.

### Compliance

- An existing Subscription retains its owner, catalog, channel and approval
  policy. The role does not reinstall it or add a duplicate OperatorGroup.
- A Subscription is not considered proof of installation: wait for its selected
  `currentCSV`, that exact CSV's `Succeeded` phase, and a fresh available
  Deployment. Preserve the existing two-VALID-ProfileBundle gate.
- API failures and empty/missing status responses are retried within finite,
  configurable budgets. Permanent failures remain fatal.
- New installations no longer suppress upstream CSV installation errors.
- Correct the upstream snapshot setup parameter to
  `install_operator_catalogsource_setup`. LB1543 currently disables Compliance
  snapshots; this does not change its catalog source.
- On readiness failure, print selected OLM state and the failed task name,
  without copying arbitrary failure payloads or bypassing `no_log`.

### MetalLB

- Keep the catalog readiness check and operator install settings.
- Retry idempotent instance, IPAddressPool and L2Advertisement creation.
- Poll the API for `Available=True` instead of nesting a 600-second module wait
  inside an outer retry loop. Preserve the approximately 10-minute readiness
  budget (plus time taken by each API request).
- Keep IPAddressPool and L2Advertisement feature flags and templates unchanged.
- Add namespaced OLM diagnostics; keep failures fatal and identify their stage.

## Offline tests

Only Kubernetes API calls (and the external installer invocation in ownership
checks) are stubbed. Real Ansible evaluates production `until`, `when`, `vars`,
`register`, `include_tasks` and rescue directives. No cluster credentials needed.

```sh
python -m unittest discover -s tests/unit -v
```

Run with both Ansible Core 2.18 and 2.19 and PyYAML installed. Tests cover missing
resources/status, transient API/webhook errors, failed CSVs, stale Deployment
generations, retry exhaustion, no-log failure handling, healthy reruns, retained
ProfileBundle checks, and existing Subscription ownership/optional resource
flags. Existing HCO/virtctl tests must also pass.

YAML lint using the existing roles' long-line/indentless-sequence style:

```sh
yamllint -d '{extends: default, rules: {line-length: disable, indentation: {spaces: 2, indent-sequences: consistent}}}' \
  automation/ansible/roles/ocp4_days_workload_compliance_operator/{defaults,tasks}/*.yml \
  automation/ansible/roles/ocp4_workload_metallb/{defaults,tasks}/*.yml
```

## Fresh LB1543 integration acceptance (not performed by offline tests)

1. In a separate integration-only AgnosticV branch, override only the
   `deliver-openshift-ops-day` collection ref in LB1543's `dev.yaml` to
   `GPTEINFRA-18460-ops-operator-resilience`. Do not move existing release tags
   or change event/prod pins.
2. Provision a fresh compact cluster with the security and networking modules
   enabled. Also test ACM enabled, to exercise externally managed Compliance
   Subscriptions without creating a second OperatorGroup.
3. Confirm Compliance's selected CSV succeeds, its Deployment is available and
   both ProfileBundles are VALID; confirm MetalLB Available=True and the
   intended IP pool/advertisement settings are unchanged.
4. Retry an interrupted provisioning run using the supported resume mechanism.
   Existing successful installations should be reused without duplicate OLM
   resources, automatic approval-policy changes or skipped readiness gates.
5. On deliberate persistent failure, verify provisioning stops and the failing
   stage/OLM state is visible without credential disclosure.
6. Check HCO health and virtctl installation plus existing lab health/e2e tests.
   Offline success does not prove fresh provisioning or workshop e2e success.

## Deliberately separate follow-ups

Strict MachineConfig preflight and shared CatalogSource ownership/pin alignment
need their own compatibility review and fresh-cluster tests. These roles still
rely on the external `install_operator` implementation for OLM installation.
This branch does not claim to eliminate every intermittent operator failure.

# GPTEINFRA-18460: Ops Day operator resilience

## Scope

This branch is based on `dev` and retains the merged HCO readiness logic.
It hardens the copied Compliance, MetalLB and ACM cloud-credentials roles and
the remaining audited RHDH, HCP, observability, GitOps, RHACS, Vault and later
HCO API paths. It also corrects/extends the virtctl fallback after job 92239
exposed a hostname lookup bug, and makes preflight/shared-catalog gates useful.
It does not change operator versions, cluster resource specifications, module
selection, IP pool/advertisement templates, lab content, or the global
`install_operator` implementation. Ansible Core >=2.18 is required and declared
in collection runtime metadata; both 2.18.20 and 2.19.15 are tested.

### Compliance

- An existing Subscription retains its owner, catalog, channel and approval
  policy. The role does not reinstall it or add a duplicate OperatorGroup.
- A Subscription is not considered proof of installation: wait for its selected
  `currentCSV`, that exact CSV's `Succeeded` phase, and a fresh available
  Deployment. Preserve the existing two-VALID-ProfileBundle gate.
- API failures and empty/missing status responses are retried within finite,
  configurable budgets. Resolution, CSV, Deployment and ProfileBundles each
  allow approximately 20 minutes on slow CNV. These budgets are cumulative,
  not a single total job deadline, and exclude API request duration.
  Permanent failures remain fatal.
- New installations keep `install_operator_install_csv_ignore_error: false`.
  If and only if the installer's final CSV polling task times out, continue to
  the mandatory local readiness gate. Recognize the exact action/name/register
  shape; reject configuration, approval, authorization and unrelated failures.
  This grants convergence time without retrying/recreating the installation.
- Correct the upstream snapshot setup parameter to
  `install_operator_catalogsource_setup`. LB1543 currently disables Compliance
  snapshots; this does not change its catalog source.
- On readiness failure, print selected OLM state and the failed task name,
  without copying arbitrary failure payloads or bypassing `no_log`.

### MetalLB

- Keep the catalog readiness check and operator install settings. Allow roughly
  20 minutes each for shared catalog, CSV convergence and MetalLB readiness on
  slow CNV clusters; creation retries retain their ~5-minute budget.
- Retry idempotent instance, IPAddressPool and L2Advertisement creation.
- Poll the API for `Available=True` instead of nesting a 600-second module wait
  inside an outer retry loop. Use a configurable approximately 20-minute
  readiness budget (plus time taken by each API request).
- As for Compliance, only an upstream final CSV wait timeout can receive local
  convergence grace. Always verify the selected MetalLB CSV succeeds before
  attempting to create custom resources.
- Keep IPAddressPool and L2Advertisement feature flags and templates unchanged.
- Add namespaced OLM diagnostics; keep failures fatal and identify their stage.

### Second review: virtctl and slow CNV backends (job 92239)

- HCO readiness completed; the direct virtctl route refused connections, then
  fallback Route discovery returned no resources after exhausting retries.
- The old fallback guessed a Route resource name from its hostname. Generated
  OpenShift hosts include the namespace, and custom hosts need not resemble
  resource names. List Routes in openshift-cnv and match the advertised
  `spec.host`; require exactly one match and a valid Service backend.
- Wait for the Service ports and a ready EndpointSlice address before proxying.
  Use a separate configurable ~15-minute polling budget per backend stage;
  keep download retries finite, avoid nesting module waits, and still fail on
  permanently missing/ambiguous Routes, Services or endpoints.
- Preserve API-token suppression, unredirected Authorization headers, archive
  validation, delegation to bastion, and the existing service-port resolution.
- The virtualization rescue now identifies the original failed stage without
  dumping raw results.
- The old API stub returned a Route regardless of the requested name. It now
  enforces name/namespace lookup semantics. The generated-hostname regression
  was verified to fail on pre-fix code. Tests also cover custom/unrelated hosts,
  ambiguous/missing backends, delayed Route discovery/endpoint readiness and
  transient download failures.

### ACM credential writes and HCP discovery (job 92272)

- ACM MultiClusterHub readiness completed; the next KubeVirt credential task
  failed patching a Namespace because the Tekton namespace-validation webhook
  had no endpoints (HTTP 500). This is an admission dependency failure, not
  evidence that ACM itself failed to install.
- Retry state:present AWS, Azure and KubeVirt credential writes with a finite
  configurable ~20-minute budget. KubeVirt retries replay the same materialized
  Namespace/Secret documents, preserving names, labels and credential data.
  No webhook is disabled and no required credential step is skipped.
- Suppress raw credential write/read results and remove the existing debug
  output of a pull-secret prefix. Diagnostic metadata remains available.
- Review also found HCP CLI discovery querying Deployment in apiVersion v1;
  correct it to apps/v1. Poll the API request itself, require fresh Deployment
  readiness, and wait for the actual Linux URL rather than CR existence only.
  Preserve the previous ~30-minute Deployment budget with configurable polling.
- Tests render actual templates with synthetic credentials and verify identical
  retry payloads, provider flags, permanent failures, healthy reruns, missing
  HCP statuses/links and secret suppression. These do not prove that the Tekton
  webhook recovered on the failed cluster or that the new job completes.

### Broad hardening after the remaining-path audit

- Safe API writes use finite retries; read gates tolerate failed queries, absent
  resources and missing controller status. Authorization/validation errors
  (clear HTTP 400/401/403/405/415/422) stay fatal without repeated retries;
  404/discovery lag, conflicts, throttling and 5xx retain bounded recovery.
- New collection-local filters check actual Deployment availability and observed
  generation, Pod Ready (not merely Running), current node configurations,
  MachineConfigPool convergence, KubeletConfig controller observation, OLM
  readiness, admitted Routes and populated Secret/ConfigMap data. They do not
  mutate the cluster or print credential contents.
- Preflight no longer ignores KubeletConfig application or final pool/node/OLM
  readiness failures. Final gates run on every provision retry, including when
  the KubeletConfig itself is unchanged. The initial rollout-start observation
  remains advisory; final convergence is mandatory. Existing ~30-minute pool
  budget is preserved.
- Shared catalog creation/readiness is required when enabled snapshot consumers
  need it; explicit ops_day_shared_catalog_required can override detection.
  The companion dev config aligns bootstrap with its existing v5.0 consumers
  instead of starting the older common.yaml catalog and replacing it mid-run.
- RHDH, ZTWIM and copied GitOps use a collection-local wrapper around the shared
  installer. Only its final read-only CSV wait can receive grace, followed by
  mandatory Subscription/selected-CSV gates. No whole-installer retry and no
  new automatic approval. ZTWIM cannot ignore readiness then declare success.
- RHDH URL fallbacks are conditional, retried reads rather than eager pipe
  lookups. Token minting is not blindly retried; token-bearing results are
  suppressed. Vault Helm installation remains a single operation with a
  configurable 30-minute convergence deadline, not nested install retries.
- RHACS route-switch ordering is preserved. Default-route removal checks only
  its two owned routes; new route admission is actually verified. Already
  configured RHACS and disabled boot-image trimming end only the role, not the
  host. Boot-image override generation resets its temporary list on each run.
- Optional diagnostics/cache warmup and intentionally faulty demo resources
  retain their existing semantics. No admission webhook is disabled.

New polling controls (finite attempt budgets, not total job deadlines):

- ops_day_api_retries: default 120 for the new API paths.
- ops_day_retry_delay: default 10 seconds for the new polling paths.
- ops_day_readiness_retries: optional override; defaults retain longer existing
  waits or give short waits ~20 minutes at their original polling interval.
- ops_day_preflight_pool_retries: default 90 at 20 seconds (~30 minutes).
- ops_day_packageserver_retries: default 60 at 20 seconds (~20 minutes).
- ops_day_helm_timeout: default 30m, one Helm operation.

Actual elapsed time also includes API/CLI request duration, and stage budgets
are cumulative. Retry warnings in Ansible output are expected; permanent or
exhausted failures remain fatal. External core_workloads/ai_workloads role
internals, arbitrary shell actions and all future operator combinations are
not claimed universally hardened by this collection-local patch.

## Offline tests

Only Kubernetes API calls (and the external installer invocation in ownership
checks) are stubbed. Real Ansible evaluates production `until`, `when`, `vars`,
`register`, `include_tasks` and rescue directives. No cluster credentials needed.

```sh
python -m unittest discover -s tests/unit -v
```

Run with both Ansible Core 2.18 and 2.19 and PyYAML installed. The installer
boundary tests execute an actual include_role/rescue with the upstream final
CSV task shape and stubbed API responses; they exercise safe convergence grace,
rejection of unrelated/permission errors, and permanent failure after grace.
Tests cover missing
resources/status, transient API/webhook errors, failed CSVs, stale Deployment
generations, retry exhaustion, no-log failure handling, healthy reruns, retained
ProfileBundle checks, and existing Subscription ownership/optional resource
flags. Existing HCO/virtctl tests must also pass. Offline tests cannot reproduce actual
CNV reboot timing or prove the job exercised transient-error recovery.

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

The new preflight, shared-catalog gating and companion dev pin alignment need
fresh-cluster validation. Other consumers may deliberately use different
catalog pins; full cross-role catalog ownership and external installer/core
role internals remain separate compatibility concerns. The failed-job evidence
establishes specific webhook races, not the cause of every slow startup.
This branch does not claim to eliminate every intermittent operator failure.

#!/bin/bash
set -euo pipefail

cat <<EOF | oc apply -f -
apiVersion: observability.openshift.io/v1
kind: ClusterLogForwarder
metadata:
  name: collector
  namespace: openshift-logging
spec:
  collector:
    resources:
      limits:
        cpu: "1"
        memory: 4Gi
      requests:
        cpu: "1"
        memory: 4Gi                    # Guaranteed QoS prevents OOM killer targeting collectors
  serviceAccount:
    name: collector
  inputs:
  - name: workshop-application
    type: application
    application:
      includes:
      - namespace: alert-demo         # keep application collection to the workshop namespace
  - name: workshop-infrastructure
    type: infrastructure
    infrastructure:
      sources:
      - node                           # node journal logs only
  - name: workshop-audit
    type: audit
    audit:
      sources:
      - kubeAPI                        # Kubernetes API audit source for the namespace filter below
  filters:
  - name: workshop-audit-policy
    type: kubeAPIAudit
    kubeAPIAudit:
      omitStages:
      - RequestReceived                # avoid forwarding the duplicate request-start event
      rules:
      - level: Metadata
        namespaces:
        - alert-demo                   # keep API audit events for the workshop namespace only
      - level: None                    # drop API audit events outside alert-demo
  outputs:
  - name: default-lokistack
    type: lokiStack
    lokiStack:
      authentication:
        token:
          from: serviceAccount         # authenticates to Loki using the SA token
      target:
        name: logging-loki             # the LokiStack we created above
        namespace: openshift-logging
    tls:
      ca:
        key: service-ca.crt
        configMapName: logging-loki-gateway-ca-bundle
  pipelines:
  - name: default-logstore
    inputRefs:
    - workshop-application             # application logs from alert-demo only
    - workshop-infrastructure          # node journal logs only
    - workshop-audit                    # Kubernetes API audit events from alert-demo only
    filterRefs:
    - workshop-audit-policy
    outputRefs:
    - default-lokistack
EOF

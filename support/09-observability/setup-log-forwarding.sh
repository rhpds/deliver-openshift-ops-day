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
        memory: 1Gi
      requests:
        cpu: 100m
        memory: 256Mi                  # reserve close to the observed scoped collector usage
  serviceAccount:
    name: collector
  inputs:
  - name: workshop-application
    type: application
    application:
      includes:
      - namespace: observability-demo # keep application collection to the workshop namespace
  - name: workshop-infrastructure
    type: infrastructure
    infrastructure:
      sources:
      - node                          # node journal logs for the infrastructure view
  - name: workshop-audit
    type: audit
    audit:
      sources:
      - kubeAPI                       # Kubernetes API audit events for the demo namespace
  filters:
  - name: workshop-audit-policy
    type: kubeAPIAudit
    kubeAPIAudit:
      omitStages:
      - RequestReceived
      rules:
      - level: Metadata
        namespaces:
        - observability-demo          # keep auditable demo activity, without request bodies
      - level: None                   # omit unrelated API audit events
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
    - workshop-application             # application logs from the demo namespace
    - workshop-infrastructure          # node journal logs for the infrastructure category
    - workshop-audit                   # namespace-scoped Kubernetes API audit events
    filterRefs:
    - workshop-audit-policy
    outputRefs:
    - default-lokistack
EOF

# Module 09 — Observability & Logging

## Brief Overview

This is the longest module in the Roadshow at 35–40 minutes, covering the full OpenShift observability stack in three sequential sections. The metrics section covers Prometheus query authoring and Alertmanager routing. The logging section installs the Loki Operator and Cluster Logging Operator, configures Vector as the log collector, and uses ODF/NooBaa S3 as the log storage backend. The tracing section installs the Red Hat build of OpenTelemetry and the Tempo Operator, then instruments a sample application to emit traces.

## Audience and Time

- **Personas:** Cluster administrators, site reliability engineers, platform engineers
- **Prerequisites:** Cluster-admin access; ODF pre-installed; basic familiarity with metrics concepts (labels, cardinality, PromQL syntax is introduced in-lab)
- **Duration:** 35–40 minutes

## Learning Objectives

1. Query cluster and application metrics in the OpenShift web console using PromQL
2. Create and route Alertmanager alerts to a webhook receiver
3. Install the Loki Operator and configure a LokiStack backed by ODF NooBaa S3
4. Install the Cluster Logging Operator and configure Vector as the log collector
5. Query application and infrastructure logs in the OpenShift Logging console
6. Install the Red Hat build of OpenTelemetry Operator and configure a collector
7. Install the Tempo Operator and view distributed traces for an instrumented application

## Lab Structure

| Section | Title | Duration |
|---------|-------|----------|
| 1 | **Part 1: Metrics** |  |
| 2 | Query metrics in OpenShift console (PromQL) | 5 min |
| 3 | Create Alertmanager alert and routing | 5 min |
| 4 | **Part 2: Logging** |  |
| 5 | Install Loki Operator and create LokiStack | 5 min |
| 6 | Install Cluster Logging Operator and configure Vector | 5 min |
| 7 | Query logs in Logging console | 5 min |
| 8 | **Part 3: Tracing** |  |
| 9 | Install OpenTelemetry Operator and configure collector | 5 min |
| 10 | Install Tempo Operator and view traces | 5–10 min |

## Key Takeaways

- OpenShift ships with Prometheus and Alertmanager pre-installed — user workload monitoring must be enabled separately
- Loki is label-based log aggregation similar to Prometheus — LogQL syntax mirrors PromQL
- NooBaa S3 (via ODF) provides the object storage backend for Loki, eliminating the need for external cloud storage
- Vector replaces Fluentd as the default log collector and offers significantly better performance
- OpenTelemetry provides vendor-neutral instrumentation; Tempo stores and queries the traces

## Infrastructure Notes

- ODF with NooBaa S3 and Ceph RBD is pre-installed — required for LokiStack storage backend
- Loki Operator, Cluster Logging Operator, OpenTelemetry Operator, and Tempo Operator are installed by participants during this module
- This module has the heaviest operator installation footprint — allow extra time if clusters are resource-constrained

# Module Outline: Observability in OpenShift

## Brief Overview

This module provides a hands-on walkthrough of OpenShift's observability stack. Participants work through metrics collection with Prometheus, log collection and storage with Vector and Loki, and distributed tracing with OpenTelemetry and Tempo — building presenter confidence with the tools, commands, and workflows needed to deliver this content to customers.

## Audience and Time

- **Target personas:** Solution architects, specialist solution architects, adoption architects, technical account managers, sales specialists
- **Prerequisites for this module:** Familiarity with `oc`/`kubectl` CLI and OpenShift web console
- **Estimated duration:** 30 minutes

## Learning Objectives

- Deliver a module on observability in OpenShift including metrics with Prometheus, logs with Loki and traces with OpenTelemetry

## Lab Structure

| Section | Title | Duration |
|---------|-------|----------|
| 1       | Metrics with Prometheus and Thanos | 10 min |
| 2       | Logs with Vector and Loki | 10 min |
| 3       | Distributed Tracing with OpenTelemetry and Tempo | 10 min |

## Detailed Steps

### Metrics with Prometheus

1. Open the OpenShift web console and navigate to the monitoring section.
2. Run a PromQL query to view CPU and memory usage for the sample application's pods.
3. Examine a pre-configured alert rule and identify what condition triggers it.

### Logs with Loki

4. Navigate to the logging interface in the OpenShift console.
5. Filter logs by namespace and pod to locate log entries from the sample application.
6. Search for error-level log entries and identify the relevant log messages.

### Distributed Tracing with OpenTelemetry and Tempo

7. Navigate to the distributed tracing interface.
8. Generate traffic against the instrumented sample application to produce trace data.
9. Locate a trace in the Tempo interface and examine the span details across services.
10. Identify a slow span and correlate it with the corresponding metric and log data.
11. Walk through the end-to-end diagnostic workflow: start from a metric alert, find related logs, and trace the request path to pinpoint the root cause.

## Key Takeaways

- OpenShift's monitoring stack (Prometheus, Thanos) provides built-in metrics collection and alerting without additional installation.
- Loki enables centralized log aggregation; the OpenShift console provides a unified interface for filtering and searching logs.
- OpenTelemetry instrumentation combined with Tempo gives end-to-end distributed tracing across services.
- The real power of observability comes from correlating metrics, logs, and traces to diagnose issues quickly.

## Infrastructure Notes

- Requires an OpenShift cluster with the full monitoring stack enabled: Prometheus, Thanos, Loki, Tempo, and OpenTelemetry Collector.
- Loki, Tempo, and OpenTelemetry operators must be installed and configured before the module.
- The sample application must be instrumented for distributed tracing.
- Pre-configured dashboards and at least one alert rule should be in place for the metrics exercise.
- Cluster credentials are provided through Showroom environment attributes.

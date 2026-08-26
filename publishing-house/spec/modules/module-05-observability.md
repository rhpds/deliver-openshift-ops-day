# Module Outline: Observability Hands-On

## Brief Overview

This module provides hands-on practice with the Observability content from the Roadshow. Participants work through metrics collection with Prometheus, log aggregation with Loki, and distributed tracing with OpenTelemetry and Tempo. As with the previous hands-on module, the focus is on building presenter confidence with the specific tools, commands, and workflows so they can deliver the content and handle questions during a live session.

## Audience and Time

- **Target personas:** Solution architects, specialist solution architects, adoption architects, technical account managers, sales specialists
- **Prerequisites for this module:** Basic familiarity with OpenShift CLI (`oc`) and the web console
- **Estimated duration:** 30 minutes

## Learning Objectives

- Query application and cluster metrics using Prometheus and the OpenShift web console
- View and filter aggregated logs using Loki through the OpenShift console's logging interface
- Trace a request across services using OpenTelemetry instrumentation and the Tempo backend
- Correlate metrics, logs, and traces to diagnose an application issue end-to-end

## Lab Structure

| Section | Title | Duration |
|---------|-------|----------|
| 1       | Metrics with Prometheus | 10 min |
| 2       | Logs with Loki | 10 min |
| 3       | Distributed Tracing with OpenTelemetry and Tempo | 10 min |

## Detailed Steps

1. Open the OpenShift web console and navigate to the monitoring section.
2. Run a PromQL query to view CPU and memory usage for the sample application's pods.
3. Examine a pre-configured alert rule and identify what condition triggers it.
4. Navigate to the logging interface in the OpenShift console.
5. Filter logs by namespace and pod to locate log entries from the sample application.
6. Search for error-level log entries and identify the relevant log messages.
7. Review how Vector (ClusterLogForwarder) forwards logs to the Loki backend.
8. Navigate to the distributed tracing interface.
9. Generate traffic against the instrumented sample application to produce trace data.
10. Locate a trace in the Tempo interface and examine the span details across services.
11. Identify a slow span in the trace and correlate it with the corresponding metric and log data.
12. Walk through the end-to-end diagnostic workflow: start from a metric alert, find related logs, and trace the request path to pinpoint the root cause.
13. Answer the checkpoint questions to confirm understanding of the observability tools and the correlation workflow.

## Key Takeaways

- OpenShift's monitoring stack (Prometheus, Thanos) provides built-in metrics collection and alerting without additional installation.
- Loki with Vector enables centralized log aggregation; the OpenShift console provides a unified interface for filtering and searching logs.
- OpenTelemetry instrumentation combined with Tempo gives end-to-end distributed tracing across services.
- The real power of observability comes from correlating metrics, logs, and traces to diagnose issues quickly; presenters should emphasize this workflow during delivery.

## Infrastructure Notes

- Requires an OpenShift cluster with the full monitoring stack enabled: Prometheus, Thanos, Loki, Vector, OpenTelemetry Collector, and Tempo.
- Loki, Tempo, and OpenTelemetry operators must be installed and configured before the module.
- The sample application must be instrumented for distributed tracing (OpenTelemetry SDK or auto-instrumentation).
- Pre-configured dashboards and at least one alert rule should be in place for the metrics exercise.
- Cluster credentials are provided through Showroom environment attributes.

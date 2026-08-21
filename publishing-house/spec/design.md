# Deliver the OpenShift Ops Day Roadshow

## Overview

This lab prepares Red Hat field teams to deliver the OpenShift Ops Day Roadshow workshop to customers. Participants learn what the Roadshow is, how to position and schedule it, and how to deliver individual modules effectively. They then complete hands-on exercises from the Application Management and Observability modules to build familiarity with the content they will be presenting.

## Target Audience

- **Role:** Solution architects, specialist solution architects, adoption architects, technical account managers, sales specialists
- **Experience level:** Intermediate
- **What they already know:** Core OpenShift concepts (clusters, projects, deployments), basic CLI usage, familiarity with the Red Hat Demo Platform
- **What they don't know:** How the Roadshow is structured, how to deliver individual modules, and the specifics of the hands-on lab environment

## Prerequisites

- Active access to the Red Hat Demo Platform (RHDP)
- Basic familiarity with OpenShift CLI (`oc`) and the web console
- Can the lab validate these automatically? No — trust-based

## Learning Objectives

1. Describe the OpenShift Ops Day Roadshow's structure, value propositions, and delivery formats
2. Identify how to position the Roadshow for different customer scenarios (single-day, regional event, individual sessions)
3. Demonstrate the delivery workflow for a Roadshow module including supporting materials, live walkthrough, student work time, and reviews
4. Verify an OpenShift cluster installation and inspect cluster health
5. Deploy an application on OpenShift and validate its components
6. Troubleshoot a failing application deployment using OpenShift diagnostic tools
7. Monitor cluster and application metrics using Prometheus and Thanos
8. Analyze application logs using ClusterLogForwarder (Vector) and Loki
9. Explore distributed traces using OpenTelemetry and Tempo

## Content Type

Lab (hands-on)

## Products & Technologies

- Red Hat OpenShift Container Platform
- Prometheus (bundled with OpenShift monitoring stack)
- Thanos (bundled with OpenShift monitoring stack)
- Loki (OpenShift Logging)
- Vector (ClusterLogForwarder)
- OpenTelemetry (OpenShift distributed tracing)
- Tempo (OpenShift distributed tracing)

## Module Map

| Module | Title | Duration |
|--------|-------|----------|
| 1 | What Is the OpenShift Roadshow? | 15 min |
| 2 | Positioning and Scheduling the Roadshow | 15 min |
| 3 | How to Deliver a Module | 30 min |
| 4 | Application Management Hands-On | 30 min |
| 5 | Observability Hands-On | 30 min |
| — | **Total hands-on** | **1 hour** |
| — | Intro / presentation | **~1 hour** |
| — | **Total lab** | **~2 hours** |

## Difficulty Level

Intermediate

## Environment

**Learner view:** An OpenShift cluster with pre-deployed sample applications and configured monitoring stack (Prometheus, Thanos, Loki, Tempo, OpenTelemetry Collector). Participants access the cluster via the web console and CLI. Roadshow supporting materials (slide decks, presenter notes) are available through the Showroom interface.

**Automation needed:** Yes

- OpenShift cluster with monitoring stack enabled
- Loki, Tempo, and OpenTelemetry operators installed and configured
- Sample application deployed for troubleshooting exercises
- Sample application instrumented for distributed tracing
- Pre-configured dashboards and alerts for observability module

## Infrastructure Requirements

- **Cloud provider:** TBD — confirmed in infrastructure phase
- **Cluster type:** TBD — confirmed in infrastructure phase
- **OCP version:** TBD — confirmed in infrastructure phase
- **Topology:** TBD — confirmed in infrastructure phase
- **Sizing:** TBD — confirmed in infrastructure phase
- **Automation approach:** TBD — confirmed in infrastructure phase
- **AI/MaaS:** None
- **External services:** TBD — confirmed in infrastructure phase
- **Non-GA products:** None (all products are GA)

# Deliver the OpenShift Ops Day Roadshow

## Overview

This lab provides an overview of the OpenShift Ops Day workshop as well as delivery instructions and lab guidance, including live content delivery. Participants learn what the Roadshow is, how to deliver modules, and the content covered across all 18 modules. They complete hands-on exercises from the Application Management and Observability modules to build familiarity with the content they will be presenting.

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

1. Describe the OpenShift Ops Day Roadshow's structure, content, value propositions, and delivery formats
2. Describe and demo how to deliver a workshop module including supporting materials, live walkthroughs and student work time
3. Describe the content included and background required for all 18 modules in the workshop
4. Demonstrate delivery of application management and troubleshooting content including cluster verification, application deployment, and debugging
5. Demonstrate delivery of observability content including metrics with Prometheus, logs with Loki, and traces with OpenTelemetry

## Content Type

Lab (hands-on)

## Products & Technologies

- Red Hat OpenShift Container Platform

## Module Map

| Module | Title | Duration |
|--------|-------|----------|
| 1 | Position the Workshop | 20 min |
| 2 | Deliver the Workshop | 15 min |
| 3 | Application Management Hands-On | 30 min |
| 4 | Overview of All Modules | 20 min |
| 5 | Observability Hands-On | 30 min |
| — | **Total hands-on** | **1 hour** |
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

- **Cloud provider:** CNV
- **Cluster type:** Multinode — 3 control plane (16 vCPU, 64GB RAM), no workers
- **OCP version:** 4.20
- **Topology:** One cluster per student
- **Automation approach:** Ansible
- **AI/MaaS:** None
- **External services:** registry.redhat.io, registry.connect.redhat.com
- **Non-GA products:** None (all products are GA)

# Deliver the OpenShift Ops Day Roadshow

## Overview

This lab provides an overview of and delivery guidance for the OpenShift Ops Day workshop followed by hands-on walkthroughs of modules on observability in OpenShift, Zero Trust Workload Identity Manager and secrets management with Vault and External Secrets Operator. Participants learn what the workshop contains and how to provision it for engagements, select content and deliver the modules.

## Target Audience

- **Role:** Solution architects, specialist solution architects, adoption architects, technical account managers, sales specialists
- **Experience level:** Intermediate
- **What they already know:** Kubernetes concepts such as pods, nodes, secrets and namespaces; and OpenShift concepts such as operators and monitoring
- **What they don't know:** How the Roadshow and its lab is structured; OpenShift observability; ZTWIM; secrets management with ESO

## Prerequisites

- Familiarity with `oc`/`kubectl` CLI and OpenShift web console

## Learning Objectives

1. Learn about the OpenShift Ops Day Roadshow's structure, content, value propositions, and delivery formats
2. Deliver a workshop module including supporting materials, lab setup, live walkthroughs and student work time
3. Deliver a module on observability in OpenShift including metrics with Prometheus, logs with Loki and traces with OpenTelemetry
4. Deliver a module on Zero Trust Workload Identity Manager for passwordless service authentication
5. Deliver a module on secrets management with Hashicorp Vault and External Secrets Operator

## Content Type

Lab (hands-on)

## Products & Technologies

- Red Hat OpenShift Container Platform
- Red Hat OpenShift Observability - Prometheus, Loki, OpenTelemetry, Tempo
- Red Hat OpenShift Zero Trust Workload Identity Manager (ZTWIM)
- Hashicorp Vault
- External Secrets Operator (ESO)

## Module Map

| Module | Title | Duration |
|--------|-------|----------|
| 1 | Position and deliver the workshop | 25 min |
| 2 | Observability in OpenShift | 30 min |
| 3 | Zero Trust Workload Identity Manager | 30 min |
| 4 | Secrets management with Vault and External Secrets Operator | 30 min |
| — | **Total hands-on** | **90 minutes** |
| — | **Total lab** | **2 hours** |

## Difficulty Level

Intermediate

## Environment

**Learner view:** Participants access content and cluster via Showroom interface. An OpenShift cluster with full monitoring stack configured (Prometheus, Thanos, Loki, Tempo, OpenTelemetry), ZTWIM ready to deploy, and Hashicorp Vault and External Secrets Operator ready to deploy.

**Automation needed:** Yes

- OpenShift cluster with monitoring stack ready - Loki, Tempo, OpenTelemetry, etc.
- OpenShift cluster with ZTWIM prerequisites
- OpenShift cluster with secret management prerequisites

## Infrastructure Requirements

- **Cloud provider:** CNV
- **Cluster type:** Multinode — 3 control plane (16 vCPU, 64GB RAM), no workers
- **OCP version:** 4.20
- **Topology:** One cluster per student
- **Automation approach:** Ansible
- **AI/MaaS:** None
- **External services:** registry.redhat.io, registry.connect.redhat.com
- **Non-GA products:** None (all products are GA)
